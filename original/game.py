import tkinter as tk
from typing import List, Optional, Protocol


class GameObject(Protocol):
    def update(self):
        """Update the game object"""

    def paint(self, canvas: tk.Canvas):
        """Paints the game object"""


class Game:  # the main class that we call "Game"
    def __init__(self, title: str, width: int, height: int, time_step: int = 50):
        self.title = title
        self.width = width
        self.height = height
        self.time_step = time_step

        self.running = False
        self.timer_id: Optional[str] = None

        self.root = tk.Tk()  # saying this window will use tkinter
        self.root.title(title)
        self.root.protocol("WM_DELETE_WINDOW", self.end)

        self.frame = tk.Frame(master=self.root)
        self.frame.grid(row=0, column=0)

        self.canvas = tk.Canvas(
            master=self.frame,
            width=self.width,
            height=self.height,
            bg="white",
            highlightthickness=0,
        )

        # makes the window called "canvas" complete
        self.canvas.grid(row=0, column=0, rowspan=2, columnspan=1)

        self.objects: List[GameObject] = []

    def add_object(self, object: GameObject):
        self.objects.append(object)

    def remove_object(self, object: GameObject):
        self.objects.remove(object)

    def run(self):
        self.running = True
        self._run()
        self.root.mainloop()

    def _run(self):
        self.update()
        self.paint()
        if self.running:
            self.timer_id = self.root.after(self.time_step, self._run)

    def end(self):
        self.running = False
        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)
        self.root.destroy()  # closes the game window and ends the program

    def update(self):
        """Updates the game"""
        for obj in self.objects:
            obj.update()

    def paint(self):
        """Paints the game"""
        self.canvas.delete(tk.ALL)  # clear the screen
        for obj in self.objects:
            obj.paint(self.canvas)
