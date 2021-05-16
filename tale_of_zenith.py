import datetime
from tale_of_zenith_header import *
import random
import pygame

screen = pygame.display.set_mode((SCREEN_SIZE[WIDTH], SCREEN_SIZE[HEIGHT]))
pygame.display.set_caption(GAME_CAPTION)
pygame.display.set_icon(TEXTURE_ICON)
random_object = random.Random()


class OnScreen:
    def __init__(self, x, y, texture):
        self.x = x
        self.y = y
        self.texture = texture
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


class Power:
    def __init__(self, entity, duration, cooldown):
        self.entity = entity
        self.duration = duration
        self.actual_duration = duration
        self.cooldown = cooldown
        self.active = False


class Effect:
    def __init__(self, entity, duration):
        self.entity = entity
        self.duration = duration
        self.actual_duration = duration
        self.active = False

    def start_effect(self):
        return

    def stop_effect(self):
        return

    def tick(self):
        return


class Regeneratable(OnScreen):
    def __init__(self, texture, regen_cooldown, effects=None, random_loc=True, x=-1, y=-1,
                 kill_conditions=None, kill_conditions_all=True):  # Kill conditions is {Effect: Immunity duration}
        OnScreen.__init__(self, x, y, texture)
        self.regen_cooldown = regen_cooldown
        self.random_loc = random_loc
        self.cooldown = 0
        self.alive = True
        if self.random_loc or x < 0 or y < 0:
            self.generate_random_loc()
        self.kill_conditions = kill_conditions
        if kill_conditions is None:
            self.kill_conditions = {}
        if type(kill_conditions) == tuple or type(kill_conditions) == list:
            self.kill_conditions = {kill_cond: None for kill_cond in self.kill_conditions}
        self.kill_conditions_all = kill_conditions_all
        if type(effects) == tuple:
            self.effects = effects
        else:
            self.effects = (effects, )

    def generate_random_loc(self):
        self.x, self.y = random_object.randint(SCREEN_PADDING, SCREEN_SIZE[WIDTH] - self.width - SCREEN_PADDING), \
                         random_object.randint(SCREEN_PADDING, SCREEN_SIZE[HEIGHT] - self.height - SCREEN_PADDING)

    def tick(self):
        if not self.cooldown:
            self.alive = True
        else:
            self.cooldown -= 1
        if self.alive:
            self.draw()

    def on_collide(self, entity):
        if self.kill_conditions_all:
            for cond, immunity in self.kill_conditions.items():
                if type(cond) == type and issubclass(cond, Effect):
                    for effect in entity.effects:
                        if cond != type(effect):
                            continue
                        if not effect.active:
                            return ()
                        if immunity is not None:
                            if effect.duration - effect.actual_duration > immunity:
                                return ()
                elif not cond.active:
                    return ()
                elif cond.active and immunity is not None:
                    if cond.duration - cond.actual_duration > immunity:
                        return ()
        else:
            kill_conditions_met = False
            for cond, immunity in self.kill_conditions.items():
                if type(cond) == type and issubclass(cond, Effect):
                    for effect in entity.effects:
                        if cond != type(effect):
                            continue
                        if effect.active:
                            if immunity is not None:
                                if effect.duration - effect.actual_duration > immunity:
                                    kill_conditions_met = True
                            else:
                                kill_conditions_met = True
                            break
                    if kill_conditions_met:
                        break
                elif cond.active:
                    if immunity is not None:
                        if cond.duration - cond.actual_duration > immunity:
                            kill_conditions_met = True
                    else:
                        kill_conditions_met = True
                    break
            if not kill_conditions_met:
                return ()

        if type(self.regen_cooldown) == tuple and len(self.regen_cooldown) == 2:
            self.cooldown = random_object.randint(*self.regen_cooldown)
        else:
            self.cooldown = self.regen_cooldown
        if self.random_loc:
            self.generate_random_loc()
        self.alive = False
        return self.effects


class RandomTeleportEffect(Effect):
    def __init__(self, entity, animation_duration=EFFECT_TELESHROOM_ANIMATION_DURATION):
        Effect.__init__(self, entity, animation_duration)
        self.changed_textures = []

    def start_effect(self):
        self.actual_duration = self.duration
        self.entity.x = random_object.randint(1, SCREEN_SIZE[WIDTH] - 2)
        self.entity.y = random_object.randint(1, SCREEN_SIZE[HEIGHT] - 2)
        self.entity.fix_location()

    def stop_effect(self):
        for changed_texture in self.changed_textures:
            load_direction_texture_match(changed_texture)

    def tick(self):  # Returns whether to stop
        for changed_texture in self.changed_textures:
            load_direction_texture_match(changed_texture)
            self.changed_textures.remove(changed_texture)
        if self.actual_duration % 6 <= 2:
            DIRECTION_TEXTURE_MATCH[self.entity.direction].fill((0, 0, 190, 100), special_flags=pygame.BLEND_SUB)
        else:
            DIRECTION_TEXTURE_MATCH[self.entity.direction].fill((190, 0, 0, 100), special_flags=pygame.BLEND_SUB)
        self.changed_textures.append(self.entity.direction)
        self.actual_duration -= 1
        if self.actual_duration <= 0:
            self.stop_effect()
            return True
        return False


class SpeedUpEffect(Effect):
    def __init__(self, entity, duration, power):
        Effect.__init__(self, entity, duration)
        self.power = power
        self.actual_duration = duration
        self.changed_textures = []
        self.active = False

    def start_effect(self):
        self.active = True
        self.actual_duration = self.duration
        self.entity.stats[STATS_VELOCITY] *= self.power

    def stop_effect(self):
        self.active = False
        self.entity.stats[STATS_VELOCITY] /= self.power
        for changed_texture in self.changed_textures:
            load_direction_texture_match(changed_texture)

    def tick(self):  # Returns whether to stop
        DIRECTION_TEXTURE_MATCH[self.entity.direction]\
            .fill((0, 190, 0, 100), special_flags=pygame.BLEND_SUB)
        self.changed_textures.append(self.entity.direction)
        self.actual_duration -= 1
        if self.actual_duration <= 0:
            self.stop_effect()
            return True
        return False


class ScoreUpEffect(Effect):
    def __init__(self, entity, power):
        Effect.__init__(self, entity, -1)
        self.power = power

    def start_effect(self):
        self.entity.stats[STATS_SCORE] += self.power


class DashPower(Power):
    def __init__(self, entity, direction):
        Power.__init__(self, entity, -1, -1)
        self.direction = direction
        self.power = -1
        self.ready = True

    def start_dash(self, direction, duration=DASH_DURATION, cooldown=DASH_COOLDOWN, power=DASH_POWER):
        if not self.ready:
            return False
        self.direction = direction
        self.duration = duration
        self.actual_duration = duration
        self.cooldown = cooldown
        self.power = power
        self.ready = False
        self.active = True
        self.entity.stats[STATS_MOVABLE] = False

        self.entity.texture.fill((190, 0, 0, 100), special_flags=pygame.BLEND_SUB)
        self.entity.stats[STATS_VELOCITY] *= self.power
        return True

    def stop_dash(self):
        self.duration = -1
        self.actual_duration = -1
        self.active = False
        self.entity.stats[STATS_MOVABLE] = True

        load_direction_texture_match(MOVE_DIRECTION_MATCH[tuple(self.direction)])
        self.entity.stats[STATS_VELOCITY] /= self.power

    def set_cooldown(self, cooldown):  # Can't stop dash! only to set the cooldown again when dash is un active
        if cooldown <= self.cooldown:
            return
        self.ready = False
        self.cooldown = cooldown

    def tick(self):
        if not self.active and self.cooldown > 0:
            self.cooldown -= 1
            return
        if self.actual_duration > 0:
            self.actual_duration -= 1
            self.entity.move_vector = self.direction

        if self.cooldown == 0:
            pygame.mixer.Channel(0).play(SOUND_TING)
            self.ready = True
            self.cooldown = -1
        if self.actual_duration == 0:
            self.stop_dash()
            self.actual_duration = -1


class SwordPowers:
    def __init__(self, sword):
        self.dash_effect = DashPower(sword, [0, 0])


class Sword(OnScreen):
    def __init__(self, x, y):
        OnScreen.__init__(self, x, y, DIRECTION_TEXTURE_MATCH[DIRECTION_NORTH])
        self.direction = DIRECTION_NORTH
        self.move_vector = [0, 0]  # By means of top-left, aka [1, 1] is South-East
        self.stats = {STATS_VELOCITY: SWORD_SPEED, STATS_SCORE: 0, STATS_MOVABLE: True}
        self.powers = SwordPowers(self)
        self.effects = []
        self.current_tick = 0

    def change_dir(self, new_dir):
        self.direction = new_dir
        self.texture = DIRECTION_TEXTURE_MATCH[new_dir]
        self.mask = TEXTURE_MASK_MATCH[new_dir]

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
        if not self.powers.dash_effect.active and self.current_tick % SWORD_ANIMATION_DELAY == 0:
            self.next_direction()
        if self.current_tick == SWORD_ANIMATION_DELAY * 2:
            self.current_tick = 1

        self.move_vector = [0, 0]

        self.keys_handler()

        self.powers.dash_effect.tick()
        for effect in self.effects:
            if effect.tick():
                self.effects.remove(effect)

        self.move()
        self.draw()

    def keys_handler(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_e]:
            flip_sound()

        if self.stats[STATS_MOVABLE]:
            self.move_keys(keys)

            if self.move_vector == [0, 0]:  # We didn't move, so we can dash
                if self.powers.dash_effect.ready and keys[pygame.K_SPACE]:
                    self.powers.dash_effect.start_dash(list(DIRECTION_MOVE_MATCH[self.direction]))
            else:
                self.change_dir(MOVE_DIRECTION_MATCH[tuple(self.move_vector)])
                self.powers.dash_effect.set_cooldown(DASH_MOVE_COOLDOWN)

    def move_keys(self, keys):
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.move_vector[0] -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.move_vector[0] += 1
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.move_vector[1] -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.move_vector[1] += 1

    def move(self):
        self.x += self.move_vector[0] * self.stats[STATS_VELOCITY]
        self.y += self.move_vector[1] * self.stats[STATS_VELOCITY]
        self.fix_location()

    def apply_effect(self, object_effects):
        for effect in object_effects:
            effect.start_effect()
            self.effects.append(effect)

    def colliding(self, obj):
        offset_x = int(obj.x_texture - self.x_texture)
        offset_y = int(obj.y_texture - self.y_texture)
        return self.mask.overlap(obj.mask, (offset_x, offset_y))


current_song = random_object.randint(0, len(BACKGROUND_SONGS) - 1)
changed = datetime.datetime.utcnow() - datetime.timedelta(seconds=2)


def flip_sound():
    global changed
    global current_song
    if datetime.datetime.utcnow() - changed < datetime.timedelta(seconds=1):
        return  # prevent spamming, I have when 'e' is pressed it calls this like 4-5 times
    changed = datetime.datetime.utcnow()
    pygame.mixer.Channel(1).stop()
    current_song = (current_song + 1) % len(BACKGROUND_SONGS)
    pygame.mixer.Channel(1).play(BACKGROUND_SONGS[current_song], loops=-1)


def game_loop():
    player = Sword(SCREEN_SIZE[WIDTH] / 2, SCREEN_SIZE[HEIGHT] / 2)
    entities = [Regeneratable(TEXTURE_SLIME, 10, effects=ScoreUpEffect(player, EFFECT_SLIME_SCORE)),
                Regeneratable(TEXTURE_SLIME, 10, effects=ScoreUpEffect(player, EFFECT_SLIME_SCORE)),
                Regeneratable(TEXTURE_SLIME, 10, effects=ScoreUpEffect(player, EFFECT_SLIME_SCORE)),
                Regeneratable(TEXTURE_GOLDEN_SLIME, (100, 300),
                              kill_conditions={player.powers.dash_effect: EFFECT_GOLDEN_SLIME_DASH_IMMUNITY,
                                               SpeedUpEffect: None}, kill_conditions_all=False,
                              effects=ScoreUpEffect(player, EFFECT_GOLDEN_SLIME_SCORE)),
                Regeneratable(TEXTURE_SPEED_MUSH, 50,
                              effects=SpeedUpEffect(player, EFFECT_SPEED_MUSH_DURATION, EFFECT_SPEED_MUSH_POWER)),
                Regeneratable(TEXTURE_TELESHROOM, 50, effects=RandomTeleportEffect(player))]
    clock = pygame.time.Clock()
    start_time = datetime.datetime.utcnow()
    text_font = pygame.font.SysFont("comicsansms", 16)
    progress_width = 10
    progress_height = 150
    game_settings = {SETTINGS_TICK_RATE: TICK_RATE}

    while True:
        clock.tick(game_settings[SETTINGS_TICK_RATE])

        screen.blit(TEXTURE_BACKGROUND, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        player.tick()

        for enemy in entities:
            if enemy.alive and player.colliding(enemy):
                player.apply_effect(enemy.on_collide(player))
            enemy.tick()

        player.draw()

        fps_text = text_font.render(f"fps: {round(clock.get_fps())}", False, (255, 255, 255))
        time_elapsed = datetime.datetime.utcnow() - start_time
        time_text = text_font.render(f"Time: {str(time_elapsed.seconds // 3600).zfill(2)}:"
                                     f"{str(time_elapsed.seconds % 3600 // 60).zfill(2)}:"
                                     f"{str(time_elapsed.seconds % 60).zfill(2)}", False, (255, 255, 255))
        score_text = text_font.render(f"Score: {player.stats[STATS_SCORE]}", False, (255, 255, 255))

        if player.powers.dash_effect.ready:
            pygame.draw.rect(screen, (100, 30, 255), (SCREEN_SIZE[WIDTH] - 10 - progress_width, 10, progress_width,
                                                      progress_height))
            pygame.draw.rect(screen, (100, 20, 110), (SCREEN_SIZE[WIDTH] - 10 - progress_width, 10, progress_width,
                                                      progress_height), 2)
        else:
            pygame.draw.rect(screen, (0, 200, 255), (SCREEN_SIZE[WIDTH] - 10 - progress_width, 10, progress_width,
                                                     round(((DASH_COOLDOWN - player.powers.dash_effect.cooldown)
                                                            * progress_height / DASH_COOLDOWN))))
            pygame.draw.rect(screen, (0, 110, 110), (SCREEN_SIZE[WIDTH] - 10 - progress_width, 10, progress_width,
                                                     progress_height), 2)
        screen.blit(fps_text, (0, 0))
        screen.blit(time_text, (SCREEN_SIZE[WIDTH] / 2 - time_text.get_rect().width / 2, 0))
        screen.blit(score_text, (SCREEN_SIZE[WIDTH] / 2 - score_text.get_rect().width / 2, time_text.get_rect().height))

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
