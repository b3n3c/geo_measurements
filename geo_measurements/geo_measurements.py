import math
import os
from math import sqrt
from typing import List, Tuple, Dict

import utm
from geographiclib.geodesic import Geodesic
from shapely.geometry import Point
from pyproj import Transformer, Geod
import geopandas as gpd
from shapely.geometry.polygon import Polygon

continent_crs_mapping = {
    'Africa': 'ESRI:102024',
    'Antarctica': 'EPSG:3031',
    'Asia': 'ESRI:102012',
    'Australia': 'EPSG:3577',
    'Europe': 'EPSG:4937',
    'North America': 'ESRI:102008',
    'South America': 'ESRI:102033',
    'Oceania': 'EPSG:5489'
}

countries_shapefile_path = os.path.join(os.path.dirname(__file__), "geo_data", "ne_10m_admin_0_countries.shp")
continents_shapefile_path = os.path.join(os.path.dirname(__file__), "geo_data", "world-continents.shp")

countries_data_frame = gpd.read_file(countries_shapefile_path)
continents_data_frame = gpd.read_file(continents_shapefile_path)


def determine_countries(points: List[Tuple[float, float]], country_crs: Dict[str, str]) -> set:
    """
    Determines the countries in which the given points are located using a spatial query.

    Parameters:
        points (List[Tuple[float, float]]): A list of tuples where each tuple represents a geographic point
                                            in (latitude, longitude) format.
        country_crs (Dict[str, str]): A dictionary mapping country names to their EPSG codes.

    Returns:
        set: A set of country names where each point is located based on the country boundaries.
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
    """
    Determines the continents in which the given points are located using a spatial query.

    Parameters:
        points (List[Tuple[float, float]]): A list of tuples where each tuple represents a geographic point
                                            in (latitude, longitude) format.
        continent_crs (Dict[str, str]): A dictionary mapping continent names to their EPSG codes.

    Returns:
        set: A set of continent names where each point is located based on the continent boundaries.
    """
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
        continent_crs: Dict[str, str] = continent_crs_mapping
) -> tuple[str | None, list[tuple[float, float]]]:
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
                                                 Defaults to `continent_crs_mapping`.

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
        continent_crs: Dict[str, str] = continent_crs_mapping
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
        continent_crs (Dict[str, str], optional): Dictionary mapping continent names to their EPSG codes. Defaults to `continent_crs_mapping`.

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


def calculate_area(
        points: List[Tuple[float, float]],
        country_crs: Dict[str, str] | None = None,
        use_continent_crs: bool = True,
        continent_crs: Dict[str, str] = continent_crs_mapping,
        reorder_points: bool = False,
) -> float:
    """
    Calculates the area enclosed by a polygon formed by a list of geographic points (latitude, longitude).
    Uses the appropriate CRS for the area calculation, preferring country or continent-specific CRS if applicable.

    Parameters:
        points (List[Tuple[float, float]]): A list of tuples representing the vertices of the polygon in
                                            (latitude, longitude) format.
        country_crs (Dict[str, str] | None, optional): A dictionary mapping country names to their EPSG codes.
                                                       If all points lie within the same country, that country's CRS
                                                       will be used. Defaults to None.
        use_continent_crs (bool, optional): If True, attempts to use continent-specific CRS when points span multiple countries
                                            but remain within a single continent. Defaults to True.
        continent_crs (Dict[str, str], optional): A dictionary mapping continent names to their EPSG codes. Defaults to `continent_crs_mapping`.
        reorder_points (bool, optional): If True, reorders points to form an irregular polygon.
                                         Defaults to False.

    Returns:
        float: The area of the polygon in square meters if calculated using a projected CRS or in square meters (approximate)
               if calculated with the WGS84 geodesic CRS.

    Notes:
        - If an optimal CRS is determined (either a country or continent-specific CRS), the area is calculated in a planar
          projection using the shoelace formula.
        - If no specific CRS can be applied and WGS84 is used, the geodesic area calculation is performed using
          `pyproj.Geod.geometry_area_perimeter`, which accounts for Earth's curvature.
    """
    crs, points = convert_points_to_optimal_crs(points, country_crs, use_continent_crs, continent_crs)

    if reorder_points:
        points = order_points_for_polygon(points)

    if crs == "wgs84":
        polygon = Polygon(points)
        geod = Geod(ellps="WGS84")
        poly_area, _ = geod.geometry_area_perimeter(polygon)
        return abs(poly_area)

    n = len(points)
    area = 0.0
    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]
        area += x1 * y2 - y1 * x2
    return abs(area) / 2.0


def order_points_for_polygon(points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """
    Orders points to form an irregular polygon.

    Parameters:
        points (List[Tuple[float, float]]): A list of tuples representing points in a planar CRS.

    Returns:
        List[Tuple[float, float]]: A list of points ordered to form an irregular polygon.
    """
    if len(points) < 3:
        return points

    centroid = (
        sum(p[0] for p in points) / len(points),
        sum(p[1] for p in points) / len(points)
    )

    def angle_from_centroid(point):
        dx = point[0] - centroid[0]
        dy = point[1] - centroid[1]
        return math.atan2(dy, dx)

    sorted_points = sorted(points, key=lambda p: angle_from_centroid(p),
                           reverse=True)

    return sorted_points


def calculate_bearing(start_point: Tuple[float, float],
                      dest_point: Tuple[float, float],
                      country_crs: Dict[str, str] | None = None,
                      use_continent_crs: bool = True,
                      continent_crs: Dict[str, str] = continent_crs_mapping
                      ) -> float:
    """
    Calculates the bearing (in degrees) from the starting point to the destination point.

    Parameters:
        start_point (Tuple[float, float]): The starting point as a tuple of (latitude, longitude).
        dest_point (Tuple[float, float]): The destination point as a tuple of (latitude, longitude).
        country_crs (Dict[str, str] | None, optional): Dictionary mapping country names to their EPSG codes.
                                                       Defaults to None.
        use_continent_crs (bool, optional): If True, uses continent-specific CRS if applicable.
                                            Defaults to True.
        continent_crs (Dict[str, str], optional): Dictionary mapping continent names to their EPSG codes.
                                                 Defaults to `continent_crs_mapping`.

    Returns:
        float: The bearing angle in degrees, from the starting point to the destination point.
    """

    crs, points = convert_points_to_optimal_crs([start_point, dest_point], country_crs, use_continent_crs,
                                                continent_crs)

    if crs == "wgs84":
        return Geodesic.WGS84.Inverse(start_point[0], start_point[1], dest_point[0], dest_point[1])['azi1']

    dx = points[1][0] - points[0][0]
    dy = points[1][1] - points[0][1]

    angle_radians = math.atan2(dx, dy)
    angle_degrees = math.degrees(angle_radians)

    if angle_degrees < 0:
        angle_degrees += 180

    return angle_degrees


def section(point1: Tuple[float, float],
            point2: Tuple[float, float],
            m: int, n: int,
            country_crs: Dict[str, str] | None = None,
            use_continent_crs: bool = True,
            continent_crs: Dict[str, str] = continent_crs_mapping) -> Tuple[float, float]:
    """
    Calculates the sectioning point between two points given as (latitude, longitude) tuples.

    Parameters:
        point1 (Tuple[float, float]): The first WGS84 point as (latitude, longitude).
        point2 (Tuple[float, float]): The second WGS84 point as (latitude, longitude).
        m (int): The first segment ratio of the sectioning.
        n (int): The second segment ratio of the sectioning.
        country_crs (Dict[str, str] | None, optional): Dictionary mapping country names to their EPSG codes.
                                                       Defaults to None.
        use_continent_crs (bool, optional): If True, uses continent-specific CRS if applicable.
                                            Defaults to True.
        continent_crs (Dict[str, str], optional): Dictionary mapping continent names to their EPSG codes.
                                                 Defaults to `continent_crs_mapping`.

    Returns:
        Tuple[float, float]: The sectioning point (latitude, longitude) in WGS84.
    """
    crs, points = convert_points_to_optimal_crs([point1, point2], country_crs, use_continent_crs, continent_crs)

    x1, y1 = points[0][0], points[0][1]
    x2, y2 = points[1][0], points[1][1]

    x = (float)((n * x1) + (m * x2)) / (m + n)
    y = (float)((n * y1) + (m * y2)) / (m + n)

    if crs == "wgs84":
        return x, y
    elif crs == "utm":
        utm_zone, utm_letter = utm.from_latlon(point1[0], point2[1])[2:4]
        return utm.to_latlon(x, y, utm_zone, utm_letter)
    else:
        transformer = Transformer.from_crs(crs, "EPSG:4326", always_xy=True)
        result = transformer.transform(x, y)
        return result[1], result[0]