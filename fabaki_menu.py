import pygame
import random


class MenuElement:
    def __init__(self, x=-1, y=-1, onclick=None, onclick_args=(), onclick_kill=True):
        self.x = x
        self.y = y
        self.texture = None
        self.width = 0
        self.height = 0
        self.onclick = onclick
        if onclick is None:
            self.onclick = MenuElement.onclick_dummy
        if onclick_kill:
            self.onclick = MenuElement.onclick_kill_dummy
        self.onclick_args = onclick_args

    def draw(self, screen):
        if self.texture is None:
            return
        screen.blit(self.texture, (self.x, self.y))

    @staticmethod
    def onclick_dummy():  # If this returns True, stop the menu
        return

    @staticmethod
    def onclick_kill_dummy():  # If this returns True, stop the menu
        return True


class TextElement(MenuElement):
    def __init__(self, text, font, text_color=(255, 255, 255), x=0, y=0, onclick=None, onclick_args=()):
        MenuElement.__init__(self, x, y, onclick, onclick_args)
        self.text = text
        self.font = font
        self.texture = self.font.render(self.text, False, text_color)
        self.width = self.texture.get_rect().width
        self.height = self.texture.get_rect().height


class ButtonElement(MenuElement):
    def __init__(self, text, button_texture, font, x=0, y=0, width=-1, height=-1, onclick=None, onclick_args=(),
                 text_padding=10, text_color=(255, 255, 255), onclick_kill=False):
        MenuElement.__init__(self, x, y, onclick, onclick_args, onclick_kill=onclick_kill)
        self.text = text
        self.font = font
        self.text_texture = font.render(self.text, False, text_color)

        if type(button_texture) == str:
            self.button_texture = pygame.image.load(button_texture)
        else:
            self.button_texture = button_texture

        if width == -1 and height == -1:
            if type(button_texture) == str:
                self.width = self.button_texture.get_width()
                self.height = self.button_texture.get_height()
            else:
                self.width = self.text_texture.get_rect().width + text_padding
                self.height = self.text_texture.get_rect().height + text_padding

    def draw(self, screen):
        if self.text_texture is None:
            return
        if type(self.button_texture) == tuple:
            pygame.draw.rect(screen, self.button_texture, (self.x, self.y, self.width, self.height))
        else:
            screen.blit(self.button_texture, (self.x, self.y))
        screen.blit(self.text_texture, (self.x + self.width / 2 - self.text_texture.get_rect().width / 2,
                                        self.y + self.height / 2 - self.text_texture.get_rect().height / 2))


class Menu:
    def __init__(self, screen, auto=True, menu_width=-1, menu_height=-1,
                 menu_x=-1, menu_y=-1, element_x_padding=10, element_y_padding=-1, background=(0, 0, 0)):
        self.screen = screen
        self.elements = []
        self.menu_width = screen.get_width()
        if menu_width >= 0:
            self.menu_width = menu_width
        self.menu_height = screen.get_height()
        if menu_height >= 0:
            self.menu_height = menu_height

        self.menu_x = menu_x
        if menu_x < 0:
            self.menu_x = screen.get_width() / 2 - self.menu_width / 2
        self.menu_y = menu_y
        if menu_y < 0:
            self.menu_y = screen.get_height() / 2 - self.menu_height / 2
        self.auto = auto
        self.x_padding_elements = element_x_padding
        self.y_padding_elements = element_y_padding
        self.background = background
        if type(background) == str:
            self.background = pygame.image.load(background)

    def add_element(self, element):
        if self.auto:
            if type(element) != list:
                element = [element]
        self.elements.append(element)

    def elements_auto_place(self):
        padding_y = self.menu_height
        elements_x_offset = []
        for elements in self.elements:
            if len(elements) == 1:
                padding_y -= elements[0].height
            else:
                padding_y -= max(*elements, key=lambda e: e.height).height
            offset_x = self.menu_width
            for element in elements:
                offset_x -= element.width
            offset_x -= self.x_padding_elements * (len(elements) - 1)
            offset_x /= 2
            elements_x_offset.append((elements, offset_x))

        if self.y_padding_elements == -1:
            padding_y /= len(self.elements) + 1
            element_y = padding_y
        else:
            padding_y -= self.y_padding_elements * (len(self.elements) - 1)
            element_y = padding_y / 2
        for elements, offset_x in elements_x_offset:
            element_x = offset_x
            if len(elements) == 1:
                row_max_height = elements[0].height
            else:
                row_max_height = max(*elements, key=lambda e: e.height).height
            for element in elements:
                element.x, element.y = element_x, element_y + row_max_height / 2 - element.height / 2
                element_x += self.x_padding_elements + element.width
            if len(elements) == 1:
                element_y += elements[0].height
            else:
                element_y += max(*elements, key=lambda e: e.height).height
            if self.y_padding_elements == -1:
                element_y += padding_y
            else:
                element_y += self.y_padding_elements

    def menu_loop(self):
        if self.auto:
            self.elements_auto_place()
        while True:
            mouse_x, mouse_y = -1, -1
            mouse_button = 0
            if type(self.background) == tuple:
                self.screen.fill(self.background, (self.menu_x, self.menu_y, self.menu_width, self.menu_height))
            else:
                self.screen.blit(self.background, (self.menu_x, self.menu_y))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    mouse_button = event.button

            for elements in self.elements:
                for element in elements:
                    element.x += self.menu_x
                    element.y += self.menu_y
                    if mouse_button == 1 and element.x <= mouse_x <= element.x + element.width and \
                            element.y <= mouse_y <= element.y + element.height:
                        if element.onclick(*element.onclick_args):
                            return

                    element.draw(self.screen)
                    element.x -= self.menu_x
                    element.y -= self.menu_y
            pygame.display.update()


def main():
    pygame.init()

    screen = pygame.display.set_mode((1000, 1000))
    # menu = Menu(screen, auto=True, background=(100, 100, 100), menu_width=700, menu_height=700)
    # comic_sans = pygame.font.SysFont("Arial", 30)
    # funny = pygame.font.SysFont("Arial", 60)
    # menu.add_element([TextElement("ogen", comic_sans), TextElement("homo", funny)])
    # menu.add_element(TextElement("roy homo?", comic_sans))
    # menu.add_element([ButtonElement("Roy efes!", (255, 0, 255), comic_sans),
    #                   ButtonElement("Roy homo!", (0, 200, 0), comic_sans)])
    # menu.menu_loop()
    # print("Starting the game!")
    # pygame.display.quit()
    # pygame.quit()


if __name__ == "__main__":
    main()
