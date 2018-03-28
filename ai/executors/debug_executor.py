# Under MIT License, see LICENSE.txt
import logging
import time
from multiprocessing import Queue
from queue import Empty

from Debug.debug_command_factory import DebugCommandFactory
from ai.Util.sta_change_command import STAChangeCommand
from ai.executors.play_executor import PlayExecutor
from ai.states.game_state import GameState
from ai.states.play_state import PlayState


class DebugExecutor:
    def __init__(self, play_state: PlayState, play_executor: PlayExecutor, ui_send_queue: Queue, ui_recv_queue: Queue):
        self.logger = logging.getLogger("DebugExecutor")
        self.ui_send_queue = ui_send_queue
        self.ui_recv_queue = ui_recv_queue
        self.play_executor = play_executor
        self.play_state = play_state
        self.last_time = 0

    def exec(self) -> None:
        while not self.ui_recv_queue.empty():
            try:
                cmd = self.ui_recv_queue.get(block=False)
                self.play_executor.order_change_of_sta(STAChangeCommand(cmd))
            except Empty:
                break

        if time.time() - self.last_time > 0.25:
            self._send_books()
            self.last_time = time.time()

    def _send_books(self):

        msg = DebugCommandFactory().books(strategy_book=self.play_state.strategy_book.strategies_required_roles,
                                          strategy_default=self.play_state.strategy_book.default_strategies,
                                          tactic_book=self.play_state.tactic_book.tactics_name,
                                          tactic_default=self.play_state.tactic_book.default_tactics)
        self.ui_send_queue.put(msg)

    def _send_state(self):
        pass
        # for player in GameState().our_team.players:
        #     self.ui_send_queue.put(UIDebugCommandFactory.robot_strategic_state())

    def _send_auto_state(self):
        msg = DebugCommandFactory.auto_play_info(GameState().referee.info,
                                                 GameState().referee.team_info,
                                                 self.play_executor.auto_play.info,
                                                 self.play_state.autonomous_flag)
        self.ui_send_queue.put(msg)
