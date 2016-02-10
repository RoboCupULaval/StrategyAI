from time import time

__author__ = 'jbecirovski'



class BlackBoard:
    # TODO Make BlackBoard documentation
    def __init__(self, field, team, opponent_team):
        self.field = field
        self.team = team
        self.opponent_team = opponent_team

        t_player_key = ('pose', 'position', 'orientation', 'kick', 'skill', 'tactic', 'next_pose', 'target',
                        'goal', 'speed', 'retro_pose')
        d_team = {}
        d_op_team = {}
        d_ball = {'position': self.field.ball.position, 'retro_pose': []}
        d_game = dict(zip(('play', 'state', 'sequence'), (None, None, None)))

        for player in self.team.players:
            t_player_data = (player.pose, player.pose.position,
                             player.pose.orientation, 0, None, None, None, None, None, None, [])
            d_team[str(player.id)] = dict(zip(t_player_key, t_player_data))
        d_team['is_yellow'] = self.team.is_team_yellow
        d_team['count'] = len(self.team.players)

        for player in self.opponent_team.players:
            t_player_data = (player.pose, player.pose.position,
                             player.pose.orientation, 0, None, None, None, None, None, None, [])
            d_op_team[str(player.id)] = dict(zip(t_player_key, t_player_data))
        d_op_team['is_yellow'] = self.opponent_team.is_team_yellow
        d_op_team['count'] = len(self.opponent_team.players)

        self.bb = dict(zip(('ball', 'friend', 'enemy', 'game'), (d_ball, d_team, d_op_team, d_game)))

    def __getitem__(self, item):
        return self.bb[item]

    def update(self):
        self.bb['ball']['position'] = self.field.ball.position
        self.bb['ball']['retro_pose'].append((time(), self.field.ball.position))
        if len(self.bb['ball']['retro_pose']) > 10:
                self.bb['ball']['retro_pose'].pop(0)

        for i in range(6):
            self.bb['friend'][str(i)]['pose'] = self.team.players[i].pose
            self.bb['friend'][str(i)]['position'] = self.team.players[i].pose.position
            self.bb['friend'][str(i)]['orientation'] = self.team.players[i].pose.orientation
            self.bb['friend'][str(i)]['retro_pose'].append((time(), self.team.players[i].pose))
            if len(self.bb['friend'][str(i)]['retro_pose']) > 10:
                self.bb['friend'][str(i)]['retro_pose'].pop(0)

            self.bb['enemy'][str(i)]['pose'] = self.opponent_team.players[i].pose
            self.bb['enemy'][str(i)]['position'] = self.opponent_team.players[i].pose.position
            self.bb['enemy'][str(i)]['orientation'] = self.opponent_team.players[i].pose.orientation
            if len(self.bb['enemy'][str(i)]['retro_pose']) > 10:
                self.bb['enemy'][str(i)]['retro_pose'].pop(0)
