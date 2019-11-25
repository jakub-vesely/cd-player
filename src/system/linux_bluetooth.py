import logging
import time
from subprocess import Popen, PIPE, STDOUT
from threading import Thread

from src.system.bluetooth_base import BluetoothBase
class LinuxBluettot(BluetoothBase):
    def __init__(self):
        super().__init__()
        self.connection_request = False

    def is_connected(self):
        subprocess = Popen(
            ["hcitool", "con"], bufsize=100, stdin=PIPE, stdout=PIPE, stderr=STDOUT
        )
        stdout = subprocess.communicate()[0]
        return b"\t" in stdout


    def requie_connetion(self):
        self.connection_request = True

    def _connect_thread(self):
        while True:
            if self.connection_request:
                self.connection_request = False

                subprocess = Popen(
                    ["bluetoothctl", "connect", "FC:A8:9A:1C:12:53"], bufsize=100, stdin=PIPE, stdout=PIPE, stderr=PIPE
                )
                stdout = subprocess.communicate(timeout=5)[0]
            time.sleep(1)

    def start_connection_threead(self):
        connection_thread = Thread(target=self._connect_thread, args=[])
        connection_thread.start()
