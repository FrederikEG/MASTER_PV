# Agrivoltaic systems Foulum

**This repository is currently private and will become public when we publish the accompanying paper.**


This repository includes scripts to process, validate, and analyze the data collected at the Agrivoltaics demonstration site in Foulumgaard which is part of the Hyperfarm project.

The script 'clean_data.py' retrieves raw data files from the weather stations and the inverters datalogger, creates a data file named 'clean_data.csv' and stores it in the folder 'resources'. 

Other scripts such as 'radiation_comparison.py' or 'efficiency_analysis.py' use the common data file 'clean_data.csv' to implement different analyses. 
