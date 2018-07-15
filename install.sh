#!/bin/bash

# Create base folder
cd ~
mkdir robocup
cd robocup

# Add python 3.6 repository if necessary
case $(lsb_release -rs) in
18.04) echo "You have 18.04 you don't need an unofficial repo! Hooray!"
  ;;
*)
echo "You don't have 18.04 so you need an unofficial repo. sadf"
sudo add-apt-repository ppa:jonathonf/python-3.6 -y
sudo apt update
  ;;
esac

# Install dependencies
sudo apt-get install --yes git python3.6 python-pip python-virtualenv build-essential cmake libqt4-dev libgl1-mesa-dev libglu1-mesa-dev libprotobuf-dev protobuf-compiler libode-dev libboost-dev

# Clone repos
git clone https://github.com/RoboCupULaval/StrategyAI.git
git clone https://github.com/RoboCupULaval/UI-Debug.git

# Create and activate virtualenv
python3.6 -m venv virtualenv
source virtualenv/bin/activate

# Install requirements
cd StrategyIA
pip install -r requirements.txt
cd ../UI-Debug
pip install -r requirements.txt

# Install VarTypes for grSim
cd /tmp
git clone https://github.com/szi/vartypes.git
cd vartypes
mkdir build
cd build
cmake ..
make -j 4
sudo make install

# Install grSim
cd ~/robocup
git clone https://github.com/RoboCup-SSL/grSim.git
cd grSim
mkdir build
cd build
cmake ..
make -j 4

# Install refbox
cd ../..
git clone https://github.com/RoboCup-SSL/ssl-refbox.git
cd ssl-refbox
sudo ./installDeps.sh
mkdir build
cd build
cmake ..
make -j 4
