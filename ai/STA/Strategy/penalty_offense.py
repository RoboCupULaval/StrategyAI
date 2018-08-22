# Under MIT license, see LICENSE.txt
from Util.constant import KickForce
from Util.pose import Pose
from Util.role import Role

from ai.STA.Strategy.team_go_to_position import TeamGoToPosition
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.goalkeeper import GoalKeeper
from ai.states.game_state import GameState


class PenaltyOffense(TeamGoToPosition):
    def __init__(self, game_state):
        super().__init__(game_state)

        our_goal = game_state.field.our_goal_pose
        their_goal = game_state.field.their_goal_pose

        role_to_positions = {Role.SECOND_ATTACK:  Pose.from_values(our_goal.position.x / 8, GameState().field.top * 2 / 3),
                             Role.MIDDLE:         Pose.from_values(our_goal.position.x / 8, GameState().field.top / 3),
                             Role.FIRST_DEFENCE:  Pose.from_values(our_goal.position.x / 8, GameState().field.bottom / 3),
                             Role.SECOND_DEFENCE: Pose.from_values(our_goal.position.x / 8, GameState().field.bottom * 2 / 3)}

        kicker = self.assigned_roles[Role.FIRST_ATTACK]
        self.create_node(Role.FIRST_ATTACK, GoKick(game_state, kicker, their_goal, kick_force=KickForce.HIGH))

        goalkeeper = self.assigned_roles[Role.GOALKEEPER]
        self.create_node(Role.GOALKEEPER, GoalKeeper(game_state, goalkeeper, penalty_kick=True))

        self.assign_tactics(role_to_positions)
