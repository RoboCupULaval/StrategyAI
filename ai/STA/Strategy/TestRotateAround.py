# Under MIT license, see LICENSE.txt

from math import pi
from RULEngine.Util.constant import PLAYER_PER_TEAM
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from ai.Algorithm.Node import Node
from ai.STA.Strategy.Strategy import Strategy
from ai.STA.Tactic.GoalKeeper import GoalKeeper
from ai.STA.Tactic.RotateAround import RotateAround
from ai.STA.Tactic.PassBall import PassBall
from ai.STA.Tactic.GoToPositionNoPathfinder import GoToPositionNoPathfinder
from ai.STA.Tactic.Stop import Stop
from ai.STA.Tactic.tactic_constants import *

__author__ = 'RoboCupULaval'


class TestRotateAround(Strategy):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)

        # TODO: modification en temps reel de la position de la balle
        self.designated_robot = 0
        self.position_to_shoot_to = Position(0, 0)
        self.origin = self.game_state.get_ball_position()

        tactic = RotateAround(self.game_state, self.designated_robot, self.origin, self.position_to_shoot_to)
        self.add_tactic(self.designated_robot, tactic)

        # le reste des robots sont a l'arret
        for robot_to_stop in range(0, 6):
            if robot_to_stop != self.designated_robot:
                self.add_tactic(robot_to_stop, Stop(self.game_state, robot_to_stop))

    def tactic_flag_success(self):
        """
        Condition pour passer du noeud présent au noeud suivant.
        :return: Un booléen indiquant si la condition pour effectuer la transition est remplie.
        """
        return self.graphs[self.designated_robot].get_current_tactic().status_flag == Flags.SUCCESS
