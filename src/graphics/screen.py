from PIL import Image, ImageDraw, ImageFont

class Screen():
    text_alignment_left="left"
    text_alignment_right="right"
    width = 128
    height = 128
    multiplier = 2
    text_size = 14
    screen_background_color = (0xff, 0xff, 0xff)
    connected_color = (0xff, 0xff, 0xff)
    disconnected_color = (0x80, 0x80, 0x80)
    header_background_color = (0x66, 0x66, 0x66)
    header_text_color = (0xff, 0xff, 0xff)
    list_item_color = (0xC6, 0x04, 0x3C)
    list_item_offset_x = 2
    list_item_height = 20
    list_item_radius = 4
    list_text_offset_x = 2
    list_text_offset_y = 2
    list_text_color_normal = (0x00, 0x00, 0x00)
    list_text_color_selected = (0xff, 0xff, 0xff)
    list_item_separator_height = 1

    progress_text_offset_x = 8
    progress_text_offset_y = 4
    progress_text_color = (0xC6, 0x04, 0x3C)
    progress_line_offset_x = 10
    progress_line_offset_y = 28
    progress_line_width = 1.5
    progress_line_color =  (0x00, 0x00, 0x00)
    progress_pointer_color = (0xC6, 0x04, 0x3C)
    progress_pointer_size = 12

    def __init__(self):
        self.image = Image.new("RGB", (self.width * self.multiplier, self.height * self.multiplier), self.screen_background_color)
        self.draw = ImageDraw.Draw(self.image)

    def _multiply(self, collection):
        return [item * self.multiplier for item in collection]

    def _draw_line(self, x1, y1, x2, y2, color, width):
        self.draw.line(self._multiply((x1, y1, x2, y2)), color, int(width * self.multiplier))

    def _draw_pieslice(self, x1, y1, size, start, end, color):
        self.draw.pieslice(self._multiply((x1, y1, x1 + size, y1 + size)), start, end, fill=color)

    def _draw_rectangle(self, x1, y1, x2, y2, fill_color, border_color=None):
        self.draw.rectangle(self._multiply((x1, y1, x2, y2)), fill_color, border_color)

    def _draw_text(self, x, y, text, color, alignment):
        font = ImageFont.truetype("DejaVuSansCondensed.ttf", self.text_size * self.multiplier, encoding="unic")
        x, y = self._multiply((x ,y))
        if alignment == self.text_alignment_right:
            width, height = self.draw.textsize(text, font=font)
            x = x - width
        self.draw.text((x, y), text, font=font, fill=color)

    def _draw_wifi(self, x, y, level):
        size = 22

        self._draw_pieslice(x, y, size, 225, 315, self.connected_color if level > 2 else self.disconnected_color)
        self._draw_pieslice(x + 2, y + 2, size-4, 225, 315, self.header_background_color)
        self._draw_pieslice(x + 4, y + 4, size-8, 225, 315, self.connected_color if level > 1 else self.disconnected_color)
        self._draw_pieslice(x + 6, y + 6, size-12, 225, 315, self.header_background_color)
        self._draw_pieslice(x + 8, y + 8, size-16, 225, 315, self.connected_color if level > 0 else self.disconnected_color)

    def _draw_bluetooth(self, x, y, connected):
        size = 3
        x1 = x
        x2 = x + size * 1.5
        x3 = x + size * 3
        y1 = y
        y2 = y + size
        y3 = y + size * 2
        y4 = y + size * 3
        y5 = y + size * 4
        color = self.connected_color if connected else self.disconnected_color
        line_width = 1.5
        self._draw_line(x2, y1, x2, y5, color, line_width)
        self._draw_line(x2, y1, x3, y2, color, line_width)
        self._draw_line(x3, y2, x1, y4, color, line_width)
        self._draw_line(x2, y5, x3, y4, color, line_width)
        self._draw_line(x3, y4, x1, y2, color, line_width)


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

    def _draw_header(self, signal_strength, is_bluetooth_connected, interpret, album):
        height = self.list_item_height
        if interpret:
            height += self.list_item_height + self.list_item_separator_height
        if album:
            height += self.list_item_height + self.list_item_separator_height
        self._draw_rectangle(0, 0, self.width -1, height, self.header_background_color)

        self._draw_wifi(3, 3, signal_strength)
        self._draw_bluetooth(110, 3, is_bluetooth_connected)

        y_start =  self.list_item_height
        if interpret:
            self._draw_item_label(y_start, interpret, self.header_text_color)
            y_start += self.list_item_height + self.list_item_separator_height
        if album:
            self._draw_item_label(y_start, album, self.header_text_color)
        return height

    def _draw_list_view(self, state, start_y):
        y = start_y
        for local_index, item in enumerate(state.folder_content[state.screen_list_start: state.screen_list_start + state.screen_list_length]):
            self._draw_list_item(y, item, local_index == state.screen_list_index)
            y = y + self.list_item_separator_height + self.list_item_height
        return y

    def _draw_playing_progress(self, y, current_time, end_time, ratio):
        self._draw_text(
            self.progress_text_offset_x,
            y + self.progress_text_offset_y,
            current_time,
            self.progress_text_color,
            self.text_alignment_left
        )
        self._draw_text(
            self.width - self.progress_text_offset_x,
            y + self.progress_text_offset_y,
            end_time,
            self.progress_text_color,
            self.text_alignment_right
        )
        self._draw_line(
            self.progress_line_offset_x,
            y + self.progress_line_offset_y,
            self.width - self.progress_line_offset_x,
            y + self.progress_line_offset_y,
            self.progress_line_color,
            self.progress_line_width
        )
        line_length = self.width - self.progress_line_offset_x - self.progress_line_offset_x
        pointer_position = int(line_length * ratio)


        self._draw_pieslice(
            self.progress_line_offset_x + pointer_position - self.progress_pointer_size / 2,
            y + self.progress_line_offset_y - self.progress_pointer_size / 2,
            self.progress_pointer_size,
            0,
            360,
            self.progress_line_color,
        )

        self._draw_pieslice(
            self.progress_line_offset_x + pointer_position - (self.progress_pointer_size - 2) / 2 ,
            y + self.progress_line_offset_y - (self.progress_pointer_size - 2) / 2,
            self.progress_pointer_size - 2,
            0,
            360,
            self.progress_pointer_color,
        )


    def render(self, state):
        self._draw_rectangle(0,0, self.width, self.height, self.screen_background_color) #it is 1 pixel higher to be compleatelly cleaned - there was fragments because of antialiasing
        header_height = self._draw_header(state.signal_strength, state.is_bluetooth_connected, state.header_line1, state.header_line2)
        list_end_y = self._draw_list_view(state, header_height + self.list_item_separator_height * 2) # to be separation more seeable
        if state.is_playing:
            self._draw_playing_progress(list_end_y, state.current_playing_time, state.total_playing_time, state.playing_ratio)
        out_image = self.image.resize((self.width, self.height), resample=Image.ANTIALIAS)
        return out_image

