class FileSystemBase():
    def __init__(self):
        pass

    def get_current_folder_path(self) -> str:
        raise NotImplementedError

    def get_current_folder_content(self) -> list:
        raise NotImplementedError

    def get_main_folder_name(self) -> str:
        raise NotImplementedError

    def go_to_subfolder(self, folder_name: str) -> bool:
        raise NotImplementedError

    def go_to_upper_folder(self) -> bool:
        raise NotImplementedError

    def is_available(self) -> bool:
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError
