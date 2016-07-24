# Under MIT License, see LICENSE.txt
__author__ = 'RoboCupULaval'


class TaskController:
    """Classe ajoutée par composition à toutes les tâches.
    Utilisée pour garder le fil des états des tâches."""

    def __init__(self):
        self.done = False
        self.success = True
        self.started = False

    def set_task(self,task):
        """Sets the task reference
        @param task Task to monitor"""
        self.task = task

    def safe_start(self,task):
        """Commence la tâche"""
        self.started = True
        task.start()

    def safe_end(self,task):
        """Termine la tâche"""
        self.done = False
        self.started = False
        task.end()

    def finish_with_success(self):
        """Termine la tâche, avec succès"""
        self.success = True
        self.done = True

    def finish_with_failure(self):
        """Termine la tâche , avec échec"""
        self.success = False
        self.done = True

    def succeeded(self):
        """Indique si la tâche a fini avec succès"""
        return self.success

    def failed(self):
        """Indique si la tâche a fini avec échec"""
        return not self.success

    def finished(self):
        """Indique si la tâche est terminée"""
        return self.done

    def started(self):
        """Indique si la tâche a commencé"""
        return self.started

    def reset_task(self):
        """Remet la tâche dans son état de départ."""
        self.done = False
