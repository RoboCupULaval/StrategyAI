from collections import namedtuple
from enum import Enum

from ai.STA.Strategy import StrategyBook, Strategy
from ai.STA.Tactic import TacticBook, Tactic
from RULEngine.Util.Pose import Pose

play = namedtuple("play", ["object", "status"])


STAStatus = Enum('boolean_enum', [('FREE', True), ('LOCKED', False)])


class PlayManager:
    # FIXME PLayer count, range, numbers and what not to fix!

    def __init__(self, p_gamestatemanager):
        self.GameStateManager = p_gamestatemanager
        self.strategybook = StrategyBook.StrategyBook()
        self.tacticbook = TacticBook.TacticBook()

        self.current_strategy = play(self.get_new_strategy("DoNothing")(self.GameStateManager, self), STAStatus.FREE)
        self.current_tactics = [play(self.get_new_tactic("Stop")(self.GameStateManager, self, i), STAStatus.FREE) for i in range(6)]
        self.robot_informations = [[None, Pose(), Pose(), 0] for i in range(6)]
        # [ai_command, target, goal, [kick_strength]

        self.DebugManager = None

    # ---Getter
    def get_current_strategy(self):
        return self.current_strategy.object

    def get_current_strategy_name(self):
        return self.current_strategy.object.get_name()

    def get_current_strategy_status(self):
        return self.current_strategy.status

    def get_current_tactic(self, player_id):
        return self.current_tactics[player_id].object

    def get_current_tactic_name(self,player_id):
        return self.current_tactics[player_id].object.get_name()

    def get_list_current_tactics_name(self):
        list_of_current_tactics = []
        for tactic in self.current_tactics:
            list_of_current_tactics.append(tactic.object.get_name())
        return list_of_current_tactics

    def get_current_tactic_status(self, player_id):
        return self.current_tactics[player_id].status

    def get_current_action_name(self, player_id):
        # FIXME fix me! ugly
        return self.current_tactics[player_id].object.current_state.__name__

    # TODO find an answer for : Should theses functions initialize the object or not?
    def get_new_strategy(self, strategy_name):
        return self.strategybook.get_strategy(strategy_name)

    def get_new_tactic(self, tactic_name):
        return self.tacticbook.get_tactic(tactic_name)

    def get_player_target(self, player_id):
        return self.robot_informations[player_id][1]

    def get_player_goal(self, player_id):
        return self.robot_informations[player_id][2]

    def get_player_kick_state(self, player_id):
        return self.robot_informations[player_id][3]

    def get_player_next_aicommand(self, player_id):
        return self.robot_informations[player_id][0]

    # ---Setter
    # TODO make less functions, you can regroup most of the next function in few better made functions
    def set_strategy(self, strategy):
        assert self.strategybook.check_existance_strategy(strategy.get_name()), "strategy isn't a name in strategybook!"

        if self.current_strategy.status == STAStatus.FREE:
            self.current_strategy = play(strategy, self.current_strategy.status)

    def set_strategy_status(self, sta_status):
        assert isinstance(sta_status, STAStatus)

        self.current_strategy = play(self.current_strategy.object, sta_status)

    def override_strategy_and_status(self, strategy, sta_status):
        assert self.strategybook.check_existance_strategy(strategy.get_name()), "strategy isn't a name in strategybook!"
        assert isinstance(sta_status, STAStatus)

        self.current_strategy = play(strategy, sta_status)

    def set_tactic(self, player_id, tactic):
        assert self.tacticbook.check_existance_tactic(tactic.get_name()), "tactic isn't a name in tacticbook!"

        if self.current_tactics[player_id] == STAStatus.FREE:
            self.current_tactics[player_id] = play(tactic, self.current_tactics[player_id].status)

    def set_tactic_status(self, player_id, sta_status):
        """
        Use with caution, this is usually reserved to debug manager!
        """
        assert isinstance(sta_status, STAStatus)

        self.current_tactics[player_id] = play(self.current_tactics[player_id].object, sta_status)

    def set_all_tactic_status(self, sta_status):
        assert isinstance(sta_status, STAStatus)

        # FIXME fixed range!!!
        for i in range(6):
            if not self.current_tactics[i].status == sta_status:
                self.current_tactics[i] = play(self.current_tactics[i].object, sta_status)

    def override_tactic_and_status(self, player_id, tactic, sta_status):
        assert self.tacticbook.check_existance_tactic(tactic.get_tactic_name()), "tactic isn't a name in tacticbook!"
        assert isinstance(sta_status, STAStatus)

        self.current_tactics[player_id] = play(tactic, sta_status)

    # end of shitty setter functions! please stay tuned!

    # FIXME see to check what is passed to us in the next 4 methods! Assert and such...
    # Also I know _replace is not the best, I'm just lazy FIXME!
    def set_player_target(self,player_id, target):
        self.robot_informations[player_id][1] = target

    def set_player_goal(self, player_id, goal):
        self.robot_informations[player_id][2] = goal

    def set_player_ai_command(self, player_id, ai_command):
        self.robot_informations[player_id][0] = ai_command

    def set_player_kick_state(self, player_id, kick_state):
        self.robot_informations[player_id][3] = kick_state

    def update(self):
        self.current_strategy.object.set_next_tactics_sequence()
        self._exec_tactics()

    def _exec_tactics(self):
        for player_id in range(0, 6):
            new_action = self.get_current_tactic(player_id).exec()
            self.set_player_ai_command(player_id, new_action)




    def register_debug_manager(self, debug_manager_ref):
        self.DebugManager = debug_manager_ref

    def acquire_gamestatemanager(self):
        return self.GameStateManager




    def set_player_skill_target_goal(self, i, action):
        # FIXME: retirer!
        self.set_player_target(i, action['target'])

    def get_next_state(self):
        return 'debug'
