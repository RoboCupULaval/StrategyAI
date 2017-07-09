# Under MIT licence, see LICENCE.txt

import math as m

from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position

from ai.STA.Action.Action import Action
from ai.states.game_state import GameState
from ai.STA.Action.rotate_around import RotateAround

from typing import Union

__author__ = 'Robocup ULaval'


class ProtectGoal(Action):
    """
    Action ProtectGoal: Action de base pour le gardien de but. Déplace le gardien entre la balle et le centre du but, à
    une certaine distance de celui-ci, tout en restant dans la zone du gardien.
    """
    def __init__(self, game_state: GameState, player: OurPlayer, distance_from_goal: Union[int, float]=None):
        """
        :param game_state: Current state of the game
        :param player: Instance of the player
        """
        Action.__init__(self, game_state, player)
        self.radius = distance_from_goal if distance_from_goal is not None \
            else 0.9 * self.game_state.const["FIELD_GOAL_RADIUS"]

    def exec(self):

        ball_position = self.game_state.get_ball_position()
        goal_x = self.game_state.const["FIELD_OUR_GOAL_X_EXTERNAL"]
        pivot = Position(goal_x, 0)

        orientation = (pivot - self.player.pose.position).angle()
        return RotateAround(self.game_state,
                            self.player,
                            Pose(pivot, orientation),
                            self.radius,
                            pathfinder_on=True,
                            aiming=ball_position,
                            rotation_speed=10*m.pi,
                            aim_in_back=False).exec()

