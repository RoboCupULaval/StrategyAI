# Under MIT License, see LICENSE.txt
import time
from typing import List, Dict
import logging

from Util import Pose, Position, AICommand, Singleton
from ai.STA.Strategy.human_control import HumanControl


from RULEngine.Debug.uidebug_command_factory import UIDebugCommandFactory
from Util.role import Role
from config.config_service import ConfigService
from ai.Util.sta_change_command import STAChangeCommand
from ai.Algorithm.auto_play import SimpleAutoPlay
from ai.states.game_state import GameState
from ai.states.play_state import PlayState


class PlayExecutor(metaclass=Singleton):

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

        cfg = ConfigService()
        self.auto_play = SimpleAutoPlay()
        self.play_state = PlayState()
        self.play_state.autonomous_flag = cfg.config_dict["GAME"]["autonomous_play"] == "true"
        self.last_available_players = {}
        self.goalie_id = -1

    def exec(self) -> List[AICommand]:
        """
        Execute la stratégie courante et envoie le status des robots et les livres de tactiques et stratégies

        :return: None
        """

        # if PlayState().autonomous_flag:
        #     if GameState().game.referee.team_info['ours']['goalie'] != self.goalie_id:
        #         self.goalie_id = GameState().game.referee.team_info['ours']['goalie']
        #         GameState().update_player_for_locked_role(self.goalie_id, Role.GOALKEEPER)
        #     self.auto_play.update(self._has_available_players_changed())

        return self._execute_strategy()

    def order_change_of_sta(self, cmd: STAChangeCommand):
        if cmd.is_strategy_change_command():
            self._change_strategy(cmd)
        elif cmd.is_tactic_change_command():
            self._change_tactic(cmd)

    def _change_strategy(self, cmd: STAChangeCommand):
        new_strategy = self.play_state.get_new_strategy(cmd.data["strategy"])
        self.play_state.set_strategy(new_strategy)

    def _change_tactic(self, cmd: STAChangeCommand):

        try:
            this_player = GameState().get_player(cmd.data['id'])
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

        if isinstance(self.play_state.current_strategy, HumanControl):
            hc = self.play_state.current_strategy
            hc.assign_tactic(tactic, player_id)
        else:
            hc = HumanControl(GameState())
            hc.assign_tactic(tactic, player_id)
            self.play_state.set_strategy(hc)

    def _execute_strategy(self) -> List[AICommand]:
        # Applique un stratégie par défault s'il n'en a pas (lors du démarage par exemple)
        # TODO change this so we don't send humancontrol when nothing is set/ Donothing would be better
        if self.play_state.current_strategy is None:
            self.play_state.set_strategy(PlayState().get_new_strategy("HumanControl")(GameState()))
        return self.play_state.current_strategy.exec()




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
