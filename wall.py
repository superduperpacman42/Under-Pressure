import pygame.draw

from sprite import Sprite
from util import *
import random


class Wall(Sprite):
    def __init__(self, lims, layer=0):
        self.x0 = lims[0]
        self.x1 = lims[1]
        self.y0 = lims[2]
        self.y1 = lims[3]
        self.pos = Pose((self.x0 + self.x1)/2, (self.y0 + self.y1)/2)
        self.w = lims[1] - lims[0]
        self.h = lims[3] - lims[2]
        name = "Sand"
        if self.h == 20:
            name = "Platform"
        self.rect = (self.x0, self.y0, self.w, self.h)
        self.layer = layer
        super().__init__(self.pos, name)
        if name != "Sand":
            return
        shells = []
        self.image = [self.image[0].copy()]
        for i in range(random.randint(0, 2)):
            shell = (random.random() * (self.w - 20) + 10, random.random() * (self.h - 20) + 10, random.randint(1, 5))
            collide = False
            for shell2 in shells:
                if (shell[0] - shell2[0]) ** 2 + (shell[1] - shell2[1]) ** 2 < 400:
                    collide = True
            if not collide:
                shells += [shell]
        for shell in shells:
            self.image[0].blit(load_image(f"Shell{shell[2]}.png")[0], shell[0:2])

    def collide(self, sprite):
        right = sprite.pos.x - sprite.imw/2 - self.x1
        left = -sprite.pos.x - sprite.imw/2 + self.x0
        down = sprite.pos.y - sprite.imh/2 - self.y1
        up = -sprite.pos.y - sprite.imh/2 + self.y0
        # Collide up/down
        if up < 1 and down < 1 and left < -10 and right < -10:
            if up > down:
                sprite.grounded = True
                sprite.pos.y += up
                sprite.v.y = min(0, sprite.v.y)
            else:
                sprite.ceilinged = True
                sprite.pos.y -= down
                sprite.v.y = max(0, sprite.v.y)
            return True
        # Collide left/right
        if up < -10 and down < -10 and left < 0 and right < 0:
            if left > right:
                sprite.pos.x += left
                sprite.v.x = min(0, sprite.v.x)
            else:
                sprite.pos.x -= right
                sprite.v.x = max(0, sprite.v.x)
            return True
        return False

    def onscreen(self, x, y, w, h):
        return self.x0 < w/2 + x and self.x1 > -w/2 + x and self.y0 < h/2 + y and self.y1 > -h/2 + y
