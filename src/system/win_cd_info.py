from src.system.cd_info_base import CdInfoBase

class WinCdInfo(CdInfoBase):
    def __init__(self):
        super().__init__()

    def get_current_folder_content(self):
        return ["Track1", "Track2"]
