from fabaki_version_header import *
from random import randint
screen = None


class OnScreen:
    def __init__(self, x, y, texture, object_type):
        self.x = x
        self.y = y
        self.texture = texture
        self.object_type = object_type
        self.mask = pygame.mask.from_surface(self.texture)
        self.width = texture.get_rect().width
        self.height = texture.get_rect().height

    def coords(self):
        return self.x, self.y

    def draw(self):
        screen.blit(self.texture, (self.x - self.width/2, self.y - self.height/2))


class Regeneratable(OnScreen):
    # for creating a mushroom should be ('MUSH_TEXTURE', 30, type="speed_mush") usually the other are not touched
    # regen_cd CAN be a 2 sized tuple, where a,b are the min and max cooldown times!
    def __init__(self, texture, regen_cd, object_type=None, random_loc=True, x=-1, y=-1):
        OnScreen.__init__(self, x, y, texture, object_type)
        self.regen_cd = regen_cd
        self.random_loc = random_loc
        self.cooldown = 1
        if self.random_loc or x < 0 or y < 0:
            self.generate_random_loc()

    def generate_random_loc(self):
        return randint(0, SCREEN_SIZE[WIDTH]-self.width), randint(0, SCREEN_SIZE[HEIGHT]-self.height)

    def tick(self):
        if not self.cooldown:
            OnScreen.draw(self)
        else:
            self.cooldown -= 1

    def on_collide(self):
        if len(self.regen_cd) == 2:
            self.cooldown = randint(*self.regen_cd)
        else:
            self.cooldown = self.regen_cd
        if self.random_loc:
            self.generate_random_loc()
        return self.object_type

# collision handler shall look like this


EFFECTS = {
    "speedshroom": "speed",
    "teleshroom": "tp"
}

for obj in regens:
    if collide(player, obj):
        t = obj.on_collide()  # by calling on_collide it also kills the object!
        if t in EFFECTS:
            player.apply_effect(EFFECTS[t])
    obj.tick()  # tick ALSO calls the method which draws said object!
