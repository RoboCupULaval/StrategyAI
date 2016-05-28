#Under MIT License, see LICENSE.txt
#!/usr/bin/python

from socketserver import ThreadingMixIn, UDPServer, BaseRequestHandler
import threading
import socket
import struct
from collections import deque


def getUDPHandler(packet_list, packet_type):
    class ThreadedUDPRequestHandler(BaseRequestHandler):

        def handle(self):
            data = self.request[0]
            packet = packet_type()
            packet.ParseFromString(data)
            packet_list.append(packet)

    return ThreadedUDPRequestHandler


class ThreadedUDPServer(ThreadingMixIn, UDPServer):

    allow_reuse_address = True

    def __init__(self, host, port, packet_type, packet_list):
        handler = getUDPHandler(packet_list, packet_type)
        super(ThreadedUDPServer, self).__init__(('', port), handler)
        self.socket.setsockopt(socket.IPPROTO_IP,
                               socket.IP_ADD_MEMBERSHIP,
                               struct.pack("=4sl",
                                           socket.inet_aton(host),
                                           socket.INADDR_ANY))
        server_thread = threading.Thread(target=self.serve_forever)
        server_thread.daemon = True
        server_thread.start()


class PBPacketReceiver(object):

    def __init__(self, host, port, packet_type):
        self.packet_list = deque(maxlen=100)
        self.server = ThreadedUDPServer(host, port,
                                        packet_type,
                                        self.packet_list)

    def pop_frames(self):
        new_list = list(self.packet_list)
        self.packet_list.clear()
        return new_list

    def get_latest_frame(self):
        try:
            return self.packet_list[-1]
        except IndexError:
            return None
