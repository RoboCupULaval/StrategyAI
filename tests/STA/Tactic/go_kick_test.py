
import unittest
from time import sleep

from Util import Pose, Position
from ai.STA.Tactic.go_kick import GoKick, COMMAND_DELAY
from tests.STA.perfect_sim import PerfectSim

A_ROBOT = 1
START_POSE = Pose(300, 0, 0)
START_BALL_POSITION = START_POSE.position + Position(100, 0)
GOAL_POSE = Pose(700, 0, 0)
class TestGoKick(unittest.TestCase):

    def setUp(self):
        self.sim = PerfectSim(GoKick)

    def test_happy_path(self):
        self.sim.add_robot(A_ROBOT, START_POSE)
        self.sim.move_ball(START_BALL_POSITION)
        self.sim.start(A_ROBOT, GOAL_POSE)

        sleep(COMMAND_DELAY)
        self.sim.tick() # Charge

        self.sim.tick() # Go Behind
        self.sim.tick() # Go Behind

        self.sim.tick() # Grab Ball

        self.sim.tick() # Kick
