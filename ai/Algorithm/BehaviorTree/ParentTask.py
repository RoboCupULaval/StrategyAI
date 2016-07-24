# Under MIT License, see LICENSE.txt
from abc import abstractmethod

from ai.Algorithm.BehaviorTree.Task import Task
from ai.Algorithm.BehaviorTree.TaskController import TaskController

__author__ = 'RoboCupULaval'


class ParentTask(Task):

    """Noeud interne du behavior tree, un
    noeud directeur du flux qui choisie le
    prochain enfant a etre execute"""

    def __init__(self):
        self.subtasks = []
        self.cur_task = None
        self.task_controller = TaskController()

    def get_control(self):
        """Gets the control reference"""
        return self.task_controller

    def check_condition(self):
        """S'assure que la liste des sous-tâches n'est pas vide"""
        # LogTask
        return len(self.subtasks) > 0

    @abstractmethod
    def child_succeeded(self):
        """Abstract à être substituée dans les classes enfants.
        Appelé quand un enfant finit avec succès."""
        pass

    @abstractmethod
    def child_failed(self):
        """Abstract à être substituée dans les classes enfants.
        Appelé quand un enfant finit avec échec."""
        pass

    def exec(self):
        """Regarde si l'enfant a commencé, est terminé ou a besoin d'être updaté.
        Agit en conséquence chaque fois qu'une nouvelle cur_task est sélectionnée"""

        if self.task_controller.finished():
            # Si cette parent_task est terminée,
            # return sans rien faire.
            return
        # TODO mettre en unit test
        if self.cur_task is None:
            # Si une child task sélectionnée est "None", 
            # nous avons un problème
            return

        # Si nous avons une cur_task...
        if self.cur_task.check_condition() is not True:
            self.child_failed()

        if not self.cur_task.task_controller.started:
            # ... et qu'elle n'est pas encore commencée, commences la.
            self.cur_task.task_controller.safe_start(self.cur_task)

        elif self.cur_task.task_controller.finished():
            # ... et qu'elle est fini, finis la correctement.
            self.cur_task.task_controller.safe_end(self.cur_task)

            if self.cur_task.task_controller.success:
                self.child_succeeded()

            elif not self.cur_task.task_controller.success:
                self.child_failed()

        else :
            # ... et qu'elle est prête, updates la.
            self.cur_task.exec()

    # Implement end()
    def end(self):
        """Finit la tâche"""
        pass

    def start(self):
        """Commence la tâche et assigne la cur_task
        à la première de  la liste des sous-tâches."""
        # LogTask
        self.cur_task = self.subtasks[0]

        if self.cur_task.check_condition() is not True:
            self.child_failed()

        if self.cur_task is None:

            print("Current task has a null action")
            # Il faudrait voir si on veut implementer un log

    def add_task(self,task):
        """Ajoute une tache a la liste des sous-tache"""
        self.subtasks.append(task)

    def reset_parent_task(self):
        self.cur_task = self.subtasks[0]

    def get_task(self):
        return self.subtasks

