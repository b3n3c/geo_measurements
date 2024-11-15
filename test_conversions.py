import unittest
from geo_measurements import (
    determine_countries, determine_continents, convert_points_to_optimal_crs,
)

class TestConversions(unittest.TestCase):

    def setUp(self):
        self.national_crs_mapping = {
            "Hungary": "EPSG:23700",
            "Serbia": "EPSG:8682",
        }

        self.continental_crs_mapping = {
            'Europe': 'EPSG:3035'
        }
        # Sample points for tests
        self.points_in_hungary = [(47.1625, 19.5033), (46.241443, 20.149143)]
        self.points_in_europe_same_utm_zones = [(48.8575, 2.3514), (50.8477, 4.3572)]   # Paris, Brussels
        self.points_in_europe_different_utm_zones = [(47.497913, 19.040236), (48.8575, 2.3514)]  # Budapest, Paris
        self.points_outside_defined = [(40.7128, 74.0060), (38.9072, 77.0369)] # New York, Washington D.C.

    def test_determine_countries_within_mapping(self):
        countries = determine_countries(self.points_in_hungary, self.national_crs_mapping)
        self.assertIn("Hungary", countries)

    def test_determine_countries_outside_mapping(self):
        countries = determine_countries(self.points_outside_defined, self.national_crs_mapping)
        self.assertEqual(countries, set())

    def test_determine_continents_within_mapping(self):
        continents = determine_continents(self.points_in_europe_different_utm_zones, self.continental_crs_mapping)
        self.assertIn("Europe", continents)

    def test_determine_continents_outside_mapping(self):
        continents = determine_continents(self.points_outside_defined, self.continental_crs_mapping)
        self.assertEqual(continents, set())

    def test_convert_points_to_optimal_crs_with_country_crs(self):
        crs, transformed_points = convert_points_to_optimal_crs(self.points_in_hungary, self.national_crs_mapping)

        self.assertEqual(crs, self.national_crs_mapping["Hungary"])
        self.assertIsInstance(transformed_points, list)
        self.assertEqual(len(transformed_points), len(self.points_in_hungary))

    def test_convert_points_to_optimal_crs_with_continent_crs_utm(self):
        crs, transformed_points = convert_points_to_optimal_crs(self.points_in_europe_same_utm_zones, continent_crs=self.continental_crs_mapping)

        self.assertEqual(crs, "utm")
        self.assertIsInstance(transformed_points, list)
        self.assertEqual(len(transformed_points), len(self.points_in_europe_same_utm_zones))

    def test_convert_points_to_optimal_crs_with_continent_crs(self):
        crs, transformed_points = convert_points_to_optimal_crs(self.points_in_europe_different_utm_zones, continent_crs=self.continental_crs_mapping)

        self.assertEqual(crs, self.continental_crs_mapping["Europe"])
        self.assertIsInstance(transformed_points, list)
        self.assertEqual(len(transformed_points), len(self.points_in_europe_different_utm_zones))

    def test_convert_points_to_optimal_crs_fallback_to_wgs84(self):
        crs, transformed_points = convert_points_to_optimal_crs(self.points_outside_defined)
        self.assertEqual(crs, "wgs84")
        self.assertEqual(transformed_points, self.points_outside_defined)


if __name__ == "__main__":
    unittest.main()