"""
Unit tests for PersonDetector - 20 Test Cases theo đặc tả
"""

import unittest
from unittest.mock import Mock, patch

import numpy as np

from src.core.person_detector import PersonDetector


class TestPersonDetector(unittest.TestCase):
    """Test cases for PersonDetector class"""

    def setUp(self):
        """Set up test fixtures"""
        with patch("ultralytics.YOLO"):
            self.detector = PersonDetector()

    def test_init(self):
        """TC1: Test PersonDetector initialization"""
        self.assertIsNotNone(self.detector)
        self.assertEqual(self.detector.confidence_threshold, 0.5)
        self.assertEqual(self.detector.iou_threshold, 0.35)
        self.assertEqual(self.detector.person_class_id, 0)

    def test_preprocess_frame_standard_size(self):
        """TC2: Test frame preprocessing với kích thước chuẩn"""
        # Create a test frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # Test preprocessing
        processed = self.detector.preprocess_frame(frame)

        # Check if frame is processed correctly
        self.assertEqual(processed.shape, (480, 640, 3))

    def test_preprocess_frame_non_standard_size(self):
        """TC3: Test preprocessing frame với kích thước khác chuẩn"""
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)

        processed = self.detector.preprocess_frame(frame)

        # Frame được xử lý (resize hoặc giữ nguyên)
        self.assertIsNotNone(processed)
        self.assertEqual(len(processed.shape), 3)
        self.assertEqual(processed.shape[2], 3)  # 3 channels

    @patch("ultralytics.YOLO")
    def test_detect_persons_empty_frame(self, mock_yolo):
        """TC4: Test detection with empty frame"""
        # Mock YOLO model
        mock_model = Mock()
        mock_result = Mock()
        mock_result.boxes = None
        mock_model.return_value = [mock_result]
        mock_yolo.return_value = mock_model

        detector = PersonDetector()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        detections = detector.detect_persons(frame)

        self.assertEqual(len(detections), 0)

    def test_detect_persons_with_single_detection(self):
        """TC5: Test detection với 1 người"""
        # Mock YOLO model and results
        mock_model = Mock()
        mock_result = Mock()
        mock_result.boxes.xyxy.cpu.return_value.numpy.return_value = np.array(
            [[100, 100, 200, 300]]
        )
        mock_result.boxes.conf.cpu.return_value.numpy.return_value = np.array([0.8])
        mock_result.boxes.cls.cpu.return_value.numpy.return_value = np.array([0])
        mock_model.return_value = [mock_result]

        detector = PersonDetector()
        # Mock the model directly
        detector.model = mock_model

        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        detections = detector.detect_persons(frame)

        self.assertEqual(len(detections), 1)
        self.assertEqual(detections[0]["class_id"], 0)
        self.assertAlmostEqual(detections[0]["confidence"], 0.8, places=2)

    def test_detect_persons_few_detections(self):
        """TC6: Test detection với 2-5 người"""
        mock_model = Mock()
        mock_result = Mock()

        # Mock 3 detections
        boxes = np.array(
            [[i * 50, i * 50, (i + 1) * 50, (i + 1) * 50] for i in range(3)]
        )
        confidences = np.array([0.8, 0.85, 0.9])
        classes = np.array([0] * 3)

        mock_result.boxes.xyxy.cpu.return_value.numpy.return_value = boxes
        mock_result.boxes.conf.cpu.return_value.numpy.return_value = confidences
        mock_result.boxes.cls.cpu.return_value.numpy.return_value = classes
        mock_model.return_value = [mock_result]

        detector = PersonDetector()
        detector.model = mock_model

        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detections = detector.detect_persons(frame)

        self.assertEqual(len(detections), 3)

    def test_detect_persons_many_detections(self):
        """TC7: Test detection với >5 người (10 người)"""
        mock_model = Mock()
        mock_result = Mock()

        # Mock 10 detections
        boxes = np.array(
            [[i * 50, i * 50, (i + 1) * 50, (i + 1) * 50] for i in range(10)]
        )
        confidences = np.array([0.7 + i * 0.01 for i in range(10)])
        classes = np.array([0] * 10)

        mock_result.boxes.xyxy.cpu.return_value.numpy.return_value = boxes
        mock_result.boxes.conf.cpu.return_value.numpy.return_value = confidences
        mock_result.boxes.cls.cpu.return_value.numpy.return_value = classes
        mock_model.return_value = [mock_result]

        detector = PersonDetector()
        detector.model = mock_model

        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detections = detector.detect_persons(frame)

        self.assertEqual(len(detections), 10)

    def test_detect_persons_filters_low_confidence(self):
        """TC8: Test lọc detection với confidence < threshold

        YOLO model lọc confidence ở inference time, nên detections
        với confidence < threshold không xuất hiện trong results.
        """
        mock_model = Mock()
        mock_result = Mock()

        # Mock YOLO trả về empty results (đã lọc ở inference time)
        mock_result.boxes = None
        mock_model.return_value = [mock_result]

        detector = PersonDetector()
        detector.model = mock_model

        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detections = detector.detect_persons(frame)

        self.assertEqual(len(detections), 0)

    def test_detect_persons_accepts_threshold_confidence(self):
        """TC9: Test accepts detection tại đúng threshold"""
        mock_model = Mock()
        mock_result = Mock()

        mock_result.boxes.xyxy.cpu.return_value.numpy.return_value = np.array(
            [[0, 0, 10, 10]]
        )
        mock_result.boxes.conf.cpu.return_value.numpy.return_value = np.array([0.5])
        mock_result.boxes.cls.cpu.return_value.numpy.return_value = np.array([0])
        mock_model.return_value = [mock_result]

        detector = PersonDetector()
        detector.model = mock_model

        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detections = detector.detect_persons(frame)

        self.assertEqual(len(detections), 1)
        self.assertAlmostEqual(detections[0]["confidence"], 0.5, places=2)

    def test_detect_persons_high_confidence(self):
        """TC10: Test với confidence cao (≥0.9)"""
        mock_model = Mock()
        mock_result = Mock()

        mock_result.boxes.xyxy.cpu.return_value.numpy.return_value = np.array(
            [[0, 0, 10, 10]]
        )
        mock_result.boxes.conf.cpu.return_value.numpy.return_value = np.array([0.95])
        mock_result.boxes.cls.cpu.return_value.numpy.return_value = np.array([0])
        mock_model.return_value = [mock_result]

        detector = PersonDetector()
        detector.model = mock_model

        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detections = detector.detect_persons(frame)

        self.assertEqual(len(detections), 1)
        self.assertAlmostEqual(detections[0]["confidence"], 0.95, places=2)

    def test_detect_persons_filters_non_person_classes(self):
        """TC11: Test lọc các class không phải person"""
        mock_model = Mock()
        mock_result = Mock()

        # 3 detections: person, bicycle, car
        boxes = np.array([[0, 0, 10, 10], [20, 20, 30, 30], [40, 40, 50, 50]])
        confidences = np.array([0.8, 0.9, 0.85])
        classes = np.array([0, 1, 2])  # person, bicycle, car

        mock_result.boxes.xyxy.cpu.return_value.numpy.return_value = boxes
        mock_result.boxes.conf.cpu.return_value.numpy.return_value = confidences
        mock_result.boxes.cls.cpu.return_value.numpy.return_value = classes
        mock_model.return_value = [mock_result]

        detector = PersonDetector()
        detector.model = mock_model

        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detections = detector.detect_persons(frame)

        # Chỉ lấy class_id=0 (person)
        self.assertEqual(len(detections), 1)
        self.assertEqual(detections[0]["class_id"], 0)

    def test_detect_persons_filters_out_of_range_classes(self):
        """TC12: Test lọc class_id ngoài phạm vi COCO"""
        mock_model = Mock()
        mock_result = Mock()

        mock_result.boxes.xyxy.cpu.return_value.numpy.return_value = np.array(
            [[0, 0, 10, 10]]
        )
        mock_result.boxes.conf.cpu.return_value.numpy.return_value = np.array([0.9])
        mock_result.boxes.cls.cpu.return_value.numpy.return_value = np.array([85])
        mock_model.return_value = [mock_result]

        detector = PersonDetector()
        detector.model = mock_model

        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detections = detector.detect_persons(frame)

        # Bị lọc
        self.assertEqual(len(detections), 0)

    def test_detect_persons_mixed_classes(self):
        """TC13: Test lọc với nhiều classes hỗn hợp"""
        mock_model = Mock()
        mock_result = Mock()

        # 5 detections: person, bicycle, person, car, person
        boxes = np.array(
            [[i * 20, i * 20, (i + 1) * 20, (i + 1) * 20] for i in range(5)]
        )
        confidences = np.array([0.8, 0.9, 0.85, 0.88, 0.92])
        classes = np.array([0, 1, 0, 2, 0])

        mock_result.boxes.xyxy.cpu.return_value.numpy.return_value = boxes
        mock_result.boxes.conf.cpu.return_value.numpy.return_value = confidences
        mock_result.boxes.cls.cpu.return_value.numpy.return_value = classes
        mock_model.return_value = [mock_result]

        detector = PersonDetector()
        detector.model = mock_model

        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detections = detector.detect_persons(frame)

        # Chỉ có 3 person
        self.assertEqual(len(detections), 3)
        for det in detections:
            self.assertEqual(det["class_id"], 0)

    def test_get_model_info(self):
        """TC14: Test getting model information"""
        info = self.detector.get_model_info()

        self.assertIsInstance(info, dict)
        self.assertIn("model_name", info)
        self.assertIn("confidence_threshold", info)
        self.assertIn("iou_threshold", info)
        self.assertIn("input_size", info)

    def test_detect_persons_converts_bbox_to_int(self):
        """TC15: Test bbox được convert sang int"""
        mock_model = Mock()
        mock_result = Mock()

        # Bbox với số thập phân
        mock_result.boxes.xyxy.cpu.return_value.numpy.return_value = np.array(
            [[100.5, 200.3, 300.7, 400.9]]
        )
        mock_result.boxes.conf.cpu.return_value.numpy.return_value = np.array([0.95])
        mock_result.boxes.cls.cpu.return_value.numpy.return_value = np.array([0])
        mock_model.return_value = [mock_result]

        detector = PersonDetector()
        detector.model = mock_model

        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detections = detector.detect_persons(frame)

        # Bbox được convert sang int
        bbox = detections[0]["bbox"]
        self.assertEqual(bbox, [100, 200, 300, 400])
        self.assertIsInstance(bbox[0], (int, np.integer))

    def test_detect_persons_handles_empty_frame_gracefully(self):
        """TC16: Test xử lý frame rỗng không crash"""
        mock_model = Mock()
        mock_model.return_value = []

        detector = PersonDetector()
        detector.model = mock_model

        # Frame rỗng
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # Không crash
        detections = detector.detect_persons(frame)
        self.assertIsInstance(detections, list)

    def test_get_model_info_keys(self):
        """TC17: Test model info dict có đủ keys"""
        info = self.detector.get_model_info()

        # Kiểm tra tất cả keys cần thiết
        required_keys = [
            "model_name",
            "confidence_threshold",
            "iou_threshold",
            "input_size",
        ]
        for key in required_keys:
            self.assertIn(key, info)

    def test_detection_contains_required_keys(self):
        """TC18: Test detection dict chứa đầy đủ keys và kiểu dữ liệu đúng"""
        mock_model = Mock()
        mock_result = Mock()

        mock_result.boxes.xyxy.cpu.return_value.numpy.return_value = np.array(
            [[0, 0, 10, 10]]
        )
        mock_result.boxes.conf.cpu.return_value.numpy.return_value = np.array([0.85])
        mock_result.boxes.cls.cpu.return_value.numpy.return_value = np.array([0])
        mock_model.return_value = [mock_result]

        detector = PersonDetector()
        detector.model = mock_model

        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detections = detector.detect_persons(frame)

        detection = detections[0]

        # Kiểm tra các keys bắt buộc
        self.assertIn("bbox", detection)
        self.assertIn("confidence", detection)
        self.assertIn("class_id", detection)

        # Kiểm tra kiểu dữ liệu
        self.assertIsInstance(detection["bbox"], list)
        self.assertIsInstance(detection["confidence"], (float, np.floating))
        self.assertEqual(len(detection["bbox"]), 4)

        # Confidence trong [0, 1]
        self.assertGreaterEqual(detection["confidence"], 0.0)
        self.assertLessEqual(detection["confidence"], 1.0)

    def test_detect_persons_multiple_calls_independent(self):
        """TC19: Test nhiều lần gọi detect_persons độc lập nhau"""
        mock_model = Mock()

        # Kết quả khác nhau cho mỗi lần gọi
        mock_result1 = Mock()
        mock_result1.boxes.xyxy.cpu.return_value.numpy.return_value = np.array(
            [[0, 0, 10, 10]]
        )
        mock_result1.boxes.conf.cpu.return_value.numpy.return_value = np.array([0.8])
        mock_result1.boxes.cls.cpu.return_value.numpy.return_value = np.array([0])

        mock_result2 = Mock()
        mock_result2.boxes.xyxy.cpu.return_value.numpy.return_value = np.array(
            [[0, 0, 10, 10], [20, 20, 30, 30]]
        )
        mock_result2.boxes.conf.cpu.return_value.numpy.return_value = np.array(
            [0.8, 0.9]
        )
        mock_result2.boxes.cls.cpu.return_value.numpy.return_value = np.array([0, 0])

        mock_model.side_effect = [[mock_result1], [mock_result2]]

        detector = PersonDetector()
        detector.model = mock_model

        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # Lần 1: 1 detection
        detections1 = detector.detect_persons(frame)
        self.assertEqual(len(detections1), 1)

        # Lần 2: 2 detections
        detections2 = detector.detect_persons(frame)
        self.assertEqual(len(detections2), 2)

        # Kết quả không ảnh hưởng lẫn nhau
        self.assertNotEqual(len(detections1), len(detections2))

    def test_detect_persons_perfect_confidence(self):
        """TC20: Test với confidence = 1.0 (perfect detection)"""
        mock_model = Mock()
        mock_result = Mock()

        mock_result.boxes.xyxy.cpu.return_value.numpy.return_value = np.array(
            [[0, 0, 10, 10]]
        )
        mock_result.boxes.conf.cpu.return_value.numpy.return_value = np.array([1.0])
        mock_result.boxes.cls.cpu.return_value.numpy.return_value = np.array([0])
        mock_model.return_value = [mock_result]

        detector = PersonDetector()
        detector.model = mock_model

        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detections = detector.detect_persons(frame)

        self.assertEqual(len(detections), 1)
        self.assertAlmostEqual(detections[0]["confidence"], 1.0, places=2)


if __name__ == "__main__":
    unittest.main()
