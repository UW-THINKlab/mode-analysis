import os
import pandas as pd

def clear_outputs_directory(path = 'data/rMove/Processed_Trajectory/'):
    # Remove older files, rather than appending to them
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        os.remove(file_path)

def pre_process_files(folder_path, locations_path):
    locations_df = pd.read_csv(f'{folder_path}{locations_path}')
    trips_df = pd.read_csv(f'{folder_path}Household_Travel_Survey_Trips_-7221806773183684102.csv', low_memory=False)
    trips_df = trips_df.set_index('trip_id')
    new_path = f'{folder_path}Processed_Trajectory/'
    if not os.path.exists(new_path):
        os.makedirs(new_path)
    else:
        clear_outputs_directory(new_path)

    count = 0
    for trip, group in locations_df.groupby('tripid'):
        if trip in trips_df.index and len(group) > 5:
            trip_info = trips_df.loc[trip]
            mode = trip_info['mode_class']
            file_name = f"{trip}_{mode}.csv"
            full_path = f"{new_path}{file_name}"

            print(f"Writing to {file_name}...")
            group.to_csv(full_path, index=False, header=True, mode='a')
            count += 1

    print(f'Processed {count} trips with corresponding trip in survey table')

def pre_process_all_files_in_directory(root_path = 'data/rMove/'):
    file_path = 'Location_2023.csv'
    print(f'Processing {file_path}...')
    pre_process_files(root_path, file_path)
    print('Done!')

def get_dataframe_from_file_path(file_path):
    points_dataframe = pd.read_csv(file_path)
    points_dataframe = points_dataframe.rename(columns={'lon': 'lng', 'collect_time': 'timestamp'})
    points_dataframe['timestamp'] = pd.to_datetime(points_dataframe['timestamp'])

    return points_dataframe