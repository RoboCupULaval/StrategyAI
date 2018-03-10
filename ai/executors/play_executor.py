# Under MIT License, see LICENSE.txt

from typing import List, Dict
import logging

from multiprocessing import Queue

from Util.engine_command import EngineCommand
from Util import Pose, Position, AICommand, Singleton
from ai.GameDomainObjects import Player
from ai.STA.Strategy.human_control import HumanControl

from RULEngine.Debug.uidebug_command_factory import UIDebugCommandFactory

from ai.executors.pathfinder_module import generate_path
from config.config_service import ConfigService
from ai.Util.sta_change_command import STAChangeCommand
from ai.Algorithm.auto_play import SimpleAutoPlay
from ai.states.game_state import GameState
from ai.states.play_state import PlayState


class PlayExecutor(metaclass=Singleton):

    def __init__(self, ui_send_queue: Queue):
        self.logger = logging.getLogger(self.__class__.__name__)

        cfg = ConfigService()
        self.auto_play = SimpleAutoPlay()
        self.play_state = PlayState()
        self.game_state = GameState()
        self.play_state.autonomous_flag = cfg.config_dict["GAME"]["autonomous_play"] == "true"
        self.last_available_players = {}
        self.goalie_id = -1
        self.ui_send_queue = ui_send_queue

    def exec(self) -> List[EngineCommand]:
        """
        Execute la stratégie courante et envoie le status des robots et les livres de tactiques et stratégies

        :return: None
        """

        # if self.play_state.autonomous_flag:
        #     if GameState().game.referee.team_info['ours']['goalie'] != self.goalie_id:
        #         self.goalie_id = GameState().game.referee.team_info['ours']['goalie']
        #         GameState().update_player_for_locked_role(self.goalie_id, Role.GOALKEEPER)
        #     self.auto_play.update(self._has_available_players_changed())
        ai_cmds = self._execute_strategy()
        engine_cmds = []

        for player, ai_cmd in ai_cmds.items():
            if ai_cmd.pathfinder_on and ai_cmd.target:
                path = generate_path(self.game_state, player, ai_cmd)
            else:
                path = None
            engine_cmds.append(self.generate_engine_cmd(player, ai_cmd, path))

        return engine_cmds

    def generate_engine_cmd(self, player: Player, ai_cmd: AICommand, path):
        return EngineCommand(robot_id=player.id,
                             path=path,
                             kick_type=ai_cmd.kick_type,
                             kick_force=ai_cmd.kick_force,
                             dribbler_active=ai_cmd.dribbler_active,
                             cruise_speed=ai_cmd.cruise_speed * 1000,
                             target_orientation=ai_cmd.target.orientation if ai_cmd.target else None,
                             target_speed=ai_cmd.target_speed,
                             charge_kick=ai_cmd.charge_kick)

    def order_change_of_sta(self, cmd: STAChangeCommand):
        if cmd.is_strategy_change_command():
            self._change_strategy(cmd)
        elif cmd.is_tactic_change_command():
            self._change_tactic(cmd)

    def _change_strategy(self, cmd: STAChangeCommand):
        self.play_state.current_strategy = cmd.data["strategy"]

    def _change_tactic(self, cmd: STAChangeCommand):

        try:
            this_player = GameState().our_team.available_players[cmd.data['id']]
        except KeyError as id:
            print("Invalid player id: {}".format(cmd.data['id']))
            return
        player_id = this_player.id
        tactic_name = cmd.data['tactic']
        # TODO ui must send better packets back with the args.
        target = cmd.data['target']
        target = Pose(Position(target[0], target[1]), this_player.pose.orientation)
        args = cmd.data.get('args', "")
        try:
            tactic = self.play_state.get_new_tactic(tactic_name)(GameState(), this_player, target, args)
        except Exception as e:
            print(e)
            print("La tactique n'a pas été appliquée par "
                  "cause de mauvais arguments.")
            raise e

        if not isinstance(self.play_state.current_strategy, HumanControl):
            self.play_state.current_strategy = "HumanControl"
        self.play_state.current_strategy.assign_tactic(tactic, player_id)

    def _execute_strategy(self) -> Dict[Player, AICommand]:
        # Applique un stratégie par défault s'il n'en a pas (lors du démarage par exemple)
        # TODO change this so we don't send humancontrol when nothing is set/ Donothing would be better
        if self.play_state.current_strategy is None:
            self.play_state.current_strategy = "HumanControl"
        return self.play_state.current_strategy.exec()

    def _send_robots_status(self) -> None:
        states = self.play_state.current_tactical_state
        cmds = []
        for player, tactic_name, action_name, target in states:
            if action_name != 'Stop':
                target_tuple = (int(target.position.x), int(target.position.y))
                cmd = UIDebugCommandFactory().robot_strategic_state(player,
                                                                    tactic_name,
                                                                    action_name,
                                                                    target_tuple)
                cmds.append(cmd)
        self.ui_send_queue.put(cmds)


    # def _has_available_players_changed(self) -> bool:
    #     available_players = GameState().our_team.available_players
    #     player_change = False
    #     for i in available_players:
    #         if i not in self.last_available_players:
    #             player_change = True
    #             break
    #     if not player_change:
    #         for i in self.last_available_players:
    #             if i not in available_players:
    #                 player_change = True
    #                 break
    #     self.last_available_players = available_players.copy()
    #     return player_change

