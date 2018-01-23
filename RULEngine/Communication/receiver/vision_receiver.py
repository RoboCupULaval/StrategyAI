# Under MIT License, see LICENSE.txt

__author__ = "Maxime Gagnon-Legault"

from ipaddress import ip_address
from queue import Full
from socket import socket, AF_INET, SOCK_DGRAM, IPPROTO_IP, IP_ADD_MEMBERSHIP, inet_aton, INADDR_ANY, timeout, SOL_SOCKET, SO_REUSEADDR
from struct import pack

from google.protobuf.message import DecodeError
from protobuf_to_dict import protobuf_to_dict

from RULEngine.Communication.protobuf.messages_robocup_ssl_wrapper_pb2 import SSL_WrapperPacket
from RULEngine.Communication.receiver.receiver_base_class import ReceiverBaseClass


class VisionReceiver(ReceiverBaseClass):
    TIME_OUT = 1

    def connect(self, connection_info):
        connection = socket(AF_INET, SOCK_DGRAM)
        connection.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        connection.bind(connection_info)
        if ip_address(connection_info[0]).is_multicast:
            connection.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, pack('=4sl', inet_aton(connection_info[0]), INADDR_ANY))
        connection.settimeout(self.TIME_OUT)

        return connection

    def receive_packet(self):

        packet = SSL_WrapperPacket()
        try:
            data = self.connection.recv(1024)
        except timeout:
            self.logger.error('Vision queue timeout. No frame received.')
            return

        try:
            packet.ParseFromString(data)
        except DecodeError:
            self.logger.error('VisionReceiver had trouble decoding a packet!')
            return
        try:
            self.queue.put(protobuf_to_dict(packet), block=False)
        except Full as e:
            self.logger.debug("Vision queue full. Frames will be lost.")
        except DecodeError:
            self.logger.error("Vision receiver had trouble decoding a packet! Are you listening "
                              "to the correct port")
