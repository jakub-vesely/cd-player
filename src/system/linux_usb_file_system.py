import os
from src.system.real_file_system_base import RealFileSystemBase
class WinUsbFileSystem(RealFileSystemBase):
    main_folder_path = "~/Music/"
    current_folder_path = main_folder_path
    def __init__(self):
        super().__init__()

    def _get_main_folder_path(self):
        return "/mnt/usb"

    def get_main_folder_name(self):
        return "/mnt/USB"

    def _mount(self):
        pass #TODO

    def is_available(self):
        if not  os.path.isdir(self._get_main_folder_path()):
            return False

        if not self.get_current_folder_content():
            self._mount()

        return len(self.get_current_folder_content()) > 0
