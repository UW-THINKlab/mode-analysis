# Author: Ekin Ugurel
# Date: 01/19/2025

# Description: This script contains a class that preprocesses trajectory data by 
# filtering based on speed, clustering stay locations, and merging stay clusters 
# with trajectory points. The class also assigns trajectory IDs and adds distance 
# and velocity columns based on temporal sequence per user. Finally, it adds start 
# and end stay cluster information, start and end datetime information, and 
# trip metrics at the user level including duration, distance, speeds, and start/end 
# locations. The class can be used

# # Citations: 
# Uğurel, E., Guan, X., Wang, Y., Huang, S., Wang, Q. and Chen, C., 2024. 
# Correcting missingness in passively-generated mobile data with Multi-Task Gaussian Processes. 
# Transportation Research Part C: Emerging Technologies, 161, p.104523.

# Uğurel, E., Huang, S. and Chen, C., 2024. 
# Learning to generate synthetic human mobility data: 
# A physics-regularized Gaussian process approach based on multiple kernel learning. 
# Transportation Research Part B: Methodological, 189, p.103064.


import pandas as pd
import numpy as np
import skmob
from skmob.preprocessing import detection
from skmob.preprocessing import clustering

class TrajectoryPreprocessor:
    def __init__(self, data: pd.DataFrame):
        # Validate required columns
        required_cols = ['unix_start_t', 'user_ID', 'orig_lat', 'orig_long', 'orig_unc']
        if not all(col in data.columns for col in required_cols):
            raise ValueError(f"Missing required columns. Need: {required_cols}")
            
        self.raw_data = data.copy()
        self.processed_data = data.copy()
        
        # Column name mappings for flexibility
        self.col_maps = {
            'lat': 'orig_lat',
            'lon': 'orig_long',
            'unix': 'unix_start_t',
            'user': 'user_ID',
            'cluster': 'cluster',
            'traj_id': 'traj_id' 
        }

    def __repr__(self):
        return f"TrajectoryPreprocessor with {len(self.raw_data)} rows of data."
    
    def convert_timestamps(self) -> 'TrajectoryPreprocessor':
        """Convert unix timestamps to datetime."""
        self.processed_data['datetime'] = pd.to_datetime(
            self.processed_data[self.col_maps['unix']], unit='s'
        )
        # Augment column mappings
        self.col_maps['datetime'] = 'datetime'

        print("Converted unix timestamps to datetime format")
        return self
    
    def filter_by_speed(self, speed_threshold: float = 200) -> 'TrajectoryPreprocessor':
        """
        Filter trajectories based on speed using scikit-mobility
        
        Args:
            speed_threshold: Maximum speed in km/h (default: 200)
        """
        try:
            self.processed_data['original_user_id'] = self.processed_data[self.col_maps['user']]

            tdf = skmob.TrajDataFrame(
                self.processed_data,
                latitude=self.col_maps['lat'],
                longitude=self.col_maps['lon'],
                datetime=self.col_maps['datetime'],
                user_id=self.col_maps['user']
            )

            filtered_tdf = skmob.preprocessing.filtering.filter(
                tdf,
                max_speed_kmh=speed_threshold,
                include_loops=False
            )

            # Rename columns to match original data
            filtered_tdf.rename(columns={
                'lat': self.col_maps['lat'],
                'lng': self.col_maps['lon'],
                'datetime': self.col_maps['datetime'],
                'uid': self.col_maps['user']
            }, inplace=True)

            self.processed_data = pd.DataFrame(filtered_tdf)
            self.processed_data = self.processed_data.rename(columns={'original_user_id': self.col_maps['user']})

            print (f"Filtered trajectories based on speed threshold of {speed_threshold} km/h")
            return self
            
        except Exception as e:
            print(f"Error in speed filtering: {str(e)}")
            return self

    def stay_location_clustering(
        self,
        cluster_radius_km: float = 0.2,
        min_samples: int = 1,
        minutes_for_a_stop: int = 15,
        spatial_radius_km: float = 0.3,
        leaving_time: bool = True
    ) -> 'TrajectoryPreprocessor':
        """
        Cluster stay locations using scikit-mobility
        
        Args:
            cluster_radius_km: Radius for DBSCAN clustering in km (default: 0.2)
            min_samples: Minimum samples for DBSCAN clustering (default: 1)
            minutes_for_a_stop: Minimum duration for a stop in minutes (default: 15)
            spatial_radius_km: Spatial radius for stay location detection in km (default: 0.3)
            leaving_time: Whether to include leaving time in stay locations (default: True)
        """
        try:
            self.processed_data['original_user_id'] = self.processed_data[self.col_maps['user']]
            print(self.processed_data.head())

            tdf = skmob.TrajDataFrame(
                self.processed_data,
                latitude=self.col_maps['lat'],
                longitude=self.col_maps['lon'],
                datetime=self.col_maps['datetime'],
                user_id=self.col_maps['user']
            )

            print(self.processed_data.head())
            
            # First detect stay locations
            stay_locations = detection.stay_locations(
                tdf,
                spatial_radius_km=spatial_radius_km,
                minutes_for_a_stop=minutes_for_a_stop,
                leaving_time=leaving_time
            )

            # Then cluster them
            self.clustered_locations = pd.DataFrame(
                clustering.cluster(
                    stay_locations,
                    cluster_radius_km=cluster_radius_km,
                    min_samples=min_samples
                  )
            )

            # Rename columns to match original data
            self.clustered_locations.rename(columns={
                'lat': self.col_maps['lat'],
                'lng': self.col_maps['lon'],
                'datetime': self.col_maps['datetime'],
                'uid': self.col_maps['user']
            }, inplace=True)

            self.clustered_locations = self.clustered_locations.rename(columns={'original_user_id': self.col_maps['user']})
            
            print("Clustered stay locations")
            return self
            
        except Exception as e:
            print(f"Error in stay location clustering: {str(e)}")
            return self
        
    
    def merge_stay_clusters(self, batch_size: int = 10000) -> 'TrajectoryPreprocessor':
        """
        Merge stay clusters with trajectory points efficiently using batched processing.
        """
        if not hasattr(self, 'clustered_locations'):
            raise ValueError("Run stay_location_clustering first")

        def process_user_data(user_df: pd.DataFrame, user_stays: pd.DataFrame) -> pd.DataFrame:
            """Process data for a single user efficiently"""
            # Convert times to numpy arrays for faster comparison
            point_times = user_df['datetime'].astype(np.int64).values
            start_times = user_stays['datetime'].astype(np.int64).values[:, None]  # Shape: (n_stays, 1)
            end_times = user_stays['leaving_datetime'].astype(np.int64).values[:, None]  # Shape: (n_stays, 1)
            clusters = user_stays['cluster'].values
            
            # Initialize clusters array
            user_df['cluster'] = -99
            
            # Process in batches to manage memory
            for i in range(0, len(point_times), batch_size):
                batch_points = point_times[i:i + batch_size]
                
                # Create boolean mask for the current batch
                # Shape: (n_stays, batch_size)
                in_cluster = (batch_points >= start_times) & (batch_points <= end_times)
                
                # Find the first True in each column (if any)
                # This gives us the index of the cluster for each point
                cluster_indices = np.argmax(in_cluster, axis=0)
                
                # Only assign clusters where we actually found a match
                has_cluster = in_cluster.any(axis=0)
                cluster_assignments = np.where(has_cluster, clusters[cluster_indices], -99)
                
                user_df.iloc[i:i + batch_size, user_df.columns.get_loc('cluster')] = cluster_assignments
                
            return user_df

        # Process each user's data
        processed_dfs = []
        for user_id in self.processed_data[self.col_maps['user']].unique():
            user_df = self.processed_data[
                self.processed_data[self.col_maps['user']] == user_id
            ].copy()
            user_stays = self.clustered_locations[
                self.clustered_locations[self.col_maps['user']] == user_id
            ]
            
            if len(user_stays) > 0:
                try:
                    processed_user_df = process_user_data(user_df, user_stays)
                    processed_dfs.append(processed_user_df)
                except Exception as e:
                    print(f"Error processing user {user_id}: {str(e)}")
                    processed_dfs.append(user_df)  # Add original data without clusters
            else:
                user_df['cluster'] = -99
                processed_dfs.append(user_df)
        
        self.processed_data = pd.concat(processed_dfs, ignore_index=True)
        print("Merged stay clusters with trajectory points")
        return self
    
    def assign_trajectory_ids(self) -> 'TrajectoryPreprocessor':
        """
        Assign trajectory IDs to sequences of points that represent trips.
        A trajectory includes: last point at origin cluster -> trip points (-99) -> first point at destination cluster
        """
        # Work on each user's data separately
        processed_dfs = []
        
        for user_id in self.processed_data[self.col_maps['user']].unique():
            # Get user's data
            user_df = self.processed_data[
                self.processed_data[self.col_maps['user']] == user_id
            ].copy()
            
            # Create helper columns
            user_df['cluster_next'] = user_df['cluster'].shift(-1, fill_value=-99)
            user_df['cluster_prev'] = user_df['cluster'].shift(1, fill_value=-99)
            
            # Identify start of trips (where current point is at a cluster and next point is -99)
            trip_starts = (user_df['cluster'] != -99) & (user_df['cluster_next'] == -99)
            
            # Identify end of trips (where current point is -99 and next point is at a cluster)
            trip_ends = (user_df['cluster'] == -99) & (user_df['cluster_next'] != -99)
            
            # Also mark the first point of the destination cluster
            destination_points = (user_df['cluster'] != -99) & (user_df['cluster_prev'] == -99)
            
            # Create trajectory IDs
            # First, mark all points that should be part of a trajectory
            user_df['is_trajectory'] = (
                trip_starts |  # Origin point
                (user_df['cluster'] == -99) |  # Trip points
                destination_points  # Destination point
            )
            
            # Use cumsum on the trip_starts to create unique trajectory IDs
            user_df['traj_id'] = np.where(
                user_df['is_trajectory'],
                trip_starts.cumsum(),
                -99
            )
            
            # Clean up helper columns
            user_df.drop(['cluster_next', 'cluster_prev', 'is_trajectory'], 
                        axis=1, inplace=True)
            
            processed_dfs.append(user_df)
        
        # Combine all processed user data
        self.processed_data = pd.concat(processed_dfs, ignore_index=True)
        print("Assigned trajectory IDs")
        return self
            
    @staticmethod
    def haversine_np(lon1, lat1, lon2, lat2):
        """Calculate the great circle distance between two points in meters"""
        lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        return c * 6371 * 1000  # Output distance in meters

    def add_distance(self, group: pd.DataFrame) -> pd.DataFrame:
        """Calculate distance between consecutive points"""
        lat1, lon1 = group[self.col_maps['lat']], group[self.col_maps['lon']]
        lat2, lon2 = lat1.shift(-1), lon1.shift(-1)
        dist = self.haversine_np(lon1, lat1, lon2, lat2)
        group['dist'] = dist.fillna(0)
        return group

    def add_velocity(self, group: pd.DataFrame) -> pd.DataFrame:
        """Calculate velocity between consecutive points"""
        if 'dist' not in group.columns:
            group = self.add_distance(group)
            
        time_diff = (group[self.col_maps['unix']] - 
                    group[self.col_maps['unix']].shift(1)).fillna(0)
        vel = group['dist'] / time_diff
        vel.iloc[0] = 0
        vel.replace([np.inf, -np.inf], np.nan, inplace=True)
        vel.fillna(0, inplace=True)
        group['vel'] = vel
        return group

    def add_dist_and_vel(self) -> 'TrajectoryPreprocessor':
        """Add distance and velocity columns based on temporal sequence per user"""
        # Process each user's data in temporal order
        self.processed_data = (self.processed_data.groupby(self.col_maps['user'], group_keys=True)
                            .apply(self.add_distance)
                            .reset_index(drop=False))

        print(self.processed_data.head())
        
        self.processed_data = (self.processed_data.groupby(self.col_maps['user'], group_keys=True)
                            .apply(self.add_velocity)
                            .reset_index(drop=True))

        self.processed_data = self.processed_data.rename(columns={'original_user_id': self.col_maps['user']})
        print(self.processed_data.head())

        print("Added distance and velocity columns")
        return self
    
    def add_start_end_stay_clusters(self) -> 'TrajectoryPreprocessor':
        """Add start and end cluster information per user's trajectories"""
        processed_dfs = []
        for user_id in self.processed_data[self.col_maps['user']].unique():
            # Get user's data
            user_df = self.processed_data[
                self.processed_data[self.col_maps['user']] == user_id
            ].copy()
            
            # Add index to preserve order
            user_df['_original_index'] = np.arange(len(user_df))
            
            # Group by trajectory ID for this user
            grouped = user_df.groupby(self.col_maps['traj_id']).agg({'cluster': ['first', 'last']})
            grouped.columns = ['start_cluster', 'end_cluster']

            # For traj_id == -99, set start and end cluster to -99
            grouped.loc[grouped.index == -99, 'start_cluster'] = -99
            
            # Merge back to user's data
            user_df = user_df.merge(
                grouped,
                left_on=self.col_maps['traj_id'],
                right_index=True
            )
            
            # Sort back to original order and drop index column
            user_df = user_df.sort_values('_original_index').drop('_original_index', axis=1)
            
            processed_dfs.append(user_df)
        
        # Combine all processed user data
        self.processed_data = pd.concat(processed_dfs, ignore_index=True)
        print("Added start and end stay cluster columns")
        return self

    def add_start_end_datetimes(self) -> 'TrajectoryPreprocessor':
        """Add start and end datetime information per user's trajectories"""
        processed_dfs = []
        
        for user_id in self.processed_data[self.col_maps['user']].unique():
            # Get user's data
            user_df = self.processed_data[
                self.processed_data[self.col_maps['user']] == user_id
            ].copy()
            
            # Add index to preserve order
            user_df['_original_index'] = np.arange(len(user_df))
            
            # Group by trajectory ID for this user
            grouped = user_df.groupby(self.col_maps['traj_id']).agg({'datetime': ['first', 'last']})
            grouped.columns = ['start_datetime', 'end_datetime']

            # For traj_id == -99, set start and end datetime to -99
            grouped['start_datetime'] = grouped['start_datetime'].astype(object)
            grouped.loc[grouped.index == -99, 'start_datetime'] = -99
            
            # Merge back to user's data
            user_df = user_df.merge(
                grouped,
                left_on=self.col_maps['traj_id'],
                right_index=True
            )
            
            # Sort back to original order and drop index column
            user_df = user_df.sort_values('_original_index').drop('_original_index', axis=1)
            
            processed_dfs.append(user_df)
        
        # Combine all processed user data
        self.processed_data = pd.concat(processed_dfs, ignore_index=True)
        print("Added start and end datetime columns")
        return self

    def add_trip_metrics(self) -> 'TrajectoryPreprocessor':
        """Add trip metrics at the user level including duration, distance, speeds, and start/end locations"""
        processed_dfs = []
        
        for user_id in self.processed_data[self.col_maps['user']].unique():
            # Get user's data
            user_df = self.processed_data[
                self.processed_data[self.col_maps['user']] == user_id
            ].copy()
            
            # Add index to preserve order
            user_df['_original_index'] = np.arange(len(user_df))
            
            # Calculate metrics per trajectory
            grouped = user_df.groupby(self.col_maps['traj_id']).agg({
                'datetime': lambda x: (pd.to_datetime(x.max()) - pd.to_datetime(x.min())).total_seconds() / 3600,  # hours
                'dist': 'sum',  # total distance
                'vel': 'max',  # maximum speed
                self.col_maps['lat']: ['first', 'last'],  # start and end latitudes
                self.col_maps['lon']: ['first', 'last']  # start and end longitudes
            })
            
            # Rename columns
            grouped.columns = [
                'trip_duration', 'trip_distance', 'max_speed',
                'start_lat', 'end_lat',
                'start_lon', 'end_lon'
            ]
            
            # Calculate average speed (km/h)
            grouped['avg_speed'] = grouped['trip_distance'] / (grouped['trip_duration'] * 3600)
            
            # For traj_id == -99, set metrics to 0
            if -99 in grouped.index:
                zero_cols = ['trip_duration', 'trip_distance', 'max_speed', 'avg_speed']
                grouped.loc[-99, zero_cols] = 0
            
            # Replace inf values in speeds with 0
            grouped.replace([np.inf, -np.inf], 0, inplace=True)
            
            # Merge back to user's data
            user_df = user_df.merge(
                grouped,
                left_on=self.col_maps['traj_id'],
                right_index=True
            )
            
            # Sort back to original order and drop index column
            user_df = user_df.sort_values('_original_index').drop('_original_index', axis=1)
            
            processed_dfs.append(user_df)
        
        # Combine all processed user data
        self.processed_data = pd.concat(processed_dfs, ignore_index=True)
        print("Added trip metrics")
        return self
    
    def add_point_counts(self) -> 'TrajectoryPreprocessor':
        """Add count of points for each trajectory at the user level"""
        processed_dfs = []
        
        for user_id in self.processed_data[self.col_maps['user']].unique():
            # Get user's data
            user_df = self.processed_data[
                self.processed_data[self.col_maps['user']] == user_id
            ].copy()
            
            # Add index to preserve order
            user_df['_original_index'] = np.arange(len(user_df))
            
            # Calculate point counts per trajectory
            point_counts = user_df.groupby(self.col_maps['traj_id']).size()
            point_counts = point_counts.to_frame('point_count')
            
            # Merge back to user's data
            user_df = user_df.merge(
                point_counts,
                left_on=self.col_maps['traj_id'],
                right_index=True
            )
            
            # Sort back to original order and drop index column
            user_df = user_df.sort_values('_original_index').drop('_original_index', axis=1)
            
            processed_dfs.append(user_df)
        
        # Combine all processed user data
        self.processed_data = pd.concat(processed_dfs, ignore_index=True)
        print("Added point counts per trajectory")
        return self

    def create_compressed_trips(self) -> 'TrajectoryPreprocessor':
        """
        Create a compressed trips dataframe with essential trip information including metrics.
        """
        required_cols = [
            'start_cluster', 'end_cluster', 'start_datetime', 'end_datetime',
            'trip_duration', 'trip_distance'
        ]
        if not all(col in self.processed_data.columns for col in required_cols):
            raise ValueError("Run add_start_end_stay_clusters, add_start_end_datetimes, and add_trip_metrics first")

        compressed_dfs = []
        
        for user_id in self.processed_data[self.col_maps['user']].unique():
            # Get user's data
            user_df = self.processed_data[
                self.processed_data[self.col_maps['user']] == user_id
            ]
            
            # Group by trajectory ID and take relevant metrics
            compressed = user_df.groupby(self.col_maps['traj_id']).agg({
                self.col_maps['user']: 'first',
                'start_cluster': 'first',
                'end_cluster': 'first',
                'start_datetime': 'first',
                'end_datetime': 'first',
                'trip_duration': 'first',
                'trip_distance': 'first',
                'max_speed': 'first',
                'avg_speed': 'first',
                'start_lat': 'first',
                'end_lat': 'first',
                'start_lon': 'first',
                'end_lon': 'first',
                'point_count': 'first'
            }).reset_index()
            
            compressed_dfs.append(compressed)
        
        # Store the compressed trips dataframe as class attribute
        self.compressed_trips = pd.concat(compressed_dfs, ignore_index=True)
        print("Created compressed trips dataframe")
        return self

    def process_all(self) -> pd.DataFrame:
        """Run all preprocessing steps"""
        return (self
                .convert_timestamps()
                .add_dist_and_vel()
                .add_start_end_stay_clusters()
                .add_start_end_datetimes()
                .add_trip_metrics()
                .create_compressed_trips()
                .processed_data)
    
