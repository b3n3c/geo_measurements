import unittest

from geo_measurements import (
    determine_countries, determine_continents, convert_points_to_optimal_crs, continent_crs_mapping,
)

class TestConversions(unittest.TestCase):

    def setUp(self):
        self.national_crs_mapping = {
            "Hungary": "EPSG:23700",
            "Serbia": "EPSG:8682",
        }

        self.continent_crs_mapping = {
            'Europe': 'EPSG:3035'
        }
        # Sample points for tests
        self.points_in_hungary = [(47.1625, 19.5033), (46.241443, 20.149143)]
        self.points_in_europe_same_utm_zones = [(48.8575, 2.3514), (50.8477, 4.3572)]  # Paris, Brussels
        self.points_in_europe_different_utm_zones = [(47.497913, 19.040236), (48.8575, 2.3514)]  # Budapest, Paris
        self.points_outside_defined = [(40.7128, 74.0060), (38.9072, 77.0369)]  # New York, Washington D.C.

    def test_determine_countries_within_mapping(self):
        countries = determine_countries(self.points_in_hungary, self.national_crs_mapping)
        self.assertIn("Hungary", countries)

    def test_determine_countries_outside_mapping(self):
        countries = determine_countries(self.points_outside_defined, self.national_crs_mapping)
        self.assertEqual(countries, set())

    def test_determine_continents_within_mapping(self):
        continents = determine_continents(self.points_in_europe_different_utm_zones, self.continent_crs_mapping)
        self.assertIn("Europe", continents)

    def test_determine_continents_outside_mapping(self):
        continents = determine_continents(self.points_outside_defined, self.continent_crs_mapping)
        self.assertEqual(continents, set())

    def test_convert_points_to_optimal_crs_with_country_crs(self):
        crs, transformed_points = convert_points_to_optimal_crs(self.points_in_hungary, self.national_crs_mapping)

        self.assertEqual(crs, self.national_crs_mapping["Hungary"])
        self.assertIsInstance(transformed_points, list)
        self.assertEqual(len(transformed_points), len(self.points_in_hungary))

    def test_convert_points_to_optimal_crs_with_continent_crs_utm(self):
        crs, transformed_points = convert_points_to_optimal_crs(self.points_in_europe_same_utm_zones,
                                                                continent_crs=self.continent_crs_mapping)

        self.assertEqual(crs, "utm")
        self.assertIsInstance(transformed_points, list)
        self.assertEqual(len(transformed_points), len(self.points_in_europe_same_utm_zones))

    def test_convert_points_to_optimal_crs_with_continent_crs(self):
        crs, transformed_points = convert_points_to_optimal_crs(self.points_in_europe_different_utm_zones,
                                                                continent_crs=self.continent_crs_mapping)

        self.assertEqual(crs, self.continent_crs_mapping["Europe"])
        self.assertIsInstance(transformed_points, list)
        self.assertEqual(len(transformed_points), len(self.points_in_europe_different_utm_zones))

    def test_convert_points_to_optimal_crs_fallback_to_wgs84(self):
        points_in_different_continents = [(1.2921, 36.8219), (35.6895, 139.6917)]
        crs, transformed_points = convert_points_to_optimal_crs(points_in_different_continents)
        self.assertEqual(crs, "wgs84")
        self.assertEqual(transformed_points, points_in_different_continents)

    def test_convert_points_to_optimal_crs_all_default_epsg_codes(self):
        # Points for Africa (Different UTM Zones)
        points_in_africa = [(1.2921, 36.8219),
                            (34.0522, 18.4232)]  # Nairobi, Kenya (Zone 37S), Cape Town, South Africa (Zone 34S)
        crs, transformed_points = convert_points_to_optimal_crs(
            points_in_africa, continent_crs=continent_crs_mapping
        )
        self.assertEqual(crs, continent_crs_mapping["Africa"])
        self.assertEqual(len(transformed_points), len(points_in_africa))
        self.assertIsInstance(transformed_points, list)

        # Points for Antarctica (Different UTM Zones)
        points_in_antarctica = [(-75.250973, -0.071389),
                                (-60.7037, -45.5167)]  # Near the South Pole (Zone 7S), Antarctic Peninsula (Zone 21S)
        crs, transformed_points = convert_points_to_optimal_crs(
            points_in_antarctica, continent_crs=continent_crs_mapping
        )
        self.assertEqual(crs, continent_crs_mapping["Antarctica"])
        self.assertEqual(len(transformed_points), len(points_in_antarctica))
        self.assertIsInstance(transformed_points, list)

        # Points for Asia (Different UTM Zones)
        points_in_asia = [(35.6895, 139.6917),
                          (37.7749, 122.4194)]  # Tokyo, Japan (Zone 54N), San Francisco, USA (Zone 10N)
        crs, transformed_points = convert_points_to_optimal_crs(
            points_in_asia, continent_crs=continent_crs_mapping
        )
        self.assertEqual(crs, continent_crs_mapping["Asia"])
        self.assertEqual(len(transformed_points), len(points_in_asia))
        self.assertIsInstance(transformed_points, list)

        # Points for Australia (Different UTM Zones)
        points_in_australia = [(-33.8688, 151.2093),
                               (-17.7596, 122.1015)]  # Sydney, Australia (Zone 56S), Broome, Australia (Zone 50S)
        crs, transformed_points = convert_points_to_optimal_crs(
            points_in_australia, continent_crs=continent_crs_mapping
        )
        self.assertEqual(crs, continent_crs_mapping["Australia"])
        self.assertEqual(len(transformed_points), len(points_in_australia))
        self.assertIsInstance(transformed_points, list)

        # Points for Europe (Different UTM Zones)
        points_in_europe = [(48.8566, 2.3522),
                            (55.6761, 12.5683)]  # Paris, France (Zone 31T), Copenhagen, Denmark (Zone 32V)
        crs, transformed_points = convert_points_to_optimal_crs(
            points_in_europe, continent_crs=continent_crs_mapping
        )
        self.assertEqual(crs, continent_crs_mapping["Europe"])
        self.assertEqual(len(transformed_points), len(points_in_europe))
        self.assertIsInstance(transformed_points, list)

        # Points for North America (Different UTM Zones)
        points_in_north_america = [(40.7128, -74.0060),
                                   (34.0522, -118.2437)]  # New York, USA (Zone 18N), Los Angeles, USA (Zone 11N)
        crs, transformed_points = convert_points_to_optimal_crs(
            points_in_north_america, continent_crs=continent_crs_mapping
        )
        self.assertEqual(crs, continent_crs_mapping["North America"])
        self.assertEqual(len(transformed_points), len(points_in_north_america))
        self.assertIsInstance(transformed_points, list)

        # Points for South America (Different UTM Zones)
        points_in_south_america = [(-22.9068, -43.1729), (
            -34.6037, -58.3816)]  # Rio de Janeiro, Brazil (Zone 23S), Buenos Aires, Argentina (Zone 21S)
        crs, transformed_points = convert_points_to_optimal_crs(
            points_in_south_america, continent_crs=continent_crs_mapping
        )
        self.assertEqual(crs, continent_crs_mapping["South America"])
        self.assertEqual(len(transformed_points), len(points_in_south_america))
        self.assertIsInstance(transformed_points, list)

        # Points for Oceania (Different UTM Zones)
        points_in_oceania = [(-36.8485, 174.7633),
                             (-12.4634, 130.8456)]  # Auckland, New Zealand (Zone 60S), Darwin, Australia (Zone 52S)
        crs, transformed_points = convert_points_to_optimal_crs(
            points_in_oceania, continent_crs=continent_crs_mapping
        )
        self.assertEqual(crs, continent_crs_mapping["Oceania"])
        self.assertEqual(len(transformed_points), len(points_in_oceania))
        self.assertIsInstance(transformed_points, list)


if __name__ == "__main__":
    unittest.main()
