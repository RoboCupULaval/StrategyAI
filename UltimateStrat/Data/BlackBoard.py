__author__ = 'jbecirovski'



class BlackBoard:
    # TODO Make BlackBoard documentation
    def __init__(self, field, team, opponent_team):

        t_player_key = ('pose', 'position', 'x', 'y', 'orientation', 'kick', 'skill', 'tactic', 'next_pose', 'target',
                        'goal')
        d_team = {}
        d_op_team = {}
        d_ball = dict(zip(('position', 'x', 'y'), (field.ball.position, field.ball.position.x, field.ball.position.y)))
        d_game = dict(zip(('play', 'state', 'sequence'), (None, None, None)))

        for player in team.players:
            t_player_data = (player.pose, player.pose.position, player.pose.position.x, player.pose.position.y,
                             player.pose.orientation, 0, None, None, None, None, None)
            d_team[str(player.id)] = dict(zip(t_player_key, t_player_data))
        d_team['is_yellow'] = team.is_team_yellow
        d_team['count'] = len(team.players)

        for player in opponent_team.players:
            t_player_data = (player.pose, player.pose.position, player.pose.position.x, player.pose.position.y,
                             player.pose.orientation, 0, None, None)
            d_op_team[str(player.id)] = dict(zip(t_player_key, t_player_data))
        d_op_team['is_yellow'] = opponent_team.is_team_yellow
        d_op_team['count'] = len(opponent_team.players)

        self.bb = dict(zip(('ball', 'friend', 'enemy', 'game'), (d_ball, d_team, d_op_team, d_game)))

    def __getitem__(self, item):
        return self.bb[item]