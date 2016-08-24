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

class Pathfinder(metaclass=ABCMeta):
    """
        Classe mère des pathfinders.
        Défini l'interface publique et la documente.
        Les pathfinders possèdent un attribut *paths*.
        Cet attribut est un dictionnaire où les clefs sont les ids des robots.
        La valeur associée est une liste de *Pose*.
    """

    def __init__(self, info_manager):
        """
            Initialise le dictionnaire *paths*.
        """
        self.state = info_manager
        self.paths = {}
        for i in range(6):
            self.paths[i] = []

    def str(self):
        """
            Retourne le en string le dictionnaire des paths.
        """
        return str(self.paths)

    @abstractmethod
    def get_path(self, pid=None, target=None):
        """
            Si l'ID est précisé, retourne la liste des *Pose* pour le chemin
            de ce robot. Autrement, retourne le dictionnaire.

            :param id: int de 0 à 5 représentant les robots de l'équipe alliée
            :return: { id : [Pose, Pose, ...] } || [Pose, Pose, ...]
        """
