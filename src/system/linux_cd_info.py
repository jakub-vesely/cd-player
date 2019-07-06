from subprocess import Popen, PIPE, STDOUT, DEVNULL
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
        subprocess = Popen(["cd-discid"], stdout=PIPE, stderr=DEVNULL) #I do not want to display errors when cdrom is not connected
        return str( subprocess.communicate()[0], "ascii")

    def _get_track_count(self):
        disc_id = self._get_disk_id()
        return len(disc_id.split(" ")) - 3 if disc_id else 0

    def _get_prefix(self, request):
        return ["cddbcmd", "-m", "http", "cddb", request]

    def _get_track_names(self):
        output = list()
        disc_id = self._get_disk_id().strip().split(" ")

        query_subprocess = Popen(self._get_prefix("query") + disc_id, stdout=PIPE)
        query_output =  str(query_subprocess.communicate()[0], 'ISO-8859-1')
        query_lines = query_output.split("\n")
        if not query_lines[0].startswith("No match for disc ID"):
            line_items = query_lines[0].split(" ")
            categ = line_items[0]
            serial = line_items[1]
            read_subprocess = Popen(self._get_prefix("read") + [categ,  serial], stdout=PIPE)
            read_output =  str(read_subprocess.communicate()[0], 'ISO-8859-1')
            lines = read_output.split("\n")
            counter = 1
            for line in lines:
                if line.startswith("TTITLE"):
                    line_parts = line.split("=")
                    output.append("{}-{}".format(counter, line_parts[1].strip()))
                    counter += 1
        return output
