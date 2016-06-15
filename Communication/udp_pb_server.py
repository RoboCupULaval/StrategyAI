#Under MIT License, see LICENSE.txt
#!/usr/bin/python

from .udp_utils import MulticastThreadedUDPServer
from socketserver import BaseRequestHandler
from collections import deque

class PBPacketReceiver(object):

    def __init__(self, host, port, packet_type):
        self.packet_list = deque(maxlen=100)
        handler = self.get_udp_handler(self.packet_list, packet_type)
        self.server = MulticastThreadedUDPServer(host, port, handler)

    def get_udp_handler(self, packet_list, packet_type):
        class ThreadedUDPRequestHandler(BaseRequestHandler):

            def handle(self):
                data = self.request[0]
                packet = packet_type()
                packet.ParseFromString(data)
                packet_list.append(packet)

        return ThreadedUDPRequestHandler

    def pop_frames(self):
        new_list = list(self.packet_list)
        self.packet_list.clear()
        return new_list

    def get_latest_frame(self):
        try:
            return self.packet_list[-1]
        except IndexError:
            return None
