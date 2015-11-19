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
from .Util.Pose import Pose
from .Util.Position import Position
from .Util.constant import PLAYER_PER_TEAM
from .Communication.vision import Vision
from .Communication.udp_command_sender import UDPCommandSender
import math
import time
from collections import deque
import threading

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


class Framework(object):

    def create_teams(self):
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


    def create_ball(self):
        ball = Ball()
        return ball


    def create_field(self):
        ball = self.create_ball()
        self.field = Field(ball)
        return self.field


    def create_referee(self):
        self.referee = Referee()
        return self.referee


    def create_game(self, strategy):
        blue_team, yellow_team = self.create_teams()
        self.create_field()
        self.referee = self.create_referee()
        self.blue_team_strategy = strategy(self.field, self.referee, blue_team, yellow_team)
        # yellow_team_strategy = WorstStrategy(field, referee, yellow_team, blue_team)

        self.game = Game(self.field, self.referee, blue_team, yellow_team, self.blue_team_strategy)

        return self.game


    def update_game_state(self):
        referee_commands = self.engine.grab_referee_commands()
        if referee_commands:
            referee_command = referee_commands[0]
            self.game.update_game_state(referee_command)


    def update_players_and_ball(self):
        vision_frame = self.vision.get_latest_frame()
        if vision_frame:
            self.game.update_players_and_ball(vision_frame)


    def update_strategies(self):
        self.game.update_strategies()


    def send_robot_commands(self):
        vision_frame = self.vision.get_latest_frame()
        if vision_frame:
            commands = self.game.get_commands()
            for command in commands:
                robot = vision_frame.detection.robots_blue[command.player.id]
                fake_player = Player(0)
                fake_player.pose = Pose(Position(robot.x, robot.y), math.degrees(robot.orientation))
                command.pose.position.x, command.pose.position.y, command.pose.orientation = convertPositionToSpeed(fake_player, command.pose.position.x, command.pose.position.y, command.pose.orientation)

                self.command_sender.send_command(command)

    def __init__(self):
        self.running_thread = None
        self.thread_terminate = threading.Event()

    def start_game(self, strategy, async=False):
        #refereePlugin = rule.RefereePlugin("224.5.23.1", 10003, "RefereePlugin")

        if not self.running_thread:
            self.vision = Vision()
            self.command_sender = UDPCommandSender("127.0.0.1", 20011)
        else:
            self.stop_game()

        self.create_game(strategy)

        self.running_thread = threading.Thread(target=self.game_thread)
        self.running_thread.start()

        if not async:
            self.running_thread.join()

    def game_thread(self):

        times = deque(maxlen=10)
        last_time = time.time()

        while not self.thread_terminate.is_set():  # TODO: Replace with a loop that will stop when the game is over
            #update_game_state(game, engine)
            self.update_players_and_ball()
            self.update_strategies()
            self.send_robot_commands()
            #time.sleep(0.01)
            new_time = time.time()
            times.append(new_time - last_time)
            print(len(times) / sum(times))
            last_time = new_time

    def stop_game(self):

        self.thread_terminate.set()
        self.running_thread.join()
        self.thread_terminate.clear()






