class IoBase():
    key_back = 8
    key_select = 13
    key_left = 37
    key_up = 38
    key_right = 39
    key_down = 40
    key_m = 77
    def __init__(self, stop_event, keyboard_callback, close_callback):
        self.stop_event = stop_event
        self.keyboard_callback = keyboard_callback
        self.close_callback = close_callback

    def bitblt(self, image):
        NotImplementedError

