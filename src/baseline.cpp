#include "baseline.hpp"

namespace rescue {

NaiveBaseline::NaiveBaseline(std::vector<Resource> resources, std::vector<Task> tasks)
    : solver_(std::move(resources), std::move(tasks)) {}

std::vector<Assignment> NaiveBaseline::resolveFromScratch() {
    return solver_.initialAssign();
}

}  // namespace rescue
