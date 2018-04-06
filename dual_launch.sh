#!/bin/bash

# Start two AI: yellow one in auto mode, blue in manual with a UI-debug.
python ../UI-Debug/main.py config/field/sim.cfg blue \
| python main.py config/sim_yellow.cfg --on_negative_side --start_in_auto \
| python main.py config/sim.cfg
