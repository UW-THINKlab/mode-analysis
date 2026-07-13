# Apply MAWpy ranking algorithm (THINK Lab owned)
# https://github.com/street-furniture/Spectus_street_furniture_analysis/tree/main/mawpy

import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import pprint
pp = pprint.PrettyPrinter()

from .calculate_speed import calculate_speed
from .predict_mode import predict_mode_mawpy
from .stats import is_correct_prediction_spectus

def update_mawpy_confusion_matrix(confusion_matrix,
                                  prediction,
                                  actual_mode):
    if prediction == "walk":
        col = 0
    elif prediction == "bike/run":
        col = 1
    elif prediction == "car":
        col = 2
    elif prediction == "unknown":
        col = 3
    else:
        col = -1

    if actual_mode == "walk":
        row = 0
    elif actual_mode == "bike":
        row = 1
    elif actual_mode == "bus":
        row = 2
    elif actual_mode == "taxi":
        row = 3
    elif actual_mode == "subway":
        row = 4
    elif actual_mode == "train":
        row = 5
    elif actual_mode == "airplane":
        row = 6
    else:
        row = -1

    confusion_matrix[row, col] = confusion_matrix[row, col] + 1

# Get error rate
def is_correct_prediction_mawpy(prediction,
                                actual_mode):
    if prediction == "walk":
        if actual_mode == "walk":
            return True
    elif prediction == "bike/run":
        if actual_mode == "bike":
            return True
    elif prediction == "car":
        if actual_mode == "car" or actual_mode == "taxi":
            return True

    return False

def analyze_all_trips_for_user_mawpy(confusion_matrix, error_state, base_path='data/Geolife/010/'):
    trajectory_path = f'{base_path}Processed_Trajectory/'
    labels_df = pd.read_csv(f'{base_path}labels.txt', sep='\t')

    for index, row in labels_df.iterrows():
        dt = pd.to_datetime(row['Start Time'])
        file_prefix = int(dt.strftime('%Y%m%d%H%M%S'))
        trajectory_files = [f for f in os.listdir(trajectory_path) \
                            if f.startswith(f"{file_prefix}")]

        # Only do ones with exactly one match, otherwise there is no label for that trajectory, or there were multiple that hour
        if len(trajectory_files) == 1:
            print('-----------')
            print(f"Start Time: {row['Start Time']}")
            print(f"Corresponding Trajectory File: {trajectory_files[0]}")
            file_to_process = f"{trajectory_path}{trajectory_files[0]}"
            df, average_speed, max_speed = calculate_speed(file_to_process)
            print(f"average speed: {average_speed}, max speed: {max_speed}")
            prediction = predict_mode_mawpy(average_speed, max_speed)
            print(f"mode predicted: {prediction}")
            actual_mode = row['Transportation Mode']
            print(f"actual mode: {actual_mode}")

            update_mawpy_confusion_matrix(confusion_matrix, prediction, actual_mode)

            if is_correct_prediction_spectus(prediction, actual_mode):
                error_state["successes"] += 1
            else:
                error_state["errors"] += 1

def run_mawpy_analysis(base_path='data/Geolife/010/'):
    confusion_matrix_mawpy = np.zeros((7, 4))
    error_state = {
        "errors": 0.0,
        "successes": 0.0
    }

    analyze_all_trips_for_user_mawpy(confusion_matrix_mawpy, error_state, base_path)
    print(confusion_matrix_mawpy)

    success_rate = error_state["successes"] / (error_state["errors"] + error_state["successes"]) * 100
    pp.pprint(error_state)
    print(f"Success Rate: {round(success_rate)}%")

    col_labels = ["walk", "bike/run", "car", "unknown"]
    row_labels = ["walk", "bike", "bus", "taxi", "subway", "train", "airplane"]

    plt.imshow(confusion_matrix_mawpy, cmap='Blues')
    plt.colorbar()
    plt.xticks(ticks=range(len(col_labels)), labels=col_labels, rotation=90)
    plt.yticks(ticks=range(len(row_labels)), labels=row_labels)
    plt.title('Prediction Based on MAWpy Analysis')

    plt.show()