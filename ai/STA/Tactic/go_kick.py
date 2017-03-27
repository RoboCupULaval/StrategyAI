# Under MIT licence, see LICENCE.txt
import math
import time

from RULEngine.Debug.debug_interface import DebugInterface
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.constant import PLAYER_PER_TEAM, POSITION_DEADZONE, BALL_RADIUS, ROBOT_RADIUS
from RULEngine.Util.geometry import get_angle
from RULEngine.Util.geometry import get_distance
from ai.STA.Action.AllStar import AllStar
from ai.STA.Action.Idle import Idle
from ai.STA.Action.Kick import Kick
from ai.STA.Tactic.GoToPositionNoPathfinder import GoToPositionNoPathfinder
from ai.STA.Tactic.GoGetBall import GoGetBall
from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.Util.ai_command import AICommand, AICommandType
from ai.STA.Action.GoBehind import GoBehind

__author__ = 'RoboCupULaval'

POSITION_DEADZONE = 40
ORIENTATION_DEADZONE = 0.2
DISTANCE_TO_KICK_REAL = ROBOT_RADIUS * 3.4
DISTANCE_TO_KICK_SIM = ROBOT_RADIUS + BALL_RADIUS
COMMAND_DELAY = 1.5


class GoKick(Tactic):
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

    def __init__(self, p_game_state, player_id, target=Pose(), args=None):
        Tactic.__init__(self, p_game_state, player_id, target, args)
        assert isinstance(player_id, int)
        assert PLAYER_PER_TEAM >= player_id >= 0

        self.player_id = player_id
        self.current_state = self.kick_charge
        self.next_state = self.kick_charge
        self.debug_interface = DebugInterface()
        self.move_action = self._generate_move_to()
        self.move_action.status_flag = Flags.SUCCESS
        self.last_ball_position = self.game_state.get_ball_position()
        self.charge_time = 0
        self.last_time = time.time()

        self.target = target

        self.go_get_ball_tactic = GoGetBall(self.game_state, self.player_id, self.target)

    def kick_charge(self):
        if time.time() - self.last_time > COMMAND_DELAY:
            DebugInterface().add_log(5, "Kick charge!")
            self.last_time = time.time()
            self.next_state = self.go_get_ball
        other_args = {"charge_kick": True, "dribbler_on": 1}
        return AllStar(self.game_state, self.player_id, **other_args)

    def go_get_ball(self):
        if self.go_get_ball_tactic.status_flag == Flags.SUCCESS:
            self.last_time = time.time()
            self.next_state = self.kick
        return self.go_get_ball_tactic

    def kick(self):
        now = time.time()
        if now - self.last_time > COMMAND_DELAY:
            DebugInterface().add_log(5, "Kick!")
            self.last_time = time.time()
            self.next_state = self.stop_dribbler
        return Kick(self.game_state, self.player_id, 1)

    def stop_dribbler(self):
        now = time.time()
        if now - self.last_time > COMMAND_DELAY:
            DebugInterface().add_log(5, "Dribbler off!")
            self.next_state = self.halt
        other_args = {"pose_goal": self.game_state.get_player_pose(self.player_id), "dribbler_on": 1}
        return AllStar(self.game_state, self.player_id, **other_args)

    def halt(self):
        self.status_flag = Flags.SUCCESS
        return Idle(self.game_state, self.player_id)

    def _get_distance_from_ball(self):
        return get_distance(self.game_state.get_player_pose(self.player_id).position,
                            self.game_state.get_ball_position())

    def _generate_move_to(self):
        player_pose = self.game_state.get_player_pose(self.player_id)
        ball_position = self.game_state.get_ball_position()

        dest_position = self.get_behind_ball_position(ball_position)
        destination_pose = Pose(dest_position, player_pose.orientation)

        return AllStar(self.game_state, self.player_id, **{"pose_goal":destination_pose,
                                                           "ai_command_type":AICommandType.MOVE
                                                           })

    def get_behind_ball_position(self, ball_position):
        vec_dir = self.target.position - ball_position
        mag = math.sqrt(vec_dir.x ** 2 + vec_dir.y ** 2)
        scale_coeff = ROBOT_RADIUS * 3 / mag
        dest_position = ball_position - (vec_dir * scale_coeff)
        return dest_position

    def _reset_ttl(self):
        super()._reset_ttl()
        if get_distance(self.last_ball_position, self.game_state.get_ball_position()) > POSITION_DEADZONE:
            self.last_ball_position = self.game_state.get_ball_position()
            self.move_action = self._generate_move_to()
