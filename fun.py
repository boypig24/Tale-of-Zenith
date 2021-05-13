import pygame
import random
from time import time as current_time


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def transform_rect(self, rect):
        new_x = self.x
        new_y = self.y
        new_x += rect.width
        new_y -= rect.height
        return Point(new_x, new_y)

    def tuple(self):
        return self.x, self.y


BACKGROUND = "nomatter.png"
MODELS_DIR = "images\\"

ROTATIONS = {(0, -1): "n",
             (0, 1): "s",
             (-1, 0): "w",
             (1, 0): "e",
             (1, -1): "ne",
             (1, 1): "se",
             (-1, 1): "sw",
             (-1, -1): "nw"}
MODEL_FILE_TYPE = ".png"
FONT_COLOR = (255, 255, 255)
SCREEN_SIZE = Point(1609, 909)
world = pygame.display.set_mode(SCREEN_SIZE.tuple())
back = pygame.image.load(BACKGROUND)
backbox = world.get_rect()
ANIMATION_DELAY = 5
DASH_LEN = 20
NO_DASH_DELAY = 15
SLIME = "slime.png"
BOSS_SLIME = "goldenslime.png"
MUSHROOM = "mushroom.png"
TELESHROOM = "teleshroom.png"
DEFAULT_SPEED = 10
DEFAULT_BOOST_SPEED = 30
MANUAL_CLOCKWISE = {(0, -1): (1, -1),
                    (0, 1): (-1, 1),
                    (-1, 0): (-1, -1),
                    (1, 0): (1, 1),
                    (1, -1): (1, 0),
                    (1, 1): (0, 1),
                    (-1, 1): (-1, 0),
                    (-1, -1): (0, -1)}
SLIME_TEXTURE = pygame.image.load(MODELS_DIR + SLIME)
BOSS_SLIME_TEXTURE = pygame.image.load(MODELS_DIR + BOSS_SLIME)
MUSHROOM_TEXTURE = pygame.image.load(MODELS_DIR + MUSHROOM)
TELESHROOM_TEXTURE = pygame.image.load(MODELS_DIR + TELESHROOM)
BOSS_MAX_COOLDOWN = 300
BOSS_MIN_COOLDOWN = 100
BOSS_POINT = 10
MUSHROOM_CD = 50
TELE_CD = 50
MUSHROOM_MULT = 2
TOUCH_MUSH_TIME = 25
MINIMAL_BOSS_INV = 5
TELESHROOM_VISUAL_EFFECT_TIME = 25
TEXT_POS = (0, 30)
RESET_SCORE = 50
SLIME_COUNT = 3
FONT = ("comicsansms", 32)
START_ROTATION = (0, -1)
TIME_ROUNDING = 2
RELATIVE_START_LOCATION = (0.5, 0.5)


def intersect(l1, r1, l2, r2):
    if l1.x >= r2.x or l2.x >= r1.x:
        return False
    if l1.y <= r2.y or l2.y <= r1.y:
        return False
    return True


def game():
    player_model = pygame.image.load(MODELS_DIR + ROTATIONS[START_ROTATION] + MODEL_FILE_TYPE)
    player_location = Point(SCREEN_SIZE.x * RELATIVE_START_LOCATION[0], SCREEN_SIZE.y * RELATIVE_START_LOCATION[1])
    rotation = START_ROTATION
    frames = 0
    dashing = 0
    speed = DEFAULT_SPEED
    slimes = [None] * SLIME_COUNT
    font = pygame.font.SysFont(*FONT)
    score = 0
    start_time = current_time()
    cooldown_boss = 0
    cooldown_mush = MUSHROOM_CD
    cooldown_tele = TELE_CD
    boss = None
    mushroom = None
    teleshroom = None
    dash_cd = 0
    touched_mush = 0
    recently_tele = 0

    continue_playing = True
    while continue_playing:
        frames += 1

        world.blit(back, backbox)
        mov = [0, 0]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                continue_playing = False

        for i in range(len(slimes)):
            if slimes[i] is None:
                slimes[i] = Point(random.randint(0, SCREEN_SIZE.x-SLIME_TEXTURE.get_rect().width),
                                  random.randint(0, SCREEN_SIZE.y-SLIME_TEXTURE.get_rect().height))
            if intersect(player_location, player_location.transform_rect(player_model.get_rect()),
                         slimes[i], slimes[i].transform_rect(SLIME_TEXTURE.get_rect())):
                score += 1
                slimes[i] = None
            if slimes[i] is not None:
                world.blit(SLIME_TEXTURE, (slimes[i].x, slimes[i].y))

        if boss is None:
            if cooldown_boss == 0:
                cooldown_boss = random.randint(BOSS_MIN_COOLDOWN, BOSS_MAX_COOLDOWN)
                boss = Point(random.randint(0, SCREEN_SIZE.x-BOSS_SLIME_TEXTURE.get_rect().width),
                             random.randint(0, SCREEN_SIZE.y-BOSS_SLIME_TEXTURE.get_rect().height))
        else:
            if intersect(player_location, player_location.transform_rect(player_model.get_rect()),
                         boss, boss.transform_rect(BOSS_SLIME_TEXTURE.get_rect())) \
                    and dashing > 0 and DASH_LEN-dashing > MINIMAL_BOSS_INV:
                score += BOSS_POINT
                boss = None

        if boss is not None:
            world.blit(BOSS_SLIME_TEXTURE, boss.tuple())

        if mushroom is None:
            if cooldown_mush == 0:
                cooldown_mush = MUSHROOM_CD
                mushroom = Point(random.randint(0, SCREEN_SIZE.x-MUSHROOM_TEXTURE.get_rect().width),
                                        random.randint(0, SCREEN_SIZE.y-MUSHROOM_TEXTURE.get_rect().height))
        else:
            if intersect(player_location,
                         player_location.transform_rect(player_model.get_rect()),
                         mushroom,
                         mushroom.transform_rect(MUSHROOM_TEXTURE.get_rect())):
                touched_mush = TOUCH_MUSH_TIME
                mushroom = None

        if mushroom is not None:
            world.blit(MUSHROOM_TEXTURE, mushroom.tuple())

        if teleshroom is None:
            if cooldown_tele == 0:
                cooldown_tele = TELE_CD
                teleshroom = Point(random.randint(0, SCREEN_SIZE.x - TELESHROOM_TEXTURE.get_rect().width),
                                   random.randint(0, SCREEN_SIZE.y - TELESHROOM_TEXTURE.get_rect().height))
        else:
            if intersect(player_location,
                         player_location.transform_rect(player_model.get_rect()),
                         teleshroom,
                         teleshroom.transform_rect(TELESHROOM_TEXTURE.get_rect())):
                player_location.x = random.randint(0, SCREEN_SIZE.x - player_model.get_rect().x)
                player_location.y = random.randint(0, SCREEN_SIZE.y - player_model.get_rect().y)
                teleshroom = None
                recently_tele = TELESHROOM_VISUAL_EFFECT_TIME

        if teleshroom is not None:
            world.blit(TELESHROOM_TEXTURE, teleshroom.tuple())

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            mov[0] -= 1
            dash_cd = NO_DASH_DELAY

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            mov[0] += 1
            dash_cd = NO_DASH_DELAY

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            mov[1] -= 1
            dash_cd = NO_DASH_DELAY

        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            mov[1] += 1
            dash_cd = NO_DASH_DELAY

        if keys[pygame.K_SPACE] or keys[pygame.K_e]:
            if dashing == 0 and mov == [0, 0] and dash_cd == 0:
                dashing = DASH_LEN

        if cooldown_boss > 0 and boss is None:  # only decrement cooldown AFTER boss death
            cooldown_boss -= 1

        if cooldown_mush > 0 and mushroom is None:
            cooldown_mush -= 1

        if cooldown_tele > 0 and teleshroom is None:
            cooldown_tele -= 1

        if touched_mush > 0:
            touched_mush -= 1

        if recently_tele > 0:
            recently_tele -= 1

        if dashing > 0:
            dashing -= 1
            speed = DEFAULT_BOOST_SPEED
            mov = rotation  # ignore all movment key presses
            if dashing == 1:
                dash_cd = NO_DASH_DELAY
        else:
            speed = DEFAULT_SPEED
            if dash_cd > 0:
                dash_cd -= 1
            # movement
            if tuple(mov) in ROTATIONS:
                rotation = mov
            else:
                if frames % ANIMATION_DELAY == 0:
                    rotation = list(MANUAL_CLOCKWISE[tuple(rotation)])
        player_model = pygame.image.load(MODELS_DIR + "\\" + ROTATIONS[tuple(rotation)] + MODEL_FILE_TYPE)

        mult = MUSHROOM_MULT if touched_mush else 1

        player_location.x += speed * mov[0] * mult
        player_location.y += speed * mov[1] * mult

        # border
        if player_location.x < 0:
            player_location.x = SCREEN_SIZE.x
        if player_location.x > SCREEN_SIZE.x:
            player_location.x = 0
        if player_location.y < 0:
            player_location.y = SCREEN_SIZE.y
        if player_location.y > SCREEN_SIZE.y:
            player_location.y = 0
        if recently_tele:
            if recently_tele % 6 <= 2:
                player_model.fill((0, 0, 190, 100), special_flags=pygame.BLEND_SUB)
            else:
                player_model.fill((190, 0, 0, 100), special_flags=pygame.BLEND_SUB)
        elif dashing:
            player_model.fill((190, 0, 0, 100), special_flags=pygame.BLEND_SUB)
        elif touched_mush:
            player_model.fill((0, 190, 0, 100), special_flags=pygame.BLEND_SUB)
        world.blit(player_model, (player_location.x, player_location.y))

        out_time = font.render(str(round(current_time()-start_time, TIME_ROUNDING)), False, FONT_COLOR)
        out_score = font.render(str(score), False, FONT_COLOR)
        world.blit(out_time, TEXT_POS)
        world.blit(out_score, (TEXT_POS[0], TEXT_POS[1] + out_time.get_rect().height))
        pygame.display.flip()


def main():
    pygame.init()
    game()
    pygame.quit()


if __name__ == '__main__':
    main()
