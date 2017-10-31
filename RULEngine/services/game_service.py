from RULEngine.GameDomainObjects.Field import Field
from RULEngine.GameDomainObjects.Game import Game
from RULEngine.GameDomainObjects.Referee import Referee
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
        self.field = Field()
