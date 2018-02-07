# Under MIT license, see LICENSE.txt
"""
    Contient les classes mères pour les modules intelligents.
"""
from abc import abstractmethod, ABCMeta


class IntelligentModule(object, metaclass=ABCMeta):
    """
        Classe mère des modules intelligents.
        Actuellement ne défini que l'attribut *state*
    """

    def __init__(self):
        """
            Reçoit une référence vers InfoManager. Cette référence est renomée
            comme étant *state*.

            :param world_state: (WorldState) Référence vers le worldstate.
        """

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
    def __init__(self):
        super().__init__()

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
        """ Effectue la mise à jour du module """
        pass
