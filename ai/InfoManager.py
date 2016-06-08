# Under MIT License, see LICENSE.txt
""" Ce module expose un tableau blanc qui centralise l'information de l'IA.
    Plusieurs méhtodes facilitent l'accès aux informations pertinentes pour le
    cadre STA.
"""
from RULEngine.Util.geometry import * # TODO: remove wildcard
from time import time

__author__ = 'RoboCupULaval'


class InfoManager:
    """ InfoManager fait le lien entre le Blackboard qui contient l'information
        sur la partie et le reste de l'application. Il est majoritairement
        composé de getters et setters
    """
    def __init__(self, field, team, op_team):
        self.field = field
        self.team = team
        self.opponent_team = op_team

        self.ball = {'position': self.field.ball.position, 'retro_pose': []}
        self.game = {'play': None, 'state': None, 'sequence': None}
        self.friend = self.init_team_dictionary(self.team)
        self.enemy = self.init_team_dictionary(self.opponent_team)

    def init_team_dictionary(self, team):
        t_player_key = ('pose', 'position', 'orientation', 'kick', 'skill', 'tactic',
                        'next_pose', 'target', 'goal', 'speed', 'retro_pose')
        team_data = {}
        for player in team.players:
            t_player_data = (player.pose, player.pose.position, player.pose.orientation,
                             0, None, None, None, None, None, None, [])
            team_data[str(player.id)] = dict(zip(t_player_key, t_player_data))
        team_data['is_yellow'] = self.team.is_team_yellow
        team_data['count'] = len(self.team.players)
        return team_data

    def update(self):
        """ Interface public pour update de BlackBoard. """
        self.update_ball()
        self.update_team(self.friend, self.team)
        self.update_team(self.enemy, self.opponent_team)


    def update_ball(self):
        self.ball['position'] = self.field.ball.position
        self.ball['retro_pose'].append((time(), self.field.ball.position))
        if len(self.ball['retro_pose']) > 10:
            self.ball['retro_pose'].pop(0)

    def update_team(self, team_data, team):
        for i in range(team_data['count']):
            team_data[str(i)]['pose'] = team.players[i].pose
            team_data[str(i)]['position'] = team.players[i].pose.position
            team_data[str(i)]['orientation'] = team.players[i].pose.orientation
            team_data[str(i)]['retro_pose'].append((time(), team.players[i].pose))
            if len(team_data[str(i)]['retro_pose']) > 10:
                team_data[str(i)]['retro_pose'].pop(0)


    # +++ BLACKBOARD +++
    # About Game
    # ---Getter
    def get_current_play(self):
        return self.game['play']

    def get_current_play_sequence(self):
        return self.game['sequence']

    # ---Setter
    def set_play(self, play):
        # TODO : Enforce that play is a subclass of Play()
        self.game['play'] = play

    # Special stuff
    def init_play_sequence(self):
        self.game['sequence'] = 0

    def inc_play_sequence(self):
        self.game['sequence'] += 1

    def get_prev_player_position(self, i):
        # TODO : Refactor to take into account teams of less/more than 6 players
        idx = (i - 1) % 6
        return self.friend[str(idx)]['position']


    # About Friend player
    # ---Getter
    def get_player_target(self, i):
        return self.friend[str(i)]['target']

    def get_player_goal(self, i):
        return self.friend[str(i)]['goal']

    def get_player_skill(self, i):
        return self.friend[str(i)]['skill']

    def get_player_tactic(self, i):
        return self.friend[str(i)]['tactic']

    def get_player_position(self, i):
        return self.friend[str(i)]['position']

    def get_player_pose(self, i):
        return self.friend[str(i)]['pose']

    def get_player_orientation(self, i):
        return self.friend[str(i)]['orientation']

    def get_player_kick_state(self, i):
        return self.friend[str(i)]['kick']

    def get_count_player(self):
        return self.friend['count']

    def get_player_next_action(self, i):
        return self.friend[str(i)]['next_pose']

    # ---Setter
    def set_player_skill_target_goal(self, i, action):
        # TODO: Enforce valid types for each attribute
        self.friend[str(i)]['skill'] = action['skill']
        self.friend[str(i)]['goal'] = action['goal']
        self.friend[str(i)]['target'] = action['target']

    def set_player_tactic(self, i, tactic):
        # TODO: Enforce valid type
        self.friend[str(i)]['tactic'] = tactic

    def set_player_next_action(self, i, next_action):
        # TODO: Enforce valid type
        self.friend[str(i)]['next_pose'] = next_action

    # About Ball
    # ---Getter
    def get_ball_position(self):
        return self.ball['position']

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
        list_pose = self.friend[str(i)]['retro_pose']

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
        list_pose = self.ball['retro_pose']

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
