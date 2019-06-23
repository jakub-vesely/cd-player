from subprocess import Popen, PIPE, STDOUT

class LinuxCdInfo():
    def _get_disk_id(src):
        subprocess = Popen(["cd-discid"], stdout=PIPE)
        return str( subprocess.communicate()[0], "ascii")
    def get_track_count(self):
        disc_id = self._get_disk_id()
        return len(disc_id.split(" ")) - 3 if disc_id else 0
