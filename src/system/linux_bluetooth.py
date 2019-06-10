import logging
from subprocess import Popen, PIPE, STDOUT

from src.system.bluetooth_base import BluetoothBase
class LinuxBluettot(BluetoothBase):
    def is_connected(self):
        subprocess = Popen(
            ["hcitool", "con"], bufsize=100, stdin=PIPE, stdout=PIPE, stderr=STDOUT
        )
        stdout = subprocess.communicate()[0]
        return b"\t" in stdout

