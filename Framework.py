import sys
import os.path
path, file = os.path.split(os.path.realpath(__file__))
#print (os.path.join(path, "Communication"))
sys.path.append(os.path.join(path, "Communication"))
from .Game.Ball import Ball
from .Game.Field import Field
from .Game.Game import Game
from .Game.Player import Player
from .Game.Referee import Referee
from .Game.Team import Team
from .Util.Pose import Pose
from .Util.Position import Position
from .Util.constant import PLAYER_PER_TEAM
from .Communication.vision import Vision
from .Communication.udp_command_sender import UDPCommandSender
import math
import time
from collections import deque

#Gui imports are optional
try:
    from PyQt4 import QtGui, QtCore
    qt_installed = True
except ImportError:
    qt_installed = False

if qt_installed:
    from .Gui.VSSL import FieldDisplay


def convertPositionToSpeed(player, x, y, theta):
    current_theta = player.pose.orientation
    current_x = player.pose.position.x
    current_y = player.pose.position.y
    theta_direction = theta - current_theta
    if theta_direction >= math.pi:
        theta_direction -= 2 * math.pi
    elif theta_direction <= -math.pi:
        theta_direction += 2*math.pi

    theta_speed = 2 if abs(theta_direction) > 0.2 else 0.4
    new_theta = theta_speed if theta_direction > 0 else -theta_speed

    direction_x = x - current_x
    direction_y = y - current_y
    norm = math.hypot(direction_x, direction_y)
    speed = 1 if norm >= 50 else 0
    if norm:
        direction_x /= norm
        direction_y /= norm
    angle = math.atan2(direction_y, direction_x)
    cosangle = math.cos(math.radians(-current_theta))
    sinangle = math.sin(math.radians(-current_theta))
    new_x = (direction_x * cosangle - direction_y * sinangle) * speed
    new_y = (direction_y * cosangle + direction_x * sinangle) * speed

    return new_x, new_y, new_theta


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
    vision_frame = vision.get_latest_frame()
    if vision_frame:
        game.update_players_and_ball(vision_frame)


def update_strategies(game):
    game.update_strategies()


def send_robot_commands(game, vision, command_sender):
    vision_frame = vision.get_latest_frame()
    if vision_frame:
        commands = game.get_commands()
        for command in commands:
            robot = vision_frame.detection.robots_blue[command.player.id]
            fake_player = Player(0)
            fake_player.pose = Pose(Position(robot.x, robot.y), math.degrees(robot.orientation))
            command.pose.position.x, command.pose.position.y, command.pose.orientation = convertPositionToSpeed(fake_player, command.pose.position.x, command.pose.position.y, command.pose.orientation)

            command_sender.send_command(command)

def start_game(strategy, gui=False):

    #refereePlugin = rule.RefereePlugin("224.5.23.1", 10003, "RefereePlugin")
    vision = Vision()
    command_sender = UDPCommandSender("127.0.0.1", 20011)

    game = create_game(strategy)

    times = deque(maxlen=10)

    last_time = time.time()

    def main_loop():
        #update_game_state(game, engine)
        update_players_and_ball(game, vision)
        update_strategies(game)
        send_robot_commands(game, vision, command_sender)

    if gui:
        if not qt_installed:
            sys.exit("PyQt4 is not installed")
        app = QtGui.QApplication(sys.argv)
        FieldDisplay(main_loop, game, vision)
        sys.exit(app.exec_())
    else:
        while True:  # TODO: Replace with a loop that will stop when the game is over
            main_loop()
            #time.sleep(0.01)
            new_time = time.time()
            times.append(new_time - last_time)
            print(len(times) / sum(times))
            last_time = new_time

