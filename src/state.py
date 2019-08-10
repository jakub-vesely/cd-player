from os.path import expanduser

class PlayingMode():
    to_end = "to_end"
    to_end_from_first = "to_end_from_first"
    repeat_song = "repeat_song"
    one_song = "one_song"

    @staticmethod
    def move(current):
        if current == PlayingMode.to_end:
            return PlayingMode.to_end_from_first
        if current == PlayingMode.to_end_from_first:
            return PlayingMode.repeat_song
        if current == PlayingMode.repeat_song:
            return PlayingMode.one_song
        if current == PlayingMode.one_song:
            return PlayingMode.to_end

class State():
    def __init__(self):
        self.signal_strength = 0
        self.is_bluetooth_connected = False

        self.folder_content = []
        self.file_system = None
        self.folder_index = 0
        self.is_cd_folder = False

        self.header_line1 = ""
        self.header_line2 = ""

        self.screen_list_max_length = 5
        self.screen_list_length = 0 #length of on-screen list
        self.screen_list_start = 0 #position of first element in folder list
        self.screen_list_index = 0 #position in on-screen list from start

        self.is_playing = False
        self.current_playing_time = ""
        self.total_playing_time = ""
        self.playing_ratio = 0
        self.playing_mode = PlayingMode.to_end
        self.random_playing = False
