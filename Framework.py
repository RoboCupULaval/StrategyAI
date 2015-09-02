import sys
import os.path
path, file = os.path.split(os.path.realpath(__file__))
print (os.path.join(path, "Communication"))
sys.path.append(os.path.join(path, "Communication"))
from .Game.Ball import Ball
from .Game.Field import Field
from .Game.Game import Game
from .Game.Player import Player
from .Game.Referee import Referee
from .Game.Team import Team
from .Util.constant import PLAYER_PER_TEAM
from .Communication.vision import Vision
from . import rule

def create_teams():
    blue_players = []
    yellow_players = []
    for i in range(PLAYER_PER_TEAM):
        bPlayer = Player(i)
        yPlayer = Player(i)
        blue_players.append(bPlayer)
        yellow_players.append(yPlayer)
    blue_team = Team(blue_players, False)
    yellow_team = Team(yellow_players, True)
    return blue_team, yellow_team


def create_ball():
    ball = Ball()
    return ball


def create_field():
    ball = create_ball()
    field = Field(ball)
    return field


def create_referee():
    referee = Referee()
    return referee


def create_game(strategy):
    blue_team, yellow_team = create_teams()
    field = create_field()
    referee = create_referee()
    blue_team_strategy = strategy(field, referee, blue_team, yellow_team)
    # yellow_team_strategy = WorstStrategy(field, referee, yellow_team, blue_team)

    game = Game(field, referee, blue_team, yellow_team, blue_team_strategy)

    return game


def update_game_state(game, engine):
    referee_commands = engine.grab_referee_commands()
    if referee_commands:
        referee_command = referee_commands[0]
        game.update_game_state(referee_command)


def update_players_and_ball(game, vision):
    vision_frames = vision.get_frames()
    if vision_frames:
        vision_frame = vision_frames[0]
        game.update_players_and_ball(vision_frame)


def update_strategies(game):
    game.update_strategies()


def send_robot_commands(game, engine):
    commands = game.get_commands()
    for command in commands:
        robot_command = command.to_robot_command()
        engine.send_robot_command(robot_command)


def start_game(strategy):

    engine = rule.Rule()

    visionPlugin = rule.VisionPlugin("224.5.23.22", 10022, "VisionPlugin");
    refereePlugin = rule.RefereePlugin("224.5.23.1", 10003, "RefereePlugin");
    navigatorPlugin = rule.UDPNavigatorPlugin(20011, "127.0.0.1", "UDPNavigatorPlugin");
    engine.install_plugin(visionPlugin)
    engine.install_plugin(refereePlugin)
    engine.install_plugin(navigatorPlugin)

    vision = Vision()

    engine.start()

    game = create_game(strategy)

    while True:  # TODO: Replace with a loop that will stop when the game is over
        update_game_state(game, engine)
        update_players_and_ball(game, vision)
        update_strategies(game)
        send_robot_commands(game, engine)

    engine.stop()
