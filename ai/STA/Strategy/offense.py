# Under MIT license, see LICENSE.txt
from functools import partial

from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.constant import PLAYER_PER_TEAM
from ai.STA.Tactic.GoGetBall import GoGetBall
from ai.STA.Tactic.GoalKeeper import GoalKeeper
from ai.STA.Tactic.Stop import Stop
from ai.STA.Tactic.capture import Capture
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.position_for_pass import PositionForPass
from ai.STA.Tactic.tactic_constants import Flags
from . Strategy import Strategy


# stratégie: tout le monde fonce vers la balle car c'est tout ce qu'on sait faire


class SimpleOffense(Strategy):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)
        self.goalkeeper = 3
        self.passing_robot = 5
        self.receiver = 4
        goal1 = Pose(Position(-1636, 0))
        goal2 = Pose(Position(1636, 0))
        self.add_tactic(self.goalkeeper, GoalKeeper(self.game_state, self.goalkeeper))

        receiver_pose = Pose(Position(-500, -500))
        self.add_tactic(self.receiver, PositionForPass(self.game_state, self.receiver, receiver_pose))
        self.add_tactic(self.receiver, GoKick(self.game_state, self.receiver, goal1))
        self.add_condition(self.receiver, 0, 1, partial(self.is_passing_robot_success, self.receiver))
        self.add_condition(self.receiver, 1, 0, partial(self.has_receiver_kicked_to_goal, self.receiver))


        self.add_tactic(self.passing_robot, Capture(self.game_state, self.passing_robot, receiver_pose))
        self.add_tactic(self.passing_robot, GoKick(self.game_state, self.passing_robot, receiver_pose))
        self.add_tactic(self.passing_robot, Stop(self.game_state, self.passing_robot))
        self.add_condition(self.passing_robot, 0, 1, partial(self.is_receiver_ready, self.passing_robot))
        self.add_condition(self.passing_robot, 1, 2, partial(self.is_passing_robot_success, self.passing_robot))
        self.add_condition(self.passing_robot, 2, 0, partial(self.has_receiver_kicked_to_goal, self.passing_robot))
        self.add_condition(self.passing_robot, 2, 1, partial(self.is_receiver_ready, self.passing_robot))

        for i in range(PLAYER_PER_TEAM):
            if not (i == self.goalkeeper or i == self.passing_robot or i == self.receiver):
                self.add_tactic(i, Stop(self.game_state, i))


    def is_passing_robot_success(self, i):
        return (self.game_state.get_ball_position().x < 0 and self.game_state.get_ball_position().y < 0)

    def has_receiver_kicked_to_goal(self, i):
        if self.graphs[self.receiver].get_current_tactic_name() == 'GoKick':
            return self.graphs[self.receiver].get_current_tactic().status_flag == Flags.SUCCESS
        else:
            return False

    def is_receiver_ready(self, i):
        if self.graphs[self.receiver].get_current_tactic_name() == 'PositionForPass':
            return self.graphs[self.receiver].get_current_tactic().status_flag == Flags.SUCCESS
        else:
            return False