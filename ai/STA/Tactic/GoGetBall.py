# Under MIT licence, see LICENCE.txt

from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic.GoToPosition import GoToPosition
from ai.STA.Action.GoBehind import GoBehind
from ai.STA.Action.GetBall import GetBall
from ai.STA.Action.Idle import Idle

from ai.STA.Tactic import tactic_constants
from ai.Util.ball_possession import *
from ai.STA.Tactic.tactic_constants import Flags


from ai.Util.ball_possession import canGetBall, hasBall
from RULEngine.Util.geometry import get_distance
from RULEngine.Util.constant import DISTANCE_BEHIND, PLAYER_PER_TEAM, POSITION_DEADZONE, BALL_RADIUS
from RULEngine.Util.Pose import Pose

__author__ = 'RoboCupULaval'

POSITION_DEADZONE = POSITION_DEADZONE + BALL_RADIUS


class GoGetBall(Tactic):
    """
    méthodes:
        exec(self) : Exécute une Action selon l'état courant
    attributs:
        game_state: L'état courant du jeu.
        player_id : Identifiant du joueur auquel est assigné la tactique
        current_state : L'état courant de la tactique
        next_state : L'état suivant de la tactique
        status_flag : L'indicateur de progression de la tactique
        target: Position à laquelle faire face après avoir pris la balle
    """

    def __init__(self, p_game_state, player_id, target=Pose()):
        Tactic.__init__(self, p_game_state, player_id, target)
        assert isinstance(player_id, int)
        assert PLAYER_PER_TEAM >= player_id >= 0

        self.player_id = player_id
        self.current_state = self.get_behind_ball
        self.next_state = self.get_behind_ball

        self.move_action = GoToPosition(self.game_state, self.player_id,
                                        self.game_state.get_player_pose(self.player_id))
        self.move_action.status_flag = Flags.SUCCESS
        self.last_ball_position = self.game_state.get_ball_position()

    def get_behind_ball(self):

        self.status_flag = Flags.WIP
        move_action_status = self.move_action.status_flag
        dist = self._get_distance_from_ball()

        if move_action_status == Flags.SUCCESS and dist <= POSITION_DEADZONE:
            self.next_state = self.halt
        elif move_action_status == Flags.SUCCESS and dist > POSITION_DEADZONE:
            self.move_action = self._generate_move_to()
            self.next_state = self.get_behind_ball
        else:
            self.next_state = self.get_behind_ball

        return self.move_action

    def grab_ball(self):
        if hasBall(self.game_state, self.player_id):
            self.next_state = self.halt
            self.status_flag = Flags.SUCCESS
        elif canGetBall(self.game_state, self.player_id):
            self.next_state = self.grab_ball
        else:
            self.next_state = self.get_behind_ball  # back to go_behind; the ball has moved

        grab_ball = GetBall(self.game_state, self.player_id)
        return grab_ball

    def halt(self):
        self.status_flag = Flags.SUCCESS
        dist = self._get_distance_from_ball()

        if dist > POSITION_DEADZONE:
            self.next_state = self.get_behind_ball
        else:
            self.next_state = self.halt

        return Idle(self.game_state, self.player_id)

    def _get_distance_from_ball(self):
        return get_distance(self.game_state.get_player_pose(self.player_id).position,
                            self.game_state.get_ball_position())

    def _generate_move_to(self):
        go_behind = GoBehind(self.game_state, self.player_id, self.game_state.get_ball_position(), self.target.position,
                             DISTANCE_BEHIND)
        destination = go_behind  # .move_destination
        return destination  # GoToPosition(self.game_state, self.player_id, destination)

    def _reset_ttl(self):
        super()._reset_ttl()
        if get_distance(self.last_ball_position, self.game_state.get_ball_position()) > POSITION_DEADZONE:
            self.last_ball_position = self.game_state.get_ball_position()
            self.move_action = self._generate_move_to()
