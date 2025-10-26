"""
Unit tests for PersonCounter
"""

import time
import unittest

from src.core.person_counter import PersonCounter


class TestPersonCounter(unittest.TestCase):
    """Test cases for PersonCounter class"""

    def setUp(self):
        """Set up test fixtures"""

        self.counter = (
            PersonCounter()
        )  # pyright: ignore[reportUninitializedInstanceVariable]

    def test_init(self):
        """Test PersonCounter initialization"""
        self.assertEqual(self.counter.current_count, 0)
        self.assertEqual(self.counter.max_count, 0)
        self.assertEqual(self.counter.total_detections, 0)
        self.assertEqual(self.counter.frame_count, 0)

    def test_update_count_empty(self):
        """Test updating count with empty detections"""
        count = self.counter.update_count([])

        self.assertEqual(count, 0)
        self.assertEqual(self.counter.current_count, 0)
        self.assertEqual(self.counter.frame_count, 1)

    def test_update_count_with_detections(self):
        """Test updating count with detections"""
        detections = [
            {"bbox": [100, 100, 200, 300], "confidence": 0.8, "class_id": 0},
            {"bbox": [300, 150, 400, 350], "confidence": 0.9, "class_id": 0},
        ]

        count = self.counter.update_count(detections)

        self.assertEqual(count, 2)
        self.assertEqual(self.counter.current_count, 2)
        self.assertEqual(self.counter.max_count, 2)
        self.assertEqual(self.counter.total_detections, 2)
        self.assertEqual(self.counter.frame_count, 1)

    def test_get_current_count(self):
        """Test getting current count"""
        self.counter.current_count = 5
        self.assertEqual(self.counter.get_current_count(), 5)

    def test_get_max_count(self):
        """Test getting max count"""
        self.counter.max_count = 10
        self.assertEqual(self.counter.get_max_count(), 10)

    def test_get_average_count(self):
        """Test getting average count"""
        # Add some test data
        self.counter.count_history.extend([1, 2, 3, 4, 5])
        # Update stats to recalculate average
        self.counter._update_stats()
        avg = self.counter.get_average_count()

        self.assertEqual(avg, 3.0)

    def test_get_running_time(self):
        """Test getting running time"""
        time.sleep(0.1)  # Small delay
        running_time = self.counter.get_running_time()

        self.assertGreater(running_time, 0)

    def test_get_fps(self):
        """Test getting FPS"""
        import time

        # Simulate some frames
        for _ in range(10):
            self.counter.update_count([])

        # Wait a small amount of time to ensure FPS calculation works
        time.sleep(0.01)

        fps = self.counter.get_fps()
        self.assertGreater(fps, 0)

    def test_get_detection_rate(self):
        """Test getting detection rate"""
        # Add some test data
        self.counter.stats["total_frames"] = 10
        self.counter.stats["frames_with_persons"] = 7

        rate = self.counter.get_detection_rate()
        self.assertEqual(rate, 0.7)

    def test_get_all_stats(self):
        """Test getting all statistics"""
        stats = self.counter.get_all_stats()

        self.assertIsInstance(stats, dict)
        self.assertIn("current_count", stats)
        self.assertIn("max_count", stats)
        self.assertIn("average_count", stats)
        self.assertIn("total_detections", stats)
        self.assertIn("total_frames", stats)
        self.assertIn("fps", stats)
        self.assertIn("running_time", stats)

    def test_reset_stats(self):
        """Test resetting statistics"""
        # Add some data
        self.counter.update_count(
            [{"bbox": [0, 0, 100, 100], "confidence": 0.8, "class_id": 0}]
        )

        # Reset
        self.counter.reset_stats()

        # Check if reset
        self.assertEqual(self.counter.current_count, 0)
        self.assertEqual(self.counter.max_count, 0)
        self.assertEqual(self.counter.total_detections, 0)
        self.assertEqual(self.counter.frame_count, 0)


if __name__ == "__main__":
    unittest.main()
