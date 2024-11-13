from math import sqrt
from typing import List, Tuple, Dict

import utm
from geographiclib.geodesic import Geodesic
from shapely.geometry import Point
from pyproj import Transformer
import geopandas as gpd

national_crs_mapping = {
    "Hungary": "EPSG:23700",
    "Serbia": "EPSG:8682",
}

continental_crs_mapping = {
    'Europe': 'EPSG:3035'
}

countries_shapefile_path = "geo_data/ne_10m_admin_0_countries.shp"
continents_shapefile_path = "geo_data/world-continents.shp"

countries_data_frame = gpd.read_file(countries_shapefile_path)
continents_data_frame = gpd.read_file(continents_shapefile_path)


def determine_countries(points: List[Tuple[float, float]], country_crs: Dict[str, str]) -> set:
    """
    Determines the countries in which the given points are located using a spatial query.
    """
    countries = set()
    for lat, lon in points:
        point = Point(lon, lat)
        for _, country in countries_data_frame.iterrows():
            if country['NAME'] in country_crs.keys():
                if country.geometry.contains(point):
                    countries.add(country['NAME'])
                    break
    return countries


def determine_continents(points: List[Tuple[float, float]], continent_crs: Dict[str, str]) -> set:
    continents = set()
    for lat, lon in points:
        point = Point(lon, lat)
        for _, continent in continents_data_frame.iterrows():
            if continent['CONTINENT'] in continent_crs.keys():
                if continent.geometry.contains(point):
                    continents.add(continent['CONTINENT'])
                    break
    return continents


def convert_points_to_optimal_crs(
        points: List[Tuple[float, float]],
        country_crs: Dict[str, str] | None = None,
        use_continent_crs: bool = True,
        continent_crs: Dict[str, str] = continental_crs_mapping
) -> tuple[str | None, list[tuple]]:
    """
    Converts a list of WGS84 geographic coordinates (latitude, longitude) to an optimal coordinate reference system (CRS)
    based on their geographical location. Prioritizes country-specific CRS if all points are in the same country,
    then UTM zone if in the same zone, or continental CRS if in the same continent. Defaults to WGS84 if no single CRS applies.

    Parameters:
        points (List[Tuple[float, float]]): A list of tuples where each tuple represents a geographic point in
                                            (latitude, longitude) format.
        country_crs (Dict[str, str] | None, optional): A dictionary mapping country names to their EPSG codes.
                                                       If all points are in a single country, the country's CRS will be used.
                                                       Defaults to None.
        use_continent_crs (bool, optional): If True, attempts to use continent-specific CRS when points span multiple countries
                                            but are within the same continent. Defaults to True.
        continent_crs (Dict[str, str], optional): A dictionary mapping continent names to their EPSG codes.
                                                 Defaults to `continental_crs_mapping`.

    Returns:
        tuple[str | None, list[tuple]]:
            - Optimal CRS as a string (e.g., EPSG code or "utm"/"wgs84" for universal cases).
            - List of transformed points in the new CRS as tuples.
    """
    countries = dict()
    continents = dict()

    if country_crs is not None:
        countries = determine_countries(points, country_crs)
    if use_continent_crs is True:
        continents = determine_continents(points, continent_crs)

    if len(countries) == 1:
        # The points are located in one country
        country = next(iter(countries))
        transformer = Transformer.from_crs("EPSG:4326", country_crs.get(country), always_xy=True)
        transformed_points = [transformer.transform(lon, lat)[:2] for lat, lon in points]
        optimal_crs = country_crs.get(country)
        return optimal_crs, transformed_points
    else:
        utm_points = [utm.from_latlon(lat, lng) for lat, lng in points]
        utm_zones = {point[2:4] for point in utm_points}
        if len(utm_zones) == 1:
            # The points are located in one UTM zone
            transformed_points = [point[:2] for point in utm_points]
            return "utm", transformed_points
        elif len(continents) == 1:
            # The points are located in one continent
            continent = next(iter(continents))
            transformer = Transformer.from_crs("EPSG:4326", continent_crs.get(continent), always_xy=True)
            transformed_points = [transformer.transform(lon, lat)[:2] for lat, lon in points]
            optimal_crs = continent_crs.get(continent)
            return optimal_crs, transformed_points
        else:
            return "wgs84", points


def calculate_distance(
    point1: Tuple[float, float],
    point2: Tuple[float, float],
    country_crs: Dict[str, str] | None = None,
    use_continent_crs: bool = True,
    continent_crs: Dict[str, str] = continental_crs_mapping
) -> float:
    """
    Calculates the distance between two geographic points, selecting an optimal CRS for the calculation.

    Parameters:
        point1 (Tuple[float, float]): Geographic coordinates of the first point in WGS84 format (latitude, longitude).
        point2 (Tuple[float, float]): Geographic coordinates of the second point in WGS84 format (latitude, longitude).
        country_crs (Dict[str, str] | None, optional): Dictionary mapping country names to their EPSG codes.
                                                       If both points are in the same country, the country's CRS
                                                       will be used. Defaults to None.
        use_continent_crs (bool, optional): If True, and points span multiple countries but are on the same continent,
                                            the continent-specific CRS will be used. Defaults to True.
        continent_crs (Dict[str, str], optional): Dictionary mapping continent names to their EPSG codes. Defaults to `continental_crs_mapping`.

    Returns:
        float: The calculated distance between the two points in meters.

    Notes:
        - If an optimal CRS cannot be determined, the distance is calculated in WGS84 using geodesic distance.
        - Euclidean distance is used if a country or continent-specific CRS is applied.
    """
    crs, points = convert_points_to_optimal_crs([point1, point2], country_crs, use_continent_crs, continent_crs)

    if crs == "wgs84":
        distance = Geodesic.WGS84.Inverse(point1[0], point1[1], point2[0], point2[1])['s12']
        return distance

    return sqrt((points[1][0] - points[0][0]) ** 2 + (points[1][1] - points[0][1]) ** 2)