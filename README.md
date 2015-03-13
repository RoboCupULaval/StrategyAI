#PythonFramework
A Python framework to develop all the required tools to ease the development of a strategy using the Rule library

To create a strategy you may derive a class from Strategy and implement the functions.
You can check the class in Strategy.

To execute your strategy, you may change create_game() in main.py
```python
yellow_team_strategy = YourStrategyName(field, referee, yellow_team, blue_team)
```
Beware, the positions on the terrain are different depending on the side you play!

###Utils
Utility class are there to structure some important data, currently Pose and Position are defined:
<b>Position</b>(x, y, z)
```python
aPosition = Utils.Position(10, 10, 0)  #instantiate a position with coord : x=10, y=10, z=0
```
<br>

<b>Pose</b>(Position(), theta)<br>
This structure contain a position and an orientation
```python
myRobotPose = Utils.Pose(Position(10, 10, 0),90)  #instantiate a position with coord : x=10, y=10, z=0 and orientation of 90 degree
```
<br>
###Simulation Data
You will need to access data from the simulation to make your strategies.

<b>Team Players</b> <br>
exemple on how to iterate your own player and print there id
```python
for player in self.team.players:
  print(player.id)
```
<br>

<b>Opponent Players</b> <br>
exemple on how to iterate your oponnent player and print there Pose
```python
for player in self.opponent_team.players:
  print(player.pose)
```
<br>
<b>Ball</b> <br>
exemple on how to print the ball Position
```python
print("self.field.ball.position")
```


##API
The types of command objects are in Command folder. You can instantiate a command and call self._send_command(command)
in your strategy class. Commands need a robot and your team as parameter.
Note that robot dribble by default

<b>SetSpeed</b>(player, team, pose)<br>
pose contain x, y and theta speed in m/s. The robot will move with this speed
```python
Command.SetSpeed(player, team, Pose(Position(1, 1), 1))  #x, y and theta speed = 1
```
<br>

<b>MoveTo</b>(player, team, position)<br>
position contain a cartesian coord of the map, the robot will move there
```python
Command.MoveTo(player, team, Position(0, 0))  #deplace the robot to 0,0 on the field
```
<br>

<b>Rotate</b>(player, team, orientation)<br>
orientation contain an angle in degree for its orientation
```python
Command.Rotate(player, team, 90)  #rotate to 90 degree in global coord system
```
<br>

<b>MoveToAndRotate</b>(player, team, pose)<br>
pose contain a position and an orientation so the robot set as position
```python
Command.MoveToAndRotate(player, team, Pose(Position(0, 0), 0))) #set the position to 0, 0 coord and orientation to 0
```
<br>

<b>Kick</b>(player, team, kick_speed=5)<br>
use the kicker
```python
Command.Kick(player, team, kick_speed=7) #kick at 7m/s
```
<br>

<b>Stop</b>(player, team)<br>
simply stop the robot

