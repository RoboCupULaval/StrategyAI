from UltimateStrat.Executor.Executor import Executor

__author__ = 'jbecirovski'


class SkillExecutor(Executor):
    """
    SkillExecutor is a sequence of request that select next pose for each players
    1 - what's player skill ?
    2 - what's player target ?
    3 - what's player goal ?
    4 - get skill object
    5 - generate next pose
    6 - set next pose
    """
    def __init__(self, info_manager):
        Executor.__init__(self, info_manager)

    def exec(self):
        # Execution for each players
        for id_player in range(self.info_manager.getCountPlayer()):
            # 1 - what's player skill ?
            current_skill = self.info_manager.getPlayerSkill(id_player)

            # 2 - what's player target ?
            current_target = self.info_manager.getPlayerTarget(id_player)

            # 3 - what's player goal ?
            current_goal = self.info_manager.getPlayerGoal(id_player)

            # 4 - get skill object
            skill = self.skill_book[current_skill]

            # 5 - generate next pose
            next_pose = skill().act(self.info_manager.getPlayerPose(id_player), current_target, current_goal)

            # 6 - set next pose
            self.info_manager.setPlayerNextPose(id_player, next_pose)