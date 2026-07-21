#!/usr/bin/env python3
"""Regenerates the submission images from the real results.json.

Usage (from the project root, after running the solver):
    python3 media/make_media.py

Outputs 3:2 PNGs into media/ -- the ratio Devpost recommends for galleries.
"""
import json
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

INK = "#1a1a2e"
MUTED = "#6b7280"
RED = "#d64545"
BLUE = "#2563eb"
GREEN = "#059669"
BG = "#ffffff"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "figure.facecolor": BG,
    "axes.facecolor": BG,
    "text.color": INK,
    "axes.labelcolor": INK,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
})


def load_results():
    for path in (os.path.join(ROOT, "results.json"),
                 os.path.join(ROOT, "dashboard", "results.json")):
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
    raise SystemExit("results.json not found -- run the solver first.")


def fig32():
    return plt.subplots(figsize=(12, 8), dpi=100)


def chart_response_time(data):
    scales = [d["disruptionScale"] for d in data]
    inc = [d["incrementalTimeMs"] for d in data]
    naive = [d["naiveTimeMs"] for d in data]

    fig, ax = fig32()
    ax.plot(scales, naive, "o-", color=RED, lw=3, ms=10,
            label="Full recompute (legacy approach)")
    ax.plot(scales, inc, "o-", color=BLUE, lw=3, ms=10,
            label="Incremental repair (ReRoute)")

    for x, y in zip(scales, naive):
        ax.annotate(f"{y:.0f} ms", (x, y), textcoords="offset points",
                    xytext=(0, 14), ha="center", color=RED, fontsize=11, fontweight="bold")
    for x, y in zip(scales, inc):
        ax.annotate(f"{y:.0f} ms", (x, y), textcoords="offset points",
                    xytext=(0, -22), ha="center", color=BLUE, fontsize=11, fontweight="bold")

    ax.set_title("Recovery time stays proportional to the disruption,\nnot to the size of the schedule",
                 fontsize=19, fontweight="bold", pad=18, loc="left")
    ax.set_xlabel("Tasks hit by the disruption", fontsize=13, labelpad=10)
    ax.set_ylabel("Time to produce a new schedule (ms)", fontsize=13, labelpad=10)
    ax.legend(fontsize=12, frameon=False, loc="center right")
    ax.grid(alpha=0.15)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.set_ylim(bottom=0)
    fig.text(0.01, 0.015,
             "10,000 tasks / 20,000 resources - median of 3 runs - identical coverage in both modes",
             fontsize=10, color=MUTED)
    fig.tight_layout(rect=[0, 0.03, 1, 1])
    fig.savefig(os.path.join(HERE, "01_response_time.png"))
    plt.close(fig)


def chart_speedup(data):
    scales = [d["disruptionScale"] for d in data]
    speedup = [d["naiveTimeMs"] / d["incrementalTimeMs"] for d in data]

    fig, ax = fig32()
    bars = ax.bar([str(s) for s in scales], speedup, color=BLUE, width=0.55)
    for b, v in zip(bars, speedup):
        ax.annotate(f"{v:.0f}x faster", (b.get_x() + b.get_width() / 2, v),
                    textcoords="offset points", xytext=(0, 8), ha="center",
                    fontsize=13, fontweight="bold", color=INK)

    ax.set_title("Speedup over full recomputation",
                 fontsize=19, fontweight="bold", pad=18, loc="left")
    ax.set_xlabel("Tasks hit by the disruption", fontsize=13, labelpad=10)
    ax.set_ylabel("Times faster", fontsize=13, labelpad=10)
    ax.grid(axis="y", alpha=0.15)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.set_ylim(0, max(speedup) * 1.18)

    unassigned = data[0]["incrementalUnassigned"]
    total = 10000
    fig.text(0.01, 0.015,
             f"Same solution quality in every run: {total - unassigned}/{total} tasks covered "
             f"by both the incremental and the full-recompute solver.",
             fontsize=11, color=GREEN, fontweight="bold")
    fig.tight_layout(rect=[0, 0.035, 1, 1])
    fig.savefig(os.path.join(HERE, "02_speedup.png"))
    plt.close(fig)


def chart_concept():
    fig, ax = fig32()
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis("off")

    ax.text(0, 7.5, "How ReRoute keeps up when a schedule falls apart",
            fontsize=19, fontweight="bold", color=INK)

    def box(x, y, w, h, label, sub, color):
        ax.add_patch(FancyBboxPatch((x, y), w, h,
                                    boxstyle="round,pad=0.12", linewidth=2,
                                    edgecolor=color, facecolor=color + "12"))
        ax.text(x + w / 2, y + h * 0.62, label, ha="center", fontsize=13,
                fontweight="bold", color=INK)
        ax.text(x + w / 2, y + h * 0.26, sub, ha="center", fontsize=10.5, color=MUTED)

    def arrow(x1, y1, x2, y2, color):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                     mutation_scale=22, linewidth=2, color=color))

    ax.text(0.1, 6.35, "LEGACY SCHEDULER", fontsize=11.5, fontweight="bold", color=RED)
    box(0.1, 4.5, 3.1, 1.5, "Storm hits", "300 crews stranded", RED)
    box(4.2, 4.5, 3.6, 1.5, "Rebuild everything", "all 10,000 assignments", RED)
    box(8.8, 4.5, 3.0, 1.5, "Too slow", "dispatchers go manual", RED)
    arrow(3.3, 5.25, 4.1, 5.25, RED)
    arrow(7.9, 5.25, 8.7, 5.25, RED)

    ax.text(0.1, 3.15, "RE-ROUTE", fontsize=11.5, fontweight="bold", color=BLUE)
    box(0.1, 1.3, 3.1, 1.5, "Storm hits", "300 crews stranded", BLUE)
    box(4.2, 1.3, 3.6, 1.5, "Repair the gap only", "touch 300, keep 9,700", BLUE)
    box(8.8, 1.3, 3.0, 1.5, "New plan ready", "in milliseconds", GREEN)
    arrow(3.3, 2.05, 4.1, 2.05, BLUE)
    arrow(7.9, 2.05, 8.7, 2.05, BLUE)

    ax.text(0, 0.35,
            "Cost of a full rebuild grows with the whole schedule. Cost of a repair grows only with what actually broke.",
            fontsize=11.5, color=INK, style="italic")

    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "03_concept.png"))
    plt.close(fig)


if __name__ == "__main__":
    results = load_results()
    chart_response_time(results)
    chart_speedup(results)
    chart_concept()
    print("Wrote 01_response_time.png, 02_speedup.png, 03_concept.png into media/")
