# Under MIT License, see LICENSE.txt

__author__ = "Maxime Gagnon-Legault"

import logging
from multiprocessing import Queue
from queue import Empty
from pickle import loads

from RULEngine.Util import singleton
from ai.Util.sta_change_command import STAChangeCommand
from ai.executors.play_executor import PlayExecutor


class DebugExecutor(metaclass=singleton):
    def __init__(self, debug_queue: Queue):
        self.logger = logging.getLogger("DebugExecutor")
        self.debug_queue = debug_queue
        self.play_executor_ref = PlayExecutor()

    def exec(self) -> None:
        while True:
            try:
                cmd = self.debug_queue.get(block=False)
                cmd = STAChangeCommand(loads(cmd))
                self.play_executor_ref.order_change_of_sta(cmd)
            except Empty:
                break

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
    # def _parse_strategy(self, cmd: UIDebugCommand)->None:
    #     """
    #     Remplace la stratégie courante par celle demander dans la commande de l'UI
    #
    #     :param cmd: (UIDebugCommand) la commande envoyée de l'UI
    #     :return: None
    #     """
    #     # TODO revise this function please, thank you!
    #     # TODO change this once UI-Debug send correct strategy names!
    #
    #     strategy_key = cmd.data['strategy']
    #
    #     if strategy_key == 'pStop':
    #         self.ws.play_state.set_strategy(self.ws.play_state.get_new_strategy("DoNothing")(self.ws.game_state))
    #     else:
    #         self.ws.play_state.set_strategy(self.ws.play_state.get_new_strategy(strategy_key)(self.ws.game_state))
    #
    # def _parse_tactic(self, cmd: UIDebugCommand)->None:
    #     """
    #     Remplace la tactique courante d'un robot par celle demander dans la commande de l'UI
    #
    #     :param cmd: (UIDebugCommand) la commande envoyée de l'UI
    #     :return: None
    #     """
    #     assert isinstance(cmd, UIDebugCommand), "debug_executor->_parse_tactic is not the correct object!"
    #     # TODO make implementation for other tactic packets!
    #     # FIXME this pid thingy is getting out of control
    #     # find the player id in question
    #     # get the player if applicable!
    #     try:
    #         this_player = self.ws.game_state.get_player(cmd.data['id'])
    #     except KeyError as id:
    #         print("Invalid player id: {}".format(cmd.data['id']))
    #         return
    #     player_id = this_player.id
    #     tactic_name = cmd.data['tactic']
    #     # TODO ui must send better packets back with the args.
    #     target = cmd.data['target']
    #     target = Pose(Position(target[0], target[1]), this_player.pose.orientation)  # 3.92 - 2 * math.pi)
    #     args = cmd.data.get('args', "")
    #     tactic = self.ws.play_state.get_new_tactic('Idle')(self.ws.game_state,
    #                                                        this_player,
    #                                                        target,
    #                                                        args)
    #     try:
    #         tactic = self.ws.play_state.get_new_tactic(tactic_name)(self.ws.game_state, this_player, target, args)
    #     except Exception as e:
    #         print(e)
    #         print("La tactique n'a pas été appliquée par "
    #               "cause de mauvais arguments.")
    #         raise e
    #
    #     if isinstance(self.ws.play_state.current_strategy, HumanControl):
    #         hc = self.ws.play_state.current_strategy
    #         hc.assign_tactic(tactic, player_id)
    #     else:
    #         hc = HumanControl(self.ws.game_state)
    #         hc.assign_tactic(tactic, player_id)
    #         self.ws.play_state.set_strategy(hc)
