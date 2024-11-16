# GeoMeasurements
  
This Python project delivers a suite of geospatial utility functions for precise geographic coordinate measurements.
  
## Features  
- **Offline Country and Continent Identification**: Determines the countries and continents where geographic points are located.  
- **Optimal CRS Conversion**: Converts geographic coordinates (latitude, longitude) to the most suitable CRS based on location.  
- **Distance Calculation**: Computes geodesic or planar distances between two points.  
- **Area Calculation**: Calculates the area of a polygon formed by a list of geographic points.  
- **Bearing Calculation**: Determines the bearing angle between two points.  
- **Sectioning point calculation**: Determines the sectioning point between two geographic points  
- **Order points for polygon**: Orders a list of points to draw a polygon. This is needed for area calculations and also useful when displaying polygons on a map.   
  
## Setup  
Install using pip or clone repository.
  ## Usage  
Prepare geographic data in the form of latitude and longitude tuples. These coordinates should be in WGS84 (EPSG:4326) projection, which is the standard format for GPS systems and maps.  
#### Example:  
```python  
from geo_measurements import calculate_distance  
  
point1 = (47.497913, 19.040236)  # Budapest, Hungary  
point2 = (48.856613, 2.352222)   # Paris, France  
  
# Calculate distance  
distance = calculate_distance(point1, point2)  
print(f"Distance: {distance} meters")  
```  
By default, geographic coordinates are processed using the **UTM (Universal Transverse Mercator)** projection system. This ensures high precision for local calculations. However, when points are not within the same UTM zone or span large geographic areas, alternative CRS strategies are employed:  
  
1. **Points in Different UTM Zones**: The coordinates will be converted to a **continent-specific CRS** to maintain accuracy.  
2. **Points Spanning Multiple Continents**: If the points span more than one continent, the calculations will default to the **WGS84** CRS, which is a global geographic coordinate system. This will result in the least accurate calculations.  
  
This means that the package will try to convert the points into an optimal CRS in this order:  
  
**utm zone -> continent -> WGS84 (no conversion)**  
  
This behavior can be overwritten for added precision.  
  

### Overriding the Default Behavior

You can customize the default CRS handling by specifying the following parameters in the relevant functions:

 - **`country_crs`**: Define a custom CRS for country-level calculations. This CRS will be applied if all input points are within the specified country. The order of CRS application will then follow:
   **country → continent → UTM zone → WGS84**. 
   
   To optimize performance, try to keep this list as short as possible.     Example of a `country_crs` dictionary:  
   `country_crs = {
         "Hungary": "EPSG:23700",
         "Serbia": "EPSG:8682"   } `
  
   You can find accepted country names in the `country_names.txt` file. The corresponding EPSG codes can typically be retrieved from the relevant government body's website or from [epsg.io](https://epsg.io/).
   
 - **`continent_crs`**: Specify the CRS to be used for continent-level calculations. This allows you to override the default continent CRS mapping.  
       The default continent CRS mapping is:
   ```python
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
   ```
     The supported continent names are: **Africa**, **Antarctica**, **Asia**, **Australia**, **Europe**, **North America**, **South America**, **Oceania**.

 -   **`use_continent_crs`**: Set this boolean value to `False` to disable continent-level CRS calculations. When this is turned off, the CRS calculation order will be **country → UTM zone → WGS84**.


# Functions

## `determine_countries`
```python
def determine_countries(points: List[Tuple[float, float]], country_crs: Dict[str, str]) -> set
``` 

### Description:

This function determines the countries in which the provided geographic points are located. It uses a spatial query by comparing the given points' locations with country boundaries to identify the countries.

-   **Parameters**:
    
    -   `points` (List[Tuple[float, float]]): A list of tuples, where each tuple represents a point in latitude and longitude format.
    -   `country_crs` (Dict[str, str]): A dictionary mapping country names to their corresponding EPSG codes.
-   **Returns**:
    
    -   `set`: A set of country names where each point is located.

----------

## `determine_continents`
```python
def determine_continents(points: List[Tuple[float, float]], continent_crs: Dict[str, str]) -> set
```

### Description:

This function identifies the continents where the given points are located by performing a spatial query. It checks each point's location against continent boundaries to determine the continent.

-   **Parameters**:
    
    -   `points` (List[Tuple[float, float]]): A list of geographic points represented as tuples of latitude and longitude.
    -   `continent_crs` (Dict[str, str]): A dictionary mapping continent names to their corresponding EPSG codes.
-   **Returns**:
    
    -   `set`: A set of continent names where each point is located.

----------

## `convert_points_to_optimal_crs`
```python
def convert_points_to_optimal_crs( points: List[Tuple[float, float]],
        country_crs: Dict[str, str] | None = None,
        use_continent_crs: bool = True,
        continent_crs: Dict[str, str] = continent_crs_mapping ) -> tuple[str | None, list[tuple[float, float]]]
   ```

### Description:

This function converts geographic points (latitude, longitude in WGS84) to an optimal coordinate reference system (CRS) based on the location of the points. The function prioritizes using a country-specific CRS, a UTM zone, or a continental CRS when applicable.

-   **Parameters**:
    
    -   `points`: A list of tuples representing points in (latitude, longitude) format.
    -   `country_crs`: An optional dictionary of country names mapped to their EPSG codes. If provided, the function attempts to use the country's CRS.
    -   `use_continent_crs`: A boolean indicating whether to consider continent-specific CRS when points span multiple countries but are within the same continent.
    -   `continent_crs`: A dictionary mapping continent names to EPSG codes for applying a continental CRS.
-   **Returns**:
    
    -   A tuple containing:
        -   The optimal CRS as a string (e.g., EPSG code or "utm"/"wgs84").
        -   A list of transformed points in the new CRS.

----------

## `calculate_distance`
```python
def calculate_distance( point1: Tuple[float, float],
    point2: Tuple[float, float],
    country_crs: Dict[str, str] | None = None,
    use_continent_crs: bool = True,
    continent_crs: Dict[str, str] = continent_crs_mapping ) -> float
   ```

### Description:

This function calculates the distance between two geographic points. It selects an optimal CRS based on the location of the points to determine the distance using either a geodesic or Euclidean approach.

-   **Parameters**:
    
    -   `point1`, `point2`: Geographic coordinates in latitude and longitude (WGS84).
    -   `country_crs`: An optional dictionary to map country names to EPSG codes.
    -   `use_continent_crs`: If True, applies continent-specific CRS if points are on the same continent.
    -   `continent_crs`: A dictionary of continent names and their EPSG codes.
-   **Returns**:
    
    -   `float`: The calculated distance in meters.

----------

## `calculate_area`
```python
def calculate_area( points: List[Tuple[float, float]],
        country_crs: Dict[str, str] | None = None,
        use_continent_crs: bool = True,
        continent_crs: Dict[str, str] = continent_crs_mapping,
        reorder_points: bool = False, ) -> float
   ```

### Description:

This function calculates the area enclosed by a polygon formed by a list of geographic points. It uses the optimal CRS for area calculation, preferring country or continent-specific CRS.

-   **Parameters**:
    
    -   `points`: A list of tuples representing the vertices of the polygon.
    -   `country_crs`: An optional dictionary of country names to EPSG codes.
    -   `use_continent_crs`: A boolean indicating whether to apply continent-specific CRS.
    -   `continent_crs`: A dictionary for mapping continent names to EPSG codes.
    -   `reorder_points`: A boolean to reorder points if the polygon is irregular.
-   **Returns**:
    
    -   `float`: The area of the polygon in square meters.

----------

## `order_points_for_polygon`
```python
def order_points_for_polygon(points: List[Tuple[float, float]]) -> List[Tuple[float, float]]
```

### Description:

This function orders points to form a polygon, either regular or irregular. It reorders the points by calculating their angle from the centroid of the polygon.

-   **Parameters**:
    
    -   `points`: A list of tuples representing points in a planar CRS.
-   **Returns**:
    
    -   A list of reordered points to form a polygon.

----------

## `calculate_bearing`
```python
def calculate_bearing(start_point: Tuple[float, float],
    dest_point: Tuple[float, float],
    country_crs: Dict[str, str] | None = None,
    use_continent_crs: bool = True,
    continent_crs: Dict[str, str] = continent_crs_mapping ) -> float:
   ```

### Description:

This function calculates the bearing (angle in degrees) between two geographic points, from the start point to the destination point. It adjusts the calculation based on the optimal CRS.

-   **Parameters**:
    
    -   `start_point`, `dest_point`: Geographic coordinates (latitude, longitude).
    -   `country_crs`: An optional dictionary for country-specific CRS.
    -   `use_continent_crs`: If True, applies continent-specific CRS.
    -   `continent_crs`: A dictionary for continent EPSG codes.
-   **Returns**:
    
    -   `float`: The bearing angle in degrees between the two points.