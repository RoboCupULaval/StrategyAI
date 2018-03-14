from Util.constant import TeamColor
from Util.exception import WrongRobotColorError
from Util.singleton import Singleton
from config.config import Config


class TeamColorService(metaclass=Singleton):
    BLUE = 'blue'
    YELLOW = 'yellow'

    def __init__(self):
        cfg = Config()
        self._our_team_color = self.convert_color_from_str(cfg['GAME']['our_color'])
        self._enemy_team_color = TeamColor.BLUE if self.is_our_team_yellow else TeamColor.YELLOW

    @property
    def our_team_color(self):
        return self._our_team_color

    @property
    def enemy_team_color(self):
        return self._enemy_team_color

    @property
    def is_our_team_yellow(self):
        return self._our_team_color == TeamColor.YELLOW

    @staticmethod
    def convert_color_from_str(color: str):
        if color == TeamColorService.BLUE:
            return TeamColor.BLUE
        elif color == TeamColorService.YELLOW:
            return TeamColor.YELLOW
        else:
            raise WrongRobotColorError('Cannot covert str to TeamColor enum.')
