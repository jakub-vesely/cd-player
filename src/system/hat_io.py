from src.system.display_base import DisplayBase
class HatDisplay(DisplayBase):
    def __init__(self, stop_event, _image):
        DisplayBase.__init__(self, stop_event)

    def bitblt(self, image):
        pass

    def unregister_keyboard_callback(self):
        pass
