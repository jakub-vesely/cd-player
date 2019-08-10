from src.system.file_system_base import FileSystemBase
class CdInfoBase(FileSystemBase):
    def __init__(self):
        pass

    def get_main_folder_name(self):
        return "CD"

    def get_current_folder_path(self):
        return ""

    def go_to_upper_folder(self):
        return False #no subfolders - return to main folder

    def is_available(self):
        return len(self.get_current_folder_content()) > 0

    def reset(self):
        pass


