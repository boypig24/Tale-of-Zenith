import pygame


class TextElement:
    def __init__(self, text, font=None, x=0, y=0):
        self.text = text
        self.font = font
        self.x = x
        self.y = y
        self.texture = font.render(self.text, False, (255, 255, 255))


class Menu:
    def __init__(self):
        self.elements = []

    def add_element(self, element):
        self.elements.append(element)

    def draw(self, screen):
        for element in self.elements:
            screen.blit(element.texture, (element.x, element.y))


if __name__ == "__main__":
    screen = pygame.display.set_mode((500, 500))
    pygame.init()
    menu = Menu()
    font = pygame.font.SysFont("comicsansms", 16)
    menu.add_element(TextElement("ogen", font=font))
    looping = True
    while looping:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                looping = False
                break

        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            break

        menu.draw(screen)
        pygame.display.update()
    pygame.quit()
