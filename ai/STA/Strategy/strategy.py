# Under MIT license, see LICENSE.txt

from abc import ABCMeta
from typing import List, Tuple, Callable, Dict

import logging

from Util import AICommand, Pose
from Util.role import Role
from ai.Algorithm.Graph.Graph import Graph, EmptyGraphException
from ai.Algorithm.Graph.Node import Node
from ai.GameDomainObjects import Player
from ai.STA.Tactic.tactic import Tactic
from ai.states.game_state import GameState


class Strategy(metaclass=ABCMeta):
    """ Définie l'interface commune aux stratégies. """
    def __init__(self, p_game_state: GameState):
        """
        Initialise la stratégie en créant un graph vide pour chaque robot de l'équipe.
        :param p_game_state: L'état courant du jeu.
        """
        assert isinstance(p_game_state, GameState)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.game_state = p_game_state

        self.roles_graph = {role: Graph() for role in self.assigned_roles}

    @property
    def assigned_roles(self):
        return self.game_state.assigned_roles

    def obstacles(self):
        return []

    @classmethod
    def required_roles(cls) -> Dict[Role, Callable]:
        """
        The required roles are the one that must be available otherwise the strategy's goal is unreachable
        """
        raise NotImplementedError("Strategy '{}' must provide the list of required roles".format(cls.__name__))

    @classmethod
    def optional_roles(cls) -> Dict[Role, Callable]:
        return []

    def create_node(self, role: Role, tactic: Tactic) -> Node:
        """
        Ajoute une tactique au graph des tactiques d'un robot.
        :param role: Le role auquel est assignée la tactique.
        :param tactic: La tactique à assigner au robot du role.
        """
        assert(isinstance(role, Role))

        tactic_node = Node(tactic)
        self.roles_graph[role].add_node(tactic_node)
        return tactic_node

    def get_current_state(self) -> List[Tuple[Player, str, str, Role]]:
        state = []
        for role, graph in self.roles_graph.items():
            current_tactic = graph.current_tactic
            if current_tactic is None:
                continue

            state_of_current_tactic = current_tactic.current_state.__name__

            clear_name_for_tatic = str(current_tactic) + " " + \
                                   current_tactic.status_flag.name
            state.append((current_tactic.player, clear_name_for_tatic, state_of_current_tactic, role))
        return state

    def clear_graph_of_role(self, r: Role):
        self.roles_graph[r] = Graph()

    def exec(self) -> Tuple[Dict[Player, AICommand], List[Dict]]:
        """
        Appelle la méthode exec de chacune des Tactics assignées aux robots.
        :return: Un dict des 6 AICommand à envoyer aux robots. La commande située à l'indice i de la liste doit être
        envoyée au robot i.
        """
        cmd_ai = {}
        cmd_debug = []

        for r, player in self.assigned_roles.items():
            # TODO: Might break a lot of thing.
            # Eventually the entering and leaving of player should be directly handle by the coach of something
            if player in self.game_state.our_team.available_players.values():
                try:
                    cmd_ai[player] = self.roles_graph[r].exec()
                    cmd_debug.extend(self.roles_graph[r].debug_cmd())
                except EmptyGraphException:
                    continue

        return cmd_ai, cmd_debug

    def __str__(self):
        return self.__class__.__name__

    def __eq__(self, other):
        assert isinstance(other, Strategy)
        return str(self) == str(other)

    def __ne__(self, other):
        return not self.__eq__(other)
