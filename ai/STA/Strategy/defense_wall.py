# Under MIT license, see LICENSE.txt
from functools import partial

from Util.role import Role
from Util.position import Position
from Util.pose import Pose
from Util.role_mapping_rule import keep_prev_mapping_otherwise_random

from ai.Algorithm.evaluation_module import closest_players_to_point
from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.align_to_defense_wall import AlignToDefenseWall
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.go_to_position_pathfinder import GoToPositionPathfinder
from ai.STA.Tactic.goalkeeper import GoalKeeper
from ai.STA.Tactic.stop import Stop
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState


# noinspection PyMethodMayBeStatic,
class DefenseWall(Strategy):
    DEFENSIVE_ROLE = [Role.MIDDLE, Role.FIRST_DEFENCE, Role.SECOND_DEFENCE]

    def __init__(self, game_state: GameState):
        super().__init__(game_state)

        their_goal = self.game_state.field.their_goal_pose

        self.robots_in_formation = [p for r, p in self.assigned_roles.items() if r in self.DEFENSIVE_ROLE]
        for role, player in self.assigned_roles.items():
            if role == Role.GOALKEEPER:
                self.create_node(Role.GOALKEEPER, GoalKeeper(self.game_state, player))
            elif role == Role.FIRST_ATTACK or role == Role.SECOND_ATTACK:
                node_stop = self.create_node(role, Stop(self.game_state, player))
                node_go_kick = self.create_node(role, GoKick(self.game_state, player, target=their_goal))

                player_is_closest = partial(self.is_closest, player)
                player_is_not_closest = partial(self.is_not_closest, player)

                node_stop.connect_to(node_go_kick, when=player_is_closest)
                node_go_kick.connect_to(node_stop, when=player_is_not_closest)
            else:
                node_align_to_defense_wall = \
                    self.create_node(role, AlignToDefenseWall(self.game_state,
                                                              player,
                                                              robots_in_formation=self.robots_in_formation))
                node_go_kick = self.create_node(role, GoKick(self.game_state, player, target=their_goal))

                player_is_closest = partial(self.is_closest, player)
                player_is_not_closest = partial(self.is_not_closest, player)

                # TODO: just for test, uncomment later
                #node_align_to_defense_wall.connect_to(node_go_kick, when=player_is_closest)
                #node_go_kick.connect_to(node_go_kick, when=player_is_closest)
                #node_go_kick.connect_to(node_align_to_defense_wall, when=player_is_not_closest)

    @classmethod
    def required_roles(cls):
        return {r: keep_prev_mapping_otherwise_random for r in [Role.GOALKEEPER,
                                                                Role.FIRST_ATTACK,
                                                                Role.SECOND_ATTACK,
                                                                Role.MIDDLE,
                                                                Role.FIRST_DEFENCE,
                                                                Role.SECOND_DEFENCE]
                }

    @staticmethod
    def is_closest(player):
        return player == closest_players_to_point(GameState().ball_position, True)[0].player

    @staticmethod
    def is_second_closest(player):
        return player == closest_players_to_point(GameState().ball_position, True)[1].player

    def is_not_closest(self, player):
        return not self.is_closest(player)

    def is_not_one_of_the_closest(self, player):
        return not self.is_closest(player) or self.is_second_closest(player)

    def has_kicked(self, player):
        role = GameState().get_role_by_player_id(player.id)
        if self.roles_graph[role].current_tactic_name == 'GoKick':
            return self.roles_graph[role].current_tactic.status_flag == Flags.SUCCESS
        else:
            return False
