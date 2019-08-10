from src.system.cd_info_base import CdInfoBase
from subprocess import Popen, PIPE, STDOUT, DEVNULL
from threading import Thread, Event, Lock
from time import sleep

class LinuxCdInfo(CdInfoBase):
    def __init__(self):
        super().__init__()

    def get_current_folder_content(self):
        if self._get_track_count():
            return self._get_track_names()
        return list()

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
