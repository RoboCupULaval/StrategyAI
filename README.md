#PythonFramework
A Python framework to develop all the required tools to ease the development of a strategy using the Rule library

To create a strategy you may derive a class from Strategy and implement the functions.
You can check the class in Strategy.

To execute your strategy, you may change create_game() in main.py
yellow_team_strategy = YourStrategyName(field, referee, yellow_team, blue_team)
You can play your strategie against your own of course.

##API
The types of command objects are in Command folder. You can instantiate a command and call self._send_command(command)
in your strategy class. Commands need a robot and your team as parameter.
Note that robot dribble by default

Command.SetSpeed(player, team, pose)
pose contain x, y and theta speed in m/s. The robot will move with this speed
ex : Command.SetSpeed(player, team, Pose(Position(1, 1), 1)) => x, y and theta speed = 1

Command.MoveTo(player, team, position)
position contain a cartesian coord of the map, the robot will move there
ex : Command.MoveTo(player, team, Position(0, 0)) => deplace the robot to 0,0 on the field

Command.Rotate(player, team, orientation)
orientation contain an angle in degree for its orientation
ex : Command.Rotate(player, team, 90) => rotate to 90 degree in global coord system

Command.MoveToAndRotate(player, team, pose)
pose contain a position and an orientation so the robot set as position
ex : Command.MoveToAndRotate(player, team, Pose(Position(0, 0), 0))) => set the position to 0, 0 coord and orientation to 0 degree

Command.Kick(player, team, kick_speed=5)
use the kicker
ex : Command.Kick(player, team, kick_speed=7) kick at 7m/s

Command.Stop(player, team)
simply stop the robot