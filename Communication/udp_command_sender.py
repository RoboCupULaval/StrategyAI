#Under MIT License, see LICENSE.txt
#!/usr/bin/python
from .command_sender import CommandSender
from .udp_utils import udp_socket
from .protobuf import grSim_Packet_pb2 as grSim_Packet
from .protobuf.grSim_Commands_pb2 import grSim_Robot_Command
import math


class UDPCommandSender(CommandSender):

    def __init__(self, host, port):
        self.server = udp_socket(host, port)

    def get_new_packet(self):
        return grSim_Packet.grSim_Packet()

    def send_packet(self, packet):
        self.server.send(packet.SerializeToString())

    def send_command(self, command):
        packet = grSim_Packet.grSim_Packet()
        #grSimCommand = grSim_Robot_Command()
        packet.commands.isteamyellow = command.team.is_team_yellow
        packet.commands.timestamp = 0
        grSimCommand = packet.commands.robot_commands.add()
        grSimCommand.id = command.player.id
        grSimCommand.wheelsspeed = False
        grSimCommand.veltangent = command.pose.position.x
        grSimCommand.velnormal = command.pose.position.y
        grSimCommand.velangular = command.pose.orientation
        grSimCommand.spinner = True
        grSimCommand.kickspeedx = command.kick_speed
        grSimCommand.kickspeedz = 0

        #packet.commands.robot_commands.append(grSimCommand)

        self.server.send(packet.SerializeToString())
