# Plot different trips (speeds) against each other to observe trends

import contextily as ctx
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import pandas as pd

from .calculate_speed import calculate_speed, calculate_speed_for_dataframe
from .filters import get_filters_for_mode
from .process_files_geolife import get_filename_for_label_row, labels_iterrable

def plot_speeds(points_dataframe, ax, label=None, with_average_and_max=True, filters=None):
    dataframe, average_speed, max_speed = calculate_speed_for_dataframe(points_dataframe)
    print(f'Average speed: {average_speed}, Max speed: {max_speed}')

    if len(dataframe) <= 1:
        return
    if filters:
        for should_filter_out in filters:
            if should_filter_out(dataframe, average_speed, max_speed):
                return

    # dataframe['speed_kmh'].plot(ax=ax, label=label)
    dataframe['time_from_start'] = (dataframe['timestamp'] - dataframe['timestamp'].min()).dt.total_seconds()
    dataframe.plot(ax=ax, label=label, x='time_from_start', y='speed_kmh')
    if with_average_and_max:
        ax.axhline(y=average_speed, color='red', linestyle='--')
        ax.axhline(y=max_speed, color='blue', linestyle='--')

# Usage: process_datetimes(["2008/03/29 16:00:00", "2008/03/30 16:00:00", "2008/03/31 16:00:08"])
def process_datetimes(datetimes_to_process, base_path='data/Geolife/010/'):
    trajectory_path = f'{base_path}Processed_Trajectory/'
    labels_path = f'{base_path}labels.txt'

    fig, ax = plt.subplots()

    for index, row in labels_iterrable(labels_path):
        if (row['Start Time'] in datetimes_to_process):
            trajectory_file = get_filename_for_label_row(row, trajectory_path)
            file_to_process = f"{trajectory_path}{trajectory_file}"
            points_dataframe = pd.read_csv(file_to_process,
                                           skiprows=6,
                                           names=['lat', 'lng', '0', 'alt', 'days_since_1899', 'date', 'time'])
            plot_speeds(points_dataframe, ax, f"{file_to_process[-18:]} ({row['Transportation Mode']})")

    ax.legend(loc='upper right')
    plt.title('Train Journeys with Average and Max Plotted')
    plt.show()

# Usage: plot_all_trips_for_specific_mode("walk", 0, 20)
def plot_all_trips_for_specific_mode(mode, start_index, end_index, base_path='data/Geolife/010/'):
    trajectory_path = f'{base_path}Processed_Trajectory/'
    labels_path = f'{base_path}labels.txt'

    fig, ax = plt.subplots()

    count = 0
    for index, row in labels_iterrable(labels_path):
        if (row['Transportation Mode'] == mode and count < end_index):
            if count <= start_index:
                count += 1
                continue

            trajectory_file = get_filename_for_label_row(row, trajectory_path)
            file_to_process = f"{trajectory_path}{trajectory_file}"
            points_dataframe = pd.read_csv(file_to_process,
                                           skiprows=6,
                                           names=['lat', 'lng', '0', 'alt', 'days_since_1899', 'date', 'time'])
            plot_speeds(points_dataframe, ax, f"{file_to_process[-18:]} ({row['Transportation Mode']})")

            count += 1

    ax.legend(loc='upper right')
    plt.title(f'"{mode}" Journeys with Average and Max Plotted')
    plt.show()

# Usage: plot_all_trips_for_specific_mode("walk", 0, 20)
def plot_all_trips_rMove_for_mode(mode,
                                  start_index,
                                  end_index,
                                  with_average_and_max=False,
                                  base_path='data/rMove/Processed_Trajectory'):
    fig, ax = plt.subplots()

    count = 0
    for f in os.scandir(base_path):
        if count >= end_index:
            break
        if count < start_index:
            count += 1
            continue
        if f.name.endswith(f"{mode}.csv"):
            print(f.name)
            points_dataframe = pd.read_csv(f.path)
            points_dataframe = points_dataframe.rename(columns={'lon': 'lng', 'collect_time': 'timestamp'})
            points_dataframe['timestamp'] = pd.to_datetime(points_dataframe['timestamp'])

            filters = get_filters_for_mode(mode)
            plot_speeds(points_dataframe,
                        ax,
                        f"{f.name[:13]}",
                        with_average_and_max,
                        filters=filters)
            count += 1

    ax.legend(loc='upper right')
    if with_average_and_max:
        title = f'"{mode}" Journeys with Average and Max Plotted'
    else:
        title = f'"{mode}" Journeys'
    plt.title(title)
    plt.show()

def plot_speeds_for_single_trip(points_dataframe, with_average_and_max=False):
    fig, ax = plt.subplots()

    df_with_speeds, average_speed, max_speed = calculate_speed_for_dataframe(points_dataframe)
    df_with_speeds['time_from_start'] = (df_with_speeds['timestamp'] - df_with_speeds['timestamp'].min()).dt.total_seconds()
    df_with_speeds.plot(ax=ax, x='time_from_start', y='speed_kmh')
    if with_average_and_max:
        ax.axhline(y=average_speed, color='red', linestyle='--')
        ax.axhline(y=max_speed, color='blue', linestyle='--')

    plt.show()

def plot_trip_on_map(points_dataframe, include_transit=False, and_transit_stops=False):
    points_geodataframe = gpd.GeoDataFrame(points_dataframe,
                                           geometry=gpd.points_from_xy(points_dataframe.lng,
                                                                       points_dataframe.lat))
    points_geodataframe.crs = "EPSG:4326"  # For lat/lon data
    points_geodataframe = points_geodataframe.to_crs(epsg=3857)

    fig, ax = plt.subplots()

    if include_transit:
        metro_routes = gpd.read_file("data/King County Metro/KC_Metro_Routes.geojson")
        metro_routes = metro_routes.to_crs(epsg=3857)
        if and_transit_stops:
            metro_stops = gpd.read_file("data/King County Metro/KC_Metro_Stops.geojson")
            metro_stops = metro_stops.to_crs(epsg=3857)
            metro_stops = metro_stops[metro_stops["STOP_STATUS"] == "ACT"]
        link_routes = gpd.read_file("data/STPublicData/LINKLine.shp")
        link_routes = link_routes.to_crs(epsg=3857)

        metro_routes.plot(ax=ax, color="steelblue", linewidth=1.5, zorder=2)
        if and_transit_stops:
            metro_stops.plot(ax=ax, color="red", zorder=2)
        link_routes.plot(ax=ax, color="mediumturquoise", linewidth=3, zorder=3)

    points_geodataframe.plot(ax=ax, color="yellow", zorder=4)
    points_geodataframe.iloc[[0]].plot(ax=ax, color='mediumseagreen', zorder=5)
    points_geodataframe.iloc[[-1]].plot(ax=ax, color='orangered', zorder=5)

    bounds = points_geodataframe.total_bounds
    x_buffer = (bounds[2] - bounds[0]) * 0.1  # 10% of width
    y_buffer = (bounds[3] - bounds[1]) * 0.1
    ax.set_xlim(bounds[0] - x_buffer, bounds[2] + x_buffer)
    ax.set_ylim(bounds[1] - y_buffer, bounds[3] + y_buffer)

    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)

    plt.show()

def plot_trips_on_map(mode=None,
                      start_index=None,
                      end_index=None,
                      base_path='data/rMove/Processed_Trajectory'):

    count = 0
    for f in os.scandir(base_path):
        if end_index != None and count >= end_index:
            break
        if start_index != None and count < start_index:
            count += 1
            continue
        if mode != None and f.name.endswith(f"{mode}.csv") == False:
            count += 1
            continue

        print(f.name)
        points_dataframe = pd.read_csv(f.path)
        points_dataframe = points_dataframe.rename(columns={'lon': 'lng', 'collect_time': 'timestamp'})
        points_dataframe['timestamp'] = pd.to_datetime(points_dataframe['timestamp'])

        should_include_transit = mode == "Transit"
        plot_trip_on_map(points_dataframe, include_transit=should_include_transit)

        count += 1