# Under MIT License, see LICENSE.txt
import time

from ai.states.game_state import GameState

import logging
from multiprocessing import Queue
from queue import Empty
from pickle import loads

from Util.singleton import Singleton
from ai.Util.sta_change_command import STAChangeCommand
from ai.executors.play_executor import PlayExecutor
from RULEngine.Debug.uidebug_command_factory import UIDebugCommandFactory
from ai.states.play_state import PlayState


class DebugExecutor(metaclass=Singleton):
    def __init__(self, play_executor, ui_send_queue: Queue, ui_recv_queue: Queue):
        self.logger = logging.getLogger("DebugExecutor")
        self.ui_send_queue = ui_send_queue
        self.ui_recv_queue = ui_recv_queue
        self.play_executor_ref = play_executor
        self.last_time = 0

    def exec(self) -> None:
        while not self.ui_recv_queue.empty():
            try:
                cmd = self.ui_recv_queue.get(block=False)
                self.play_executor_ref.order_change_of_sta(STAChangeCommand(cmd))
            except Empty:
                break

        if time.time() - self.last_time > 0.25:
            self._send_books()
            self.last_time = time.time()

    def _send_books(self) -> None:
        cmd_tactics = {'strategy': PlayState().strategy_book.get_strategies_name_list(),
                       'tactic': PlayState().tactic_book.get_tactics_name_list(),
                       'action': ['None']}

        msg = UIDebugCommandFactory().books(cmd_tactics)
        self.ui_send_queue.put(msg)

    def _send_state(self) -> None:
        pass
        # for player in GameState().our_team.players:
        #     self.ui_send_queue.put(UIDebugCommandFactory.robot_strategic_state())

    def _send_auto_state(self) -> None:
        msg = UIDebugCommandFactory.autoplay_info(GameState().referee.info,
                                                  GameState().referee.team_info,
                                                  PlayState().auto_play.info,
                                                  PlayState().autonomous_flag)
        self.ui_send_queue.put(msg)

        # def _parse_command(self, cmd: UIDebugCommand)->None:
    #     if cmd.is_strategy_cmd():
    #         self._parse_strategy(cmd)
    #
    #     elif cmd.is_tactic_cmd():
    #         self._parse_tactic(cmd)
    #
    #     elif cmd.is_auto_play_cmd():
    #         self.ws.play_state.autonomous_flag = cmd.data['status']
    #         if not self.ws.play_state.autonomous_flag:
    #             self.ws.play_state.set_strategy(self.ws.play_state.get_new_strategy("DoNothing")(self.ws.game_state))
    #     else:
    #         self.logger.warning("received undefined debug command from UI-Debug of type: {0}".format(cmd.cmd_type))
    #
