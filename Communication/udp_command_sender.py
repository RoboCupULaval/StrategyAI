# Under MIT License, see LICENSE.txt

from .command_sender import CommandSender
from .protobuf import grSim_Packet_pb2 as grSim_Packet
from .udp_utils import udp_socket

class UDPCommandSender(CommandSender):

    def __init__(self, host, port):
        self.server = udp_socket(host, port)

    def get_new_packet(self):
        return grSim_Packet.grSim_Packet()

    def send_packet(self, packet):
        self.server.send(packet.SerializeToString())

    def send_command(self, command):
        packet = grSim_Packet.grSim_Packet()
        packet.commands.isteamyellow = command.team.is_team_yellow
        packet.commands.timestamp = 0
        grsim_command = packet.commands.robot_commands.add()
        grsim_command.id = command.player.id
        grsim_command.wheelsspeed = False
        grsim_command.veltangent = command.pose.position.x
        grsim_command.velnormal = command.pose.position.y
        grsim_command.velangular = command.pose.orientation
        grsim_command.spinner = True
        grsim_command.kickspeedx = command.kick_speed
        grsim_command.kickspeedz = 0

        self.server.send(packet.SerializeToString())
