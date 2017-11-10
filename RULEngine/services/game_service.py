from RULEngine.GameDomainObjects.Field import Field
from RULEngine.GameDomainObjects.GameState import GameState
from RULEngine.GameDomainObjects.Referee import Referee
from RULEngine.Util.singleton import Singleton


@Singleton
class WorldService:
    def __init__(self):
        self.game = None
        self.referee = None
        self.field = None

    def create_game(self):
        self.game = GameState()
        self.referee = Referee()
        self.field = Field()
