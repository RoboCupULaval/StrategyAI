# Under MIT license, see LICENSE.txt
"""
    Contient les classes mères pour les modules intelligents.
"""
from abc import abstractmethod, ABCMeta
from typing import List

from RULEngine.Debug.debug_interface import DebugInterface
from RULEngine.GameDomainObjects.OurPlayer import OurPlayer
from RULEngine.GameDomainObjects.Player import Player
from RULEngine.Util.Pose import Pose

__author__ = 'RoboCupULaval'


class IntelligentModule(object, metaclass=ABCMeta):
    """
        Classe mère des modules intelligents.
        Actuellement ne défini que l'attribut *state*
    """

    def __init__(self, world_state):
        """
            Reçoit une référence vers InfoManager. Cette référence est renomée
            comme étant *state*.

            :param world_state: (WorldState) Référence vers le worldstate.
        """

        self.ws = world_state
        self.debug_interface = DebugInterface()

    @abstractmethod
    def update(self):
        """ Effectue la mise à jour du module """
        pass

    @abstractmethod
    def str(self):
        """
            La représentation en string d'un module intelligent devrait
            permettre de facilement envoyer son information dans un fichier de
            log.
        """


class Pathfinder(IntelligentModule, metaclass=ABCMeta):
    """
        Classe mère des pathfinders.
        Défini l'interface publique et la documente.
        Les pathfinders possèdent un attribut *paths*.
        Cet attribut est un dictionnaire où les clefs sont les ids des robots.
        La valeur associée est une liste de *Pose*.
    """
    # TODO Make this class better please!
    def __init__(self, worldstate):
        super().__init__(worldstate)

        # TODO see if we can remove this part!
        self.paths = {}
        # TODO insert constant for max numbers of robots below instead of 11!
        for i in range(11):
            self.paths[i] = []

    def str(self):
        """
            Retourne le en string le dictionnaire des paths.
        """
        return str(self.paths)

    @abstractmethod
    def update(self):
        """
            Prepare le pathfinder pour retourner les paths voulues. ie.
            calcule toutes les paths activés
        :return:
        """

    @abstractmethod
    def get_path(self, player: OurPlayer, target=Pose(), cruise_speed=1) -> List[Pose]:
        """
            Si l'ID est précisé, retourne la liste des *Pose* pour le chemin
            de ce robot. Autrement, retourne le dictionnaire.

            :param player: Player une instance de robot de notre équipe
            :param target: LEGACY -> a etre supprimer dans versin future.
            :param cruise_speed: asdf->dsf
            :return: [Pose, Pose, ...]
        """

    @abstractmethod
    def get_next_point(self, robot_id=None):
        """
            Si l'ID est précisé, retourne le prochain point *Pose* pour le
            chemin de ce robot. Autrement, retourne dictionaire des
            prochains points avec clé l'id des robots.
            :param robot_id: int entre 0 à 11 représentant l'id des robots de
                             l'équipe alliée
            :return: {id : Pose, ... }
        """
