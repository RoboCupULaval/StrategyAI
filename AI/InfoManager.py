# Under MIT License, see LICENSE.txt
""" Ce module expose un tableau blanc qui centralise l'information de l'IA.
    Plusieurs méhtodes facilitent l'accès aux informations pertinentes pour le
    cadre STA.
"""
from AI.Data.BlackBoard import BlackBoard
from RULEngine.Util.geometry import * # TODO: remove wildcard
#from Util.geometry import *

__author__ = 'RoboCupULaval'


class InfoManager:
    """ InfoManager fait le lien entre le Blackboard qui contient l'information
        sur la partie et le reste de l'application. Il est majoritairement
        composé de getters et setters
    """
    def __init__(self, field, team, op_team):
        self.black_board = BlackBoard(field, team, op_team)

    def update(self):
        """ Interface public pour update de BlackBoard. """
        self.black_board.update()

    # +++ BLACKBOARD +++
    # About Game
    # ---Getter
    def get_current_play(self):
        return self.black_board['game']['play']

    def get_current_play_sequence(self):
        return self.black_board['game']['sequence']

    # ---Setter
    def set_play(self, play):
        # ToDo : Enforce that play is a subclass of Play()
        self.black_board['game']['play'] = play

    # Special stuff
    def init_play_sequence(self):
        self.black_board['game']['sequence'] = 0

    def inc_play_sequence(self):
        self.black_board['game']['sequence'] += 1

    def get_prev_player_position(self, i):
        idx = (i - 1) % 6
        return self.black_board['friend'][str(idx)]['position']

    # About Friend player
    # ---Getter
    def get_player_target(self, i):
        return self.black_board['friend'][str(i)]['target']

    def get_player_goal(self, i):
        return self.black_board['friend'][str(i)]['goal']

    def get_player_skill(self, i):
        return self.black_board['friend'][str(i)]['skill']

    def get_player_tactic(self, i):
        return self.black_board['friend'][str(i)]['tactic']

    def get_player_position(self, i):
        return self.black_board['friend'][str(i)]['position']

    def get_player_pose(self, i):
        return self.black_board['friend'][str(i)]['pose']

    def get_player_orientation(self, i):
        return self.black_board['friend'][str(i)]['orientation']

    def get_player_kick_state(self, i):
        return self.black_board['friend'][str(i)]['kick']

    def get_count_player(self):
        return self.black_board['friend']['count']

    def get_player_next_action(self, i):
        return self.black_board['friend'][str(i)]['next_pose']

    # ---Setter
    def set_player_skill_target_goal(self, i, action):
        # TODO: Enforce valid types for each attribute
        self.black_board['friend'][str(i)]['skill'] = action['skill']
        self.black_board['friend'][str(i)]['target'] = action['target']
        self.black_board['friend'][str(i)]['goal'] = action['goal']

    def set_player_tactic(self, i, tactic):
        # TODO: Enforce valid type
        self.black_board['friend'][str(i)]['tactic'] = tactic

    def set_player_next_action(self, i, next_action):
        # TODO: Enforce valid type
        self.black_board['friend'][str(i)]['next_pose'] = next_action

    # About Ball
    # ---Getter
    def get_ball_position(self):
        return self.black_board['ball']['position']

    """ +++ INTELLIGENCE MODULE +++ """
    # State machine
    # TODO implement getNextState
    def get_next_state(self):
        return 'debug'

    # TODO implement getNextPlay
    def get_next_play(self, state):
        #  return 'pQueueLeuLeu'
        return 'pTestBench'

    def get_speed(self, i):
        list_pose = self.black_board['friend'][str(i)]['retro_pose']

        if not len(list_pose) == 10:
            return {'speed': 0, 'normal': (0, 0), 'vector': (0, 0)}
        else:
            # Get 10 feedback on previous position
            time_ref, pst_ref = list_pose[9]
            time_sec, pst_sec = list_pose[0]

            # Pre calculations
            angle = get_angle(pst_ref.position, pst_sec.position)
            dst_tot = get_distance(pst_ref.position, pst_sec.position)
            time_tot = get_milliseconds(time_ref) - get_milliseconds(time_sec)

            # Final calculations
            speed = dst_tot / time_tot
            normal = (m.cos(m.radians(angle)), m.sin(m.radians(angle)))
            vector = (normal[0] * speed, normal[1] * speed)

            # print('SPEED:{0:.4f} | NORMAL:{1} | VECTOR:{2}'.format(speed, normal, vector))
            return {'speed': speed, 'normal': normal, 'vector': vector}

    @property
    def get_ball_speed(self):
        list_pose = self.black_board['ball']['retro_pose']

        if not len(list_pose) == 10:
            return {'speed': 0, 'normal': (0, 0), 'vector': (0, 0)}
        else:
            # Get 10 feedback on previous position
            time_ref, pst_ref = list_pose[9]
            time_sec, pst_sec = list_pose[0]

            # Pre calculations
            angle = get_angle(pst_ref, pst_sec)
            dst_tot = get_distance(pst_ref, pst_sec)
            time_tot = get_milliseconds(time_ref) - get_milliseconds(time_sec)

            # Final calculations
            speed = dst_tot / time_tot
            normal = (m.cos(m.radians(angle)), m.sin(m.radians(angle)))
            vector = (normal[0] * speed, normal[1] * speed)

            # print('SPEED:{0:.4f} | NORMAL:{1} | VECTOR:{2}'.format(speed, normal, vector))
            return {'speed': speed, 'normal': normal, 'vector': vector}
