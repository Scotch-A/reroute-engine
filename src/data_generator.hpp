#pragma once
#include "types.hpp"
#include <vector>

namespace rescue {

struct DatasetConfig {
    int numResources = 5000;
    int numTasks = 2000;
    int numQualificationTags = 8;
    unsigned int seed = 42;
};

struct Dataset {
    std::vector<Resource> resources;
    std::vector<Task> tasks;
};

// Generates a synthetic resource/task pool (e.g. crew members and flights,
// or workers and warehouse dock slots -- the domain is intentionally generic).
Dataset generateDataset(const DatasetConfig& config);

// Generates a sequence of disruption events at increasing scale, e.g.
// { 300, 1000, 5000, 10000 } affected tasks, to stress-test the solver
// the same way Southwest's 2022 storm did to SkySolver.
std::vector<DisruptionEvent> generateDisruptionWave(const Dataset& dataset,
                                                      const std::vector<int>& scales,
                                                      unsigned int seed = 123);

}  // namespace rescue
