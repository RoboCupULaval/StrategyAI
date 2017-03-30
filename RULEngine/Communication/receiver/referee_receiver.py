# Under MIT License, see LICENSE.txt

from RULEngine.Communication.protobuf import referee_pb2 as ssl_referee
from RULEngine.Communication.util.protobuf_packet_receiver import ProtobufPacketReceiver


class RefereeReceiver(ProtobufPacketReceiver):

    def __init__(self, host="224.5.23.1", port=10003):
        super(RefereeReceiver, self).__init__(host, port, ssl_referee.SSL_Referee)
