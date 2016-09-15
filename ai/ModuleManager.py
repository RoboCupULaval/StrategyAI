from .Algorithm import PathfinderRRT

class NonExistentModule(Exception):
    """ Est levée si le module intelligent requis n'est pas enregistré. """
    pass

class ModuleManager:
    def __init__(self):
        self.modules = {}
        f = open('module_config', 'r')
        for module_name in f.read().split('\n'):
            if hasattr(PathfinderRRT.modules[__name__], module_name):
                module = getattr(object, module_name)
                self.register_module(module_name, module)

    def register_module(self, module_name, module_ref):
        self.modules[module_name] = module_ref(self)

    def acquire_module(self, module_name):
        try:
            return self.modules[module_name]
        except KeyError:
            raise NonExistentModule("Le module " + module_name + " n'existe pas.")