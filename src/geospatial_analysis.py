import geopandas as gpd

def evaluate_transit_likelihood(points_dataframe):
    points_geodataframe = gpd.GeoDataFrame(points_dataframe,
                                           geometry=gpd.points_from_xy(points_dataframe.lng,
                                                                       points_dataframe.lat))
    points_geodataframe.crs = "EPSG:4326"  # For lat/lon data
    points_geodataframe = points_geodataframe.to_crs(epsg=3857)

    has_enough_route_overlap = check_route_overlap(points_geodataframe)
    # check_stops_against_slow_points(points_geodataframe)

    return has_enough_route_overlap

def check_route_overlap(points_geodataframe):
    metro_routes = gpd.read_file("data/King County Metro/KC_Metro_Routes.geojson")
    metro_routes = metro_routes.to_crs(epsg=3857)
    # metro_routes = gpd.read_file("data/WSDOT/WSDOT_Specific_Transit_Routes.geojson")
    # metro_routes = metro_routes.to_crs(epsg=3857)
    link_routes = gpd.read_file("data/STPublicData/LINKLine.shp")
    link_routes = link_routes.to_crs(epsg=3857)

    # print(f"Number of datapoints: {len(points_geodataframe)}")

    metro_overlap = gpd.sjoin_nearest(
        points_geodataframe,
        metro_routes,
        how="inner",
        max_distance=50,  # in CRS units (meters if projected)
        distance_col="dist"
    )
    num_points_overlapped_metro = metro_overlap['timestamp'].nunique()
    # print(f"Points overlapping Metro routes: {num_points_overlapped_metro}")

    # 2319612701006_Transit.csv ?
    link_overlap = gpd.sjoin_nearest(
        points_geodataframe,
        link_routes,
        how="inner",
        max_distance=200,  # in CRS units (meters if projected)
        distance_col="dist"
    )
    num_points_overlapped_link = link_overlap['timestamp'].nunique()
    # print(f"Points overlapping Link routes: {num_points_overlapped_link}")

    num_total_points = len(points_geodataframe)
    if num_points_overlapped_metro >= (0.9 * num_total_points) or \
       num_points_overlapped_link >= (0.9 * num_total_points):
        return True
    elif num_total_points - num_points_overlapped_metro == 1 or \
         num_total_points - num_points_overlapped_link == 1:
        return True
    else:
        return False

def check_stops_against_slow_points(points_geodataframe):
    metro_stops = gpd.read_file("data/King County Metro/KC_Metro_Stops.geojson")
    metro_stops = metro_stops.to_crs(epsg=3857)
    metro_stops = metro_stops[metro_stops["STOP_STATUS"] == "ACT"]