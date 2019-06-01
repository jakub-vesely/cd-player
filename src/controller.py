import os
import logging
import sys
import time
from queue import Queue
from threading import Event

from src.system.cd_info import CdInfo
from src.system.io_base import IoBase
from src.system.player import Player
from src.system.timer import Timer
from src.graphics.screen import Screen
from src.state import State


class Controller():
    queue_sleep_time = 0.1

    def __init__(self, use_hat):
        self.use_hat = use_hat
        self.stop_event = Event() #to be possible to stop threads
        self.request_queue = Queue() #queue of two tuples where the first element is method and the rest are the method's arguments
        self.screen = Screen()
        self.state = State()
        if use_hat:
            pass
            #from src.system. import HatDisplay
            #from src.system.raspberry_hat.hat_keyboard import HatKeyboard
            #self.display = HatDisplay(self.stop_event, self.screen.image)
            #self.keyboard = HatKeyboard()
        else:
            from src.system.desktop_io import DesktopIo
            self.io = DesktopIo(self.stop_event, self._key_pressed, self._close, self.screen.image)

        # self.cd_info = CdInfo()
        # self.player = Player()

    def _key_pressed(self, key_code):
        if key_code == IoBase.key_up:
            self.request_queue.put((self._process_key_up,)) #must be called indirectly to be processed in main thread
        elif key_code == IoBase.key_down:
            self.request_queue.put((self._process_key_down,)) #must be called indirectly to be processed in main thread
        elif key_code == IoBase.key_select:
            self.request_queue.put((self._update_folder_data, ("Ja do lesa nepojedu", "Bezi liska k taboru"), ("Song1", "Song2", "Song3", "Song4", "Song5", "Song6")))
        elif key_code == IoBase.key_left:
            self.request_queue.put((self._process_key_left,))
        elif key_code == IoBase.key_right:
            self.request_queue.put((self._process_key_right,))

    def _close(self):
        self.request_queue.put((self._terminate,)) #must be called indirectly to be processed in main thread

    def _terminate(self):
        print("terminating")
        self.stop_event.set()
        return False

    def _stop_playing(self):
        self.state.is_playing = False
        self._adjust_screen_list()


    def _start_playing(self):
        self.state.is_playing = True
        self.state.screen_list_length = 1
        self._adjust_screen_list()
        return True

    def _process_key_left(self):
        return self._start_playing()

    def _process_key_right(self):
        return self._start_playing()

    def _process_key_up(self):
        if self.state.folder_index == 0:
            return False#I'm on the end nothing to do
        self.state.folder_index -= 1
        self.state.screen_list_index -= 1
        self._adjust_screen_list()
        return True

    def _process_key_down(self):
        if self.state.folder_index + 1 == len(self.state.folder_content):
            return False#I'm on the end nothing to do
        self.state.folder_index += 1
        self.state.screen_list_index += 1
        self._adjust_screen_list()
        return True

    def _process_key_select(self):
        pass
    def _process_key_back(self):
        pass

    def _go_to_subfolder(self):
        self.state.got_to_subfolder_request()


    def _initialize_state(self):
        self.state.folder_content = os.listdir(self.state.folder_path)
        #self.state.folder_content = ["Track1", "Track2", "Track3", "Track4", "Track5", "Track6",]
        self.state.screen_list_length = min(self.state.screen_list_max_length, len(self.state.folder_content))
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

        if self.state.screen_list_length > 2:
            if self.state.screen_list_index == self.state.screen_list_length -1: #If index is on the end of the screen list
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

        self.state.screen_list_length = min(self.state.screen_list_max_length, len(self.state.folder_content))
        if header and header[0]:
            self.state.header_line1 = header[0]
            self.state.screen_list_length -= 1
        if len(header) > 1 and header[1]:
            self.state.header_line2 = header[1]
            self.state.screen_list_length -= 1

        self._adjust_screen_list()
        return True

    def _perform_initial_procedure(self):
        self.request_queue.put((self._initialize_state,))

    def start(self):
        self._perform_initial_procedure()

        change_performed = False

        while True:
            request = self.request_queue.get(True, None)
            request_method = request[0]
            request_arguments = request[1:]
            change_performed |= request_method(*request_arguments)

            if self.stop_event.isSet():
                break

            if self.request_queue.empty() and change_performed:
                self.io.bitblt(self.screen.render(self.state))
                change_performed = False
