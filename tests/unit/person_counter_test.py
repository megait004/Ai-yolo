"""
Unit tests for PersonCounter - 20 Test Cases theo đặc tả
"""

import time
import unittest

from src.core.person_counter import PersonCounter


class TestPersonCounter(unittest.TestCase):
    """Test cases for PersonCounter class"""

    def setUp(self):
        """Set up test fixtures"""
        self.counter = PersonCounter()

    def test_init(self):
        """TC1: Test PersonCounter initialization"""
        self.assertEqual(self.counter.current_count, 0)
        self.assertEqual(self.counter.max_count, 0)
        self.assertEqual(self.counter.total_detections, 0)
        self.assertEqual(self.counter.frame_count, 0)

    def test_update_count_empty(self):
        """TC2: Test updating count with empty detections"""
        count = self.counter.update_count([])

        self.assertEqual(count, 0)
        self.assertEqual(self.counter.current_count, 0)
        self.assertEqual(self.counter.frame_count, 1)

    def test_update_count_with_single_detection(self):
        """TC3: Test updating count with 1 detection"""
        detections = [
            {"bbox": [100, 100, 200, 300], "confidence": 0.8, "class_id": 0},
        ]

        count = self.counter.update_count(detections)

        self.assertEqual(count, 1)
        self.assertEqual(self.counter.current_count, 1)
        self.assertEqual(self.counter.max_count, 1)
        self.assertEqual(self.counter.total_detections, 1)

    def test_update_count_with_multiple_detections(self):
        """TC4: Test updating count with 2-10 detections"""
        detections = [
            {"bbox": [100, 100, 200, 300], "confidence": 0.8, "class_id": 0},
            {"bbox": [300, 150, 400, 350], "confidence": 0.9, "class_id": 0},
        ]

        count = self.counter.update_count(detections)

        self.assertEqual(count, 2)
        self.assertEqual(self.counter.current_count, 2)
        self.assertEqual(self.counter.max_count, 2)

    def test_update_count_many_detections(self):
        """TC5: Test với >10 detections (15 người)"""
        detections = [
            {"bbox": [i * 10, i * 10, (i + 1) * 10, (i + 1) * 10], "confidence": 0.9, "class_id": 0}
            for i in range(15)
        ]

        count = self.counter.update_count(detections)

        self.assertEqual(count, 15)
        self.assertEqual(self.counter.current_count, 15)
        self.assertEqual(self.counter.max_count, 15)
        self.assertEqual(self.counter.total_detections, 15)

    def test_max_count_tracking_over_multiple_updates(self):
        """TC6: Test max_count được giữ lại qua nhiều lần update"""
        # Lần 1: 2 người
        detections1 = [
            {"bbox": [0, 0, 10, 10], "confidence": 0.8, "class_id": 0},
            {"bbox": [20, 20, 30, 30], "confidence": 0.9, "class_id": 0},
        ]
        self.counter.update_count(detections1)
        self.assertEqual(self.counter.max_count, 2)

        # Lần 2: 1 người (giảm xuống)
        detections2 = [{"bbox": [0, 0, 10, 10], "confidence": 0.8, "class_id": 0}]
        self.counter.update_count(detections2)

        # max_count vẫn giữ nguyên = 2
        self.assertEqual(self.counter.current_count, 1)
        self.assertEqual(self.counter.max_count, 2)

    def test_count_history_and_average(self):
        """TC7: Test lịch sử count và tính average"""
        counts = [1, 2, 3, 4, 5]
        for value in counts:
            detections = [
                {"bbox": [i, i, i + 10, i + 10], "confidence": 0.9, "class_id": 0}
                for i in range(value)
            ]
            self.counter.update_count(detections)

        # Kiểm tra lịch sử
        history, timestamps = self.counter.get_count_history()
        self.assertEqual(history, counts)
        self.assertEqual(len(timestamps), 5)

        # Kiểm tra average
        self.assertEqual(self.counter.get_average_count(), 3.0)

    def test_history_max_length_limit(self):
        """TC8: Test history giới hạn tối đa 100 phần tử"""
        # Thêm 105 frames
        for i in range(105):
            detections = [
                {"bbox": [0, 0, 10, 10], "confidence": 0.9, "class_id": 0}
            ] * (i % 5)
            self.counter.update_count(detections)

        history, _ = self.counter.get_count_history()

        # Chỉ giữ 100 frame gần nhất
        self.assertEqual(len(history), 100)

    def test_total_detections_accumulates(self):
        """TC9: Test total_detections cộng dồn qua nhiều lần update"""
        # Lần 1: 1 detection
        self.counter.update_count([{"bbox": [0, 0, 10, 10], "confidence": 0.9, "class_id": 0}])

        # Lần 2: 2 detections
        self.counter.update_count([
            {"bbox": [0, 0, 10, 10], "confidence": 0.9, "class_id": 0},
            {"bbox": [20, 20, 30, 30], "confidence": 0.9, "class_id": 0},
        ])

        # Lần 3: 3 detections
        self.counter.update_count([
            {"bbox": [0, 0, 10, 10], "confidence": 0.9, "class_id": 0},
            {"bbox": [20, 20, 30, 30], "confidence": 0.9, "class_id": 0},
            {"bbox": [40, 40, 50, 50], "confidence": 0.9, "class_id": 0},
        ])

        # Tổng = 1 + 2 + 3 = 6 detections
        self.assertEqual(self.counter.total_detections, 6)

    def test_detection_rate_zero_all_empty_frames(self):
        """TC10: Test detection_rate = 0 khi tất cả frames rỗng"""
        for _ in range(10):
            self.counter.update_count([])

        rate = self.counter.get_detection_rate()
        self.assertEqual(rate, 0.0)

    def test_detection_rate_one_all_detected_frames(self):
        """TC11: Test detection_rate = 1.0 khi tất cả frames có người"""
        for _ in range(10):
            self.counter.update_count([{"bbox": [0, 0, 10, 10], "confidence": 0.9, "class_id": 0}])

        rate = self.counter.get_detection_rate()
        self.assertEqual(rate, 1.0)

    def test_detection_rate_partial_detection(self):
        """TC12: Test detection_rate với 70% frames có người"""
        for i in range(10):
            if i < 7:
                # 7 frames có người
                self.counter.update_count([{"bbox": [0, 0, 10, 10], "confidence": 0.9, "class_id": 0}])
            else:
                # 3 frames rỗng
                self.counter.update_count([])

        rate = self.counter.get_detection_rate()
        self.assertAlmostEqual(rate, 0.7, places=2)

    def test_fps_zero_immediately_after_init(self):
        """TC13: Test FPS = 0 ngay sau khởi tạo"""
        counter = PersonCounter()
        fps = counter.get_fps()
        self.assertEqual(fps, 0.0)

    def test_fps_calculation_after_updates(self):
        """TC14: Test FPS được tính sau nhiều updates"""
        # Thêm 10 frames
        for _ in range(10):
            self.counter.update_count([])

        # Chờ một chút để có running time
        time.sleep(0.01)

        fps = self.counter.get_fps()

        # FPS phải > 0 sau khi có frames và running time
        self.assertGreater(fps, 0)

    def test_get_all_stats(self):
        """TC15: Test getting all statistics"""
        stats = self.counter.get_all_stats()

        self.assertIsInstance(stats, dict)
        self.assertIn("current_count", stats)
        self.assertIn("max_count", stats)
        self.assertIn("average_count", stats)
        self.assertIn("total_detections", stats)
        self.assertIn("total_frames", stats)
        self.assertIn("fps", stats)
        self.assertIn("running_time", stats)

    def test_get_count_history_returns_tuple(self):
        """TC16: Test get_count_history trả về tuple (counts, timestamps)"""
        # Thêm vài detections
        for i in range(3):
            self.counter.update_count([{"bbox": [0, 0, 10, 10], "confidence": 0.9, "class_id": 0}] * i)

        history, timestamps = self.counter.get_count_history()

        self.assertIsInstance(history, list)
        self.assertIsInstance(timestamps, list)
        self.assertEqual(len(history), 3)
        self.assertEqual(len(timestamps), 3)

    def test_reset_stats(self):
        """TC17: Test resetting statistics"""
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

    def test_getter_methods(self):
        """TC18: Test các getter methods"""
        self.counter.current_count = 5
        self.counter.max_count = 10

        # Add history for average
        self.counter.count_history.extend([1, 2, 3, 4, 5])
        self.counter._update_stats()

        self.assertEqual(self.counter.get_current_count(), 5)
        self.assertEqual(self.counter.get_max_count(), 10)
        self.assertEqual(self.counter.get_average_count(), 3.0)

    def test_get_running_time(self):
        """TC19: Test getting running time"""
        time.sleep(0.1)  # Small delay
        running_time = self.counter.get_running_time()

        self.assertGreater(running_time, 0)

    def test_frames_with_persons_counts_only_detected_frames(self):
        """TC20: Test frames_with_persons chỉ đếm frames có người"""
        # Frame 1: rỗng
        self.counter.update_count([])

        # Frame 2: có 1 người
        self.counter.update_count([{"bbox": [0, 0, 10, 10], "confidence": 0.9, "class_id": 0}])

        # Frame 3: rỗng
        self.counter.update_count([])

        # Frame 4: có 1 người
        self.counter.update_count([{"bbox": [0, 0, 10, 10], "confidence": 0.9, "class_id": 0}])

        # Frame 5: có 1 người
        self.counter.update_count([{"bbox": [0, 0, 10, 10], "confidence": 0.9, "class_id": 0}])

        # Chỉ có 3 frames có người
        stats = self.counter.get_all_stats()
        self.assertEqual(stats["frames_with_persons"], 3)


if __name__ == "__main__":
    unittest.main()
