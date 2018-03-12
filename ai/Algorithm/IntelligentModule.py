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

    @abstractmethod
    def update(self, *args, **kwargs):
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
    def __init__(self):
        super().__init__()

        self.paths = {}
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
