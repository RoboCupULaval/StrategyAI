# Under MIT License, see LICENSE.txt
__author__ = 'RoboCupULaval'

from time import time
import math
from RULEngine.Util.Position import Position


class BlackBoard:
    """
    Blackboard consists of four dictionaries that contain information on the ball, friendly team,
    opponent team and on the game itself.

    Blackboard est un objet regroupant 4 dictionnaires. Ceux-ci contiennent de l'information
    sur l'état de la balle, de la partie, de l'équipe alliée et de l'équipe adverse.

    Ces 4 dictionnaires sont divisés comme suit :

    ball : {position : Util.Position(), retro_pose : liste des 10 précédents
                                                        tuples (time(), Util.Position()}

    game : {play : STP.Play.Play(), state : ???, sequence : play_sequence}
    Play sequence est défini dans chacun des play; il s'agit d'une liste de 6
    tactiques qui seront assignées à chacun des robots pour le play sélectionné.


    friend et ennemy sont divisés de la même façon :
    {is_yellow : Bool, count : int, id(6 fois) : dict}

    Les 6 dernières clés correpondent à l'identifiant de chacun des robots, et est
    mappé à un autre dictionnaire contenant l'information sur le joueur spécifié :

    {pose : Util.Pose(), position : Util.Position(), orientation : int/float, kick : Bool,
     skill : STP.Skill.Skill(), tactic : STP.Tactic.Tactic(), next_pose : ???,
     target : ???, goal : ???, speed : float, retro_pose : Liste des 10 précédents
                                                            tuples (time(), Util.Pose()}



    """
    def __init__(self, field, team, opponent_team):
        """
        Initialise le BlackBoard avec le terrain et les deux équipes. La majorité des valeurs des
        robots sont vides, elles seront remplies par l'info manager au cours de la partie.
        Args:
            field: Terrain de jeu utilisé (instance de Game.Field).
            team: Équipe alliée (instance de Game.Team)
            opponent_team: Équipe adverse (instance de Game.Team)

        Returns: Void

        """
        self.field = field
        self.team = team
        self.opponent_team = opponent_team

        t_player_key = ('pose', 'position', 'orientation', 'kick', 'skill', 'tactic', 'next_pose', 'target',
                        'goal', 'speed', 'retro_pose')
        d_team = {}
        d_op_team = {}
        d_ball = {'position': self.field.ball.position, 'retro_pose': []}
        d_game = {'play': None, 'state': None, 'sequence': None}

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

        self.bb = {'ball': d_ball, 'friend': d_team, 'enemy': d_op_team, 'game': d_game}

    def __getitem__(self, item):
        return self.bb[item]

    def update(self):
        """
        Mets à jour les informations sur la balle via self.field, puis
        itère sur chacun des robots alliés et adverses pour mettre à jour
        leurs informations.

        Returns:

        """
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
            self.bb['ennemy'][str(i)]['retro_pose'].append((time(), self.opponent_team.players[i].pose))
            if len(self.bb['enemy'][str(i)]['retro_pose']) > 10:
                self.bb['enemy'][str(i)]['retro_pose'].pop(0)
