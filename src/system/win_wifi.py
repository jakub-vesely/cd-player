from src.system.wifi_base import WifiBase

class WinWifi(WifiBase):
    def get_strength(self):
        return 0.5 #Faked

    def get_name(self):
        raise NotImplementedError
