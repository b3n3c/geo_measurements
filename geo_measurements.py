from typing import List, Tuple, Dict

import utm
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

def convert_points_to_optimal_crs(points: List[Tuple[float, float]], country_crs: Dict[str, str] | None =None, continent_crs: Dict[str, str] | None =None) -> tuple[str | None, list[tuple]]:
    countries = dict()
    continents = dict()

    if country_crs is not None:
        countries = determine_countries(points, country_crs)
    if continent_crs is not None:
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


test_points = [(47.4979, 19.0402), (44.7866, 20.4489)]  # Coordinates for Budapest, Hungary and Belgrade, Serbia
print("Countries:", determine_countries(test_points, national_crs_mapping))
print("Continents:", determine_continents(test_points, continental_crs_mapping))