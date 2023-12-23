# IMPORTANT INFORMATION: the use of 'self' ALWAYS refers to the class that it is in.
# EVERY FUNCTION INSIDE OF A CLASS MUST DECLARE SELF!
# ex: 'def exampleFunction(self, input1, input2):

import math
import random
from itertools import product
from tkinter import ALL, CENTER, END, NW, Canvas, Frame, Listbox, Tk

from PIL import Image, ImageTk

GRID_SIZE = 30  # the height and width of the array of blocks
BLOCK_SIZE = 20  # pixels wide of each block
MAP_SIZE = GRID_SIZE * BLOCK_SIZE
BLOCK_GRID = [
    [0 for y in range(GRID_SIZE)] for x in range(GRID_SIZE)
]  # creates the array for the grid
BLOCK_DICT = ["NormalBlock", "PathBlock", "WaterBlock"]
MONSTER_DICT = [
    "Monster1",
    "Monster2",
    "AlexMonster",
    "BenMonster",
    "LeoMonster",
    "MonsterBig",
]
TOWER_DICT = {
    "Arrow Shooter": "ArrowShooterTower",
    "Bullet Shooter": "BulletShooterTower",
    "Tack Tower": "TackTower",
    "Power Tower": "PowerTower",
}
TOWER_COST = {
    "Arrow Shooter": 150,
    "Bullet Shooter": 150,
    "Tack Tower": 150,
    "Power Tower": 200,
}
TOWER_GRID = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
PATH_LIST = []
SPAWN_X = 0
SPAWN_Y = 0
MONSTERS = []
MONSTERS_BY_HEALTH = []
MONSTERS_BY_HEALTH_REVERSED = []
MONSTERS_BY_DISTANCE = []
MONSTERS_BY_DISTANCE_REVERSED = []
MONSTERS_LIST = [
    MONSTERS_BY_HEALTH,
    MONSTERS_BY_HEALTH_REVERSED,
    MONSTERS_BY_DISTANCE,
    MONSTERS_BY_DISTANCE_REVERSED,
]
PROJECTILES = []
HEALTH = 100
MONEY = 5000000000
SELECTED_TOWER = "<None>"
DISPLAY_TOWER = None


class Game:  # the main class that we call "Game"
    def __init__(self):  # setting up the window for the game here
        self.root = Tk()  # saying this window will use tkinter
        self.root.title("Tower Defense Ultra Mode")
        self.root.protocol("WM_DELETE_WINDOW", self.end)

        self.frame = Frame(master=self.root)
        self.frame.grid(row=0, column=0)

        self.canvas = Canvas(
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
            try:
                projectile.update()
            except:
                pass
        for x, y in product(range(GRID_SIZE), repeat=2):
            BLOCK_GRID[x][y].update()  # updates each block one by one
        for monster in MONSTERS:
            try:
                monster.update()
            except:
                pass
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
        self.canvas.delete(ALL)  # clear the screen
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


class Map:
    def __init__(self):
        self.image = None
        self.load_map("LeoMap")

    def load_map(self, mapName):
        self.drawn_map = Image.new("RGBA", (MAP_SIZE, MAP_SIZE), (255, 255, 255, 255))
        self.map_file = open("texts/mapTexts/" + mapName + ".txt", "r")
        self.grid_values = list(map(int, (self.map_file.read()).split()))
        for x, y in product(range(GRID_SIZE), repeat=2):
            global BLOCK_GRID
            self.block_number = self.grid_values[GRID_SIZE * y + x]
            self.block_type = globals()[BLOCK_DICT[self.block_number]]
            BLOCK_GRID[x][y] = self.block_type(
                x * BLOCK_SIZE + BLOCK_SIZE / 2,
                y * BLOCK_SIZE + BLOCK_SIZE / 2,
                self.block_number,
                x,
                y,
            )  # creates a grid of Blocks
            BLOCK_GRID[x][y].paint(self.drawn_map)
        self.drawn_map.save("images/mapImages/" + mapName + ".png")
        self.image = Image.open("images/mapImages/" + mapName + ".png")
        self.image = ImageTk.PhotoImage(self.image)

    def paint(self, canvas):
        canvas.create_image(0, 0, image=self.image, anchor=NW)


class WaveGenerator:
    def __init__(self, game):
        self.game = game
        self.done = False
        self.current_wave = []
        self.current_monster = 0
        self.direction = None
        self.grid_x = 0
        self.grid_y = 0
        self.find_spawn()
        self.decide_move()
        self.ticks = 1
        self.max_ticks = 2
        self.wave_file = open("texts/waveTexts/WaveGenerator2.txt", "r")

    def get_wave(self):
        self.game.display_board.next_wave_button.can_press = False
        self.current_monster = 1
        self.waveLine = self.wave_file.readline()
        if len(self.waveLine):
            self.current_wave = self.waveLine.split()
            self.current_wave = list(map(int, self.current_wave))
            self.max_ticks = self.current_wave[0]
        else:
            self.done = True

    def find_spawn(self):
        global SPAWN_X
        global SPAWN_Y
        for x in range(GRID_SIZE):
            if isinstance(BLOCK_GRID[x][0], PathBlock):
                self.grid_x = x
                SPAWN_X = x * BLOCK_SIZE + BLOCK_SIZE / 2
                SPAWN_Y = 0
                return
        for y in range(GRID_SIZE):
            if isinstance(BLOCK_GRID[0][y], PathBlock):
                self.grid_y = y
                SPAWN_X = 0
                SPAWN_Y = y * BLOCK_SIZE + BLOCK_SIZE / 2
                return

    def move(self):
        global PATH_LIST
        PATH_LIST.append(self.direction)
        if self.direction == 1:
            self.grid_x += 1
        if self.direction == 2:
            self.grid_x -= 1
        if self.direction == 3:
            self.grid_y += 1
        if self.direction == 4:
            self.grid_y -= 1
        self.decide_move()

    def decide_move(self):
        if (
            self.direction != 2
            and self.grid_x < GRID_SIZE - 1
            and self.grid_y >= 0
            and self.grid_y <= GRID_SIZE - 1
        ):
            if isinstance(BLOCK_GRID[self.grid_x + 1][self.grid_y], PathBlock):
                self.direction = 1
                self.move()
                return

        if (
            self.direction != 1
            and self.grid_x > 0
            and self.grid_y >= 0
            and self.grid_y <= GRID_SIZE - 1
        ):
            if isinstance(BLOCK_GRID[self.grid_x - 1][self.grid_y], PathBlock):
                self.direction = 2
                self.move()
                return

        if (
            self.direction != 4
            and self.grid_y < GRID_SIZE - 1
            and self.grid_x >= 0
            and self.grid_x <= GRID_SIZE - 1
        ):
            if isinstance(BLOCK_GRID[self.grid_x][self.grid_y + 1], PathBlock):
                self.direction = 3
                self.move()
                return

        if (
            self.direction != 3
            and self.grid_y > 0
            and self.grid_x >= 0
            and self.grid_x <= GRID_SIZE - 1
        ):
            if isinstance(BLOCK_GRID[self.grid_x][self.grid_y - 1], PathBlock):
                self.direction = 4
                self.move()
                return

        global PATH_LIST
        PATH_LIST.append(5)

    def spawn_monster(self):
        monster = globals()[MONSTER_DICT[self.current_wave[self.current_monster]]]
        MONSTERS.append(monster(0))
        self.current_monster = self.current_monster + 1

    def update(self):
        if not self.done:
            if self.current_monster == len(self.current_wave):
                self.game.display_board.next_wave_button.can_press = True
            else:
                self.ticks += +1
                if self.ticks == self.max_ticks:
                    self.ticks = 0
                    self.spawn_monster()


class NextWaveButton:
    def __init__(self, game):
        self.game = game
        self.x1 = 450
        self.y1 = 25
        self.x2 = 550
        self.y2 = 50
        self.can_press = True

    def is_within_bounds(self, x: int, y: int) -> bool:
        return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2

    def check_press(self, click, x, y):
        if (
            self.can_press
            and click
            and len(MONSTERS) == 0
            and self.is_within_bounds(x, y)
        ):
            self.game.wave_generator.get_wave()

    def paint(self, canvas):
        if self.can_press and len(MONSTERS) == 0:
            self.color = "blue"
        else:
            self.color = "red"
        canvas.create_rectangle(
            self.x1, self.y1, self.x2, self.y2, fill=self.color, outline=self.color
        )  # draws a rectangle where the pointer is
        canvas.create_text(500, 37, text="Next Wave")


class BaseButton:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def is_within_bounds(self, x: int, y: int) -> bool:
        return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2

    def check_press(self, click, x, y):
        if self.is_within_bounds(x, y):
            self.pressed()
            return True
        return False

    def pressed(self):
        pass

    def paint(self, canvas):
        canvas.create_rectangle(
            self.x1, self.y1, self.x2, self.y2, fill="red", outline="black"
        )


class TargetButton(BaseButton):
    def __init__(self, x1, y1, x2, y2, my_type):
        super(TargetButton, self).__init__(x1, y1, x2, y2)
        self.type = my_type

    def pressed(self):
        global DISPLAY_TOWER
        DISPLAY_TOWER.target_list = self.type


class StickyButton(BaseButton):
    def __init__(self, x1, y1, x2, y2):
        super(StickyButton, self).__init__(x1, y1, x2, y2)

    def pressed(self):
        global DISPLAY_TOWER
        if DISPLAY_TOWER.sticky_target == False:
            DISPLAY_TOWER.sticky_target = True


class SellButton(BaseButton):
    def __init__(self, x1, y1, x2, y2):
        super(SellButton, self).__init__(x1, y1, x2, y2)

    def pressed(self):
        global DISPLAY_TOWER
        DISPLAY_TOWER.sold()
        DISPLAY_TOWER = None


class UpgradeButton(BaseButton):
    def __init__(self, x1, y1, x2, y2):
        super(UpgradeButton, self).__init__(x1, y1, x2, y2)

    def pressed(self):
        global MONEY
        global DISPLAY_TOWER
        if MONEY >= DISPLAY_TOWER.upgrade_cost:
            MONEY -= DISPLAY_TOWER.upgrade_cost
            DISPLAY_TOWER.upgrade()


class InfoBoard:
    def __init__(self, game):
        self.canvas = Canvas(
            master=game.frame, width=162, height=174, bg="gray", highlightthickness=0
        )
        self.canvas.grid(row=0, column=1)
        self.image = ImageTk.PhotoImage(Image.open("images/infoBoard.png"))
        self.canvas.create_image(0, 0, image=self.image, anchor=NW)
        self.current_buttons = []

    def buttons_check(self, click, x, y):
        if click:
            for button in self.current_buttons:
                if button.check_press(click, x, y):
                    self.display_specific()
                    return

    def display_specific(self):
        self.canvas.delete(ALL)  # clear the screen
        self.canvas.create_image(0, 0, image=self.image, anchor=NW)
        self.current_buttons = []
        if DISPLAY_TOWER is None:
            return

        self.towerImage = ImageTk.PhotoImage(
            Image.open(
                "images/towerImages/"
                + DISPLAY_TOWER.__class__.__name__
                + "/"
                + str(DISPLAY_TOWER.level)
                + ".png"
            )
        )
        self.canvas.create_text(80, 75, text=DISPLAY_TOWER.name, font=("times", 20))
        self.canvas.create_image(5, 5, image=self.towerImage, anchor=NW)

        if issubclass(DISPLAY_TOWER.__class__, TargetingTower):
            self.current_buttons.append(TargetButton(26, 30, 35, 39, 0))
            self.canvas.create_text(
                37, 28, text="> Health", font=("times", 12), fill="white", anchor=NW
            )

            self.current_buttons.append(TargetButton(26, 50, 35, 59, 1))
            self.canvas.create_text(
                37, 48, text="< Health", font=("times", 12), fill="white", anchor=NW
            )

            self.current_buttons.append(TargetButton(92, 50, 101, 59, 2))
            self.canvas.create_text(
                103, 48, text="> Distance", font=("times", 12), fill="white", anchor=NW
            )

            self.current_buttons.append(TargetButton(92, 30, 101, 39, 3))
            self.canvas.create_text(
                103, 28, text="< Distance", font=("times", 12), fill="white", anchor=NW
            )

            self.current_buttons.append(StickyButton(10, 40, 19, 49))
            self.current_buttons.append(SellButton(5, 145, 78, 168))
            if DISPLAY_TOWER.upgrade_cost:
                self.current_buttons.append(UpgradeButton(82, 145, 155, 168))
                self.canvas.create_text(
                    120,
                    157,
                    text="Upgrade: " + str(DISPLAY_TOWER.upgrade_cost),
                    font=("times", 12),
                    fill="light green",
                    anchor=CENTER,
                )

            self.canvas.create_text(
                28, 146, text="Sell", font=("times", 22), fill="light green", anchor=NW
            )

            self.current_buttons[DISPLAY_TOWER.target_list].paint(self.canvas)
            if DISPLAY_TOWER.sticky_target:
                self.current_buttons[4].paint(self.canvas)

    def display_generic(self):
        self.current_buttons = []
        if SELECTED_TOWER == "<None>":
            self.text = None
            self.towerImage = None
        else:
            self.text = SELECTED_TOWER + " cost: " + str(TOWER_COST[SELECTED_TOWER])
            self.towerImage = ImageTk.PhotoImage(
                Image.open(
                    "images/towerImages/" + TOWER_DICT[SELECTED_TOWER] + "/1.png"
                )
            )
        self.canvas.delete(ALL)  # clear the screen
        self.canvas.create_image(0, 0, image=self.image, anchor=NW)
        self.canvas.create_text(80, 75, text=self.text)
        self.canvas.create_image(5, 5, image=self.towerImage, anchor=NW)


class DisplayBoard:
    def __init__(self, game):
        self.canvas = Canvas(
            master=game.frame, width=600, height=80, bg="gray", highlightthickness=0
        )
        self.canvas.grid(row=2, column=0)
        self.health_bar = HealthBar()
        self.money_bar = MoneyBar()
        self.next_wave_button = NextWaveButton(game)
        self.paint()

    def update(self):
        self.health_bar.update()
        self.money_bar.update()

    def paint(self):
        self.canvas.delete(ALL)  # clear the screen
        self.health_bar.paint(self.canvas)
        self.money_bar.paint(self.canvas)
        self.next_wave_button.paint(self.canvas)


class TowerBox:
    def __init__(self, game):
        self.game = game
        self.box = Listbox(
            master=game.frame,
            selectmode="SINGLE",
            font=("times", 18),
            height=18,
            width=13,
            bg="gray",
            fg="dark blue",
            bd=1,
            highlightthickness=0,
        )
        self.box.insert(END, "<None>")
        for i in TOWER_DICT:
            self.box.insert(END, i)
        self.box.grid(row=1, column=1, rowspan=2)
        self.box.bind("<<ListboxSelect>>", self.on_select)

    def on_select(self, event):
        global SELECTED_TOWER
        global DISPLAY_TOWER
        SELECTED_TOWER = str(self.box.get(self.box.curselection()))
        DISPLAY_TOWER = None
        self.game.info_board.display_generic()


class Mouse:
    def __init__(self, game):  # when i define a "Mouse", this is what happens
        self.game = game
        self.x = 0
        self.y = 0
        self.grid_x = 0
        self.grid_y = 0
        self.offset_x = 0
        self.offset_y = 0
        self.pressed = False
        game.root.bind(
            "<Button-1>", self.clicked
        )  # whenever left mouse button is pressed, go to def released(event)
        game.root.bind(
            "<ButtonRelease-1>", self.released
        )  # whenever left mouse button is released, go to def released(event)
        game.root.bind(
            "<Motion>", self.motion
        )  # whenever left mouse button is dragged, go to def released(event)
        self.image = Image.open("images/mouseImages/HoveringCanPress.png")
        self.image = ImageTk.PhotoImage(self.image)
        self.can_not_press_image = Image.open(
            "images/mouseImages/HoveringCanNotPress.png"
        )
        self.can_not_press_image = ImageTk.PhotoImage(self.can_not_press_image)

    def clicked(self, event):
        self.pressed = True  # sets a variable
        self.image = Image.open("images/mouseImages/Pressed.png")
        self.image = ImageTk.PhotoImage(self.image)

    def released(self, event):
        self.pressed = False
        self.image = Image.open("images/mouseImages/HoveringCanPress.png")
        self.image = ImageTk.PhotoImage(self.image)

    def motion(self, event):
        if event.widget == self.game.canvas:
            self.offset_x = 0
            self.offset_y = 0
        elif event.widget == self.game.info_board.canvas:
            self.offset_x = MAP_SIZE
            self.offset_y = 0
        elif event.widget == self.game.tower_box.box:
            self.offset_x = MAP_SIZE
            self.offset_y = 174
        elif event.widget == self.game.display_board.canvas:
            self.offset_y = MAP_SIZE
            self.offset_x = 0
        self.x = event.x + self.offset_x  # sets the "Mouse" x to the real mouse's x
        self.y = event.y + self.offset_y  # sets the "Mouse" y to the real mouse's y
        if self.x < 0:
            self.x = 0
        if self.y < 0:
            self.y = 0
        self.grid_x = int((self.x - (self.x % BLOCK_SIZE)) / BLOCK_SIZE)
        self.grid_y = int((self.y - (self.y % BLOCK_SIZE)) / BLOCK_SIZE)

    def is_within_bounds(self):
        return 0 <= self.grid_x <= GRID_SIZE - 1 and 0 <= self.grid_y <= GRID_SIZE - 1

    def update(self):
        if self.is_within_bounds():
            BLOCK_GRID[self.grid_x][self.grid_y].hovered_over(self.pressed, self.game)
        else:
            self.game.display_board.next_wave_button.check_press(
                self.pressed, self.x - self.offset_x, self.y - self.offset_y
            )
            self.game.info_board.buttons_check(
                self.pressed, self.x - self.offset_x, self.y - self.offset_y
            )

    def paint(self, canvas):
        if self.is_within_bounds():
            if BLOCK_GRID[self.grid_x][self.grid_y].can_place:
                canvas.create_image(
                    self.grid_x * BLOCK_SIZE,
                    self.grid_y * BLOCK_SIZE,
                    image=self.image,
                    anchor=NW,
                )
            else:
                canvas.create_image(
                    self.grid_x * BLOCK_SIZE,
                    self.grid_y * BLOCK_SIZE,
                    image=self.can_not_press_image,
                    anchor=NW,
                )


class HealthBar:
    def __init__(self):
        self.text = str(HEALTH)

    def update(self):
        self.text = str(HEALTH)

    def paint(self, canvas):
        canvas.create_text(40, 40, text="Health: " + self.text, fill="black")


class MoneyBar:
    def __init__(self):
        self.text = str(MONEY)

    def update(self):
        self.text = str(MONEY)

    def paint(self, canvas):
        canvas.create_text(240, 40, text="Money: " + self.text, fill="black")


class Projectile(object):
    def __init__(self, x, y, damage, speed):
        self.hit = False
        self.x = x
        self.y = y
        self.damage = damage
        self.speed = speed

    def update(self):
        try:
            if target.alive == False:
                PROJECTILES.remove(self)
                return
        except:
            if self.hit:
                self.got_monster()
            self.move()
            self.check_hit()

    def got_monster(self):
        self.target.health -= self.damage
        PROJECTILES.remove(self)

    def paint(self, canvas):
        canvas.create_image(self.x, self.y, image=self.image)


class TrackingBullet(Projectile):
    def __init__(self, x, y, damage, speed, target):
        super(TrackingBullet, self).__init__(x, y, damage, speed)
        self.target = target
        self.image = Image.open("images/projectileImages/bullet.png")
        self.image = ImageTk.PhotoImage(self.image)

    @property
    def delta_x(self):
        return self.target.x - self.x

    @property
    def delta_y(self):
        return self.target.y - self.y

    def move(self):
        self.length = (self.delta_x**2 + self.delta_y**2) ** 0.5
        self.x += self.speed * self.delta_x / self.length
        self.y += self.speed * self.delta_y / self.length

    def check_hit(self):
        self.hit = self.speed**2 > self.delta_x**2 + self.delta_y**2


class PowerShot(TrackingBullet):
    def __init__(self, x, y, damage, speed, target, slow):
        super(PowerShot, self).__init__(x, y, damage, speed, target)
        self.slow = slow
        self.image = Image.open("images/projectileImages/powerShot.png")
        self.image = ImageTk.PhotoImage(self.image)

    def got_monster(self):
        self.target.health -= self.damage
        if self.target.movement > (self.target.speed) / self.slow:
            self.target.movement = (self.target.speed) / self.slow
        PROJECTILES.remove(self)


class AngledProjectile(Projectile):
    def __init__(self, x, y, damage, speed, angle, givenRange):
        super(AngledProjectile, self).__init__(x, y, damage, speed)
        self.change_x = speed * math.cos(angle)
        self.change_y = speed * math.sin(-angle)
        self.range = givenRange
        self.image = Image.open("images/projectileImages/arrow.png")
        self.image = ImageTk.PhotoImage(self.image.rotate(math.degrees(angle)))
        self.target = None
        self.speed = speed
        self.distance = 0

    def check_hit(self):
        for monster in MONSTERS:
            if (monster.x - self.x) ** 2 + (monster.y - self.y) ** 2 <= BLOCK_SIZE**2:
                self.hit = True
                self.target = monster
                return

    def got_monster(self):
        self.target.health -= self.damage
        self.target.tick = 0
        self.target.max_tick = 5
        PROJECTILES.remove(self)

    def move(self):
        self.x += self.change_x
        self.y += self.change_y
        self.distance += self.speed
        if self.distance >= self.range:
            PROJECTILES.remove(self)


class Tower(object):
    def __init__(self, x, y, grid_x, grid_y):
        self.upgrade_cost = None
        self.level = 1
        self.range = 0
        self.clicked = False
        self.x = x
        self.y = y
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.image = Image.open(
            "images/towerImages/" + self.__class__.__name__ + "/1.png"
        )
        self.image = ImageTk.PhotoImage(self.image)

    def upgrade(self):
        self.level = self.level + 1
        self.image = Image.open(
            "images/towerImages/"
            + self.__class__.__name__
            + "/"
            + str(self.level)
            + ".png"
        )
        self.image = ImageTk.PhotoImage(self.image)
        self.next_level()

    def sold(self):
        TOWER_GRID[self.grid_x][self.grid_y] = None

    def paint_select(self, canvas):
        canvas.create_oval(
            self.x - self.range,
            self.y - self.range,
            self.x + self.range,
            self.y + self.range,
            fill=None,
            outline="white",
        )

    def paint(self, canvas):
        canvas.create_image(self.x, self.y, image=self.image, anchor=CENTER)


class ShootingTower(Tower):
    def __init__(self, x, y, grid_x, grid_y):
        super(ShootingTower, self).__init__(x, y, grid_x, grid_y)
        self.bullets_per_second = None
        self.ticks = 0
        self.damage = 0
        self.speed = None

    def update(self):
        self.prepare_shot()


class TargetingTower(ShootingTower):
    def __init__(self, x, y, grid_x, grid_y):
        super(TargetingTower, self).__init__(x, y, grid_x, grid_y)
        self.target = None
        self.target_list = 0
        self.sticky_target = False

    def prepare_shot(self):
        self.check_list = MONSTERS_LIST[self.target_list]
        if self.ticks != 20 / self.bullets_per_second:
            self.ticks += 1
        if not self.sticky_target:
            for cl in self.check_list:
                if (self.range + BLOCK_SIZE / 2) ** 2 >= (self.x - cl.x) ** 2 + (
                    self.y - cl.y
                ) ** 2:
                    self.target = cl
        if self.target:
            if (
                self.target.alive
                and (self.range + BLOCK_SIZE / 2)
                >= ((self.x - self.target.x) ** 2 + (self.y - self.target.y) ** 2)
                ** 0.5
            ):
                if self.ticks >= 20 / self.bullets_per_second:
                    self.shoot()
                    self.ticks = 0
            else:
                self.target = None
        elif self.sticky_target:
            for cl in self.check_list:
                if (self.range + BLOCK_SIZE / 2) ** 2 >= (self.x - cl.x) ** 2 + (
                    self.y - cl.y
                ) ** 2:
                    self.target = cl


class ArrowShooterTower(TargetingTower):
    def __init__(self, x, y, grid_x, grid_y):
        super(ArrowShooterTower, self).__init__(x, y, grid_x, grid_y)
        self.name = "Arrow Shooter"
        self.info_text = (
            "ArrowShooterTower at [" + str(grid_x) + "," + str(grid_y) + "]."
        )
        self.range = BLOCK_SIZE * 10
        self.bullets_per_second = 1
        self.damage = 10
        self.speed = BLOCK_SIZE
        self.upgrade_cost = 50

    def next_level(self):
        if self.level == 2:
            self.upgrade_cost = 100
            self.range = BLOCK_SIZE * 11
            self.damage = 12
        elif self.level == 3:
            self.upgrade_cost = None
            self.bullets_per_second = 2

    def shoot(self):
        self.angle = math.atan2(self.y - self.target.y, self.target.x - self.x)
        PROJECTILES.append(
            AngledProjectile(
                self.x,
                self.y,
                self.damage,
                self.speed,
                self.angle,
                self.range + BLOCK_SIZE / 2,
            )
        )


class BulletShooterTower(TargetingTower):
    def __init__(self, x, y, grid_x, grid_y):
        super(BulletShooterTower, self).__init__(x, y, grid_x, grid_y)
        self.name = "Bullet Shooter"
        self.info_text = (
            "BulletShooterTower at [" + str(grid_x) + "," + str(grid_y) + "]."
        )
        self.range = BLOCK_SIZE * 6
        self.bullets_per_second = 4
        self.damage = 5
        self.speed = BLOCK_SIZE / 2

    def shoot(self):
        PROJECTILES.append(
            TrackingBullet(self.x, self.y, self.damage, self.speed, self.target)
        )


class PowerTower(TargetingTower):
    def __init__(self, x, y, grid_x, grid_y):
        super(PowerTower, self).__init__(x, y, grid_x, grid_y)
        self.name = "Power Tower"
        self.info_text = "PowerTower at [" + str(grid_x) + "," + str(grid_y) + "]."
        self.range = BLOCK_SIZE * 8
        self.bullets_per_second = 10
        self.damage = 1
        self.speed = BLOCK_SIZE
        self.slow = 3

    def shoot(self):
        PROJECTILES.append(
            PowerShot(self.x, self.y, self.damage, self.speed, self.target, self.slow)
        )


class TackTower(TargetingTower):
    def __init__(self, x, y, grid_x, grid_y):
        super(TackTower, self).__init__(x, y, grid_x, grid_y)
        self.name = "Tack Tower"
        self.info_text = "TackTower at [" + str(grid_x) + "," + str(grid_y) + "]."
        self.range = BLOCK_SIZE * 5
        self.bullets_per_second = 1
        self.damage = 10
        self.speed = BLOCK_SIZE

    def shoot(self):
        for i in range(8):
            self.angle = math.radians(i * 45)
            PROJECTILES.append(
                AngledProjectile(
                    self.x, self.y, self.damage, self.speed, self.angle, self.range
                )
            )


class Monster(object):
    def __init__(self, distance):
        self.alive = True
        self.image = None
        self.health = 0
        self.max_health = 0
        self.speed = 0.0
        self.movement = 0.0
        self.tick = 0
        self.max_tick = 1
        self.distance_traveled = distance
        if self.distance_traveled <= 0:
            self.distance_traveled = 0
        self.x, self.y = self.position_formula(self.distance_traveled)
        self.armor = 0
        self.magic_resist = 0
        self.value = 0
        self.image = Image.open(
            "images/monsterImages/" + self.__class__.__name__ + ".png"
        )
        self.image = ImageTk.PhotoImage(self.image)

    def update(self):
        if self.health <= 0:
            self.killed()
        self.move()

    def move(self):
        if self.tick >= self.max_tick:
            self.distance_traveled += self.movement
            self.x, self.y = self.position_formula(self.distance_traveled)

            self.movement = self.speed
            self.tick = 0
            self.max_tick = 1
        self.tick += 1

    def position_formula(self, distance):
        self.pos_x = SPAWN_X
        self.pos_y = SPAWN_Y + BLOCK_SIZE / 2
        self.blocks = int((distance - (distance % BLOCK_SIZE)) / BLOCK_SIZE)
        if self.blocks != 0:
            for i in range(self.blocks):
                if PATH_LIST[i] == 1:
                    self.pos_x += BLOCK_SIZE
                elif PATH_LIST[i] == 2:
                    self.pos_x -= BLOCK_SIZE
                elif PATH_LIST[i] == 3:
                    self.pos_y += BLOCK_SIZE
                else:
                    self.pos_y -= BLOCK_SIZE
        if distance % BLOCK_SIZE != 0:
            if PATH_LIST[self.blocks] == 1:
                self.pos_x += distance % BLOCK_SIZE
            elif PATH_LIST[self.blocks] == 2:
                self.pos_x -= distance % BLOCK_SIZE
            elif PATH_LIST[self.blocks] == 3:
                self.pos_y += distance % BLOCK_SIZE
            else:
                self.pos_y -= distance % BLOCK_SIZE
        if PATH_LIST[self.blocks] == 5:
            self.got_through()
        return self.pos_x, self.pos_y

    def killed(self):
        global MONEY
        MONEY += self.value
        self.die()

    def got_through(self):
        global HEALTH
        HEALTH -= 1
        self.die()

    def die(self):
        self.alive = False
        MONSTERS.remove(self)

    def paint(self, canvas):
        canvas.create_rectangle(
            self.x - self.axis,
            self.y - 3 * self.axis / 2,
            self.x + self.axis - 1,
            self.y - self.axis - 1,
            fill="red",
            outline="black",
        )
        canvas.create_rectangle(
            self.x - self.axis + 1,
            self.y - 3 * self.axis / 2 + 1,
            self.x - self.axis + (self.axis * 2 - 2) * self.health / self.max_health,
            self.y - self.axis - 2,
            fill="green",
            outline="green",
        )
        canvas.create_image(self.x, self.y, image=self.image, anchor=CENTER)


class Monster1(Monster):
    def __init__(self, distance):
        super(Monster1, self).__init__(distance)
        self.max_health = 30
        self.health = self.max_health
        self.value = 5
        self.speed = float(BLOCK_SIZE) / 2
        self.movement = BLOCK_SIZE / 3
        self.axis = BLOCK_SIZE / 2


class Monster2(Monster):
    def __init__(self, distance):
        super(Monster2, self).__init__(distance)
        self.max_health = 50
        self.health = self.max_health
        self.value = 10
        self.speed = float(BLOCK_SIZE) / 4
        self.movement = float(BLOCK_SIZE) / 4
        self.axis = BLOCK_SIZE / 2

    def killed(self):
        global MONEY
        MONEY += self.value
        MONSTERS.append(
            Monster1(self.distance_traveled + BLOCK_SIZE * (0.5 - random.random()))
        )
        self.die()


class AlexMonster(Monster):
    def __init__(self, distance):
        super(AlexMonster, self).__init__(distance)
        self.max_health = 500
        self.health = self.max_health
        self.value = 100
        self.speed = float(BLOCK_SIZE) / 5
        self.movement = float(BLOCK_SIZE) / 5
        self.axis = BLOCK_SIZE

    def killed(self):
        global MONEY
        MONEY += self.value
        for _ in range(5):
            MONSTERS.append(
                Monster2(self.distance_traveled + BLOCK_SIZE * (0.5 - random.random()))
            )
        self.die()


class BenMonster(Monster):
    def __init__(self, distance):
        super(BenMonster, self).__init__(distance)
        self.max_health = 200
        self.health = self.max_health
        self.value = 30
        self.speed = float(BLOCK_SIZE) / 4
        self.movement = float(BLOCK_SIZE) / 4
        self.axis = BLOCK_SIZE / 2

    def killed(self):
        global MONEY
        MONEY += self.value
        for _ in range(2):
            MONSTERS.append(
                LeoMonster(
                    self.distance_traveled + BLOCK_SIZE * (0.5 - random.random())
                )
            )
        self.die()


class LeoMonster(Monster):
    def __init__(self, distance):
        super(LeoMonster, self).__init__(distance)
        self.max_health = 20
        self.health = self.max_health
        self.value = 2
        self.speed = float(BLOCK_SIZE) / 2
        self.movement = float(BLOCK_SIZE) / 2
        self.axis = BLOCK_SIZE / 4


class MonsterBig(Monster):
    def __init__(self, distance):
        super(MonsterBig, self).__init__(distance)
        self.max_health = 1000
        self.health = self.max_health
        self.value = 10
        self.speed = float(BLOCK_SIZE) / 6
        self.movement = float(BLOCK_SIZE) / 6
        self.axis = 3 * BLOCK_SIZE / 2


class Block(object):
    def __init__(
        self, x, y, block_number, grid_x, grid_y
    ):  # when i define a "Block", this is what happens
        self.x = x  # sets Block x to the given 'x'
        self.y = y  # sets Block y to the given 'y'
        self.can_place = True
        self.block_number = block_number
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.image = None
        self.axis = BLOCK_SIZE / 2

    def hovered_over(self, click, game):
        if click:
            global TOWER_GRID
            global MONEY
            if TOWER_GRID[self.grid_x][self.grid_y]:
                if SELECTED_TOWER == "<None>":
                    TOWER_GRID[self.grid_x][self.grid_y].clicked = True
                    global DISPLAY_TOWER
                    DISPLAY_TOWER = TOWER_GRID[self.grid_x][self.grid_y]
                    game.info_board.display_specific()
            elif (
                SELECTED_TOWER != "<None>"
                and self.can_place == True
                and MONEY >= TOWER_COST[SELECTED_TOWER]
            ):
                self.towerType = globals()[TOWER_DICT[SELECTED_TOWER]]
                TOWER_GRID[self.grid_x][self.grid_y] = self.towerType(
                    self.x, self.y, self.grid_x, self.grid_y
                )
                MONEY -= TOWER_COST[SELECTED_TOWER]

    def update(self):
        pass

    def paint(self, draw):
        self.image = Image.open(
            "images/blockImages/" + self.__class__.__name__ + ".png"
        )
        self.offset = (int(self.x - self.axis), int(self.y - self.axis))
        draw.paste(self.image, self.offset)
        self.image = None


class NormalBlock(Block):
    def __init__(self, x, y, block_number, grid_x, grid_y):
        super(NormalBlock, self).__init__(x, y, block_number, grid_x, grid_y)


class PathBlock(Block):
    def __init__(self, x, y, block_number, grid_x, grid_y):
        super(PathBlock, self).__init__(x, y, block_number, grid_x, grid_y)
        self.can_place = False


class WaterBlock(Block):
    def __init__(self, x, y, block_number, grid_x, grid_y):
        super(WaterBlock, self).__init__(x, y, block_number, grid_x, grid_y)
        self.can_place = False


def main():
    Game()  # start the application at Class Game()


if __name__ == "__main__":
    main()
