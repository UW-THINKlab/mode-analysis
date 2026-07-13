import numpy as np
import pprint
pp = pprint.PrettyPrinter()

from .calculate_speed import calculate_speed
from .predict_mode import predict_mode_spectus
from .process_files_geolife import labels_iterrable, get_filename_for_label_row
from .stats import update_success_rate_stats


def run_spectus_analysis(base_path='data/Geolife/010/',
                         plot_speeds = True,
                         with_stats = True,
                         with_confusion_matrix = True):
    trajectory_path = f'{base_path}Processed_Trajectory/'
    labels_path = f'{base_path}labels.txt'

    if with_stats:
        stats_for_average = {
            "errors": 0.0,
            "successes": 0.0
        }
        stats_for_max = {
            "errors": 0.0,
            "successes": 0.0
        }
    if with_confusion_matrix:
        confusion_matrix = np.zeros((8, 8))

    for index, row in labels_iterrable(labels_path):
        trajectory_file = get_filename_for_label_row(row, trajectory_path)
        file_to_process = f"{trajectory_path}{trajectory_file}"

        print('-----------')
        print(f"Base path: {base_path}")
        print(f"Start Time: {row['Start Time']}")
        print(f"Corresponding Trajectory File: {trajectory_file}")
        df, average_speed, max_speed = calculate_speed(file_to_process)

        prediction_for_average = predict_mode_spectus(average_speed)
        prediction_for_max = predict_mode_spectus(max_speed)
        actual_mode = row['Transportation Mode']
        print(f"mode for average speed: {prediction_for_average}")
        print(f"mode for max speed: {prediction_for_max}")
        print(f"actual mode: {actual_mode}")
        update_success_rate_stats(stats_for_average, prediction_for_average, actual_mode)
        update_success_rate_stats(stats_for_max, prediction_for_max, actual_mode)

        label = f"{file_to_process[20:]}"
        if plot_speeds:
            df['speed_kmh'].plot(label=label)

    if with_stats:
        average_success_rate = stats_for_average["successes"] / (
                    stats_for_average["errors"] + stats_for_average["successes"]) * 100
        max_success_rate = stats_for_max["successes"] / (stats_for_max["errors"] + stats_for_max["successes"]) * 100

        pp.pprint(stats_for_average)
        pp.pprint(stats_for_max)
        print(f"Average Success Rate: {round(average_success_rate)}%")
        print(f"Max Success Rate: {round(max_success_rate)}%")