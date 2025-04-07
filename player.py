import math

from sprite import Sprite
from util import *
import random


class Player(Sprite):
    def __init__(self, pos=Pose(0, 0)):
        super().__init__(pos, "Player", frames=3)
        self.right = load_image("Player.png", number=3, flip=False, scale=1)
        self.left = load_image("Player.png", number=3, flip=True, scale=1)
        self.grounded = False
        self.ceilinged = False
        self.weight = 0
        self.pressure = 0

    def draw(self, surface, x, y, t):
        i = 1
        if self.pressure > 1:
            i = 2
        if self.pressure < -1:
            i = 0
        offset = -100 if self.image == self.left else 100
        theta = math.degrees(math.atan2(-self.v.y, self.v.x + offset))
        if self.image == self.left:
            theta += 180
        img = pygame.transform.rotate(self.image[i], theta)
        self.imh = self.image[0].get_height()
        surface.blit(img, (self.pos.x - x - self.imw / 2 + WIDTH/2, self.pos.y - y - self.imh / 2 + HEIGHT/2))
        if i == 0:
            self.imh -= 14

    def update(self, user_input, dt):
        if user_input == "R":
            self.v.x = PLAYER_SPEED
            self.image = self.right
        elif user_input == "L":
            self.v.x = -PLAYER_SPEED
            self.image = self.left
        else:
            self.v.x -= self.v.x * PLAYER_LATERAL_FRICTION
            if abs(self.v.x) < PLAYER_SPEED/10:
                self.v.x = 0
        if self.v.y > PLAYER_MAX_FALL:
            self.v.y = PLAYER_MAX_FALL
        elif self.v.y < -PLAYER_MAX_FALL:
            self.v.y = -PLAYER_MAX_FALL
        self.pressure = max(min(self.weight - self.pos.y / GRID, 3), -3)
        self.v.y += PLAYER_GRAVITY * self.pressure * dt/1000
        self.v.y -= self.v.y * PLAYER_FRICTION
        self.pos += self.v * dt / 1000

    def jump(self, up=False):
        if up and self.grounded:
            self.v.y = -PLAYER_JUMP
            self.grounded = False
        if not up and self.ceilinged:
            self.v.y = PLAYER_JUMP
            self.ceilinged = False
