from enum import IntEnum

class Event(IntEnum):
    MOUSE_LEFT = 1
    MOUSE_RIGHT = 2
    PLAY_BUTTON_PRESSED = 3
    STATS_BUTTON_PRESSED = 4
    QUIT_BUTTON_PRESSED = 5
    GAME_WON = 6
    GAME_LOST = 7

class EventListener:
    def notify_event(self, event):
        pass

class Subject:
    """
    Subjectilla on lista sitä kuuntelevista EventListenereistä, Subject voi halutessaan kutsua EventListenerin
    notify_event -methodia, ja näin saadaan kätevästi infoa kulkemaan luokkien välillä.
    """
    def __init__(self):
        self.listeners = []

    def add_listener(self, listener):
        if not listener in self.listeners:
            self.listeners.append(listener)

    def notify_listeners(self, event):
        for listener in self.listeners:
            listener.notify_event(event)
