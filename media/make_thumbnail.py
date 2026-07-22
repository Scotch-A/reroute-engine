#!/usr/bin/env python3
"""Generates the project thumbnail (3:2) for Devpost / GitHub.

Usage (from project root):
    python3 media/make_thumbnail.py
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))

# Palette
BG = "#0f172a"       # deep slate
PANEL = "#1e293b"
BLUE = "#3b82f6"
RED = "#ef4444"
GREEN = "#22c55e"
INK = "#f1f5f9"
MUTED = "#94a3b8"

plt.rcParams.update({"font.family": "DejaVu Sans"})

# 3:2 ratio, 1200x800
fig = plt.figure(figsize=(12, 8), dpi=100)
fig.patch.set_facecolor(BG)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 12)
ax.set_ylim(0, 8)
ax.axis("off")

# --- Title block ---
ax.text(0.7, 6.95, "ReRoute", fontsize=68, fontweight="bold", color=INK)
ax.text(0.75, 6.15, "SCHEDULE  RECOVERY  ENGINE", fontsize=18,
        color=BLUE, fontweight="bold")

# thin accent rule
ax.plot([0.8, 6.6], [5.75, 5.75], color=BLUE, lw=2.5)

# --- Tagline ---
ax.text(0.8, 5.15,
        "Recover only what broke — not the whole plan.",
        fontsize=21, color=INK, style="italic")

# --- Hero metric ---
ax.text(0.8, 3.7, "156x", fontsize=76, fontweight="bold", color=GREEN)
ax.text(0.85, 2.85, "faster recovery, identical coverage",
        fontsize=17, color=MUTED)

# --- Mini before/after bars (right side) ---
panel = FancyBboxPatch((7.1, 2.4), 4.3, 3.9, boxstyle="round,pad=0.1",
                       linewidth=0, facecolor=PANEL)
ax.add_patch(panel)

ax.text(7.45, 5.75, "Recovery time", fontsize=14, color=MUTED, fontweight="bold")

# legacy bar (tall, red)
ax.add_patch(FancyBboxPatch((7.55, 3.0), 1.4, 2.35, boxstyle="round,pad=0.02",
                            linewidth=0, facecolor=RED))
ax.text(8.25, 2.62, "legacy", fontsize=13, color=MUTED, ha="center")
ax.text(8.25, 5.5, "1785 ms", fontsize=13, color=RED, ha="center", fontweight="bold")

# reroute bar (tiny, blue)
ax.add_patch(FancyBboxPatch((9.55, 3.0), 1.4, 0.16, boxstyle="round,pad=0.02",
                            linewidth=0, facecolor=BLUE))
ax.text(10.25, 2.62, "ReRoute", fontsize=13, color=MUTED, ha="center")
ax.text(10.25, 3.4, "11 ms", fontsize=13, color=BLUE, ha="center", fontweight="bold")

# --- Footer strip ---
ax.plot([0.8, 11.2], [1.75, 1.75], color="#334155", lw=1.2)
ax.text(0.8, 1.15, "C++17  ·  STL  ·  incremental repair",
        fontsize=15, color=MUTED)
ax.text(11.2, 1.15, "Build Beyond Hackathon", fontsize=14,
        color=MUTED, ha="right")

fig.savefig(os.path.join(HERE, "thumbnail.png"), facecolor=BG)
print("Wrote thumbnail.png into media/")
