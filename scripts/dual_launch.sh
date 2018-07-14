#!/bin/bash

# Start two AI: yellow one in auto mode, blue in manual with a UI-debug.
python ../../UI-Debug/main.py ../config/field/sim.cfg blue \
| python ../main.py ../config/sim.cfg yellow negative --start_in_auto  --engine_fps 30\
| python ../main.py ../config/sim.cfg blue positive --engine_fps 30
