![Untitled](Logo.png)

---

## Unity Simulation

Our Unity project for simulation can be found at: https://github.com/Software-Cat/AutoFlowUnity/

---

## Authors

Naman Doshi, James Jiang, Bowen Wu, Xuanyu Liu

## Overview

Uber AutoFlow is a centralised multi-vehicle routing system that leverages smartphone-to-server wireless communications to overcome the barrier of limited intervehicular communications, thus allowing global optimisations that enhance road conditions while lowering CO2 emissions.

By considering various factors such as the speed limit of relevant roads and the emission rate of each individual vehicle, AutoFlow performs a balanced multi-agent path-searching algorithm (an A\* variant similar to the one shown in David Silver’s [paper](https://www.davidsilver.uk/wp-content/uploads/2020/03/coop-path-AIWisdom.pdf)).

## File Navigation Made Easy

### Sample_Case

The folder with the same name is composed of two files: ClassDefinitions (containing basic class definitions) and test.py, which contains the main code for analysis.

The function of this code is to compare the traditional "selfish" navigation systems and AutoFlow. It uses a map based on the one provided in the "Sample Case" section of our PDF report, and calculates the differences in median commute time, total CO2 emissions, and peak congestion levels between the two navigation systems.

TO RUN: simply execute test.py in this directory, no frills needed.

### LandscapeComponents.py

Contains all the code and class definitions for generating pseudo-random cities based on given features.

### VehicleAgents.py

Contains concise class definitions for gas and electric vehicles alike.

### test.py

Includes sample, and example code, to demonstrate the functionality of the city generation.

### AutoFlow.py

This is the main program — it includes our A\* variant, which is used to find the optimal path for each vehicle. It includes definitions for a landscape and several vehicles, which can be modified at the end of the code.

TO RUN: Execute the code, and it will print each vehicle's optimal path to the terminal.

## Resolving Errors

All code has been tested and is highly unlikely to produce any errors at runtime, although if you encounter any, please check whether any custom parameters you have modified (e.g. traffic light interval) is an invalid value — for example, a negative number is clearly impossible, as well as 0.
