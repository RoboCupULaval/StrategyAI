# Under MIT license, see LICENSE.txt

from abc import ABCMeta
from typing import List, Tuple, Callable, Dict

from RULEngine.Util.constant import PLAYER_PER_TEAM
from ai.Algorithm.Graph.Graph import Graph
from ai.Algorithm.Graph.Node import Node
from ai.STA.Tactic.Tactic import Tactic
from ai.Util.ai_command import AICommand
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
        self.graphs = []
        for i in range(PLAYER_PER_TEAM):
            self.graphs.append(Graph())

    def add_tactic(self, robot_id: int, tactic: Tactic) -> None:
        """
        Ajoute une tactique au graph des tactiques d'un robot.
        :param robot_id: L'id du robot auquel est assignée la tactique.
        :param tactic: La tactique à assigner au robot.
        """
        assert(isinstance(robot_id, int))
        self.graphs[robot_id].add_node(Node(tactic))

    def add_condition(self, robot_id: int, start_node: int, end_node: int, condition: Callable[..., bool]):
        """
        Ajoute une condition permettant de gérer la transition entre deux tactiques d'un robot.
        :param robot_id: L'id du robot.
        :param start_node: Le noeud de départ du vertex.
        :param end_node: Le noeud d'arrivée du vertex.
        :param condition: Une fonction retournant un booléen permettant de déterminer si on peut effectuer la transition
        du noeud de départ vers le noeud d'arrivé.
        """
        assert(isinstance(robot_id, int))
        self.graphs[robot_id].add_vertex(start_node, end_node, condition)

    def get_current_state(self) -> List[Tuple[int, str, str, str]]:
        """
            Retourne l'état actuel de la stratégie, dans une liste de 6 tuples. Chaque tuple contient:
                -L'id d'un robot;
                -Le nom de la Tactic qui lui est présentement assignée sous forme d'une chaîne de caractères;
                -Le nom de l'Action en cours sous forme d'une chaîne de caractères;
                -Sa target, soit un objet Pose.
        """
        state = []
        for player in self.game_state.my_team.available_players.values():
            current_tactic = self.graphs[player.id].get_current_tactic()
            try:
                tactic_name = current_tactic.current_state.__name__
            except AttributeError:
                tactic_name = "DEFAULT"
            state.append((current_tactic.player_id, str(current_tactic)+" "+current_tactic.status_flag.name+" " +
                          current_tactic.current_state.__name__, tactic_name, current_tactic.target))
        return state

    def exec(self) -> Dict[int, AICommand]:
        """
        Appelle la méthode exec de chacune des Tactics assignées aux robots.
        :return: Un dict des 6 AICommand à envoyer aux robots. La commande située à l'indice i de la liste doit être
        envoyée au robot i.
        """
        commands = {}
        for player in self.game_state.my_team.available_players.values():
            commands[player.id] = self.graphs[player.id].exec()
        return commands

    def __str__(self):
        return self.__class__.__name__

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
