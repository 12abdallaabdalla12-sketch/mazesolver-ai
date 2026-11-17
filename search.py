"""Four-direction, unit-cost grid search. Coordinates are (row, column)."""

from collections import deque
from dataclasses import dataclass
import heapq
from time import perf_counter


@dataclass
class SearchResult:
    path: list[tuple[int, int]]
    expanded: list[tuple[int, int]]
    elapsed_ms: float

    @property
    def found(self):
        return bool(self.path)

    @property
    def path_length(self):
        return len(self.path) - 1 if self.found else None


def validate(grid, start, goal):
    if not grid or not grid[0] or any(len(row) != len(grid[0]) for row in grid):
        raise ValueError("The grid must be a nonempty rectangle.")
    if any(cell not in (0, 1) for row in grid for cell in row):
        raise ValueError("Use 0 for open cells and 1 for walls.")
    for row, col in (start, goal):
        if not (0 <= row < len(grid) and 0 <= col < len(grid[0])):
            raise ValueError("Start and goal must be inside the grid.")
        if grid[row][col] == 1:
            raise ValueError("Start and goal must be open cells.")


def neighbors(grid, cell):
    row, col = cell
    for dr, dc in ((-1, 0), (0, 1), (1, 0), (0, -1)):
        nr, nc = row + dr, col + dc
        if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] == 0:
            yield nr, nc


def finish(parent, goal, expanded, started):
    path = []
    if goal in parent:
        current = goal
        while current is not None:
            path.append(current)
            current = parent[current]
        path.reverse()
    return SearchResult(path, expanded, (perf_counter() - started) * 1000)


def bfs(grid, start, goal):
    """Expand cells in increasing distance from the start, using a FIFO queue."""
    started = perf_counter()
    validate(grid, start, goal)
    frontier = deque([start])
    parent = {start: None}
    expanded = []
    while frontier:
        current = frontier.popleft()
        expanded.append(current)
        if current == goal:
            break
        for cell in neighbors(grid, current):
            if cell not in parent:
                parent[cell] = current
                frontier.append(cell)
    return finish(parent, goal, expanded, started)


def manhattan(cell, goal):
    return abs(cell[0] - goal[0]) + abs(cell[1] - goal[1])


def astar(grid, start, goal):
    """Choose the lowest f = g + h. For tied f, prefer larger g, then coordinates."""
    started = perf_counter()
    validate(grid, start, goal)
    frontier = [(manhattan(start, goal), 0, start)]
    cost = {start: 0}
    parent = {start: None}
    closed = set()
    expanded = []
    while frontier:
        _, _, current = heapq.heappop(frontier)
        if current in closed:
            continue
        closed.add(current)
        expanded.append(current)
        if current == goal:
            break
        for cell in neighbors(grid, current):
            new_cost = cost[current] + 1
            if cell not in closed and new_cost < cost.get(cell, float("inf")):
                cost[cell] = new_cost
                parent[cell] = current
                priority = new_cost + manhattan(cell, goal)
                heapq.heappush(frontier, (priority, -new_cost, cell))
    return finish(parent, goal, expanded, started)


ALGORITHMS = {"BFS": bfs, "A*": astar}
