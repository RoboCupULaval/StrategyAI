# Under MIT licence, see LICENCE.txt
from typing import List

from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.geometry import get_distance
from RULEngine.Util.Pose import Pose
from RULEngine.Util.constant import POSITION_DEADZONE, ROBOT_RADIUS
from ai.Algorithm.evaluation_module import is_ball_our_side
from ai.STA.Action.PathfindToPosition import PathfindToPosition
from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Action.Idle import Idle
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState

__author__ = 'RoboCupULaval'

FOLLOW_SPEED = 1.5


class DemoFollowBall(Tactic):
    """
    méthodes:
        exec(self) : Exécute une Action selon l'état courant
    attributs:
        game_state: état courant du jeu
        player : Instance du joueur auquel est assigné la tactique
    """
    def __init__(self, game_state: GameState, player: OurPlayer, p_target: Pose=Pose(), args: List[str]=None):
        Tactic.__init__(self, game_state, player, p_target, args)
        self.current_state = self.halt
        self.next_state = self.halt

    def move_to_ball(self):
        self.status_flag = Flags.WIP
        self.target = Pose(self.game_state.get_ball_position())

        if get_distance(self.player.pose.position, self.target.position) < POSITION_DEADZONE + ROBOT_RADIUS:
            self.next_state = self.halt
        else:
            self.next_state = self.move_to_ball
        return PathfindToPosition(self.game_state, self.player, self.target)

    def halt(self):
        self.status_flag = Flags.SUCCESS

        if get_distance(self.player.pose.position, self.game_state.get_ball_position()) < \
           POSITION_DEADZONE + ROBOT_RADIUS:
            self.next_state = self.halt
        else:
            self.next_state = self.move_to_ball
        return Idle(self.game_state, self.player)
