# Under MIT licence, see LICENCE.txt

import logging
from collections import namedtuple
from typing import Dict, List

from RULEngine.regulators import VelocityRegulator, PositionRegulator
from RULEngine.filters.path_smoother import path_smoother
from RULEngine.robot import Robot

from Util.constant import PLAYER_PER_TEAM
from Util.team_color_service import TeamColorService
from Util.csv_plotter import Observer

RobotPacket = namedtuple('RobotPacket', 'robot_id command kick_type kick_force dribbler_active charge_kick')
RobotState = namedtuple('RobotState', 'timestamp is_team_yellow packet')


# TODO see if necessary, also same as RobotPacket
class EngineCommand(namedtuple('EngineCommand',
                               'robot_id cruise_speed path kick_type'
                               ' kick_force dribbler_active charge_kick target_orientation')):
    pass


class Controller(list):

    def __init__(self, observer=Observer):
        logging.basicConfig(format='%(levelname)s: %(name)s: %(message)s', level=logging.DEBUG)
        self.logger = logging.getLogger("Controller")

        self.timestamp = None
        self.observer = observer

        super().__init__(Robot(robot_id) for robot_id in range(PLAYER_PER_TEAM))

        for robot in self:
            robot.position_regulator = PositionRegulator()
            robot.velocity_regulator = VelocityRegulator()

    def update(self, track_frame: Dict, engine_cmds: List[EngineCommand]):
        self.timestamp = track_frame['timestamp']
        our_team_color = str(TeamColorService().our_team_color)

        for robot in track_frame[our_team_color]:
            self[robot['id']].pose = robot['pose']
            self[robot['id']].velocity = robot['velocity']

        for cmd in engine_cmds:
            robot_id = cmd.robot_id
            self[robot_id].engine_command = cmd

    def execute(self) -> RobotState:
        commands = dict()
        active_robots = [robot for robot in self if robot.pose is not None and robot.raw_path is not None]

        for robot in active_robots:
            robot.raw_path.quick_update_path(robot.pose.position)
            robot.path = path_smoother(robot, robot.raw_path)
            commands[robot.robot_id] = robot.velocity_regulator.execute(robot)

        return self.generate_packet(commands)

    def generate_packet(self, commands: Dict):
        packet = RobotState(timestamp=self.timestamp,
                            is_team_yellow=TeamColorService().is_our_team_yellow,
                            packet=[])

        for robot_id, cmd in commands.items():
            packet.packet.append(
                RobotPacket(robot_id=robot_id,
                            command=cmd,
                            kick_type=self[robot_id].engine_command.kick_type,
                            kick_force=self[robot_id].engine_command.kick_force,
                            dribbler_active=self[robot_id].engine_command.dribbler_active,
                            charge_kick=self[robot_id].engine_command.charge_kick))
        return packet
