# Under MIT licence, see LICENCE.txt

from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Action.MoveTo import MoveTo
from ai.STA.Action.Idle import Idle
from ai.STA.Tactic.tactic_constants import Flags
from ai.Util.ball_possession import player_grabbed_ball
from RULEngine.Util.Pose import Pose
from RULEngine.Util.geometry import get_angle, get_closest_point_on_line
from RULEngine.Util.constant import PLAYER_PER_TEAM

__author__ = 'RoboCupULaval'


class ReceivePass(Tactic):
    """
    méthodes:
        exec(self) : Exécute une Action selon l'état courant
    attributs:
        game_state: L'état courant du jeu.
        player_id : Identifiant du joueur auquel est assigné la tactique
        current_state : L'état courant de la tactique
        next_state : L'état suivant de la tactique
        status_flag : L'indicateur de progression de la tactique
    """

    def __init__(self, game_state, player_id):
        Tactic.__init__(self, game_state, player_id)
        assert isinstance(player_id, int)
        assert PLAYER_PER_TEAM >= player_id >= 0

        self.current_state = self.move_to_catch_ball
        self.next_state = self.move_to_catch_ball
        self.player_id = player_id

    def move_to_catch_ball(self):
        ball_position = self.game_state.get_ball_position()
        if player_grabbed_ball(self.game_state, self.player_id, ball_position):
            self.next_state = self.halt
            self.status_flag = Flags.SUCCESS
            return Idle(self.game_state, self.player_id)
        else:  # position the robot to be able to catch the ball
            current_position = self.game_state.get_player_position(self.player_id)
            next_ball_position = ball_position + self.game_state.get_ball_velocity()
            destination_position = get_closest_point_on_line(current_position, ball_position, next_ball_position)

            rotation_towards_ball = get_angle(destination_position, ball_position)
            pose_towards_ball = Pose(destination_position, rotation_towards_ball)

            self.next_state = self.move_to_catch_ball
            self.status_flag = Flags.WIP
            return MoveTo(self.game_state, self.player_id, pose_towards_ball)
