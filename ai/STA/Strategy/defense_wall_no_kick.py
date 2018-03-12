# Under MIT license, see LICENSE.txt

from Util.role import Role
from Util.position import Position
from Util.pose import Pose
from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.align_to_defense_wall import AlignToDefenseWall
from ai.STA.Tactic.goalkeeper import GoalKeeper
from ai.states.game_state import GameState


class DefenseWallNoKick(Strategy):
    def __init__(self, game_state: GameState, number_of_players: int = 4):
        super().__init__(game_state)
        self.number_of_players = number_of_players
        self.robots = []
        ourgoal = Pose(Position(GameState().const["FIELD_OUR_GOAL_X_EXTERNAL"], 0), 0)
        self.theirgoal = Pose(Position(GameState().const["FIELD_THEIR_GOAL_X_EXTERNAL"], 0), 0)

        roles_to_consider = [Role.FIRST_ATTACK, Role.SECOND_ATTACK, Role.MIDDLE,
                             Role.FIRST_DEFENCE, Role.SECOND_DEFENCE]

        goalkeeper = self.game_state.get_player_by_role(Role.GOALKEEPER)

        self.add_tactic(Role.GOALKEEPER, GoalKeeper(self.game_state, goalkeeper, ourgoal))

        role_by_robots = [(i, self.game_state.get_player_by_role(i)) for i in roles_to_consider]
        self.robots = [player for _, player in role_by_robots if player is not None]
        for role, player in role_by_robots:
            if player:
                self.add_tactic(role, AlignToDefenseWall(self.game_state, player, self.robots))
