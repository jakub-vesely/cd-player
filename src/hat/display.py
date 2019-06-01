import sys

class Display():
    def __init__(self):
        pass

    def bitblt(self, image):
        if sys.platform.startswith("win"):
            import win32gui

