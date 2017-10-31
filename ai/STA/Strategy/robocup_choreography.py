# Under MIT License, see LICENSE.txt

from functools import partial
from random import shuffle

from RULEngine.Util.Pose import Position, Pose
from ai.STA.Strategy.strategy_placehlder import Strategy
from RULEngine.Util.constant import PLAYER_PER_TEAM
from ai.STA.Tactic.go_to_position_pathfinder import GoToPositionPathfinder
from ai.STA.Tactic.stop import Stop
from ai.STA.Tactic.tactic_constants import Flags


class RobocupChoreography(Strategy):

    def __init__(self, p_game_state):
        super().__init__(p_game_state)

        robot1 = 4
        robot2 = 2
        robot3 = 3
        self.tactic_conditions = [False for i in range(PLAYER_PER_TEAM)]
        dist_inter_robot = 300
        positions_on_xaxis = [Pose(Position(-dist_inter_robot*3, 0), 1.57),
                              Pose(Position(-dist_inter_robot*2, 0), 1.57),
                              Pose(Position(-dist_inter_robot, 0), 1.57),
                              Pose(Position(dist_inter_robot, 0), 1.57),
                              Pose(Position(2*dist_inter_robot, 0), 1.57),
                              Pose(Position(3*dist_inter_robot, 0), 1.57)]
        shuffle(positions_on_xaxis)
        positions_on_yaxis = [Pose(Position(0, -dist_inter_robot * 3), 0),
                              Pose(Position(0, -dist_inter_robot * 2), 0),
                              Pose(Position(0, -dist_inter_robot), 0),
                              Pose(Position(0, dist_inter_robot), 0),
                              Pose(Position(0, 2 * dist_inter_robot), 0),
                              Pose(Position(0, 3 * dist_inter_robot), 0)]
        shuffle(positions_on_yaxis)
        '''
        for i in range(PLAYER_PER_TEAM):
            self.add_tactic(i, GoToPositionPathfinder(self.game_state, i, positions_on_xaxis[i]))
            self.add_tactic(i, GoToPositionPathfinder(self.game_state, i, positions_on_yaxis[i]))
            self.add_condition(i, 0, 1, partial(self.condition, i))
            self.add_condition(i, 1, 0, partial(self.condition, i))
        '''
        self.add_tactic(robot1, GoToPositionPathfinder(self.game_state, robot1, positions_on_xaxis[robot1]))
        self.add_tactic(robot1, GoToPositionPathfinder(self.game_state, robot1, positions_on_yaxis[robot1]))
        self.add_condition(robot1, 0, 1, partial(self.condition, robot1))
        self.add_condition(robot1, 1, 0, partial(self.condition, robot1))

        self.add_tactic(robot2, GoToPositionPathfinder(self.game_state, robot2, positions_on_xaxis[robot2]))
        self.add_tactic(robot2, GoToPositionPathfinder(self.game_state, robot2, positions_on_yaxis[robot2]))
        self.add_condition(robot2, 0, 1, partial(self.condition, robot2))
        self.add_condition(robot2, 1, 0, partial(self.condition, robot2))

        self.add_tactic(robot3, GoToPositionPathfinder(self.game_state, robot3, positions_on_xaxis[robot3]))
        self.add_tactic(robot3, GoToPositionPathfinder(self.game_state, robot3, positions_on_yaxis[robot3]))
        self.add_condition(robot3, 0, 1, partial(self.condition, robot3))
        self.add_condition(robot3, 1, 0, partial(self.condition, robot3))

        for i in range(PLAYER_PER_TEAM):
            if not (i == robot1 or i == robot2 or i == robot3):
                self.add_tactic(i, Stop(self.game_state, i))


    def condition(self, i):
        self.tactic_conditions[i] = self.graphs[i].get_current_tactic().status_flag == Flags.SUCCESS

        if not self.tactic_conditions[4]:
            return False
        if not self.tactic_conditions[2]:
            return False
        if not self.tactic_conditions[3]:
            return False
        '''
        for k in range(PLAYER_PER_TEAM):
            if not self.tactic_conditions[k]:
                return False
        '''
        return True

