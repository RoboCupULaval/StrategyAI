

from ai.Algorithm.BehaviorTree.ParentTask import ParentTask

__author__ = 'RoboCupULaval'


class Selector(ParentTask):

    """Cette parent task choisit un de ses enfants pour l'update.

    Pour choisir un enfant, elle commence par le début
    de la liste des enfants et les essaye un par un
    jusqu'à ce qu'elle en trouve un qui passe le test check_condition.
    Ensuite, elle update l'enfant jusqu'à sa fin.

    Si l'enfant finit avec échec, le Selecteur continue à
    parcourir la liste en cherchant un autre enfant à update.
    S'il ne réussit pas, le Selecteur finit avec échec.
    Si l'enfant finit avec succès, le Sélecteur considère
    que sa tâche est fait et retourne succès."""

    def __init__(self):
        self.task = None
        self.found = None
        self.cur_pos = None
        ParentTask.__init__(self)

    def choose_new_task(self):
        """Choisir la nouvelle tâche à update.
        @return la nouvelle tâche, ou None
        si aucune n'est trouvée."""

        self.task = None
        self.found = False
        self.cur_pos = self.subtasks.index(self.cur_task)

        while self.found is not True:
            if self.cur_pos == self.subtasks.__len__()-1:
                self.found = True
                self.task = None
                break
            self.cur_pos += 1

            self.task = self.subtasks[self.cur_pos]
            if self.task.check_condition():
                self.found = True

            return self.task

    def child_failed(self):
        """Dans le cas où l'enfant actuel finit avec un échec,
         on trouve un nouvel à update, ou si aucun enfant n'est
         trouvé, le parent task échoue ."""

        self.cur_task = self.choose_new_task()
        if self.cur_task is None:
            self.task_controller.finish_with_failure()

    def child_succeeded(self):
        """Si l'enfant finit avec succès."""

        self.task_controller.finish_with_success()

