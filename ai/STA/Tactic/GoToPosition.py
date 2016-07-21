from ai.STA.Tactic import Tactic
from ai.STA.Action.MoveTo import MoveTo

class GoGetBall(Tactic):
    """
    méthodes:
        exec(self) : Exécute une Action selon l'état courant
    attributs:
        info_manager: référence à la façade InfoManager
        team_id : Identifiant de l'équipe
        player_id : Identifiant du joueur auquel est assigné la tactique
        current_state : chcîne de caratères définissant l'état courant
        next_state : chcîne de caratères définissant l'état suivant
    """

    def __init__(self, info_manager, team_id, player_id, destination_position):
        Tactic.__init__(self, info_manager, team_id, player_id)
        self.current_state = self.move_to_position
        self.next_state = self.move_to_position
        self.player_id = player_id
        self.destination_position = destination_position

    def move_to_position(self):
        player_position = self.info_manager.get_player_position(self.player_id)

        if player_position == self.destination_position:
                self.next_state = self.halt
        else:
            self.next_state = self.move_to_position

        move_to = MoveTo(self.info_manager, self.player_id, self.destination_position)
        return move_to