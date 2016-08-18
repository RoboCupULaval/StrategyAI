# Under MIT licence, see LICENCE.txt

from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic import tactic_constants
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

    def __init__(self, info_manager, player_id):
        Tactic.__init__(self, info_manager)
        assert isinstance(player_id, int)
        assert PLAYER_PER_TEAM >= player_id >= 0

        self.current_state = self.kick_ball_towards_target
        self.next_state = self.kick_ball_towards_target
        self.player_id = player_id
        self.target = self.info_manager.get_player_target(self.player_id)

    def kick_ball_towards_target(self):
        if player_grabbed_ball(self.info_manager, self.player_id):  # derniere verification avant de frapper
            player_position = self.info_manager.get_player_position(self.player_id)
            target_position = self.info_manager.get_player_target(self.player_id)
            kick_force = get_required_kick_force(player_position, target_position)

            kick_ball = Kick(self.info_manager, self.player_id, kick_force)

            self.next_state = self.halt
            self.status_flag = tactic_constants.WIP
            return kick_ball

        else: # returns error, strategy goes back to GoGetBall
            self.next_state = self.halt
            self.status_flag = tactic_constants.FAILURE
            return Idle(self.info_manager, self.player_id)



