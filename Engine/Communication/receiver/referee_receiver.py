# Under MIT License, see LICENSE.txt

from ipaddress import ip_address
from multiprocessing.managers import DictProxy
from multiprocessing.queues import Queue

from socket import socket, AF_INET, SOCK_DGRAM, IPPROTO_IP, IP_ADD_MEMBERSHIP, inet_aton, INADDR_ANY, SOL_SOCKET, SO_REUSEADDR
from struct import pack
from typing import Tuple, Union

from protobuf_to_dict import protobuf_to_dict

from Engine.Communication.protobuf.referee_pb2 import Referee
from Engine.Communication.receiver.receiver_base_class import ReceiverProcess
from Engine.Communication.monitor import monitor_queue
from Engine.Communication.sender.referee_team_sender import RefereeTeamSender
from ai.GameDomainObjects import RefereeState

__author__ = "Simon Bouchard"


@monitor_queue
class RefereeReceiver(ReceiverProcess):

    def connect(self, connection_info):
        connection = socket(AF_INET, SOCK_DGRAM)
        connection.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        # For some reason with Ubuntu on Windows (WSL) you need to first bind to 0.0.0.0, before changing the address
        connection.bind(('0.0.0.0', connection_info[1]))

        if ip_address(connection_info[0]).is_multicast:
            connection.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, pack('=4sl', inet_aton(connection_info[0]), INADDR_ANY))

        return connection

    def receive_packet(self):

        packet = Referee()

        data, ip_addr = self.connection.recvfrom(1024)

        packet.ParseFromString(data)
        packet = protobuf_to_dict(packet)
        packet['ip_addr'] = ip_addr[0]

        ref_state = RefereeState(packet)

        self._link.put(ref_state)

