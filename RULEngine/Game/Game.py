# Under MIT License, see LICENSE.txt
from typing import List

from RULEngine.Communication.protobuf import messages_robocup_ssl_wrapper_pb2
from RULEngine.Game.OurTeam import OurTeam
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.team_color_service import TeamColor

from RULEngine.Game.Team import Team
from RULEngine.Game.Ball import Ball
from RULEngine.Game.Field import Field
from RULEngine.Game.Referee import Referee
from config.config_service import ConfigService


class Game:
    def __init__(self):
        self.ball = Ball()
        self.field = Field(self.ball)
        self.referee = None
        self.our_team_color = None
        self.enemy_team_color = None
        self.blue_team = None
        self.yellow_team = None
        self.friends = None
        self.enemies = None
        self.delta_t = None
        self.cmd = None
        self._create_teams()
        self.update = self._update
        if ConfigService().config_dict["IMAGE"]["kalman"] == "true":
            self.update = self._kalman_update

    def set_command(self, cmd):
        for commands in cmd:
            self.friends.update_player_command(commands.player.id, commands)

    def set_referee(self, p_referee):
        self.referee = p_referee

    def _create_teams(self):
        cfg = ConfigService()
        if cfg.config_dict["GAME"]["our_color"] == "blue":
            self.our_team_color = TeamColor.BLUE_TEAM
            self.blue_team = OurTeam(TeamColor.BLUE_TEAM)
            self.friends = self.blue_team
            self.yellow_team = Team(TeamColor.YELLOW_TEAM)
            self.enemies = self.yellow_team
        elif cfg.config_dict["GAME"]["our_color"] == "yellow":
            self.our_team_color = TeamColor.YELLOW_TEAM
            self.yellow_team = OurTeam(TeamColor.YELLOW_TEAM)
            self.friends = self.yellow_team
            self.blue_team = Team(TeamColor.BLUE_TEAM)
            self.enemies = self.blue_team
        else:
            raise ValueError("Config file contains wrong colors!")

    def update_game_state(self, referee_command):
        # TODO: Réviser code, ça semble louche
        # TODO: remove or change completly! WHAT IS THIS??? MGL 2017/05/14
        blue_team = referee_command.teams[0]
        self.blue_team.score = blue_team.goalie_count
        yellow_team = referee_command.teams[0]
        self.yellow_team.score = yellow_team.goalie_count

        # Commented out since it is not used MGL 2017/01/07
        # command = Referee.Command(referee_command.command.name)
        # self.referee.command = command

    def _update(self, vision_frame: messages_robocup_ssl_wrapper_pb2, delta: float) -> None:
        self.delta_t = delta
        # print(delta)
        self._update_ball(vision_frame, delta)
        self._update_players(vision_frame, delta)

    def _kalman_update(self, vision_frame: List, delta: float) -> None:
        self.delta_t = delta
        self.kalman_update_ball(vision_frame, delta)
        self.kalman_update_players(vision_frame, delta)

    def is_team_yellow(self):
        return self.our_team_color == TeamColor.YELLOW_TEAM

    def _update_ball(self, vision_frame, delta):
        try:
            ball_position = Position(vision_frame.detection.balls[0].x,
                                     vision_frame.detection.balls[0].y,
                                     vision_frame.detection.balls[0].z)
            self.field.move_ball(ball_position, delta)
        except IndexError:
            pass
            # print("Ball not found")

    def _update_players(self, vision_frame, delta):
        blue_team = vision_frame.detection.robots_blue
        yellow_team = vision_frame.detection.robots_yellow

        self._update_players_of_team(blue_team, self.blue_team, delta)
        self._update_players_of_team(yellow_team, self.yellow_team, delta)

    def kalman_update_ball(self, vision_frame, delta):
        kalman_list = []
        for c in vision_frame:
            kalman_list.append(c["ball"])
        self.ball.kalman_update(kalman_list, delta)

    def kalman_update_players(self, vision_frame, delta):
        kalman_blue = [[] for _ in range(0, 6)]
        kalman_yellow = [[] for _ in range(0, 6)]
        for c in vision_frame:
            for i in range(0, 6):
                kalman_blue[i].append(c["blues"][i])
                kalman_yellow[i].append(c["yellows"][i])

        for i in range(0, 6):
            self.blue_team.update_player(i, kalman_blue[i], delta)
            self.yellow_team.update_player(i, kalman_yellow[i], delta)

    @staticmethod
    def _update_players_of_team(players, team, delta):
        for player in players:
            player_position = Position(player.x, player.y, player.height)
            player_pose = Pose(player_position, player.orientation)
            team.update_player(player.robot_id, player_pose, delta)
