# Under MIT License, see LICENSE.txt

from functools import partial
from random import shuffle

from Util.constant import PLAYER_PER_TEAM
from Util.pose import Pose, Position

from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.go_to_position_pathfinder import GoToPositionPathfinder
from ai.STA.Tactic.stop import Stop
from ai.STA.Tactic.tactic_constants import Flags
from Util.role import Role


class RobocupChoreography(Strategy):

    def __init__(self, p_game_state):
        super().__init__(p_game_state)

        robot1 = Role.FIRST_ATTACK
        robot2 = Role.SECOND_ATTACK
        robot3 = Role.MIDDLE
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
        self.add_tactic(robot1, GoToPositionPathfinder(self.game_state, self.game_state.get_player_by_role(robot1), positions_on_xaxis[1], cruise_speed=2))
        self.add_tactic(robot1, GoToPositionPathfinder(self.game_state, self.game_state.get_player_by_role(robot1), positions_on_yaxis[2], cruise_speed=2))
        self.add_condition(robot1, 0, 1, partial(self.condition, robot1))
        self.add_condition(robot1, 1, 0, partial(self.condition, robot1))

        self.add_tactic(robot2, GoToPositionPathfinder(self.game_state, self.game_state.get_player_by_role(robot2), positions_on_xaxis[3], cruise_speed=2))
        self.add_tactic(robot2, GoToPositionPathfinder(self.game_state, self.game_state.get_player_by_role(robot2), positions_on_yaxis[4], cruise_speed=2))
        self.add_condition(robot2, 0, 1, partial(self.condition, robot2))
        self.add_condition(robot2, 1, 0, partial(self.condition, robot2))

        self.add_tactic(robot3, GoToPositionPathfinder(self.game_state, self.game_state.get_player_by_role(robot3), positions_on_xaxis[5], cruise_speed=2))
        self.add_tactic(robot3, GoToPositionPathfinder(self.game_state, self.game_state.get_player_by_role(robot3), positions_on_yaxis[0], cruise_speed=2))
        self.add_condition(robot3, 0, 1, partial(self.condition, robot3))
        self.add_condition(robot3, 1, 0, partial(self.condition, robot3))

        for i in range(PLAYER_PER_TEAM):
            if not (i == robot1 or i == robot2 or i == robot3):
                self.add_tactic(i, Stop(self.game_state, i))

    def condition(self, i):
        try:
            role = self.game_state.get_role_by_player_id(i)
            return self.roles_graph[role].get_current_tactic().status_flag == Flags.SUCCESS
        except:
            return False
        '''
        for k in range(PLAYER_PER_TEAM):
            if not self.tactic_conditions[k]:
                return False
        '''
        return True
