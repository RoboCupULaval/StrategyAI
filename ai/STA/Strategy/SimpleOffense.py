# Under MIT license, see LICENSE.txt

from RULEngine.Util.constant import *
from RULEngine.Util.area import player_close_to_ball_facing_target as player_facing_target_with_ball, player_close_to_ball
from RULEngine.Util.geometry import get_angle
from RULEngine.Util.Pose import Pose
from ai.STA.Tactic.GoGetBall import GoGetBall
from ai.STA.Tactic.GoalKeeper import GoalKeeper
from ai.STA.Tactic.GoToPosition import GoToPosition
from ai.STA.Tactic.makePass import MakePass
from ai.STA.Tactic.ReceivePass import ReceivePass
from ai.STA.Tactic.Stop import Stop
from ai.STA.Tactic.RotateAround import RotateAround
from . Strategy import Strategy
from ai.Util.raycast import raycast2

class SimpleOffense(Strategy):
    def __init__(self, p_info_manager):

        self.info_manager = p_info_manager
        self.first_scorer_id = 1
        self.second_scorer_id = 2
        self.unmarked_pose = self.get_unmarked_pose()

        self.tactics =   [GoalKeeper(self.info_manager, 0),
                          GoGetBall(self.info_manager, self.first_scorer_id),
                         GoToPosition(self.info_manager, self.second_scorer_id,self.unmarked_pose),
                         Stop(self.info_manager, 3),
                         Stop(self.info_manager, 4),
                         Stop(self.info_manager, 5)]

        self.set_goal_as_first_target(self.first_scorer_id)
        self.set_goal_as_first_target(self.second_scorer_id)
        self.update_first_scorer_tactic()
        self.update_second_scorer_tactic()

        super().__init__(p_info_manager, self.tactics)

    def update_first_scorer_tactic(self):
        # si le joueur n'a pas la balle, il va la chercher
        if player_close_to_ball(self.info_manager, self.first_scorer_id):
            print(1)

            # si l'orientation n'est pas bonne, on tourne autour de la balle
            if player_facing_target_with_ball(self.info_manager, self.first_scorer_id):
                print(2)

                # si la vue est obstruée, on acquiert une nouvelle target
                scorer_pos = self.info_manager.get_player_position(self.first_scorer_id)
                target = self.info_manager.get_player_target(self.first_scorer_id)
                if not raycast2(self.info_manager, scorer_pos, target, ROBOT_RADIUS,
                           blue_players_ignored=[0,1,2,3,4,5], yellow_players_ignored=[]):
                    print(3)
                    self.tactics[self.first_scorer_id] = MakePass(self.info_manager,
                                                                  self.first_scorer_id)
                else:
                    print("else3")
                    self.info_manager.set_player_target(self.first_scorer_id, self.get_unmarked_position())

            else:
                print("else2")
                self.tactics[self.first_scorer_id] = RotateAround(self.info_manager, self.first_scorer_id)

        else:
            print("else1")
            self.tactics[self.first_scorer_id] = GoGetBall(self.info_manager, self.first_scorer_id)

    def update_second_scorer_tactic(self):

        second_scorer_pose = self.info_manager.get_player_pose(self.second_scorer_id)
        unmarked_pose = self.get_unmarked_pose()

        if second_scorer_pose == unmarked_pose:

            if player_close_to_ball(self.info_manager,self.second_scorer_id):

                if player_facing_target_with_ball(self.info_manager,self.second_scorer_id):

                    self.tactics[self.second_scorer_id] = MakePass(self.info_manager,
                                                                 self.second_scorer_id) # shoot to goal
                else:
                    self.tactics[self.second_scorer_id] = RotateAround(self.info_manager, self.second_scorer_id)

            else:
                self.tactics[self.second_scorer_id] = ReceivePass(self.info_manager,self.second_scorer_id)

        else:
            self.tactics[self.second_scorer_id] = GoToPosition(self.info_manager, self.second_scorer_id,unmarked_pose)

    def set_goal_as_first_target(self, player_id):
        self.null_target = Position(0, 0, 0)
        self.scorer_target = self.info_manager.get_player_target(player_id)
        self.score_in_right_goal = True  # hack: on score toujours a droite. TODO: identifier équipe
        self.goal_x = FIELD_X_RIGHT if self.score_in_right_goal else FIELD_X_LEFT
        self.goal_position = Position(self.goal_x,0)
        try:
            if self.scorer_target == self.null_target:
                self.info_manager.set_player_target(player_id, self.goal_position)
        except:
            self.info_manager.set_player_target(player_id, self.goal_position)

    def get_unmarked_position(self):

        self.unmarked_position = Position(1128,-1400,0) # hardcoded
        return self.unmarked_position

    def get_unmarked_pose(self):
        unmarked_position = self.get_unmarked_position()
        first_scorer_position = self.info_manager.get_player_position(self.first_scorer_id)
        second_scorer_position = self.info_manager.get_player_position(self.second_scorer_id)
        orientation = get_angle(second_scorer_position,first_scorer_position)
        return Pose(unmarked_position,orientation)