#include "solver.hpp"
#include <algorithm>
#include <limits>

namespace rescue {

IncrementalSolver::IncrementalSolver(std::vector<Resource> resources, std::vector<Task> tasks)
    : resources_(std::move(resources)), tasks_(std::move(tasks)) {
    for (size_t i = 0; i < resources_.size(); ++i)
        resourceIndexById_[resources_[i].id] = static_cast<int>(i);
    for (size_t i = 0; i < tasks_.size(); ++i)
        taskIndexById_[tasks_[i].id] = static_cast<int>(i);
    resourceBusy_.assign(resources_.size(), false);

    // Build qualification index once: tag -> [resourceIdx, ...]
    // This makes both initialAssign() and repair() scan only the eligible
    // subset of resources instead of all of them.
    for (size_t i = 0; i < resources_.size(); ++i)
        for (const auto& q : resources_[i].qualifications)
            qualIndex_[q].push_back(static_cast<int>(i));
}

bool IncrementalSolver::isEligible(const Resource& r, const Task& t) const {
    for (const auto& req : t.requiredQualifications) {
        bool has = std::find(r.qualifications.begin(), r.qualifications.end(), req)
                   != r.qualifications.end();
        if (!has) return false;
    }
    return r.availableFrom <= t.startTime && r.availableUntil >= t.endTime;
}

double IncrementalSolver::cost(const Resource& r, const Task& t) const {
    return std::abs(t.startTime - r.availableFrom);
}

// Returns the index into resources_ of the best free eligible resource for t,
// or -1 if none exists. Uses qualIndex_ to skip resources that can't possibly
// match -- O(resources_with_required_tag) instead of O(all_resources).
int IncrementalSolver::bestCandidateForTask(const Task& t) const {
    int best = -1;
    double bestCost = std::numeric_limits<double>::max();

    if (!t.requiredQualifications.empty()) {
        // Narrow the search to resources that have the first required tag.
        // isEligible() then checks the remaining tags + time window.
        auto qIt = qualIndex_.find(t.requiredQualifications[0]);
        if (qIt == qualIndex_.end()) return -1;
        for (int rIdx : qIt->second) {
            if (resourceBusy_[rIdx]) continue;
            if (!isEligible(resources_[rIdx], t)) continue;
            double c = cost(resources_[rIdx], t);
            if (c < bestCost) { bestCost = c; best = rIdx; }
        }
    } else {
        for (size_t r = 0; r < resources_.size(); ++r) {
            if (resourceBusy_[r]) continue;
            double c = cost(resources_[r], t);
            if (c < bestCost) { bestCost = c; best = static_cast<int>(r); }
        }
    }
    return best;
}

std::vector<Assignment> IncrementalSolver::initialAssign() {
    assignment_.clear();
    taskToResourceIdx_.clear();
    taskToAssignmentIdx_.clear();
    std::fill(resourceBusy_.begin(), resourceBusy_.end(), false);

    std::vector<int> taskOrder(tasks_.size());
    for (size_t i = 0; i < taskOrder.size(); ++i) taskOrder[i] = static_cast<int>(i);
    std::sort(taskOrder.begin(), taskOrder.end(), [this](int a, int b) {
        return tasks_[a].priority > tasks_[b].priority;
    });

    for (int taskIdx : taskOrder) {
        const Task& t = tasks_[taskIdx];
        int rIdx = bestCandidateForTask(t);
        if (rIdx >= 0) {
            resourceBusy_[rIdx] = true;
            taskToResourceIdx_[t.id] = rIdx;
            taskToAssignmentIdx_[t.id] = assignment_.size();
            assignment_.push_back({ resources_[rIdx].id, t.id, cost(resources_[rIdx], t) });
        }
    }
    return assignment_;
}

std::vector<Assignment> IncrementalSolver::repair(const DisruptionEvent& event) {
    // Phase 1: free resources assigned to disrupted tasks.
    // O(affected_tasks) thanks to taskToResourceIdx_ and taskToAssignmentIdx_.
    for (int taskId : event.affectedTaskIds) {
        auto rIt = taskToResourceIdx_.find(taskId);
        if (rIt == taskToResourceIdx_.end()) continue;   // task was already unassigned

        resourceBusy_[rIt->second] = false;
        taskToResourceIdx_.erase(rIt);

        // O(1) removal from assignment_ via swap-and-pop
        auto aIt = taskToAssignmentIdx_.find(taskId);
        if (aIt != taskToAssignmentIdx_.end()) {
            size_t idx = aIt->second;
            size_t last = assignment_.size() - 1;
            if (idx != last) {
                // Move last element into the vacated slot and update its index.
                assignment_[idx] = assignment_[last];
                taskToAssignmentIdx_[assignment_[idx].taskId] = idx;
            }
            assignment_.pop_back();
            taskToAssignmentIdx_.erase(aIt);
        }
    }

    // Phase 2: re-assign only the affected tasks.
    // Cost: O(affected_tasks × resources_with_required_tag), not O(total_tasks × ...).
    // This is why repair time tracks disruption size, not problem size.
    for (int taskId : event.affectedTaskIds) {
        auto tIt = taskIndexById_.find(taskId);
        if (tIt == taskIndexById_.end()) continue;
        const Task& t = tasks_[tIt->second];

        int rIdx = bestCandidateForTask(t);
        if (rIdx >= 0) {
            resourceBusy_[rIdx] = true;
            taskToResourceIdx_[t.id] = rIdx;
            taskToAssignmentIdx_[t.id] = assignment_.size();
            assignment_.push_back({ resources_[rIdx].id, t.id, cost(resources_[rIdx], t) });
        }
    }
    return assignment_;
}

}  // namespace rescue
