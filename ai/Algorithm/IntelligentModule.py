# Under MIT license, see LICENSE.txt
"""
    Contient les classes mères pour les modules intelligents.
"""
from abc import abstractmethod, ABCMeta

from RULEngine.Debug.debug_interface import DebugInterface

__author__ = 'RoboCupULaval'


class IntelligentModule(object, metaclass=ABCMeta):
    """
        Classe mère des modules intelligents.
        Actuellement ne défini que l'attribut *state*
    """

    def __init__(self, p_worldstate):
        """
            Reçoit une référence vers InfoManager. Cette référence est renomée
            comme étant *state*.

            :param pInfoManager: Référence vers l'InfoManager
        """

        self.ws = p_worldstate
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

    def __init__(self, p_worldstate):
        super().__init__(p_worldstate)

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
    def get_path(self, robot_id=None, target=None):
        """
            Si l'ID est précisé, retourne la liste des *Pose* pour le chemin
            de ce robot. Autrement, retourne le dictionnaire.

            :param robot_id: int entre 0 à 11 représentant les robots de
                             l'équipe alliée
            :param target: LEGACY -> a etre supprimer dans versin future.
            :return: { id : [Pose, Pose, ...] } || [Pose, Pose, ...]
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
