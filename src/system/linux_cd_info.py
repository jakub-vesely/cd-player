from subprocess import Popen, PIPE, STDOUT
from threading import Thread, Event, Lock
from time import sleep

class LinuxCdInfo():
    def __init__(self, stop_event, cd_track_count_callback, cd_track_names_callback):
        self.stop_event = stop_event
        self.cd_track_count_callback = cd_track_count_callback
        self.cd_track_names_callback = cd_track_names_callback

        self.count = -1
        self.thread = Thread(target=self._listening, args=[])
        self.thread.start()


    def _listening(self):
        while not self.stop_event.isSet():
            new_count = self._get_track_count()
            if new_count != self.count:
                self.count = new_count
                self.cd_track_count_callback(new_count)
                if self.count:
                     self.cd_track_names_callback(self._get_track_names())
            sleep(0.5)

    def _get_disk_id(self):
        subprocess = Popen(["cd-discid"], stdout=PIPE)
        return str( subprocess.communicate()[0], "ascii")

    def _get_track_count(self):
        disc_id = self._get_disk_id()
        return len(disc_id.split(" ")) - 3 if disc_id else 0

    def _get_prefix(self, request):
        return ["cddb-tool", request, "http://freedb.freedb.org/~cddb/cddb.cgi", "5", "$(whoami)", "$(hostname)"]

    def _get_track_names(self):
        output = list()
        disc_id = self._get_disk_id().strip().split(" ")

        query_subprocess = Popen(self._get_prefix("query") + disc_id, stdout=PIPE)
        query_output =  str(query_subprocess.communicate()[0], 'ISO-8859-1')
        query_lines = query_output.split("\n")
        if len(query_lines) > 2: #line(s) + empty line
            genre_line = query_lines[1]
            genre = [genre_line.split(" ")[0], genre_line.split(" ")[1]]
        else:
            genre_line = query_lines[0]
            genre = [genre_line.split(" ")[1], genre_line.split(" ")[2]]

        read_subprocess = Popen(self._get_prefix("read") + genre + disc_id, stdout=PIPE)
        read_output =  str(read_subprocess.communicate()[0], 'ISO-8859-1')
        lines = read_output.split("\n")
        counter = 1
        for line in lines:
            if line.startswith("TTITLE"):
                line_parts = line.split("=")
                output.append("{}-{}".format(counter, line_parts[1].strip()))
                counter += 1
        return output
