# Code explanation

Start with search.py. The interface is longer, but the AI algorithms are in this
shorter file. This guide explains what the code does; use the actual source
beside it when preparing for questions.

## The overall task

A state is a tuple (row, column), such as (2, 3). A grid value of 0 means open
and 1 means blocked. A move changes either the row or the column by one. The
algorithms receive the grid, start, and goal, and return a SearchResult.

SearchResult stores the final path, cells expanded in order, and elapsed time.
Its found property is true if the path is nonempty. Its path_length property
subtracts one from the number of path cells because steps are the connections
between cells. If start equals goal, the path has one cell and zero steps.

## Shared functions in search.py

- validate checks that the grid is rectangular and nonempty, contains only 0/1,
  and has valid open start and goal cells.
- neighbors yields legal open neighbors in the order up, right, down, left.
  A generator yields one item at a time rather than constructing a complete list.
- finish follows parent links backward from the goal to the start, reverses that
  list into forward order, and records the elapsed time. If the goal was never
  reached, the returned path is empty.
- manhattan adds the absolute row difference and absolute column difference
  between a cell and the goal.

The dictionary parent maps a cell to the cell that led to it. The start maps to
None. This avoids copying a full route into every frontier entry.

## BFS

1. Put the start into a deque, a queue that removes the oldest entry first.
2. Remove the next cell with popleft and record it as expanded.
3. If it is the goal, stop.
4. For every legal neighbor not already discovered, record its parent and append
   it to the queue.
5. If the queue becomes empty, no route exists.

BFS marks a cell as discovered when adding it to the queue. The parent
dictionary therefore also acts as the discovered set. That prevents multiple
insertions of the same cell. With equal move costs, cells are processed in
increasing path length, which makes the first goal route shortest.

## A*

The cost dictionary stores g, the best known cost from the start. h is Manhattan
distance. The heap chooses the smallest f = g + h.

Each heap entry is (f, -g, cell). The heap compares tuple fields in order:
first f, then -g, then the coordinate tuple. Negative g makes a larger g win
when f values tie. f still has first priority, so this is still A* search.

For each neighbor, the candidate cost is cost[current] + 1. If it improves on
the old cost, update the neighbor's cost and parent, then push its new priority.
An older heap entry may remain in the heap. The closed set prevents processing
the same cell again after it has been expanded.

The code does not reopen closed cells. This is valid here because Manhattan
distance is consistent with four-direction, unit-cost movement. Changing the
movement or heuristic requires checking that assumption again.

An admissible heuristic never overestimates the true remaining cost. A
consistent heuristic also satisfies h(current) <= cost(current,next) + h(next)
for each legal move. Here moving one step changes Manhattan distance by at most
one. Walls may increase the real distance but do not make the estimate too large.

## mazes.py

Maze is a dataclass containing a name, grid, start, and goal. preset_maps creates
the ten test cases. Random maps use random.Random with fixed integer seeds.
The same presets are regenerated for the application, benchmark, and tests.
The two final maps intentionally have no route.

## benchmark.py

Each algorithm receives three warmup runs per map, then fifty measured runs.
The order alternates so BFS is not always first. The benchmark records median,
minimum, and maximum time, path length, and expanded cells. There are 1,000
measured searches and 60 warmup searches in one default benchmark.

The elapsed timer starts before input validation and ends after route
reconstruction. It excludes UI drawing, animation, and saving files. The CSV
stores summary timings, not each individual run. environment.json records the
Python version, operating system, processor information, and metric definitions.

## main.py

MazeApp creates the controls, canvas, result table, and event bindings. Tk's
mainloop listens for events. edit converts a clicked canvas pixel into a grid
coordinate. run_selected runs one search, then animate replays the expansion
order. root.after schedules animation frames without using blocking sleep.
compare runs both methods on the same current grid and updates the table.
export benchmarks the ten fixed presets, rather than the current custom edits.

Stop cancels the replay animation. It does not cancel a running search because
the search finishes before replay begins. The reported time is algorithm time,
not the time taken to watch the animation.

## test_search.py

This file uses unittest. Run python -m unittest -v from the project folder.
The five test methods cover many cases, including every one of the 128 possible
wall arrangements for a 3x3 grid with fixed open endpoints. They check expected
route lengths, legal path steps, failure handling, input validation, reproducible
presets, unchanged grids, agreement between BFS and A*, and complete CSV export.

## Questions to answer in your own words

1. Why is BFS a good baseline? All moves cost one, so it gives a shortest route.
2. What is h? An estimate of remaining cost; here it is Manhattan distance.
3. Why is this AI without training? It uses state-space search and a goal-directed
   heuristic to plan actions. Machine learning is one part of AI, not all of it.
4. Why can two routes differ? Multiple shortest routes can exist. Neighbor and
   tie ordering decide which one is returned.
5. Does a blue cell mean it is on the route? No. It was processed during search;
   only the yellow route is the final answer.
6. Does fewer expansions prove less memory? No. Memory was not measured.
7. What would weighted terrain change? BFS would no longer be a shortest-cost
   baseline; a cost-aware method such as uniform-cost search would be appropriate.
8. Why is one timing screenshot insufficient? A single run is noisy; the report
   uses medians from fifty repeated measurements.
9. What happens when there is no route? The frontier becomes empty and an empty
   path is returned. The application reports no route.
10. What did AI assistance involve? ChatGPT helped generate code, explain fixes,
    analyse measurements, and draft the report and slides. Explain the code and
    evidence honestly; do not claim to have written it without that assistance.

Background references are listed in README.md.
