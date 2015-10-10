import pygame
from enum import IntEnum
from eventlistener import Subject, Event
from color import Color

class Button:
    class Type(IntEnum):
        PLAY = 1
        STATS = 2
        QUIT = 3

    def __init__(self, rect, btn_type, btn_text):
        self.rect = rect
        self.type = btn_type
        self.text = btn_text

    def draw(self, screen):
        pygame.draw.rect(screen, Color.DARK_GREY, self.rect)
        screen.blit(self.text, self.text.get_rect(center=(150, self.rect[1]+25)))

class Menu(Subject):
    """
    Tekee pelille päävalikon jossa on kolme näppäintä ja hoitaa niiden piirtämisen ja painallusten tarkastamisen.
    """
    def __init__(self):
        Subject.__init__(self)
        self.buttons = []
        self.main_menu = pygame.display.set_mode((300, 300))
        pygame.display.set_caption("Minesweeper")
        self.font = pygame.font.Font(None, 32)
        self.buttons.append(Button((50, 50, 200, 50), Button.Type.PLAY, self.font.render("Start game", 1, Color.BLACK)))
        self.buttons.append(Button((50, 125, 200, 50), Button.Type.STATS, self.font.render("View statistics", 1, Color.BLACK)))
        self.buttons.append(Button((50, 200, 200, 50), Button.Type.QUIT, self.font.render("Exit game", 1, Color.BLACK)))
        self.draw()

    def draw(self):
        self.main_menu.fill(Color.GREY)
        for button in self.buttons:
            button.draw(self.main_menu)
        pygame.display.update()

    def check_buttons(self, mouse_pos):
        button_type = None
        for button in self.buttons:
            if self.point_inside_rect(mouse_pos, button.rect):
                button_type = button.type
        if button_type == None:
            return
        if button_type == Button.Type.PLAY:
            self.notify_listeners(Event.PLAY_BUTTON_PRESSED)
        elif button_type == Button.Type.STATS:
            self.notify_listeners(Event.STATS_BUTTON_PRESSED)
        elif button_type == Button.Type.QUIT:
            self.notify_listeners(Event.QUIT_BUTTON_PRESSED)

    def point_inside_rect(self, point, rect):
        #point = (x, y), rect = (x, y, width, height)
        if point[0] > rect[0] and point[0] < rect[0] + rect[2]:
            if point[1] > rect[1] and point[1] < rect[1] + rect[3]:
                return True
        return False
