#!/usr/bin/env python

import os
import pygame
import input
import menu
import game
import filehandler
from sys import setrecursionlimit
from time import strftime
from enum import IntEnum
from eventlistener import EventListener, Event

class Minesweeper(EventListener):
    class State(IntEnum):
        INITIALIZING = 1
        AT_MENU = 2
        PLAYING = 3
        EXITING = 4

    def __init__(self):
        self.game_state = self.State.INITIALIZING
        os.environ["SDL_VIDEO_CENTERED"] = "1"
        pygame.init()
        self.frame_timer = pygame.time.Clock()
        self.input_handler = input.Input()
        self.input_handler.add_listener(self)
        self.main_menu = menu.Menu()
        self.main_menu.add_listener(self)
        self.file_handler = filehandler.FileHandler()
        self.settings = {"GridWidth": 10,
                         "GridHeight": 10,
                         "MineCount": 20}
        proposed_grid_width = self.file_handler.get_setting("GridWidth", 5, 35)
        if proposed_grid_width != None:
            self.settings["GridWidth"] = proposed_grid_width
        proposed_grid_height = self.file_handler.get_setting("GridHeight", 5, 30)
        if proposed_grid_height != None:
            self.settings["GridHeight"] = proposed_grid_height
        proposed_mine_count = self.file_handler.get_setting("MineCount", 1, self.settings["GridWidth"] * self.settings["GridHeight"] - 1)
        if proposed_mine_count != None:
            self.settings["MineCount"] = proposed_mine_count 

    def notify_event(self, event):
        """
        Käsittelee pelin sisäisiä tapahtumia.
        """
        if event == Event.MOUSE_LEFT:
            if self.game_state == self.State.AT_MENU:
                self.main_menu.check_buttons(pygame.mouse.get_pos())
            elif self.game_state == self.State.PLAYING:
                self.game_screen.check_tile(pygame.mouse.get_pos())
        elif event == Event.MOUSE_RIGHT:
            if self.game_state == self.State.PLAYING:
                self.game_screen.mark_tile(pygame.mouse.get_pos())
        elif event == Event.PLAY_BUTTON_PRESSED:
            self.game_state = self.State.PLAYING
            self.game_screen = game.Game(self.settings["GridWidth"], self.settings["GridHeight"], self.settings["MineCount"], self.frame_timer)
            self.game_screen.add_listener(self)
        elif event == Event.STATS_BUTTON_PRESSED:
            self.file_handler.print_statistics()
        elif event == Event.QUIT_BUTTON_PRESSED:
            self.game_state = self.State.EXITING
        elif event == Event.GAME_WON:
            self.log_game("W")
        elif event == Event.GAME_LOST:
            self.log_game("L")

    def log_game(self, game_result):
        """
        Koostaa pelatun pelin tilastoista merkkijonon.
        """
        stats = []
        stats.append(game_result)
        stats.append(strftime("%d.%m.%Y %H:%M:%S"))
        stats.append(str(self.settings["GridWidth"]))
        stats.append(str(self.settings["GridHeight"]))
        stats.append(str(self.settings["MineCount"]))
        minutes = int(self.game_screen.elapsed_time / 60000)
        seconds = int((self.game_screen.elapsed_time % 60000) / 1000)
        stats.append(str(minutes))
        stats.append(str(seconds))
        stats.append(str(self.game_screen.moves))
        self.file_handler.write_statistics(stats)
            
    def start(self):
        self.game_state = self.State.AT_MENU
        while self.game_state != self.State.EXITING:
            for event in pygame.event.get():
                self.handle_event(event)
            if self.game_state == self.State.PLAYING:
                self.game_screen.update()
            self.frame_timer.tick(120)
        self.quit()

    def handle_event(self, pygame_event):
        """
        Käsittelee pygamen puolelta tulevat tapahtumat.
        """
        if pygame_event.type == pygame.QUIT:
            self.game_state = self.State.EXITING
        elif pygame_event.type == pygame.MOUSEBUTTONDOWN:
            self.input_handler.mouse_pressed(pygame.mouse.get_pressed())
        elif pygame_event.type == pygame.MOUSEBUTTONUP:
            self.input_handler.mouse_released(pygame.mouse.get_pressed())
        elif pygame_event.type == pygame.KEYDOWN and self.game_state == self.State.PLAYING:
            if pygame_event.key == pygame.K_r:
                self.game_screen = game.Game(self.settings["GridWidth"], self.settings["GridHeight"], self.settings["MineCount"], self.frame_timer)
                self.game_screen.add_listener(self)
            if pygame_event.key == pygame.K_ESCAPE:
                self.game_state = self.State.AT_MENU
                self.main_menu = menu.Menu()
                self.main_menu.add_listener(self)
            if pygame_event.key == pygame.K_w:
                self.game_screen.win_game()
            if pygame_event.key == pygame.K_e:
                self.game_screen.lose_game()

    def quit(self):
        pygame.quit()

if __name__ == "__main__":
    setrecursionlimit(2000)
    msweep = Minesweeper()
    msweep.start()

