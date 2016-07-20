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
        self.future_target = future_target # TODO: implémenter la target du info_manager lorsque le conflit entre target et goal sera résolu
        # constants
        self.robot_radius = 90
        self.distance_behind = self.robot_radius + 30 # in millimeters
        self.tolerated_angle_to_go_grab_ball = 1 # in radians; must be large in case ball moves fast
        self.tolerated_radius_to_go_grab_ball = self.robot_radius + 30
        self.tolerated_angle_to_halt = 0.09
        self.tolerated_radius_to_halt = self.robot_radius + 5

    # Util methods TODO: mettre dans Util si utiles dans d'autres cas
    def angle_to_ball_is_tolerated(self, player_position, ball_position, angle_to_verify):
        angle_player_to_ball = get_angle(player_position, ball_position)
        angle_ball_to_target = get_angle(ball_position, self.future_target)
        angle_difference = abs(angle_player_to_ball - angle_ball_to_target)
        if angle_difference < angle_to_verify:
            return True
        return False

    def player_can_grab_ball(self):
        player_position = self.info_manager.get_player_position(self.player_id)
        ball_position = self.info_manager.get_ball_position()

        if isInsideCircle(ball_position, ball_position, self.tolerated_radius_to_go_grab_ball):

            if self.angle_to_ball_is_tolerated(player_position, ball_position, self.tolerated_angle_to_go_grab_ball):
                return True

        return False

    def player_grabbed_ball(self):
        player_position = self.info_manager.get_player_position(self.player_id)
        ball_position = self.info_manager.get_ball_position()

        if player_position.isInsideCircle(ball_position, ball_position, self.tolerated_radius_to_halt):

            if self.angle_to_ball_is_tolerated(player_position, ball_position, self.tolerated_angle_to_halt):
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

        if self.player_grabbed_ball():
            self.next_state = self.halt
        elif self.player_can_grab_ball():
            self.next_state = self.get_behind_ball # back to go_behind; the ball has moved
        else:
            self.next_state = self.grab_ball

        grab_ball = GrabBall(self.info_manager,self.player_id)
        return grab_ball