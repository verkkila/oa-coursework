from eventlistener import Subject, Event

class Input(Subject):
    def __init__(self):
        Subject.__init__(self)
        self.mouse_state_old = (0, 0, 0)

    def mouse_pressed(self, mouse_state_new):
        self.mouse_state_old = mouse_state_new

    def mouse_released(self, mouse_state_new):
        if self.mouse_state_old[0] == 1 and mouse_state_new[0] == 0:
            self.notify_listeners(Event.MOUSE_LEFT)
        if self.mouse_state_old[2] == 1 and mouse_state_new[2] == 0:
            self.notify_listeners(Event.MOUSE_RIGHT)
        self.mouse_state_old = mouse_state_new
