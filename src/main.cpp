#include "data_generator.hpp"
#include "solver.hpp"
#include "baseline.hpp"
#include "metrics.hpp"
#include <iostream>
#include <algorithm>
#include <functional>

using namespace rescue;

namespace {
// Timings on a normal desktop are noisy (OS scheduling, turbo, other apps).
// A single sample made the "naive" curve jump around by ~50%, which hid the
// actual trend. Taking the median of a few runs gives a stable, honest number.
constexpr int kRepetitions = 3;

double medianTimeMs(const std::function<void()>& work) {
    std::vector<double> samples;
    samples.reserve(kRepetitions);
    for (int i = 0; i < kRepetitions; ++i) {
        Timer t;
        work();
        samples.push_back(t.elapsedMs());
    }
    std::sort(samples.begin(), samples.end());
    return samples[samples.size() / 2];
}
}  // namespace

int main() {
    DatasetConfig config;
    // NOTE: in the current model a resource covers at most ONE task (see
    // resourceBusy_ in solver.cpp), so we need a resource pool larger than the
    // task set for coverage to be meaningful. Allowing one resource to serve
    // several non-overlapping tasks is a roadmap item -- see README.
    config.numResources = 20000;
    config.numTasks = 10000;  // must be larger than the biggest disruption scale

    Dataset dataset = generateDataset(config);

    IncrementalSolver solver(dataset.resources, dataset.tasks);
    solver.initialAssign();

    NaiveBaseline baseline(dataset.resources, dataset.tasks);
    baseline.resolveFromScratch();

    // Disruption scales must be well below numTasks so the incremental solver
    // actually repairs a SUBSET -- that's the whole point of the demo.
    // Old scales {300,1000,5000,10000} with numTasks=2000 caused the last two
    // to clamp to 2000 (full recompute), making incremental appear slower.
    std::vector<int> scales = { 100, 500, 1500, 3000 };  // 1%, 5%, 15%, 30% of 10000 tasks
    auto events = generateDisruptionWave(dataset, scales);

    std::vector<RunResult> results;
    for (size_t i = 0; i < events.size(); ++i) {
        RunResult r;
        r.disruptionScale = scales[i];

        r.incrementalTimeMs = medianTimeMs([&] { solver.repair(events[i]); });
        r.incrementalUnassigned = solver.unassignedCount();

        r.naiveTimeMs = medianTimeMs([&] { baseline.resolveFromScratch(); });
        r.naiveUnassigned = baseline.unassignedCount();

        results.push_back(r);
        std::cout << "Scale " << r.disruptionScale
                  << " | incremental: " << r.incrementalTimeMs << " ms"
                  << " (" << r.incrementalUnassigned << " uncovered)"
                  << " | naive: " << r.naiveTimeMs << " ms"
                  << " (" << r.naiveUnassigned << " uncovered)"
                  << " | speedup: " << (r.naiveTimeMs / r.incrementalTimeMs) << "x\n";
    }

    auto written = writeResultsEverywhere(results);
    std::cout << "\nresults.json written to " << written.size() << " location(s):\n";
    for (const auto& p : written) std::cout << "  " << p << "\n";
    std::cout << "Open dashboard/index.html through a local web server "
                 "(see README) to view the chart.\n";
    return 0;
}
