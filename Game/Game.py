# Under MIT License, see LICENSE.txt

from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.team_color_service import TeamColor

from RULEngine.Game.Team import Team
from RULEngine.Game.Ball import Ball
from RULEngine.Game.Field import Field
from RULEngine.Game.Referee import Referee


class Game:
    def __init__(self):
        self.ball = Ball()
        self.field = Field(self.ball)
        self.referee = None
        self.our_team_color = None
        self.enemy_team_color = None
        self.blue_team = Team(TeamColor.BLUE_TEAM)
        self.yellow_team = Team(TeamColor.YELLOW_TEAM)
        self.friends = None
        self.enemies = None
        self.delta = None

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

    def update(self, vision_frame, delta):
        self.delta = delta
        self._update_ball(vision_frame, delta)
        self._update_players(vision_frame, delta)

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
            print("Ball not found")

    def _update_players(self, vision_frame, delta):
        blue_team = vision_frame.detection.robots_blue
        yellow_team = vision_frame.detection.robots_yellow

        self._update_players_of_team(blue_team, self.blue_team, delta)
        self._update_players_of_team(yellow_team, self.yellow_team, delta)

    @staticmethod
    def _update_players_of_team(players, team, delta):
        for player in players:
            player_position = Position(player.x, player.y, player.height)
            player_pose = Pose(player_position, player.orientation)
            team.update_player(player.robot_id, player_pose, delta)
