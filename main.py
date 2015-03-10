from Game.Ball import Ball
from Game.Field import Field
from Game.Game import Game
from Game.Player import Player
from Game.Referee import Referee
from Game.Team import Team
from Strategy.BestStrategy import BestStrategy
from Strategy.WorstStrategy import WorstStrategy


def create_teams():
    blue_players = []
    yellow_players = []
    for i in range(12):
        player = Player(i)
        if i < 6:
            blue_players.append(player)
        else:
            yellow_players.append(player)
    blue_team = Team(blue_players)
    yellow_team = Team(yellow_players)
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


def create_game():
    blue_team, yellow_team = create_teams()
    field = create_field()
    referee = create_referee()
    blue_team_strategy = BestStrategy(field, referee, blue_team, yellow_team)
    yellow_team_strategy = WorstStrategy(field, referee, yellow_team, blue_team)

    game = Game(field, referee, blue_team, yellow_team, blue_team_strategy, yellow_team_strategy)

    return game


def update_game_state(game, engine):
    referee_commands = engine.grab_referee_commands()
    if referee_commands:
        referee_command = referee_commands[0]
        game.update_game_state(referee_command)


def update_players_and_ball(game, engine):
    vision_frames = engine.grab_vision_frames()
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


if __name__ == '__main__':
    import rule

    engine = rule.Rule()
    engine.start()

    game = create_game()

    while True:  # TODO: Replace with a loop that will stop when the game is over
        update_game_state(game, engine)
        update_players_and_ball(game, engine)
        update_strategies(game)
        send_robot_commands(game, engine)

    engine.stop()
