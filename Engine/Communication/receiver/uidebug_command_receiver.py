# Under MIT License, see LICENSE.txt

from ipaddress import ip_address
from pickle import loads
from queue import Full
# noinspection PyUnresolvedReferences
from socket import socket, AF_INET, SOCK_DGRAM, IPPROTO_IP, IP_ADD_MEMBERSHIP, inet_aton, INADDR_ANY
from struct import pack

from Engine.Communication.receiver.receiver_base_class import ReceiverProcess
from Engine.Communication.monitor import monitor_queue


@monitor_queue
class UIDebugCommandReceiver(ReceiverProcess):

    def connect(self, connection_info):
        connection = socket(AF_INET, SOCK_DGRAM)
        connection.bind(connection_info)
        if ip_address(connection_info[0]).is_multicast:
            connection.setsockopt(IPPROTO_IP,
                                  IP_ADD_MEMBERSHIP,
                                  pack("=4sl", inet_aton(connection_info[0]), INADDR_ANY))

        return connection

    def receive_packet(self):

        data, _ = self.connection.recvfrom(2048)

        try:
            self._link.put(loads(data))
        except Full as e:
            self.logger.debug("{}".format(e))

