
import logging

from Util import Pose, Position
from Util.constant import ROBOT_CENTER_TO_KICKER, BALL_RADIUS, KickForce
from Util.geometry import compare_angle
from ai.STA.Tactic.tactic import Tactic
from ai.states.game_state import GameState


class PerfectSim:

    def __init__(self, tactic_obj):
        assert not isinstance(tactic_obj, Tactic), "You must pass the class, not an instance of the class. (ex: 'GoToPosition', not 'GoToPosition()')"

        self.logger = logging.getLogger(self.__class__.__name__)
        self.tactic_obj = tactic_obj
        self.tactic = None

        self.hero_robot = None
        self.game_state = GameState()

        # Singleton are a pain in the ass, there state must be reset
        self.game_state.reset()

        # Variable for assertion
        self.last_ia_cmd = None
        self.has_charge_kick = False
        self.has_hit_ball = False

    def add_robot(self, robot_id, pose: Pose):
        self.game_state.our_team.players[robot_id].pose = pose

    def add_enemy_robot(self, robot_id, pose: Pose):
        self.game_state.enemy_team.players[robot_id].pose = pose

    def move_ball(self, position: Position):
        self.game_state.ball.position = position

    def start(self, robot_id, target: Pose):
        self.hero_robot = GameState().our_team.players[robot_id]
        self.tactic = self.tactic_obj(GameState(), self.hero_robot, target)

    def tick(self):
        if not self.tactic:
            raise RuntimeError("You must call start() to initialize the simulation")

        print("====== Executing {} ======".format(str(self.tactic.current_state.__func__)))
        ia_cmd = self.tactic.exec()

        self._apply_cmd(ia_cmd)

    def has_kick(self):
        return self.last_ia_cmd.kick_force != KickForce.NONE

    def _apply_cmd(self, ia_cmd):
        self.last_ia_cmd = ia_cmd

        if ia_cmd.target:
            print("Hero Robot moved to {}".format(ia_cmd.target))
            self.hero_robot.pose = ia_cmd.target

        if ia_cmd.kick_force != KickForce.NONE:
            if self._robot_can_hit_ball(self.hero_robot):
                print("Hero Robot has kick and hit the ball")
                self.has_hit_ball = True
            else:
                print("Hero Robot has kick, but didn't hit the ball")

        if ia_cmd.charge_kick:
            self.has_charge_kick = True

    def _robot_can_hit_ball(self, robot):
        KICK_DISTANCE_MIN = ROBOT_CENTER_TO_KICKER - BALL_RADIUS * 0.5
        KICK_DISTANCE_MAX = ROBOT_CENTER_TO_KICKER + BALL_RADIUS * 1.5
        MAX_ANGLE_FOR_KICK = 15

        ball_position = self.game_state.ball.position
        robot_to_ball = robot.pose.position - ball_position

        return KICK_DISTANCE_MIN < robot_to_ball.norm <  KICK_DISTANCE_MAX \
               and compare_angle(robot.pose.orientation, robot_to_ball.angle, abs_tol=MAX_ANGLE_FOR_KICK)





