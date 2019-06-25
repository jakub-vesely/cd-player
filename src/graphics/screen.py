from PIL import Image, ImageDraw, ImageFont
from src.state import PlayingMode
import colorsys
class WidgetBase():
    text_alignment_left = "left"
    text_alignment_right = "right"
    multiplier = 2
    text_size = 14


    color1_darkest = (0x36, 0x6B, 0x01)
    color1_dark = (0x4E, 0x7B, 0x20)
    color1_mid = (0x54, 0xA4, 0x02)
    color1_light = (0xCC, 0xED, 0xAA)
    color2 = (0xA0, 0x02, 0x39)

    def __init__(self, imageDraw):
        self.imageDraw = imageDraw

    def _multiply(self, collection):
        return [item * self.multiplier for item in collection]

    def _draw_line(self, x1, y1, x2, y2, color, width):
        self.imageDraw.line(self._multiply((x1, y1, x2, y2)), color, int(width * self.multiplier))

    def _draw_pieslice(self, x1, y1, size, start, end, color):
        self.imageDraw.pieslice(self._multiply((x1, y1, x1 + size, y1 + size)), start, end, fill=color)

    def _draw_rectangle(self, x1, y1, x2, y2, fill_color, border_color=None):
        self.imageDraw.rectangle(self._multiply((x1, y1, x2, y2)), fill_color, border_color)

    def _draw_rounded_rectangle(self, x1, y1, x2, y2, radius, color):
        self._draw_rectangle(x1 + radius, y1 + radius, x2 - radius, y2 - radius, color)
        self._draw_rectangle(x1 + radius, y1, x2 - radius, y1 + radius, color)
        self._draw_rectangle(x1 + radius, y2 - radius, x2 - radius, y2, color)
        self._draw_rectangle(x2 - radius, y1 + radius, x2, y2 - radius, color)
        self._draw_rectangle(x1, y1 + radius, x1 + radius, y2 - radius, color)

        diameter = radius * 2
        self._draw_pieslice(x1, y1, diameter, 180, 270, color)
        self._draw_pieslice(x2 - diameter, y1, diameter, 270, 360, color)
        self._draw_pieslice(x2 - diameter, y2 - diameter, diameter, 0, 90, color)
        self._draw_pieslice(x1, y2 - diameter, diameter, 90, 180, color)

    def _draw_text(self, x, y, text, color, alignment, text_size=None):
        size = text_size if text_size else self.text_size
        font = ImageFont.truetype("DejaVuSansCondensed.ttf", size * self.multiplier, encoding="unic")
        x, y = self._multiply((x ,y))
        if alignment == self.text_alignment_right:
            width, _height = self.imageDraw.textsize(text, font=font)
            x = x - width
        self.imageDraw.text((x, y), text, font=font, fill=color)

class HeaderWidgetBase(WidgetBase):
    background_color = WidgetBase.color1_darkest
    inactive_color = WidgetBase.color1_dark
    active_color = (0xFF, 0xFF, 0xFF)


    def __init__(self, imageDraw):
        super().__init__(imageDraw)

class Wifi(HeaderWidgetBase):
    wifi_size = 22

    def __init__(self, imageDraw, offset):
        super().__init__(imageDraw)
        self.offset = offset

    def draw(self, level):
        x = self.offset[0]
        y = self.offset[1]
        size = self.wifi_size

        self._draw_pieslice(x, y, size, 225, 315, self.active_color if level > 2 else self.inactive_color)
        self._draw_pieslice(x + 2, y + 2, size-4, 225, 315, self.background_color)
        self._draw_pieslice(x + 4, y + 4, size-8, 225, 315, self.active_color if level > 1 else self.inactive_color)
        self._draw_pieslice(x + 6, y + 6, size-12, 225, 315, self.background_color)
        self._draw_pieslice(x + 8, y + 8, size-16, 225, 315, self.active_color if level > 0 else self.inactive_color)

class Bluetooth(HeaderWidgetBase):
    line_width = 1.5
    base_size = 3

    def __init__(self, imageDraw, offset):
        super().__init__(imageDraw)
        self.offset = offset

    def draw(self, connected):
        x = self.offset[0]
        y = self.offset[1]

        x1 = x
        x2 = x + self.base_size * 1.5
        x3 = x + self.base_size * 3
        y1 = y
        y2 = y + self.base_size
        y3 = y + self.base_size * 2
        y4 = y + self.base_size * 3
        y5 = y + self.base_size * 4
        color = self.active_color if connected else self.inactive_color
        self._draw_line(x2, y1, x2, y5, color, self.line_width)
        self._draw_line(x2, y1, x3, y2, color, self.line_width)
        self._draw_line(x3, y2, x1, y4, color, self.line_width)
        self._draw_line(x2, y5, x3, y4, color, self.line_width)
        self._draw_line(x3, y4, x1, y2, color, self.line_width)

class RepeatIcon(HeaderWidgetBase):
    line_width = 1.5
    base_size = 4
    def __init__(self, imageDraw, offset):
        super().__init__(imageDraw)
        self.offset = offset

    def _draw_pieslice_line(self, x, y, size, start, end,  width, color):
        self._draw_pieslice(x, y, size * 2, start, end, color)
        self._draw_pieslice(x + width, y + width, (size - width)* 2, start, end, self.background_color)


    def _draw_triangle(self, x, y, size, is_reverse, color):
        while True:
            self._draw_line(x, y - size / 2, x, y, color, self.line_width)
            self._draw_line(x, y, x, y + size / 2, color, self.line_width)
            size -= self.line_width
            if is_reverse:
                x -= self.line_width
            else:
                x += self.line_width
            if size <= 0:
                break

    def draw(self, repeat, one):
        x0 = self.offset[0]
        x1 = x0 + self.base_size
        x2 = x0 + self.base_size * 2
        x3 = x0 + self.base_size * 3
        x4 = x0 + self.base_size * 4

        y0 = self.offset[1]
        y1 = y0 + self.base_size
        y2 = y0 + self.base_size * 2
        y3 = y0 + self.base_size * 3
        y4 = y0 + self.base_size * 4

        self._draw_line(x0, y1, x0, y2, self.active_color, self.line_width)
        self._draw_pieslice_line(x0, y1, self.base_size, 90, 180, self.line_width, self.active_color)
        self._draw_line(x1, y3, x3, y3, self.active_color, self.line_width)
        self._draw_triangle(x3, y3, self.base_size, False, self.active_color)

        repeat_color = self.active_color if repeat else self.inactive_color
        self._draw_line(x4, y1, x4, y2, repeat_color, self.line_width)
        self._draw_pieslice_line(x2, y0, self.base_size, 270, 360, self.line_width, repeat_color)
        self._draw_line(x1, y0, x3, y0, repeat_color, self.line_width)
        self._draw_triangle(x1, y0, self.base_size, True, repeat_color)

        text_x = x0 + self.base_size * 1.5
        text_y = y0 + self.base_size / 2 - 1
        text_color = self.active_color if one else self.inactive_color
        self._draw_text(text_x, text_y, "1", text_color, self.text_alignment_left, 9)

class Header(HeaderWidgetBase):
    item_separator_height = 1
    offset_x = 4
    offset_y = 2
    item_height = 20
    header_text_color = (0xff, 0xff, 0xff)

    wifi_offset = (85, 3)
    bluetooth_offset = (110, 3)
    repeat_offset = (3, 3)

    def __init__(self, imageDraw, width):
        super().__init__(imageDraw)
        self.width = width
        self.wifi_icon = Wifi(self.imageDraw, self.wifi_offset)
        self.bluetooth_icon = Bluetooth(self.imageDraw, self.bluetooth_offset)
        self.repeat = RepeatIcon(self.imageDraw, self.repeat_offset)

    def _draw_label(self, item_y, label):
        self._draw_text(
                self.offset_x,
                item_y + self.offset_y,
                label,
                self.header_text_color,
                self.text_alignment_left
        )
    def draw_header(self, signal_strength, is_bluetooth_connected, interpret, album, repeate, one):
        height = self.item_height
        if interpret:
            height += self.item_height + self.item_separator_height
        if album:
            height += self.item_height + self.item_separator_height
        self._draw_rectangle(0, 0, self.width -1, height, self.background_color)

        self.wifi_icon.draw(signal_strength)
        self.bluetooth_icon.draw(is_bluetooth_connected)
        self.repeat.draw(repeate, one)

        y_start = self.item_height
        if interpret:
            self._draw_label(y_start, interpret)
            y_start += self.item_height + self.item_separator_height
        if album:
            self._draw_label(y_start, album)
        return height


class ListView(WidgetBase):
    def __init__(self, imageDraw, width):
        super().__init__(imageDraw)
        self.width = width

    list_item_color = WidgetBase.color2
    list_item_offset_x = 2
    list_item_height = 20
    list_item_radius = 4
    list_text_offset_x = 2
    list_text_offset_y = 2
    list_text_color_normal = (0x00, 0x00, 0x00)
    list_text_color_selected = (0xff, 0xff, 0xff)
    list_item_separator_height = 1

    def _draw_item_label(self, item_y, label, color):
        self._draw_text(
                self.list_item_offset_x + self.list_text_offset_x,
                item_y + self.list_text_offset_y,
                label,
                color,
                self.text_alignment_left
        )

    def _draw_list_item(self, y, label, selected):
        if selected:
            self._draw_rounded_rectangle(
                    self.list_item_offset_x,
                    y,
                    self.width - self.list_item_offset_x -1,
                    y + self.list_item_height,
                    self.list_item_radius,
                    self.list_item_color
            )

        self._draw_item_label(y, label, self.list_text_color_selected if selected else self.list_text_color_normal)

    def draw(self, state, start_y):
        y = start_y
        for local_index, item in enumerate(state.folder_content[state.screen_list_start: state.screen_list_start + state.screen_list_length]):
            self._draw_list_item(y, item, local_index == state.screen_list_index)
            y = y + self.list_item_separator_height + self.list_item_height
        return y


class PlayingProgress(WidgetBase):
    y_size = 41
    y_bottom_offset = 2
    text_offset_x = 9
    text_offset_y = 5
    text_color = (0x00, 0x00, 0x00)
    line_offset_x = 12
    line_offset_y = 29
    line_width = 1.5
    line_color = WidgetBase.color1_darkest
    background_color =  WidgetBase.color1_light
    pointer_color = WidgetBase.color1_mid
    pointer_size = 12

    def __init__(self, imageDraw, width, height):
        super().__init__(imageDraw)
        self.width = width
        self.height = height

    def draw(self, current_time, end_time, ratio):
        y = self.height - self.y_bottom_offset - self.y_size
        self._draw_rounded_rectangle(1, y + 1, self.width - 2, self.height - self.y_bottom_offset, 5, self.line_color)
        self._draw_rounded_rectangle(2.5, y + 2.5, self.width - 3.5, self.height - 3.5, 4.5, self.background_color)
        self._draw_text(
                self.text_offset_x,
                y + self.text_offset_y,
                current_time,
                self.text_color,
                self.text_alignment_left
        )
        self._draw_text(
                self.width - self.text_offset_x,
                y + self.text_offset_y,
                end_time,
                self.text_color,
                self.text_alignment_right
        )
        self._draw_line(
                self.line_offset_x,
                y + self.line_offset_y,
                self.width - self.line_offset_x,
                y + self.line_offset_y,
                self.line_color,
                self.line_width
        )
        line_length = self.width - self.line_offset_x - self.line_offset_x
        pointer_position = int(line_length * ratio)


        self._draw_pieslice(
                self.line_offset_x + pointer_position - self.pointer_size / 2,
                y + self.line_offset_y - self.pointer_size / 2,
                self.pointer_size,
                0,
                360,
                self.line_color,
        )

        self._draw_pieslice(
                self.line_offset_x + pointer_position - (self.pointer_size - 2) / 2 ,
                y + self.line_offset_y - (self.pointer_size - 2) / 2,
                self.pointer_size - 2,
                0,
                360,
                self.pointer_color,
        )

class Screen(WidgetBase):
    width = 128
    height = 128
    screen_background_color = (0xff, 0xff, 0xff)

    def __init__(self):
        self.image = Image.new("RGB", (self.width * self.multiplier, self.height * self.multiplier), self.screen_background_color)
        super().__init__(ImageDraw.Draw(self.image))

        self.header = Header(self.imageDraw, self.width)
        self.list_view = ListView(self.imageDraw, self.width)
        self.playing_progress = PlayingProgress(self.imageDraw, self.width, self.height)

    def render(self, state):
        self._draw_rectangle(0, 0, self.width, self.height, self.screen_background_color) #it is 1 pixel higher to be completely cleaned - there was fragments because of antialiasing

        repeate = state.playing_mode in (PlayingMode.repeat_song, PlayingMode.to_end_from_first)
        one = state.playing_mode in (PlayingMode.one_song, PlayingMode.repeat_song)
        header_height = self.header.draw_header(
                state.signal_strength, state.is_bluetooth_connected, state.header_line1, state.header_line2, repeate, one
        )
        self.list_view.draw(state, header_height + ListView.list_item_separator_height * 2) # to be separation more seeable

        if state.is_playing:
            self.playing_progress.draw(state.current_playing_time, state.total_playing_time, state.playing_ratio)
        out_image = self.image.resize((self.width, self.height), resample=Image.ANTIALIAS)
        return out_image
