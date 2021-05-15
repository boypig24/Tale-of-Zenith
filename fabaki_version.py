import datetime
from fabaki_version_header import *
from random import randint
import pygame

screen = pygame.display.set_mode((SCREEN_SIZE[WIDTH], SCREEN_SIZE[HEIGHT]))


class OnScreen:
    def __init__(self, x, y, texture, object_type, vulnerabilities=(None, )):
        self.x = x
        self.y = y
        self.texture = texture
        self.object_type = object_type
        self.mask = pygame.mask.from_surface(self.texture)
        self.width = texture.get_rect().width
        self.height = texture.get_rect().height
        self.x_texture = x
        self.y_texture = y
        self.vulnerabilities = vulnerabilities

    def coords(self):
        return self.x, self.y

    def draw(self):
        self.x_texture = self.x - self.width / 2
        self.y_texture = self.y - self.height / 2
        screen.blit(self.texture, (self.x_texture, self.y_texture))


class Regeneratable(OnScreen):
    # for creating a mushroom should be ('MUSH_TEXTURE', 30, type="speed_mush") usually the other are not touched
    # regen_cd CAN be a 2 sized tuple, where a,b are the min and max cooldown times!
    def __init__(self, texture, regen_cooldown, object_type=None, random_loc=True, x=-1, y=-1,
                 vulnerabilities=(None, )):
        OnScreen.__init__(self, x, y, texture, object_type)
        self.regen_cooldown = regen_cooldown
        self.random_loc = random_loc
        self.cooldown = 0
        self.alive = True
        if self.random_loc or x < 0 or y < 0:
            self.generate_random_loc()
        self.vulnerabilities = vulnerabilities

    def generate_random_loc(self):
        self.x, self.y = randint(SCREEN_PADDING, SCREEN_SIZE[WIDTH] - self.width - SCREEN_PADDING), \
                         randint(SCREEN_PADDING, SCREEN_SIZE[HEIGHT] - self.height - SCREEN_PADDING)

    def tick(self):
        if not self.cooldown:
            self.alive = True
        else:
            self.cooldown -= 1
        if self.alive:
            self.draw()

    def on_collide(self):
        if type(self.regen_cooldown) == tuple and len(self.regen_cooldown) == 2:
            self.cooldown = randint(*self.regen_cooldown)
        else:
            self.cooldown = self.regen_cooldown
        if self.random_loc:
            self.generate_random_loc()
        self.alive = False
        return self.object_type


class Sword:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.x_texture = x
        self.y_texture = y
        self.direction = DIRECTION_NORTH
        self.texture = TEXTURE_NORTH
        self.mask = pygame.mask.from_surface(self.texture)
        self.dashing = False
        self.dashing_dir = (0, 0)
        self.stop_dash_time = None
        self.undashable = None
        self.vel = SWORD_SPEED
        self.score = 0
        self.effects = []

    def change_dir(self, new_dir):
        self.direction = new_dir
        self.texture = DIRECTION_TEXTURE_MATCH[new_dir]
        self.mask = pygame.mask.from_surface(self.texture)

    def coords(self):
        return self.x, self.y

    def draw(self):
        if self.direction == DIRECTION_NORTH or self.direction == DIRECTION_SOUTH:
            self.x_texture = self.x - TEXTURE_PERP_VERT_SIZE[WIDTH] / 2
            self.y_texture = self.y - TEXTURE_PERP_VERT_SIZE[HEIGHT] / 2
        elif self.direction == DIRECTION_EAST or self.direction == DIRECTION_WEST:
            self.x_texture = self.x - TEXTURE_PERP_HORZ_SIZE[WIDTH] / 2
            self.y_texture = self.y - TEXTURE_PERP_HORZ_SIZE[HEIGHT] / 2
        else:  # Diagonal
            self.x_texture = self.x - TEXTURE_DIAG_SIZE[WIDTH] / 2
            self.y_texture = self.y - TEXTURE_DIAG_SIZE[HEIGHT] / 2
        screen.blit(self.texture, (self.x_texture, self.y_texture))

    def next_direction(self):
        index = DIRECTION_ORDER.index(self.direction)
        index += 1
        if index == len(DIRECTION_ORDER):
            index = 0
        self.change_dir(DIRECTION_ORDER[index])

    def fix_location(self):
        if self.x < 0:
            self.x = SCREEN_SIZE[WIDTH] + self.x
        elif self.x >= SCREEN_SIZE[WIDTH]:
            self.x = self.x - SCREEN_SIZE[WIDTH]
        if self.y < 0:
            self.y = SCREEN_SIZE[HEIGHT] + self.y
        elif self.y >= SCREEN_SIZE[HEIGHT]:
            self.y = self.y - SCREEN_SIZE[HEIGHT]

    def tick(self):
        self.vel = SWORD_SPEED

        for effect in self.effects:
            if effect[0] == EFFECT_SPEED_UP:
                effect[1] -= 1
                if effect[1] <= 0:
                    self.effects.remove(effect)
                    continue
                self.vel *= effect[2]
        if self.dashing:
            self.vel *= DASH_MULTIPLIER

        if self.dashing:
            self.dash()
            if datetime.datetime.utcnow() > self.stop_dash_time:
                self.stop_dash()
        else:
            self.move()

    def move(self):
        keys = pygame.key.get_pressed()
        mov = [0, 0]  # By means of top-left, aka [1, 1] is South-East

        if keys[pygame.K_e]:
            flip_sound()

        if self.undashable is not None and datetime.datetime.utcnow() > self.undashable:
            self.undashable = None  # means dash is ready
            pygame.mixer.music.load(f"{SOUND_PATH}\\{SOUND_TING_NAME}.{SOUND_FILE_EXT}")
            pygame.mixer.music.play()
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
        DIRECTION_TEXTURE_MATCH[self.direction] = load_texture(self.direction)
        self.stop_dash_time = None

    def apply_effect(self, object_type):
        if object_type not in TYPE_EFFECT:
            return

        for effect in TYPE_EFFECT[object_type]:
            if effect.startswith(EFFECT_SCORE_UP):
                self.score += int(effect[len(EFFECT_SCORE_UP):])
            if effect.startswith(EFFECT_SPEED_UP):
                dur_power = effect[len(EFFECT_SPEED_UP):].split("@")
                self.effects.append([EFFECT_SPEED_UP, int(dur_power[0]), int(dur_power[1])])

    def colliding(self, obj):
        offset_x = int(obj.x_texture - self.x_texture)
        offset_y = int(obj.y_texture - self.y_texture)
        return self.mask.overlap(obj.mask, (offset_x, offset_y))


# music

pygame.mixer.init()
pygame.mixer.music.set_volume(0.5)
pygame.mixer.Channel(1).set_volume(0.1)

song1load = pygame.mixer.Sound(f"{SOUND_PATH}\\{SOUND_BACKGROUND1_NAME}.{SOUND_FILE_EXT}")
song2load = pygame.mixer.Sound(f"{SOUND_PATH}\\{SOUND_BACKGROUND2_NAME}.{SOUND_FILE_EXT}")
current_song = randint(1, 2)
changed = datetime.datetime.utcnow()-datetime.timedelta(seconds=2)


def flip_sound():
    global changed
    global current_song
    if datetime.datetime.utcnow()-changed < datetime.timedelta(seconds=1):
        return  # prevent spamming, I have when 'e' is pressed it calls this like 4-5 times
    changed = datetime.datetime.utcnow()
    pygame.mixer.Channel(1).stop()
    current_song = 3 - current_song  # lol 3 - 1 = 2 and 3 - 2 = 1 funny math!
    if current_song == 1:
        pygame.mixer.Channel(1).play(song1load)
    elif current_song == 2:
        pygame.mixer.Channel(1).play(song2load)

# music END


def game_loop():
    player = Sword(SCREEN_SIZE[WIDTH] / 2, SCREEN_SIZE[HEIGHT] / 2)
    enemies = [Regeneratable(TEXTURE_SLIME, 10, TEXTURE_SLIME_NAME, vulnerabilities=("normal", "dash")),
               Regeneratable(TEXTURE_SLIME, 10, TEXTURE_SLIME_NAME, vulnerabilities=("normal", "dash")),
               Regeneratable(TEXTURE_SLIME, 10, TEXTURE_SLIME_NAME, vulnerabilities=("normal", "dash")),
               Regeneratable(TEXTURE_GOLDEN_SLIME, (100, 300), TEXTURE_GOLDEN_SLIME_NAME, vulnerabilities=("dash",)),
               Regeneratable(TEXTURE_SPEED_MUSH, 50, TEXTURE_SPEED_MUSH_NAME, vulnerabilities=("normal", "dash"))]
    clock = pygame.time.Clock()
    frame = -1
    text_font = pygame.font.SysFont("comicsansms", 16)
    # pygame.mixer.music.load(f"{SOUND_PATH}\\{SOUND_TING_NAME}.{SOUND_FILE_EXT}")
    # pygame.mixer.music.play()

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

        player.tick()

        for enemy in enemies:
            if enemy.alive:
                if "normal" in enemy.vulnerabilities or ("dash" in enemy.vulnerabilities and player.dashing):
                    if player.colliding(enemy):
                        player.apply_effect(enemy.on_collide())
            enemy.tick()

        fps_text = text_font.render(f"fps: {round(clock.get_fps())}", False, (255, 255, 255))
        score_text = text_font.render(f"score: {player.score}", False, (255, 255, 255))
        screen.blit(fps_text, (0, 0))
        screen.blit(score_text, (0, fps_text.get_rect().height))
        player.draw()
        pygame.display.update()


def main():
    pygame.init()
    flip_sound()
    game_loop()
    pygame.quit()


if __name__ == '__main__':
    main()
