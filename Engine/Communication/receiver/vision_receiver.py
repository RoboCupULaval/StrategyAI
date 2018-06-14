# Under MIT License, see LICENSE.txt

from ipaddress import ip_address


from socket import AF_INET, SOCK_DGRAM, IPPROTO_IP, IP_ADD_MEMBERSHIP, INADDR_ANY, SOL_SOCKET, SO_REUSEADDR
from socket import inet_aton, socket, timeout
from struct import pack

from multiprocessing.managers import DictProxy

import time
from google.protobuf.message import DecodeError
from protobuf_to_dict import protobuf_to_dict

from Engine.Communication.protobuf.messages_robocup_ssl_wrapper_pb2 import SSL_WrapperPacket
from Engine.Communication.receiver.receiver_base_class import ReceiverProcess

__author__ = 'Simon Bouchard'


class VisionReceiver(ReceiverProcess):
    TIME_OUT = 1.0
    TIME_OFFSET = None
    MAX_TIME_OFFSET_DIFFERENCE = 1.0

    def __init__(self, connection_info, link: DictProxy, field: DictProxy):
        self.field = field
        super().__init__(connection_info, link)

    def connect(self, connection_info):
        connection = socket(AF_INET, SOCK_DGRAM)
        connection.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        connection.bind(connection_info)
        if ip_address(connection_info[0]).is_multicast:
            connection.setsockopt(IPPROTO_IP,
                                  IP_ADD_MEMBERSHIP,
                                  pack('=4sl', inet_aton(connection_info[0]), INADDR_ANY))
        connection.settimeout(VisionReceiver.TIME_OUT)

        return connection

    def run(self):
        self.catch_geometry_packet()
        super().run()

    def catch_geometry_packet(self):
        self.logger.debug('Waiting for geometry packet...')
        geometry_packet = None
        while geometry_packet is None:
            wrapper_packet = SSL_WrapperPacket()
            try:
                data = self.connection.recv(2048)
            except timeout:
                self.logger.debug('No Vision Frame received.')
                continue
            wrapper_packet.ParseFromString(data)
            wrapper_packet = protobuf_to_dict(wrapper_packet)
            geometry_packet = wrapper_packet.get('geometry', None)
        self.logger.debug('Geometry packet received.')
        self.field.update(geometry_packet)

    def receive_packet(self):

        wrapper_packet = SSL_WrapperPacket()

        try:
            data = self.connection.recv(2048)
        except timeout:
            self.logger.debug('No Vision Frame received.')
            return

        try:
            wrapper_packet.ParseFromString(data)
        except DecodeError:
            self.logger.error('VisionReceiver had trouble decoding a packet!')

        wrapper_packet = protobuf_to_dict(wrapper_packet)

        detection_packet = wrapper_packet.get('detection', None)

        if detection_packet:

            current_time_offset = time.time() - detection_packet['t_capture']

            if VisionReceiver.TIME_OFFSET is None:
                self.logger.debug('Offset time between system is {:.0f} sec.'.format(current_time_offset))
                VisionReceiver.TIME_OFFSET = current_time_offset

            if abs(VisionReceiver.TIME_OFFSET - current_time_offset) > VisionReceiver.MAX_TIME_OFFSET_DIFFERENCE:
                self.logger.debug('Offset time between system was reset to {:.0f} sec (was {:.0f} sec)'.format(current_time_offset,
                                                                                                            VisionReceiver.TIME_OFFSET))
                self.logger.warning('You might be receiving vision frame from more then one source.')
                VisionReceiver.TIME_OFFSET = current_time_offset

            detection_packet['t_capture'] = VisionReceiver.TIME_OFFSET + detection_packet['t_capture']
            self._link[detection_packet['camera_id']] = detection_packet

