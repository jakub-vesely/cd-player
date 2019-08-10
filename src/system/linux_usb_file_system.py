import os
from subprocess import Popen, PIPE, STDOUT
from src.system.real_file_system_base import RealFileSystemBase
class LinuxUsbFileSystem(RealFileSystemBase):
    main_folder_path = "~/Music/"
    current_folder_path = main_folder_path
    def __init__(self):
        super().__init__()

    def _get_main_folder_path(self):
        return "/mnt/usb"

    def get_main_folder_name(self):
        return "USB"

    def _mount(self, device):
        subprocess = Popen(["mount", "-t", "vfat", device, "/mnt/usb/"], stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        stdout = subprocess.communicate()[0]
        print(stdout)
        return len(stdout) == 0

    def is_available(self):
        if not  os.path.isdir(self._get_main_folder_path()):
            return False

        if not self.get_current_folder_content():
            if (not self._mount("/dev/sda1")):
                self._mount("/dev/sdb1")

        return len(self.get_current_folder_content()) > 0
