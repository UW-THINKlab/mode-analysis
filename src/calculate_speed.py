import numpy as np
import pandas as pd

# Haversine function (vectorized)
# This is faster than importing from Haversine, because it will apply to whole dataset at once, rather than one row at a time
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    return 2 * R * np.arcsin(np.sqrt(a))

def calculate_speed(file_to_process):
    # Read file as dataframe
    df = pd.read_csv(file_to_process,
                     skiprows=6,
                     names=['lat', 'lng', '0', 'alt', 'days_since_1899', 'date', 'time'])

    return calculate_speed_for_dataframe(df)

# Generates speed between each point in the CSV file, chronologically
# Also applies truncation of extreme outliers (>98% and <1%), and smoothing of curves (5 point rolling average)
def calculate_speed_for_dataframe(df, with_smoothing=True):
    # Combine date and time into a single timestamp column
    if 'timestamp' not in df.columns:
        df['timestamp'] = pd.to_datetime(df['date'] + ' ' + df['time'])
    df = df.sort_values('timestamp')

    # Calculate distance traveled for each point (from previous)
    df['distance_km'] = haversine(
        df['lat'].shift(1), df['lng'].shift(1),
        df['lat'], df['lng']
    )

    # Calculate time difference in hours
    df['time_diff_hr'] = (df['timestamp'] - df['timestamp'].shift(1)).dt.total_seconds() / 3600

    # Calculate speed
    df['speed_kmh'] = df['distance_km'] / df['time_diff_hr']

    # Set first row to 0 because no point to compare against
    df[['distance_km', 'time_diff_hr', 'speed_kmh']] = df[['distance_km', 'time_diff_hr', 'speed_kmh']].fillna(0)

    if with_smoothing:
        # Smooth top 3% and bottom 1% of speeds
        upper_cap = df['speed_kmh'].quantile(0.98)
        lower_cap = df['speed_kmh'].quantile(0.01)
        df['speed_kmh'] = df['speed_kmh'].clip(lower=lower_cap, upper=upper_cap)

        # Smooth curves with rolling window
        df['speed_kmh'] = df['speed_kmh'].rolling(window=5).mean()

    average_speed = df['speed_kmh'].mean()
    # average_speed = dataframe['distance_km'].sum() / dataframe['time_diff_hr'].sum()
    max_speed = df['speed_kmh'].max()

    return df, average_speed, max_speed