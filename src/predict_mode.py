from .geospatial_analysis import evaluate_transit_likelihood
from .thresholds.custom_thresholds import strict as strict_thresholds

def predict_mode_spectus(speed):
    if speed < 4.0:
        return "walk"
    elif speed < 15.0:
        return "bike/run"
    elif speed < 80.0:
        return "car"
    elif speed < 200:
        return "train/highway"
    else:
        return "plane"

def predict_mode_mawpy(average_speed, max_speed):
    if 0.1 <= average_speed <= 15.0 and max_speed <= 25.0:
        return "walk"
    elif 10.0 <= average_speed <= 150.0 and max_speed <= 200.0:
        return "car"
    elif 5.0 <= average_speed <= 30.0 and max_speed <= 60.0:
        return "bike/run"
    else:
        return "unknown"

def predict_mode_with_custom_thresholds(
        average_speed,
        max_speed,
        priority = ['walk', 'taxi', 'bus', 'subway', 'train', 'airplane'],
        thresholds = strict_thresholds
):
    predicted_mode = 'unknown'
    for mode in priority:
        threshold = thresholds[mode]
        if (threshold['min_avg_speed'] <= average_speed <= threshold['max_avg_speed'] and max_speed <= threshold['max_max_speed']):
            predicted_mode = mode
            break

    return predicted_mode

def update_prediction_with_transit_information(prediction, points_dataframe):
    if evaluate_transit_likelihood(points_dataframe):
        return "transit"
    else:
        return prediction