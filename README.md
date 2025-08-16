
🚗🔋 EV Smart Rerouting with SUMO + TraCI

This project demonstrates how an electric vehicle (EV) can automatically reroute to the nearest charging station when its battery drops below a threshold, wait until it is recharged, and then resume its original trip.

Built with SUMO (Simulation of Urban Mobility), TraCI (Traffic Control Interface), and Python.

✨ Features

Monitors EV battery state in real time using TraCI.

Automatically detects low battery and reroutes to the nearest charging station.

Issues stop commands at the charger and resumes trip after charging.

Handles safe stopping near charging stations to avoid end-of-lane conflicts.

Logs battery level and simulation time during the run.

Generates a battery vs. time plot with Matplotlib.
⚙️ Requirements

SUMO (with sumo-gui)

Python 3.8+

Packages:

pip install traci matplotlib
