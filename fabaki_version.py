import datetime
import pygame
from fabaki_version_header import *

screen = pygame.display.set_mode((SCREEN_SIZE[WIDTH], SCREEN_SIZE[HEIGHT]))


class Sword:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = DIRECTION_NORTH
        self.texture = TEXTURE_NORTH
        self.dashing = False
        self.dashing_dir = (0, 0)
        self.stop_dash_time = None
        self.undashable = None
        self.vel = SWORD_SPEED

    def change_dir(self, new_dir):
        self.direction = new_dir
        self.texture = DIRECTION_TEXTURE_MATCH[new_dir]

    def coords(self):
        return self.x, self.y

    def draw(self):
        if self.direction == DIRECTION_NORTH or self.direction == DIRECTION_SOUTH:
            screen.blit(self.texture, (self.x - TEXTURE_PERP_VERT_SIZE[WIDTH] / 2,
                                       self.y - TEXTURE_PERP_VERT_SIZE[HEIGHT] / 2))
        elif self.direction == DIRECTION_EAST or self.direction == DIRECTION_WEST:
            screen.blit(self.texture, (self.x - TEXTURE_PERP_HORZ_SIZE[WIDTH] / 2,
                                       self.y - TEXTURE_PERP_HORZ_SIZE[HEIGHT] / 2))
        elif self.direction == DIRECTION_NORTHEAST or \
                self.direction == DIRECTION_NORTHWEST or \
                self.direction == DIRECTION_SOUTHEAST or \
                self.direction == DIRECTION_SOUTHWEST:
            screen.blit(self.texture, (self.x - TEXTURE_DIAG_SIZE[WIDTH] / 2, self.y - TEXTURE_DIAG_SIZE[HEIGHT] / 2))

    def next_direction(self):
        index = DIRECTION_ORDER.index(self.direction)
        index += 1
        if index == len(DIRECTION_ORDER):
            index = 0
        self.change_dir(DIRECTION_ORDER[index])

    def fix_location(self):
        if self.x < 0:
            self.x = SCREEN_SIZE[WIDTH] - self.x
        elif self.x >= SCREEN_SIZE[WIDTH]:
            self.x = self.x - SCREEN_SIZE[WIDTH]
        if self.y < 0:
            self.y = SCREEN_SIZE[HEIGHT] - self.y
        elif self.y >= SCREEN_SIZE[HEIGHT]:
            self.y = self.y - SCREEN_SIZE[HEIGHT]

    def move(self):
        keys = pygame.key.get_pressed()
        mov = [0, 0]  # By means of top-left, aka [1, 1] is South-East

        if self.undashable is not None and datetime.datetime.utcnow() > self.undashable:
            self.undashable = None
        if not self.dashing:
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                mov[0] -= 1
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                mov[0] += 1
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                mov[1] -= 1
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                mov[1] += 1

            if mov == [0, 0]:  # We didn't move, so we can dash
                if self.undashable is None and keys[pygame.K_SPACE]:
                    self.dashing = True
                    for k, v in MOVE_DIRECTION_MATCH.items():
                        if v == self.direction:
                            self.dashing_dir = k
                            break
                    self.vel *= DASH_MULTIPLIER
                    self.stop_dash_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=DASH_DURATION)
                    self.undashable = datetime.datetime.utcnow() + datetime.timedelta(seconds=DASH_COOLDOWN)
                    return
            else:
                self.undashable = datetime.datetime.utcnow() + datetime.timedelta(seconds=UNDASHABLE_DURATION)
                self.change_dir(MOVE_DIRECTION_MATCH[tuple(mov)])

        self.x += mov[0] * self.vel
        self.y += mov[1] * self.vel
        self.fix_location()

    def dash(self):
        self.x += self.dashing_dir[0] * self.vel
        self.y += self.dashing_dir[1] * self.vel
        self.texture.fill((190, 0, 0, 100), special_flags=pygame.BLEND_SUB)
        self.fix_location()

    def stop_dash(self):
        self.dashing = False
        self.dashing_dir = (0, 0)
        self.vel /= DASH_MULTIPLIER
        DIRECTION_TEXTURE_MATCH[self.direction] = load_texture(self.direction)
        self.stop_dash_time = None

    def apply_effect(self, effect, time):
        pass


def game_loop():
    player = Sword(SCREEN_SIZE[WIDTH] / 2, SCREEN_SIZE[HEIGHT] / 2)
    clock = pygame.time.Clock()
    frame = -1

    while True:
        clock.tick(TICK_RATE)
        frame += 1
        if frame == TICK_RATE:
            frame = 0

        screen.blit(TEXTURE_BACKGROUND, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        if not player.dashing and frame % ANIMATION_DELAY == 0:
            player.next_direction()

        if not player.dashing:
            player.move()
        if player.dashing:
            player.dash()
            if datetime.datetime.utcnow() > player.stop_dash_time:
                player.stop_dash()

        player.draw()
        pygame.display.update()


def main():
    pygame.init()
    game_loop()
    pygame.quit()


if __name__ == '__main__':
    main()
