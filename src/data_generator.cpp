#include "data_generator.hpp"
#include <algorithm>
#include <random>

namespace rescue {

namespace {
std::vector<std::string> makeTagPool(int n) {
    std::vector<std::string> tags;
    tags.reserve(n);
    for (int i = 0; i < n; ++i) tags.push_back("SKILL_" + std::to_string(i));
    return tags;
}
}  // namespace

Dataset generateDataset(const DatasetConfig& config) {
    std::mt19937 rng(config.seed);
    std::uniform_real_distribution<double> timeDist(0.0, 480.0);   // ~20-day window, in hours
    std::uniform_real_distribution<double> durationDist(1.0, 6.0);
    std::uniform_int_distribution<int> tagDist(0, config.numQualificationTags - 1);

    auto tagPool = makeTagPool(config.numQualificationTags);

    Dataset dataset;
    dataset.resources.reserve(config.numResources);
    for (int i = 0; i < config.numResources; ++i) {
        Resource r;
        r.id = i;
        r.name = "R" + std::to_string(i);
        r.qualifications = { tagPool[tagDist(rng)], tagPool[tagDist(rng)] };
        r.availableFrom = 0.0;
        r.availableUntil = 480.0;
        dataset.resources.push_back(std::move(r));
    }

    dataset.tasks.reserve(config.numTasks);
    for (int i = 0; i < config.numTasks; ++i) {
        Task t;
        t.id = i;
        t.label = "T" + std::to_string(i);
        t.requiredQualifications = { tagPool[tagDist(rng)] };
        t.startTime = timeDist(rng);
        t.endTime = t.startTime + durationDist(rng);
        t.priority = 1.0;
        dataset.tasks.push_back(std::move(t));
    }

    return dataset;
}

std::vector<DisruptionEvent> generateDisruptionWave(const Dataset& dataset,
                                                      const std::vector<int>& scales,
                                                      unsigned int seed) {
    std::mt19937 rng(seed);
    std::vector<int> taskIds;
    taskIds.reserve(dataset.tasks.size());
    for (const auto& t : dataset.tasks) taskIds.push_back(t.id);
    std::shuffle(taskIds.begin(), taskIds.end(), rng);

    std::vector<DisruptionEvent> events;
    double timestamp = 0.0;
    for (int scale : scales) {
        DisruptionEvent event;
        event.type = EventType::Disruption;
        event.timestamp = timestamp++;
        int n = std::min<int>(scale, static_cast<int>(taskIds.size()));
        event.affectedTaskIds.assign(taskIds.begin(), taskIds.begin() + n);
        events.push_back(std::move(event));
    }
    return events;
}

}  // namespace rescue
