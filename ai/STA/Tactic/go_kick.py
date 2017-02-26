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

    def __init__(self, p_game_state, player_id, target=Pose()):
        Tactic.__init__(self, p_game_state, player_id, target)
        assert isinstance(player_id, int)
        assert PLAYER_PER_TEAM >= player_id >= 0

        self.player_id = player_id
        self.current_state = self.get_behind_ball
        self.next_state = self.get_behind_ball
        self.debug_interface = DebugInterface()
        self.move_action = self._generate_move_to()
        self.move_action.status_flag = Flags.SUCCESS
        self.last_ball_position = self.game_state.get_ball_position()
        self.charge_time = 0
        self.last_time = time.time()

    def get_behind_ball(self):
        ball_position = self.game_state.get_ball_position()
        player_pose = self.game_state.get_player_pose(self.player_id)
        distance_from_ball = get_distance(ball_position, player_pose.position)

        if distance_from_ball < self.game_state.const["KICK_BALL_DISTANCE"]*3.5:
            DebugInterface().add_log(5, "Behind ball OK!")
            self.next_state = self.get_close_ball
        else:
            DebugInterface().add_log(5, "distance from ball: {}".format(distance_from_ball))
            self.next_state = self.get_behind_ball

        self.move_action = GoBehind(self.game_state, self.player_id, ball_position, self.target.position,
                                    self.game_state.const["KICK_BALL_DISTANCE"]*2, robot_speed=0.3)
        return self.move_action

    def get_close_ball(self):
        ball_position = self.game_state.get_ball_position()
        player_pose = self.game_state.get_player_pose(self.player_id)
        distance_from_ball = get_distance(ball_position, player_pose.position)

        if distance_from_ball < self.game_state.const["KICK_BALL_DISTANCE"]*1.2:
            DebugInterface().add_log(5, "Close to ball, OK!")
            self.next_state = self.orient
        else:
            DebugInterface().add_log(5, "distance from ball: {}".format(distance_from_ball))
            self.next_state = self.get_close_ball

        self.move_action = GoBehind(self.game_state, self.player_id, ball_position, self.target.position,
                                    self.game_state.const["KICK_BALL_DISTANCE"], robot_speed=0.08)

        return self.move_action

    def orient(self):
        player_pose = self.game_state.get_player_pose(self.player_id)
        angle = get_angle(player_pose.position, self.target.position)
        orientation_erreur = angle - player_pose.orientation
        if math.fabs(orientation_erreur < ORIENTATION_DEADZONE):
            self.next_state = self.prepare_grab
            self.last_time = time.time()
        else:
            DebugInterface(4, "Erreur d'orientation: {}".format(orientation_erreur))
            self.next_state = self.orient
        # TODO angle check
        destination = Pose(player_pose.position, get_angle(player_pose.position, self.target.position))
        return GoToPositionNoPathfinder(self.game_state, self.player_id, destination)

    def prepare_grab(self):
        now = time.time()
        if now - self.last_time < COMMAND_DELAY:
            DebugInterface().add_log(5, "Dribbler on!")
            self.next_state = self.kiss_ball
        other_args = {"dribbler_on":2}
        return AllStar(self.game_state, self.player_id, **other_args)

    def kiss_ball(self):

        # get a point between you and the ball to approach
        ball_position = self.game_state.get_ball_position()
        player_pose = self.game_state.get_player_pose(self.player_id)
        angle = get_angle(player_pose.position, self.target.position)
        move_vec = ball_position + Position(self.game_state.const["ROBOT_RADIUS"] * math.cos(angle),
                                            self.game_state.const["ROBOT_RADIUS"] * math.sin(angle))
        target_pose = Pose(move_vec, angle)

        distance = get_distance(target_pose.position, player_pose.position)
        if distance <= self.game_state.const["KISS_BALL_DISTANCE"]:
            DebugInterface().add_log(5, "Ball grabbed!")
            self.next_state = self.kick_charge
        else:
            DebugInterface().add_log(5, "Distance from kiss: {}".format(distance))
            self.next_state = self.kiss_ball

        return GoToPositionNoPathfinder(self.game_state, self.player_id, target_pose)

    def kick_charge(self):

        if time.time() - self.last_time > COMMAND_DELAY * 6:
            DebugInterface().add_log(5, "Kick charge!")
            self.last_time = time.time()
            self.next_state = self.kick
        other_args = {"charge_kick":True, "dribbler_on":1}
        return AllStar(self.game_state, self.player_id, **other_args)

    def kick(self):
        now = time.time()
        if now - self.last_time > COMMAND_DELAY:
            DebugInterface().add_log(5, "Kick!")
            self.last_time = time.time()
            self.next_state = self.stop_dribbler
        return Kick(self.game_state, self.player_id, 7)

    def stop_dribbler(self):
        now = time.time()
        if now - self.last_time > COMMAND_DELAY:
            DebugInterface().add_log(5, "Dribbler off!")
            self.next_state = self.halt
        other_args = {"pose_goal":self.game_state.get_player_pose(self.player_id), "dribbler_on":1}
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
