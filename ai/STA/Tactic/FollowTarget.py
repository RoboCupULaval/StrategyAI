from ai.STA.Tactic import Tactic


class FollowTarget(Tactic):
    """
    Classe mère de toutes les tactiques
    méthodes:
        exec(self) : Exécute une Action selon l'état courant
        dispatch(self) : Trouve la fonction qui calcul le prochain état. est appelé après exec().
    attributs:
        info_manager: référence à la façade InfoManager
        team_id : Identifiant de l'équipe
        player_id : Identifiant du joueur auquel est assigné la tactique
        current_state : chcîne de caratères définissant l'état courant
        next_state : chcîne de caratères définissant l'état suivant
    """

    def __init__(self, game_state, team_id, player_id):
        Tactic.__init__(self, game_state, team_id, player_id)
        self.current_state = 'halt'
        self.next_state = 'halt'
        self.dispatch.update({'follow_ball': self.follow_ball, 'follow_next_player': self.follow_next_player})

    def halt(self):
        dist_ball_player1 = self.game_state.get_player_position(0) - self.game_state.get_ball_position()
        if len(dist_ball_player1) < 20:
            self.next_state = 'halt'
        else:
            if self.player_id == 0:
                self.next_state = 'follow_ball'
            else:
                self.next_state = 'follow_next_player'

    def follow_ball(self):
        if self.player_id == 0:
            self.next_state = 'follow_ball'
        else:
            self.next_state = 'follow_next_player'

    def follow_next_player(self):
        if self.player_id == 0:
            self.next_state = 'follow_ball'
        else:
            self.next_state = 'follow_next_player'
