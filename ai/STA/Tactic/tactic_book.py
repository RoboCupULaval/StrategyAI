# Under MIT License, see LICENSE.txt
import logging
from typing import List, Type

from ai.STA.Tactic.align_around_the_ball import AlignAroundTheBall
from ai.STA.Tactic.demo_follow_ball import DemoFollowBall
from ai.STA.Tactic.demo_follow_robot import DemoFollowRobot
from ai.STA.Tactic.face_target import FaceTarget
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.go_kick_experimental_sequence import GoKickExperimental
from ai.STA.Tactic.go_to_position import GoToPosition
from ai.STA.Tactic.go_to_random_pose_in_zone import GoToRandomPosition
from ai.STA.Tactic.goalkeeper import GoalKeeper
from ai.STA.Tactic.leeroy_jenkins import LeeroyJenkins
from ai.STA.Tactic.pass_to_player import PassToPlayer
from ai.STA.Tactic.place_ball import PlaceBall
from ai.STA.Tactic.receive_pass import ReceivePass
from ai.STA.Tactic.rotate_around_ball import RotateAroundBall
from ai.STA.Tactic.stay_away_from_ball import StayAwayFromBall
from ai.STA.Tactic.stop import Stop
from ai.STA.Tactic.stress_test_robot import StressTestRobotWaypoint, StressTestRobot
from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.test_best_passing_option import TestBestPassingOption


class TacticBook:
    def __init__(self):

        self.logger = logging.getLogger(self.__class__.__name__)

        self.stop_tactic = Stop

        defaults_tactics = [GoToPosition, GoKick]

        tactics = {ReceivePass,
                   PlaceBall,
                   FaceTarget,
                   DemoFollowBall,
                   DemoFollowRobot,
                   GoalKeeper,
                   GoToRandomPosition,
                   PassToPlayer,
                   StayAwayFromBall,
                   RotateAroundBall,
                   GoKickExperimental,
                   RotateAroundBall,
                   StressTestRobot,
                   StressTestRobotWaypoint,
                   AlignAroundTheBall,
                   LeeroyJenkins,
                   TestBestPassingOption,
                   *defaults_tactics,
                   self.stop_tactic}

        self.tactic_book = {tactic.name(): tactic for tactic in tactics}
        self.default_tactics = [tactic.name() for tactic in defaults_tactics]

    @property
    def tactics_name(self) -> List[str]:
        return list(self.tactic_book.keys())

    def check_existance_tactic(self, tactic_name: str) -> bool:
        assert isinstance(tactic_name, str)
        return tactic_name in self.tactic_book

    def get_tactic(self, tactic_name: str) -> Type[Tactic]:
        if self.check_existance_tactic(tactic_name):
            return self.tactic_book[tactic_name]
        self.logger.error('A non-existing tactic was asked: {}'.format(tactic_name))
        return self.stop_tactic
