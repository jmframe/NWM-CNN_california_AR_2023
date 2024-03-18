# Analysis Code for NWM-CNN
This repository contains the IPython notebooks used for the analysis presented in our paper on flood prediction using the NWM-CNN model. The analysis demonstrates the capability of the NWM-CNN model to predict surface water area across California, leveraging data from the U.S. National Water Model and a convolutional neural network.

# Repository Structure
* Figure1.ipynb: Analysis code for Figure 1 in the paper.  
* Table1.ipynb: Analysis code for Table 1 in the paper.  
* Figure2: QGIS map, no code available.  
* Figure3.ipynb: Analysis code for Figure 3 in the paper.  
* environment.yml: Conda environment file to recreate the analysis environment.  

# Data Directory Structure
* The data used in this analysis is hosted on HydroShare (link to be added) and has the following directory structure within the repository:
* NWM-CNN_predictions: Predictions from the NWM-CNN model.
* csv_files: Miscellaneous data files in CSV format.
* images_for_sacramento_stats: Images and statistics for Sacramento area analysis.
* map: QGIS map files.
* shapefile: Shapefiles used in the analysis.

# Usage
To use the analysis notebooks:
1. Ensure you have Conda installed.
2. Clone this repository to your local machine.
3. Navigate to the repository directory and create the Conda environment from environment.yml:  ``conda env create -f environment.yml``
4. Activate the environment:  ``conda activate nwm-cnn``
5. Open the Jupyter notebooks in Jupyter Lab or Notebook

# Floodbase
For more information please visit: [](floodbase.com)