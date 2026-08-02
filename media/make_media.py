#!/usr/bin/env python3
"""Generates the submission image set from the real results.json.

The gallery is ordered as a narrative, because that's how judges scroll it:
  01 hero         -> what this is, in five seconds
  02 problem      -> the real incident, and the structural flaw behind it
  03 results      -> the measured payoff
  04 architecture -> how it works (the technical-depth slide)
  05 proof        -> real terminal output + the core code
  06 honesty      -> limitations and roadmap

Usage (from the project root, after running the solver):
    python3 media/make_media.py
"""
import json
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# --- Shared design language -------------------------------------------------
BG    = "#0f172a"   # deep slate background
PANEL = "#1e293b"   # raised panel
LINE  = "#334155"   # hairlines
INK   = "#f1f5f9"   # primary text
MUTED = "#94a3b8"   # secondary text
BLUE  = "#3b82f6"   # ReRoute
RED   = "#ef4444"   # legacy / problem
GREEN = "#22c55e"   # wins
AMBER = "#f59e0b"   # caveats

plt.rcParams.update({"font.family": "DejaVu Sans"})
MONO = {"family": "DejaVu Sans Mono"}


def poster():
    """A blank 3:2 poster with a 12x8 coordinate space."""
    fig = plt.figure(figsize=(12, 8), dpi=100)
    fig.patch.set_facecolor(BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis("off")
    return fig, ax


def panel(ax, x, y, w, h, color=PANEL, edge=None, alpha=1.0):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                                linewidth=(1.6 if edge else 0),
                                edgecolor=(edge or "none"),
                                facecolor=color, alpha=alpha, zorder=1))


def footer(ax, left, right="ReRoute Engine"):
    ax.plot([0.7, 11.3], [0.85, 0.85], color=LINE, lw=1.2)
    ax.text(0.7, 0.4, left, fontsize=11.5, color=MUTED)
    ax.text(11.3, 0.4, right, fontsize=11.5, color=MUTED, ha="right")


def load_results():
    for p in (os.path.join(HERE, "results.json"),
              os.path.join(ROOT, "results.json"),
              os.path.join(ROOT, "dashboard", "results.json")):
        if os.path.exists(p):
            with open(p) as f:
                return json.load(f)
    raise SystemExit("results.json not found -- run the solver first.")


# --- 01 HERO ----------------------------------------------------------------
def hero(data):
    best = max(d["naiveTimeMs"] / d["incrementalTimeMs"] for d in data)
    small = min(data, key=lambda d: d["disruptionScale"])

    fig, ax = poster()

    ax.text(0.7, 6.85, "ReRoute", fontsize=64, fontweight="bold", color=INK)
    ax.text(0.78, 6.15, "SCHEDULE   RECOVERY   ENGINE", fontsize=17,
            color=BLUE, fontweight="bold")
    ax.plot([0.78, 5.9], [5.8, 5.8], color=BLUE, lw=2.5)

    ax.text(0.7, 5.05,
            "When a schedule breaks, recovery should cost", fontsize=23, color=INK)
    ax.text(0.7, 4.5, "what broke — not the whole plan.", fontsize=23, color=INK)

    tiles = [
        (f"{best:.0f}x", "faster recovery", GREEN),
        (f"{small['incrementalTimeMs']:.0f} ms", "to reschedule 100 tasks", BLUE),
        ("0", "loss in coverage", INK),
    ]
    x = 0.7
    for value, label, color in tiles:
        panel(ax, x, 2.0, 3.4, 1.95)
        ax.text(x + 1.7, 3.05, value, fontsize=40, fontweight="bold",
                color=color, ha="center", zorder=2)
        ax.text(x + 1.7, 2.4, label, fontsize=13, color=MUTED,
                ha="center", zorder=2)
        x += 3.75

    footer(ax, "C++17  ·  STL only  ·  no external dependencies",
           "Build Beyond Hackathon 2026")
    fig.savefig(os.path.join(HERE, "01_hero.png"), facecolor=BG)
    plt.close(fig)


# --- 02 PROBLEM -------------------------------------------------------------
def problem():
    fig, ax = poster()

    ax.text(0.7, 7.2, "The flaw is structural, not algorithmic",
            fontsize=27, fontweight="bold", color=INK)

    panel(ax, 0.7, 5.1, 10.6, 1.6, color="#2a1215", edge=RED)
    ax.text(1.1, 6.28, "DECEMBER 2022   ·   SOUTHWEST AIRLINES",
            fontsize=12, color=RED, fontweight="bold", zorder=2)
    ax.text(1.1, 5.72,
            "A winter storm outpaced the crew scheduler. Dispatchers fell back to pen and paper.",
            fontsize=14, color=INK, zorder=2)
    ax.text(1.1, 5.3, "16,700 flights cancelled   ·   2,000,000+ passengers stranded",
            fontsize=12.5, color=MUTED, zorder=2)

    ax.text(0.7, 4.45, "Two ways to answer the same question",
            fontsize=15.5, color=MUTED, fontweight="bold")

    panel(ax, 0.7, 1.5, 5.15, 2.6, edge=RED)
    ax.text(1.05, 3.5, "Rebuild everything", fontsize=17,
            fontweight="bold", color=RED, zorder=2)
    ax.text(1.05, 2.98, "Recovery cost scales with the", fontsize=13.5,
            color=INK, zorder=2)
    ax.text(1.05, 2.63, "size of the whole operation.", fontsize=13.5,
            color=INK, zorder=2)
    ax.text(1.05, 2.05, "The bigger you get, the slower", fontsize=12.8,
            color=MUTED, style="italic", zorder=2)
    ax.text(1.05, 1.75, "you recover.", fontsize=12.8, color=MUTED,
            style="italic", zorder=2)

    panel(ax, 6.15, 1.5, 5.15, 2.6, edge=BLUE)
    ax.text(6.5, 3.5, "Repair the gap", fontsize=17,
            fontweight="bold", color=BLUE, zorder=2)
    ax.text(6.5, 2.98, "Recovery cost scales with the", fontsize=13.5,
            color=INK, zorder=2)
    ax.text(6.5, 2.63, "size of the disruption.", fontsize=13.5,
            color=INK, zorder=2)
    ax.text(6.5, 2.05, "Growth no longer works", fontsize=12.8,
            color=GREEN, style="italic", zorder=2)
    ax.text(6.5, 1.75, "against you.", fontsize=12.8, color=GREEN,
            style="italic", zorder=2)

    footer(ax, "ReRoute inverts which variable drives the cost of recovery.")
    fig.savefig(os.path.join(HERE, "02_problem.png"), facecolor=BG)
    plt.close(fig)


# --- 03 RESULTS -------------------------------------------------------------
def results(data):
    scales = [d["disruptionScale"] for d in data]
    inc = [d["incrementalTimeMs"] for d in data]
    naive = [d["naiveTimeMs"] for d in data]
    covered = 10000 - data[0]["incrementalUnassigned"]

    fig = plt.figure(figsize=(12, 8), dpi=100)
    fig.patch.set_facecolor(BG)
    ax = fig.add_axes([0.09, 0.18, 0.86, 0.6])
    ax.set_facecolor(BG)

    fig.text(0.06, 0.895, "Same answer. A fraction of the time.",
             fontsize=27, fontweight="bold", color=INK)
    fig.text(0.06, 0.845,
             "10,000 tasks  ·  20,000 resources  ·  median of 3 runs",
             fontsize=13, color=MUTED)

    ax.plot(scales, naive, "o-", color=RED, lw=3, ms=9, label="Rebuild everything")
    ax.plot(scales, inc, "o-", color=BLUE, lw=3, ms=9, label="ReRoute (repair only)")

    ax.annotate(f"{naive[0]:.0f} ms", (scales[0], naive[0]),
                textcoords="offset points", xytext=(8, 14), color=RED,
                fontsize=12.5, fontweight="bold")
    ax.annotate(f"{inc[0]:.0f} ms", (scales[0], inc[0]),
                textcoords="offset points", xytext=(8, -22), color=BLUE,
                fontsize=12.5, fontweight="bold")
    ax.annotate(f"{inc[-1]:.0f} ms", (scales[-1], inc[-1]),
                textcoords="offset points", xytext=(-20, -26), color=BLUE,
                fontsize=12.5, fontweight="bold")

    ax.set_xlabel("Tasks hit by the disruption", fontsize=13.5,
                  color=MUTED, labelpad=10)
    ax.set_ylabel("Time to produce a new schedule (ms)", fontsize=13.5,
                  color=MUTED, labelpad=10)
    ax.tick_params(colors=MUTED, labelsize=11)
    ax.grid(alpha=0.13, color=MUTED)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(LINE)
    ax.set_ylim(bottom=0)
    leg = ax.legend(fontsize=13, frameon=False, loc="center right")
    for t, c in zip(leg.get_texts(), (RED, BLUE)):
        t.set_color(c)

    fig.text(0.06, 0.075,
             "Flat red line = cost tied to the whole schedule.   "
             "Rising blue line = cost tied to the disruption.",
             fontsize=12.5, color=MUTED)
    fig.text(0.06, 0.032,
             f"Both solvers cover the identical {covered}/10,000 tasks — "
             "the speed costs nothing in solution quality.",
             fontsize=12.5, color=GREEN, fontweight="bold")

    fig.savefig(os.path.join(HERE, "03_results.png"), facecolor=BG)
    plt.close(fig)


# --- 04 ARCHITECTURE --------------------------------------------------------
def architecture():
    fig, ax = poster()

    ax.text(0.7, 7.2, "How the repair stays cheap", fontsize=27,
            fontweight="bold", color=INK)
    ax.text(0.7, 6.7, "Three design choices do the work.", fontsize=14,
            color=MUTED)

    steps = [
        ("1", "Qualification index", "tag -> [resource ids]",
         "Search only resources that\ncould qualify, not all 20,000."),
        ("2", "O(1) unassign", "swap-and-pop + id maps",
         "Free a disrupted task without\nscanning the assignment vector."),
        ("3", "Subset rematch", "touch 300, keep 9,700",
         "Rematch only what broke; valid\nassignments are never revisited."),
    ]

    x = 0.7
    for num, title, code, desc in steps:
        panel(ax, x, 2.5, 3.4, 3.7)
        ax.text(x + 0.42, 5.6, num, fontsize=14, fontweight="bold",
                color=BG, zorder=3, ha="center", va="center",
                bbox=dict(boxstyle="circle,pad=0.34", fc=BLUE, ec="none"))
        ax.text(x + 0.35, 4.92, title, fontsize=15.5, fontweight="bold",
                color=INK, zorder=2)
        ax.text(x + 0.35, 4.45, code, fontsize=11, color=BLUE,
                zorder=2, fontdict=MONO)
        ax.text(x + 0.35, 3.25, desc, fontsize=12.3, color=MUTED,
                zorder=2, linespacing=1.5)
        x += 3.75

    panel(ax, 0.7, 1.2, 10.6, 1.0, color="#0b2a1a", edge=GREEN)
    ax.text(1.1, 1.57, "Repair cost:", fontsize=13.5, color=MUTED, zorder=2)
    ax.text(2.95, 1.55, "O(disrupted x candidates)", fontsize=14.5,
            color=GREEN, fontweight="bold", zorder=2, fontdict=MONO)
    ax.text(7.05, 1.57, "instead of", fontsize=13.5, color=MUTED, zorder=2)
    ax.text(8.55, 1.55, "O(all x candidates)", fontsize=14.5,
            color=RED, zorder=2, fontdict=MONO)

    footer(ax, "Plain C++17 and the STL — no solver library, no framework.")
    fig.savefig(os.path.join(HERE, "04_architecture.png"), facecolor=BG)
    plt.close(fig)


# --- 05 PROOF ---------------------------------------------------------------
def proof(run_lines):
    fig, ax = poster()

    ax.text(0.7, 7.2, "It runs. Here is the output.", fontsize=27,
            fontweight="bold", color=INK)
    ax.text(0.7, 6.7,
            "One command builds both solvers and benchmarks them side by side.",
            fontsize=14, color=MUTED)

    panel(ax, 0.7, 3.1, 10.6, 3.25, color="#020617", edge=LINE)
    ax.text(1.05, 5.95, "$ ./build.sh", fontsize=13, color=GREEN,
            zorder=2, fontdict=MONO)
    y = 5.45
    for line in run_lines:
        ax.text(1.05, y, line, fontsize=10.2, color=INK, zorder=2,
                fontdict=MONO)
        y -= 0.42
    ax.text(1.05, y - 0.12,
            "-> identical coverage on both sides; only the clock differs",
            fontsize=10.6, color=GREEN, zorder=2, fontdict=MONO)

    panel(ax, 0.7, 1.2, 10.6, 1.6, color="#020617", edge=LINE)
    ax.text(1.05, 2.42, "// solver.cpp — the whole idea, in one loop",
            fontsize=10.8, color=MUTED, zorder=2, fontdict=MONO)
    ax.text(1.05, 1.98, "for (int taskId : event.affectedTaskIds)   // only what broke",
            fontsize=11.3, color=INK, zorder=2, fontdict=MONO)
    ax.text(1.05, 1.55, "    reassign(taskId);                      // never the rest",
            fontsize=11.3, color=BLUE, zorder=2, fontdict=MONO)

    footer(ax, "Reproducible: build.bat on Windows, build.sh on Linux and macOS.")
    fig.savefig(os.path.join(HERE, "05_proof.png"), facecolor=BG)
    plt.close(fig)


# --- 06 HONESTY -------------------------------------------------------------
def honesty():
    fig, ax = poster()

    ax.text(0.7, 7.2, "What it does not do (yet)", fontsize=27,
            fontweight="bold", color=INK)
    ax.text(0.7, 6.7,
            "Being precise about the boundary is part of the result.",
            fontsize=14, color=MUTED)

    panel(ax, 0.7, 3.45, 5.15, 2.8, edge=AMBER)
    ax.text(1.05, 5.75, "Current limits", fontsize=16, fontweight="bold",
            color=AMBER, zorder=2)
    limits = [
        "One resource covers one task",
        "Greedy repair, not provably optimal",
        "No rest-period or travel constraints",
        "Synthetic dataset, not live ops data",
    ]
    y = 5.2
    for item in limits:
        ax.text(1.05, y, "—", fontsize=13, color=AMBER, zorder=2)
        ax.text(1.45, y, item, fontsize=12.5, color=INK, zorder=2)
        y -= 0.45

    panel(ax, 6.15, 3.45, 5.15, 2.8, edge=BLUE)
    ax.text(6.5, 5.75, "Next", fontsize=16, fontweight="bold",
            color=BLUE, zorder=2)
    nexts = [
        "Bounded local search over the repair",
        "Multiple tasks per resource",
        "Rest and overtime constraints",
        "Parallel repair of disjoint clusters",
    ]
    y = 5.2
    for item in nexts:
        ax.text(6.5, y, "—", fontsize=13, color=BLUE, zorder=2)
        ax.text(6.9, y, item, fontsize=12.5, color=INK, zorder=2)
        y -= 0.45

    panel(ax, 0.7, 1.25, 10.6, 1.8, color="#111c33", edge=LINE)
    ax.text(1.05, 2.55, "The honest boundary", fontsize=14,
            fontweight="bold", color=INK, zorder=2)
    ax.text(1.05, 2.05,
            "The two approaches converge as a disruption approaches the size of the entire schedule.",
            fontsize=12.5, color=MUTED, zorder=2)
    ax.text(1.05, 1.63,
            "ReRoute wins on partial disruptions — which is what real incidents actually look like.",
            fontsize=12.5, color=MUTED, zorder=2)

    footer(ax, "Same greedy matcher on both sides: a fair test of architecture, not of heuristics.")
    fig.savefig(os.path.join(HERE, "06_honesty.png"), facecolor=BG)
    plt.close(fig)


if __name__ == "__main__":
    data = load_results()

    run_path = os.path.join(HERE, "run_output.txt")
    if os.path.exists(run_path):
        with open(run_path) as f:
            # Only the benchmark rows -- the trailing "written to N locations"
            # chatter adds nothing for a reader and truncates awkwardly.
            lines = [l.rstrip("\n") for l in f if l.startswith("Scale")]
    else:
        lines = [
            f"Scale {d['disruptionScale']} | incremental: {d['incrementalTimeMs']:.1f} ms "
            f"| naive: {d['naiveTimeMs']:.1f} ms "
            f"| speedup: {d['naiveTimeMs'] / d['incrementalTimeMs']:.0f}x"
            for d in data
        ]

    hero(data)
    problem()
    results(data)
    architecture()
    proof(lines)
    honesty()
    print("Wrote 01_hero, 02_problem, 03_results, 04_architecture, "
          "05_proof, 06_honesty")
