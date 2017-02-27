# Under MIT licence, see LICENCE.txt
import time

from RULEngine.Debug.debug_interface import DebugInterface
from ai.STA.Action.AllStar import AllStar
from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Action.GoBehind import GoBehind
from ai.STA.Action.GetBall import GetBall
from ai.STA.Action.Idle import Idle
from ai.STA.Tactic.GoToPositionNoPathfinder import GoToPositionNoPathfinder
from ai.STA.Tactic.tactic_constants import Flags
from ai.STA.Action.MoveToPosition import MoveToPosition

from ai.Util.ball_possession import can_get_ball, has_ball
from RULEngine.Util.geometry import get_distance, get_angle
from RULEngine.Util.constant import DISTANCE_BEHIND, PLAYER_PER_TEAM, POSITION_DEADZONE, BALL_RADIUS
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
import numpy as np

__author__ = 'RoboCupULaval'

ANGLE_DEADZONE = 0.08
COMMAND_DELAY = 0.5


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
        self.p_game_state = p_game_state
        self.move_action = \
            GoToPositionNoPathfinder(self.game_state,
                                     self.player_id,
                                     self.game_state.
                                     get_player_pose(self.player_id))
        self.move_action.status_flag = Flags.SUCCESS
        self.last_ball_position = self.game_state.get_ball_position()
        self.last_angle = 0
        self.last_time = time.time()
        self.vector_norm = 1000

    def get_behind_ball(self):
        self.status_flag = Flags.WIP
        dist = self._get_distance_from_ball()
        angle = get_angle(self.game_state.get_player_pose(self.player_id).position, self.target.position)

        player_x = self.game_state.game.friends.players[self.player_id].pose.position.x
        player_y = self.game_state.game.friends.players[self.player_id].pose.position.y

        ball_x = self.game_state.get_ball_position().x
        ball_y = self.game_state.get_ball_position().y

        target_x = self.target.position.x
        target_y = self.target.position.y

        vector_player_2_ball = np.array([ball_x - player_x, ball_y - player_y])
        vector_target_2_ball = np.array([ball_x - target_x, ball_y - target_y])
        angle_ball_2_target =  np.arctan2(vector_target_2_ball[1], vector_target_2_ball[0])

        vector_player_2_ball /= np.linalg.norm(vector_player_2_ball)
        vector_target_2_ball /= np.linalg.norm(vector_target_2_ball)

        if np.dot(vector_player_2_ball, vector_target_2_ball) < - 0.95:
            if self.game_state.game.friends.players[self.player_id].velocity[2] < 0.01:
                print(abs(angle_ball_2_target - self.game_state.game.friends.players[self.player_id].pose.orientation))
                if abs(abs(angle_ball_2_target - self.game_state.game.friends.players[self.player_id].pose.orientation) - np.pi) < 0.1 or \
                                abs(angle_ball_2_target - self.game_state.game.friends.players[self.player_id].pose.orientation) < 0.1:
                    self.last_time = time.time()
                    self.next_state = self.stay_idle
        else:
            DebugInterface().add_log(4, "Distance from ball: {}".format(dist))
            self.next_state = self.get_behind_ball
        return GoBehind(self.game_state, self.player_id, self.game_state.get_ball_position()+Position(vector_player_2_ball[0]*70, vector_player_2_ball[1] * 70), self.target.position,
                        self.game_state.const["DISTANCE_BEHIND"])

    def stay_idle(self):
        self.next_state = self.start_dribbler
        # if self.vector_norm > 150:
        #     print("are you even real^")
        #     self.next_state = self.get_behind_ball

        return Idle(self.game_state, self.player_id)

    def start_dribbler(self):
        now = time.time()
        if now - self.last_time > COMMAND_DELAY:
            DebugInterface().add_log(5, "Dribbler on!")
            self.last_ball_position = self.game_state.get_ball_position()
            self.last_angle = self.game_state.game.friends.players[self.player_id].pose.orientation
            self.next_state = self.grab_ball
        other_args = {"dribbler_on": 2}
        return AllStar(self.game_state, self.player_id, **other_args)

    def grab_ball(self):
        # if has_ball(self.game_state, self.player_id):
        #     self.next_state = self.halt
        #     self.status_flag = Flags.SUCCESS
        # elif can_get_ball(self.game_state, self.player_id, self.target.position):
        #     self.next_state = self.grab_ball
        # else:
        #     self.next_state = self.get_behind_ball  # back to go_behind; the ball has moved
        DebugInterface().add_log(1, "Grab ball called")
        player_x = self.game_state.game.friends.players[self.player_id].pose.position.x
        player_y = self.game_state.game.friends.players[self.player_id].pose.position.y
        ball_x = self.game_state.get_ball_position().x
        ball_y = self.game_state.get_ball_position().y
        vector_player_2_ball = np.array([ball_x - player_x, ball_y - player_y])

        self.vector_norm = np.linalg.norm(vector_player_2_ball)
        DebugInterface().add_log(1, "vector player 2 ball : {} mm".format(self.vector_norm))
        if self.vector_norm < 110:
            self.next_state = self.halt
        DebugInterface().add_log(1, "orientation go get ball {}".format(self.last_angle))
        #grab_ball = GetBall(self.game_state, self.player_id)
        return MoveToPosition(self.game_state, self.player_id, Pose(Position(vector_player_2_ball[0]*300, vector_player_2_ball[1] * 300), self.last_angle), 0.15)

    def halt(self):
        self.status_flag = Flags.SUCCESS
        dist = self._get_distance_from_ball()
        # else:
        #     self.next_state = self.halt
        DebugInterface().add_log(1, "GogetBall so sucessfull")
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
