import tkinter as tk


class Game:  # the main class that we call "Game"
    def __init__(self):  # setting up the window for the game here
        self.root = tk.Tk()  # saying this window will use tkinter
        self.root.title("Tower Defense Ultra Mode")
        self.root.protocol("WM_DELETE_WINDOW", self.end)

        self.frame = tk.Frame(master=self.root)
        self.frame.grid(row=0, column=0)

        self.canvas = tk.Canvas(
            master=self.frame,
            width=MAP_SIZE,
            height=MAP_SIZE,
            bg="white",
            highlightthickness=0,
        )  # actually creates a window and puts our frame on it
        self.canvas.grid(
            row=0, column=0, rowspan=2, columnspan=1
        )  # makes the window called "canvas" complete

        self.display_board = DisplayBoard(self)
        self.info_board = InfoBoard(self)
        self.tower_box = TowerBox(self)
        self.mouse = Mouse(self)
        self.game_map = Map()
        self.wave_generator = WaveGenerator(self)
        self.run()  # calls the function 'def run(self):'
        self.root.mainloop()  # starts running the tkinter graphics loop

    def run(self):
        self.update()  # calls the function 'def update(self):'
        self.paint()  # calls the function 'def paint(self):'
        self.root.after(50, self.run)  # refresh @ 20 Hz

    def end(self):
        self.root.destroy()  # closes the game window and ends the program

    def update(self):
        self.mouse.update()
        self.wave_generator.update()
        self.display_board.update()
        for projectile in PROJECTILES:
            projectile.update()
        for x, y in product(range(GRID_SIZE), repeat=2):
            BLOCK_GRID[x][y].update()  # updates each block one by one
        for monster in MONSTERS:
            monster.update()

        global MONSTERS_BY_HEALTH
        global MONSTERS_BY_HEALTH_REVERSED
        global MONSTERS_BY_DISTANCE
        global MONSTERS_BY_DISTANCE_REVERSED
        global MONSTERS_LIST
        MONSTERS_BY_HEALTH = sorted(MONSTERS, key=lambda x: x.health, reverse=True)
        MONSTERS_BY_DISTANCE = sorted(
            MONSTERS, key=lambda x: x.distance_traveled, reverse=True
        )
        MONSTERS_BY_HEALTH_REVERSED = MONSTERS_BY_HEALTH[::-1]
        MONSTERS_BY_DISTANCE_REVERSED = MONSTERS_BY_DISTANCE[::-1]
        MONSTERS_LIST = [
            MONSTERS_BY_HEALTH,
            MONSTERS_BY_HEALTH_REVERSED,
            MONSTERS_BY_DISTANCE,
            MONSTERS_BY_DISTANCE_REVERSED,
        ]

        for x, y in product(range(GRID_SIZE), repeat=2):
            if TOWER_GRID[x][y]:
                TOWER_GRID[x][y].update()  # updates each tower one by one

    def paint(self):
        self.canvas.delete(tk.ALL)  # clear the screen
        self.game_map.paint(self.canvas)
        self.mouse.paint(self.canvas)  # draw the mouse dot
        for x, y in product(range(GRID_SIZE), repeat=2):
            if TOWER_GRID[x][y]:
                TOWER_GRID[x][y].paint(self.canvas)
        for monster in MONSTERS_BY_DISTANCE_REVERSED:
            monster.paint(self.canvas)
        for projectile in PROJECTILES:
            projectile.paint(self.canvas)
        if DISPLAY_TOWER:
            DISPLAY_TOWER.paint_select(self.canvas)
        self.display_board.paint()
