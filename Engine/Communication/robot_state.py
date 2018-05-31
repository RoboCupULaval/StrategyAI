from collections import namedtuple

RobotPacket = namedtuple('RobotPacket', 'robot_id command kick_type kick_force dribbler_active dribbler_speed charge_kick')
RobotState = namedtuple('RobotState', 'timestamp is_team_yellow packet')

