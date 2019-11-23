import sys
import logging
from subprocess import Popen, PIPE, STDOUT
from threading import Event, Thread
import time

class Player():
    ans_time_pos_porefix = "ANS_TIME_POSITION="
    ans_length_prefix = "ANS_LENGTH="
    player_executable = "mplayer"
    def __init__(self, stop_event, playing_time_callback, playing_filished_callback):
        self.stop_event = stop_event
        self.playing_time_callback = playing_time_callback
        self.playing_filished_callback = playing_filished_callback
        self.mplayer = None

        self.listening_thread = None
        self.stop_listening_event = Event()
        self.popen = None
        self.current_time = 0
        self.total_time = 0

    def _write_to_mplayer(self, request):
        self.mplayer.stdin.write(request)
        self.mplayer.stdin.flush()


    def _get_time(self, line, prefix):
        text = line.replace(prefix, "")
        parts = text.split(".") #real
        return int(parts[0])

    def _output_processor(self):
        while not self.stop_event.isSet() and not self.stop_listening_event.isSet():
            line =str(self.mplayer.stdout.readline(), "ascii")
            if line:
                logging.debug("mplayer: {}".format(line))
            if line.startswith('Exiting... (End of file)'):
                self.mplayer = None
                self.listening_thread = None
                self.stop_listening_event.clear()
                self.playing_filished_callback()
                return
            elif line.startswith(self.ans_time_pos_porefix):
                new_current_time = self._get_time(line, self.ans_time_pos_porefix)
                if self.current_time != new_current_time:
                    self.current_time = new_current_time
                    self.playing_time_callback(self.current_time, self.total_time)
            elif line.startswith(self.ans_length_prefix):
                new_total_time = self._get_time(line, self.ans_length_prefix)
                if self.total_time != new_total_time:
                    self.total_time = new_total_time
                    self.playing_time_callback(self.current_time, self.total_time)

    def start_mplayer(self):
        pass
    def _play(self, commands):
        parameters = [self.player_executable, "-slave", "-quiet", "-cache", "2048"]
        if not sys.platform.startswith("win"): #alsa is not available for win. I want to force this channel because I use bluetooth over alsa
            parameters += ["-ao", "alsa"]
        parameters += commands
        self.mplayer = Popen(parameters, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        self.current_time = 0
        self.total_time = 0
        self.playing_time_callback(self.current_time, self.total_time)
        self.stop_listening_event.clear()
        self.listening_thread = Thread(target=self._output_processor, args=[])
        self.listening_thread.start()

    def play(self, arg, is_cd_track):

        if is_cd_track:
            track_nr = arg+1 #if arg else -1 #when there is 0 is played whole CD
            if sys.platform.startswith("win"):
                device = "D:" #FIXME: hardcoded
            else:
                device = "/dev/cdrom"
            self._play(("-cdrom-device", {}, "cdda://{}".format(device, track_nr)))
        else:
            self._play((arg,))

    def stop_if_playing(self):
        if self.listening_thread:
            self.stop_listening_event.set()
            self.listening_thread.join(1)
            self.listening_thread = None
        if self.mplayer:
            self._write_to_mplayer(b'stop\n')
            self.mplayer.kill()
            self.mplayer = None

    def move(self, percentage):
        self._write_to_mplayer(bytes(f'set_property percent_pos {percentage}\r\n',  "ascii"))

    def ask_fort_time(self):
        if self.mplayer:
            self._write_to_mplayer(b'get_time_length\n')
            self._write_to_mplayer(b'get_time_pos\n')
