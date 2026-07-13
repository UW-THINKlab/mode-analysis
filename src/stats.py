def new_classification_statistics():
    return {
        "walk": {
            "true_positive": 0.0,
            "false_positive": 0.0,
            "true_negative": 0.0,
            "false_negative": 0.0,
        },
        "bike": {
            "true_positive": 0.0,
            "false_positive": 0.0,
            "true_negative": 0.0,
            "false_negative": 0.0,
        },
        "taxi": {
            "true_positive": 0.0,
            "false_positive": 0.0,
            "true_negative": 0.0,
            "false_negative": 0.0,
        },
        "bus": {
            "true_positive": 0.0,
            "false_positive": 0.0,
            "true_negative": 0.0,
            "false_negative": 0.0,
        },
        "subway": {
            "true_positive": 0.0,
            "false_positive": 0.0,
            "true_negative": 0.0,
            "false_negative": 0.0,
        },
        "train": {
            "true_positive": 0.0,
            "false_positive": 0.0,
            "true_negative": 0.0,
            "false_negative": 0.0,
        },
        "airplane": {
            "true_positive": 0.0,
            "false_positive": 0.0,
            "true_negative": 0.0,
            "false_negative": 0.0,
        }
    }

def is_correct_prediction_spectus(prediction,
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
    elif prediction == "bus":
        if actual_mode == "bus":
            # We do not actually predict "bus" yet, based off the current speed model
            return True
    elif prediction == "train/highway":
        if actual_mode == "subway" or actual_mode == "train":
            return True
    elif prediction == "plane":
        if actual_mode == "airplane":
            return True

    return False

def is_correct_prediction_custom_thresholds(prediction,
                                            actual_mode):
    if prediction == actual_mode:
        return True
    if prediction == "walk" and actual_mode == "run":
        return True
    if prediction == "taxi" and actual_mode == "car":
        return True

    return False

def update_success_rate_stats(stats, prediction, actual_mode):
    if is_correct_prediction_spectus(prediction, actual_mode):
        stats["successes"] += 1
    else:
        stats["errors"] += 1

def update_classification_statistics(stats, prediction, actual_mode):
    if actual_mode == "run":
        actual_mode = "walk"
    if actual_mode == "car":
        actual_mode = "taxi"
    if actual_mode == "boat" or actual_mode == "motorcycle":
        return

    if is_correct_prediction_custom_thresholds(prediction, actual_mode):
        print(f"incrementing true_positive for {actual_mode}")
        stats[actual_mode]["true_positive"] += 1
        for mode in stats.keys():
            if mode != actual_mode:
                print(f"incrementing true_negative for {mode}")
                stats[mode]["true_negative"] += 1
    else:
        print(f"incrementing false_negative for {actual_mode}")
        stats[actual_mode]["false_negative"] += 1
        print(f"incrementing false_positive for {prediction}")
        if prediction != "unknown":
            stats[prediction]["false_positive"] += 1

def new_classification_statistics_rmove():
    return {
        "walk": {
            "true_positive": 0.0,
            "false_positive": 0.0,
            "true_negative": 0.0,
            "false_negative": 0.0,
        },
        "bike": {
            "true_positive": 0.0,
            "false_positive": 0.0,
            "true_negative": 0.0,
            "false_negative": 0.0,
        },
        "car": {
            "true_positive": 0.0,
            "false_positive": 0.0,
            "true_negative": 0.0,
            "false_negative": 0.0,
        },
        "transit": {
            "true_positive": 0.0,
            "false_positive": 0.0,
            "true_negative": 0.0,
            "false_negative": 0.0,
        },
        "other": {
            "true_positive": 0.0,
            "false_positive": 0.0,
            "true_negative": 0.0,
            "false_negative": 0.0,
        }
    }

def update_classification_statistics_rmove(stats, prediction, actual_mode):
    if is_correct_prediction_custom_thresholds(prediction, actual_mode):
        print(f"incrementing true_positive for {actual_mode}")
        stats[actual_mode]["true_positive"] += 1
        for mode in stats.keys():
            if mode != actual_mode:
                print(f"incrementing true_negative for {mode}")
                stats[mode]["true_negative"] += 1
    else:
        print(f"incrementing false_negative for {actual_mode}")
        stats[actual_mode]["false_negative"] += 1
        print(f"incrementing false_positive for {prediction}")
        if prediction != "unknown":
            stats[prediction]["false_positive"] += 1