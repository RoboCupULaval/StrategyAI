# Under MIT License, see LICENSE.txt
from typing import Dict

from RULEngine.Communication.protobuf import grSim_Packet_pb2 as grSim_Packet
from RULEngine.Communication.sender.sender_base_class import SenderBaseClass
from RULEngine.Communication.util.udp_socket import udp_socket


class GrSimCommandSender(SenderBaseClass):

    def connect(self, connection_info):
        return udp_socket(connection_info)

    def send_packet(self):
        try:
            packet = self._create_protobuf_packet(self.queue.get(block=False))
            self.connection.send(packet.SerializeToString())
        finally:
            self.connection.close()

    @staticmethod
    def _create_protobuf_packet(command: Dict) -> grSim_Packet.grSim_Packet:
        packet = grSim_Packet.grSim_Packet()
        packet.commands.isteamyellow = command["is_team_yellow"]
        packet.commands.timestamp = 0
        grsim_command = packet.commands.robot_commands.add()
        grsim_command.id = command["id"]
        grsim_command.wheelsspeed = False
        grsim_command.veltangent = command["x"]
        grsim_command.velnormal = command["y"]
        grsim_command.velangular = command["orientation"]
        grsim_command.spinner = True
        grsim_command.kickspeedx = command["kick"]
        grsim_command.kickspeedz = 0

        return packet
