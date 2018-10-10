#!/bin/bash

# The goal of this script is to be executed directly via curl:
# sh -c "$(curl -fsSL https://raw.githubusercontent.com/RoboCupULaval/StrategyAI/dev/scripts/install_from_scratch.sh)"
# It install the ultron and than launch `install_all.py`

mkdir -p ~/robocup/ultron
cd ~/robocup/ultron

# Clone repos
git clone https://github.com/RoboCupULaval/StrategyAI.git

cd StrategyAI/

# Install ultron
bash ./scripts/install_ultron.sh

# Install all the tools
python3.6 ./install_all.py