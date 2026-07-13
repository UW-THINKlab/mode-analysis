def make_max_speed_filter(threshold):
    def max_speed_filter(dataframe_with_speeds, average_speed, max_speed):
        if max_speed > threshold:
            return True

        return False

    return max_speed_filter

def sparse_data_filter(dataframe_with_speeds, average_speed, max_speed):
    if len(dataframe_with_speeds) < 8:
        return True

    # Check if any gap between datapoints is greater than 100 seconds
    has_large_time_gap = dataframe_with_speeds['timestamp'].diff().dt.total_seconds().abs().gt(400).any()
    if has_large_time_gap:
        return True

    return False

def make_speed_gap_filter(threshold):
    def speed_gap_filter(dataframe_with_speeds, average_speed, max_speed):
        speed_gaps = dataframe_with_speeds['speed_kmh'].diff().abs()
        if speed_gaps.gt(threshold).any():
            print(speed_gaps[speed_gaps > threshold])
            return True

        return False

    return speed_gap_filter

def get_filters_for_mode(mode):
    filters = []
    if mode == "Walk": filters.append(make_max_speed_filter(40.0))
    if mode == "Transit" or mode == "Drive SOV" or mode == "Drive HOV2" or mode == "Drive HOV3+":
        filters.append(make_speed_gap_filter(100.0))
    filters.append(sparse_data_filter)

    return filters