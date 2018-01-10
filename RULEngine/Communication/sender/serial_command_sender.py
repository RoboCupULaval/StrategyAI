# Under MIT License, see LICENSE.txt

from pyhermes import McuCommunicator

from RULEngine.Communication.sender.sender_base_class import SenderBaseClass


class SerialCommandSender(SenderBaseClass):

    def __init__(self):
        super(SerialCommandSender, self).__init__()

        self.mcu_com = McuCommunicator(timeout=0.1)

    def send_packet(self, commands):
        pass

    def run(self):
        pass

    def start(self):
        pass

    def terminate(self):
        pass

