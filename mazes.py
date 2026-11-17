"""Ten reproducible maps. 0 means an open cell; 1 means a wall."""

from dataclasses import dataclass
import random


@dataclass
class Maze:
    name: str
    grid: list[list[int]]
    start: tuple[int, int]
    goal: tuple[int, int]


def empty(size):
    return [[0] * size for _ in range(size)]


def preset_maps():
    maps = [Maze("01 Open field (10x10)", empty(10), (0, 0), (9, 9))]

    grid = empty(10)
    for row in range(9):
        grid[row][4] = 1
    maps.append(Maze("02 Wall detour (10x10)", grid, (1, 1), (1, 8)))

    grid = empty(15)
    for row, gap in ((3, 13), (6, 1), (9, 13), (12, 1)):
        grid[row] = [int(col != gap) for col in range(15)]
    maps.append(Maze("03 Zigzag (15x15)", grid, (1, 1), (13, 13)))

    grid = empty(20)
    for col, gap in ((6, 3), (13, 16)):
        for row in range(20):
            grid[row][col] = int(row != gap)
    maps.append(Maze("04 Three rooms (20x20)", grid, (1, 1), (18, 18)))

    grid = [[1] * 15 for _ in range(15)]
    for col in range(15):
        grid[0][col] = 0
    for row in range(15):
        grid[row][14] = 0
    maps.append(Maze("05 Narrow corridor (15x15)", grid, (0, 0), (14, 14)))

    for number, size, density, seed in ((6, 20, .15, 7), (7, 20, .25, 21), (8, 30, .30, 42)):
        rng = random.Random(seed)
        grid = [[int(rng.random() < density) for _ in range(size)] for _ in range(size)]
        grid[0][0] = grid[-1][-1] = 0
        maps.append(Maze(f"{number:02} Random seed {seed} ({size}x{size})", grid, (0, 0), (size - 1, size - 1)))

    grid = empty(10)
    grid[8][9] = grid[9][8] = 1
    maps.append(Maze("09 Blocked goal (10x10)", grid, (0, 0), (9, 9)))

    grid = empty(20)
    for row in range(20):
        grid[row][10] = 1
    maps.append(Maze("10 Disconnected (20x20)", grid, (1, 1), (18, 18)))
    return maps
