#!/usr/bin/python

import socket
import struct
from socketserver import ThreadingMixIn, UDPServer, BaseRequestHandler
import threading
from . import messages_robocup_ssl_wrapper_pb2 as ssl_wrapper

class ThreadedUDPServer(ThreadingMixIn, UDPServer): pass

def getUDPHandler(packet_list):
    class ThreadedUDPRequestHandler(BaseRequestHandler):

        def handle(self):
            data = self.request[0]
            packet = ssl_wrapper.SSL_WrapperPacket()
            packet.ParseFromString(data)
            packet_list.append(packet)

    return ThreadedUDPRequestHandler

class Vision(object):

    def __init__(self, host = "224.5.23.2", port = 10020):

        self.packet_list = []
        self.server = ThreadedUDPServer(('', port), getUDPHandler(self.packet_list))
        self.server.socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP,
                struct.pack("=4sl", socket.inet_aton(host), socket.INADDR_ANY))
        server_thread = threading.Thread(target=self.server.serve_forever)
        server_thread.daemon = True
        server_thread.start()

    def get_frames(self):
        new_list = list(self.packet_list)
        del self.packet_list[:]
        return new_list
