class State():
    def __init__(self):
        self.signal_strength = 0
        self.is_bluetooth_available = False

        self.folder_path = "/"
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

    def move_down_request(self):
        return False

    def move_up_request(self):
        return False

    def got_to_upper_folder_request(self):
        return False

    def got_to_subfolder_request(self):
        return False

    def play_request(self):
        return False

    def stop_request(self):
        return False

    def folder_content_change_request(self, new_content):
        return False

    def playing_progress_change_request(self, new_state):
        return False
