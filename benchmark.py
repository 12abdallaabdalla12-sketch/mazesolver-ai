"""Run both algorithms on identical maps and export actual measurements."""

import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
from statistics import median
import sys

from mazes import preset_maps
from search import ALGORITHMS


def run_benchmark(output_dir, repeats=50):
    if repeats < 1:
        raise ValueError("Repeats must be at least 1.")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for maze in preset_maps():
        samples = {name: [] for name in ALGORITHMS}
        results = {}
        for algorithm in ALGORITHMS.values():
            for _ in range(3):
                algorithm(maze.grid, maze.start, maze.goal)
        for iteration in range(repeats):
            names = list(ALGORITHMS)
            if iteration % 2:
                names.reverse()
            for name in names:
                result = ALGORITHMS[name](maze.grid, maze.start, maze.goal)
                results[name] = result
                samples[name].append(result.elapsed_ms)
        if results["BFS"].path_length != results["A*"].path_length:
            raise AssertionError(f"Shortest path lengths disagree on {maze.name}")
        for name, result in results.items():
            records.append({
                "map": maze.name, "rows": len(maze.grid), "columns": len(maze.grid[0]),
                "walls": sum(sum(row) for row in maze.grid), "algorithm": name,
                "found": result.found, "path_length": result.path_length,
                "expanded_cells": len(result.expanded),
                "median_ms": round(median(samples[name]), 6),
                "min_ms": round(min(samples[name]), 6),
                "max_ms": round(max(samples[name]), 6), "repeats": repeats,
            })
    csv_path = output_dir / "benchmark.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    metadata = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version, "platform": platform.platform(),
        "processor": platform.processor(), "repeats": repeats, "warmup_runs": 3,
        "timing": "Validation, search, and path reconstruction; excludes drawing and animation.",
        "expanded_cells": "Cells removed from the frontier and processed, including start and goal when reached.",
        "movement": "Up, right, down, left. Every move costs 1. No diagonals.",
        "astar_heuristic": "Manhattan distance; ties prefer larger g, then (row, column).",
        "note": "Small timing differences are noisy. Fewer expansions need not imply faster execution.",
    }
    (output_dir / "environment.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return csv_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeats", type=int, default=50)
    parser.add_argument("--output", default=str(Path(__file__).parent / "results"))
    args = parser.parse_args()
    print("Saved:", run_benchmark(args.output, args.repeats))
