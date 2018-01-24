# Under MIT License, see LICENSE.txt
import time

from multiprocessing import Queue

from RULEngine.Debug.uidebug_command_factory import UIDebugCommandFactory
from Util import Pose, Position
from ai.STA.Strategy.human_control import HumanControl
from ai.executors.executor import Executor
from ai.states.play_state import PlayState

STRATEGY_COMMAND_TYPE = 5002
TACTIC_COMMAND_TYPE = 5003
AUTO_PLAY_COMMAND_TYPE = 5008


class UIDebugCommand(object):

    def __init__(self, raw_cmd):
        self.data = raw_cmd['data']
        self.cmd_type = raw_cmd['type']

    def is_strategy_cmd(self):
        return self.cmd_type == STRATEGY_COMMAND_TYPE

    def is_tactic_cmd(self):
        return self.cmd_type == TACTIC_COMMAND_TYPE

    def is_auto_play_cmd(self):
        return self.cmd_type == AUTO_PLAY_COMMAND_TYPE


class DebugExecutor(Executor):

    def __init__(self, ui_send_queue: Queue):
        """initialise"""
        super().__init__()
        self.debug_in = []
        self.last_time = 0
        self.ui_send_queue = ui_send_queue

    def exec(self):
        """Open packet, parse them and execute them"""
        self._execute_incoming_debug_commands()

        if time.time() - self.last_time > 0.25:
            # TODO use handshake with the UI-DEBUG to stop sending it every frame! MGL 2017/03/16
            self._send_books()
            self.last_time = time.time()

    def _send_books(self) -> None:

        cmd_tactics = {'strategy': PlayState().strategy_book.get_strategies_name_list(),
                       'tactic': PlayState().tactic_book.get_tactics_name_list(),
                       'action': ['None']}

        msg = UIDebugCommandFactory().books(cmd_tactics)
        self.ui_send_queue.put(msg)

    def set_reference(self, debug_ref) -> None:
        """ rentre la référence donné par le RULEngine"""
        self.debug_in = debug_ref

    def _execute_incoming_debug_commands(self) -> None:
        """
        change les packets en commandes correspondant, et les applique.

        :return: None
        """
        for command in self.debug_in:
            self._parse_command(UIDebugCommand(command))

    def _parse_command(self, cmd: UIDebugCommand)->None:
        """
        Choisit la méthode puor appliquer la commande de l'UI

        :param cmd: (UIDebugCommand) la commande de l'UIDebug
        :return: None
        """
        if cmd.is_strategy_cmd():
            self._parse_strategy(cmd)

        elif cmd.is_tactic_cmd():
            self._parse_tactic(cmd)

        elif cmd.is_auto_play_cmd():
            self.ws.play_state.autonomous_flag = cmd.data['status']
            if not self.ws.play_state.autonomous_flag:
                self.ws.play_state.set_strategy(self.ws.play_state.get_new_strategy("DoNothing")(self.ws.game_state))

        else:
            pass


    def _parse_strategy(self, cmd: UIDebugCommand)->None:
        """
        Remplace la stratégie courante par celle demander dans la commande de l'UI

        :param cmd: (UIDebugCommand) la commande envoyée de l'UI
        :return: None
        """
        # TODO revise this function please, thank you!
        # TODO change this once UI-Debug send correct strategy names!

        strategy_key = cmd.data['strategy']

        if strategy_key == 'pStop':
            self.ws.play_state.set_strategy(self.ws.play_state.get_new_strategy("DoNothing")(self.ws.game_state))
        else:
            self.ws.play_state.set_strategy(self.ws.play_state.get_new_strategy(strategy_key)(self.ws.game_state))

    def _parse_tactic(self, cmd: UIDebugCommand)->None:
        """
        Remplace la tactique courante d'un robot par celle demander dans la commande de l'UI

        :param cmd: (UIDebugCommand) la commande envoyée de l'UI
        :return: None
        """
        assert isinstance(cmd, UIDebugCommand), "debug_executor->_parse_tactic is not the correct object!"
        # TODO make implementation for other tactic packets!
        # FIXME this pid thingy is getting out of control
        # find the player id in question
        # get the player if applicable!
        try:
            this_player = self.ws.game_state.get_player(cmd.data['id'])
        except KeyError as id:
            print("Invalid player id: {}".format(cmd.data['id']))
            return
        player_id = this_player.id
        tactic_name = cmd.data['tactic']
        # TODO ui must send better packets back with the args.
        target = cmd.data['target']
        target = Pose(Position(target[0], target[1]), this_player.pose.orientation)  # 3.92 - 2 * math.pi)
        args = cmd.data.get('args', "")
        tactic = self.ws.play_state.get_new_tactic('Idle')(self.ws.game_state,
                                                           this_player,
                                                           target,
                                                           args)
        try:
            tactic = self.ws.play_state.get_new_tactic(tactic_name)(self.ws.game_state, this_player, target, args)
        except Exception as e:
            print(e)
            print("La tactique n'a pas été appliquée par "
                  "cause de mauvais arguments.")
            raise e

        if isinstance(self.ws.play_state.current_strategy, HumanControl):
            hc = self.ws.play_state.current_strategy
            hc.assign_tactic(tactic, player_id)
        else:
            hc = HumanControl(self.ws.game_state)
            hc.assign_tactic(tactic, player_id)
            self.ws.play_state.set_strategy(hc)
