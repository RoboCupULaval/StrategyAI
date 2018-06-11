# Under MIT license, see LICENSE.txt


from Util import Position, Pose
from Util.constant import ROBOT_RADIUS
from Util.role import Role
from ai.STA.Strategy.team_go_to_position import TeamGoToPosition
from ai.states.game_state import GameState


class LineUp(TeamGoToPosition):
    def __init__(self, game_state: GameState):
        super().__init__(game_state)

        self.target_position = Position(self.game_state.field.our_goal_area.left - 3*ROBOT_RADIUS, 0)

        number_of_player = len(self.game_state.our_team.available_players)

        role_to_positions = {}
        for i, role in enumerate(Role.as_list()):
            position_offset = Position(0, (i-(number_of_player-1)/2) * ROBOT_RADIUS * 4)
            role_to_positions[role] = Pose(self.target_position + position_offset)

        self.assign_tactics(role_to_positions)

    @classmethod
    def required_roles(cls):
        return []

    @classmethod
    def optional_roles(cls):
        return Role.as_list()
