# Under MIT License, see LICENSE.txt

from Engine.Communication.protobuf import grSim_Packet_pb2 as grSim_Packet
from Engine.Communication.sender.sender_base_class import Sender
from Engine.Communication.sender.udp_socket import udp_socket

from Util.constant import KickForce, DribbleState

__author__ = "Maxime Gagnon-Legault"


class GrSimCommandSender(Sender):

    def connect(self, connection_info):
        return udp_socket(connection_info)

    def send_packet(self, packet):
        packet = self._create_protobuf_packet(packet)
        self.connection.send(packet.SerializeToString())

    def _create_protobuf_packet(self, packets_frame) -> grSim_Packet.grSim_Packet:
        grsim_packet = grSim_Packet.grSim_Packet()

        grsim_packet.commands.isteamyellow = packets_frame.is_team_yellow
        grsim_packet.commands.timestamp = packets_frame.timestamp if packets_frame.timestamp is not None else 0

        for packet in packets_frame.packet:
            grsim_command = grsim_packet.commands.robot_commands.add()
            grsim_command.id = packet.robot_id
            grsim_command.wheelsspeed = False
            grsim_command.veltangent = packet.command.x/1000
            grsim_command.velnormal = packet.command.y/1000
            grsim_command.velangular = packet.command.orientation
            grsim_command.spinner = packet.dribbler_state != DribbleState.FORCE_STOP
            grsim_command.kickspeedx = self.translate_kick_force(packet.kick_force)
            grsim_command.kickspeedz = 0

        active_robot_id = {packet.robot_id for packet in packets_frame.packet}
        inactive_robot_id = set(range(12)) - active_robot_id

        for robot_id in inactive_robot_id:
            grsim_command = grsim_packet.commands.robot_commands.add()
            grsim_command.id = robot_id
            grsim_command.wheelsspeed = False
            grsim_command.veltangent = 0
            grsim_command.velnormal = 0
            grsim_command.velangular = 0
            grsim_command.spinner = False
            grsim_command.kickspeedx = 0
            grsim_command.kickspeedz = 0

        return grsim_packet

    @staticmethod
    def translate_kick_force(kick_force: KickForce) -> int:
        kick_translation = {KickForce.NONE: 0,
                            KickForce.LOW: 2,
                            KickForce.MEDIUM: 3,
                            KickForce.HIGH: 5}
        return kick_translation[kick_force]

