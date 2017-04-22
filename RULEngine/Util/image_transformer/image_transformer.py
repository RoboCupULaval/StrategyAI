from abc import abstractmethod, ABCMeta


class ImageTransformer(object, metaclass=ABCMeta):
    """
            Classe mère des classes de traitements de la vision.
            Actuellement ne défini que la méthode update et init
        """

    def __init__(self):
        pass

    @abstractmethod
    def update(self, packets):
        """ Effectue la mise à jour du module """
        pass
