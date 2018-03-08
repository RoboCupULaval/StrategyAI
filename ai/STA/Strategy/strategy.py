# Under MIT license, see LICENSE.txt

from abc import ABCMeta
from typing import List, Tuple, Callable, Dict

from Util import AICommand
from Util.role import Role
from ai.Algorithm.Graph.Graph import Graph, EmptyGraphException
from ai.Algorithm.Graph.Node import Node
from ai.GameDomainObjects import Player
from ai.STA.Tactic.tactic import Tactic
from ai.states.game_state import GameState


class Strategy(metaclass=ABCMeta):
    """ Définie l'interface commune aux stratégies. """
    def __init__(self, p_game_state: GameState, keep_roles=True):
        """
        Initialise la stratégie en créant un graph vide pour chaque robot de l'équipe.
        :param p_game_state: L'état courant du jeu.
        """
        assert isinstance(p_game_state, GameState)
        self.game_state = p_game_state
        self.roles_graph = {r: Graph() for r in Role}
        players = [p for p in self.game_state.our_team.players.values()]  # FIXME: SB. was available_players
        roles = [r for r in Role]
        role_mapping = dict(zip(roles, players))
        # Magnifique hack pour bypasser un mapping de goalkeeper
        current_goaler = p_game_state.get_player_by_role(Role.GOALKEEPER)
        if current_goaler is not None:
            new_goaler = role_mapping[Role.GOALKEEPER]
            new_goaler_old_role = p_game_state.get_role_by_player_id(new_goaler.id)
            role_mapping[Role.GOALKEEPER] = current_goaler
            role_mapping[new_goaler_old_role] = new_goaler

        self.game_state.map_players_to_roles_by_player(role_mapping)

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

    def get_current_state(self) -> List[Tuple[int, str, str, str]]:
        """
            Retourne l'état actuel de la stratégie, dans une liste de 6 tuples. Chaque tuple contient:
                -L'id d'un robot;
                -Le nom de la Tactic qui lui est présentement assignée sous forme d'une chaîne de caractères;
                -Le nom de l'Action en cours sous forme d'une chaîne de caractères;
                -Sa target, soit un objet Pose.
        """
        state = []
        for r in Role:
            current_tactic = self.roles_graph[r].get_current_tactic()
            if current_tactic is None:
                continue

            try:
                tactic_name = current_tactic.current_state.__name__
            except AttributeError:
                tactic_name = "DEFAULT"
            state.append((current_tactic.player, str(current_tactic)+" "+current_tactic.status_flag.name+" " +
                          current_tactic.current_state.__name__, str(current_tactic), current_tactic.target))
        return state

    def exec(self) -> Dict[Player, AICommand]:
        """
        Appelle la méthode exec de chacune des Tactics assignées aux robots.
        :return: Un dict des 6 AICommand à envoyer aux robots. La commande située à l'indice i de la liste doit être
        envoyée au robot i.
        """
        commands = {}
        # for i, g in enumerate(self.roles_graph):
        #     print(i,"->",g)
        # TODO We should probably iterate over game_state.RoleMapping instead of Role
        # TODO It would allow us to deal with fewer than 6 roles
        for r in Role:
            player = self.game_state.get_player_by_role(r)
            if player is None:
                continue
            tactic = self.roles_graph.get(r, None)
            if tactic is None:
                continue

            try:
                commands[player] = self.roles_graph[r].exec()
            except EmptyGraphException as e:
                continue

        return commands

    def __str__(self):
        return self.__class__.__name__

    # TODO check if this is correct MGL 2017/06/16
    def __eq__(self, other):
        """
        La comparaison est basée sur le nom des stratégies. Deux stratégies possédant le même nom sont considérée égale.
        """
        assert isinstance(other, Strategy)
        return str(self) == str(other)

    def __ne__(self, other):
        """ Return self != other """
        assert isinstance(other, Strategy)
        return not self.__eq__(other)
