#!/bin/bash

# Create base folder
cd ~
mkdir RobocupULaval
cd RobocupULaval

# Add python 3.6 repository
sudo add-apt-repository ppa:jonathonf/python-3.6 -y
sudo apt update

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
git checkout dev
cd ../UI-Debug
pip install -r requirements.txt
git checkout dev

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
cd ~/RobocupULaval
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
