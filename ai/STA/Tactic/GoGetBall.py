from . import Tactic
from ai.STA.Action.GoBehind import GoBehind
from ai.STA.Action.GrabBall import GrabBall
from RULEngine.Util.geometry import get_angle
from RULEngine.Util.area import isInsideCircle

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
        Tactic.__init__(self, info_manager, team_id, player_id)
        self.current_state = self.get_behind_ball
        self.next_state = self.get_behind_ball
        self.player_id = player_id
        self.future_target = future_target
        self.distance_behind = 20 # amount of pixels to go to behind ball
        self.tolerated_angle_difference = 1 # in radians
        self.tolerated_radius_to_go_grab_ball = 20
        self.tolerated_radius_to_halt = 5

    # Util methods
    # TODO: mettre dans Util si utile dans d'autres cas
    def player_can_grab_ball(self):
        player_position = self.info_manager.get_player_position(self.player_id)
        ball_position = self.info_manager.get_ball_position()

        if isInsideCircle(ball_position, ball_position, self.tolerated_radius_to_go_grab_ball):
            angle_player_to_ball = get_angle(player_position, ball_position)
            angle_ball_to_target = get_angle(ball_position, self.future_target)
            angle_difference = abs(angle_player_to_ball - angle_ball_to_target)

            if angle_difference < self.tolerated_angle_difference:
                return True

        return False

    def player_grabbed_ball(self):
        player_position = self.info_manager.get_player_position(self.player_id)
        ball_position = self.info_manager.get_ball_position()

        if player_position.isInsideCircle(ball_position, ball_position, self.tolerated_radius_to_halt):
            return True
        return False

    # States

    def get_behind_ball(self):
        ball_position = self.info_manager.get_ball_position()

        if self.player_can_grab_ball:
                self.next_state = self.grab_ball
        else:
            self.next_state = self.get_behind_ball

        go_behind = GoBehind(self.info_manager, self.player_id, ball_position, self.future_target, self.distance_behind)
        return go_behind

    def grab_ball(self):
        player_position = self.info_manager.get_player_position(self.player_id)
        ball_position = self.info_manager.get_ball_position()

        if self.player_grabbed_ball():
            self.next_state = self.halt
        elif self.player_can_grab_ball():
            self.next_state = self.get_behind_ball # back to go_behind; the ball has moved
        else:
            self.next_state = self.grab_ball

        grab_ball = GrabBall(self.info_manager,self.player_id)
        return grab_ball