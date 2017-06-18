# Under MIT license, see LICENSE.txt

from abc import ABCMeta
from typing import List, Tuple, Callable, Dict

from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Pose import Pose
from RULEngine.Util.constant import PLAYER_PER_TEAM
from ai.Algorithm.Graph.Graph import Graph, EmptyGraphException
from ai.Algorithm.Graph.Node import Node
from ai.STA.Tactic.Tactic import Tactic
from ai.Util.ai_command import AICommand
from ai.Util.role import Role
from ai.states.game_state import GameState


# Pour l'instant, les stratégies n'optimisent pas la gestion des ressources (ex: toujours le même robot qui va chercher
# la balle et non le plus proche). TODO: À optimiser
class Strategy(metaclass=ABCMeta):
    """ Définie l'interface commune aux stratégies. """
    def __init__(self, p_game_state: GameState):
        """
        Initialise la stratégie en créant un graph vide pour chaque robot de l'équipe.
        :param p_game_state: L'état courant du jeu.
        """
        assert isinstance(p_game_state, GameState)
        self.game_state = p_game_state
        self.roles_graph = {r: Graph() for r in Role}
        players = [p for p in self.game_state.my_team.available_players.values()]
        roles = [r for r in Role]
        role_mapping = dict(zip(roles, players))
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
                          current_tactic.current_state.__name__, tactic_name, current_tactic.target))
        return state

    def exec(self) -> Dict[int, AICommand]:
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
                commands[player.id] = self.roles_graph[r].exec()
            except EmptyGraphException as e:
                continue
            player.ai_command = commands[player.id]

        return commands

    def _update_roles_translation(self) -> None:
        pass

    def _store_tactic_arguments(self, role: Role, node_id: int, tactic_arguments = List) -> None:
        self._tactics_arguments[role][node_id] = tactic_arguments

    def _retrive_tactic_arguments(self, role: Role, node_id: int) -> List:
        return self._tactics_arguments[role][node_id]

    def get_player_by_role(self, role: Role) -> OurPlayer:
        return self.game_state.my_team.available_players[self._roles_translation[role]]

    def get_role_by_player_id(self, player_id: int) -> Role:
        for r, id in self._roles_translation.items():
            if id == player_id:
                return r
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
