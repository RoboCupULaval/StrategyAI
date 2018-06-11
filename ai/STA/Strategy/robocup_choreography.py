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

        node_robot1_go_to_x = self.create_node(robot1, GoToPositionPathfinder(self.game_state, self.assigned_roles[robot1], positions_on_xaxis[1], cruise_speed=2))
        node_robot1_go_to_y = self.create_node(robot1, GoToPositionPathfinder(self.game_state, self.assigned_roles[robot1], positions_on_yaxis[2], cruise_speed=2))
        robot_1_succeeded = partial(self.current_tactic_succeed, robot1)

        node_robot1_go_to_x.connect_to(node_robot1_go_to_y, when=robot_1_succeeded)
        node_robot1_go_to_y.connect_to(node_robot1_go_to_x, when=robot_1_succeeded)

        node_robot_2_go_to_x = self.create_node(robot2, GoToPositionPathfinder(self.game_state, self.assigned_roles[robot2], positions_on_xaxis[3], cruise_speed=2))
        node_robot_2_go_to_y = self.create_node(robot2, GoToPositionPathfinder(self.game_state, self.assigned_roles[robot2], positions_on_yaxis[4], cruise_speed=2))
        robot2_succeeded = partial(self.current_tactic_succeed, robot2)

        node_robot_2_go_to_x.connect_to(node_robot_2_go_to_y, when=robot2_succeeded)
        node_robot_2_go_to_y.connect_to(node_robot_2_go_to_x, when=robot2_succeeded)

        node_robot3_go_to_x = self.create_node(robot3, GoToPositionPathfinder(self.game_state, self.assigned_roles[robot3], positions_on_xaxis[5], cruise_speed=2))
        node_robot3_go_to_y = self.create_node(robot3, GoToPositionPathfinder(self.game_state, self.assigned_roles[robot3], positions_on_yaxis[0], cruise_speed=2))
        robot3_succeeded = partial(self.current_tactic_succeed, robot3)

        node_robot3_go_to_x.connect_to(node_robot3_go_to_y, when=robot3_succeeded)
        node_robot3_go_to_y.connect_to(node_robot3_go_to_x, when=robot3_succeeded)

    def current_tactic_succeed(self, role):
        try:
            tactic = self.roles_graph[role].current_tactic
            return tactic is not None and tactic.status_flag == Flags.SUCCESS
        except IndexError:
            return False

    @classmethod
    def required_roles(cls):
        return [Role.FIRST_ATTACK,
                Role.SECOND_ATTACK,
                Role.MIDDLE]
