# Under MIT license, see LICENSE.txt

from abc import ABCMeta

from ..Tactic.Stop import Stop
from ..Tactic import tactic_constants
from ai.Algorithm.Graph import Graph
from ai.Algorithm.Node import Node
from ai.Algorithm.Vertex import Vertex
from RULEngine.Util.constant import PLAYER_PER_TEAM


# Pour l'instant, les stratégies n'optimisent pas la gestion des ressources (ex: toujours le même robot qui va chercher
# la balle et non le plus proche). TODO: À optimiser
class Strategy(metaclass=ABCMeta):
    """ Définie l'interface commune aux stratégies. """
    def __init__(self, p_game_state):
        """
        Initialise la stratégie en créant un graph vide pour chaque robot de l'équipe.
        :param p_game_state: L'état courant du jeu.
        """
        self.game_state = p_game_state
        self.graphs = []
        for i in range(PLAYER_PER_TEAM):
            self.graphs.append(Graph())

    def add_tactic(self, robot_id, tactic):
        """
        Ajoute une tactique au graph des tactiques d'un robot.
        :param robot_id: L'id du robot auquel est assignée la tactique.
        :param tactic: La tactique à assigner au robot.
        """
        assert(isinstance(robot_id, int))
        self.graphs[robot_id].add_node(Node(tactic))

    def add_condition(self, robot_id, start_node, end_node, condition):
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

    def get_current_state(self):
        """
            Retourne l'état actuel de la stratégie, dans une liste de 6 tuples. Chaque tuple contient:
                -L'id d'un robot;
                -Le nom de la Tactic qui lui est présentement assignée sous forme d'une chaîne de caractères;
                -Le nom de l'Action en cours sous forme d'une chaîne de caractères;
                -Sa target, soit un objet Pose.
        """
        state = []
        for i in range(PLAYER_PER_TEAM):
            current_tactic = self.graphs[i].get_current_tactic()
            state.append((current_tactic.player_id, str(current_tactic)+" "+current_tactic.status_flag.name,
                         current_tactic.current_state.__name__, current_tactic.target))
        return state

    def add_tactic(self, robot_id, tactic):
        self.graphs[robot_id].add_node(Node(tactic))

    def add_condition(self, robot_id, start_node, end_node, condition):
        self.graphs[robot_id].add_vertex(start_node,end_node,condition)

    def exec(self):
        """
        Appelle la méthode exec de chacune des Tactics assignées aux robots.
        :return: Une liste des 6 AICommand à envoyer aux robots. La commande située à l'indice i de la liste doit être
        envoyée au robot i.
        """
        commands = []
        for i in range(PLAYER_PER_TEAM):
            commands.append(self.graphs[i].exec())
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
