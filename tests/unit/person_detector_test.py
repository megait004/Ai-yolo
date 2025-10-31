"""
Unit tests for PersonDetector
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

            self.detector = (
                PersonDetector()
            )  # pyright: ignore[reportUninitializedInstanceVariable]

    def test_init(self):
        """Test PersonDetector initialization"""
        self.assertIsNotNone(self.detector)
        self.assertEqual(self.detector.confidence_threshold, 0.5)
        self.assertEqual(self.detector.iou_threshold, 0.35)
        self.assertEqual(self.detector.person_class_id, 0)

    def test_preprocess_frame(self):
        """Test frame preprocessing"""
        # Create a test frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # Test preprocessing
        processed = self.detector.preprocess_frame(frame)

        # Check if frame is resized correctly
        self.assertEqual(processed.shape, (480, 640, 3))

    def test_get_model_info(self):
        """Test getting model information"""
        info = self.detector.get_model_info()

        self.assertIsInstance(info, dict)
        self.assertIn("model_name", info)
        self.assertIn("confidence_threshold", info)
        self.assertIn("iou_threshold", info)
        self.assertIn("input_size", info)

    @patch("ultralytics.YOLO")
    def test_detect_persons_empty_frame(self, mock_yolo):
        """Test detection with empty frame"""
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

    def test_detect_persons_with_detections(self):
        """Test detection with mock detections"""
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
        self.assertEqual(detections[0]["confidence"], 0.8)


if __name__ == "__main__":
    unittest.main()
