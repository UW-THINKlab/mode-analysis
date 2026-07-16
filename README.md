# Mode Analysis

## Overview

This project was initiated by THINK Lab as a way to differentiate travel through regions by their mode of travel (such as walk, bike, drive, bus, train), in order to better analyze behavior when using each respective mode.


The code base focuses on Location Based Service (LBS) data, and contains functionality for:
1. Processing the raw data into usable formats 
2. Calculating metrics like distance traveled, speed, sparsity
3. Applying algorithms to infer mode of travel 
4. Generating visualizations to describe differences between datasets

## Glossary

* **LBS Data** - Location-Based Service data, collected from devices that measure location (commonly via GPS and proximal wifi) as they move around the world
* **Location** - An exact spot on a map that something may be located, defined by latitude and longitude
* **Mobile device** - a cellular phone that records location data via GPS and nearby wifi networks
* **Record** - an individual datapoint in the dataset, representing a single location at a single time (during a trip)
* **Stop** - a location where the device remains for a period of time (multiple datapoints)
* **Spatio-temporal datapoint** A datapoint in the dataset that is defined by location information (latitude/longitude) and a moment in time.
* **Trajectory/Trip** - a path of travel that a device follows from an origin to a destination
* **User** - a person who is measured via the platform, represented by their mobile device's movements

## Running the code

1. Open the code base in an IDE that can support Jupyter Notebooks, for example PyCharm
2. Download any required data, for example [GeoLife](https://www.microsoft.com/en-us/download/details.aspx?id=52367), and place in the `data/` folder. Note that `rMove` and `Spectus` data must be obtained via private agreement.
3. Open the desired Jupyter Notebook and select a kernel that can run Python, we recommend `Python 3.12.12`
4. Run the code, cell by cell, according to your use case.
5. Note that some use cases require pre-processing of the raw data. For example, GeoLife must be pre-processed using the code in from `src.process_files_geolife`. This will only need to be completed once.

## Code Structure

```html
data/                                      # Raw LBS data to process, map shapefiles
draft_notebooks/                           # Investigations that are in a less polished state
images/                                    # Visualizations generated to summarize database characteristics
src/                                       # Code used across Jupyter notebooks (utility functions)
 |_ Existing_ThinkLab_Code/                # Code from previous projects that can process Spectus data into defined "trips"
 |_ thresholds/                            # Pre-defined boundaries to infer mode based on average or max speed
 |_ calculate_speed.py                     # Process dataframe and add inferred speed at each moment in time, based on comparison of consecutive datapoints
 |_ confusion_matrix.py                    # Generating visualization demonstrating how predictions deviate from ideal classification results
 |_ filters.py                             # Remove data deemed unsuitable for usage in training and testing
 |_ geospatial_analysis.py                 # Pulls in maps from cities (transit routes and bus stops) for comparison against locations in LBS data
 |_ map_terminology.py                     # Converts labels used for each mode to a standardized version in order to properly compare across algorithms, datasets
 |_ mawpy_analysis.py                      # One technique for mode analysis based off our lab's previously used thresholds: https://github.com/street-furniture/MAWpy2
 |_ optimized_analysis.py                  # The finely tuned thresholds found to maximize classification recall
 |_ plot.py                                # Utility functions for visualizing a single trip's speeds on a graph
 |_ predict_mode.py                        # The logic to compare inputs (average and max speed) against thresholds to determine mode
 |_ process_files_geolife.py               # Process raw data from GeoLife to make format more usable with our code
 |_ process_files_rmove.py                 # Process raw data from rMove to make format more usable with our code
 |_ spectus_analysis.py                    # Most basic analysis by speed threshold, using only maximum thresholds given by Spectus platform
 |_ stats.py                               # Used for calculating recall, precision, accuracy and other statistics for measuring algorithm performance
Dataset_Comparison_Graphs_Geolife.ipynb    # Visualizing various metrics related to the GeoLife dataset for comparison against other datasets
Dataset_Comparison_Graphs_rMove.ipynb      # Visualizing various metrics related to the rMove dataset for comparison against other datasets
Dataset_Comparison_Graphs_Spectus.ipynb    # Visualizing various metrics related to the Spectus dataset for comparison against other datasets
Generate_Anonymized_Data.ipynb             # Further processes already-processed data (input as speeds or metrics) in order to remove unique identifiers or other sensitive information
Generate_Dataset_Metrics.ipynb             # Processes dataset's spatio-temporal datapoints to gather descriptive statistics about each trip conducted
Mode_Analysis_By_Speed_Geolife.ipynb       # Full demonstration of applying various algorithms to GeoLife database, and displaying visualizations of speeds for given modes
Mode_Analysis_By_Speed_rMove.ipynb         # Full demonstration of applying various algorithms to rMove database, and displaying visualizations of speeds for given modes
Spectus_Spatial_Coverage.ipynb             # Generating visuals to demonstrate area of Seattle covered by Spectus sample data
```

### Key documents for each process
##### _Performing baseline mode analysis with speed thresholds_

_Mode_Analysis_By_Speed_Geolife_ and _Mode_Analysis_By_Speed_rMove_ contain logic to process the raw spatio-temporal datapoints and assign a speed at each moment in time, based on distance traveled and time elapsed. They then process each trip one at a time, obtaining average and max speed for the trip and then applying the defined thresholds to assign a predicted mode of travel. They summarize results with statistics and a confusion matrix to demonstrate performance.

##### _Processing the raw location data for use with training Deep Learning models_

_Generate_Anonymized_Data_ is used for processing raw spatio-temporal datapoints into a format that is usable by Deep Learning algorithms external to this Code Base (i.e. LSTM, Random Forest, Transformer models).

It returns all datapoints in the original dataset, but replaces the original latitude/longitude and timestamp with the features required for Deep Learning: The trip's trajectory ID, the time interval elapsed between since the previous datapoint, the speed at the current dataopint, the distance traveled since the previous datapoint, and the label of true mode of travel for the given trip. Trajectory ID and label will be the same across all datapoints in a given trip, whereas the time elapsed, speed and distance traveled will differ for each datapoint.

Data is only removed if the datapoints for a trip do not have a label for mode of travel, or if the label is "other".

##### _Generating metrics and visualizations for descriptive analysis of each dataset_

_Dataset_Comparison_Graphs_Geolife_, _Dataset_Comparison_Graphs_rMove_, and _Dataset_Comparison_Graphs_Spectus_ are used for comparing the datasets along a handful of metrics at the level of each trip in the dataset.

Graphs are displayed based off metrics generated within _Generate_Dataset_Metrics_, which looks at each individual trip in the dataset and summarizes it in terms of number of records, time duration, distance traveled, density of datapoints, sparsity of datapoints (at 5 second, 30 second, and 1 minute intervals), and average and maximum speed.

##### _Generating sparsity masks for Spectus data (to enable downsampling)_

_Generate_Downsampling_Masks_ contains logic for processing each trip in Spectus, resampling it into invervals of 5 seconds, 20 seconds, 30 seconds and 60 seconds, and then creating an output file summarizing the number of datapoints found in each interval the trip was divided into. The output does not include any intervals with zero datapoints, for the sake of storage space. The unique identifiers for each row are 'trip_id', 'bin_size_sec', and 'bin_index'.


### Notes on Data Adjustments

The Spectus dataset is given as raw Location-Based Service (LBS) datapoints that are not divided into stopping points (where the user remains for a period of time), nor trips (datapoints describing the motion of a user between stopping points). For this reason, we have applied the [scikit-mobility framework](https://github.com/scikit-mobility/scikit-mobility) for inferring stopping points and trips, in order to analyze each user's movements by each trip they make.

For the purpose of high quality data, we have filtered out trips from the Spectus dataset that meet the following criteria:
* number_of_records < 2
* total_trip_time_minutes <= 0
* total_distance_km <= 0
* non-finite speed values, e.g., inf or NaN in average/max speed