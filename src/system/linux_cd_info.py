import logging
from src.system.cd_info_base import CdInfoBase
from subprocess import Popen, PIPE, STDOUT, DEVNULL, TimeoutExpired
from threading import Thread, Event, Lock
from time import sleep

class LinuxCdInfo(CdInfoBase):
    def __init__(self):
        super().__init__()
        self.last_disc_id = None
        self.last_track_names = None

    def get_current_folder_content(self):
        disc_id = self._get_disc_id()
        if disc_id == self.last_disc_id:
            return self.last_track_names
        self.last_disc_id = disc_id

        self.last_track_names = list()
        track_count = self._get_track_count(disc_id)
        if track_count:
            track_names = self._get_track_names_from_cddb(disc_id)
            self.last_track_names = track_names

        if not self.last_track_names: #second option it can take a time if there is not cd_text
            cd_text_names = self._get_track_names_from_cd_text()
            if cd_text_names:
                self.last_track_names = cd_text_names

        if not self.last_track_names: #last option
            for i in range(track_count):
                self.last_track_names.append(f"Track{i+1}")

        return self.last_track_names 

    def _get_track_names_from_cd_text(self):
        subprocess = Popen(["cd-info"], stdout=PIPE, stderr=DEVNULL) #I do not want to display errors when cdrom is not connected
        try:
            stdout = str( subprocess.communicate(timeout=10)[0], "utf-8") #10 sec should be enough for the case when data is available
        except TimeoutExpired:
            subprocess.kill()
            return list()

        track_info_pos =  stdout.find("CD-TEXT for Track")
        if track_info_pos == -1:
            return list()

        track_names = list()
        track_info_lines = stdout[track_info_pos:].split("\n")
        for line in track_info_lines:
            title_prefix = "TITLE: "
            title_prefix_pos = line.find(title_prefix)
            if title_prefix_pos == -1:
                continue
            track_names.append(line[title_prefix_pos + len(title_prefix):])
        return track_names

    def _get_disc_id(self):
        subprocess = Popen(["cd-discid"], stdout=PIPE, stderr=DEVNULL) #I do not want to display errors when cdrom is not connected
        return str( subprocess.communicate()[0], "ascii")

    def _get_track_count(self, disc_id):
        return len(disc_id.split(" ")) - 3 if disc_id else 0

    def _get_prefix(self, request):
        return ["cddbcmd", "-m", "http", "cddb", request]

    def _get_track_names_from_cddb(self, disc_id):
        output = list()
        processed_disc_id = disc_id.strip().split(" ")

        query_subprocess = Popen(self._get_prefix("query") + processed_disc_id, stdout=PIPE)
        query_output =  str(query_subprocess.communicate()[0], 'ISO-8859-1')
        query_lines = query_output.split("\n")
        if not query_lines[0].startswith("No match for disc ID"):
            line_items = query_lines[0].split(" ")
            if len(line_items) < 2:
                logging.error("unexpected line count in CD info")
                return output

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
