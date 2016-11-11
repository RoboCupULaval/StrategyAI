# Under MIT License, see LICENSE.txt

from . import Referee
from ..Util.Pose import Pose
from ..Util.Position import Position
from .Team import Team
from .Ball import Ball
from .Field import Field


class Game():
    def __init__(self, referee, is_team_yellow):
        self.ball = Ball()
        self.field = Field(self.ball)
        self.referee = referee
        self.blue_team, self.yellow_team = self.create_teams()

        if is_team_yellow:
            self.friends = self.yellow_team
            self.enemies = self.blue_team
        else:
            self.friends = self.blue_team
            self.enemies = self.yellow_team

        self.delta = None

    def create_teams(self):
        blue_team = Team(is_team_yellow=False)
        yellow_team = Team(is_team_yellow=True)

        return blue_team, yellow_team

    def update_game_state(self, referee_command):
        # TODO: Réviser code, ça semble louche
        blue_team = referee_command.teams[0]
        self.blue_team.score = blue_team.goalie_count
        yellow_team = referee_command.teams[0]
        self.yellow_team.score = yellow_team.goalie_count

        command = Referee.Command(referee_command.command.name)
        self.referee.command = command

        # TODO: Correctly update the referee with the data from the referee_command

    def update(self, vision_frame, delta):
        self.delta = delta
        self._update_ball(vision_frame, delta)
        self._update_players(vision_frame, delta)

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

    def _update_players_of_team(self, players, team, delta):
        for player in players:
            player_position = Position(player.x, player.y, player.height)
            player_pose = Pose(player_position, player.orientation)
            team.update_player(player.robot_id, player_pose, delta)
