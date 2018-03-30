# Under MIT licence, see LICENCE.txt
from Util import Pose, Position, AICommand
from Util.ai_command import MoveTo
from Util.area import stayInsideCircle
from Util.geometry import closest_point_on_segment
from ai.GameDomainObjects import Player
from ai.STA.Action import Action
from ai.states.game_state import GameState


def ProtectGoal(game_state: GameState, player: Player, is_right_goal: bool=True,
                 minimum_distance: [int, float]=150 / 2, maximum_distance: [int, float, None]=None):

        """
        Calcul la pose que doit prendre le gardien en fonction de la position de la balle.
        :return: Un tuple (Pose, kick) où Pose est la destination du gardien et kick est nul (on ne botte pas)
        """
        goalkeeper_position = player.pose.position
        ball_position = game_state.ball_position
        goal_x = game_state.const["FIELD_OUR_GOAL_X_EXTERNAL"]
        goal_position = Position(goal_x, 0)

        # Calcul des deux positions extremums entre la balle et le centre du but
        inner_circle_position = stayInsideCircle(ball_position, goal_position, minimum_distance)
        outer_circle_position = stayInsideCircle(ball_position, goal_position, maximum_distance)

        destination_position = closest_point_on_segment(goalkeeper_position,
                                                        inner_circle_position,
                                                        outer_circle_position)

        # Vérification que destination_position respecte la distance maximale
        if maximum_distance is None:
            destination_position = self.game_state.game.field.stay_inside_goal_area(destination_position,
                                                                                    our_goal=True)
        else:
            destination_position = stayInsideCircle(destination_position, goal_position, maximum_distance)

        # Calcul de l'orientation de la pose de destination
        destination_orientation = (ball_position - destination_position).angle

        destination_pose = Pose(destination_position, destination_orientation)
        return MoveTo(destination_pose)
