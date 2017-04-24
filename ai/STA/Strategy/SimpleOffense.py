# Under MIT license, see LICENSE.txt
from functools import partial

from RULEngine.Command.command import Stop
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.constant import PLAYER_PER_TEAM
from ai.STA.Tactic.GoGetBall import GoGetBall
from ai.STA.Tactic.GoalKeeper import GoalKeeper
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

        receiver_pose = Pose(Position(-500, 200))
        self.add_tactic(self.receiver, PositionForPass(self.game_state, self.receiver, receiver_pose))
        self.add_tactic(self.receiver, GoKick(self.game_state, self.receiver, goal1))
        self.add_condition(self.receiver, 0, 1, partial(self.passing_robot_success, self.receiver))
        self.add_condition(self.receiver, 1, 0, partial(self.receiver_kick_to_goal, self.receiver))

        self.add_tactic(self.passing_robot, GoKick(self.game_state, self.passing_robot, receiver_pose))
        self.add_condition(self.passing_robot, 0, 0, partial(self.receiver_kick_to_goal, self.passing_robot))

        for i in range(PLAYER_PER_TEAM):
            if not (i == self.goalkeeper or i == self.passing_robot or i == self.receiver):
                self.add_tactic(i, Stop(self.game_state, i))


    def passing_robot_success(self):
        return self.graphs[self.passing_robot].get_current_tactic().status_flag == Flags.SUCCESS

    def receiver_kick_to_goal(self):
        return self.graphs[self.receiver].get_current_tactic().status_flag == Flags.SUCCESS