# Under MIT licence, see LICENCE.txt
from ai.STA.Tactic.GoToPositionNoPathfinder import GoToPositionNoPathfinder
from .Tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags, DEFAULT_TIME_TO_LIVE
from ..Action.ProtectGoal import ProtectGoal
from ai.STA.Action.GetBall import GetBall
from ai.STA.Action.GoBehind import GoBehind
from ai.STA.Action.Idle import Idle
from ai.Util.ball_possession import canGetBall, hasBall
from RULEngine.Util.Position import Position
from RULEngine.Util.Pose import Pose
from RULEngine.Util.area import isInsideGoalArea
from RULEngine.Util.constant import PLAYER_PER_TEAM, DISTANCE_BEHIND, TeamColor
from RULEngine.Util.constant import Relative


__author__ = 'RoboCupULaval'

# TODO WORK IN PROGRESS
class AssistantGoalkeeper(Tactic):
    """
    """
    # TODO: À complexifier pour prendre en compte la position des jouers adverses et la vitesse de la balle.

    def __init__(self, p_game_state, p_player_id, target=Pose(),
                 time_to_live=DEFAULT_TIME_TO_LIVE):
        Tactic.__init__(self, p_game_state, p_player_id, target)
        assert isinstance(p_player_id, int)
        assert PLAYER_PER_TEAM >= p_player_id >= 0

        self.player_id = p_player_id
        self.current_state = self.protect_goal
        self.next_state = self.protect_goal
        self.status_flag = Flags.INIT
        self.side = None
        self.zone = None
        self._check_side_and_zone()

    def protect_goal(self):
        # FIXME : enlever ce hack de merde
        ball_position = self.game_state.get_ball_position()
        if not isInsideGoalArea(ball_position):
            self.next_state = self.protect_goal
        else:
            if canGetBall(self.game_state, self.player_id, ball_position):
                self.next_state = self.grab_ball
            else:
                self.next_state = self.go_behind_ball
        self.target = Pose(self.game_state.get_ball_position())

        return GoToPositionNoPathfinder(self.game_state, self.player_id)

    def go_behind_ball(self):
        ball_position = self.game_state.get_ball_position()

        if canGetBall(self.game_state, self.player_id, ball_position):
            self.next_state = self.grab_ball
        else:
            self.next_state = self.go_behind_ball

        return GoBehind(self.game_state, self.player_id, ball_position, Position(0, 0), DISTANCE_BEHIND)

    def grab_ball(self):
        ball_position = self.game_state.get_ball_position()
        if hasBall(self.game_state, self.player_id):
            self.next_state = self.halt
            self.status_flag = Flags.SUCCESS
        elif canGetBall(self.game_state, self.player_id, ball_position):
            self.next_state = self.grab_ball
        else:
            self.next_state = self.go_behind_ball  # back to go_behind; the ball has moved
        return GetBall(self.game_state, self.player_id)

    def _check_zone(self):
        # TODO change this
        if self.target.position.y < 0:
            self.zone = Relative.NEGATIVE
        elif self.target.position.y > 0:
            self.zone = Relative.POSITIVE
        else:
            raise TypeError("Le target d'une tactique assistant_goalkeeper doit "
                            "avoir un position en y positive ou négative(pas 0)!")
