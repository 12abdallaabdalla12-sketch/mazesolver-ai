"""Correctness tests; run with: python -m unittest -v"""

from copy import deepcopy
import itertools
from pathlib import Path
import tempfile
import unittest

from benchmark import run_benchmark
from mazes import preset_maps
from search import ALGORITHMS


class SearchTests(unittest.TestCase):
    def check_valid(self, grid, start, goal, result):
        self.assertEqual(len(result.expanded), len(set(result.expanded)))
        if result.found:
            self.assertEqual(result.path[0], start)
            self.assertEqual(result.path[-1], goal)
            for row, col in result.path:
                self.assertTrue(0 <= row < len(grid) and 0 <= col < len(grid[0]))
                self.assertEqual(grid[row][col], 0)
            for a, b in zip(result.path, result.path[1:]):
                self.assertEqual(abs(a[0] - b[0]) + abs(a[1] - b[1]), 1)

    def test_known_shortest_lengths_and_no_route(self):
        cases = [([[0]], (0, 0), (0, 0), 0),
                 ([[0, 0, 0], [0, 0, 0]], (0, 0), (1, 2), 3),
                 ([[0, 1, 0], [0, 1, 0], [0, 0, 0]], (0, 0), (0, 2), 6),
                 ([[0, 1, 0]], (0, 0), (0, 2), None)]
        for name, algorithm in ALGORITHMS.items():
            for grid, start, goal, expected in cases:
                with self.subTest(algorithm=name, expected=expected):
                    result = algorithm(grid, start, goal)
                    self.assertEqual(result.path_length, expected)
                    self.check_valid(grid, start, goal, result)

    def test_exhaustive_small_grids(self):
        # Every wall arrangement with fixed open endpoints on a 3x3 grid.
        cells = [(r, c) for r in range(3) for c in range(3) if (r, c) not in ((0, 0), (2, 2))]
        for bits in itertools.product((0, 1), repeat=len(cells)):
            grid = [[0] * 3 for _ in range(3)]
            for (row, col), bit in zip(cells, bits):
                grid[row][col] = bit
            results = [algorithm(grid, (0, 0), (2, 2)) for algorithm in ALGORITHMS.values()]
            self.assertEqual(results[0].path_length, results[1].path_length)
            for result in results:
                self.check_valid(grid, (0, 0), (2, 2), result)

    def test_presets_reproducible_and_unchanged(self):
        maps = preset_maps()
        self.assertEqual(len(maps), 10)
        self.assertEqual(maps, preset_maps())
        for maze in maps:
            original = deepcopy(maze.grid)
            results = []
            for algorithm in ALGORITHMS.values():
                result = algorithm(maze.grid, maze.start, maze.goal)
                self.check_valid(maze.grid, maze.start, maze.goal, result)
                results.append(result)
            self.assertEqual(results[0].path_length, results[1].path_length)
            self.assertEqual(maze.grid, original)
        self.assertEqual(ALGORITHMS["BFS"](maps[1].grid, maps[1].start, maps[1].goal).path_length, 23)
        for maze in maps[-2:]:
            self.assertFalse(ALGORITHMS["BFS"](maze.grid, maze.start, maze.goal).found)

    def test_invalid_input(self):
        for algorithm in ALGORITHMS.values():
            for grid, start, goal in (([], (0, 0), (0, 0)),
                                     ([[0], [0, 0]], (0, 0), (1, 0)),
                                     ([[1, 0]], (0, 0), (0, 1)),
                                     ([[0, 0]], (-1, 0), (0, 1))):
                with self.assertRaises(ValueError):
                    algorithm(grid, start, goal)

    def test_benchmark_exports_all_cases(self):
        import csv
        import json
        with tempfile.TemporaryDirectory() as folder:
            path = run_benchmark(folder, repeats=2)
            with path.open(newline="", encoding="utf-8") as file:
                rows = list(csv.DictReader(file))
            self.assertEqual(len(rows), 20)
            self.assertEqual({row["algorithm"] for row in rows}, {"BFS", "A*"})
            metadata = json.loads((Path(folder) / "environment.json").read_text())
            self.assertEqual(metadata["repeats"], 2)


if __name__ == "__main__":
    unittest.main()
