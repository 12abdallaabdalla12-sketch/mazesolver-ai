"""Run this file to open the interactive maze solver."""

from copy import deepcopy
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from benchmark import run_benchmark
from mazes import preset_maps
from search import ALGORITHMS


COLORS = {"wall": "#243449", "open": "#ffffff", "expanded": "#bfdbfe",
          "path": "#fbbf24", "start": "#059669", "goal": "#e05252"}


class MazeApp:
    def __init__(self, root):
        self.root = root
        root.title("MazeSolver | A* and BFS")
        root.geometry("1100x780")
        root.minsize(880, 660)
        root.configure(background="#f4f6fa")
        style = ttk.Style(root)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("TFrame", background="#f4f6fa")
        style.configure("TLabel", background="#f4f6fa", foreground="#243449", font=("Segoe UI", 10))
        style.configure("TRadiobutton", background="#f4f6fa", font=("Segoe UI", 10))
        style.configure("TButton", padding=(10, 7), font=("Segoe UI", 10))
        self.maps = {maze.name: maze for maze in preset_maps()}
        self.map_name = tk.StringVar(value=next(iter(self.maps)))
        self.algorithm = tk.StringVar(value="A*")
        self.tool = tk.StringVar(value="Wall")
        self.delay = tk.IntVar(value=18)
        self.status = tk.StringVar(value="")
        self.results = {}
        self.expanded = set()
        self.path = set()
        self.running = False
        self.after_id = None
        self.cell_ids = {}
        self.cell_size = 1
        self.origin = (0, 0)

        outer = ttk.Frame(root, padding=18)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="MazeSolver", font=("Segoe UI", 24, "bold")).pack(anchor="w")
        ttk.Label(outer, text="Explore the same maze with informed and uninformed search.").pack(anchor="w", pady=(2, 14))

        map_bar = ttk.Frame(outer)
        map_bar.pack(fill="x", pady=(0, 10))
        ttk.Label(map_bar, text="Preset map").pack(side="left", padx=(0, 8))
        chooser = ttk.Combobox(map_bar, textvariable=self.map_name, values=list(self.maps), state="readonly", width=36)
        chooser.pack(side="left")
        chooser.bind("<<ComboboxSelected>>", lambda event: self.load_maze())
        ttk.Button(map_bar, text="Reset preset", command=self.load_maze).pack(side="left", padx=8)
        ttk.Button(map_bar, text="Remove all walls", command=self.blank_grid).pack(side="left")

        controls = ttk.Frame(outer)
        controls.pack(fill="x", pady=(0, 10))
        ttk.Combobox(controls, textvariable=self.algorithm, values=list(ALGORITHMS), state="readonly", width=6).pack(side="left", padx=(0, 8))
        ttk.Button(controls, text="Run selected", command=self.run_selected).pack(side="left")
        ttk.Button(controls, text="Compare both", command=self.compare).pack(side="left", padx=8)
        ttk.Button(controls, text="Stop", command=self.stop).pack(side="left")
        ttk.Button(controls, text="Clear search", command=self.clear_search).pack(side="left", padx=8)

        tools = ttk.Frame(outer)
        tools.pack(fill="x", pady=(0, 12))
        ttk.Label(tools, text="Draw:").pack(side="left", padx=(0, 5))
        for name in ("Wall", "Erase", "Start", "Goal"):
            ttk.Radiobutton(tools, text=name, value=name, variable=self.tool).pack(side="left", padx=4)
        ttk.Label(tools, text="Animation delay").pack(side="left", padx=(18, 5))
        tk.Scale(tools, from_=0, to=80, orient="horizontal", variable=self.delay, length=135,
                 showvalue=False, highlightthickness=0, background="#f4f6fa").pack(side="left")

        content = ttk.Frame(outer)
        content.pack(fill="both", expand=True)
        content.columnconfigure(0, weight=1)
        content.rowconfigure(0, weight=1)
        self.canvas = tk.Canvas(content, background="#e7edf5", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        self.canvas.bind("<Configure>", lambda event: self.draw())
        self.canvas.bind("<Button-1>", self.edit)
        self.canvas.bind("<B1-Motion>", self.edit)

        side = ttk.Frame(content, width=280)
        side.grid(row=0, column=1, sticky="ns")
        side.grid_propagate(False)
        ttk.Label(side, text="Results", font=("Segoe UI", 15, "bold")).pack(anchor="w", pady=(0, 10))
        self.table = ttk.Treeview(side, columns=("metric", "BFS", "A*"), show="headings", height=4)
        for name, width in (("metric", 120), ("BFS", 77), ("A*", 77)):
            self.table.heading(name, text=name.title() if name == "metric" else name)
            self.table.column(name, width=width, stretch=False, anchor="w" if name == "metric" else "center")
        self.table.pack(anchor="w", fill="x")
        ttk.Label(side, text="Time is a single run in milliseconds. Drawing and animation are excluded.", wraplength=270).pack(anchor="w", pady=(8, 16))
        for label, color in (("Start (S)", "start"), ("Goal (G)", "goal"), ("Wall", "wall"),
                             ("Expanded cell", "expanded"), ("Final path", "path")):
            row = ttk.Frame(side)
            row.pack(anchor="w", pady=3)
            tk.Label(row, background=COLORS[color], width=2).pack(side="left", padx=(0, 8))
            ttk.Label(row, text=label).pack(side="left")
        ttk.Label(side, text="Click or drag to edit.\nMove up, down, left or right.\nEach move costs 1.", wraplength=270).pack(anchor="w", pady=(16, 12))
        ttk.Button(side, text="Export 10-map benchmark", command=self.export).pack(anchor="w", fill="x")
        ttk.Label(side, text="Exports CSV results and computer details using 50 runs per algorithm per map.", wraplength=270).pack(anchor="w", pady=8)
        ttk.Label(outer, textvariable=self.status, wraplength=1000).pack(fill="x", pady=(12, 0))
        self.load_maze()

    def cancel_animation(self):
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.running = False

    def load_maze(self):
        self.cancel_animation()
        maze = self.maps[self.map_name.get()]
        self.grid = deepcopy(maze.grid)
        self.start, self.goal = maze.start, maze.goal
        self.reset_results()
        self.status.set("Choose an algorithm and click Run selected, or edit the maze first.")

    def reset_results(self):
        self.cancel_animation()
        self.results.clear()
        self.expanded.clear()
        self.path.clear()
        self.update_table()
        self.draw()

    def blank_grid(self):
        self.grid = [[0] * len(self.grid[0]) for _ in self.grid]
        self.reset_results()
        self.status.set("Walls removed. Choose Wall to draw a new maze.")

    def clear_search(self):
        self.reset_results()
        self.status.set("Search cleared. The maze is ready.")

    def stop(self):
        was_running = self.running
        self.cancel_animation()
        if was_running:
            self.status.set("Animation stopped. Click Run selected to replay the search.")

    def color(self, cell):
        if cell == self.start:
            return COLORS["start"]
        if cell == self.goal:
            return COLORS["goal"]
        if self.grid[cell[0]][cell[1]]:
            return COLORS["wall"]
        return COLORS["path" if cell in self.path else "expanded" if cell in self.expanded else "open"]

    def draw(self):
        if not hasattr(self, "grid"):
            return
        rows, cols = len(self.grid), len(self.grid[0])
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        self.cell_size = max(1, min((width - 24) // cols, (height - 24) // rows))
        size = self.cell_size
        ox, oy = (width - cols * size) // 2, (height - rows * size) // 2
        self.origin = ox, oy
        self.canvas.delete("all")
        self.cell_ids.clear()
        for row in range(rows):
            for col in range(cols):
                x, y = ox + col * size, oy + row * size
                self.cell_ids[(row, col)] = self.canvas.create_rectangle(x, y, x + size, y + size,
                    fill=self.color((row, col)), outline="#d8e1ed")
        for cell, letter in ((self.start, "S"), (self.goal, "G")):
            self.canvas.create_text(ox + (cell[1] + .5) * size, oy + (cell[0] + .5) * size,
                text=letter, fill="white", font=("Segoe UI", max(8, min(16, size // 2)), "bold"))

    def edit(self, event):
        if self.running:
            return
        ox, oy = self.origin
        cell = ((event.y - oy) // self.cell_size, (event.x - ox) // self.cell_size)
        row, col = cell
        if not (0 <= row < len(self.grid) and 0 <= col < len(self.grid[0])):
            return
        tool = self.tool.get()
        if tool in ("Wall", "Erase"):
            value = int(tool == "Wall")
            if cell in (self.start, self.goal) or self.grid[row][col] == value:
                return
            self.grid[row][col] = value
        elif tool == "Start":
            if cell in (self.start, self.goal):
                return
            self.start = cell
            self.grid[row][col] = 0
        elif tool == "Goal":
            if cell in (self.start, self.goal):
                return
            self.goal = cell
            self.grid[row][col] = 0
        self.reset_results()
        self.status.set("Custom maze. Click Run selected or Compare both to test it.")

    def update_table(self):
        self.table.delete(*self.table.get_children())
        metrics = (("Route found", lambda r: "Yes" if r.found else "No"),
                   ("Path steps", lambda r: r.path_length if r.found else "N/A"),
                   ("Cells expanded", lambda r: len(r.expanded)),
                   ("Time (ms)", lambda r: f"{r.elapsed_ms:.3f}"))
        for label, value in metrics:
            self.table.insert("", "end", values=[label] + [value(self.results[name]) if name in self.results else "-" for name in ("BFS", "A*")])

    def run_selected(self):
        self.cancel_animation()
        name = self.algorithm.get()
        result = ALGORITHMS[name](self.grid, self.start, self.goal)
        self.results[name] = result
        self.update_table()
        self.expanded.clear()
        self.path.clear()
        self.draw()
        self.running = True
        self.status.set(f"Animating {name}. The timer measures the algorithm, not this animation.")
        self.animate(result, name, 0)

    def animate(self, result, name, index):
        self.after_id = None
        batch = max(1, len(result.expanded) // 100)
        for cell in result.expanded[index:index + batch]:
            self.expanded.add(cell)
            self.canvas.itemconfigure(self.cell_ids[cell], fill=self.color(cell))
        index += batch
        if index < len(result.expanded):
            self.after_id = self.root.after(max(1, self.delay.get()), lambda: self.animate(result, name, index))
        else:
            self.running = False
            self.path = set(result.path)
            self.draw()
            self.status.set(f"{name}: {result.path_length} path steps; {len(result.expanded)} cells expanded." if result.found
                            else f"{name}: no route exists. Expanded {len(result.expanded)} reachable cells.")

    def compare(self):
        self.cancel_animation()
        self.results = {name: algorithm(self.grid, self.start, self.goal) for name, algorithm in ALGORITHMS.items()}
        selected = self.results[self.algorithm.get()]
        self.expanded = set(selected.expanded)
        self.path = set(selected.path)
        self.update_table()
        self.draw()
        self.status.set("Both algorithms ran on the same maze. The drawing shows the selected algorithm. Timing is from one run.")

    def export(self):
        self.cancel_animation()
        folder = filedialog.askdirectory(title="Choose a folder for benchmark results")
        if not folder:
            return
        self.status.set("Measuring 10 preset maps. Please wait briefly...")
        self.root.update_idletasks()
        try:
            path = run_benchmark(folder)
        except (OSError, ValueError, AssertionError) as error:
            messagebox.showerror("Could not export results", str(error))
            self.status.set("Export did not finish. See the error message.")
            return
        self.status.set("Benchmark exported: benchmark.csv and environment.json. Custom edits are not included.")
        messagebox.showinfo("Benchmark complete", f"Saved results to:\n{path}\n\nThese measurements use the 10 preset maps.")


if __name__ == "__main__":
    app_root = tk.Tk()
    MazeApp(app_root)
    app_root.mainloop()
