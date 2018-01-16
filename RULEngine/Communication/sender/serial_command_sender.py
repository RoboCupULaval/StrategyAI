# Under MIT License, see LICENSE.txt

from pyhermes import McuCommunicator

from RULEngine.Communication.sender.sender_base_class import SenderBaseClass


class SerialCommandSender(SenderBaseClass):

    def connect(self, connection_info):
        return McuCommunicator(timeout=0.1)

    def send_packet(self):
        packet = self.queue.get()
        for robot_state in packet:
            self.connection.sendSpeed(robot_state.robot_id,
                                      robot_state.command.x/1000,
                                      robot_state.command.y/1000,
                                      robot_state.command.orientation)

