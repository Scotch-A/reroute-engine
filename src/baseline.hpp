#pragma once
#include "types.hpp"
#include "solver.hpp"
#include <vector>

namespace rescue {

// Simulates a legacy "full re-batch" scheduler: on every disruption it
// throws away the whole assignment and recomputes from scratch. This is
// the behavior documented in Southwest's 2022 meltdown -- it's what makes
// response time scale with the size of the WHOLE problem, not the size of
// the disruption. This class exists purely as the "before" side of the
// demo comparison.
class NaiveBaseline {
public:
    NaiveBaseline(std::vector<Resource> resources, std::vector<Task> tasks);
    std::vector<Assignment> resolveFromScratch();
    int unassignedCount() const { return solver_.unassignedCount(); }

private:
    IncrementalSolver solver_;  // reuses the same greedy matching logic
};

}  // namespace rescue
