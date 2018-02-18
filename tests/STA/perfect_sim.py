
import logging

from Util import Pose, Position
from ai.GameDomainObjects import Ball
from ai.STA.Tactic.tactic import Tactic
from ai.states import GameState


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

    def add_robot(self, robot_id, pose: Pose):
        self.game_state.our_team.players[robot_id].pose = pose

    def add_enemy_robot(self, robot_id, pose: Pose):
        self.game_state.enemy_team.players[robot_id].pose = pose

    def move_ball(self, position: Position):
        self.game_state.ball = Ball(0, position)

    def start(self, robot_id, target: Pose):
        self.hero_robot = GameState().our_team.players[robot_id]
        self.tactic = self.tactic_obj(GameState(), self.hero_robot, target)

    def tick(self):
        if not self.tactic:
            raise RuntimeError("You must call start() to initialize the simulation")
        ia_cmd = self.tactic.exec()

        self._apply_cmd(ia_cmd)

    def _apply_cmd(self, ia_cmd):
        if ia_cmd.kick_type:
            print("kick")
        if ia_cmd.target:
            self.hero_robot.pose = ia_cmd.target


