# Under MIT License, see LICENSE.txt

from ipaddress import ip_address

from socket import socket, AF_INET, SOCK_DGRAM, IPPROTO_IP, IP_ADD_MEMBERSHIP, inet_aton, INADDR_ANY, timeout, SOL_SOCKET, SO_REUSEADDR
from struct import pack

from protobuf_to_dict import protobuf_to_dict

from Engine.Communication.protobuf.referee_pb2 import SSL_Referee
from Engine.Communication.receiver.receiver_base_class import ReceiverProcess
from Engine.Communication.monitor import monitor_queue

__author__ = "Simon Bouchard"


@monitor_queue
class RefereeReceiver(ReceiverProcess):

    def connect(self, connection_info):
        connection = socket(AF_INET, SOCK_DGRAM)
        connection.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        connection.bind(connection_info)
        if ip_address(connection_info[0]).is_multicast:
            connection.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, pack('=4sl', inet_aton(connection_info[0]), INADDR_ANY))

        return connection

    def receive_packet(self):

        packet = SSL_Referee()

        data = self.connection.recv(1024)

        packet.ParseFromString(data)
        packet = protobuf_to_dict(packet)
        self._link.put(packet)
