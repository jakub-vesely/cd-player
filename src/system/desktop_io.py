import logging
import time
from threading import Thread, Event, Lock
import tkinter as tk
from PIL import ImageTk
from src.system.io_base import IoBase

class DesktopIo(IoBase):
    def __init__(self, stop_event, keyboard_callback, close_callback, image):
        IoBase.__init__(self, stop_event, keyboard_callback, close_callback)
        self.redraw = Event()
        self.image_lock = Lock()

        self.drawing_thread = Thread(target=self._drawing, args=[image])
        self.drawing_thread.start()

    def key(self, event):
        print("pressed " + f"{repr(event.char)} #{event.keycode}")
        self.keyboard_callback(event.keycode)

    def _drawing(self, image):
        self.root = tk.Tk()
        canvas = tk.Canvas(self.root, width=128, height=128, bd=0, highlightthickness=0)
        canvas.pack(side=tk.LEFT, expand=1)

        self.image_lock.acquire()
        self.tkimage = ImageTk.PhotoImage(image)
        self.image_lock.release()

        canvas.create_image(0, 0, anchor=tk.NW, image=self.tkimage)

        self._on_update()
        self.root.bind("<Key>", self.key)
        self.root.mainloop()
        self.close_callback()

        #to be deleted in as the same thread as were created
        del(self.tkimage)
        del(self.root)

    def _on_update(self):
        if self.stop_event.is_set():
            print("drawing termination")
            return

        if self.redraw.isSet():
            logging.debug("redraw")
            self.tkimage.paste(self.image)
            self.redraw.clear()
        self.root.after(100, self._on_update)

    def bitblt(self, image):
        self.image_lock.acquire()
        self.image = image
        self.image_lock.release()
        self.redraw.set()
