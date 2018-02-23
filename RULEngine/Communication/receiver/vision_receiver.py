# Under MIT License, see LICENSE.txt

from ipaddress import ip_address

from socket import socket, AF_INET, SOCK_DGRAM, IPPROTO_IP, IP_ADD_MEMBERSHIP, inet_aton, INADDR_ANY, timeout, SOL_SOCKET, SO_REUSEADDR

from struct import pack

from google.protobuf.message import DecodeError
from protobuf_to_dict import protobuf_to_dict

from RULEngine.Communication.protobuf.messages_robocup_ssl_wrapper_pb2 import SSL_WrapperPacket
from RULEngine.Communication.receiver.receiver_base_class import ReceiverBaseClass

__author__ = "Maxime Gagnon-Legault"


class VisionReceiver(ReceiverBaseClass):
    TIME_OUT = 1

    def connect(self, connection_info):
        connection = socket(AF_INET, SOCK_DGRAM)
        connection.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        connection.bind(connection_info)
        if ip_address(connection_info[0]).is_multicast:
            connection.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, pack('=4sl', inet_aton(connection_info[0]), INADDR_ANY))
        connection.settimeout(VisionReceiver.TIME_OUT)

        return connection

    def receive_packet(self):

        packet = SSL_WrapperPacket()

        try:
            data = self.connection.recv(1024)
        except timeout:
            self.logger.debug('No Vision Frame received.')
            return

        try:
            packet.ParseFromString(data)
        except DecodeError:
            if not packet.HasField('geometry'):
                self.logger.error('VisionReceiver had trouble decoding a packet!')

        packet = protobuf_to_dict(packet)['detection']

        self._link[packet['camera_id']] = packet
