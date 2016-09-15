# Under MIT license, see LICENSE.txt

from RULEngine.Util.constant import *
from ai.STA.Tactic.GoGetBall import GoGetBall
from ai.STA.Tactic.GoalKeeper import GoalKeeper
from ai.STA.Tactic.shootToGoal import ShootToGoal
from ai.STA.Tactic.CoverZone import CoverZone
from ai.STA.Tactic.Stop import Stop
from . Strategy import Strategy
from RULEngine.Util.area import player_grabbed_ball
from RULEngine.Util.geometry import player_in_the_way
from ai.STA.Tactic.makePass import MakePass
from ai.STA.Tactic.ReceivePass import ReceivePass
from RULEngine.Util.Pose import Pose

# stratégie: un tente de scorer, les autres couvrent en offense
# on envoie un joueur a un endroit stratégique si le but est bloqué, et on lui fait une passe

class SimpleOffense(Strategy):
    def __init__(self, p_info_manager):

        self.info_manager = p_info_manager
        self.score_in_right_goal = True # hack: on score toujours a droite. TODO: identifier équipe
        self.designated_scorer_id = 1
        self.position_demarquee = Position(1128,-1400,0) # hardcoded

        self.goal_x = FIELD_X_RIGHT if self.score_in_right_goal else FIELD_X_LEFT
        self.goal_position = Position(self.goal_x, 0)

        self.info_manager.set_player_target(self.designated_scorer_id,self.goal_position)

        self.tactics =   [GoalKeeper(self.info_manager, 0),
                     GoGetBall(self.info_manager, self.designated_scorer_id),
                     CoverZone(self.info_manager, 2, FIELD_Y_TOP, 0, FIELD_X_RIGHT / 2, FIELD_X_RIGHT),
                     CoverZone(self.info_manager, 3, 0, FIELD_Y_BOTTOM, FIELD_X_RIGHT / 2, FIELD_X_RIGHT),
                     CoverZone(self.info_manager, 4, FIELD_Y_TOP, 0, 0, FIELD_X_RIGHT / 2),
                     CoverZone(self.info_manager, 5, 0, FIELD_Y_BOTTOM, 0, FIELD_X_RIGHT / 2)]

        self.check_if_can_score_ball()

        super().__init__(self.info_manager, self.tactics)

    # TODO: discussion d'architecture: on ne veut sûrement pas conserver notre sélecteur de tactiques par stratégie ici
    def check_if_can_score_ball(self):
        # si le scorer principal a la balle
        if player_grabbed_ball(self.info_manager, self.designated_scorer_id):
            self.scorer_pos = self.info_manager.get_player_position(self.designated_scorer_id)
            # si aucun joueur ne bloque la vue
            if player_in_the_way(self.info_manager,self.scorer_pos,self.goal_position,
                                 id_to_ignore=self.designated_scorer_id) is None:
                # alors tir au but
                self.tactics[self.designated_scorer_id] = ShootToGoal(self.info_manager, self.designated_scorer_id, self.score_in_right_goal)
            else:
                # le joueur attend
                self.tactics[self.designated_scorer_id] = Stop(self.info_manager, self.designated_scorer_id)
        else:
            # sinon le scorer va chercher la balle
            self.tactics[self.designated_scorer_id] = GoGetBall(self.info_manager, self.designated_scorer_id)