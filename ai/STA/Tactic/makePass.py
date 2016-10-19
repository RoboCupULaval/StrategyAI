# Under MIT licence, see LICENCE.txt

from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.STA.Action.Kick import Kick
from ai.STA.Action.Idle import Idle
from RULEngine.Util.area import player_grabbed_ball
from RULEngine.Util.geometry import get_required_kick_force
from RULEngine.Util.constant import PLAYER_PER_TEAM

__author__ = 'RoboCupULaval'


class MakePass(Tactic):
    # TODO : vérifier que la balle a été bottée avant de retourner à halt
    """
    méthodes:
        exec(self) : Exécute une Action selon l'état courant
    attributs:
        info_manager: référence à la façade InfoManager
        player_id : Identifiant du joueur auquel est assigné la tactique
        current_state : L'état courant de la tactique
        next_state : L'état suivant de la tactique
        status_flag : L'indicateur de progression de la tactique
    """

    def __init__(self, game_state, player_id):
        Tactic.__init__(self, game_state, player_id)
        assert isinstance(player_id, int)
        assert PLAYER_PER_TEAM >= player_id >= 0

        self.current_state = self.kick_ball_towards_target
        self.next_state = self.kick_ball_towards_target
        self.player_id = player_id
        self.target = self.game_state.get_player_target(self.player_id)

    def kick_ball_towards_target(self):
        if player_grabbed_ball(self.game_state, self.player_id):  # derniere verification avant de frapper
            player_position = self.game_state.get_player_position(self.player_id)
            target_position = self.game_state.get_player_target(self.player_id)
            kick_force = get_required_kick_force(player_position, target_position)

            kick_ball = Kick(self.game_state, self.player_id, kick_force)

            self.next_state = self.halt
            self.status_flag = Flags.WIP
            return kick_ball

        else: # returns error, strategy goes back to GoGetBall
            self.next_state = self.halt
            self.status_flag = Flags.FAILURE
            return Idle(self.game_state, self.player_id)



