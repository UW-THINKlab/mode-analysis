# Reads each file (.plt) in a user's Trajectory/ folder (.plt) and aggregates all points
# Then splits into new files directly corresponding to each trip in user's labels.txt file
# Output: Processed_Trajectory folder in each user's directory (i.e. 010/Processed_Trajectory/)
# Usage: call pre_process_all_files_in_directory(), which will process all users in 'data/Geolife/'

import os
import pandas as pd

def labels_iterrable(labels_path):
    labels_df = pd.read_csv(labels_path, sep='\t')
    return labels_df.iterrows()

def get_filename_for_label_row(row, trajectory_path):
    dt = pd.to_datetime(row['Start Time'])
    file_prefix = int(dt.strftime('%Y%m%d%H%M%S'))
    trajectory_files = [f for f in os.listdir(trajectory_path) \
                        if f.startswith(f"{file_prefix}")]

    # Only do ones with exactly one match, otherwise there is no label for that trajectory, or there were multiple that hour
    if len(trajectory_files) == 1:
        return trajectory_files[0]

def pre_process_files(folder_path):
    trajectory_path = f'{folder_path}Trajectory/'
    labels_df = pd.read_csv(f'{folder_path}labels.txt', sep='\t')
    new_path = f'{folder_path}Processed_Trajectory/'
    if not os.path.exists(new_path):
        os.makedirs(new_path)

    trajectory_files = sorted([f for f in os.listdir(trajectory_path)])
    massive_dataframe = pd.DataFrame(columns=['lat', 'lng', '0', 'alt', 'days_since_1899', 'date', 'time'])
    for file in trajectory_files:
        filename = f"{trajectory_path}{file}"
        df = pd.read_csv(filename,
                         skiprows=6,
                         names=['lat', 'lng', '0', 'alt', 'days_since_1899', 'date', 'time'])
        massive_dataframe = pd.concat([massive_dataframe, df], ignore_index=True)

    # print(massive_dataframe.head(10))
    # print(massive_dataframe.tail(10))
    massive_dataframe['datetime'] = pd.to_datetime(massive_dataframe['date'] + ' ' + massive_dataframe['time'])
    massive_dataframe = massive_dataframe.set_index('datetime')

    for index, row in labels_df.iterrows():
        start_time = pd.to_datetime(row['Start Time'])
        end_time = pd.to_datetime(row['End Time'])
        corresponding_rows = massive_dataframe.loc[start_time:end_time]

        file_prefix = f"{start_time.strftime('%Y%m%d%H%M%S')}.plt"
        full_path = f"{new_path}{file_prefix}"
        # print(f"Writing to {file_prefix}...")

        with open(full_path, 'w') as f:
            f.write("Geolife trajectory\n")
            f.write("WGS 84\n")
            f.write("Altitude is in Feet\n")
            f.write("Reserved 3\n")
            f.write("0,2,255,My Track,0,0,2,8421376\n")
            f.write("0\n")

        corresponding_rows.to_csv(full_path, index=False, header=False, mode='a')

def pre_process_all_files_in_directory(root_path = 'data/Geolife/'):
    for file in sorted([f for f in os.listdir(root_path)]):
        path = f"{root_path}{file}/"
        print(f'Processing {path}...')
        pre_process_files(path)
        print('Done!')