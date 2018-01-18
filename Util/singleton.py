# Under MIT License, see LICENSE.txt
__author__ = "Maxime Gagnon-Legault, and others"


class Singleton(type):
    """ Implemente le pattern Singleton avec une metaclass """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
