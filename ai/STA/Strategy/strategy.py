# Under MIT license, see LICENSE.txt

from abc import ABCMeta
from typing import List, Tuple, Callable, Dict

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
        self.game_state = p_game_state
        self.roles = Role.as_list()
        self.roles_graph = {r: Graph() for r in self.roles}
        players = [p for p in self.game_state.our_team.players.values()]

        role_mapping = dict(zip(self.roles, players))
        role_mapping = self.hack_goalkeeper(role_mapping)

        self.game_state.map_players_to_roles_by_player(role_mapping)

    def hack_goalkeeper(self, role_mapping):
        current_goaler = self.game_state.get_player_by_role(Role.GOALKEEPER)
        if current_goaler is not None:
            new_goaler = role_mapping[Role.GOALKEEPER]
            new_goaler_old_role = self.game_state.get_role_by_player_id(new_goaler.id)
            role_mapping[Role.GOALKEEPER] = current_goaler
            role_mapping[new_goaler_old_role] = new_goaler
        return role_mapping

    def add_tactic(self, role: Role, tactic: Tactic) -> None:
        """
        Ajoute une tactique au graph des tactiques d'un robot.
        :param role: Le role auquel est assignée la tactique.
        :param tactic: La tactique à assigner au robot du role.
        """
        assert(isinstance(role, Role))
        self.roles_graph[role].add_node(Node(tactic))

    def add_condition(self, role: Role, start_node: int, end_node: int, condition: Callable[..., bool]):
        """
        Ajoute une condition permettant de gérer la transition entre deux tactiques d'un robot.
        :param role: Le role qui a la tactic.
        :param start_node: Le noeud de départ du vertex.
        :param end_node: Le noeud d'arrivée du vertex.
        :param condition: Une fonction retournant un booléen permettant de déterminer si on peut effectuer la transition
        du noeud de départ vers le noeud d'arrivé.
        """
        assert(isinstance(role, Role))
        self.roles_graph[role].add_vertex(start_node, end_node, condition)

    def get_current_state(self) -> List[Tuple[Player, str, str, Pose]]:
        """ [
                Player: Player;
                Tactic Name: str
                Action name: str
                Tactic target: Pose
            ]
        """
        state = []
        for r in self.roles:
            current_tactic = self.roles_graph[r].get_current_tactic()
            if current_tactic is None:
                continue

            try:
                state_of_current_tactic = current_tactic.current_state.__name__
            except AttributeError:
                state_of_current_tactic = "DEFAULT"
            clear_name_for_tatic = str(current_tactic) + " " + \
                                   current_tactic.status_flag.name+" " + \
                                   state_of_current_tactic
            state.append((current_tactic.player, clear_name_for_tatic, str(current_tactic), current_tactic.target))
        return state

    def clear_graph_of_role(self, r: Role):
        self.roles_graph[r] = Graph()

    def exec(self) -> Dict[Player, AICommand]:
        """
        Appelle la méthode exec de chacune des Tactics assignées aux robots.
        :return: Un dict des 6 AICommand à envoyer aux robots. La commande située à l'indice i de la liste doit être
        envoyée au robot i.
        """
        commands = {}

        for r in self.roles:
            player = self.game_state.get_player_by_role(r)
            if player is None:
                continue
            tactic = self.roles_graph.get(r, None)
            if tactic is None:
                continue

            try:
                commands[player] = self.roles_graph[r].exec()
            except EmptyGraphException:
                continue

        return commands

    def __str__(self):
        return self.__class__.__name__

    def __eq__(self, other):
        assert isinstance(other, Strategy)
        return str(self) == str(other)

    def __ne__(self, other):
        return not self.__eq__(other)
