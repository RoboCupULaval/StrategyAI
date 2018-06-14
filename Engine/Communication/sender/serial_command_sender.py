# Under MIT License, see LICENSE.txt

from pyhermes import McuCommunicator

from Engine.Communication.sender.sender_base_class import Sender
from Util.constant import KickForce, DribbleState


class SerialCommandSender(Sender):

    def connect(self, connection_info):
        return McuCommunicator(timeout=0.1)

    def send_packet(self, packets_frame):
        try:
            for packet in packets_frame.packet:
                self.connection.sendSpeedAdvance(packet.robot_id,
                                                 packet.command.x/1000,
                                                 packet.command.y/1000,
                                                 packet.command.orientation,
                                                 packet.charge_kick,
                                                 self.translate_kick_force(packet.kick_force),
                                                 self.translate_dribbler_speed(packet.dribbler_state))
        except AttributeError:
            raise RuntimeError("You should update your pyhermes, by reinstalling the requirement:"
                               "'pip install -r requirements.txt --upgrade'")
    @staticmethod
    def translate_kick_force(kick_force: KickForce) -> int:
        kick_translation = {KickForce.NONE: 0,
                            KickForce.LOW: 10,
                            KickForce.MEDIUM: 40,
                            KickForce.HIGH: 60}
        return kick_translation[kick_force]

    @staticmethod
    def translate_dribbler_speed(dribbler_speed: DribbleState) -> int:
        dribbler_translation = {DribbleState.AUTOMATIC: 0,
                                DribbleState.FORCE_STOP: 0,
                                DribbleState.FORCE_SPIN: 3}
        return dribbler_translation[dribbler_speed]