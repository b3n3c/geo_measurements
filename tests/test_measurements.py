import unittest
from geo_measurements import (
    calculate_area, calculate_distance, calculate_bearing, section, order_points_for_polygon,
    convert_points_to_optimal_crs
)


class TestMeasurements(unittest.TestCase):

    def setUp(self):
        self.national_crs_mapping = {
            "Hungary": "EPSG:23700",
            "Serbia": "EPSG:8682",
        }

        # Sample points for tests
        self.point_1 = (45.8349661, 19.99823932)
        self.point_2 = (45.83492691, 19.99875827)
        self.point_3 = (45.83112519, 19.99817165)
        self.point_4 = (45.83116438, 19.99765274)

    def test_calculate_area(self):
        area = calculate_area(
            [self.point_1, self.point_2, self.point_3, self.point_4],
            country_crs=self.national_crs_mapping
        )
        self.assertIsInstance(area, float)
        self.assertAlmostEqual(area, 17224.149658203125, delta=10)

        area_2 = calculate_area(
            [self.point_1, self.point_2, self.point_3, self.point_4]
        )
        self.assertIsInstance(area_2, float)
        self.assertAlmostEqual(area_2, 17224.149658203125, delta=10)

        area_3 = calculate_area(
            [self.point_1, self.point_3, self.point_2, self.point_4],
            country_crs=self.national_crs_mapping, reorder_points=True
        )
        self.assertIsInstance(area_3, float)
        self.assertAlmostEqual(area_3, 17224.149658203125, delta=10)

    def test_calculate_distance(self):
        distance = calculate_distance(
            self.point_1,
            self.point_2,
            country_crs=self.national_crs_mapping
        )
        self.assertIsInstance(distance, float)
        self.assertAlmostEqual(distance, 40.54034921687736, delta=1)

        distance_2 = calculate_distance(
            self.point_1,
            self.point_2,
        )
        self.assertIsInstance(distance_2, float)
        self.assertAlmostEqual(distance_2, 40.54034921687736, delta=2)

    def test_calculate_bearing(self):
        bearing = calculate_bearing(
            self.point_1,
            self.point_2
        )
        self.assertIsInstance(bearing, float)
        self.assertGreaterEqual(bearing, 0)
        self.assertLessEqual(bearing, 360)

    def test_section(self):
        midpoint_1 = section(
            self.point_1,
            self.point_2,
            m=1,
            n=1,
            country_crs=self.national_crs_mapping
        )
        self.assertIsInstance(midpoint_1, tuple)
        self.assertEqual(len(midpoint_1), 2)
        midpoint_1_to_pont_1 = calculate_distance(midpoint_1, self.point_1, country_crs=self.national_crs_mapping)
        midpoint_1_to_pont_2 = calculate_distance(midpoint_1, self.point_2, country_crs=self.national_crs_mapping)
        self.assertAlmostEqual(midpoint_1_to_pont_1, midpoint_1_to_pont_2, delta=1)

        midpoint_2 = section(
            self.point_1,
            self.point_2,
            m=1,
            n=1
        )
        self.assertIsInstance(midpoint_2, tuple)
        self.assertEqual(len(midpoint_2), 2)
        midpoint_2_to_pont_1 = calculate_distance(midpoint_2, self.point_1, country_crs=self.national_crs_mapping)
        midpoint_2_to_pont_2 = calculate_distance(midpoint_2, self.point_2, country_crs=self.national_crs_mapping)
        self.assertAlmostEqual(midpoint_2_to_pont_1, midpoint_2_to_pont_2, delta=1)

    def test_order_points_for_polygon(self):
        crs, utm_points = convert_points_to_optimal_crs([self.point_1, self.point_3, self.point_2, self.point_4])
        ordered_points = order_points_for_polygon(utm_points)
        self.assertIsInstance(ordered_points, list)
        self.assertEqual(len(ordered_points), len(utm_points))
        self.assertEqual(ordered_points, [utm_points[0], utm_points[2], utm_points[1], utm_points[3]])


if __name__ == "__main__":
    unittest.main()
