#pragma once
#include <string>
#include <vector>
#include <cstdint>

// Core data model. Deliberately domain-agnostic: "Resource" can be a crew
// member, a warehouse worker, or a dock slot; "Task" can be a flight leg,
// a shift, or a truck arrival window. The demo narrative uses airline crew
// scheduling (inspired by the 2022 Southwest Airlines meltdown), but the
// engine itself doesn't know or care about airlines.

namespace rescue {

struct Resource {
    int id = -1;
    std::string name;
    std::vector<std::string> qualifications;  // skill/certification tags
    double availableFrom = 0.0;               // simulation time, hours
    double availableUntil = 1e9;
    double restRequiredHours = 0.0;           // TODO(week 2): enforce in solver
};

struct Task {
    int id = -1;
    std::string label;
    std::vector<std::string> requiredQualifications;
    double startTime = 0.0;
    double endTime = 0.0;
    double priority = 1.0;                    // higher = more critical to cover
};

struct Assignment {
    int resourceId = -1;
    int taskId = -1;
    double cost = 0.0;
};

enum class EventType { Disruption, Recovery };

struct DisruptionEvent {
    EventType type = EventType::Disruption;
    std::vector<int> affectedTaskIds;
    std::vector<int> affectedResourceIds;
    double timestamp = 0.0;
};

}  // namespace rescue
