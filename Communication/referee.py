#Under MIT License, see LICENSE.txt
#!/usr/bin/python

from .udp_server import PBPacketReceiver
from .protobuf import referee_pb2 as ssl_referee


class RefereeServer(PBPacketReceiver):

    def __init__(self, host="224.5.23.1", port=10003):
        super(RefereeServer, self).__init__(host, port, ssl_referee.SSL_Referee)
