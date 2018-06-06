
import unittest
from time import sleep

from Util import Pose, Position
from ai.STA.Tactic.go_kick import GoKick, COMMAND_DELAY
from tests.STA.perfect_sim import PerfectSim

A_ROBOT_ID = 1
START_POSE = Pose.from_values(300, 0, 0)
START_BALL_POSITION = START_POSE.position + Position(100, 0)
GOAL_POSE = Pose.from_values(700, 0, 0)
MAX_TICK_UNTIL_KICK = 7


class TestGoKick(unittest.TestCase):

    def setUp(self):
        self.sim = PerfectSim(GoKick)

    def test_givenARobotAndABall_thenKickTheBall(self):
        self.sim.add_robot(A_ROBOT_ID, START_POSE)
        self.sim.move_ball(START_BALL_POSITION)
        self.sim.start(A_ROBOT_ID, target=GOAL_POSE)

        self.sim.tick() # initialize

        for _ in range(0, MAX_TICK_UNTIL_KICK):
            self.sim.tick()
            if self.sim.has_kick():
                assert self.sim.has_hit_ball
                return
        assert False, "Reach max number of tick and no kick"


