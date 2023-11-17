
---

## Unity Simulation

Our Unity project for simulation can be found at: https://github.com/Software-Cat/AutoFlowUnity/

---

## Authors

Naman Doshi, James Jiang, Bowen Wu

---

## Overview

Uber AutoFlow is a centralised multi-vehicle routing system that leverages smartphone-to-server wireless communications to overcome the barrier of limited intervehicular communications, thus allowing global optimisations that enhance road conditions while lowering CO2 emissions.

By considering various factors such as the speed limit of relevant roads and the emission rate of each individual vehicle, AutoFlow performs a balanced multi-agent path-searching algorithm (an A\* variant similar to the one shown in David Silver’s [paper](https://www.davidsilver.uk/wp-content/uploads/2020/03/coop-path-AIWisdom.pdf)).

---

## File Navigation Made Easy

### Sample_Case

The folder with the same name is composed of two files: ClassDefinitions (containing basic class definitions) and test.py, which contains the main code for analysis.

The function of this code is to compare the traditional "selfish" navigation systems and AutoFlow. It uses a map based on the one provided in the "Sample Case" section of our PDF report, and calculates the differences in median commute time, total CO2 emissions, and peak congestion levels between the two navigation systems.
