from queue import deque
from typing import List

from Util import Position, Pose
from Util.ai_command import CmdBuilder
from Util.constant import ROBOT_RADIUS
from ai.GameDomainObjects import Player
from ai.STA.Tactic.tactic import Tactic
from ai.executors.pathfinder_module import WayPoint
from ai.states.game_state import GameState

VALID_DISTANCE = ROBOT_RADIUS * 0.5
DEFAULT_SPEED = 2
ROTATE_DISTANCE = 500


class StressTestRobotWaypoint(Tactic):
    def __init__(self, game_state: GameState, player: Player, target: Pose=Pose,
                 args: List[str]=None, cruise_speed=DEFAULT_SPEED):
        super().__init__(game_state, player, target, args)
        self.current_state = self.next_corner
        self.next_state = self.next_corner
        self.cruise_speed = cruise_speed
        self.iteration = 0
        self.x_sign = 1
        self.y_sign = 1
        self.coord_x = game_state.field.field_length/3
        self.coord_y = game_state.field.field_width/3
        self.points = [WayPoint(Position(self.coord_x, self.coord_y)),
                       WayPoint(Position(-self.coord_x, self.coord_y)),
                       WayPoint(Position(-self.coord_x, -self.coord_y)),
                       WayPoint(Position(self.coord_x, -self.coord_y))]
        self.points = deque(self.points)

    def next_corner(self):
        orientation = (self.points[0].position - self.player.position).angle

        if (self.player.position-self.points[0].position).norm < ROTATE_DISTANCE:
            self.points.rotate()
        return CmdBuilder().addMoveTo(Pose(self.points[0].position, orientation),
                                      way_points=list(self.points),
                                      cruise_speed=self.cruise_speed).build()


class StressTestRobot(StressTestRobotWaypoint):
    def next_corner(self):
        orientation = (self.points[0].position - self.player.position).angle

        if (self.player.position - self.points[0].position).norm < ROTATE_DISTANCE:
            self.points.rotate()
        return CmdBuilder().addMoveTo(Pose(self.points[0].position, orientation),
                                      cruise_speed=self.cruise_speed).build()
