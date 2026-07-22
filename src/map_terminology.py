def map_to_shared_mode_names(input):
    if (input == "taxi" or
        input == "Drive SOV" or
        input == "Drive HOV2" or
        input == "Drive HOV3+" or
        input == "Ride Hail" or
        input == "Household vehicle 1" or
        input == "Household vehicle 2" or
        input == "Household vehicle 3" or
        input == "Friend/colleague's car" or
        input == "Other hired service (Uber, Lyft, or other smartphone-app car service)" or
        input == "Other non-household vehicle" or
        input == "Other vehicle in household" or
        input == "Car from work"):
        return "car"

    if (input == "Bus (public transit)" or
        input == "School Bus" or
        input == "School Bus2" or
        input == "School Bus3" or
        input == "Private bus or shuttle"):
        return "bus"

    if (input == "Walk (or jog/wheelchair)"):
        return "walk"

    if (input == "Bicycle or e-bike (rSurvey only)" or
        input == "Standard bicycle (my household's)"):
        return "bike"

    if (input == "Urban Rail (e.g., Link light rail, monorail)"):
        return "train"

    input = input.lower()
    return input


# Add these
# "Carshare service (e.g., Turo, Zipcar, ReachNow)"
# "Other hired service (Uber, Lyft, or other smartphone-app car service)"
# "Other mode (e.g., skateboard, kayak, motorhome, etc.)"
# "Other rail (e.g., streetcar)"
# "Taxi (e.g., Yellow Cab)"
# "Urban Rail (e.g., Link light rail, monorail)"
# Airplane or helicopter
# Bicycle or e-bike (rSurvey only)
# Bus (public transit)
# Car from work
# Ferry or water taxi
# Friend/colleague's car
# Household vehicle 1
# Household vehicle 2
# Household vehicle 3
# Household vehicle 4
# Missing Response
# Other bus (rMove only)
# Other motorcycle/moped/scooter
# Other non-household vehicle
# Other vehicle in household
# Private bus or shuttle
# Rental car
# School bus
# Vanpool
rMove_to_generic_mode_map = {
    "Borrowed bicycle (e.g., a friend's)": "bike",
    "Carshare service (e.g., Turo, Zipcar, Getaround, GIG)": "car",
    "Commuter rail (Sounder, Amtrak)": "rail",
    "Other hired car service (e.g., black car, limo)": "car",
    "Other hired service (Uber, Lyft, or other smartphone-app car service)": "car",
    "Other mode (e.g., skateboard, kayak, motorhome, etc.)": "other",
    "Other scooter, moped, skateboard": "other",
    "Scooter-share (e.g., Bird, Lime)": "other",
    "Taxi (e.g., Yellow Cab)": "car",
    "Urban Rail (e.g., Link light rail, monorail, streetcar)": "rail",
    "Airplane or helicopter": "other",
    "Bicycle or e-bike (rSurvey only)": "bike",
    "Bike-share - electric bicycle": "bike",
    "Bike-share - standard bicycle": "bike",
    "Bus (public transit)": "bus",
    "Car from work": "car",
    "Electric bicycle (my household's)": "bike",
    "Ferry or water taxi": "boat",
    "Friend/colleague's car": "car",
    "Household vehicle 1": "car",
    "Household vehicle 2": "car",
    "Household vehicle 3": "car",
    "Household vehicle 4": "car",
    "Household vehicle 5": "car",
    "Household vehicle 6": "car",
    "Household vehicle 7": "car",
    "Household vehicle 8": "car",
    "Missing Response": "other",
    "Other bus (rMove only)": "bus",
    "Other motorcycle (not my household's)": "other",
    "Other motorcycle in household": "other",
    "Other non-household vehicle": "car",
    "Other rail": "rail",
    "Other rented bicycle": "bike",
    "Other vehicle in household": "car",
    "Paratransit": "other",
    "Personal scooter or moped (not shared)": "other",
    "Private bus or shuttle": "bus",
    "Rental car": "car",
    "School bus": "bus",
    "Segway or Onewheel/electric unicycle": "other",
    "Skateboard or rollerblade": "other",
    "Standard bicycle (my household's)": "bike",
    "Vanpool": "other",
    "Vehicle ferry (took vehicle on board)": "boat",
    "Walk (or jog/wheelchair)": "walk",
}

rMove_to_generic_mode_map_lowercase = {
    key.lower(): value for key, value in rMove_to_generic_mode_map.items()
}

def map_rmove_to_generic_mode(rmove_label):
    return rMove_to_generic_mode_map_lowercase.get(rmove_label.lower(), rmove_label)