# Under MIT License, see LICENSE.txt

from RULEngine.Communication.protobuf import grSim_Packet_pb2 as grSim_Packet
from RULEngine.Communication.sender.sender_base_class import Sender
from RULEngine.Communication.sender.udp_socket import udp_socket

__author__ = "Maxime Gagnon-Legault"


class GrSimCommandSender(Sender):

    def connect(self, connection_info):
        return udp_socket(connection_info)

    def send_packet(self, packet):
        packet = self._create_protobuf_packet(packet)
        self.connection.send(packet.SerializeToString())

    @staticmethod
    def _create_protobuf_packet(packets_frame) -> grSim_Packet.grSim_Packet:
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
            grsim_command.spinner = packet.dribbler_active
            grsim_command.kickspeedx = packet.kick_force
            grsim_command.kickspeedz = 0

        return grsim_packet
