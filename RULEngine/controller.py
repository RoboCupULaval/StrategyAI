# Under MIT licence, see LICENCE.txt

import logging
from collections import namedtuple
from multiprocessing import Queue
from queue import Empty
from typing import Dict, List

from RULEngine.controllers import VelocityController, PositionController
from RULEngine.filters.path_smoother import path_smoother
from RULEngine.robot import Robot
from Util.constant import PLAYER_PER_TEAM
from config.config_service import ConfigService

RobotPacket = namedtuple('RobotPacket', 'robot_id command kick_type kick_force dribbler_active charge_kick')
RobotState = namedtuple('RobotState', 'timestamp is_team_yellow packet')


# TODO see if necessary, also same as RobotPacket
class EngineCommand(namedtuple('EngineCommand',
                               'robot_id cruise_speed path kick_type'
                               ' kick_force dribbler_active charge_kick target_orientation')):
    pass


class Observer:
    def __init__(self):
        pass

    def write(self, poses):
        pass


class Controller(list):
    def __init__(self, observer=Observer):
        self.timestamp = None
        self.observer = observer

        logging.basicConfig(format='%(levelname)s: %(name)s: %(message)s', level=logging.DEBUG)
        self.logger = logging.getLogger("Controller")

        self.cfg = ConfigService()
        self.team_color = self.cfg.config_dict['GAME']['our_color']

        super().__init__(Robot(robot_id) for robot_id in range(PLAYER_PER_TEAM))

        for robot in self:
            robot.position_controller = PositionController()
            robot.velocity_controller = VelocityController()

    def execute(self, track_frame: Dict, engine_cmds: EngineCommand) -> RobotState:

        self.timestamp = track_frame['timestamp']
        self.update_robots_states(track_frame[self.team_color], engine_cmds)
        self.update_robot_path()

        commands = self.execute_controller()

        packet = self.generate_packet(commands)

        return packet

    def update_robots_states(self, robots_states: Dict, engine_cmds: List[EngineCommand]):
        for robot in robots_states:
            self[robot['id']].pose = robot['pose']
            self[robot['id']].velocity = robot['velocity']

        for cmd in engine_cmds:
            robot_id = cmd.robot_id
            # TODO: engine command could be a field of Robot
            self[robot_id].kick_type = cmd.kick_type
            self[robot_id].kick_force = cmd.kick_force
            self[robot_id].dribbler_active = cmd.dribbler_active
            self[robot_id].raw_path = cmd.path
            self[robot_id].cruise_speed = cmd.cruise_speed
            self[robot_id].target_orientation = cmd.target_orientation

    def update_robot_path(self):
        for robot in self:
            if robot.raw_path is not None and robot.pose is not None:
                robot.raw_path = robot.raw_path.quick_update_path(robot.pose.position)
                robot.path = path_smoother(robot, robot.raw_path)

    def execute_controller(self):
        commands = dict()
        for robot in self:
            if robot.pose is not None and robot.path is not None:  # active robots
                commands[robot.robot_id] = robot.velocity_controller.execute(robot)

        return commands

    def generate_packet(self, commands):
        packet = RobotState(timestamp=self.timestamp,
                            is_team_yellow=True if self.team_color == 'yellow' else False,
                            packet=[])

        for robot_id, cmd in commands.items():
            robot = self[robot_id]
            packet.packet.append(
                RobotPacket(robot_id=robot_id,
                            command=cmd,
                            kick_type=robot.kick_type,
                            kick_force=robot.kick_force,
                            dribbler_active=robot.dribbler_active,
                            charge_kick=robot.charge_kick))
        return packet
