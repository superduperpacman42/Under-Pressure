import random

from sprite import Sprite
from util import *


class Creature(Sprite):
    def __init__(self, pos, weight, image, frames=1):
        super().__init__(pos, image, frames)
        self.weight = weight
        self.bob = 5

    def update(self, game, dt):
        pass

    def draw(self, surface, x, y, t):
        offset = math.sin((t - self.t0)/300) * self.bob
        super().draw(surface, x, y + offset, t)


class Hint(Creature):
    def __init__(self, pos, text, size=40):
        super().__init__(pos, 1000, "Sand")
        color = (242, 177, 0)
        font = pygame.font.SysFont("Calibri", size)
        self.image = [font.render(text, True, color)]

    def collide(self, sprite):
        return False


class Food(Creature):
    def __init__(self, pos, weight):
        name = "Anchor"
        frames = 1
        if weight < 0:
            name = "Bubbles"
            frames = 16
        super().__init__(pos, weight, name, frames=frames)
        self.bob = 0


class Treasure(Creature):
    def __init__(self, pos):
        name = "Treasure"
        super().__init__(pos, 1000, name)
        self.bob = 0


class Urchin(Creature):
    def __init__(self, pos):
        super().__init__(pos, 0, "Urchin")
        self.bob = 2


class Fish(Creature):
    def __init__(self, pos, right=True):
        i = random.randint(1, 4)
        super().__init__(pos, 3, f"Fish{i}", frames=1)
        self.mirror = load_image(f"Fish{i}.png", number=1, flip=True)
        if not right:
            self.image, self.mirror = self.mirror, self.image
        self.direction = 1 if right else -1

    def update(self, game, dt):
        patrol_x(self, game, dt)


class Shark(Creature):
    def __init__(self, pos, right=True):
        super().__init__(pos, 0, "Shark", frames=1)
        self.mirror = load_image("Shark.png", number=1, flip=True)
        if not right:
            self.image, self.mirror = self.mirror, self.image
        self.direction = 1 if right else -1

    def update(self, game, dt):
        patrol_x(self, game, dt)


class Jelly(Creature):
    def __init__(self, pos, down=True):
        super().__init__(pos, 0, "Jellyfish", frames=6)
        self.direction = 1 if down else -1
        self.frame_rate = FRAME_RATE / 2

    def update(self, game, dt):
        patrol_y(self, game, dt)


def patrol_x(self, game, dt, speed=PATROL_SPEED):
    i = round(self.pos.y / GRID) - game.top
    j = round(self.pos.x / GRID + self.direction * self.imw / 2 / GRID)
    if i < 0 or i >= len(game.grid):
        return
    if j < 0 or j >= len(game.grid[i]):
        return
    if game.grid[i][j]:
        self.direction *= -1
        self.image, self.mirror = self.mirror, self.image
    self.pos.x += speed * self.direction * dt / 1000


def patrol_y(self, game, dt, speed=PATROL_SPEED):
    i = round(self.pos.y / GRID + self.direction * self.imh / 2 / GRID) - game.top
    j = round(self.pos.x / GRID)
    if i < 0 or i >= len(game.grid):
        return
    if j < 0 or j >= len(game.grid[i]):
        return
    if game.grid[i][j]:
        self.direction *= -1
    self.pos.y += speed * self.direction * dt / 1000
