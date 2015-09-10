#!/usr/bin/python
from .command_sender import CommandSender
import socket
from . import grSim_Packet_pb2 as grSim_Packet


class UDPCommandSender(CommandSender):

    def __init__(self, host, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.connection_info = (host, port)

    def send_command(command):
        pass
