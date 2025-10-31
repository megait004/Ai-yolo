"""
Integration tests for the AI-YOLO application
"""

import os
import sys

import numpy as np
import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from src.core.alert_system import AlertSystem
from src.core.person_counter import PersonCounter
from src.core.person_detector import PersonDetector
from src.core.visualizer import Visualizer


class TestIntegration:
    """Integration tests for core components"""

    def test_person_detector_integration(self):
        """Test PersonDetector integration"""
        detector = PersonDetector()
        assert detector is not None
        assert detector.confidence_threshold == 0.5
        assert detector.iou_threshold == 0.35
        assert detector.person_class_id == 0

    def test_person_counter_integration(self):
        """Test PersonCounter integration"""
        counter = PersonCounter()
        assert counter is not None
        assert counter.current_count == 0

    def test_visualizer_integration(self):
        """Test Visualizer integration"""
        visualizer = Visualizer()
        assert visualizer is not None

    def test_alert_system_integration(self):
        """Test AlertSystem integration"""
        alert_system = AlertSystem(max_count=5)
        assert alert_system is not None
        assert alert_system.max_count == 5

    def test_components_work_together(self):
        """Test that components can work together"""
        detector = PersonDetector()
        counter = PersonCounter()
        visualizer = Visualizer()
        alert_system = AlertSystem(max_count=10)

        # Test that all components can be instantiated together
        assert detector is not None
        assert counter is not None
        assert visualizer is not None
        assert alert_system is not None

        # Test basic functionality
        info = detector.get_model_info()
        assert "model_name" in info

        # Test counter stats
        assert counter.current_count == 0
        assert counter.max_count == 0

    def test_detector_and_counter_workflow(self):
        """Test detector and counter workflow"""
        counter = PersonCounter()

        # Simulate detection results
        detections = [
            {"bbox": [100, 100, 200, 200], "confidence": 0.9, "class_id": 0},
            {"bbox": [300, 300, 400, 400], "confidence": 0.85, "class_id": 0},
        ]

        # Update counter with detections
        count = counter.update_count(detections)

        assert counter.current_count == 2
        assert count == 2

    def test_visualizer_with_frame(self):
        """Test visualizer with a frame"""
        visualizer = Visualizer()

        # Create a dummy frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # Create dummy detections
        detections = [{"bbox": [100, 100, 200, 200], "confidence": 0.9, "class_id": 0}]

        # Draw detections on frame
        result_frame = visualizer.draw_detections(frame, detections, person_count=1)

        assert result_frame is not None
        # Frame shape may change due to info panel added by visualizer
        assert result_frame.shape[1] == frame.shape[1]  # width should be same
        assert result_frame.shape[2] == frame.shape[2]  # channels should be same

    def test_alert_system_workflow(self):
        """Test alert system workflow"""
        alert_system = AlertSystem(max_count=3)

        # Test below threshold
        result = alert_system.check_alert(2)
        assert result is None

        # Test above threshold
        result = alert_system.check_alert(5)
        alerts = alert_system.get_alert_history()
        assert len(alerts) > 0

    def test_full_pipeline_simulation(self):
        """Test full pipeline simulation"""
        # Initialize all components
        counter = PersonCounter()
        visualizer = Visualizer()
        alert_system = AlertSystem(max_count=3)

        # Create a dummy frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # Simulate detections
        detections = [
            {"bbox": [100, 100, 200, 200], "confidence": 0.9, "class_id": 0},
            {"bbox": [300, 300, 400, 400], "confidence": 0.85, "class_id": 0},
            {"bbox": [500, 100, 600, 200], "confidence": 0.8, "class_id": 0},
            {"bbox": [200, 400, 300, 500], "confidence": 0.95, "class_id": 0},
        ]

        # Update counter
        count = counter.update_count(detections)

        # Draw visualizations
        result_frame = visualizer.draw_detections(
            frame, detections, person_count=counter.current_count
        )

        # Check alerts
        alert_system.check_alert(counter.current_count)

        # Verify results
        assert counter.current_count == 4
        assert count == 4
        assert result_frame is not None
        alerts = alert_system.get_alert_history()
        assert len(alerts) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
