import pathlib
import importlib
import inspect

from tests.STA.perfect_sim import PerfectSim
from Util import Pose

TACTIC_PATH = ('ai', 'STA', 'Tactic')


def pytest_generate_tests(metafunc):
    # get all the tactic file names
    tactic_paths = pathlib.Path(*TACTIC_PATH).glob("[!_]*.py")
    tactic_modules_list = []

    # import all the tactic in variables
    for tactic_path in tactic_paths:
        import_name = '.'.join(tactic_path.parts[0:]).rsplit('.', 1)[0]
        tactic_modules_list.append(importlib.import_module(import_name))

    # some import magic to get the tactic class since we want its type
    tactic_base_class_import = pathlib.Path(*TACTIC_PATH, 'tactic')
    tactic_import_name = '.'.join(tactic_base_class_import.parts[0:])
    tactic_base_class_type = importlib.import_module(tactic_import_name).Tactic

    # check which objects within the modules are classes derived from Tactic
    tactic_classes_list = []
    for a_tactic_module in tactic_modules_list:
        for __, obj in inspect.getmembers(a_tactic_module):
            # we want:
            # a class,
            # that is in defined in the module,
            # derived from Tactic or a child of it
            if inspect.isclass(obj) and\
               inspect.getfile(obj) == inspect.getfile(a_tactic_module) and\
               tactic_base_class_type in inspect.getmro(obj)[1:]:
                tactic_classes_list.append(obj)

    metafunc.parametrize('tactic_class', tactic_classes_list)

def test_initialize_tactic(tactic_class):
    simulator = PerfectSim(tactic_class)
    mock_id = 1
    mock_pose = Pose()
    simulator.start(mock_id, mock_pose)
