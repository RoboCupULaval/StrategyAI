# Under MIT licence, see LICENCE.txt

from ai.STA.Tactic import Tactic
from ai.STA.Action import Kick
from ai.STA.Action import Idle
from RULEngine.Util.area import player_grabbed_ball
from RULEngine.Util.geometry import get_required_kick_force

__author__ = 'RoboCupULaval'


class MakePass(Tactic):
    """
    méthodes:
        exec(self) : Exécute une Action selon l'état courant
    attributs:
        info_manager: référence à la façade InfoManager
        player_id : Identifiant du joueur auquel est assigné la tactique
        current_state : chcîne de caratères définissant l'état courant
        next_state : chcîne de caratères définissant l'état suivant
    """

    def __init__(self, info_manager, player_id):
        Tactic.__init__(self, info_manager)
        assert isinstance(player_id, int)

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
            return kick_ball

        else: # returns error, strategy goes back to GoGetBall
            self.next_state = self.halt
            # TODO : Mettre flag d'état à failed
            return Idle(self.info_manager, self.player_id)



