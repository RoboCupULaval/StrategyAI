# Under MIT License, see LICENSE.txt

from socketserver import ThreadingMixIn, UDPServer
import threading
import socket
import struct
from ipaddress import ip_address


class ThreadedUDPServer(ThreadingMixIn, UDPServer):

    allow_reuse_address = True

    def __init__(self, host, port, handler):
        super(ThreadedUDPServer, self).__init__(('', port), handler)
        if ip_address(host).is_multicast:
            self.register_multicast_membership(host)
        self._start()

    def register_multicast_membership(self, host):
        self.socket.setsockopt(socket.IPPROTO_IP,
                               socket.IP_ADD_MEMBERSHIP,
                               struct.pack("=4sl",
                                           socket.inet_aton(host),
                                           socket.INADDR_ANY))

    def _start(self):
        server_thread = threading.Thread(target=self.serve_forever)
        server_thread.daemon = True
        server_thread.start()
