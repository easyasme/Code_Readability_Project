#!/usr/bin/env python3

import requests
import math
from collections import Counter

# Function to get the current location of Starlink satellites
def get_starlink_satellites():
    url = "https://api.spacexdata.com/v4/starlink"
    response = requests.get(url)
    return response.json()

# Function to calculate the direction (N, NNE, NE, etc.) from a given location
def calculate_direction(lat1, lon1, lat2, lon2):
    directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    dx = lon2 - lon1
    dy = lat2 - lat1
    angle = math.degrees(math.atan2(dy, dx))
    if angle < 0:
        angle += 360
    compass_index = round(angle / 22.5)
    return directions[compass_index % 16]

# Function to calculate the distance between two points using the Haversine formula
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# Function to calculate azimuth and elevation angles
def calculate_angles(lat1, lon1, lat2, lon2, alt2):
    # Calculate azimuth
    dlon = math.radians(lon2 - lon1)
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(dlon))
    azimuth = math.atan2(x, y)
    azimuth = math.degrees(azimuth)
    if azimuth < 0:
        azimuth += 360

    # Calculate elevation
    distance = haversine(math.degrees(lat1), lon1, math.degrees(lat2), lon2)
    elevation = math.atan2(alt2, distance)
    elevation = math.degrees(elevation)
    
    return azimuth, elevation

# Function to find the direction counts of satellites within a specified range
def find_satellite_directions(satellites, lat, lon, max_distance_km):
    directions = []
    satellite_data = []
    for satellite in satellites:
        sat_lat = satellite.get('latitude')
        sat_lon = satellite.get('longitude')
        sat_alt = satellite.get('height_km', 550)  # Assuming height_km is available in the data, default to 550 km if not
        if sat_lat is not None and sat_lon is not None:
            distance = haversine(lat, lon, sat_lat, sat_lon)
            if distance <= max_distance_km:
                direction = calculate_direction(lat, lon, sat_lat, sat_lon)
                directions.append(direction)
                satellite_data.append({
                    'latitude': sat_lat,
                    'longitude': sat_lon,
                    'altitude': sat_alt,
                    'direction': direction,
                    'distance': distance
                })
    direction_counts = Counter(directions)
    return direction_counts, satellite_data

# Coordinates for London, UK
lat_london = 51.5074
lon_london = -0.1278

# Maximum distance to consider (in kilometers)
max_distance_km = 1000

# Get current Starlink satellites data
satellites = get_starlink_satellites()

# Find the direction counts of satellites within the specified range
direction_counts, satellite_data = find_satellite_directions(satellites, lat_london, lon_london, max_distance_km)

if direction_counts:
    highest_density_direction = direction_counts.most_common(1)[0]
    print(f"The direction with the highest density of Starlink satellites from London within {max_distance_km} km is {highest_density_direction[0]} with {highest_density_direction[1]} satellites.\n")
    print("Starlink satellites in other directions are distributed as follows (from high to low density):")
    for direction, count in direction_counts.most_common():
        if direction != highest_density_direction[0]:
            print(f"{direction}: {count} satellites")

    # Output all satellite data for review
    print("\nSatellite data within range:")
    for data in satellite_data:
        print(data)

    # Calculate azimuth and elevation for satellites in the highest density direction
    azimuths = []
    elevations = []
    for data in satellite_data:
        if data['direction'] == highest_density_direction[0]:
            azimuth, elevation = calculate_angles(lat_london, lon_london, data['latitude'], data['longitude'], data['altitude'])
            azimuths.append(azimuth)
            elevations.append(elevation)
            print(f"Satellite at ({data['latitude']}, {data['longitude']}) - Azimuth: {azimuth:.2f} degrees, Elevation: {elevation:.2f} degrees")

    if azimuths and elevations:
        avg_azimuth = sum(azimuths) / len(azimuths)
        avg_elevation = sum(elevations) / len(elevations)
        print(f"\nAverage Azimuth: {avg_azimuth:.2f} degrees, Average Elevation: {avg_elevation:.2f} degrees")
    else:
        print("No valid satellites found in the highest density direction.")
else:
    print(f"No Starlink satellites found within {max_distance_km} km from London.")

