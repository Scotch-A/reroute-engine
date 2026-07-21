#pragma once
#include "types.hpp"
#include <unordered_map>
#include <vector>

namespace rescue {

// Incremental solver: keeps the current assignment and, on each disruption,
// repairs only the affected subset instead of recomputing everything from
// scratch. This is the core idea that differentiates it from a legacy
// full-batch resolve (see baseline.hpp) -- unbounded full recomputation is
// what let Southwest's SkySolver collapse once disruptions passed a few
// hundred changes in Dec 2022.
class IncrementalSolver {
public:
    IncrementalSolver(std::vector<Resource> resources, std::vector<Task> tasks);

    // Full greedy assignment, called once at startup.
    std::vector<Assignment> initialAssign();

    // Repairs only the tasks/resources touched by the event.
    // TODO(week 2): replace pure-greedy repair with bounded local search
    // (augmenting-path swaps / simulated annealing) to recover the quality
    // greedy-only repair leaves on the table.
    std::vector<Assignment> repair(const DisruptionEvent& event);

    const std::vector<Assignment>& currentAssignment() const { return assignment_; }

    // Tasks with no resource covering them. This is the QUALITY metric that
    // sits opposite the speed metric: a fast repair that leaves flights
    // uncovered isn't a win. Reported alongside timings in results.json.
    int unassignedCount() const {
        return static_cast<int>(tasks_.size()) - static_cast<int>(assignment_.size());
    }

private:
    bool isEligible(const Resource& r, const Task& t) const;
    double cost(const Resource& r, const Task& t) const;

    // O(1) lookup: taskId → index of its resource in resources_
    int bestCandidateForTask(const Task& t) const;

    std::vector<Resource> resources_;
    std::vector<Task> tasks_;
    std::unordered_map<int, int> resourceIndexById_;
    std::unordered_map<int, int> taskIndexById_;
    std::vector<Assignment> assignment_;
    std::vector<bool> resourceBusy_;

    // Fast lookup: taskId → assigned resourceIdx (avoids O(n) scan of assignment_)
    std::unordered_map<int, int> taskToResourceIdx_;
    // Fast removal: taskId → index in assignment_ vector (enables O(1) swap-and-pop)
    std::unordered_map<int, size_t> taskToAssignmentIdx_;
    // Qualification index: tag → list of resource indices that have it
    // (reduces inner search from O(all_resources) to O(resources_with_tag))
    std::unordered_map<std::string, std::vector<int>> qualIndex_;
};

}  // namespace rescue
