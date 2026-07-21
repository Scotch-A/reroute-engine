#!/usr/bin/env bash
# Build + run on Linux / macOS.
# Usage: ./build.sh   (run "chmod +x build.sh" once if needed)
set -euo pipefail
cd "$(dirname "$0")"

if command -v cmake >/dev/null 2>&1; then
    echo "[build] Using CMake..."
    cmake -B build -S .
    cmake --build build --config Release
    BIN=build/reroute
else
    echo "[build] cmake not found, using g++ directly..."
    g++ -std=c++17 -O2 -Isrc \
        src/main.cpp src/data_generator.cpp src/solver.cpp src/baseline.cpp \
        -o reroute
    BIN=./reroute
fi

echo "[build] OK. Running..."
"$BIN"

echo
echo "[build] Done. To view the chart:  cd dashboard && python3 -m http.server"
echo "[build] then open http://localhost:8000"
