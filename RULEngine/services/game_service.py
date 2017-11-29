from RULEngine.GameDomainObjects.Shitty_Field import Shitty_Field
from RULEngine.GameDomainObjects.game import Game
from RULEngine.GameDomainObjects.referee import Referee
from RULEngine.Util.singleton import Singleton


@Singleton
class WorldService:
    def __init__(self):
        self.game = None
        self.referee = None
        self.field = None

    def create_game(self):
        self.game = Game()
        self.referee = Referee()
        self.field = Shitty_Field()
