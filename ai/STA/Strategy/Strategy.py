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
    def __init__(self, p_info_manager):
        self.info_manager = p_info_manager
        self.graphs = []
        for i in range(PLAYER_PER_TEAM):
            self.graphs.append(Graph())

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
            current_tactic = self.graphs[i].get_current_tactic
            state.append((current_tactic.player_id, str(current_tactic), current_tactic.current_state.__name__,
                          current_tactic.target))
        return state

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
