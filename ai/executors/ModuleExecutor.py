from ai.executors.Executor import Executor


class ModuleExecutor(Executor):

    def __init__(self, p_world_state):
        super().__init__(p_world_state)
        self.start_initial_modules()

    def exec(self):

        for module in self.ws.module_state.modules.values():
            module.upddate()

    def start_initial_modules(self):
        pass
