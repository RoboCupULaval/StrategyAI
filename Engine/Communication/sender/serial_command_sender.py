# Under MIT License, see LICENSE.txt

from pyhermes import McuCommunicator

from Engine.Communication.sender.sender_base_class import Sender
from Engine.robot import MAX_LINEAR_SPEED, MAX_ANGULAR_SPEED
from Util.constant import KickForce, DribbleState
from Util.geometry import clamp
import numpy as np


class SerialCommandSender(Sender):

    def connect(self, connection_info):
        return McuCommunicator(timeout=0.1)

    def send_packet(self, packets_frame):
        try:
            for packet in packets_frame.packet:
                if np.isnan(packet.command.x) or \
                    np.isnan(packet.command.y) or \
                    np.isnan(packet.command.orientation):
                    continue
                cx = clamp(packet.command.x, -MAX_LINEAR_SPEED, MAX_LINEAR_SPEED)
                cy = clamp(packet.command.y, -MAX_LINEAR_SPEED, MAX_LINEAR_SPEED)
                orien = clamp(packet.command.orientation, -MAX_ANGULAR_SPEED, MAX_ANGULAR_SPEED)
                self.connection.sendSpeedAdvance(packet.robot_id,
                                                 cx/1000,
                                                 cy/1000,
                                                 orien,
                                                 packet.charge_kick,
                                                 self.translate_kick_force(packet.kick_force),
                                                 self.translate_dribbler_speed(packet.dribbler_state))
        except AttributeError:
            raise RuntimeError("You should update your pyhermes, by reinstalling the requirement:"
                               "'pip install -r requirements.txt --upgrade'")
    @staticmethod
    def translate_kick_force(kick_force: KickForce) -> int:
        kick_translation = {KickForce.NONE: 0,
                            KickForce.LOW: 10,     # 1   m/s
                            KickForce.MEDIUM: 18,  # 2   m/s
                            KickForce.HIGH: 60}    # 5.5 m/s
        return kick_translation[kick_force]

    @staticmethod
    def translate_dribbler_speed(dribbler_speed: DribbleState) -> int:
        dribbler_translation = {DribbleState.AUTOMATIC: 0,
                                DribbleState.FORCE_STOP: 0,
                                DribbleState.FORCE_SPIN: 3}
        return dribbler_translation[dribbler_speed]