from src.system.real_file_system_base import RealFileSystemBase
class WinUsbFileSystem(RealFileSystemBase):
    main_folder_path = "~/Music/"
    current_folder_path = main_folder_path
    def __init__(self):
        super().__init__()

    def _get_main_folder_path(self):
        return "D:\\"

    def get_main_folder_name(self):
        return "USB"
