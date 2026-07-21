#pragma once
#include <chrono>
#include <fstream>
#include <string>
#include <vector>

namespace rescue {

struct RunResult {
    int disruptionScale = 0;
    double incrementalTimeMs = 0.0;
    double naiveTimeMs = 0.0;
    int incrementalUnassigned = 0;  // tasks left uncovered after repair
    int naiveUnassigned = 0;        // tasks left uncovered after full resolve
};

class Timer {
public:
    Timer() : start_(std::chrono::steady_clock::now()) {}
    double elapsedMs() const {
        auto end = std::chrono::steady_clock::now();
        return std::chrono::duration<double, std::milli>(end - start_).count();
    }

private:
    std::chrono::steady_clock::time_point start_;
};

// Minimal hand-rolled JSON writer -- deliberately no external dependency so
// the build stays plain STL for now. Swap for a real JSON lib later if the
// output shape grows.
inline bool writeResultsJson(const std::string& path, const std::vector<RunResult>& results) {
    std::ofstream out(path);
    if (!out) return false;
    out << "[\n";
    for (size_t i = 0; i < results.size(); ++i) {
        const auto& r = results[i];
        out << "  {\n"
            << "    \"disruptionScale\": " << r.disruptionScale << ",\n"
            << "    \"incrementalTimeMs\": " << r.incrementalTimeMs << ",\n"
            << "    \"naiveTimeMs\": " << r.naiveTimeMs << ",\n"
            << "    \"incrementalUnassigned\": " << r.incrementalUnassigned << ",\n"
            << "    \"naiveUnassigned\": " << r.naiveUnassigned << "\n"
            << "  }" << (i + 1 < results.size() ? "," : "") << "\n";
    }
    out << "]\n";
    return out.good();
}

// Writes results.json to every plausible location so the dashboard finds it
// no matter where the binary was launched from (project root, build/, or a
// Visual Studio Debug/Release subfolder). Missing directories are simply
// skipped -- writing to at least one path is enough.
inline std::vector<std::string> writeResultsEverywhere(const std::vector<RunResult>& results) {
    const std::vector<std::string> candidates = {
        "results.json",
        "dashboard/results.json",
        "../dashboard/results.json",
        "../../dashboard/results.json",
    };
    std::vector<std::string> written;
    for (const auto& path : candidates)
        if (writeResultsJson(path, results)) written.push_back(path);
    return written;
}

}  // namespace rescue
