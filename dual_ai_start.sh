#!/bin/bash

#start ai blue
python main.py config/sim.cfg | python main.py config/sim_yellow.cfg | python ../UI-Debug/main.py config/field/sim.cfg blue | python ../UI-Debug/main.py config/field/sim.cfg yellow

