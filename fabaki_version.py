import datetime
from fabaki_version_header import *
from random import randint
import pygame

screen = pygame.display.set_mode((SCREEN_SIZE[WIDTH], SCREEN_SIZE[HEIGHT]))


class OnScreen:
    def __init__(self, x, y, texture, object_type):
        self.x = x
        self.y = y
        self.texture = texture
        self.object_type = object_type
        self.mask = pygame.mask.from_surface(self.texture)
        self.width = texture.get_rect().width
        self.height = texture.get_rect().height
        self.x_texture = x
        self.y_texture = y

    def coords(self):
        return self.x, self.y

    def draw(self):
        self.x_texture = self.x - self.width / 2
        self.y_texture = self.y - self.height / 2
        screen.blit(self.texture, (self.x_texture, self.y_texture))


class Effect:
    def __init__(self, entity, duration, cooldown):
        self.entity = entity
        self.duration = duration
        self.cooldown = cooldown
        self.active = False


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


class SpeedUpEffect(Effect):
    def __init__(self, entity):
        Effect.__init__(self, entity, -1, -1)


class DashEffect(Effect):
    def __init__(self, entity, direction):
        Effect.__init__(self, entity, -1, -1)
        self.direction = direction
        self.power = -1
        self.ready = True

    def start_dash(self, direction, duration=DASH_DURATION, cooldown=DASH_COOLDOWN, power=DASH_POWER):
        if not self.ready:
            return False
        self.direction = direction
        self.duration = duration
        self.cooldown = cooldown
        self.power = power
        self.ready = False
        self.active = True

        self.entity.texture.fill((190, 0, 0, 100), special_flags=pygame.BLEND_SUB)
        self.entity.vel *= self.power
        return True

    def stop_dash(self):
        self.duration = -1
        self.active = False

        DIRECTION_TEXTURE_MATCH[MOVE_DIRECTION_MATCH[tuple(self.direction)]] = \
            load_texture(MOVE_DIRECTION_MATCH[tuple(self.direction)])
        self.entity.vel /= self.power

    def set_cooldown(self, cooldown):  # Can't stop dash! only to set the cooldown again when dash is un active
        if cooldown <= self.cooldown:
            return
        self.ready = False
        self.cooldown = cooldown

    def tick(self):
        if not self.active and self.cooldown > 0:
            self.cooldown -= 1
            return
        if self.duration > 0:
            self.duration -= 1
            self.entity.move_vector = self.direction

        if self.cooldown == 0:
            self.ready = True
            pygame.mixer.music.load(f"{SOUND_PATH}\\{SOUND_TING_NAME}.{SOUND_FILE_EXT}")
            pygame.mixer.music.play()
            self.cooldown = -1
        if self.duration == 0:
            self.stop_dash()
            self.duration = -1


class SwordEffects:
    def __init__(self, sword):
        self.dash_effect = DashEffect(sword, [0, 0])
        self.speed_mush_effect = SpeedUpEffect(sword)


class Sword:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.x_texture = x
        self.y_texture = y
        self.direction = DIRECTION_NORTH
        self.move_vector = [0, 0]  # By means of top-left, aka [1, 1] is South-East
        self.texture = TEXTURE_NORTH
        self.mask = pygame.mask.from_surface(self.texture)
        self.vel = SWORD_SPEED
        self.score = 0
        self.effects = SwordEffects(self)
        self.current_tick = 0

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
        self.current_tick += 1
        if self.current_tick % SWORD_ANIMATION_DELAY == 0 and not self.effects.dash_effect.active:
            self.next_direction()

        self.move_vector = [0, 0]
        if not self.effects.dash_effect.active:
            self.move_keys()
        self.effects.dash_effect.tick()

        self.move()
        self.draw()

    def move_keys(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_e]:
            flip_sound()

        if not self.effects.dash_effect.active:  # Not dashing
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.move_vector[0] -= 1
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.move_vector[0] += 1
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                self.move_vector[1] -= 1
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                self.move_vector[1] += 1

            if self.move_vector == [0, 0]:  # We didn't move, so we can dash
                if self.effects.dash_effect.ready and keys[pygame.K_SPACE]:
                    self.effects.dash_effect.start_dash(list(DIRECTION_MOVE_MATCH[self.direction]))
            else:
                self.change_dir(MOVE_DIRECTION_MATCH[tuple(self.move_vector)])
                self.effects.dash_effect.set_cooldown(DASH_MOVE_COOLDOWN)

    def move(self):
        self.x += self.move_vector[0] * self.vel
        self.y += self.move_vector[1] * self.vel
        self.fix_location()

    def apply_effect(self, object_type):
        if object_type not in TYPE_EFFECT:
            return

        for effect in TYPE_EFFECT[object_type]:
            if effect.startswith(EFFECT_SCORE_UP):
                self.score += int(effect[len(EFFECT_SCORE_UP):])
            # if effect.startswith(EFFECT_SPEED_UP):
            #     dur_power = effect[len(EFFECT_SPEED_UP):].split("@")
            #     self.effects.append([EFFECT_SPEED_UP, int(dur_power[0]), int(dur_power[1])])

    def colliding(self, obj):
        offset_x = int(obj.x_texture - self.x_texture)
        offset_y = int(obj.y_texture - self.y_texture)
        return self.mask.overlap(obj.mask, (offset_x, offset_y))


# music

current_song = randint(0, len(BACKGROUND_SONGS) - 1)
changed = datetime.datetime.utcnow() - datetime.timedelta(seconds=2)


def flip_sound():
    global changed
    global current_song
    if datetime.datetime.utcnow() - changed < datetime.timedelta(seconds=1):
        return  # prevent spamming, I have when 'e' is pressed it calls this like 4-5 times
    changed = datetime.datetime.utcnow()
    pygame.mixer.Channel(1).stop()
    current_song = (current_song + 1) % len(BACKGROUND_SONGS)
    pygame.mixer.Channel(1).play(BACKGROUND_SONGS[current_song])


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

    while True:
        clock.tick(TICK_RATE)
        frame += 1
        if frame == TICK_RATE:
            frame = 0

        screen.blit(TEXTURE_BACKGROUND, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        player.tick()

        for enemy in enemies:
            # if enemy.alive:
            #     if "normal" in enemy.vulnerabilities or ("dash" in enemy.vulnerabilities and player.dashing):
            #         if player.colliding(enemy):
            #             player.apply_effect(enemy.on_collide())
            if enemy.alive and player.colliding(enemy):
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
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.Channel(1).set_volume(0.1)
    flip_sound()
    game_loop()
    pygame.quit()


if __name__ == '__main__':
    main()
