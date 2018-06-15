#!/bin/bash

# Start two AI: yellow one in auto mode, blue in manual with a UI-debug.
python ../UI-Debug/main.py config/field/autoref.cfg blue \
| python main.py config/autoref.cfg yellow negative --start_in_auto --engine_fps 65 \
| python main.py config/autoref.cfg blue positive --engine_fps 65
