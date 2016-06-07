#Under MIT License, see LICENSE.txt
from collections import namedtuple

from . import Referee
from ..Util.Pose import Pose
from ..Util.Position import Position
from ..Util.constant import PLAYER_PER_TEAM

GameState = namedtuple('GameState', ['field', 'referee', 'friends',
                                     'enemies', 'debug'])

class Game():
    def __init__(self, field, referee, blue_team, yellow_team, strategy):
        self.field = field
        self.referee = referee
        self.blue_team = blue_team
        self.yellow_team = yellow_team
        self.strategy = strategy

        if strategy.is_team_yellow:
            self.friends = yellow_team
            self.enemies = blue_team
        else:
            self.friends = blue_team
            self.enemies = yellow_team

        self.delta = None

    def update_strategies(self):

        game_state = self.get_game_state()

        state = self.referee.command.name
        if state == "HALT":
            self.strategy.on_halt(game_state)

        elif state == "NORMAL_START":
            self.strategy.on_start(game_state)

        elif state == "STOP":
            self.strategy.on_stop(game_state)

    def get_game_state(self):

        return GameState(field=self.field,
                         referee=self.referee,
                         friends=self.friends,
                         enemies=self.enemies,
                         debug={})

    def get_commands(self):
        blue_team_commands = [command for command in self._get_blue_team_commands()] #Copy

        self.strategy.commands.clear()

        return blue_team_commands

    def _get_blue_team_commands(self):
        blue_team_commands = self.strategy.commands
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
