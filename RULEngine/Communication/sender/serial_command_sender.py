# Under MIT License, see LICENSE.txt

from pyhermes import McuCommunicator

from RULEngine.Communication.sender.sender_base_class import SenderBaseClass
from RULEngine.Communication.monitor import monitor_queue

@monitor_queue
class SerialCommandSender(SenderBaseClass):

    def connect(self, connection_info):
        return McuCommunicator(timeout=0.1)

    def send_packet(self):
        packets_frame = self._link.get()
        for packet in packets_frame.packet:

            # FIXME PB:  Currently we are sending as much packet as the ctrl loop is generating.
            # It would be preferable if the speed commands were send at a fix rate
            # The following hack make it impossible to immediately break,
            # instead the robot will stop receiving commands and thus break 0.5s later...

            self.connection.sendSpeed(packet.robot_id,
                                      packet.command['x']/1000,
                                      packet.command['y']/1000,
                                      packet.command['orientation'])
            # FIXME PB: Because of the issue #18 of the Communication Tower, every 3 packets mights be lost
            # We should it fix this in the ComTower or check it here
            if packet.kick_force > 0:
                self.connection.kick(packet.robot_id, packet.kick_force)

            if packet.dribbler_active:
                self.connection.turnOnDribbler(packet.robot_id)

            if packet.charge_kick:
                self.connection.charge(packet.robot_id)

