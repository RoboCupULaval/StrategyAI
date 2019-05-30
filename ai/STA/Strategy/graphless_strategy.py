# Under MIT license, see LICENSE.txt

from typing import List, Tuple, Dict, Callable

from Util import AICommand
from Util.role import Role
from ai.GameDomainObjects import Player
from ai.STA.Strategy.strategy import Strategy
from ai.states.game_state import GameState


class GraphlessStrategy(Strategy):
    def __init__(self, p_game_state: GameState):
        super().__init__(p_game_state)
        self.roles_to_tactics = {}
        self.next_state = self.halt

    def exec(self) -> Tuple[Dict[Player, AICommand], List[Dict]]:
        self.next_state()

        cmd_ai = {}
        cmds_debug = []

        for r, player in self.assigned_roles.items():
            if player in self.game_state.our_team.available_players.values():
                cmd_ai[player] = self.roles_to_tactics[r].exec()
                cmd_debug = self.roles_to_tactics[r].debug_cmd()
                if cmd_debug is not None:
                    cmds_debug.extend([cmd_debug] if isinstance(cmd_debug, dict) else cmd_debug)

        return cmd_ai, cmds_debug

    def halt(self):
        self.roles_to_tactics = {}

    @classmethod
    def required_roles(cls) -> Dict[Role, Callable]:
        """
        The required roles are the one that must be available otherwise the strategy's goal is unreachable
        """
        raise NotImplementedError("Strategy '{}' must provide the list of required roles".format(cls.__name__))
