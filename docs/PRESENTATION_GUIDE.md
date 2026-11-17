# Six-minute solo presentation guide

Use the speaking notes as prompts and practise with a timer. The eight allocations
add to 360 seconds. The instructor then has one minute for Q&A or transition.
If you include a live demonstration, use the time allocated to slide 5 and shorten
the spoken explanation. Screenshots provide a backup.

| Slide | Topic | Time |
| --- | --- | ---: |
| 1 | Visual Maze Solver | 25 seconds |
| 2 | Maze search problem | 35 seconds |
| 3 | BFS and A* | 55 seconds |
| 4 | Implementation and evaluation | 45 seconds |
| 5 | Same path length, less exploration | 65 seconds |
| 6 | Search effort across 10 maps | 50 seconds |
| 7 | Fewer expansions can still take longer | 45 seconds |
| 8 | Conclusions and limitations | 40 seconds |

## Slide 1: Visual Maze Solver (25 seconds)

My project is a visual maze solver that compares breadth-first search, or BFS, with A* search. The goal is to find a shortest route around walls, then investigate how much work each algorithm needs. The application is interactive, and the comparison uses recorded experiments on ten different maps.

## Slide 2: Maze search problem (35 seconds)

The input is a grid with a start, a goal, and blocked cells. The agent can move up, right, down, or left. Every move costs one, and diagonal movement is disabled. The output is a shortest route or a clear message that the goal cannot be reached. I compare three things: route length, expanded cells, and runtime. Path length counts moves. An expanded cell is a cell removed from the frontier and processed by the algorithm.

## Slide 3: BFS and A* (55 seconds)

BFS uses a first-in, first-out queue. It explores nearby cells first, then moves outward one level at a time. With equal movement costs, this gives a shortest path. A* uses a priority queue. Its priority is f equals g plus h. g is the cost already taken, and h estimates the remaining cost. Here h is Manhattan distance: the row difference plus the column difference from the goal. This estimate ignores walls, so it does not overestimate the true remaining cost under our movement rules. For equal priorities, my implementation prefers larger g, then coordinate order. That tie rule can change expansion counts.

## Slide 4: Implementation and evaluation (45 seconds)

The interface uses Tkinter, and the algorithm code is separate from the display. Ten fixed maps include open spaces, detours, corridors, three seeded random maps, and two unreachable goals. Each method has three warmup runs and fifty measured runs on every map. The order alternates, and the results report the median time. There are one thousand timed searches in total. Timing includes validation, search, and path reconstruction, but excludes the animation. Automated checks also cover known route lengths, unreachable goals, and all one hundred twenty-eight wall arrangements on a small three-by-three grid with fixed endpoints.

## Slide 5: Same path length, less exploration (65 seconds)

These are actual application outputs for the same random map with seed twenty-one. Dark cells are walls, blue cells were expanded, and yellow cells show the final route. Both methods return thirty-eight moves. BFS expands two hundred ninety-three cells. A* expands sixty-eight, about seventy-seven percent fewer. This makes the difference between exploring broadly and using a goal estimate visible. The screenshots are also a backup for the live demonstration. If time allows, I can switch to the application, show Compare both on the wall-detour preset, then show that both algorithms report no route on the blocked-goal preset. The full timing comparison comes from the repeated benchmark, rather than one GUI run.

## Slide 6: Search effort across 10 maps (50 seconds)

This chart shows the number of expanded cells for every preset. A* expands fewer cells on seven maps and the same number on three. Across the set, BFS processes two thousand one hundred eighty-eight cells, and A* processes nine hundred three. That is a fifty-eight point seven percent reduction. The narrow corridor and the two unreachable maps have equal counts because the heuristic provides little or no pruning benefit there. This count describes search effort. It is not a direct measurement of memory, and the result should not be generalized to every possible maze.

## Slide 7: Fewer expansions can still take longer (45 seconds)

Fewer expansions do not always mean a faster program. The rooms example favors A*, but the zigzag and blocked-goal examples favor BFS. On the zigzag map, A* processes slightly fewer cells, yet its median runtime is higher. This is consistent with the extra work of priority-queue operations and heuristic calculations outweighing the saved expansions. I did not profile those operations separately, so this is an explanation of the pattern rather than a measured breakdown. Across all ten maps, A* is faster on five. All of these measurements are below one millisecond, so small timing differences need cautious interpretation.

## Slide 8: Conclusions and limitations (40 seconds)

The project demonstrates a working visual solver and a reproducible comparison. Both methods preserve shortest-path quality on the eight solvable maps and handle unreachable goals. A* reduces search effort on this set, but its runtime benefit depends on the map. The main limitations are small synthetic grids, one computer, static walls, and equal movement costs. A useful extension would be testing larger map sets and measuring memory separately. ChatGPT assisted with coding and writing, and the outputs were checked against tests and recorded results. Thank you.

## Optional live demonstration

Have the app running before the presentation. Keep it to about 20 seconds.

1. Select 02 Wall detour and click Compare both. Point to the identical 23-step paths.
2. Select 09 Blocked goal and click Compare both. Point to Route found: No.
3. Return to the slides. Do not run the 10-map export during the presentation.

## Likely questions

**What makes this an AI project?**
It models states, actions, costs, and a goal, then uses search to plan a route.
A* adds a heuristic that guides which states are explored.

**Why do both algorithms find shortest paths here?**
All moves cost one. BFS explores by distance. A* uses a consistent Manhattan
heuristic for four-direction movement and unit costs.

**What is the difference between g, h, and f?**
g is the cost already taken, h estimates the cost remaining, and f is their sum.

**Does A* always run faster?**
No. It was faster on five of the ten recorded maps. Maintaining the priority
queue and evaluating a heuristic add work that may outweigh fewer expansions.

**Why do the screenshot times differ from the report?**
The screenshot shows one UI run. The report uses a separate benchmark's median
of fifty measured runs per algorithm on each map.

**Why are the two blocked maps included?**
They test whether the algorithms stop and report failure correctly instead of
returning an invalid route or looping.

**Can fewer expanded cells be described as less memory?**
No. The experiment counts processed cells and measures time. It does not measure
memory use directly.

**What are the project's limits?**
Small synthetic maps on one computer, static walls, four-direction movement, and
unit movement cost. Results cannot be generalized to every path-planning task.

**What assistance did you use?**
ChatGPT assisted with coding, debugging guidance, analysis, and drafting. The
application was run and the outputs were checked against tests and benchmark
evidence. The report and README disclose that assistance.

**What would you improve next?**
Use larger map sets, retain individual timings, try different tie rules, and
measure memory separately. Weighted terrain would need a cost-aware baseline.

## Before presenting

- Run the app and practise the two demonstration cases.
- Run python -m unittest -v in the project terminal and understand what it checks.
- Explain the short functions in search.py using docs/CODE_GUIDE.md.
- Read the report's limitations, including timing noise and the tie rule.
- Keep the PowerPoint and report available locally for the presentation.
