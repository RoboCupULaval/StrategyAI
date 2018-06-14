# Under MIT licence, see LICENCE.txt
from typing import List, Optional, Any, Iterable

import logging

from Util import Pose, Position
from Util.ai_command import AICommand
from Util.constant import ROBOT_RADIUS, KEEPOUT_DISTANCE_FROM_GOAL
from Util.geometry import Area, Line
from ai.GameDomainObjects import Player
from Util.ai_command import Idle
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState

__author__ = 'RobocupULaval'


class Tactic:

    def __init__(self, game_state: GameState, player: Player, target: Optional[Pose]=None,
                 args: Optional[List[Any]]=None, forbidden_areas: Optional[List[Area]]=None):
        self.logger = logging.getLogger(self.__class__.__name__)

        assert isinstance(player, Player), "Le player doit être un Player, non un '{}'".format(player)
        assert target is None or isinstance(target, Pose), "La target devrait être une Pose"
        self.game_state = game_state
        self.player = player
        self.player_id = player.id
        if args is None:
            self.args = []
        else:
            self.args = args

        self.current_state = self.halt
        self.next_state = self.halt
        self.status_flag = Flags.INIT
        self.target = target

        if forbidden_areas is None:
            field = self.game_state.field

            top_area = Area.from_limits(field.top + 100 * field.boundary_width,
                                        field.top + field.boundary_width,
                                        field.right,
                                        field.left)
            bottom_area = Area.from_limits(field.bottom - field.boundary_width,
                                           field.bottom - 100 * field.boundary_width,
                                           field.right,
                                           field.left)
            right_area = Area.from_limits(field.top,
                                           field.bottom,
                                           field.right + 100 * field.boundary_width,
                                           field.right + field.boundary_width)
            left_area = Area.from_limits(field.top,
                                         field.bottom,
                                         field.left - field.boundary_width,
                                         field.left - 100 * field.boundary_width)
            areas = [
                top_area,
                bottom_area,
                right_area,
                left_area,
                self.game_state.field.their_goal_area,
                self.game_state.field.our_goal_area]
            self.forbidden_areas = [Area.pad(area, KEEPOUT_DISTANCE_FROM_GOAL) for area in areas]
        else:
            self.forbidden_areas = forbidden_areas

    def halt(self) -> Idle:
        self.next_state = self.halt
        return Idle

    def exec(self) -> AICommand:
        next_ai_command = self.current_state()
        if not isinstance(next_ai_command, AICommand):
            raise RuntimeError("A tactic MUST return an AICommand, not a {}. {} is the culprit.".format(type(next_ai_command), self.current_state))
        self.current_state = self.next_state

        if next_ai_command.target:
            next_ai_command = self._check_for_forbidden_area(next_ai_command)

        return next_ai_command

    def _check_for_forbidden_area(self, next_ai_command):
        old_target_position = next_ai_command.target.position
        target_to_position = Line(self.player.position, next_ai_command.target.position)
        for area in self.forbidden_areas:
            if old_target_position in area:
                target_position = self._find_best_next_target(area, old_target_position, self.player.position, target_to_position)
                new_target = Pose(target_position, next_ai_command.target.orientation)

                # This trailing _ is not for protected access, it was add to avoid a name conflict with the function replace ;)
                return next_ai_command._replace(target=new_target)
        return next_ai_command

    def _find_best_next_target(self, area: Area, old_target_position, player_position: Position, target_to_position: Line):
        intersections = area.intersect(target_to_position)
        if intersections:
            return intersections[0]
        elif old_target_position == player_position:
            return area.closest_border_point(old_target_position)
        else:  # The player is already in the forbidden area, so it must go in the opposite direction than the target
            intersections = area.intersect_with_line(target_to_position)
            if (intersections[0] - self.player.position).norm < (intersections[1] - self.player.position).norm:
                return intersections[0]
            else:
                return intersections[1]

    def debug_cmd(self):
        return []

    @classmethod
    def name(cls):
        return cls.__name__

    def __str__(self):
        return self.__class__.__name__
