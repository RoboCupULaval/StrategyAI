# Under MIT licence, see LICENCE.txt
import math
import time

from RULEngine.Debug.debug_interface import DebugInterface
from RULEngine.Util.Pose import Pose
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

__author__ = 'RoboCupULaval'

#POSITION_DEADZONE = POSITION_DEADZONE + BALL_RADIUS + ROBOT_RADIUS
POSITION_DEADZONE = 90
ORIENTATION_DEADZONE = 0.05
DISTANCE_TO_KICK_REAL = ROBOT_RADIUS * 3.4
DISTANCE_TO_KICK_SIM = ROBOT_RADIUS + BALL_RADIUS


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

    def get_behind_ball(self):
        print('GET_BEHIND_BALL')
        dest_position = self.get_behind_ball_position(self.game_state.get_ball_position())
        player_position = self.game_state.get_player_pose(self.player_id).position
        dist = get_distance(player_position, dest_position)

        if dist <= POSITION_DEADZONE:
            print('LETS_ORIENT')
            self.next_state = self.orient
        elif dist > POSITION_DEADZONE:
            print('LETS_MOVE_TO')
            self.move_action = self._generate_move_to()
            self.next_state = self.get_behind_ball

        self.move_action = self._generate_move_to()
        return self.move_action

    def orient(self):
        print('ORIENT')
        player_pose = self.game_state.get_player_pose(self.player_id)
        #vec_dir = self.target.position - player_pose.position
        #theta = math.atan2(vec_dir.y, vec_dir.x)
        if math.fabs(get_angle(player_pose.position, self.target.position)) - player_pose.orientation < ORIENTATION_DEADZONE:
            self.next_state = self.prepare_grab
        # TODO angle check
        destination = Pose(player_pose.position, get_angle(player_pose.position, self.target.position))
        return GoToPositionNoPathfinder(self.game_state, self.player_id, destination)

    def prepare_grab(self):
        print('PREPARE GRAB')
        self.next_state = self.kiss_ball
        other_args = {"dribbler_on": 2}
        return AllStar(self.game_state, self.player_id, **other_args)

    def kiss_ball(self):

        if self._get_distance_from_ball() <= DISTANCE_TO_KICK_REAL:
            self.next_state = self.kick_charge

        # get a point between you and the ball to approach
        ball_pst = self.game_state.get_ball_position()
        player_pose = self.game_state.get_player_pose(self.player_id)

        return GoToPositionNoPathfinder(self.game_state, self.player_id,
                                        Pose(ball_pst, player_pose.orientation))

    def kick_charge(self):
        if self.charge_time == 0:
            self.charge_time = time.time()

        if time.time() - self.charge_time > 4:
            self.next_state = self.kick
        other_args = {"charge_kick": True, "dribbler_on": 1}
        return AllStar(self.game_state, self.player_id, **other_args)

    def kick(self):
        print('KICK!')
        self.next_state = self.stop_dribbler
        return Kick(self.game_state, self.player_id, 7)

    def stop_dribbler(self):
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

        return AllStar(self.game_state, self.player_id, **{"pose_goal": destination_pose,
                                                           "ai_command_type": AICommandType.MOVE})

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
