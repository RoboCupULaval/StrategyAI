from collections import namedtuple

RobotPacket = namedtuple('RobotPacket', 'robot_id command kick_type kick_force dribbler_state charge_kick')
RobotState = namedtuple('RobotState', 'timestamp is_team_yellow packet')

