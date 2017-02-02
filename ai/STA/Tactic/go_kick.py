# Under MIT licence, see LICENCE.txt
from math import sqrt
from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Action.GoBehind import GoBehind
from ai.STA.Action.GetBall import GetBall
from ai.STA.Action.Idle import Idle
from ai.STA.Tactic.GoToPositionNoPathfinder import GoToPositionNoPathfinder
from ai.STA.Action.Kick import Kick
from ai.Debug.debug_interface import DebugInterface

from RULEngine.Util.geometry import get_angle
from ai.STA.Tactic.tactic_constants import Flags

from ai.Util.ball_possession import canGetBall, hasBall
from RULEngine.Util.geometry import get_distance
from RULEngine.Util.constant import DISTANCE_BEHIND, PLAYER_PER_TEAM, POSITION_DEADZONE, BALL_RADIUS, ROBOT_RADIUS
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position

__author__ = 'RoboCupULaval'

POSITION_DEADZONE = POSITION_DEADZONE + BALL_RADIUS + ROBOT_RADIUS
DISTANCE_TO_KICK_REAL = ROBOT_RADIUS
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

    def get_behind_ball(self):

        self.status_flag = Flags.WIP
        dist = self._get_distance_from_ball()

        if dist <= POSITION_DEADZONE:
            self.next_state = self.orient
        elif dist > POSITION_DEADZONE:
            self.move_action = self._generate_move_to()
            self.next_state = self.get_behind_ball
        self.move_action = self._generate_move_to()

        return self.move_action

    def orient(self):
        player_pose = self.game_state.get_player_pose(self.player_id)
        if get_angle(player_pose.position, self.target.position) - player_pose.orientation < 0.1:
            self.next_state = self.kiss_ball
        # TODO angle check
        destination = Pose(player_pose.position, get_angle(player_pose.position, self.target.position))
        return GoToPositionNoPathfinder(self.game_state, self.player_id, destination)

    def kiss_ball(self):

        if self._get_distance_from_ball() <= DISTANCE_TO_KICK_SIM:
            self.next_state = self.kick

        # get a point between you and the ball to approach
        ball_pst = self.game_state.get_ball_position()
        player_pose = self.game_state.get_player_pose(self.player_id)

        return GoToPositionNoPathfinder(self.game_state, self.player_id,
                                        Pose(ball_pst, player_pose.orientation))

    def kick(self):
        self.next_state = self.halt
        # TODO KICKING!!!!
        return Kick(self.game_state, self.player_id, 7)

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
                             DISTANCE_BEHIND, pathfinding=True)
        destination = go_behind  # .move_destination
        return destination  # GoToPosition(self.game_state, self.player_id, destination)

    def _reset_ttl(self):
        super()._reset_ttl()
        if get_distance(self.last_ball_position, self.game_state.get_ball_position()) > POSITION_DEADZONE:
            self.last_ball_position = self.game_state.get_ball_position()
            self.move_action = self._generate_move_to()
