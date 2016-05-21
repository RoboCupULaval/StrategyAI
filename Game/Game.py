import math

from . import Referee
from ..Util.Pose import Pose
from ..Util.Position import Position
from ..Util.constant import PLAYER_PER_TEAM


class Game():
    def __init__(self, field, referee, blue_team, yellow_team, blue_team_strategy):
        self.field = field
        self.referee = referee
        self.blue_team = blue_team
        self.yellow_team = yellow_team
        self.blue_team_strategy = blue_team_strategy
        self.delta = None

    def update_strategies(self):
        state = self.referee.command.name
        if state == "HALT":
            self.blue_team_strategy.on_halt()

        elif state == "NORMAL_START":
            self.blue_team_strategy.on_start()

        elif state == "STOP":
            self.blue_team_strategy.on_stop()

    def get_commands(self):
        blue_team_commands = [command for command in self._get_blue_team_commands()] #Copy

        self.blue_team_strategy.commands.clear()

        return blue_team_commands

    def _get_blue_team_commands(self):
        blue_team_commands = self.blue_team_strategy.commands
        #blue_team_commands = self._remove_commands_from_opponent_team(blue_team_commands, self.yellow_team)
        return blue_team_commands

    @staticmethod
    def _remove_commands_from_opponent_team(commands, opponent_team):
        final_commands = []
        for command in commands:
            if command.team != opponent_team:
                final_commands.append(command)
        return final_commands

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
        ball_position = Position(vision_frame.detection.balls[0].x, vision_frame.detection.balls[0].y,
                                 vision_frame.detection.balls[0].z)
        self.field.move_ball(ball_position, delta)

    def _update_players(self, vision_frame, delta):
        blue_team = vision_frame.detection.robots_blue
        yellow_team = vision_frame.detection.robots_yellow

        self._update_players_of_team(blue_team, self.blue_team, delta)
        self._update_players_of_team(yellow_team, self.yellow_team, delta)

    def _update_players_of_team(self, players, team, delta):
        for player in players:
            player_position = Position(player.x, player.y, player.height)
            player_pose = Pose(player_position, player.orientation)
            team.move_and_rotate_player(player.robot_id, player_pose)
