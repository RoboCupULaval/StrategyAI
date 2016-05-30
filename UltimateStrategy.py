#Under MIT License, see LICENSE.txt
""" Module supérieur de l'IA """

from RULEngine.Strategy.Strategy import Strategy
from RULEngine.Command import Command
from RULEngine.Util.Pose import Pose
import RULEngine.Util.geometry as geometry

from UltimateStrat.Executor.CoachExecutor import CoachExecutor
from UltimateStrat.Executor.PlayExecutor import PlayExecutor
from UltimateStrat.Executor.TacticExecutor import TacticExecutor
from UltimateStrat.Executor.SkillExecutor import SkillExecutor
from UltimateStrat.InfoManager import InfoManager

__author__ = 'RoboCupULaval'

class UltimateStrategy(Strategy):
    """ Niveau supérieur de l'IA, est appelé et créé par Framework.

        La classe créée une partie du GameState et exécute la boucle principale
        de la logique de l'IA.

        À chaque itération, les Executors sont déclenchés et InfoManager est
        mit à jour.

        À la fin d'une itération, les commandes des robots sont récupérées dans
        l'InfoManager et finalement envoyée au serveur de communication.
    """

    def __init__(self, field, referee, team, opponent_team, is_team_yellow=False):
        """ Constructeur, réplique une grande partie du GameState pour
            construire l'InfoManager. TODO: éliminer cette redondance (DRY)
        """
        Strategy.__init__(self, field, referee, team, opponent_team)

        # Create InfoManager
        self.team.is_team_yellow = is_team_yellow
        self.info_manager = InfoManager(field, team, opponent_team)

        # Create Executors
        self.ex_coach = CoachExecutor(self.info_manager)
        self.ex_play = PlayExecutor(self.info_manager)
        self.ex_tactic = TacticExecutor(self.info_manager)
        self.ex_skill = SkillExecutor(self.info_manager)

    def on_start(self):
        """ Boucle principale de l'IA, est appelé par Framework """
        self.info_manager.update()
        # Main Strategy sequence
        self.ex_coach.exec()
        self.ex_play.exec()
        self.ex_tactic.exec()
        self.ex_skill.exec()

        # ::COMMAND SENDER::
        # TODO: Extraire en méthode
        for i in range(6):
            next_action = self.info_manager.get_player_next_action(i)
            if isinstance(next_action, Pose):

                # Move Manager :: if next action is Pose
                command = Command.MoveToAndRotate(self.team.players[i],
                                                  self.team,
                                                  next_action)
                self._send_command(command)
            elif isinstance(next_action, int):

                # Kick Manager :: if next action is int
                if not 0 < next_action <= 8:
                    next_action = 5

                command = Command.Kick(self.team.players[i],
                                       self.team,
                                       next_action)
                self._send_command(command)

                player_pos = self.info_manager.get_player_position(i)
                ball_pos = self.info_manager.get_ball_position()
                if geometry.get_distance(player_pos, ball_pos) > 150:
                    player_pos = self.info_manager.get_player_position(i)
                    self.info_manager.set_player_next_action(i, player_pos)
            else:

                # Path Manager :: if next action is list of Pose
                # TODO: refactor dans PathExecutor
                if geometry.get_distance(self.info_manager.get_player_position(i),
                                         next_action[0].position) < 180:
                    next_pose = next_action.pop(0)
                    if len(next_action) == 0:
                        next_action = next_pose
                    self.info_manager.set_player_next_action(i, next_action)
                    command = Command.MoveToAndRotate(self.team.players[i],
                                                      self.team,
                                                      next_pose)
                    self._send_command(command)
                else:
                    # TODO: code smell
                    command = Command.MoveToAndRotate(self.team.players[i],
                                                      self.team,
                                                      next_action[0])
                    self._send_command(command)

    def on_halt(self):
        self.on_start()

    def on_stop(self):
        self.on_start()
