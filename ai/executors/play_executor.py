# Under MIT License, see LICENSE.txt

import logging
from multiprocessing import Queue
from queue import Empty
from time import sleep

from typing import List, Dict

from Debug.debug_command_factory import DebugCommandFactory
from Util import Pose, Position, AICommand, EngineCommand, Path
from Util.role import Role
from ai.Algorithm.auto_play import SimpleAutoPlay
from ai.GameDomainObjects import Player
from ai.STA.Strategy.human_control import HumanControl
from ai.Util.sta_change_command import STAChangeCommand
from ai.executors.pathfinder_module import PathfinderModule
from ai.states.game_state import GameState
from ai.states.play_state import PlayState
from config.config import Config
config = Config()


class PlayExecutor:

    def __init__(self, play_state: PlayState, ui_send_queue: Queue, referee_queue: Queue):

        self.logger = logging.getLogger(self.__class__.__name__)

        self.auto_play = SimpleAutoPlay(play_state)
        self.play_state = play_state
        self.game_state = GameState()
        self.ui_send_queue = ui_send_queue
        self.referee_queue = referee_queue

        self.autonomous_flag = config['GAME']['is_autonomous_play_at_startup']
        self.ref_states = []

        self.pathfinder_module = PathfinderModule()

    def exec(self) -> List[EngineCommand]:
        self._fetch_referee_state()

        if self.autonomous_flag:
            self._exec_auto_play()

        ai_cmds, debug_cmds = self._execute_strategy()

        self.ui_send_queue.put_nowait(debug_cmds)

        strategy_obstacles = self.play_state.current_strategy.obstacles()
        paths = self.pathfinder_module.exec(ai_cmds, strategy_obstacles)

        engine_cmds = []
        for player, ai_cmd in ai_cmds.items():
            engine_cmds.append(generate_engine_cmd(player, ai_cmd, paths[player]))

        self._send_robots_status()

        return engine_cmds
        #return []

    def order_change_of_sta(self, cmd: STAChangeCommand):
        if cmd.is_strategy_change_command():
            self._change_strategy(cmd)
        elif cmd.is_tactic_change_command():
            self._change_tactic(cmd)
        elif cmd.is_autoplay_change_command():
            self.order_change_of_autonomous_play(cmd.data['status'])

    def order_change_of_autonomous_play(self, is_autonomous: bool):
        # If we switch from manual to autonomous we clear previous referee's command
        if not self.autonomous_flag and is_autonomous:
            self.logger.debug('Switching to autonomous mode')
        elif self.autonomous_flag and not is_autonomous:
            self.logger.debug('Switching to manual mode')
            self.play_state.current_strategy = 'DoNothing'

        self.autonomous_flag = is_autonomous

    def _fetch_referee_state(self):
        self.ref_states = []
        try:
            while not self.referee_queue.empty():
                referee_state = self.referee_queue.get(block=False)
                self.ref_states.append(referee_state)
        except Empty:
            pass
        # if GameState().game.referee.team_info['ours']['goalie'] != self.goalie_id:
        #     self.goalie_id = GameState().game.referee.team_info['ours']['goalie']
        #     GameState().update_player_for_locked_role(self.goalie_id, Role.GOALKEEPER)

    def _exec_auto_play(self):
        for state in self.ref_states:
            self.auto_play.update(state)

    def _change_strategy(self, cmd: STAChangeCommand):
        # Convert string role to their enum equivalent
        roles = cmd.data['roles']
        if roles is not None:
            roles = {Role[r]: i for r, i in cmd.data['roles'].items()}
        self.play_state.change_strategy(cmd.data['strategy'], roles)

    def _change_tactic(self, cmd: STAChangeCommand):

        try:
            this_player = GameState().our_team.available_players[cmd.data['id']]
        except KeyError:
            self.logger.info('A tactic was assign to a player which is not on the field (id={}).'.format(cmd.data['id']))
            this_player = GameState().our_team.players[cmd.data['id']]

        player_id = this_player.id
        tactic_name = cmd.data['tactic']
        target = Position.from_list(cmd.data['target'])
        if config['GAME']['on_negative_side']:
            target = target.flip_x()
        target = Pose(target, this_player.orientation)
        args = cmd.data.get('args', '')
        try:
            tactic = self.play_state.get_new_tactic(tactic_name)(self.game_state, this_player, target, args)
        except:
            self.logger.exception('message')
            self.logger.debug('The tactic was call with wrong arguments')
            raise

        if not isinstance(self.play_state.current_strategy, HumanControl):
            self.play_state.current_strategy = 'HumanControl'
        self.play_state.current_strategy.assign_tactic(tactic, player_id)

    def _execute_strategy(self) -> Dict[Player, AICommand]:
        # Applique un stratégie par défault s'il n'en a pas (lors du démarage par exemple)
        # Apply the default strategy if there is none (for example at startup)
        if self.play_state.current_strategy is None:
            self.play_state.current_strategy = 'DoNothing'
        return self.play_state.current_strategy.exec()

    def _send_robots_status(self):
        states = self.play_state.current_tactical_state
        if len(states) > 0:
            cmd = DebugCommandFactory.robots_strategic_state(states)
            self.ui_send_queue.put(cmd)


def generate_engine_cmd(player: Player, ai_cmd: AICommand, path: Path) -> EngineCommand:
    return EngineCommand(player.id,
                         cruise_speed=ai_cmd.cruise_speed * 1000,
                         path=path,
                         kick_type=ai_cmd.kick_type,
                         kick_force=ai_cmd.kick_force,
                         dribbler_state=ai_cmd.dribbler_state,
                         target_orientation=ai_cmd.target.orientation if ai_cmd.target else None,
                         end_speed=ai_cmd.end_speed,
                         charge_kick=ai_cmd.charge_kick)
