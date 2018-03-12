# Under MIT licence, see LICENCE.txt
from typing import List

from Util import Pose, Position
from Util.area import isInsideSquare, stayInsideSquare
from Util.constant import ROBOT_RADIUS
from ai.GameDomainObjects import Player
from ai.STA.Action.GoBetween import GoBetween
from Util.ai_command import Idle
from ai.STA.Action.MoveToPosition import MoveToPosition
from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState

__author__ = 'RoboCupULaval'


class ProtectZone(Tactic):
    """
    méthodes:
        exec(self) : Exécute une Action selon l'état courant
    attributs:
        game_state: L'état courant du jeu
        player: Instance du joueur à qui la tactique est assignée
        y_top : La limite supérieur de la zone
        y_bottom : La limite inférieur de la zone
        x_left : La limite de gauche de la zone
        x_right : La limite de droite de la zone
        is_yellow : Un booléen indiquant si le joueur fait parti de l'équipe des jaunes, dont la zone défensive est la
        moitié droite du terrain.
        current_state : L'état courant de la tactique
        next_state : L'état suivant de la tactique
        status_flag : L'indicateur de progression de la tactique
    """

    def __init__(self, game_state: GameState, player: Player, target: Pose=Pose(), args: List[str]=None,
                 p_y_top: [int, float]=3000, p_y_bottom: [int, float]=-3000, p_x_left: [int, float]=-4500,
                 p_x_right: [int, float]=4500, p_is_yellow: bool=False):
        super().__init__(game_state, player, target, args)
        assert isinstance(p_y_top, (int, float))
        assert isinstance(p_y_bottom, (int, float))
        assert isinstance(p_x_left, (int, float))
        assert isinstance(p_x_right, (int, float))
        assert isinstance(p_is_yellow, bool)
        self.y_top = p_y_top
        self.y_bottom = p_y_bottom
        self.x_left = p_x_left
        self.x_right = p_x_right
        self.is_yellow = p_is_yellow
        self.current_state = self.cover_zone
        self.next_state = self.cover_zone
        self.status_flag = Flags.WIP
        self.target = Pose(Position(int((p_x_right - p_x_left)/2), int((p_y_top - p_y_bottom)/2)))

    def cover_zone(self):
        enemy_positions = self.get_enemy_in_zone()
        ball_pos = self.game_state.ball_position

        if len(enemy_positions) == 0:
            self.next_state = self.support_other_zone
            return Idle(self.game_state, self.player)
        else:
            self.next_state = self.cover_zone

        mean_position = Position()
        for pos in enemy_positions:
            mean_position = mean_position + pos
        mean_position /= len(enemy_positions)
        destination = stayInsideSquare(mean_position, self.y_top, self.y_bottom, self.x_left, self.x_right)
        return GoBetween(self.game_state, self.player, ball_pos, destination, ball_pos, 2*ROBOT_RADIUS)

    def support_other_zone(self):
        enemy_positions = self.get_enemy_in_zone()

        if len(enemy_positions) == 0:
            self.next_state = self.support_other_zone
        else:
            self.next_state = self.cover_zone

        destination = stayInsideSquare(self.game_state.ball_position, self.y_top, self.y_bottom, self.x_left,
                                       self.x_right)
        destination = self.game_state.game.field.stay_outside_goal_area(destination, our_goal=True)
        orientation = (self.game_state.ball_position - destination).angle
        return MoveToPosition(self.game_state, self.player, Pose(destination, orientation))

    def get_enemy_in_zone(self):
        enemy_list = []
        for robot in self.game_state.game.enemies.values():
            pos = self.game_state.get_player_position(robot, False)
            if isInsideSquare(pos, self.y_top, self.y_bottom, self.x_left, self.x_right):
                enemy_list.append(pos)
        return enemy_list
