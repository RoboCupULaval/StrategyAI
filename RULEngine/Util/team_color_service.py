from RULEngine.Util.constant import TeamColor
from RULEngine.Util.exception import WrongRobotColorError
from RULEngine.Util.singleton import Singleton
from config.config_service import ConfigService


class TeamColorService(object, metaclass=Singleton):

    def __init__(self):
        cfg = ConfigService()
        if cfg.config_dict["GAME"]["our_color"] == "yellow":
            try:
                assert cfg.config_dict["GAME"]["their_color"] == "blue"
            except AssertionError:
                raise WrongRobotColorError("The enemies robot color is wrong please check "
                                           "the config file")
            self.OUR_TEAM_COLOR = TeamColor.YELLOW
            self.ENEMY_TEAM_COLOR = TeamColor.BLUE

        elif cfg.config_dict["GAME"]["our_color"] == "blue":
            self.OUR_TEAM_COLOR = TeamColor.BLUE
            self.ENEMY_TEAM_COLOR = TeamColor.YELLOW

        else:
            raise WrongRobotColorError("")

