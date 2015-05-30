import sys
sys.path.append(".")
from PythonFramework import Framework
import Strategy.BestStrategy


Framework.start_game(Strategy.BestStrategy.BestStrategy)
