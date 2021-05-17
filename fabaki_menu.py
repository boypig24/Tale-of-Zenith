import pygame
import random


class MenuElement:
    def __init__(self, x=0, y=0, onclick=None, onclick_args=()):
        self.x = x
        self.y = y
        self.texture = None
        self.width = 0
        self.height = 0
        self.onclick = onclick
        if onclick is None:
            self.onclick = MenuElement.onclick_dummy
        self.onclick_args = onclick_args

    def draw(self, screen):
        if self.texture is None:
            return
        screen.blit(self.texture, (self.x, self.y))

    @staticmethod
    def onclick_dummy():  # If this returns True, stop the menu
        return


class TextElement(MenuElement):
    def __init__(self, text, font=None, x=0, y=0, onclick=None, onclick_args=()):
        MenuElement.__init__(self, x, y, onclick, onclick_args)
        self.text = text
        self.font = font
        self.texture = font.render(self.text, False, (255, 255, 255))
        self.width = self.texture.get_rect().width
        self.height = self.texture.get_rect().height


class ButtonElement(MenuElement):
    def __init__(self, text, color, x=0, y=0, width=-1, height=-1, font=None, onclick=None, onclick_args=()):
        MenuElement.__init__(self, x, y, onclick, onclick_args)
        self.text = text
        self.font = font
        self.texture = font.render(self.text, False, (255, 255, 255))
        self.color = color

        if width == -1 and height == -1:
            self.width = self.texture.get_rect().width + 10
            self.height = self.texture.get_rect().height + 10

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        if self.texture is None:
            return
        pygame.draw.rect(screen, self.color, self.rect)
        screen.blit(self.texture, (self.x + self.width / 2 - self.texture.get_rect().width / 2,
                                   self.y + self.height / 2 - self.texture.get_rect().height / 2))


class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.elements = []

    def add_element(self, element):
        self.elements.append(element)

    def menu_loop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

            for element in self.elements:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                buttons = pygame.mouse.get_pressed(5)
                if buttons[0] and element.x <= mouse_x <= element.x + element.width and \
                        element.y <= mouse_y <= element.y + element.height:
                    if element.onclick(*element.onclick_args):
                        return
                element.draw(self.screen)
            pygame.display.update()


def play():
    return True


def stop_loop():
    global loop
    loop = False
    return True


def main():
    global loop
    pygame.init()

    loop = True
    while loop:
        screen = pygame.display.set_mode((random.randint(200, 700), random.randint(200, 700)))
        menu = Menu(screen)
        comic_sans = pygame.font.SysFont("comicsansms", 16)
        menu.add_element(TextElement("ogen", font=comic_sans, onclick=stop_loop))
        menu.add_element(ButtonElement("Roy homo!", (0, 200, 0), font=comic_sans, x=100, y=100, onclick=play))
        menu.menu_loop()
        print("Starting the game!")
        pygame.display.quit()
    pygame.quit()


if __name__ == "__main__":
    main()
