import msvcrt
import time
from threading import Thread, Event
from src.system.keyboard_base import KeyboardBase

class DesktopKeyboard(KeyboardBase):
    def __init__(self):
        KeyboardBase.__init__(self)
        self.drawing_thread = None
        self.stop_event = Event()

    def _listen_keyboard(self):
        while not self.stop_event.is_set():
            while not msvcrt.kbhit() and not self.stop_event.is_set():
                time.sleep(0.1)
            char = msvcrt.getch()
            print(char)
            self.press_callback_method(char)

    def register_keyboard_callback(self, method):
        KeyboardBase.register_keyboard_callback(self, method)
        self.stop_event.clear()
        self.drawing_thread = Thread(target=self._listen_keyboard, args=[])
        self.drawing_thread.start()

    def unregister_keyboard_callback(self):
        self.stop_event.set()
