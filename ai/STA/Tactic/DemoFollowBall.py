
# Under MIT licence, see LICENCE.txt

from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic import tactic_constants
from ai.STA.Action.MoveTo import MoveTo
from ai.STA.Action.Idle import Idle
from ai.STA.Tactic import tactic_constants
from RULEngine.Util.geometry import get_distance, get_angle
from RULEngine.Util.Pose import Pose
from RULEngine.Util.constant import POSITION_DEADZONE, BALL_RADIUS

__author__ = 'RoboCupULaval'


class DemoFollowBall(Tactic):
    # TODO : Renommer la classe pour illustrer le fait qu'elle set une Pose et non juste une Position
    """
    méthodes:
        exec(self) : Exécute une Action selon l'état courant
    attributs:
        info_manager: référence à la façade InfoManager
        player_id : Identifiant du joueur auquel est assigné la tactique
    """
    def __init__(self, game_state, player_id, p_target, time_to_live=tactic_constants.DEFAULT_TIME_TO_LIVE):
        Tactic.__init__(self, game_state, p_target, time_to_live=time_to_live)
        assert isinstance(player_id, int)

        self.current_state = self.halt
        self.next_state = self.halt
        self.player_id = player_id

    def move_to_ball(self):
        self.target = Pose(self.game_state.get_ball_position())
        move = MoveTo(self.game_state, self.player_id, self.target)

        if get_distance(self.game_state.get_player_pose(self.player_id).position, self.target.position) < POSITION_DEADZONE + BALL_RADIUS:
            self.next_state = self.halt
        else:
            self.game_state

        return move

    def halt(self, reset=False):
        stop = Idle(self.game_state, self.player_id)

        if get_distance(self.game_state.get_player_pose(self.player_id).position, self.game_state.get_ball_position()) < POSITION_DEADZONE:
            self.next_state = self.halt
        else:
            self.next_state = self.move_to_ball
        return stop
