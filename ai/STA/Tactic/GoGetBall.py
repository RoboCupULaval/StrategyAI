# Under MIT licence, see LICENCE.txt

from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Action.GoBehind import GoBehind
from ai.STA.Action.GrabBall import GrabBall
from RULEngine.Util.area import player_can_grab_ball, player_grabbed_ball
from RULEngine.Util.constant import DISTANCE_BEHIND, PLAYER_PER_TEAM
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position

__author__ = 'RoboCupULaval'


class GoGetBall(Tactic):
    """
    méthodes:
        exec(self) : Exécute une Action selon l'état courant
    attributs:
        info_manager: référence à la façade InfoManager
        player_id : Identifiant du joueur auquel est assigné la tactique
        current_state : L'état courant de la tactique
        next_state : L'état suivant de la tactique
        target: Position à laquelle faire face après avoir pris la balle
    """

    def __init__(self, info_manager, player_id):
        Tactic.__init__(self, info_manager)
        assert isinstance(player_id, int)
        assert PLAYER_PER_TEAM >= player_id >= 0

        self.player_id = player_id
        self.current_state = self.get_behind_ball
        self.next_state = self.get_behind_ball
        self.target = self.info_manager.get_player_target(player_id)
        # FIXME: hack
        if self.target is None:
            self.target = self.info_manager.get_ball_position()
            self.info_manager.set_player_target(self.player_id, self.target)

    def get_behind_ball(self):
        ball_position = self.info_manager.get_ball_position()

        if player_can_grab_ball(self.info_manager, self.player_id):
            self.next_state = self.grab_ball
        else:
            self.next_state = self.get_behind_ball

        go_behind = GoBehind(self.info_manager, self.player_id, ball_position, self.target, DISTANCE_BEHIND)
        return go_behind

    def grab_ball(self):
        if player_grabbed_ball(self.info_manager, self.player_id):
            self.next_state = self.halt
        elif player_can_grab_ball(self.info_manager, self.player_id):
            self.next_state = self.grab_ball
        else:
            self.next_state = self.get_behind_ball  # back to go_behind; the ball has moved

        grab_ball = GrabBall(self.info_manager,self.player_id)
        return grab_ball
