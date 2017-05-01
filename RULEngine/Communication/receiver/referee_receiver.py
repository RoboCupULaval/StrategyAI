# Under MIT License, see LICENSE.txt

from RULEngine.Communication.protobuf import referee_pb2 as ssl_referee
from RULEngine.Communication.util.protobuf_packet_receiver import ProtobufPacketReceiver
from config.config_service import ConfigService


class RefereeReceiver(ProtobufPacketReceiver):

    def __init__(self):
        cfg = ConfigService()
        host = cfg.config_dict["COMMUNICATION"]["udp_address"]
        port = int(cfg.config_dict["COMMUNICATION"]["referee_port"])
        super(RefereeReceiver, self).__init__(host, port, ssl_referee.SSL_Referee)
