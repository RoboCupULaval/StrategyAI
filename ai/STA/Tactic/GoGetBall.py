from ai.STA.Tactic import Tactic
from ai.STA.Action.GoBehind import GoBehind
from ai.STA.Action.GrabBall import GrabBall
from RULEngine.Util.area import player_can_grab_ball, player_grabbed_ball
from RULEngine.Util.constant import DISTANCE_BEHIND

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
        future_target: position à laquelle faire face après avoir pris la balle
    """

    def __init__(self, info_manager, team_id, player_id, future_target):
        Tactic.__init__(self, info_manager)
        self.team_id = team_id
        self.player_id = player_id
        self.current_state = self.get_behind_ball
        self.next_state = self.get_behind_ball
        self.target = info_manager.get_player_target


    def get_behind_ball(self):
        ball_position = self.info_manager.get_ball_position()

        if player_can_grab_ball:
                self.next_state = self.grab_ball
        else:
            self.next_state = self.get_behind_ball

        go_behind = GoBehind(self.info_manager, self.player_id, ball_position, self.future_target, DISTANCE_BEHIND)
        return go_behind

    def grab_ball(self):

        if player_grabbed_ball():
            self.next_state = self.halt
        elif player_can_grab_ball():
            self.next_state = self.get_behind_ball # back to go_behind; the ball has moved
        else:
            self.next_state = self.grab_ball

        grab_ball = GrabBall(self.info_manager,self.player_id)
        return grab_ball