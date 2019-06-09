from os.path import expanduser

class State():
    def __init__(self):
        self.signal_strength = 0
        self.is_bluetooth_connected = False

        self.home_folder = expanduser("~") + "/Music"
        self.folder_path = self.home_folder
        self.folder_content = []
        self.folder_index = 0
        #self.is_cd_folder = False

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
