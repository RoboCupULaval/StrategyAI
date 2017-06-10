from RULEngine.Util.constant import TeamColor
from RULEngine.Util.exception import WrongRobotColorError
from RULEngine.Util.singleton import Singleton
from config.config_service import ConfigService


class TeamColorService(object, metaclass=Singleton):

    def __init__(self, team_color = None):
        if team_color is None:
            cfg = ConfigService()
            team_str = cfg.config_dict["GAME"]["our_color"]
            if team_str == cfg.config_dict["GAME"]["their_color"]:
                raise WrongRobotColorError("The enemies robot color is wrong please check "
                                           "the config file")
        else:
            team_str = team_color.__str__()
        if team_str == "yellow":
            self.OUR_TEAM_COLOR = TeamColor.YELLOW_TEAM
            self.ENEMY_TEAM_COLOR = TeamColor.BLUE_TEAM

        elif team_str == "blue":
            self.OUR_TEAM_COLOR = TeamColor.BLUE_TEAM
            self.ENEMY_TEAM_COLOR = TeamColor.YELLOW_TEAM

        else:
            raise WrongRobotColorError("")

