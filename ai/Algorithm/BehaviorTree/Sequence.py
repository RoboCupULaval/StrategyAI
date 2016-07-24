# Under MIT License, see LICENSE.txt
from ai.Algorithm.BehaviorTree.ParentTask import ParentTask

__author__ = 'RoboCupULaval'


class Sequence(ParentTask):

    """This ParentTask executes each of it's children
    in turn until he has finished all of them.

    It always starts by the first child, updating each one.
    If any child finishes with failure, the
    Sequence fails, and we finish with failure.
    When a child finishes with success, we
    select the next child as the update victim.
    If we have finished updating the last child,
    the Sequence returns with success.

    @author Ying"""

    def __init__(self):
        self.cur_pos = None
        ParentTask.__init__(self)

    def child_failed(self):
        """Un enfant a terminé avec échec.
        On a échoué à mettre la séquence à jour.
        Termine avec échec."""
        self.task_controller.finish_with_failure()

    def child_succeeded(self):
        """Un enfant a terminé avec succès.
        Sélectionne le prochain enfant à mettre à jour.
        Si c'est le dernier de la séquence, elle finit avec succès."""
        self.cur_pos = self.subtasks.index(self.cur_task)
        if self.cur_pos == self.subtasks.__len__() - 1 :
            self.task_controller.finish_with_success()
        else:
            self.cur_task = self.subtasks[self.cur_pos + 1]
            if self.cur_task.check_condition() is not True:
                self.task_controller.finish_with_failure()




