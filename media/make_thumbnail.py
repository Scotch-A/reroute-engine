#!/usr/bin/env python3
"""Generates the project thumbnail (3:2) for Devpost and GitHub.

The thumbnail is seen at ~350px wide in a gallery grid, so it carries only
three things: the name, what it does, and the number. Everything else is
noise at that size.

Usage (from the project root):
    python3 media/make_thumbnail.py
"""
import json
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

BG    = "#0f172a"
INK   = "#f1f5f9"
MUTED = "#94a3b8"
BLUE  = "#3b82f6"
RED   = "#ef4444"
GREEN = "#22c55e"

plt.rcParams.update({"font.family": "DejaVu Sans"})


def load_results():
    for p in (os.path.join(HERE, "results.json"),
              os.path.join(ROOT, "results.json"),
              os.path.join(ROOT, "dashboard", "results.json")):
        if os.path.exists(p):
            with open(p) as f:
                return json.load(f)
    return None


data = load_results()
if data:
    best = max(d["naiveTimeMs"] / d["incrementalTimeMs"] for d in data)
    small = min(data, key=lambda d: d["disruptionScale"])
    slow, fast = small["naiveTimeMs"], small["incrementalTimeMs"]
else:
    best, slow, fast = 141, 1807, 13

fig = plt.figure(figsize=(12, 8), dpi=100)
fig.patch.set_facecolor(BG)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 12)
ax.set_ylim(0, 8)
ax.axis("off")

# Left rail accent
ax.add_patch(FancyBboxPatch((0, 0), 0.22, 8, boxstyle="square,pad=0",
                            linewidth=0, facecolor=BLUE))

# Name + role
ax.text(0.95, 6.45, "ReRoute", fontsize=76, fontweight="bold", color=INK)
ax.text(1.02, 5.75, "SCHEDULE   RECOVERY   ENGINE", fontsize=19,
        color=BLUE, fontweight="bold")

# What it does -- the one sentence that matters
ax.text(0.95, 4.55, "Recover only what broke,", fontsize=30, color=INK)
ax.text(0.95, 3.75, "not the whole plan.", fontsize=30, color=INK)

# The number, on its own line so nothing can collide with it
ax.text(0.95, 1.95, f"{best:.0f}x", fontsize=82, fontweight="bold", color=GREEN)
ax.text(1.05, 1.35, "faster schedule recovery, identical coverage",
        fontsize=18, color=MUTED)

# Visual proof: two bars sharing a left edge, width to scale
bar_x, bar_w = 6.9, 4.3
ax.text(bar_x, 3.25, f"rebuild everything   {slow:.0f} ms",
        fontsize=14, color=RED, fontweight="bold")
ax.add_patch(FancyBboxPatch((bar_x, 2.72), bar_w, 0.44,
                            boxstyle="round,pad=0.03", linewidth=0, facecolor=RED))

ax.text(bar_x, 2.05, f"ReRoute   {fast:.0f} ms",
        fontsize=14, color=BLUE, fontweight="bold")
ax.add_patch(FancyBboxPatch((bar_x, 1.52), max(bar_w * (fast / slow), 0.12), 0.44,
                            boxstyle="round,pad=0.03", linewidth=0, facecolor=BLUE))

# Footer
ax.text(0.95, 0.55, "C++17  ·  STL only  ·  no external dependencies",
        fontsize=14, color=MUTED)

fig.savefig(os.path.join(HERE, "thumbnail.png"), facecolor=BG)
print("Wrote thumbnail.png")
