# Under MIT licence, see LICENCE.txt

from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Action.Kick import Kick
from ai.STA.Action.Idle import Idle
from ai.STA.Tactic.tactic_constants import Flags
from ai.Util.ball_possession import hasBallFacingTarget
from RULEngine.Util.kick import getRequiredKickForce
from RULEngine.Util.constant import PLAYER_PER_TEAM, FIELD_X_LEFT, FIELD_X_RIGHT
from RULEngine.Util.Position import Position

__author__ = 'RoboCupULaval'


class ShootGoal(Tactic):
    # TODO : vérifier que la balle a été bottée avant de retourner à halt
    """
    méthodes:
        exec(self) : Exécute une Action selon l'état courant
    attributs:
        info_manager: référence à la façade InfoManager
        player_id : Identifiant du joueur auquel est assigné la tactique
        current_state : L'état courant de la tactique
        next_state : L'état suivant de la tactique
    """

    def __init__(self, info_manager, player_id, p_score_in_right_goal):
        Tactic.__init__(self, info_manager)
        assert isinstance(player_id, int)
        assert PLAYER_PER_TEAM >= player_id >= 0

        self.current_state = self.kick_ball_towards_goal
        self.next_state = self.kick_ball_towards_goal
        self.player_id = player_id
        self.score_in_right_goal = p_score_in_right_goal

    def kick_ball_towards_goal(self):
        goal_x = FIELD_X_RIGHT if self.score_in_right_goal else FIELD_X_LEFT
        goal_position = Position(goal_x, 0)
        if hasBallFacingTarget(self.info_manager, self.player_id, point=self.game_state.get_ball_position()):  # derniere verification avant de frapper
            player_position = self.info_manager.get_player_position(self.player_id)
            kick_force = getRequiredKickForce(player_position, goal_position)
            kick_ball = Kick(self.info_manager, self.player_id, kick_force)
            self.status_flag = Flags.SUCCESS
            self.next_state = self.halt
            return kick_ball

        else: # returns error, strategy goes back to GoGetBall
            self.next_state = self.halt
            self.status_flag = Flags.FAILURE
            return Idle(self.info_manager, self.player_id)