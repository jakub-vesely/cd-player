import src.system.hat.LCD_1in44 as LCD_1in44
import src.system.hat.LCD_Config as LCD_Config
import RPi.GPIO as GPIO

from src.system.io_base import IoBase
class HatIo(IoBase):
    key1 = 21
    key2 = 20
    key3 = 16
    joystick_up = 6
    joystick_down = 19
    joystick_left = 5
    joystick_right = 26
    joystick_press = 13

    def __init__(self, stop_event, keyboard_callback, close_callback):
        IoBase.__init__(self, stop_event, keyboard_callback, close_callback)
        self.lcd = LCD_1in44.LCD()
        self.lcd.LCD_Init(LCD_1in44.SCAN_DIR_DFT)

        self._init_button(self.joystick_up, self.joystick_up_pressed)
        self._init_button(self.joystick_down, self.joystick_down_pressed)
        self._init_button(self.joystick_left, self.joystick_left_pressed)
        self._init_button(self.joystick_right, self.joystick_right_pressed)
        self._init_button(self.joystick_press, self.joystick_press_pressed)
        self._init_button(self.key1, self.key1_pressed)
        self._init_button(self.key3, self.key3_pressed)

    def _init_button(self, pin, method):
        GPIO.setup(pin, GPIO.IN, GPIO.PUD_UP)
        GPIO.add_event_detect(pin, GPIO.RISING, method)

    def joystick_up_pressed(self, arg):
        self.keyboard_callback(self.key_up)

    def joystick_down_pressed(self, arg):
        self.keyboard_callback(self.key_down)

    def joystick_left_pressed(self, arg):
        self.keyboard_callback(self.key_left)

    def joystick_right_pressed(self, arg):
        self.keyboard_callback(self.key_right)

    def joystick_press_pressed(self, arg):
        self.keyboard_callback(self.key_select)

    def key1_pressed(self, arg):
        self.keyboard_callback(self.key_back)

    def key3_pressed(self, arg):
        self.keyboard_callback(self.key_m)

    def bitblt(self, image):
        self.lcd.LCD_ShowImage(image,0, 0)

    def unregister_keyboard_callback(self):
        pass

    def change_display_backlight(self, is_on):
        GPIO.output(LCD_Config.LCD_BL_PIN, GPIO.HIGH if is_on else  GPIO.LOW)
