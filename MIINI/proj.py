import tkinter as tk
import random
from tkinter import ttk

# Sub App 1: Random Walk Simulation
class RandomWalkApp(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("2D Random Walk Simulation")
        self.geometry("600x650")
        self.step_size = 5
        self.num_steps = 1000

        self.canvas = tk.Canvas(self, width=600, height=600, bg="white")
        self.canvas.pack()

        self.start_button = tk.Button(self, text="Start Random Walk", command=self.run_simulation)
        self.start_button.pack(pady=10)

    def run_simulation(self):
        self.canvas.delete("all")
        x, y = 300, 300  # Start in the center
        self.canvas.create_oval(x-2, y-2, x+2, y+2, fill="red", outline="red")  # Start point

        for _ in range(self.num_steps):
            direction = random.choice(["up", "down", "left", "right"])
            if direction == "up":
                y -= self.step_size
            elif direction == "down":
                y += self.step_size
            elif direction == "left":
                x -= self.step_size
            elif direction == "right":
                x += self.step_size

            self.canvas.create_oval(x-1, y-1, x+1, y+1, fill="blue", outline="blue")
            self.canvas.update()

class SubApp2(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Bouncing Ball Simulation")
        self.geometry("600x600")
        self.canvas = tk.Canvas(self, width=600, height=600, bg="white")
        self.canvas.pack()
        self.ball = self.canvas.create_oval(290, 290, 310, 310, fill="green")
        self.dx, self.dy = 3, 2
        self.animate()

    def animate(self):
        self.canvas.move(self.ball, self.dx, self.dy)
        coords = self.canvas.coords(self.ball)
        if coords[0] <= 0 or coords[2] >= 600:
            self.dx = -self.dx
        if coords[1] <= 0 or coords[3] >= 600:
            self.dy = -self.dy
        self.after(20, self.animate)

class MonteCarloPiApp(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Monte Carlo π Estimation")
        self.geometry("700x850")

        # Simulation parameters
        self.canvas_size = 700
        self.num_samples = 5000
        self.delay_ms = 1  # milliseconds between points

        # State
        self.total_points = 0
        self.inside_circle = 0

        # Canvas & controls
        self.canvas = tk.Canvas(self, width=self.canvas_size, height=self.canvas_size, bg="white")
        self.canvas.pack()

        # Live π‐estimate label
        self.label = tk.Label(self, text="π Estimate: Not started", font=("Arial", 14))
        self.label.pack(pady=10)

        self.start_button = tk.Button(self, text="Start Simulation", command=self.start_simulation)
        self.start_button.pack(pady=5)

        # Draw the square border
        self.canvas.create_rectangle(0, 0, self.canvas_size, self.canvas_size, outline="black")

        # Draw quarter-circle arc from (600,0) to (0,600)
        r = self.canvas_size
        self.canvas.create_arc(-r, -r, r, r,
                               start=0, extent=-90,
                               style="pieslice", fill="#e0f7fa", outline="black")

        # On-canvas counter
        self.count_text = self.canvas.create_text(
            10, self.canvas_size - 10,
            text="Inside: 0 / Total: 0",
            anchor="sw",
            font=("Arial", 12),
            fill="black"
        )

    def start_simulation(self):
        # Reset state and UI
        self.canvas.delete("dot")
        self.total_points = 0
        self.inside_circle = 0
        self.canvas.itemconfig(self.count_text, text="Inside: 0 / Total: 0")
        self.label.config(text="π Estimate: Not started")
        self.start_button.config(state="disabled")

        # Kick off the animated loop
        self.after(self.delay_ms, self._animate_step)

    def _animate_step(self):
        # Plot one point
        x = random.uniform(0, self.canvas_size)
        y = random.uniform(0, self.canvas_size)
        self.total_points += 1

        if x*x + y*y <= self.canvas_size*self.canvas_size:
            self.inside_circle += 1
            color = "green"
        else:
            color = "red"

        self.canvas.create_oval(x, y, x+1.5, y+1.5,
                                fill=color, outline=color, tags="dot")

        # Update on-canvas counter
        self.canvas.itemconfig(
            self.count_text,
            text=f"Inside: {self.inside_circle} / Total: {self.total_points}"
        )

        # **Dynamically update the π estimate label every step**
        pi_est = 4 * self.inside_circle / self.total_points
        self.label.config(text=f"π Estimate: {pi_est:.6f}")

        # Continue animation or finish
        if self.total_points < self.num_samples:
            self.after(self.delay_ms, self._animate_step)
        else:
            self.start_button.config(state="normal")# Main App Window
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Main App")
        self.geometry("400x300")

        ttk.Label(self, text="Main App Interface", font=("Arial", 16)).pack(pady=20)
        ttk.Button(self, text="Open Sub App 1 (Random Walk)", command=self.open_subapp1).pack(pady=10)
        ttk.Button(self, text="Open Sub App 2 (Bouncing Ball)", command=self.open_subapp2).pack(pady=10)
        ttk.Button(self, text="Open Sub App 3 (Monte carlo)", command=self.open_subapp3).pack(pady=10)

    def open_subapp1(self):
        RandomWalkApp(self)
    def open_subapp2(self):
        SubApp2(self)
    def open_subapp3(self):
        MonteCarloPiApp(self)

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
