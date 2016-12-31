# Under MIT license, see LICENSE.txt

from math import pi
from RULEngine.Util.constant import PLAYER_PER_TEAM
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from ai.Algorithm.Node import Node
from ai.STA.Strategy.Strategy import Strategy
from ai.STA.Tactic.ProtectGoal import GoalKeeper
from ai.STA.Tactic.RotateAround import RotateAround
from ai.STA.Tactic.PassBall import PassBall
from ai.STA.Tactic.GoToPosition import GoToPosition
from ai.STA.Tactic.GoToPositionNoPathfinder import GoToPositionNoPathfinder
from ai.STA.Tactic.Stop import Stop
from ai.STA.Tactic.tactic_constants import *

__author__ = 'RoboCupULaval'


class test_rotateAround(Strategy):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)

        #TODO: modification en temps reel de la position de la balle
        self.designated_robot = 1
        self.position_to_shoot_to = Pose(Position(1500, 1500))

        print(self.game_state.get_player_pose(1).position)

        # état 1: le robot désigné va chercher la balle
        ball_position = self.game_state.get_ball_position()
        tactic = GoToPositionNoPathfinder(self.game_state, self.designated_robot, Pose(ball_position, 0)) #TODO: ajouter pathfinder lorsque temps
        self.add_tactic(self.designated_robot, tactic)

        # état 2: une fois rendu (condition 1), le robot désigné tourne autour de la balle
        tactic = RotateAround(self.game_state, player_id=self.designated_robot, origin=ball_position, target=self.position_to_shoot_to)
        self.add_tactic(self.designated_robot, tactic)

        # condition 1: le robot désigné s'est rendu a la balle
        self.add_condition(self.designated_robot, 0, 1, self.tactic_flag_success)

        # état 3: une fois orienté, le robot frappe la balle
        tactic = PassBall(self.game_state, player_id=self.designated_robot, target=self.position_to_shoot_to)
        self.add_tactic(self.designated_robot, tactic)

        # condition 2: le robot désigné a tourné autour de la balle et est dans la bonne orientation
        self.add_condition(self.designated_robot, 1, 2, self.tactic_flag_success)

        # le reste des robots sont a l arret
        for robot_to_stop in range(0,6):
            if robot_to_stop != self.designated_robot:
                tactic = Stop(self.game_state, robot_to_stop)
                self.add_tactic(robot_to_stop, tactic)

    def tactic_flag_success(self):
        """
        Condition pour passer du noeud présent au noeud suivant.
        :return: Un booléen indiquant si la condition pour effectuer la transition est remplie.
        """
        return self.graphs[self.designated_robot].get_current_tactic().status_flag == Flags.SUCCESS
