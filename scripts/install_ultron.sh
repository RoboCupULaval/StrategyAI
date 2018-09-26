#!/bin/bash

# Base folder
mkdir -p ~/robocup/ultron
cd ~/robocup/ultron

# Add python 3.6 repository if necessary
case $(lsb_release -rs) in
18.04) echo "You have 18.04 you don't need an unofficial repo! Hooray!"
  ;;
*)
echo "You don't have 18.04 so you need an unofficial repo. sadf"
sudo add-apt-repository ppa:jonathonf/python-3.6 -y
sudo apt update
sudo apt-get install python3.6-venv
  ;;
esac

# Install dependencies
sudo -S apt-get install --yes git python3.6 python-pip python3-venv python-virtualenv build-essential cmake libqt4-dev libgl1-mesa-dev libglu1-mesa-dev libprotobuf-dev protobuf-compiler libode-dev libboost-dev

# Clone repos
git clone https://github.com/RoboCupULaval/UI-Debug.git

# Create and activate virtualenv
python3.6 -m venv virtualenv
source virtualenv/bin/activate

# Install requirements
cd StrategyAI
pip install -r requirements.txt
cd ../UI-Debug
pip install -r requirements.txt