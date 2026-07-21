@echo off
REM Build + run on Windows. Works with MSVC (Visual Studio) or MinGW g++.
REM Usage: double-click, or run "build.bat" from a terminal in this folder.

setlocal
cd /d "%~dp0"

where cmake >nul 2>&1
if %errorlevel%==0 goto cmake_build

REM ---- Fallback: direct g++ build (MinGW / MSYS2) ----
where g++ >nul 2>&1
if %errorlevel%==0 (
    echo [build] cmake not found, using g++ directly...
    g++ -std=c++17 -O2 -Isrc src/main.cpp src/data_generator.cpp src/solver.cpp src/baseline.cpp -o reroute.exe
    if errorlevel 1 goto fail
    echo [build] OK. Running...
    reroute.exe
    goto done
)

echo [build] ERROR: neither cmake nor g++ found in PATH.
echo         Install one of:
echo           - Visual Studio with "Desktop development with C++"
echo           - MSYS2/MinGW-w64 ^(g++^)
echo           - CMake ^(https://cmake.org/download/^)
exit /b 1

:cmake_build
echo [build] Using CMake...
cmake -B build -S . || goto fail
cmake --build build --config Release || goto fail
echo [build] OK. Running...
if exist "build\Release\reroute.exe" (
    build\Release\reroute.exe
) else (
    build\reroute.exe
)
goto done

:fail
echo [build] BUILD FAILED
exit /b 1

:done
echo.
echo [build] Done. results.json generated.
echo [build] To view the chart:  cd dashboard ^&^& python -m http.server
echo [build] then open http://localhost:8000
endlocal
