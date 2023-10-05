# ROCK-PAPER-SCISSORS #

This repo contains (clean) code related to the rock-paper-scissors robot.


### What is this repository for? ###

This repo is used for the rock-paper-scissors robot currently installed Technopolis, Belgium.
It contains all code related to the streamlit frontend (with openCV stream integration), the classification logic and the physical connection.
It is not necessary to have the physical device to run the code.


### Usage ###

Firstly, install all packages/versions mentioned in the `requirements.txt` file.
Then you can run the streamlit web app by running `bash run_app.sh` in the CLI. The web app will get deployed on `localhost:8051`.
The `config.py` file serves as the central "control panel" from where you can tune different time delays, detection thresholds, etc.

**IMPORTANT**: In the `config.py` there is the constant boolean `PHYSICAL` which specifies whether or not the physical robot device is connected or not. Note that if you set this variable to True and do not have the robot arm connected via a USB connection that the program will crash for obvious reasons.
