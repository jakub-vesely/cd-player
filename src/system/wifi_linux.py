from subprocess import *
from src.system.wifi_base import WifiBase

class WifiLinux(WifiBase):
    def get_strength(self):
        shell_cmd = 'iwconfig | grep Link'
        proc = Popen(shell_cmd, shell=True, stdout=PIPE, stderr=PIPE)
        output, err = proc.communicate()
        msg = output.decode('utf-8').strip()
        msg_parts = msg.split()
        if msg_parts and msg_parts[0] == "Link" and len(msg_parts) > 1:
            quality_parts = msg_parts[1].split("=")
            if len(quality_parts) > 1 and quality_parts[0] == "Quality":
               ratio_parts = quality_parts[1].split("/")
               if len(ratio_parts) == 2:
                current = ratio_parts[0]
                max = ratio_parts[1]
                if max != 0:
                    return int(current)/int(max)

        return 0

    def get_name(self):
        raise NotImplementedError
