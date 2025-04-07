from util import *
import random


class Sprite:
    def __init__(self, pos, image, frames=1, flip=False, layer=0):
        self.pos = pos
        self.v = Pose(0, 0)
        self.image = load_image(image + ".png", number=frames, flip=flip)
        self.imw = self.image[0].get_width()
        self.imh = self.image[0].get_height()
        self.layer = layer
        self.frames = frames
        self.frame_rate = FRAME_RATE
        self.t0 = random.random() * self.frame_rate * frames

    def draw(self, surface, x, y, t):
        i = int((t - self.t0) * self.frame_rate / 1000) % len(self.image)
        surface.blit(self.image[i], (self.pos.x - x - self.imw / 2 + WIDTH/2, self.pos.y - y - self.imh / 2 + HEIGHT/2))

    def onscreen(self, x, y, w, h):
        p0 = self.pos - (self.imw/2, self.imh/2)
        p1 = self.pos + (self.imw/2, self.imh/2)
        return p1.x > x - w/2 and p0.x < x + w/2 and p1.y > y - h/2 and p0.y < y + h/2

    def collide(self, sprite, buffer=BUFFER):
        return self.pos.x - self.imw/2 < sprite.pos.x + sprite.imw/2 - buffer and \
               self.pos.x + self.imw/2 > sprite.pos.x - sprite.imw/2 + buffer and \
               self.pos.y - self.imh / 2 < sprite.pos.y + sprite.imh / 2 - buffer and \
               self.pos.y + self.imh / 2 > sprite.pos.y - sprite.imh / 2 + buffer
