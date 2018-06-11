# Under MIT License, see LICENSE.txt

from ipaddress import ip_address

from socket import socket, AF_INET, SOCK_DGRAM, IPPROTO_IP, IP_ADD_MEMBERSHIP, inet_aton, INADDR_ANY, SOL_SOCKET, SO_REUSEADDR
from struct import pack

from protobuf_to_dict import protobuf_to_dict

from Engine.Communication.protobuf.referee_pb2 import SSL_Referee
from Engine.Communication.receiver.receiver_base_class import ReceiverProcess
from Engine.Communication.monitor import monitor_queue
from ai.GameDomainObjects import RefereeState
from ai.GameDomainObjects.referee_state import Stage

__author__ = "Simon Bouchard"


@monitor_queue
class RefereeReceiver(ReceiverProcess):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_packet = None

    def connect(self, connection_info):
        connection = socket(AF_INET, SOCK_DGRAM)
        connection.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        connection.bind(connection_info)
        if ip_address(connection_info[0]).is_multicast:
            connection.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, pack('=4sl', inet_aton(connection_info[0]), INADDR_ANY))

        return connection

    def receive_packet(self):

        packet = SSL_Referee()

        data = self.connection.recv(1024)

        packet.ParseFromString(data)
        packet = protobuf_to_dict(packet)

        ref_state = RefereeState(packet)

        self.log_packet(packet)
        self._link.put(ref_state)

    def log_packet(self, packet: SSL_Referee):

        if self.last_packet:
            last_team_names = (self.last_packet['blue']['name'], self.last_packet['yellow']['name'])
            last_stage = self.last_packet['stage']
            last_blue_team_info = self.last_packet['blue']
            last_yellow_team_info = self.last_packet['yellow']
        else:
            last_team_names = None
            last_stage = None
            last_blue_team_info = {'score': 0, 'red_cards': 0, 'yellow_cards': 0, 'timeouts': 4}
            last_yellow_team_info = {'score': 0, 'red_cards': 0, 'yellow_cards': 0, 'timeouts': 4}


        self.last_packet = packet

        new_team_names = (packet['blue']['name'], packet['yellow']['name'])
        new_blue_team_info = packet['blue']
        new_yellow_team_info = packet['yellow']
        new_stage = packet['stage']

        is_name_change = last_team_names != new_team_names
        is_state_change = last_stage != new_stage

        if last_blue_team_info['score'] != new_blue_team_info['score']:
            scoring_team = new_blue_team_info['name']
        elif last_yellow_team_info['score'] != new_yellow_team_info['score']:
            scoring_team = new_yellow_team_info['name']
        else:
            scoring_team = None

        if last_blue_team_info['red_cards'] != new_blue_team_info['red_cards']:
            red_card_team = new_blue_team_info['name']
        elif last_yellow_team_info['red_cards'] != new_yellow_team_info['red_cards']:
            red_card_team = new_yellow_team_info['name']
        else:
            red_card_team = None

        if last_blue_team_info['yellow_cards'] != new_blue_team_info['yellow_cards']:
            yellow_card_team = new_blue_team_info['name']
        elif last_yellow_team_info['yellow_cards'] != new_yellow_team_info['yellow_cards']:
            yellow_card_team = new_yellow_team_info['name']
        else:
            yellow_card_team = None

        if last_blue_team_info['timeouts'] != new_blue_team_info['timeouts']:
            timeout_team = new_blue_team_info['name']
            timeout_time = new_blue_team_info['timeout_time']
            timeout_left = new_blue_team_info['timeouts']
        elif last_yellow_team_info['timeouts'] != new_yellow_team_info['timeouts']:
            timeout_team = new_yellow_team_info['name']
            timeout_time = new_blue_team_info['timeout_time']
            timeout_left = new_blue_team_info['timeouts']
        else:
            timeout_team = None
            timeout_time = None
            timeout_left = None

        if is_name_change:
            self.logger.info('Team change detected.\n\n' + '-' * 40 + '\n' +
                             '  {} (BLUE) vs. {} (YELLOW)'.format(*new_team_names) + '\n' + '-' * 40 + '\n\n')

        if is_state_change:
            self.logger.info('Stage change detected. Now at {}.'.format(Stage(new_stage).name))

        if scoring_team is not None:
            self.logger.info('A goal was score by {}. ({}: {} - {}: {})'.format(scoring_team,
                                                                                new_blue_team_info['name'],
                                                                                new_blue_team_info['score'],
                                                                                new_yellow_team_info['name'],
                                                                                new_yellow_team_info['score']))

        if red_card_team is not None:
            self.logger.info('A red card was taken by {}.'.format(red_card_team))

        if yellow_card_team is not None:
            self.logger.info('A yellow card was taken by {}.'.format(yellow_card_team))

        if timeout_team is not None:
            self.logger.info('A timeout was ask by {}. Timeout left: {}. Time left: {:.1f} seconds'.format(timeout_team,
                                                                                                       timeout_left,
                                                                                                       timeout_time/1000000))
