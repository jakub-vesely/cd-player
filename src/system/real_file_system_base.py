from src.system.file_system_base import FileSystemBase
import os

class RealFileSystemBase(FileSystemBase):
    def __init__(self):
        super().__init__()
        self.reset()

    def _get_main_folder_path(self) -> str:
        raise NotImplementedError

    def get_main_folder_name(self) -> str:
        raise NotImplementedError

    def _sort_folder_content(self, item):
        if item.endswith("/"): #folder
            return " " + item #I want to have folders first
        return item

    def get_current_folder_path(self):
        return self.current_folder_path

    def get_current_folder_content(self):
        content =  os.listdir(self.current_folder_path)
        out = list()
        for item in content:
            if os.path.isdir(self.current_folder_path + "/" + item):
                out.append(item + "/")
            else:
                item_parts = item.split(".")
                postfix = item_parts[1] if len(item_parts) > 1 else ""
                if postfix in ("mp3", "ogg"):
                    out.append(item)
        return sorted(out, key=self._sort_folder_content)


    def go_to_subfolder(self, folder_name):
        if not os.path.isdir(self.current_folder_path + "/" + folder_name):
            return False
        self.current_folder_path = self.current_folder_path + "/" + folder_name
        return True

    def go_to_upper_folder(self):
        if self.current_folder_path == self._get_main_folder_path():
            return False

        self.current_folder_path = os.path.dirname(self.current_folder_path)
        return True

    def is_available(self):
        return os.path.isdir(self._get_main_folder_path())


    def reset(self):
        self.current_folder_path = self._get_main_folder_path()
