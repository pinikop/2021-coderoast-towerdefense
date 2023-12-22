# IMPORTANT INFORMATION: the use of 'self' ALWAYS refers to the class that it is in.
# EVERY FUNCTION INSIDE OF A CLASS MUST DECLARE SELF!
# ex: 'def exampleFunction(self, input1, input2):

import math
import random
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
TOWER_GRID = [[None for y in range(GRID_SIZE)] for x in range(GRID_SIZE)]
PATH_LIST = []
SPAWN_X = 0
SPAWN_Y = 0
MONSTERS = []
MONSTERS_BY_HEALTH = []
MONSTERS_BY_HEALTH_REVERSED = []
MONSTERS_BY_DISTANCE = []
MONSTERS_BY_DISTANCE_REVERSED = []
monstersListList = [
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
        self.RUN = True  # creating a variable RUN. does nothing yet.hu
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

        self.displayboard = Displayboard(self)

        self.infoboard = Infoboard(self)

        self.towerbox = Towerbox(self)

        self.mouse = Mouse(self)

        self.gameMap = Map()

        self.wavegenerator = Wavegenerator(self)

        self.run()  # calls the function 'def run(self):'

        self.root.mainloop()  # starts running the tkinter graphics loop

    def run(self):
        if self.RUN is True:  # always going to be true for now
            self.update()  # calls the function 'def update(self):'
            self.paint()  # calls the function 'def paint(self):'

            self.root.after(
                50, self.run
            )  # does a run of the function every 50/1000 = 1/20 of a second

    def end(self):
        self.root.destroy()  # closes the game window and ends the program

    def update(self):
        self.mouse.update()
        self.wavegenerator.update()
        self.displayboard.update()
        for i in range(len(PROJECTILES)):
            try:
                PROJECTILES[i].update()
            except:
                pass
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                BLOCK_GRID[x][
                    y
                ].update()  # updates each block one by one by going to its 'def update():' command
        for i in range(len(MONSTERS)):
            try:
                MONSTERS[i].update()
            except:
                pass
        global MONSTERS_BY_HEALTH
        global MONSTERS_BY_HEALTH_REVERSED
        global MONSTERS_BY_DISTANCE
        global MONSTERS_BY_DISTANCE_REVERSED
        global monstersListList
        MONSTERS_BY_HEALTH = sorted(MONSTERS, key=lambda x: x.health, reverse=True)
        MONSTERS_BY_DISTANCE = sorted(
            MONSTERS, key=lambda x: x.distanceTravelled, reverse=True
        )
        MONSTERS_BY_HEALTH_REVERSED = sorted(
            MONSTERS, key=lambda x: x.health, reverse=False
        )
        MONSTERS_BY_DISTANCE_REVERSED = sorted(
            MONSTERS, key=lambda x: x.distanceTravelled, reverse=False
        )
        monstersListList = [
            MONSTERS_BY_HEALTH,
            MONSTERS_BY_HEALTH_REVERSED,
            MONSTERS_BY_DISTANCE,
            MONSTERS_BY_DISTANCE_REVERSED,
        ]

        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if TOWER_GRID[x][y]:
                    TOWER_GRID[x][
                        y
                    ].update()  # updates each tower one by one by going to its 'def update():' command

    def paint(self):
        self.canvas.delete(ALL)  # clear the screen
        self.gameMap.paint(self.canvas)
        self.mouse.paint(
            self.canvas
        )  # draw the mouse dot by going to its 'def paint(canvas):' command
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if TOWER_GRID[x][y]:
                    TOWER_GRID[x][y].paint(self.canvas)
        for i in range(len(MONSTERS_BY_DISTANCE_REVERSED)):
            MONSTERS_BY_DISTANCE_REVERSED[i].paint(self.canvas)
        for i in range(len(PROJECTILES)):
            PROJECTILES[i].paint(self.canvas)
        if DISPLAY_TOWER:
            DISPLAY_TOWER.paintSelect(self.canvas)
        self.displayboard.paint()


class Map:
    def __init__(self):
        self.image = None
        self.loadMap("LeoMap")

    def loadMap(self, mapName):
        self.drawnMap = Image.new("RGBA", (MAP_SIZE, MAP_SIZE), (255, 255, 255, 255))
        self.mapFile = open("texts/mapTexts/" + mapName + ".txt", "r")
        self.gridValues = list(map(int, (self.mapFile.read()).split()))
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                global BLOCK_GRID
                self.blockNumber = self.gridValues[GRID_SIZE * y + x]
                self.blockType = globals()[BLOCK_DICT[self.blockNumber]]
                BLOCK_GRID[x][y] = self.blockType(
                    x * BLOCK_SIZE + BLOCK_SIZE / 2,
                    y * BLOCK_SIZE + BLOCK_SIZE / 2,
                    self.blockNumber,
                    x,
                    y,
                )  # creates a grid of Blocks
                BLOCK_GRID[x][y].paint(self.drawnMap)
        self.drawnMap.save("images/mapImages/" + mapName + ".png")
        self.image = Image.open("images/mapImages/" + mapName + ".png")
        self.image = ImageTk.PhotoImage(self.image)

    def saveMap(self):
        self.mapFile = open("firstMap.txt", "w")
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                self.mapFile.write(BLOCK_GRID[x][y].blockType + " ")
        self.mapFile.close()

    def paint(self, canvas):
        canvas.create_image(0, 0, image=self.image, anchor=NW)


class Wavegenerator:
    def __init__(self, game):
        self.game = game
        self.done = False
        self.currentWave = []
        self.currentMonster = 0
        self.direction = None
        self.gridx = 0
        self.gridy = 0
        self.findSpawn()
        self.decideMove()
        self.ticks = 1
        self.maxTicks = 2
        self.waveFile = open("texts/waveTexts/WaveGenerator2.txt", "r")

    def getWave(self):
        self.game.displayboard.nextWaveButton.canPress = False
        self.currentMonster = 1
        self.waveLine = self.waveFile.readline()
        if len(self.waveLine) == 0:
            self.done = True
        else:
            self.currentWave = self.waveLine.split()
            self.currentWave = list(map(int, self.currentWave))
            self.maxTicks = self.currentWave[0]

    def findSpawn(self):
        global SPAWN_X
        global SPAWN_Y
        for x in range(GRID_SIZE):
            if isinstance(BLOCK_GRID[x][0], PathBlock):
                self.gridx = x
                SPAWN_X = x * BLOCK_SIZE + BLOCK_SIZE / 2
                SPAWN_Y = 0
                return
        for y in range(GRID_SIZE):
            if isinstance(BLOCK_GRID[0][y], PathBlock):
                self.gridy = y
                SPAWN_X = 0
                SPAWN_Y = y * BLOCK_SIZE + BLOCK_SIZE / 2
                return

    def move(self):
        global PATH_LIST
        PATH_LIST.append(self.direction)
        if self.direction == 1:
            self.gridx += 1
        if self.direction == 2:
            self.gridx -= 1
        if self.direction == 3:
            self.gridy += 1
        if self.direction == 4:
            self.gridy -= 1
        self.decideMove()

    def decideMove(self):
        if (
            self.direction != 2
            and self.gridx < GRID_SIZE - 1
            and self.gridy >= 0
            and self.gridy <= GRID_SIZE - 1
        ):
            if isinstance(BLOCK_GRID[self.gridx + 1][self.gridy], PathBlock):
                self.direction = 1
                self.move()
                return

        if (
            self.direction != 1
            and self.gridx > 0
            and self.gridy >= 0
            and self.gridy <= GRID_SIZE - 1
        ):
            if isinstance(BLOCK_GRID[self.gridx - 1][self.gridy], PathBlock):
                self.direction = 2
                self.move()
                return

        if (
            self.direction != 4
            and self.gridy < GRID_SIZE - 1
            and self.gridx >= 0
            and self.gridx <= GRID_SIZE - 1
        ):
            if isinstance(BLOCK_GRID[self.gridx][self.gridy + 1], PathBlock):
                self.direction = 3
                self.move()
                return

        if (
            self.direction != 3
            and self.gridy > 0
            and self.gridx >= 0
            and self.gridx <= GRID_SIZE - 1
        ):
            if isinstance(BLOCK_GRID[self.gridx][self.gridy - 1], PathBlock):
                self.direction = 4
                self.move()
                return

        global PATH_LIST
        PATH_LIST.append(5)

    def spawnMonster(self):
        self.monsterType = globals()[
            MONSTER_DICT[self.currentWave[self.currentMonster]]
        ]
        MONSTERS.append(self.monsterType(0))
        self.currentMonster = self.currentMonster + 1

    def update(self):
        if self.done == False:
            if self.currentMonster == len(self.currentWave):
                self.game.displayboard.nextWaveButton.canPress = True
            else:
                self.ticks = self.ticks + 1
                if self.ticks == self.maxTicks:
                    self.ticks = 0
                    self.spawnMonster()


class NextWaveButton:
    def __init__(self, game):
        self.game = game
        self.x = 450
        self.y = 25
        self.xTwo = 550
        self.yTwo = 50
        self.canPress = True

    def checkPress(self, click, x, y):
        if x >= self.x and y >= self.y and x <= self.xTwo and y <= self.yTwo:
            if self.canPress and click and len(MONSTERS) == 0:
                self.game.wavegenerator.getWave()

    def paint(self, canvas):
        if self.canPress and len(MONSTERS) == 0:
            self.color = "blue"
        else:
            self.color = "red"
        canvas.create_rectangle(
            self.x, self.y, self.xTwo, self.yTwo, fill=self.color, outline=self.color
        )  # draws a rectangle where the pointer is
        canvas.create_text(500, 37, text="Next Wave")


class MyButton(object):
    def __init__(self, x, y, xTwo, yTwo):
        self.x = x
        self.y = y
        self.xTwo = xTwo
        self.yTwo = yTwo

    def checkPress(self, click, x, y):
        if x >= self.x and y >= self.y and x <= self.xTwo and y <= self.yTwo:
            self.pressed()
            return True
        return False

    def pressed(self):
        pass

    def paint(self, canvas):
        canvas.create_rectangle(
            self.x, self.y, self.xTwo, self.yTwo, fill="red", outline="black"
        )


class TargetButton(MyButton):
    def __init__(self, x, y, xTwo, yTwo, myType):
        super(TargetButton, self).__init__(x, y, xTwo, yTwo)
        self.type = myType

    def pressed(self):
        global DISPLAY_TOWER
        DISPLAY_TOWER.targetList = self.type


class StickyButton(MyButton):
    def __init__(self, x, y, xTwo, yTwo):
        super(StickyButton, self).__init__(x, y, xTwo, yTwo)

    def pressed(self):
        global DISPLAY_TOWER
        if DISPLAY_TOWER.stickyTarget == False:
            DISPLAY_TOWER.stickyTarget = True
        else:
            DISPLAY_TOWER.stickyTarget = False


class SellButton(MyButton):
    def __init__(self, x, y, xTwo, yTwo):
        super(SellButton, self).__init__(x, y, xTwo, yTwo)

    def pressed(self):
        global DISPLAY_TOWER
        DISPLAY_TOWER.sold()
        DISPLAY_TOWER = None


class UpgradeButton(MyButton):
    def __init__(self, x, y, xTwo, yTwo):
        super(UpgradeButton, self).__init__(x, y, xTwo, yTwo)

    def pressed(self):
        global MONEY
        global DISPLAY_TOWER
        if MONEY >= DISPLAY_TOWER.upgradeCost:
            MONEY -= DISPLAY_TOWER.upgradeCost
            DISPLAY_TOWER.upgrade()


class Infoboard:
    def __init__(self, game):
        self.canvas = Canvas(
            master=game.frame, width=162, height=174, bg="gray", highlightthickness=0
        )
        self.canvas.grid(row=0, column=1)
        self.image = ImageTk.PhotoImage(Image.open("images/infoBoard.png"))
        self.canvas.create_image(0, 0, image=self.image, anchor=NW)
        self.currentButtons = []

    def buttonsCheck(self, click, x, y):
        if click:
            for i in range(len(self.currentButtons)):
                if self.currentButtons[i].checkPress(click, x, y):
                    self.displaySpecific()
                    return

    def displaySpecific(self):
        self.canvas.delete(ALL)  # clear the screen
        self.canvas.create_image(0, 0, image=self.image, anchor=NW)
        self.currentButtons = []
        if DISPLAY_TOWER == None:
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
            self.currentButtons.append(TargetButton(26, 30, 35, 39, 0))
            self.canvas.create_text(
                37, 28, text="> Health", font=("times", 12), fill="white", anchor=NW
            )

            self.currentButtons.append(TargetButton(26, 50, 35, 59, 1))
            self.canvas.create_text(
                37, 48, text="< Health", font=("times", 12), fill="white", anchor=NW
            )

            self.currentButtons.append(TargetButton(92, 50, 101, 59, 2))
            self.canvas.create_text(
                103, 48, text="> Distance", font=("times", 12), fill="white", anchor=NW
            )

            self.currentButtons.append(TargetButton(92, 30, 101, 39, 3))
            self.canvas.create_text(
                103, 28, text="< Distance", font=("times", 12), fill="white", anchor=NW
            )

            self.currentButtons.append(StickyButton(10, 40, 19, 49))
            self.currentButtons.append(SellButton(5, 145, 78, 168))
            if DISPLAY_TOWER.upgradeCost:
                self.currentButtons.append(UpgradeButton(82, 145, 155, 168))
                self.canvas.create_text(
                    120,
                    157,
                    text="Upgrade: " + str(DISPLAY_TOWER.upgradeCost),
                    font=("times", 12),
                    fill="light green",
                    anchor=CENTER,
                )

            self.canvas.create_text(
                28, 146, text="Sell", font=("times", 22), fill="light green", anchor=NW
            )

            self.currentButtons[DISPLAY_TOWER.targetList].paint(self.canvas)
            if DISPLAY_TOWER.stickyTarget == True:
                self.currentButtons[4].paint(self.canvas)

    def displayGeneric(self):
        self.currentButtons = []
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


class Displayboard:
    def __init__(self, game):
        self.canvas = Canvas(
            master=game.frame, width=600, height=80, bg="gray", highlightthickness=0
        )
        self.canvas.grid(row=2, column=0)
        self.healthbar = Healthbar()
        self.moneybar = Moneybar()
        self.nextWaveButton = NextWaveButton(game)
        self.paint()

    def update(self):
        self.healthbar.update()
        self.moneybar.update()

    def paint(self):
        self.canvas.delete(ALL)  # clear the screen
        self.healthbar.paint(self.canvas)
        self.moneybar.paint(self.canvas)
        self.nextWaveButton.paint(self.canvas)


class Towerbox:
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
        for i in range(50):
            self.box.insert(END, "<None>")
        self.box.grid(row=1, column=1, rowspan=2)
        self.box.bind("<<ListboxSelect>>", self.onselect)

    def onselect(self, event):
        global SELECTED_TOWER
        global DISPLAY_TOWER
        SELECTED_TOWER = str(self.box.get(self.box.curselection()))
        DISPLAY_TOWER = None
        self.game.infoboard.displayGeneric()


class Mouse:
    def __init__(self, game):  # when i define a "Mouse", this is what happens
        self.game = game
        self.x = 0
        self.y = 0
        self.gridx = 0
        self.gridy = 0
        self.xoffset = 0
        self.yoffset = 0
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
        self.canNotPressImage = Image.open("images/mouseImages/HoveringCanNotPress.png")
        self.canNotPressImage = ImageTk.PhotoImage(self.canNotPressImage)

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
            self.xoffset = 0
            self.yoffset = 0
        elif event.widget == self.game.infoboard.canvas:
            self.xoffset = MAP_SIZE
            self.yoffset = 0
        elif event.widget == self.game.towerbox.box:
            self.xoffset = MAP_SIZE
            self.yoffset = 174
        elif event.widget == self.game.displayboard.canvas:
            self.yoffset = MAP_SIZE
            self.xoffset = 0
        self.x = event.x + self.xoffset  # sets the "Mouse" x to the real mouse's x
        self.y = event.y + self.yoffset  # sets the "Mouse" y to the real mouse's y
        if self.x < 0:
            self.x = 0
        if self.y < 0:
            self.y = 0
        self.gridx = int((self.x - (self.x % BLOCK_SIZE)) / BLOCK_SIZE)
        self.gridy = int((self.y - (self.y % BLOCK_SIZE)) / BLOCK_SIZE)

    def update(self):
        if (
            self.gridx >= 0
            and self.gridx <= GRID_SIZE - 1
            and self.gridy >= 0
            and self.gridy <= GRID_SIZE - 1
        ):
            BLOCK_GRID[self.gridx][self.gridy].hoveredOver(self.pressed, self.game)
        else:
            self.game.displayboard.nextWaveButton.checkPress(
                self.pressed, self.x - self.xoffset, self.y - self.yoffset
            )
            self.game.infoboard.buttonsCheck(
                self.pressed, self.x - self.xoffset, self.y - self.yoffset
            )

    def paint(self, canvas):
        if (
            self.gridx >= 0
            and self.gridx <= GRID_SIZE - 1
            and self.gridy >= 0
            and self.gridy <= GRID_SIZE - 1
        ):
            if BLOCK_GRID[self.gridx][self.gridy].canPlace:
                canvas.create_image(
                    self.gridx * BLOCK_SIZE,
                    self.gridy * BLOCK_SIZE,
                    image=self.image,
                    anchor=NW,
                )
            else:
                canvas.create_image(
                    self.gridx * BLOCK_SIZE,
                    self.gridy * BLOCK_SIZE,
                    image=self.canNotPressImage,
                    anchor=NW,
                )


class Healthbar:
    def __init__(self):
        self.text = str(HEALTH)

    def update(self):
        self.text = str(HEALTH)

    def paint(self, canvas):
        canvas.create_text(40, 40, text="Health: " + self.text, fill="black")


class Moneybar:
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
        self.speed = BLOCK_SIZE / 2
        self.damage = damage
        self.speed = speed
        # self.image = Image.open("images/projectileImages/"+self.__class__.__name__+ ".png")
        # self.image = ImageTk.PhotoImage(self.image)

    def update(self):
        try:
            if target.alive == False:
                PROJECTILES.remove(self)
                return
        except:
            if self.hit:
                self.gotMonster()
            self.move()
            self.checkHit()

    def gotMonster(self):
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

    def move(self):
        self.length = (
            (self.x - (self.target.x)) ** 2 + (self.y - (self.target.y)) ** 2
        ) ** 0.5
        self.x += self.speed * ((self.target.x) - self.x) / self.length
        self.y += self.speed * ((self.target.y) - self.y) / self.length

    def checkHit(self):
        if (
            self.speed**2
            > (self.x - (self.target.x)) ** 2 + (self.y - (self.target.y)) ** 2
        ):
            self.hit = True


class PowerShot(TrackingBullet):
    def __init__(self, x, y, damage, speed, target, slow):
        super(PowerShot, self).__init__(x, y, damage, speed, target)
        self.slow = slow
        self.image = Image.open("images/projectileImages/powerShot.png")
        self.image = ImageTk.PhotoImage(self.image)

    def gotMonster(self):
        self.target.health -= self.damage
        if self.target.movement > (self.target.speed) / self.slow:
            self.target.movement = (self.target.speed) / self.slow
        PROJECTILES.remove(self)


class AngledProjectile(Projectile):
    def __init__(self, x, y, damage, speed, angle, givenRange):
        super(AngledProjectile, self).__init__(x, y, damage, speed)
        self.xChange = speed * math.cos(angle)
        self.yChange = speed * math.sin(-angle)
        self.range = givenRange
        self.image = Image.open("images/projectileImages/arrow.png")
        self.image = ImageTk.PhotoImage(self.image.rotate(math.degrees(angle)))
        self.target = None
        self.speed = speed
        self.distance = 0

    def checkHit(self):
        for i in range(len(MONSTERS)):
            if (MONSTERS[i].x - self.x) ** 2 + (
                MONSTERS[i].y - self.y
            ) ** 2 <= BLOCK_SIZE**2:
                self.hit = True
                self.target = MONSTERS[i]
                return

    def gotMonster(self):
        self.target.health -= self.damage
        self.target.tick = 0
        self.target.maxTick = 5
        PROJECTILES.remove(self)

    def move(self):
        self.x += self.xChange
        self.y += self.yChange
        self.distance += self.speed
        if self.distance >= self.range:
            PROJECTILES.remove(self)


class Tower(object):
    def __init__(self, x, y, gridx, gridy):
        self.upgradeCost = None
        self.level = 1
        self.range = 0
        self.clicked = False
        self.x = x
        self.y = y
        self.gridx = gridx
        self.gridy = gridy
        self.image = Image.open(
            "images/towerImages/" + self.__class__.__name__ + "/1.png"
        )
        self.image = ImageTk.PhotoImage(self.image)

    def update(self):
        pass

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
        self.nextLevel()

    def sold(self):
        TOWER_GRID[self.gridx][self.gridy] = None

    def paintSelect(self, canvas):
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
    def __init__(self, x, y, gridx, gridy):
        super(ShootingTower, self).__init__(x, y, gridx, gridy)
        self.bulletsPerSecond = None
        self.ticks = 0
        self.damage = 0
        self.speed = None

    def update(self):
        self.prepareShot()


class TargetingTower(ShootingTower):
    def __init__(self, x, y, gridx, gridy):
        super(TargetingTower, self).__init__(x, y, gridx, gridy)
        self.target = None
        self.targetList = 0
        self.stickyTarget = False

    def prepareShot(self):
        self.checkList = monstersListList[self.targetList]
        if self.ticks != 20 / self.bulletsPerSecond:
            self.ticks += 1
        if self.stickyTarget == False:
            for i in range(len(self.checkList)):
                if (self.range + BLOCK_SIZE / 2) ** 2 >= (
                    self.x - self.checkList[i].x
                ) ** 2 + (self.y - self.checkList[i].y) ** 2:
                    self.target = self.checkList[i]
        if self.target:
            if (
                self.target.alive
                and (self.range + BLOCK_SIZE / 2)
                >= ((self.x - self.target.x) ** 2 + (self.y - self.target.y) ** 2)
                ** 0.5
            ):
                if self.ticks >= 20 / self.bulletsPerSecond:
                    self.shoot()
                    self.ticks = 0
            else:
                self.target = None
        elif self.stickyTarget == True:
            for i in range(len(self.checkList)):
                if (self.range + BLOCK_SIZE / 2) ** 2 >= (
                    self.x - self.checkList[i].x
                ) ** 2 + (self.y - self.checkList[i].y) ** 2:
                    self.target = self.checkList[i]


class ArrowShooterTower(TargetingTower):
    def __init__(self, x, y, gridx, gridy):
        super(ArrowShooterTower, self).__init__(x, y, gridx, gridy)
        self.name = "Arrow Shooter"
        self.infotext = "ArrowShooterTower at [" + str(gridx) + "," + str(gridy) + "]."
        self.range = BLOCK_SIZE * 10
        self.bulletsPerSecond = 1
        self.damage = 10
        self.speed = BLOCK_SIZE
        self.upgradeCost = 50

    def nextLevel(self):
        if self.level == 2:
            self.upgradeCost = 100
            self.range = BLOCK_SIZE * 11
            self.damage = 12
        elif self.level == 3:
            self.upgradeCost = None
            self.bulletsPerSecond = 2

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
    def __init__(self, x, y, gridx, gridy):
        super(BulletShooterTower, self).__init__(x, y, gridx, gridy)
        self.name = "Bullet Shooter"
        self.infotext = "BulletShooterTower at [" + str(gridx) + "," + str(gridy) + "]."
        self.range = BLOCK_SIZE * 6
        self.bulletsPerSecond = 4
        self.damage = 5
        self.speed = BLOCK_SIZE / 2

    def shoot(self):
        PROJECTILES.append(
            TrackingBullet(self.x, self.y, self.damage, self.speed, self.target)
        )


class PowerTower(TargetingTower):
    def __init__(self, x, y, gridx, gridy):
        super(PowerTower, self).__init__(x, y, gridx, gridy)
        self.name = "Power Tower"
        self.infotext = "PowerTower at [" + str(gridx) + "," + str(gridy) + "]."
        self.range = BLOCK_SIZE * 8
        self.bulletsPerSecond = 10
        self.damage = 1
        self.speed = BLOCK_SIZE
        self.slow = 3

    def shoot(self):
        PROJECTILES.append(
            PowerShot(self.x, self.y, self.damage, self.speed, self.target, self.slow)
        )


class TackTower(TargetingTower):
    def __init__(self, x, y, gridx, gridy):
        super(TackTower, self).__init__(x, y, gridx, gridy)
        self.name = "Tack Tower"
        self.infotext = "TackTower at [" + str(gridx) + "," + str(gridy) + "]."
        self.range = BLOCK_SIZE * 5
        self.bulletsPerSecond = 1
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
        self.maxHealth = 0
        self.speed = 0.0
        self.movement = 0.0
        self.tick = 0
        self.maxTick = 1
        self.distanceTravelled = distance
        if self.distanceTravelled <= 0:
            self.distanceTravelled = 0
        self.x, self.y = self.positionFormula(self.distanceTravelled)
        self.armor = 0
        self.magicresist = 0
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
        if self.tick >= self.maxTick:
            self.distanceTravelled += self.movement
            self.x, self.y = self.positionFormula(self.distanceTravelled)

            self.movement = self.speed
            self.tick = 0
            self.maxTick = 1
        self.tick += 1

    def positionFormula(self, distance):
        self.xPos = SPAWN_X
        self.yPos = SPAWN_Y + BLOCK_SIZE / 2
        self.blocks = int((distance - (distance % BLOCK_SIZE)) / BLOCK_SIZE)
        if self.blocks != 0:
            for i in range(self.blocks):
                if PATH_LIST[i] == 1:
                    self.xPos += BLOCK_SIZE
                elif PATH_LIST[i] == 2:
                    self.xPos -= BLOCK_SIZE
                elif PATH_LIST[i] == 3:
                    self.yPos += BLOCK_SIZE
                else:
                    self.yPos -= BLOCK_SIZE
        if distance % BLOCK_SIZE != 0:
            if PATH_LIST[self.blocks] == 1:
                self.xPos += distance % BLOCK_SIZE
            elif PATH_LIST[self.blocks] == 2:
                self.xPos -= distance % BLOCK_SIZE
            elif PATH_LIST[self.blocks] == 3:
                self.yPos += distance % BLOCK_SIZE
            else:
                self.yPos -= distance % BLOCK_SIZE
        if PATH_LIST[self.blocks] == 5:
            self.gotThrough()
        return self.xPos, self.yPos

    def killed(self):
        global MONEY
        MONEY += self.value
        self.die()

    def gotThrough(self):
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
            self.x - self.axis + (self.axis * 2 - 2) * self.health / self.maxHealth,
            self.y - self.axis - 2,
            fill="green",
            outline="green",
        )
        canvas.create_image(self.x, self.y, image=self.image, anchor=CENTER)


class Monster1(Monster):
    def __init__(self, distance):
        super(Monster1, self).__init__(distance)
        self.maxHealth = 30
        self.health = self.maxHealth
        self.value = 5
        self.speed = float(BLOCK_SIZE) / 2
        self.movement = BLOCK_SIZE / 3
        self.axis = BLOCK_SIZE / 2


class Monster2(Monster):
    def __init__(self, distance):
        super(Monster2, self).__init__(distance)
        self.maxHealth = 50
        self.health = self.maxHealth
        self.value = 10
        self.speed = float(BLOCK_SIZE) / 4
        self.movement = float(BLOCK_SIZE) / 4
        self.axis = BLOCK_SIZE / 2

    def killed(self):
        global MONEY
        MONEY += self.value
        MONSTERS.append(
            Monster1(self.distanceTravelled + BLOCK_SIZE * (0.5 - random.random()))
        )
        self.die()


class AlexMonster(Monster):
    def __init__(self, distance):
        super(AlexMonster, self).__init__(distance)
        self.maxHealth = 500
        self.health = self.maxHealth
        self.value = 100
        self.speed = float(BLOCK_SIZE) / 5
        self.movement = float(BLOCK_SIZE) / 5
        self.axis = BLOCK_SIZE

    def killed(self):
        global MONEY
        MONEY += self.value
        for i in range(5):
            MONSTERS.append(
                Monster2(self.distanceTravelled + BLOCK_SIZE * (0.5 - random.random()))
            )
        self.die()


class BenMonster(Monster):
    def __init__(self, distance):
        super(BenMonster, self).__init__(distance)
        self.maxHealth = 200
        self.health = self.maxHealth
        self.value = 30
        self.speed = float(BLOCK_SIZE) / 4
        self.movement = float(BLOCK_SIZE) / 4
        self.axis = BLOCK_SIZE / 2

    def killed(self):
        global MONEY
        MONEY += self.value
        for i in range(2):
            MONSTERS.append(
                LeoMonster(
                    self.distanceTravelled + BLOCK_SIZE * (0.5 - random.random())
                )
            )
        self.die()


class LeoMonster(Monster):
    def __init__(self, distance):
        super(LeoMonster, self).__init__(distance)
        self.maxHealth = 20
        self.health = self.maxHealth
        self.value = 2
        self.speed = float(BLOCK_SIZE) / 2
        self.movement = float(BLOCK_SIZE) / 2
        self.axis = BLOCK_SIZE / 4


class MonsterBig(Monster):
    def __init__(self, distance):
        super(MonsterBig, self).__init__(distance)
        self.maxHealth = 1000
        self.health = self.maxHealth
        self.value = 10
        self.speed = float(BLOCK_SIZE) / 6
        self.movement = float(BLOCK_SIZE) / 6
        self.axis = 3 * BLOCK_SIZE / 2


class Block(object):
    def __init__(
        self, x, y, blockNumber, gridx, gridy
    ):  # when i define a "Block", this is what happens
        self.x = x  # sets Block x to the given 'x'
        self.y = y  # sets Block y to the given 'y'
        self.canPlace = True
        self.blockNumber = blockNumber
        self.gridx = gridx
        self.gridy = gridy
        self.image = None
        self.axis = BLOCK_SIZE / 2

    def hoveredOver(self, click, game):
        if click == True:
            global TOWER_GRID
            global MONEY
            if TOWER_GRID[self.gridx][self.gridy]:
                if SELECTED_TOWER == "<None>":
                    TOWER_GRID[self.gridx][self.gridy].clicked = True
                    global DISPLAY_TOWER
                    DISPLAY_TOWER = TOWER_GRID[self.gridx][self.gridy]
                    game.infoboard.displaySpecific()
            elif (
                SELECTED_TOWER != "<None>"
                and self.canPlace == True
                and MONEY >= TOWER_COST[SELECTED_TOWER]
            ):
                self.towerType = globals()[TOWER_DICT[SELECTED_TOWER]]
                TOWER_GRID[self.gridx][self.gridy] = self.towerType(
                    self.x, self.y, self.gridx, self.gridy
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
    def __init__(self, x, y, blockNumber, gridx, gridy):
        super(NormalBlock, self).__init__(x, y, blockNumber, gridx, gridy)


class PathBlock(Block):
    def __init__(self, x, y, blockNumber, gridx, gridy):
        super(PathBlock, self).__init__(x, y, blockNumber, gridx, gridy)
        self.canPlace = False


class WaterBlock(Block):
    def __init__(self, x, y, blockNumber, gridx, gridy):
        super(WaterBlock, self).__init__(x, y, blockNumber, gridx, gridy)
        self.canPlace = False


def main():
    Game()  # start the application at Class Game()


if __name__ == "__main__":
    main()
