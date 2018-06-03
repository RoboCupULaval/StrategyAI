# Under MIT licence, see LICENCE.txt

import logging
import time
from queue import Queue

import numpy as np
from typing import Dict, List, Type

from Debug.debug_command_factory import DebugCommandFactory
from Engine.regulators import VelocityRegulator, PositionRegulator
from Engine.filters.path_smoother import path_smoother
from Engine.robot import Robot
from Engine.Communication.robot_state import RobotPacket, RobotState
from Util import Pose

from Util.engine_command import EngineCommand
from Util.constant import PLAYER_PER_TEAM
from Util.geometry import rotate
from Util.team_color_service import TeamColorService
from config.config import Config


class Controller:

    def __init__(self, ui_send_queue: Queue):
        logging.basicConfig(format='%(levelname)s: %(name)s: %(message)s', level=logging.DEBUG)
        self.logger = logging.getLogger("Controller")

        self.timestamp = None
        self.ui_send_queue = ui_send_queue

        self.robots = [Robot(robot_id) for robot_id in range(PLAYER_PER_TEAM)]

        for robot in self.robots:
            robot.position_regulator = PositionRegulator()
            robot.velocity_regulator = VelocityRegulator()

    def update(self, track_frame: Dict, engine_cmds: List[EngineCommand]):
        self.timestamp = track_frame['timestamp']
        our_team_color = str(TeamColorService().our_team_color)

        for robot in track_frame[our_team_color]:
            self[robot['id']].pose = robot['pose']
            self[robot['id']].velocity = robot['velocity']

        for cmd in engine_cmds:
            self[cmd.robot_id].engine_cmd = cmd
            if self[cmd.robot_id].raw_path is None:
                self[cmd.robot_id].path = None

    def execute(self) -> RobotState:
        commands = {}
        active_robots = [robot for robot in self if robot.pose is not None and robot.raw_path is not None]

        for robot in active_robots:
            robot.path, robot.target_speed = path_smoother(robot)

            if robot.position_error.norm < 200 and robot.target_speed == 0:
                cmd = robot.position_regulator.execute(robot)
                robot.velocity_regulator.reset()
            else:
                cmd = robot.velocity_regulator.execute(robot)

            self.ui_send_queue.put_nowait(DebugCommandFactory.plot_point("mm/s",
                                                                         "robot {} cmd speed".format(robot.robot_id),
                                                                         [time.time()],
                                                                         [cmd.norm]))
            self.ui_send_queue.put_nowait(DebugCommandFactory.plot_point("mm/s",
                                                                         "robot {} kallman speed".format(robot.robot_id),
                                                                         [time.time()],
                                                                         [robot.velocity.norm]))

            commands[robot.robot_id] = self._put_in_robots_referencial(robot, cmd)

        return self.generate_packet(commands)

    def generate_packet(self, commands: Dict[int, Pose]) -> RobotState:
        packet = RobotState(timestamp=self.timestamp,
                            is_team_yellow=TeamColorService().is_our_team_yellow,
                            packet=[])

        for robot_id, cmd in commands.items():
            packet.packet.append(
                RobotPacket(robot_id=robot_id,
                            command=cmd,
                            kick_type=self[robot_id].engine_cmd.kick_type,
                            kick_force=self[robot_id].engine_cmd.kick_force,
                            dribbler_state=self[robot_id].engine_cmd.dribbler_state,
                            charge_kick=self[robot_id].engine_cmd.charge_kick))
        return packet

    @staticmethod
    def _put_in_robots_referencial(robot, cmd):
        if Config()["GAME"]["on_negative_side"]:
            cmd.x *= -1
            cmd.orientation *= -1
            cmd.position = rotate(cmd.position, np.pi + robot.orientation)
        else:
            cmd.position = rotate(cmd.position, -robot.orientation)
        return cmd

    def __iter__(self) -> Robot:
        for robot in self.robots:
            yield robot

    def __getitem__(self, item: int) -> Robot:
        return self.robots[item]
