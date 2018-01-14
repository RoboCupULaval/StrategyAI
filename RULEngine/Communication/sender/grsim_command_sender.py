# Under MIT License, see LICENSE.txt
from typing import Dict

from RULEngine.Communication.protobuf import grSim_Packet_pb2 as grSim_Packet
from RULEngine.Communication.sender.sender_base_class import SenderBaseClass
from RULEngine.Communication.util.udp_socket import udp_socket


class GrSimCommandSender(SenderBaseClass):

    def connect(self, connection_info):
        return udp_socket(connection_info)

    def send_packet(self):
        packet = self.queue.get()
        packet = self._create_protobuf_packet(packet)
        self.connection.send(packet.SerializeToString())

    @staticmethod
    def _create_protobuf_packet(packet: Dict) -> grSim_Packet.grSim_Packet:
        grsim_packet = grSim_Packet.grSim_Packet()

        grsim_packet.commands.isteamyellow = packet['is_team_yellow']
        grsim_packet.commands.timestamp = packet['timestamp'] if packet['timestamp'] is not None else 0

        for robot_id, cmd in packet['commands'].items():
            grsim_command = grsim_packet.commands.robot_commands.add()
            grsim_command.id = robot_id
            grsim_command.wheelsspeed = False
            grsim_command.veltangent = cmd['x']/1000
            grsim_command.velnormal = cmd['y']/1000
            grsim_command.velangular = cmd['orientation']
            grsim_command.spinner = cmd['dribbler_active']
            grsim_command.kickspeedx = cmd['kick']
            grsim_command.kickspeedz = 0

        return grsim_packet
