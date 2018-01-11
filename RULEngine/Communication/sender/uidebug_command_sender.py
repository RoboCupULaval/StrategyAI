# Under MIT License, see LICENSE.txt

__author__ = "Maxime Gagnon-Legault"

import pickle
from math import cos, sin

from RULEngine.Communication.sender.sender_base_class import SenderBaseClass
from RULEngine.Communication.util.udp_socket import udp_socket


class DebugCommand(dict):

    def __init__(self, p_type, p_data, p_link=None, p_version="1.0"):
        super().__init__()
        self['name'] = 'Engine'
        self['version'] = p_version
        self['type'] = p_type
        self['link'] = p_link
        self['data'] = p_data


class UIDebugCommandSender(SenderBaseClass):

    def connect(self, connection_info):
        return udp_socket(connection_info)

    def send_packet(self):

        try:
            track_frame = self.queue.get()

            for robot in track_frame['blue']:
                self.send_robot_position(robot['pose'], color=(255, 0, 0), radius=10, color_angle=(255, 0, 0))

            for robot in track_frame['yellow']:
                self.send_robot_position(robot['pose'], color=(255, 0, 0), radius=10, color_angle=(255, 0, 0))

            for ball in track_frame['balls']:
                self.send_balls_position(ball['pose'], color=(255, 0, 0))
        except ConnectionRefusedError as e:
            print(e)

    def send_robot_position(self, pos, color=(0, 255, 0), color_angle=(0, 0, 0), radius=90):
        player_center = (pos[0], pos[1])
        data_circle = {'center': player_center,
                       'radius': radius,
                       'color': color,
                       'is_fill': True,
                       'timeout': 0.08}

        end_point = (pos[0] + radius * cos(pos[2]),
                     pos[1] + radius * sin(pos[2]))
        data_line = {'start': player_center,
                     'end': end_point,
                     'color': color_angle,
                     'timeout': 0.08}

        self.connection.send(pickle.dumps(DebugCommand(3003, data_circle)))
        self.connection.send(pickle.dumps(DebugCommand(3001, data_line)))

    def send_balls_position(self, pose, color=(255, 127, 80)):
        data_circle = {'center': (pose[0], pose[1]),
                       'radius': 150,
                       'color': color,
                       'is_fill': True,
                       'timeout': 0.06}

        self.connection.send(pickle.dumps(DebugCommand(3003, data_circle)))

