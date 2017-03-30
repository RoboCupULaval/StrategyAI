# Under MIT License, see LICENSE.txt
from typing import List

from RULEngine.Communication.protobuf import messages_robocup_ssl_wrapper_pb2
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.team_color_service import TeamColor

from RULEngine.Game.Team import Team
from RULEngine.Game.Ball import Ball
from RULEngine.Game.Field import Field
from RULEngine.Game.Referee import Referee


class Game:
    def __init__(self, terrain_type="sim"):
        self.ball = Ball()
        self.field = Field(self.ball, terrain_type)
        self.referee = None
        self.our_team_color = None
        self.enemy_team_color = None
        self.blue_team = Team(TeamColor.BLUE_TEAM, type="friend")
        self.yellow_team = Team(TeamColor.YELLOW_TEAM, type="enemi")
        self.friends = None
        self.enemies = None
        self.delta_t = None
        self.cmd = None

    def set_command(self, cmd):
        for commands in cmd:
            self.friends.update_player_command(commands.player.id, commands)

    def set_referee(self, p_referee):
        self.referee = p_referee

    def set_our_team_color(self, p_our_team_color):
        assert isinstance(p_our_team_color, TeamColor), \
            "The color of any team must be a TeamColor enum!"

        self.our_team_color = p_our_team_color
        self._adjust_teams_color()

    def set_enemy_team_color(self, p_enemy_team_color):
        assert isinstance(p_enemy_team_color, TeamColor), \
            "The color of any team must be a TeamColor enum!"

        self.our_team_color = p_enemy_team_color

    def update_game_state(self, referee_command):
        # TODO: Réviser code, ça semble louche
        blue_team = referee_command.teams[0]
        self.blue_team.score = blue_team.goalie_count
        yellow_team = referee_command.teams[0]
        self.yellow_team.score = yellow_team.goalie_count

        # Commented out since it is not used MGL 2017/01/07
        # command = Referee.Command(referee_command.command.name)
        # self.referee.command = command

    def update(self, vision_frame: messages_robocup_ssl_wrapper_pb2, delta: float):
        self.delta_t = delta
        # print(delta)
        self._update_ball(vision_frame, delta)
        self._update_players(vision_frame, delta)

    def update_kalman(self, vision_frame: List, delta: float):
        self.delta_t = delta
        self.kalman_update_ball(vision_frame, delta)
        self.kalman_update_players(vision_frame, delta)

    def is_team_yellow(self):
        return self.our_team_color == TeamColor.YELLOW_TEAM

    def _adjust_teams_color(self):
        if self.our_team_color == TeamColor.YELLOW_TEAM:
            self.friends = self.yellow_team
            self.enemies = self.blue_team
        elif self.our_team_color == TeamColor.BLUE_TEAM:
            self.friends = self.blue_team
            self.enemies = self.yellow_team
        else:
            raise ValueError("Can't adjust the teamscolor in Game object!")

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

    def kalman_update_players(self, vision_frame, delta):
        kalman_blue = [[] for i in range(0, 11)]
        kalman_yellow = [[] for i in range(0, 11)]
        for c in vision_frame:
            for i in range(0, 11):
                kalman_blue[i].append(c["blues"][i])
                kalman_yellow[i].append(c["yellows"][i])

        for i in range(0, 11):
            self.blue_team.kalman_update(i, kalman_blue[i], delta)
            self.yellow_team.kalman_update(i, kalman_yellow[i], delta)


    @staticmethod
    def _update_players_of_team(players, team, delta):
        for player in players:
            player_position = Position(player.x, player.y, player.height)
            player_pose = Pose(player_position, player.orientation)
            team.update_player(player.robot_id, player_pose, delta)
