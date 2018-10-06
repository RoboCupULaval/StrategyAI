#!/usr/bin/env python3
import os
import subprocess
from time import sleep

GREEN = '\033[92m'
END_COLOR = '\033[0m'

ROOT = os.getenv("HOME") + "/robocup"
TOOLS_DIR = ROOT + "/tools"
LOCAL_INSTALL = ROOT + "/local"

# The ~/robocup/local is the location where all the binary and library are installed
# CMAKE_PREFIX_PATH -> where to fetch library/binary/include
# CMAKE_INSTALL_PREFIX -> where to install library/binary/include
# CMAKE_INSTALL_CMD = "mkdir -p build && cd build && cmake .. -DCMAKE_PREFIX_PATH={local_dir} " \
#                     "-DCMAKE_INSTALL_PREFIX={local_dir} && make -j 4".format(local_dir=LOCAL_INSTALL)
CMAKE_INSTALL_CMD = "mkdir -p build && cd build && cmake .. && make -j 4"


def run_cmd(cmd, working_directory=None):
    print(f"{GREEN}==>{END_COLOR}  {cmd}")
    subprocess.Popen(cmd,
                     shell=True,
                     cwd=working_directory).wait()
    sleep(1)  # Synchronize the stdout and stderr


def cmake_install(tool_name, install=True):
    cmd = CMAKE_INSTALL_CMD + " && sudo -S make install" if install else CMAKE_INSTALL_CMD
    run_cmd(cmd, TOOLS_DIR + "/" + tool_name)


def init_folder():
    run_cmd("mkdir -p {tools_folder}".format(tools_folder=TOOLS_DIR))
    run_cmd("mkdir -p {local_install}".format(local_install=LOCAL_INSTALL))


def grsim():
    PATCH_FILE = os.getcwd() + "/scripts/grsim.patch"
    CORRECT_GRSIM_CONFIG = os.getcwd() + "/scripts/grsim.xml"
    GRSIM_COMMIT_HASH = "45f0b3d71134b90594ee387675f95324160cb239"

    run_cmd("sudo -S apt-get install --yes git build-essential cmake libqt4-dev libgl1-mesa-dev libglu1-mesa-dev "
            "libprotobuf-dev protobuf-compiler libode-dev libboost-dev")
    run_cmd("git clone https://github.com/szi/vartypes.git || true", TOOLS_DIR)
    run_cmd("git clone https://github.com/RoboCup-SSL/grSim.git || true", TOOLS_DIR)
    run_cmd("git checkout {}".format(GRSIM_COMMIT_HASH), TOOLS_DIR + "/grSim")

    # By default grsim use the ~/.grsim.xml for saving settings. The patch makes it use ~/arena/tools/.grsim.xml
    # This make it possible to have two versions of grsim with two different configurations
    run_cmd("git apply {}".format(PATCH_FILE), TOOLS_DIR + "/grSim")
    run_cmd("cp {src} {dst}".format(src=CORRECT_GRSIM_CONFIG, dst=TOOLS_DIR + "/.grsim.xml"))

    # Desktop shortcut
    run_cmd("cp {src} {dst}".format(src=os.getcwd() + "/scripts/grsim.desktop", dst="~/Desktop"))

    cmake_install("vartypes")
    cmake_install("grSim")


def ssl_refbox():
    PATCH_FILE = os.getcwd() + "/scripts/ssl-refbox.patch"

    run_cmd("sudo -S apt-get --yes install cmake g++ git libgtkmm-2.4-dev libprotobuf-dev protobuf-compiler")

    run_cmd("git clone https://github.com/RoboCup-SSL/ssl-refbox.git || true", TOOLS_DIR)

    # This patch change the default port and make so adding team's name is not mandatory
    run_cmd("git apply {}".format(PATCH_FILE), TOOLS_DIR + "/ssl-refbox")

    # Add a desktop shortcut
    run_cmd("cp {src} {dst}".format(src=os.getcwd() + "/scripts/ssl-refbox.desktop", dst="~/Desktop"))

    cmake_install("ssl-refbox", install=False)


def autoref():
    PATCH_FILE = os.getcwd() + "/scripts/autoref.patch"

    run_cmd("sudo -S apt-get --yes install openjdk-8-jdk maven")

    run_cmd("git clone https://gitlab.tigers-mannheim.de/open-source/AutoReferee.git || true", TOOLS_DIR)

    # The autoref completely ignore vision port configuration, we have change the code and rebuild it.
    run_cmd("git apply {}".format(PATCH_FILE), TOOLS_DIR + "/AutoReferee")

    run_cmd("./build.sh", TOOLS_DIR + "/AutoReferee")

def ultron():
    run_cmd(os.getcwd() + "/scripts/install_ultron.sh")



steps = \
    [(init_folder, "Setup folders"),
     (grsim, "Install and configure GrSim (simulator"),
     (ssl_refbox, "Install and configure refbox (referee)"),
     (ultron, "Install team ultron"),
     (autoref, "Install and configure TIGER's autoref")
     ]

if __name__ == "__main__":
    skip_cnt = 0
    while True:
        print("======= Installation steps =======")
        [print("\t[{}] {}".format(i, name)) for i, (_, name) in enumerate(steps)]
        res = input("Do you want to skip a{} step? [#step/n]:".format("nother" if skip_cnt > 0 else ""))
        if res.lower() == 'n' or res == "":
            break
        id = int(res)
        if 0 <= id < len(steps):
            del steps[id]
            skip_cnt += 1

    n = len(steps)
    for i, (step, name) in enumerate(steps):
        print("{color}[{i}/{n}] {name} {end_color}".format(i=i+1, n=n, name=name, color=GREEN, end_color=END_COLOR))
        step()

    print("DONE! :)")
