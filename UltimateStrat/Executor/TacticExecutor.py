#Under MIT License, see LICENSE.txt
from UltimateStrat.Executor.Executor import Executor

__author__ = 'RoboCupULaval'


class TacticExecutor(Executor):
    """
    TacticExecutor is a sequence of request that select skill for each players
    """
    def __init__(self, info_manager):
        """

        Args:
            info_manager: Requires access to the blackbox through the infomanager.

        Returns:

        """
        Executor.__init__(self, info_manager)

    def exec(self):
        """
        For each robots, get its tactic, confirm that it exist in the tacticbook, calcul/apply what the skill should be
        """
        # Execution for each players
        for id_player in range(self.info_manager.getCountPlayer()):

            # 1 - what's player tactic ?
            current_tactic = self.info_manager.getPlayerTactic(id_player)

            # 2 - get specific tactic from tactic book
            tactic = self.tactic_book[current_tactic]

            # 3 - select skill, target, goal from tactic object
            action = tactic().apply(self.info_manager, id_player)

            # 4 - set skill, target, goal
            self.info_manager.setPlayerSkillTargetGoal(id_player, action)


