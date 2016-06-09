# Under MIT license, see LICENSE.txt
"""
    Contient les classes mères pour les modules intelligents.
"""
from abc import abstractmethod, ABCMeta

__author__ = 'RoboCupULaval'

class IntelligentModule(object, metaclass=ABCMeta):
    """
        Classe mère des modules intelligents.
        Actuellement ne défini que l'attribut *state*
    """

    def __init__(self, pInfoManager):
        """
            Reçoit une référence vers InfoManager. Cette référence est rennomée
            comme étant *state*.

            :param pInfoManager: Référence vers l'InfoManager
        """

        self.state = pInfoManager

    def get_info_manager(self):
        """ Retourne la référence de l'InfoManager """
        return self.state

    @abstractmethod
    def str(self):
        """ Ne pas utiliser """

class Pathfinder(IntelligentModule, metaclass=ABCMeta):
    """
        Classe mère des pathfinders.
        Défini l'interface publique et la documente.
        Les pathfinders possèdent un attribut *paths*.
        Cet attribut est un dictionnaire où les clefs sont les ids des robots.
        La valeur associée est une liste de *Pose*.
    """

    def __init__(self, pInfoManager):
        """
            Initialise le dictionnaire *paths*.
        """
        super().__init__(pInfoManager)
        self.paths = {}
        for i in range(6):
            self.paths[i] = []

    def str(self):
        """
            Retourne la représentation en String de paths.

            :return: String
        """
        return str(self.paths)

    @abstractmethod
    def get_path(self, pid=None):
        """
            Si l'ID est précisé, retourne la liste des *Pose* pour le chemin
            de ce robot. Autrement, retourne le dictionnaire. Cette méthode est
            aussi responsable de faire les appels pour mettre à jour les
            informatoins.

            :param id: int de 0 à 5 représentant les robots de l'équipe alliée
            :return: { id : [Pose, Pose, ...] } || [Pose, Pose, ...]
        """
