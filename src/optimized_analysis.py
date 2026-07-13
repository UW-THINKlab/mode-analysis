import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import pprint
pp = pprint.PrettyPrinter()

from .calculate_speed import calculate_speed, calculate_speed_for_dataframe
from .confusion_matrix import update_confusion_matrix_new_threshold, update_confusion_matrix_rmove
from .filters import get_filters_for_mode
from .predict_mode import predict_mode_with_custom_thresholds, update_prediction_with_transit_information
from .process_files_geolife import labels_iterrable, get_filename_for_label_row
from .stats import new_classification_statistics, new_classification_statistics_rmove, update_classification_statistics, update_classification_statistics_rmove
from .thresholds.custom_thresholds import strict as strict_thresholds, rMove as rMove_thresholds

# Optimal Algorithm
def analyze_all_trips_for_user(thresholds, base_path, classification_statistics, confusion_matrix):
    trajectory_path = f'{base_path}Processed_Trajectory/'
    labels_path = f'{base_path}labels.txt'

    for index, row in labels_iterrable(labels_path):
        trajectory_file = get_filename_for_label_row(row, trajectory_path)
        file_to_process = f"{trajectory_path}{trajectory_file}"

        print('-----------')
        print(f"Base path: {base_path}")
        print(f"Start Time: {row['Start Time']}")
        print(f"Corresponding Trajectory File: {trajectory_file}")

        df, average_speed, max_speed = calculate_speed(file_to_process)
        if len(df) <= 1:
            print("Not enough data points for trip, skipping mode prediction")
            continue

        priority = ['walk', 'bike', 'taxi', 'bus', 'subway', 'train', 'airplane']
        prediction = predict_mode_with_custom_thresholds(average_speed, max_speed, priority, thresholds)
        print(f"max speed: {max_speed}, average speed: {average_speed}")
        print(f"mode predicted: {prediction}")

        actual_mode = row['Transportation Mode']
        print(f"actual mode: {actual_mode}")

        update_classification_statistics(classification_statistics, prediction, actual_mode)
        update_confusion_matrix_new_threshold(confusion_matrix, prediction, actual_mode)

def get_prediction_for_trip(dataframe, thresholds=strict_thresholds):
    df, average_speed, max_speed = calculate_speed_for_dataframe(dataframe)
    priority = ['walk', 'bike', 'taxi', 'bus', 'subway', 'train', 'airplane']
    prediction = predict_mode_with_custom_thresholds(average_speed, max_speed, priority, thresholds)

    return prediction

def get_prediction_for_trip_rmove(dataframe, thresholds=rMove_thresholds):
    df, average_speed, max_speed = calculate_speed_for_dataframe(dataframe)
    priority = ['walk', 'car', 'bike', 'transit']
    prediction = predict_mode_with_custom_thresholds(average_speed, max_speed, priority, thresholds)
    prediction = map_rMove_mode_predicted(prediction)

    return prediction

# Optimal Algorithm
def analyze_all_users(
        thresholds = strict_thresholds,
        root_path = 'data/Geolife/',
        with_stats = True,
        with_confusion_matrix = True
):

    if with_stats:
        stats = new_classification_statistics()
    if with_confusion_matrix:
        confusion_matrix = np.zeros((8, 8))

    for directory in sorted([f for f in os.listdir(root_path)]):
        user_path = f"{root_path}{directory}/"
        analyze_all_trips_for_user(thresholds, user_path, stats, confusion_matrix)

    print('-- Classification Statistics Totals:')
    pp.pprint(stats)

    for mode in stats.keys():
        true_positive = stats[mode]["true_positive"]
        true_negative = stats[mode]["true_negative"]
        false_positive = stats[mode]["false_positive"]
        false_negative = stats[mode]["false_negative"]

        print(f"-- Classification Statistics for {mode} (n={int(true_positive + false_negative)}):")
        recall = (true_positive) / (true_positive + false_negative)
        print(f"Recall (Success Rate): {str(round(recall, 2))}")
        accuracy = (true_positive + true_negative) / (true_positive + true_negative + false_positive + false_negative)
        print(f"Accuracy: {str(round(accuracy, 2))}")
        precision = (true_positive) / (true_positive + false_positive)
        print(f"Precision: {str(round(precision, 2))}")

    col_labels = ["walk", "bike", "taxi", "bus", "subway", "train", "airplane", "unknown"]
    row_labels = ["walk", "bike", "taxi", "bus", "subway", "train", "airplane", "unknown"]

    plt.imshow(confusion_matrix, cmap='Blues')
    plt.colorbar()
    plt.xticks(ticks=range(len(col_labels)), labels=col_labels, rotation=90)
    plt.yticks(ticks=range(len(row_labels)), labels=row_labels)
    plt.title('Prediction Based on New Thresholds')

    plt.show()

def get_mode_from_file_path(file_path):
    return file_path.split('/')[-1].split('_')[-1].split('.csv')[0]

def map_rMove_mode_actual(declared_mode):
    if declared_mode == "Walk":
        return "walk"
    elif declared_mode == "Bike" or declared_mode == "Micromobility":
        return "bike"
    elif declared_mode == "Drive SOV" or declared_mode == "Drive HOV2" or declared_mode == "Drive HOV3+" or declared_mode == "Ride Hail":
        return "car"
    elif declared_mode == "Transit":
        return "transit"
    else:
        return "other"

def map_rMove_mode_predicted(predicted_mode):
    if predicted_mode == "taxi":
        return "car"
    elif predicted_mode == "bus" or predicted_mode == "subway" or predicted_mode == "train":
        return "transit"
    elif predicted_mode == "airplane" or predicted_mode == "unknown":
        return "other"
    else:
        return predicted_mode

def analyze_trip_rMove(file_to_process, thresholds=rMove_thresholds, classification_statistics=None, confusion_matrix=None, filters=None):
    print('-----------')
    print(f"File to Process: {file_to_process}")

    points_dataframe = pd.read_csv(file_to_process)
    points_dataframe = points_dataframe.rename(columns={'lon': 'lng', 'collect_time': 'timestamp'})
    points_dataframe['timestamp'] = pd.to_datetime(points_dataframe['timestamp'])

    df, average_speed, max_speed = calculate_speed_for_dataframe(points_dataframe)

    if filters:
        for should_filter_out in filters:
            if should_filter_out(df, average_speed, max_speed):
                print("Skipping analysis due to bad data")
                return

    priority = ['walk', 'car', 'bike', 'transit']
    prediction = predict_mode_with_custom_thresholds(average_speed, max_speed, priority, thresholds)
    # prediction = update_prediction_with_transit_information(prediction, points_dataframe)
    prediction = map_rMove_mode_predicted(prediction)
    print(f"max speed: {max_speed}, average speed: {average_speed}")
    print(f"mode predicted: {prediction}")

    declared_mode = get_mode_from_file_path(file_to_process)
    actual_mode = map_rMove_mode_actual(declared_mode)
    print(f"actual mode: {actual_mode}")

    if classification_statistics is not None:
        update_classification_statistics_rmove(classification_statistics, prediction, actual_mode)
    if confusion_matrix is not None:
        update_confusion_matrix_rmove(confusion_matrix, prediction, actual_mode)

def analyze_all_rMove(
        max_count = None,
        thresholds = rMove_thresholds,
        root_path = 'data/rMove/Processed_Trajectory/',
        with_stats = True,
        with_confusion_matrix = True
):

    if with_stats:
        stats = new_classification_statistics_rmove()
    if with_confusion_matrix:
        confusion_matrix = np.zeros((5, 5))

    count = 0
    for f in os.scandir(root_path):
        if max_count == None or count < max_count:
            mode = get_mode_from_file_path(f.path)
            filters = get_filters_for_mode(mode)

            analyze_trip_rMove(f.path, thresholds, stats, confusion_matrix, filters)
        count += 1

    print(confusion_matrix.astype(int))

    print('-- Classification Statistics Totals:')
    pp.pprint(stats)

    total_recall_denominator = 0.0
    total_recall_numerator = 0.0
    for mode in stats.keys():
        true_positive = stats[mode]["true_positive"]
        true_negative = stats[mode]["true_negative"]
        false_positive = stats[mode]["false_positive"]
        false_negative = stats[mode]["false_negative"]

        try:
            print(f"-- Classification Statistics for {mode} (n={int(true_positive + false_negative)}):")
            recall = (true_positive) / (true_positive + false_negative)
            total_recall_numerator += true_positive
            total_recall_denominator += (true_positive + false_negative)
            print(f"Recall (Success Rate): {str(round(recall, 2))}")
            accuracy = (true_positive + true_negative) / (true_positive + true_negative + false_positive + false_negative)
            print(f"Accuracy: {str(round(accuracy, 2))}")
            precision = (true_positive) / (true_positive + false_positive)
            print(f"Precision: {str(round(precision, 2))}")
        except ZeroDivisionError:
            print("Unable to divide by 0")

    total_recall = total_recall_numerator / total_recall_denominator
    print(f"Total Recall: {str(round(total_recall, 2))}")

    # Prediction
    col_labels = ["walk", "bike", "car", "transit", "other"]
    # Actual
    row_labels = ["walk", "bike", "car", "transit", "other"]

    plt.imshow(confusion_matrix, cmap='Blues')
    plt.colorbar()
    plt.xticks(ticks=range(len(col_labels)), labels=col_labels, rotation=90)
    plt.yticks(ticks=range(len(row_labels)), labels=row_labels)
    plt.title('Prediction Based on New Thresholds')

    plt.show()