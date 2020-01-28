# Under MIT License, see LICENSE.txt
from typing import Union

from pyhermes import McuCommunicator

from Engine.Communication.sender.sender_base_class import Sender
from Engine.Controller.robot import MAX_LINEAR_SPEED, MAX_ANGULAR_SPEED
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
                                                 cx / 1000,
                                                 cy / 1000,
                                                 orien,
                                                 packet.charge_kick,
                                                 self.translate_kick_force(packet.kick_force),
                                                 self.translate_dribbler_speed(packet.dribbler_state))
        except AttributeError:
            raise RuntimeError("You should update your pyhermes, by reinstalling the requirement:"
                               "'pip install -r requirements.txt --upgrade'")

    @staticmethod
    def translate_kick_force(kick_force: Union[KickForce, float]) -> int:
        # command = speed / 0.1536 + 0.61 /  0.1536
        # The plage of usable value is 12 to 30, after 30 the force stay the same,  the minimum speed is 1 m/s
        if isinstance(kick_force, float):
            kick_force_translated = int(clamp(kick_force / 0.1536 + 0.61 / 0.1536, 12, 30))
        elif isinstance(kick_force, KickForce):
            kick_force_translated = {
                KickForce.NONE: 0,
                KickForce.LOW: 10,  # 1   m/s
                KickForce.MEDIUM: 18,  # 2   m/s
                KickForce.HIGH: 60  # 5.5 m/s
            }.get(kick_force)
        else:
            raise RuntimeError(f"Kick force : {kick_force} is not a KickForce or an int")
        return kick_force_translated

    @staticmethod
    def translate_dribbler_speed(dribbler_speed: DribbleState) -> int:
        dribbler_translation = {DribbleState.AUTOMATIC: 0,
                                DribbleState.FORCE_STOP: 0,
                                DribbleState.FORCE_SPIN: 3}
        return dribbler_translation[dribbler_speed]
