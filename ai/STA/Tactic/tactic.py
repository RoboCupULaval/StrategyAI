# Under MIT licence, see LICENCE.txt
from typing import List, Optional, Any, Iterable

from Util import Pose
from Util.ai_command import AICommand
from Util.geometry import Area, position_outside_area, Line
from ai.GameDomainObjects import Player
from Util.ai_command import Idle
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState

__author__ = 'RobocupULaval'


class Tactic:

    def __init__(self, game_state: GameState, player: Player, target: Optional[Pose]=None,
                 forbidden_areas: Optional[List[Area]]=None, args: Optional[List[Any]]=None):

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
        self.forbidden_areas = forbidden_areas if forbidden_areas is not None else []

    def halt(self) -> Idle:
        self.next_state = self.halt
        return Idle

    def exec(self) -> AICommand:
        next_ai_command = self.current_state()
        if not isinstance(next_ai_command, AICommand):
            raise RuntimeError("A tactic MUST return an AICommand, not a {}. {} is the culprit.".format(type(next_ai_command), self.current_state))
        self.current_state = self.next_state

        if next_ai_command.target:
            target_position = next_ai_command.target.position
            target_to_position = Line(self.player.position, next_ai_command.target.position)
            for area in self.forbidden_areas:
                if target_position in area:
                    intersections = area.intersect(target_to_position)
                    if intersections:
                        target_position = intersections[0]
                    else:
                        target_position = position_outside_area(target_position, area)
                    new_target = Pose(target_position, next_ai_command.target.orientation)
                    # This trailing _ is not for protected access, it was add to avoid a name conflict with the function replace ;)
                    next_ai_command = next_ai_command._replace(target=new_target)
                    break

        return next_ai_command

    def debug_cmd(self):
        return []

    def __str__(self):
        return self.__class__.__name__
