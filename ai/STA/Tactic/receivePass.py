from ai.STA.Tactic import Tactic
from ai.STA.Action import MoveTo
from RULEngine.Util.area import player_grabbed_ball
from RULEngine.Util.Pose import Pose
from RULEngine.Util.geometry import get_angle

class makePass(Tactic):
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

    def __init__(self, info_manager, team_id, player_id):
        Tactic.__init__(self, info_manager, team_id, player_id)
        self.current_state = self.rotate_towards_ball
        self.next_state = self.rotate_towards_ball
        self.player_id = player_id

    def rotate_towards_ball(self):

        if player_grabbed_ball():
            self.next_state = self.halt
            return 0 # what to return here?
        else: # keep rotating
            current_position = self.info_manager.get_player_position()
            ball_position = self.info_manager.get_ball_position()

            rotation_towards_ball = get_angle(current_position,ball_position)
            pose_towards_ball = Pose(current_position,rotation_towards_ball)

            move_to = MoveTo(self.info_manager,self.player_id,pose_towards_ball)
            self.next_state = self.rotate_towards_ball
            return move_to