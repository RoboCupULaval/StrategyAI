# Under MIT License, see LICENSE.txt
"""
    Ce module expose un tableau blanc qui centralise l'information de l'IA.
    Plusieurs méhtodes facilitent l'accès aux informations pertinentes pour le
    cadre STA.
"""
import math as m
from time import time

from .Debug.debug_manager import DebugManager

from RULEngine.Util.geometry import get_distance, get_angle, get_milliseconds
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position

__author__ = 'RoboCupULaval'


class InfoManager:
    """
        InfoManager contient l'information sur la partie, la balle
        et les joueurs. C'est l'objet que les composantes de
        l'intelligence artificielle doivent consulter pour connaître
        l'état de la partie.
    """
    def __init__(self):
        """
        L'infomanager s'initialise avec quatre dictionnaires;
        la partie, la balle, l'équipe alliée et l'équipe adverse.

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
        self.ball = {'position': Position(), 'retro_pose': []}
        self.game = {'play': None, 'state': None, 'sequence': None}
        self.friend = self.init_team_dictionary()
        self.enemy = self.init_team_dictionary()
        self.modules = {}
        self.tactics = list(range(6))
        self.timestamp = 0
        self.debug_manager = DebugManager()


    def init_team_dictionary(self):
        """
        Initialise le dictionnaire de données pour l'équipe passée en paramètre.

        Args:
            team: Équipe de joueur dont on veut initialiser les données.
                Peut être composoée d'un nombre arbitraire de joueurs.

        Returns: Le dictionnaire de données de l'équipe.

        """

        t_player_key = ('pose', 'position', 'orientation', 'kick', 'skill', 'tactic',
                        'next_pose', 'target', 'goal', 'speed', 'retro_pose')
        team_data = {}
        team_data['count'] = 6 #Should not be hardcoded
        for i in range(team_data['count']):
            t_player_data = (Pose(), Position(), 0,
                             0, None, None, None, None, None, None, [])
            team_data[str(i)] = dict(zip(t_player_key, t_player_data))
        return team_data

    def update(self, game_state):
        """ Interface public pour update de l'infomanager. """
        self._update_ball(game_state.field.ball)
        self._update_team(self.friend, game_state.friends)
        self._update_team(self.enemy, game_state.enemies)
        ui_debug_commands = game_state.debug
        if self.debug_manager:
            for command in ui_debug_commands:
                self.debug_manager.add_ui_command(command)
        self.timestamp = game_state.timestamp


    def _update_ball(self, ball):
        """
        Mets à jour la position de la balle, de même que ses anciennes positions.
        """
        self.ball['position'] = ball.position
        self.ball['retro_pose'].append((time(), ball.position))
        if len(self.ball['retro_pose']) > 10:
            self.ball['retro_pose'].pop(0)

    def _update_team(self, team_data, team):
        """
        Mets à jour les données de chacun des joueurs de l'équipe
        passée en paramètre.

        Args:
            team_data: Dictionnaire de données de l'équipe.
            team: Équipe de joueur dont on veut initialiser les données.
                Peut être composée d'un nombre arbitraire de joueurs.
        """
        for i in range(team_data['count']):
            team_data[str(i)]['pose'] = team.players[i].pose
            team_data[str(i)]['position'] = team.players[i].pose.position
            team_data[str(i)]['orientation'] = team.players[i].pose.orientation
            team_data[str(i)]['retro_pose'].append((time(), team.players[i].pose))
            if len(team_data[str(i)]['retro_pose']) > 10:
                team_data[str(i)]['retro_pose'].pop(0)



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

    # Sequences
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

    def get_player_tactic(self, pid):
        return self.tactics[pid]

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
        # FIXME: retirer!
        self.set_player_target(i, action['target'])

    def set_player_target(self, pid, target):
        assert isinstance(target, Position), "target is not a Position"
        self.friend[str(pid)]['target'] = target

    def set_player_tactic(self, i, tactic):
        # FIXME: hack
        self.tactics[i] = tactic


    def set_player_next_action(self, i, next_action):
        # TODO: Enforce valid type
        self.friend[str(i)]['next_pose'] = next_action

    # About Enemy robots
    # ---Getter
    def get_enemy_position(self, i):
        return self.enemy[str(i)]['position']

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

    def get_strategic_state(self):
        """
            Retourne un des 8 états stratégiques possibles.

            * Hors Jeu
            * Mise en jeu
            * Défense avec balle
            * Défense sans balle
            * Offense avec balle
            * Offense sans balle
            * ???
            * ???
        """
        return None

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


    def register_module(self, module_name, module_ref):
        """ Enregistre un module intelligent. """
        self.modules[module_name] = module_ref(self)

    def acquire_module(self, module_name):
        """ Acquiert la référence sur un module. """
        try:
            return self.modules[module_name]
        except KeyError:
            raise NonExistentModule("Le module " + module_name + " n'existe pas.")

class NonExistentModule(Exception):
    """ Est levée si le module intelligent requis n'est pas enregistré. """
    pass
