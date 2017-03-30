import sys
import os.path

folder = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(1, folder)

from . import google
