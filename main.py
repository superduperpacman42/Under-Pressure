from creature import *
from player import Player
from util import *
from wall import Wall

import pygame
import asyncio
import random


class Game:

    def reset(self, restart=False):
        """ Resets the game state """
        if restart:
            self.level = 1
            self.top = 0
            self.bottom = 0
            self.right = 0
            self.depth = 0
            self.tutorial = 0
        self.t = 0
        self.t0 = 0
        self.input = ["0"]
        self.pause = False
        self.sprites = []
        self.prev_sprites = []
        self.walls = []
        self.prev_walls = []
        self.player = Player()
        self.load_level(self.level)
        self.player.pos = self.respawn
        self.player.pos.y = GRID * self.top
        goal = self.get_camera_target()
        self.x = goal.x
        self.y = goal.y

    def load_level(self, level):
        # if level == 1:
        # self.sprites.append(Hint(Pose(100, self.top * GRID + HEIGHT * .15), "Under Pressure", 120))
        random.seed(0)
        self.grid = []
        with open(f"levels/Level{level}.txt") as file:
            for i, line in enumerate(file):
                row = []
                y = i * GRID + self.top * GRID
                for j, c in enumerate(line):
                    if c == "\n":
                        continue
                    x = j * GRID
                    row += [None]
                    if c == ".":  # wall
                        self.walls.append(Wall((x-GRID/2, x+GRID/2, y-GRID/2, y+GRID/2)))
                        row[-1] = self.walls[-1]
                    elif c == "-":  # platform
                        self.walls.append(Wall((x-GRID/2, x+GRID/2, y-10, y+10)))
                        row[-1] = self.walls[-1]
                    elif c == "P":  # player
                        self.respawn = Pose(x, y)
                    elif c == "(":  # fish
                        self.sprites.append(Fish(Pose(x, y), right=False))
                    elif c == ")":  # fish
                        self.sprites.append(Fish(Pose(x, y), right=True))
                    elif c == "<":  # shark
                        self.sprites.append(Shark(Pose(x, y), right=False))
                    elif c == ">":  # shark
                        self.sprites.append(Shark(Pose(x, y), right=True))
                    elif c == "^":  # jelly
                        self.sprites.append(Jelly(Pose(x, y), down=False))
                    elif c == "v":  # jelly
                        self.sprites.append(Jelly(Pose(x, y), down=True))
                    elif c == "*":  # urchin
                        self.sprites.append(Urchin(Pose(x, y)))
                    elif c == "o":  # bubbles
                        self.sprites.append(Food(Pose(x, y), -3))
                    elif c.isdigit():  # food
                        self.sprites.append(Food(Pose(x, y), ord(c)))
                    elif c == "$":  # treasure
                        self.sprites.append(Treasure(Pose(x, y)))

                self.grid += [row]
        self.bottom = self.top + len(self.grid)
        self.right = len(self.grid[0])
        self.player.weight = self.respawn.y // GRID

    def ui(self, surface):
        """ Draws the user interface overlay """
        color = (242, 177, 0)
        if self.state == "splash":
            caption = self.title_font.render("Under Pressure", True, color)
            surface.blit(caption, (WIDTH / 2 - caption.get_width() / 2, HEIGHT * 0.1))
            caption = self.font.render("Press Enter to Begin", True, color)
            surface.blit(caption, (WIDTH / 2 - caption.get_width() / 2, HEIGHT * 0.25))
        elif self.state == "play":
            # caption = self.font.render("Press Enter to Begin", True, color)
            # surface.blit(caption, (WIDTH / 2 - caption.get_width() / 2, HEIGHT * 0.25))
            pass
        elif self.state == "defeat":
            pass
        elif self.state == "victory":
            caption = self.title_font.render("Treasure Found!", True, color)
            surface.blit(caption, (WIDTH / 2 - caption.get_width() / 2, HEIGHT * 0.5))
            caption = self.font.render("Press Enter to Play Again", True, color)
            surface.blit(caption, (WIDTH / 2 - caption.get_width() / 2, HEIGHT * 0.65))
            pass

    def update(self, dt, keys):
        """ Updates the game by a timestep and redraws graphics """
        if dt > 100:
            return
        self.t += dt
        self.update_keys(keys)

        # Player update
        if self.state in ["play", "victory"] and self.player.pos.y < (self.bottom - 0.2) * GRID:
            self.player.update(self.input[-1], dt)
        else:
            self.player.v.x = 0
            self.player.update("", dt)

        # Level completion
        if self.player.pos.y > self.bottom * GRID and self.player.weight > self.bottom:
            self.level += 1
            self.top = self.bottom
            self.load_level(self.level)

        # Camera update
        goal = self.get_camera_target()
        self.x += max(min(CAMERA_KP * (goal.x - self.x), CAMERA_SPEED), -CAMERA_SPEED) * dt / 1000
        self.y += max(min(CAMERA_KP * (goal.y - self.y), CAMERA_SPEED), -CAMERA_SPEED) * dt / 1000

        # Clear surface
        surface = pygame.Surface((WIDTH, HEIGHT))
        if self.player.pos.y / GRID != self.depth:
            self.depth = self.player.pos.y / GRID
            self.shaded_water = pygame.Surface((WIDTH, HEIGHT))
            self.shaded_water.blit(self.water[0], (0, 0))
            self.shadow.set_alpha(min(255, int(100 * self.depth / 200)))
            self.shaded_water.blit(self.shadow, (0, 0))
        surface.blit(self.shaded_water, (0, 0))
        # Update walls
        for w in self.walls:
            if w.onscreen(self.x, self.y, WIDTH, HEIGHT):
                w.draw(surface, self.x, self.y, self.t)
        self.player.grounded = False
        self.player.ceilinged = False
        i0 = round(self.player.pos.y / GRID) - self.top
        j0 = round(self.player.pos.x / GRID)
        for i in [i0 - 1, i0, i0 + 1]:
            if i < 0 or i >= len(self.grid):
                continue
            for j in [j0 - 1, j0, j0 + 1]:
                if j < 0 or j >= len(self.grid[i]):
                    continue
                wall = self.grid[i][j]
                if wall:
                    wall.collide(self.player)

        # Update sprites
        self.sprites = sorted(self.sprites, key=lambda sp: sp.layer)
        for s in self.sprites[:]:
            s.update(self, dt)
            if s.collide(self.player):
                if s.weight == 1000:
                    self.state = "victory"
                    # self.sprites.append(Hint(Pose(0, self.top * GRID + HEIGHT * .25), "Treasure Found!", 120))
                    self.sprites.remove(s)
                elif s.weight > 0:
                    self.player.weight += s.weight
                    self.sprites.remove(s)
                elif s.weight < 0:
                    self.player.weight = round(s.pos.y / GRID) - 3
                else:
                    self.reset(restart=False)
                    return
            if s.onscreen(self.x, self.y, WIDTH, HEIGHT):
                s.draw(surface, self.x, self.y, self.t)

        # Draw player
        self.player.draw(surface, self.x, self.y, self.t)
        # if self.state == "defeat":
        #     shadow = pygame.Surface((WIDTH, HEIGHT)).convert()
        #     shadow.set_alpha(min(255, int((self.t - self.game_over) * 255 / 500)))
        #     surface.blit(shadow, (0, 0))

        self.screen.blit(surface, (0, 0))
        self.ui(self.screen)
        # if self.t > self.wind and not self.splash:
        #     play_sound("Wind.ogg", True)
        #     self.wind = self.t + 5000 + random.random()*(LIGHTNING_PERIOD - 5000)

    def get_camera_target(self):
        xgoal = self.player.pos.x
        ygoal = self.player.pos.y
        xgoal = max(xgoal, 0 - GRID / 2 + WIDTH / 2)
        xgoal = min(xgoal, self.right * GRID - GRID / 2 - WIDTH / 2)
        ygoal = max(ygoal, self.top * GRID - GRID / 2 + HEIGHT / 2)
        ygoal = min(ygoal, self.bottom * GRID - GRID / 2 - HEIGHT / 2)
        return Pose(xgoal, ygoal)

    def key_pressed(self, key):
        """ Respond to a key press event """
        if key == pygame.K_RETURN:
            if self.state == "splash":
                self.state = "play"
                self.t0 = 0
                play_music("Into_the_Depths.wav")
            elif self.state == "play":
                self.reset(restart=False)
            elif self.state == "victory" and self.t - self.t0 > 2000:
                self.reset(restart=True)
                self.state = "play"
        elif key == pygame.K_ESCAPE:
            self.full_screen = not self.full_screen
            if self.full_screen:
                self.screen = pygame.display.set_mode([WIDTH, HEIGHT], pygame.FULLSCREEN)
            else:
                self.screen = pygame.display.set_mode([WIDTH, HEIGHT])
        elif key == pygame.K_RIGHT or key == pygame.K_d:
            if "R" in self.input:
                self.input.remove("R")
            self.input.append("R")
        elif key == pygame.K_LEFT or key == pygame.K_a:
            if "L" in self.input:
                self.input.remove("L")
            self.input.append("L")
        elif key == pygame.K_UP or key == pygame.K_w:
            if self.state == "play" or self.state == "victory":
                self.player.jump(up=True)
        elif key == pygame.K_DOWN or key == pygame.K_s:
            if self.state == "play" or self.state == "victory":
                self.player.jump(up=False)
        # elif key == pygame.K_p:
        #     self.player.weight += 1
        # elif key == pygame.K_o:
        #     self.level += 1
        #     self.top = self.bottom
        #     self.reset(restart=False)

    def update_keys(self, keys):
        """ Respond to a key press event """
        if "R" in self.input and not (keys[pygame.K_RIGHT] or keys[pygame.K_d]):
            self.input.remove("R")
        if "L" in self.input and not (keys[pygame.K_LEFT] or keys[pygame.K_a]):
            self.input.remove("L")

    ################################################################################

    def __init__(self, name):
        """ Initialize the game """
        self.state = "splash"
        self.level = 1
        self.right = 0
        self.top = 0
        self.bottom = 0
        self.depth = 0
        self.t = 0
        self.t0 = 0
        self.x = 0
        self.y = 0
        self.input = ["0"]
        self.pause = False
        self.respawn = Pose(0, 0)
        self.player = None
        self.sprites = []
        self.prev_sprites = []
        self.walls = []
        self.prev_walls = []
        self.grid = []
        pygame.init()
        os.environ['SDL_VIDEO_WINDOW_POS'] = '0, 30'
        pygame.display.set_caption(name)
        self.full_screen = False
        if not self.full_screen:
            self.screen = pygame.display.set_mode([WIDTH, HEIGHT])
        else:
            self.screen = pygame.display.set_mode([WIDTH, HEIGHT], pygame.FULLSCREEN)
        self.water = load_image("Water.png")
        self.shaded_water = self.water
        self.shadow = pygame.Surface((WIDTH, HEIGHT)).convert()
        icon = load_image("Icon.png", scale=1)[0]
        icon.set_colorkey((255, 0, 0))
        pygame.display.set_icon(icon)
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        self.font = pygame.font.SysFont("Calibri", 40)
        self.title_font = pygame.font.SysFont("Calibri", 120)
        self.reset(restart=True)
        # play_music("Into_the_Depths.wav")
        set_volume(0.1)
        asyncio.run(self.run())

    async def run(self):
        """ Iteratively call update """
        clock = pygame.time.Clock()
        self.pause = False
        while not self.pause:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    self.key_pressed(event.key)
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    sys.exit()
            dt = clock.tick(TIME_STEP)
            self.update(dt, pygame.key.get_pressed())
            pygame.display.update()
            await asyncio.sleep(0)


if __name__ == '__main__':
    game = Game("Under Pressure")
