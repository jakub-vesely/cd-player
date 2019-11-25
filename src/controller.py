#!/usr/bin/env python
import os
import logging
import sys
from queue import Queue
from threading import Event, Timer

from src.system.io_base import IoBase
from src.system.player import Player
from src.graphics.screen import Screen
from src.state import State, PlayingMode
from src.system.music_file_system import MusicFileSystem

if sys.platform.startswith("win"):
    from src.system.win_cd_info import WinCdInfo as CdInfo
    from src.system.win_wifi import WinWifi as Wifi
    from src.system.win_bluetooth import WinBluettot as Bluetooth
    from src.system.win_usb_file_system import WinUsbFileSystem as Usb
else:
    from src.system.linux_cd_info import LinuxCdInfo as CdInfo
    from src.system.linux_wifi import LinuxWifi as Wifi
    from src.system.linux_bluetooth import LinuxBluettot as Bluetooth
    from src.system.linux_usb_file_system import LinuxUsbFileSystem as Usb

class Controller():
    connectivity_timeout_multiplier = 2
    playing_progress_multiplier = 1
    tenth_scheduler_timeout = 0.5
    tenth_scheduler_counter = 0
    queue_sleep_time = 0.1
    display_timeout = 60

    def __init__(self, use_hat):
        self.use_hat = use_hat
        self.display_time = self.display_timeout
        self.stop_event = Event() #to be possible to stop threads
        self.request_queue = Queue() #queue of two tuples where the first element is method and the rest are the method's arguments
        self.screen = Screen()
        self.state = State()
        self.wifi = Wifi()
        #self.cd_info = CdInfo(self.stop_event, self._cd_track_count_changed, self._cd_track_names_changed)
        self.bluetooth = Bluetooth()
        self.tenth_scheduler_timer = Timer(self.tenth_scheduler_timeout, self._process_tenth_scheduler_timeout)
        self.player = Player(self.stop_event, self._playing_time_changed, self._playing_filished)
        #self.usb = Usb(self.stop_event, self._usb_path_changed)
        self.file_systems = (MusicFileSystem(), Usb(), CdInfo())
        if use_hat:
            from src.system.hat_io import HatIo
            self.io = HatIo(self.stop_event, self._key_pressed, self._close)
        else:
            from src.system.desktop_io import DesktopIo
            self.io = DesktopIo(self.stop_event, self._key_pressed, self._close, self.screen.image)

        self._fill_list(0)

    def _get_file_system_names(self):
        names = list()
        for file_system in self.file_systems:
            if file_system.is_available():
                names.append(file_system.get_main_folder_name() + "/")
        return names

    def _playing_filished(self):
        self.request_queue.put((self._stop_playing, ))
        self.request_queue.put((self._move_to_next_and_play,))

    def _playing_time_changed(self, current_time, total_time):
        self.request_queue.put((self._change_playing_time, current_time, total_time))

    def _get_time_string(self, sec):
        minutes = int(sec / 60)
        return "{:02d}:{:02d}".format(minutes, (sec%(minutes*60) if minutes else sec))

    def _change_playing_time(self, current_time, total_time):
        self.state.current_playing_time = self._get_time_string(current_time)
        self.state.total_playing_time = self._get_time_string(total_time)
        self.state.playing_ratio = current_time / total_time if total_time else 0
        return True

    def _key_pressed(self, key_code):
        if self.display_time == 0:
            self.io.change_display_backlight(True)
            self.display_time = self.display_timeout
            return False #display will be waked up nothing change

        self.display_time = self.display_timeout

        if key_code == IoBase.key_up:
            self.request_queue.put((self._process_key_up,)) #must be called indirectly to be processed in main thread
        elif key_code == IoBase.key_down:
            self.request_queue.put((self._go_to_next_item,)) #must be called indirectly to be processed in main thread
        elif key_code == IoBase.key_select:
            self.request_queue.put((self._process_key_select,))
        elif key_code == IoBase.key_left:
            self.request_queue.put((self._process_key_left,))
        elif key_code == IoBase.key_right:
            self.request_queue.put((self._process_key_right,))
        elif key_code == IoBase.key_back:
            self.request_queue.put((self._process_key_back,))
        elif key_code == IoBase.key_m:
            self.request_queue.put((self._process_key_m,))

    def _close(self):
        self.request_queue.put((self._terminate,)) #must be called indirectly to be processed in main thread

    def _terminate(self):
        print("terminating")
        self.stop_event.set()
        return False

    def _stop_playing(self):
        self.player.stop_if_playing()
        self.state.is_playing = False
        self._set_screen_list_length()
        self._adjust_screen_list()
        return True

    def _move_to_next_and_play(self):
        if self.state.playing_mode == PlayingMode.one_song:
            return False #one song has been played
        elif self.state.playing_mode != PlayingMode.repeat_song:
            if len(self.state.folder_content) == self.state.folder_index + 1:
                if self.state.playing_mode == PlayingMode.to_end_from_first:
                    self._go_to_first_item()
                else:
                    return False #nothing to do last song has been played
            else:
                self._go_to_next_item()
        return self._start_playing()

    def _start_playing(self):
        is_cd_folder = isinstance(self.state.file_system,  CdInfo)
        if is_cd_folder:
            arg = self.state.folder_index
        else:
            if not self.state.file_system:
                return False
            arg = self.state.file_system.get_current_folder_path() + "/" + self.state.folder_content[self.state.folder_index]
            if not os.path.isfile(arg):
                return False #dir is not playable

        self.player.stop_if_playing()
        self.state.is_playing = True
        self._set_screen_list_length()
        self._adjust_screen_list()
        self.player.play(arg, is_cd_folder)
        return True

    def _process_key_left(self):
        if self.state.is_playing:
            value = int(self.state.playing_ratio * 100) - 10
            self.player.move(value if value  > 0 else 0)
            return False

        return self._go_to_upper_folder()

    def _process_key_right(self):
        if self.state.is_playing:
            value = int(self.state.playing_ratio * 100) + 10
            self.player.move(value if value < 100 else 100)
            return False

        return self._go_to_subfolder()

    def _process_key_up(self):
        if self.state.folder_index == 0:
            return False#I'm on the end nothing to do
        self.state.folder_index -= 1
        self.state.screen_list_index -= 1
        self._adjust_screen_list()
        return True

    def _go_to_next_item(self):
        if self.state.folder_index + 1 == len(self.state.folder_content):
            return False#I'm on the end nothing to do
        self.state.folder_index += 1
        self.state.screen_list_index += 1
        self._adjust_screen_list()
        return True

    def _process_key_select(self):
        if self.state.is_playing:
            return self._start_playing() #next song
        elif not self._go_to_subfolder():
            return self._start_playing() #it is file

        return True

    def _go_to_first_item(self):
        self.state.folder_index = 0
        self.state.screen_list_start = 0
        self.state.screen_list_index = 0

    def _change_folder(self):
        self.state.folder_content = self.state.file_system.get_current_folder_content()
        self._go_to_first_item()
        self.state.screen_list_length = self.state.screen_list_max_length

    def _process_key_m(self):
        self.state.playing_mode = PlayingMode.move(self.state.playing_mode)
        return True

    def _process_key_back(self):
        if not self.state.file_system and not self.bluetooth.is_connected():
            print("bluetooth connect required")
            self.bluetooth.requie_connetion()

        if self.state.is_playing:
            self._stop_playing()
            return True
        else:
            return self._go_to_upper_folder()

    def _go_to_subfolder(self):
        if not self.state.folder_content:
            return False #workaround when tha app is executed first time it is called this method because button press is erroneously detected

        item_name = self.state.folder_content[self.state.folder_index]
        if not item_name.endswith("/"): #folder contains / as a last character
            return False

        if self.state.file_system:
            if not self.state.file_system.go_to_subfolder(item_name[:-1]): #remove folder indicator
                return False
        else:
            for file_system in self.file_systems:
                if file_system.get_main_folder_name() == item_name[:-1]: #remove /
                    file_system.reset()
                    self.state.file_system = file_system
                    self.player.start_mplayer(isinstance(self.state.file_system,  CdInfo)) #mplayer is started in required mode to be start of song playing faster
                    break

        self._change_folder()
        return True

    def _go_to_upper_folder(self):
        if not self.state.file_system:
            return False
        if not self.state.file_system.go_to_upper_folder():
            self.state.file_system = None
            self._fill_list(0)
        else:
            self._change_folder()
        return True

    def _set_screen_list_length(self):
        max_lngth = self.state.screen_list_max_length - 2 if self.state.is_playing else self.state.screen_list_max_length
        self.state.screen_list_length = min(max_lngth, len(self.state.folder_content))

    def _fill_list(self, cd_track_count):
        if self.state.file_system:
            content = self.state.file_system.get_current_folder_content()
        else:
            content = self._get_file_system_names()
            if content == self.state.folder_content:
                return False #nothing to change
            self._go_to_first_item()

        self.state.folder_content = content
        self._set_screen_list_length()
        return True

    def _adjust_screen_list(self):
        if self.state.screen_list_index >= self.state.screen_list_length:
            diff = self.state.screen_list_length - self.state.screen_list_index - 1
            self.state.screen_list_start -= diff
            self.state.screen_list_index += diff

        if self.state.screen_list_index < 0:
            diff = -self.state.screen_list_index
            self.state.screen_list_start -= diff
            self.state.screen_list_index += diff

        end_diff = (self.state.folder_index - len(self.state.folder_content)) - (self.state.screen_list_index - self.state.screen_list_length)
        if end_diff > 0: #can happen when playing is finished
            for _i in range(0, end_diff):
                if self.state.screen_list_start - 1 > 0: #number of items can be less than window length
                    self.state.screen_list_start -= 1
                    self.state.screen_list_index += 1

        if self.state.screen_list_length > 2:
            if self.state.screen_list_index == self.state.screen_list_length -1: #if index is on the end of the screen list
                if self.state.screen_list_start + self.state.screen_list_index != len(self.state.folder_content)-1: #and index is not on the end of folder list
                    self.state.screen_list_start += 1
                    self.state.screen_list_index -= 1

            if self.state.screen_list_index == 0 and self.state.screen_list_start != 0:
                self.state.screen_list_start -= 1
                self.state.screen_list_index += 1

    def _update_folder_data(self, header, content):
        if self.state.folder_index >= len(self.state.folder_content):
            logging.error("folder content is unexpectedly short")
            return False #The change can't be performed

        self.state.folder_content = content

        self._set_screen_list_length()
        if header and header[0]:
            self.state.header_line1 = header[0]
            self.state.screen_list_length -= 1
        if len(header) > 1 and header[1]:
            self.state.header_line2 = header[1]
            self.state.screen_list_length -= 1

        self._adjust_screen_list()
        return True

    def _set_signnal_strength(self, signal_strength):
        if signal_strength != self.state.signal_strength:
            self.state.signal_strength = signal_strength
            return True
        return False

    def _process_wifi(self):
        strength = self.wifi.get_strength()
        if strength > 0.67:
            signal_strength = 3
        elif strength > 0.34:
            signal_strength = 2
        elif strength > 0:
            signal_strength = 1
        else:
            signal_strength = 0
        self.request_queue.put((self._set_signnal_strength, signal_strength))

    def _set_bluetooth_state(self, is_connected):
        if is_connected != self.state.is_bluetooth_connected:
            self.state.is_bluetooth_connected = is_connected
            return True
        return False

    def _process_blutooth(self):
        self.request_queue.put((self._set_bluetooth_state, self.bluetooth.is_connected()))

    def _process_tenth_scheduler_timeout(self):
        if self.tenth_scheduler_counter % self.connectivity_timeout_multiplier == 0:
            self._process_wifi()
            self._process_blutooth()
            if not self.state.file_system:
                self.request_queue.put((self._fill_list, 0))

        if self.display_time > 0:
            self.display_time -= 1
            if self.display_time == 0:
                self.io.change_display_backlight(False)


        if self.state.is_playing and self.tenth_scheduler_counter % self.playing_progress_multiplier == 0:
            self.player.ask_fort_time()

        self.tenth_scheduler_timer = Timer(self.tenth_scheduler_timeout, self._process_tenth_scheduler_timeout)
        self.tenth_scheduler_timer.start()
        self.tenth_scheduler_counter += 1

    def start(self):
        change_performed = False
        self.tenth_scheduler_timer.start()
        self.bluetooth.start_connection_threead()
        while True:
            request = self.request_queue.get(True, None)
            request_method = request[0]
            request_arguments = request[1:]
            change_performed |= request_method(*request_arguments)

            if self.stop_event.isSet():
                self.tenth_scheduler_timer.cancel()
                break

            if self.request_queue.empty() and change_performed and self.display_time > 0:
                self.io.bitblt(self.screen.render(self.state))
                change_performed = False
