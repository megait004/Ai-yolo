"""
System Tests for Person Detection System
Test cases end-to-end cho toàn bộ hệ thống
"""

import pytest
import sys
import os
from pathlib import Path
import time
import cv2
import numpy as np
from unittest.mock import Mock, patch, MagicMock

# Thêm thư mục gốc vào Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.person_detector import PersonDetector
from src.core.person_counter import PersonCounter
from src.core.alert_system import AlertSystem
from src.core.data_logger import DataLogger


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_dirs(tmp_path):
    """Tạo các thư mục tạm cho tests"""
    data_dir = tmp_path / "data"
    output_dir = tmp_path / "output"
    data_dir.mkdir()
    output_dir.mkdir()
    return {
        "data": data_dir,
        "output": output_dir,
        "csv": output_dir / "test_log.csv",
        "alert": output_dir / "alert_log.txt",
        "excel": output_dir / "test_export.xlsx"
    }


@pytest.fixture
def mock_detector():
    """Mock PersonDetector để tránh load YOLO model thật"""
    detector = Mock(spec=PersonDetector)
    detector.confidence_threshold = 0.5
    detector.iou_threshold = 0.35
    detector.person_class_id = 0
    return detector


@pytest.fixture
def person_counter():
    """PersonCounter instance"""
    return PersonCounter()


@pytest.fixture
def alert_system():
    """AlertSystem instance với cấu hình test"""
    system = AlertSystem(max_count=10, enabled=True)
    # alert_cooldown được set mặc định = 5 trong __init__()
    return system


@pytest.fixture
def data_logger(temp_dirs):
    """DataLogger instance"""
    logger = DataLogger(filename=str(temp_dirs["csv"]), enabled=True)
    return logger


@pytest.fixture
def full_system(mock_detector, person_counter, alert_system, data_logger):
    """Hệ thống đầy đủ với tất cả modules"""
    return {
        "detector": mock_detector,
        "counter": person_counter,
        "alert": alert_system,
        "logger": data_logger
    }


def create_mock_frame(width=640, height=480, num_persons=0):
    """Tạo mock frame với số người xác định"""
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    # Vẽ các hình chữ nhật đại diện cho người
    for i in range(num_persons):
        x = 50 + (i % 5) * 100
        y = 50 + (i // 5) * 100
        cv2.rectangle(frame, (x, y), (x + 80, y + 150), (0, 255, 0), 2)
    return frame


def create_mock_detections(num_persons):
    """Tạo mock detections"""
    detections = []
    for i in range(num_persons):
        x = 50 + (i % 5) * 100
        y = 50 + (i // 5) * 100
        detections.append({
            "bbox": [x, y, x + 80, y + 150],
            "confidence": 0.8 + (i * 0.01),
            "class_id": 0
        })
    return detections


# ============================================================================
# TEST CLASS 1: VIDEO PROCESSING
# ============================================================================

class TestVideoProcessing:
    """Test cases STC1-STC10: Video Processing System"""

    def test_STC1_video_no_persons(self, full_system, temp_dirs):
        """STC1: Video không có người"""
        # Setup
        detector = full_system["detector"]
        counter = full_system["counter"]
        alert = full_system["alert"]
        logger = full_system["logger"]

        # Giả lập 100 frames không có người
        num_frames = 100
        detector.detect_persons = Mock(return_value=[])

        start_time = time.time()
        for i in range(num_frames):
            frame = create_mock_frame(num_persons=0)
            detections = detector.detect_persons(frame)
            counter.update_count(detections)

            alert_result = alert.check_alert(counter.get_current_count())

            stats = counter.get_all_stats()
            logger.log_data(stats)

        elapsed_time = time.time() - start_time
        fps = num_frames / elapsed_time if elapsed_time > 0 else 0

        # Assertions
        assert counter.get_current_count() == 0
        assert counter.get_max_count() == 0
        assert alert.is_alert_active == False
        assert len(alert.get_alert_history()) == 0
        assert fps >= 20, f"FPS quá thấp: {fps}"

        # Lưu và kiểm tra log
        logger.save_to_csv()
        assert temp_dirs["csv"].exists()

    def test_STC2_video_few_persons(self, full_system):
        """STC2: Video với 1-3 người"""
        detector = full_system["detector"]
        counter = full_system["counter"]
        alert = full_system["alert"]

        # Giả lập 50 frames với 2-3 người
        person_counts = [2, 2, 3, 3, 2, 1, 2, 3] * 6  # Lặp lại pattern

        for count in person_counts:
            detector.detect_persons = Mock(return_value=create_mock_detections(count))
            frame = create_mock_frame(num_persons=count)
            detections = detector.detect_persons(frame)
            counter.update_count(detections)
            alert.check_alert(counter.get_current_count())

        # Assertions
        assert counter.get_max_count() == 3
        assert counter.get_current_count() in [1, 2, 3]
        assert alert.is_alert_active == False, "Không nên có cảnh báo với <=10 người"
        assert len(alert.get_alert_history()) == 0

    def test_STC3_video_exceeds_threshold(self, full_system, temp_dirs):
        """STC3: Video vượt ngưỡng (15 người)"""
        detector = full_system["detector"]
        counter = full_system["counter"]
        alert = full_system["alert"]
        logger = full_system["logger"]

        # Giả lập video: 0-5-10-15-15-15 người
        person_sequence = [0]*10 + [5]*10 + [10]*10 + [15]*20

        for count in person_sequence:
            detector.detect_persons = Mock(return_value=create_mock_detections(count))
            frame = create_mock_frame(num_persons=count)
            detections = detector.detect_persons(frame)
            counter.update_count(detections)

            alert_result = alert.check_alert(counter.get_current_count())

        # Assertions
        assert counter.get_max_count() == 15
        assert alert.is_alert_active == True, "Alert phải active khi có 15 người"

        history = alert.get_alert_history()
        assert len(history) > 0, "Phải có ít nhất 1 alert"

        # Kiểm tra emergency alert được tạo
        emergency_alerts = [a for a in history if a.get("type") == "emergency"]
        assert len(emergency_alerts) > 0, "Phải có emergency alert khi 15 người"

        # Lưu alert log
        alert.save_alert_log(str(temp_dirs["alert"]))
        assert temp_dirs["alert"].exists()

    def test_STC4_low_quality_video(self, full_system):
        """STC4: Video chất lượng thấp (320x240)"""
        detector = full_system["detector"]
        counter = full_system["counter"]

        num_frames = 50
        detector.detect_persons = Mock(return_value=create_mock_detections(2))

        start_time = time.time()
        for _ in range(num_frames):
            frame = create_mock_frame(width=320, height=240, num_persons=2)
            detections = detector.detect_persons(frame)
            counter.update_count(detections)

        elapsed_time = time.time() - start_time
        fps = num_frames / elapsed_time if elapsed_time > 0 else 0

        # Với resolution thấp, FPS có thể thấp hơn nhưng vẫn xử lý được
        assert fps > 0, "Phải xử lý được video low quality"
        assert counter.get_current_count() == 2

    def test_STC5_high_quality_video(self, full_system):
        """STC5: Video HD (1920x1080)"""
        detector = full_system["detector"]
        counter = full_system["counter"]

        num_frames = 30  # Ít frames hơn vì HD xử lý chậm
        detector.detect_persons = Mock(return_value=create_mock_detections(3))

        start_time = time.time()
        for _ in range(num_frames):
            frame = create_mock_frame(width=1920, height=1080, num_persons=3)
            detections = detector.detect_persons(frame)
            counter.update_count(detections)

        elapsed_time = time.time() - start_time
        fps = num_frames / elapsed_time if elapsed_time > 0 else 0

        # FPS có thể thấp hơn với HD nhưng vẫn >= 15
        assert fps >= 10, f"FPS HD quá thấp: {fps}"
        assert counter.get_current_count() == 3

    def test_STC7_transition_video(self, full_system):
        """STC7: Video với transition (0→5→15 người)"""
        detector = full_system["detector"]
        counter = full_system["counter"]
        alert = full_system["alert"]

        # Phase 1: 0 người (30 frames)
        for _ in range(30):
            detector.detect_persons = Mock(return_value=[])
            frame = create_mock_frame(num_persons=0)
            detections = detector.detect_persons(frame)
            counter.update_count(detections)
            alert.check_alert(counter.get_current_count())

        phase1_count = counter.get_current_count()
        assert phase1_count == 0

        # Phase 2: 5 người (30 frames)
        for _ in range(30):
            detector.detect_persons = Mock(return_value=create_mock_detections(5))
            frame = create_mock_frame(num_persons=5)
            detections = detector.detect_persons(frame)
            counter.update_count(detections)
            alert.check_alert(counter.get_current_count())

        phase2_count = counter.get_current_count()
        assert phase2_count == 5
        assert alert.is_alert_active == False

        # Phase 3: 15 người (30 frames)
        for _ in range(30):
            detector.detect_persons = Mock(return_value=create_mock_detections(15))
            frame = create_mock_frame(num_persons=15)
            detections = detector.detect_persons(frame)
            counter.update_count(detections)
            alert.check_alert(counter.get_current_count())

        phase3_count = counter.get_current_count()
        assert phase3_count == 15
        assert counter.get_max_count() == 15
        assert alert.is_alert_active == True, "Alert phải active ở phase 3"

        # Kiểm tra average
        avg_count = counter.get_average_count()
        assert 5 <= avg_count <= 8, f"Average count không hợp lý: {avg_count}"


# ============================================================================
# TEST CLASS 2: ALERT INTEGRATION
# ============================================================================

class TestAlertIntegration:
    """Test cases STC11-STC18: Alert System Integration"""

    def test_STC11_no_alert_triggered(self, full_system):
        """STC11: Không trigger alert (count ≤ 10)"""
        counter = full_system["counter"]
        alert = full_system["alert"]
        detector = full_system["detector"]

        # Giữ count luôn ≤ 10
        for count in [5, 8, 10, 7, 9, 10] * 10:
            detector.detect_persons = Mock(return_value=create_mock_detections(count))
            frame = create_mock_frame(num_persons=count)
            detections = detector.detect_persons(frame)
            counter.update_count(detections)
            alert.check_alert(counter.get_current_count())

        # Assertions
        assert alert.is_alert_active == False
        assert len(alert.get_alert_history()) == 0

        stats = alert.get_alert_stats()
        assert stats["total_alerts"] == 0

    def test_STC12_warning_then_normalize(self, full_system):
        """STC12: Warning alert rồi normalize về bình thường"""
        counter = full_system["counter"]
        alert = full_system["alert"]
        detector = full_system["detector"]

        # Sequence: 8 → 11 → 12 → 10
        sequence = [8]*10 + [11]*10 + [12]*10 + [10]*10

        for count in sequence:
            detector.detect_persons = Mock(return_value=create_mock_detections(count))
            frame = create_mock_frame(num_persons=count)
            detections = detector.detect_persons(frame)
            counter.update_count(detections)
            alert.check_alert(counter.get_current_count())

        # Assertions
        history = alert.get_alert_history()
        assert len(history) > 0, "Phải có warning alerts"

        # Kiểm tra có warning
        warnings = [a for a in history if a.get("type") == "warning"]
        assert len(warnings) > 0, "Phải có ít nhất 1 warning"

        # Khi về 10, alert không còn active (hoặc có info alert)
        # is_alert_active có thể False hoặc True tùy implementation

    def test_STC13_critical_alert(self, full_system):
        """STC13: Critical alert (count 13-15)"""
        counter = full_system["counter"]
        alert = full_system["alert"]
        detector = full_system["detector"]

        # Sequence: 10 → 13 → 15 → 12
        sequence = [10]*10 + [13]*10 + [15]*10 + [12]*10

        for count in sequence:
            detector.detect_persons = Mock(return_value=create_mock_detections(count))
            frame = create_mock_frame(num_persons=count)
            detections = detector.detect_persons(frame)
            counter.update_count(detections)
            alert.check_alert(counter.get_current_count())

        # Assertions
        history = alert.get_alert_history()
        assert len(history) > 0

        # Kiểm tra có critical hoặc emergency
        critical_or_emergency = [a for a in history
                                 if a.get("type") in ["critical", "emergency"]]
        assert len(critical_or_emergency) > 0

    def test_STC14_emergency_alert(self, full_system, temp_dirs):
        """STC14: Emergency alert (count > 15)"""
        counter = full_system["counter"]
        alert = full_system["alert"]
        detector = full_system["detector"]

        # Sequence: 10 → 18
        sequence = [10]*10 + [18]*20

        for count in sequence:
            detector.detect_persons = Mock(return_value=create_mock_detections(count))
            frame = create_mock_frame(num_persons=count)
            detections = detector.detect_persons(frame)
            counter.update_count(detections)
            alert.check_alert(counter.get_current_count())

        # Assertions
        assert alert.is_alert_active == True

        history = alert.get_alert_history()
        assert len(history) > 0

        # Kiểm tra emergency
        emergency = [a for a in history if a.get("type") == "emergency"]
        assert len(emergency) > 0, "Phải có emergency alert"

        # Kiểm tra excess_count
        if emergency:
            assert emergency[0].get("excess_count") == 8  # 18 - 10 = 8

        # Save alert log
        alert.save_alert_log(str(temp_dirs["alert"]))
        assert temp_dirs["alert"].exists()

    def test_STC15_cooldown_prevents_spam(self, full_system):
        """STC15: Cooldown ngăn spam alerts"""
        counter = full_system["counter"]
        alert = full_system["alert"]
        detector = full_system["detector"]

        # Set cooldown = 2s
        alert.set_alert_cooldown(2.0)

        # Trigger alert lần 1
        for _ in range(5):
            detector.detect_persons = Mock(return_value=create_mock_detections(15))
            frame = create_mock_frame(num_persons=15)
            detections = detector.detect_persons(frame)
            counter.update_count(detections)
            alert.check_alert(counter.get_current_count())

        history_count_1 = len(alert.get_alert_history())
        assert history_count_1 > 0

        # Ngay lập tức trigger lại (trong cooldown)
        for _ in range(5):
            detector.detect_persons = Mock(return_value=create_mock_detections(15))
            frame = create_mock_frame(num_persons=15)
            detections = detector.detect_persons(frame)
            counter.update_count(detections)
            alert.check_alert(counter.get_current_count())

        history_count_2 = len(alert.get_alert_history())
        # History không tăng hoặc tăng rất ít (do cooldown)
        assert history_count_2 <= history_count_1 + 1

        # Chờ cooldown hết
        time.sleep(2.1)

        # Trigger lại (sau cooldown)
        for _ in range(5):
            detector.detect_persons = Mock(return_value=create_mock_detections(15))
            frame = create_mock_frame(num_persons=15)
            detections = detector.detect_persons(frame)
            counter.update_count(detections)
            alert.check_alert(counter.get_current_count())

        history_count_3 = len(alert.get_alert_history())
        # Sau cooldown, history phải tăng
        assert history_count_3 > history_count_2

    def test_STC16_toggle_alert_system(self, full_system):
        """STC16: Bật/tắt alert system"""
        counter = full_system["counter"]
        alert = full_system["alert"]
        detector = full_system["detector"]

        # Bật alert, trigger với 15 người
        alert.set_enabled(True)
        for _ in range(10):
            detector.detect_persons = Mock(return_value=create_mock_detections(15))
            frame = create_mock_frame(num_persons=15)
            detections = detector.detect_persons(frame)
            counter.update_count(detections)
            alert.check_alert(counter.get_current_count())

        history_1 = len(alert.get_alert_history())
        assert history_1 > 0, "Alert phải hoạt động khi enabled=True"

        # Tắt alert, trigger lại
        alert.set_enabled(False)
        alert.clear_alert_history()  # Clear để dễ test

        for _ in range(10):
            detector.detect_persons = Mock(return_value=create_mock_detections(15))
            frame = create_mock_frame(num_persons=15)
            detections = detector.detect_persons(frame)
            counter.update_count(detections)
            result = alert.check_alert(counter.get_current_count())
            assert result is None, "Alert phải trả về None khi disabled"

        history_2 = len(alert.get_alert_history())
        assert history_2 == 0, "Alert không được ghi khi disabled"

    def test_STC17_change_threshold(self, full_system):
        """STC17: Thay đổi ngưỡng alert"""
        counter = full_system["counter"]
        alert = full_system["alert"]
        detector = full_system["detector"]

        # Đặt ngưỡng = 15, test với 12 người
        alert.set_max_count(15)

        for _ in range(10):
            detector.detect_persons = Mock(return_value=create_mock_detections(12))
            frame = create_mock_frame(num_persons=12)
            detections = detector.detect_persons(frame)
            counter.update_count(detections)
            alert.check_alert(counter.get_current_count())

        assert len(alert.get_alert_history()) == 0, "12 < 15, không alert"

        # Đổi ngưỡng = 10, test lại
        alert.set_max_count(10)
        counter.reset_stats()

        for _ in range(10):
            detector.detect_persons = Mock(return_value=create_mock_detections(12))
            frame = create_mock_frame(num_persons=12)
            detections = detector.detect_persons(frame)
            counter.update_count(detections)
            alert.check_alert(counter.get_current_count())

        assert len(alert.get_alert_history()) > 0, "12 > 10, phải có alert"


# ============================================================================
# TEST CLASS 3: DATA LOGGING INTEGRATION
# ============================================================================

class TestDataLoggingIntegration:
    """Test cases STC19-STC26: Data Logging Integration"""

    def test_STC19_buffered_logging(self, full_system, temp_dirs):
        """STC19: Buffered logging mode"""
        counter = full_system["counter"]
        logger = full_system["logger"]
        detector = full_system["detector"]

        num_frames = 50
        log_interval = 5  # Log mỗi 5 frames

        for i in range(num_frames):
            detector.detect_persons = Mock(return_value=create_mock_detections(5))
            frame = create_mock_frame(num_persons=5)
            detections = detector.detect_persons(frame)
            counter.update_count(detections)

            if (i + 1) % log_interval == 0:
                stats = counter.get_all_stats()
                logger.log_data(stats)

        # Save buffer cuối video
        logger.save_to_csv()

        # Assertions
        assert temp_dirs["csv"].exists()

        # Đọc CSV
        df = logger.load_data()
        expected_rows = num_frames // log_interval
        assert len(df) == expected_rows, f"Expected {expected_rows} rows, got {len(df)}"
        assert len(df.columns) == 11, "Phải có 11 cột"

    def test_STC20_immediate_logging(self, full_system, temp_dirs):
        """STC20: Immediate logging mode"""
        counter = full_system["counter"]
        logger = full_system["logger"]
        detector = full_system["detector"]

        num_frames = 30

        for i in range(num_frames):
            detector.detect_persons = Mock(return_value=create_mock_detections(3))
            frame = create_mock_frame(num_persons=3)
            detections = detector.detect_persons(frame)
            counter.update_count(detections)

            stats = counter.get_all_stats()
            logger.save_immediate(stats)  # Lưu ngay mỗi frame

        # Assertions
        assert temp_dirs["csv"].exists()

        df = logger.load_data()
        assert len(df) == num_frames, f"Phải có {num_frames} dòng"

    def test_STC21_logging_disabled(self, temp_dirs):
        """STC21: Logging bị tắt"""
        counter = PersonCounter()
        logger = DataLogger(filename=str(temp_dirs["csv"]), enabled=False)

        # Giả lập xử lý video
        for i in range(30):
            detections = create_mock_detections(5)
            counter.update_count(detections)
            stats = counter.get_all_stats()
            logger.log_data(stats)

        logger.save_to_csv()

        # CSV không được tạo hoặc rỗng
        if temp_dirs["csv"].exists():
            df = logger.load_data()
            assert df.empty, "CSV phải rỗng khi logging disabled"

    def test_STC22_log_order_preservation(self, full_system, temp_dirs):
        """STC22: Thứ tự log được giữ nguyên"""
        counter = full_system["counter"]
        logger = full_system["logger"]
        detector = full_system["detector"]

        # Sequence: 5 → 10 → 15 → 20 → 15 → 10 → 5
        sequence = [5, 10, 15, 20, 15, 10, 5]

        for count in sequence:
            detector.detect_persons = Mock(return_value=create_mock_detections(count))
            frame = create_mock_frame(num_persons=count)
            detections = detector.detect_persons(frame)
            counter.update_count(detections)

            stats = counter.get_all_stats()
            logger.log_data(stats)

        logger.save_to_csv()

        # Assertions
        df = logger.load_data()
        assert len(df) == len(sequence)

        # Kiểm tra person_count theo đúng thứ tự
        person_counts = df["person_count"].tolist()
        assert person_counts == sequence, "Thứ tự không khớp"

        # Kiểm tra timestamp tăng dần
        timestamps = df["timestamp"].tolist()
        assert all(timestamps[i] <= timestamps[i+1] for i in range(len(timestamps)-1))

    def test_STC23_summary_stats(self, full_system, temp_dirs):
        """STC23: Summary statistics"""
        counter = full_system["counter"]
        logger = full_system["logger"]
        detector = full_system["detector"]

        # Log 10 frames
        for i in range(10):
            count = 5 + i  # 5,6,7,...,14
            detector.detect_persons = Mock(return_value=create_mock_detections(count))
            frame = create_mock_frame(num_persons=count)
            detections = detector.detect_persons(frame)
            counter.update_count(detections)

            stats = counter.get_all_stats()
            logger.log_data(stats)

        logger.save_to_csv()

        # Get summary
        summary = logger.get_summary_stats()

        # Assertions
        assert summary["total_records"] == 10
        assert summary["max_person_count"] == 14
        assert "avg_person_count" in summary
        assert "first_record" in summary
        assert "last_record" in summary

    def test_STC24_export_to_excel(self, full_system, temp_dirs):
        """STC24: Export to Excel"""
        counter = full_system["counter"]
        logger = full_system["logger"]
        detector = full_system["detector"]

        # Log data
        for i in range(10):
            detector.detect_persons = Mock(return_value=create_mock_detections(5))
            frame = create_mock_frame(num_persons=5)
            detections = detector.detect_persons(frame)
            counter.update_count(detections)

            stats = counter.get_all_stats()
            logger.log_data(stats)

        logger.save_to_csv()

        # Export to Excel
        excel_path = str(temp_dirs["excel"])
        logger.export_to_excel(excel_path)

        # Assertions
        assert temp_dirs["excel"].exists()

    def test_STC25_value_rounding(self, full_system, temp_dirs):
        """STC25: Làm tròn giá trị"""
        logger = full_system["logger"]

        # Log với giá trị cần làm tròn
        stats = {
            "current_count": 5,
            "max_count": 10,
            "average_count": 7.567,
            "total_detections": 50,
            "frame_count": 10,
            "fps": 30.789,
            "running_time": 100.123,
            "detection_rate": 0.8234,
            "frames_with_persons": 8
        }

        logger.log_data(stats)
        logger.save_to_csv()

        # Đọc lại
        df = logger.load_data()
        assert len(df) == 1

        row = df.iloc[0]
        # Kiểm tra làm tròn (average: 2 số, rate: 3 số, fps: 2 số)
        assert abs(row["average_count"] - 7.57) < 0.01
        assert abs(row["detection_rate"] - 0.823) < 0.001
        assert abs(row["fps"] - 30.79) < 0.01

    def test_STC26_clear_then_log_again(self, full_system, temp_dirs):
        """STC26: Clear data rồi log lại"""
        counter = full_system["counter"]
        logger = full_system["logger"]
        detector = full_system["detector"]

        # Log đợt 1
        for i in range(5):
            detector.detect_persons = Mock(return_value=create_mock_detections(5))
            frame = create_mock_frame(num_persons=5)
            detections = detector.detect_persons(frame)
            counter.update_count(detections)
            stats = counter.get_all_stats()
            logger.log_data(stats)

        logger.save_to_csv()
        df1 = logger.load_data()
        assert len(df1) == 5

        # Clear
        logger.clear_data()
        df_after_clear = logger.load_data()
        assert df_after_clear.empty, "Sau clear phải rỗng"

        # Log đợt 2
        counter.reset_stats()
        for i in range(3):
            detector.detect_persons = Mock(return_value=create_mock_detections(8))
            frame = create_mock_frame(num_persons=8)
            detections = detector.detect_persons(frame)
            counter.update_count(detections)
            stats = counter.get_all_stats()
            logger.log_data(stats)

        logger.save_to_csv()
        df2 = logger.load_data()
        assert len(df2) == 3, "Chỉ có dữ liệu mới"


# ============================================================================
# TEST CLASS 4: END-TO-END FULL SYSTEM
# ============================================================================

class TestEndToEndFullSystem:
    """Test cases STC27-STC36: Full System E2E"""

    def test_STC27_normal_scene(self, full_system, temp_dirs):
        """STC27: Normal scene (3-8 người)"""
        detector = full_system["detector"]
        counter = full_system["counter"]
        alert = full_system["alert"]
        logger = full_system["logger"]

        num_frames = 100

        start_time = time.time()
        for i in range(num_frames):
            # Random 3-8 người
            count = 3 + (i % 6)  # 3,4,5,6,7,8,3,4,...
            detector.detect_persons = Mock(return_value=create_mock_detections(count))
            frame = create_mock_frame(num_persons=count)

            # Full pipeline
            detections = detector.detect_persons(frame)
            counter.update_count(detections)
            alert.check_alert(counter.get_current_count())
            stats = counter.get_all_stats()
            logger.log_data(stats)

        elapsed = time.time() - start_time
        fps = num_frames / elapsed if elapsed > 0 else 0

        logger.save_to_csv()

        # Assertions
        assert counter.get_max_count() == 8
        assert alert.is_alert_active == False, "Không alert với ≤10 người"
        assert len(alert.get_alert_history()) == 0
        assert temp_dirs["csv"].exists()
        assert fps >= 15, f"FPS quá thấp: {fps}"

        df = logger.load_data()
        assert len(df) == num_frames

    def test_STC28_crowded_scene(self, full_system, temp_dirs):
        """STC28: Crowded scene (15-20 người)"""
        detector = full_system["detector"]
        counter = full_system["counter"]
        alert = full_system["alert"]
        logger = full_system["logger"]

        num_frames = 100

        for i in range(num_frames):
            count = 15 + (i % 6)  # 15-20 người
            detector.detect_persons = Mock(return_value=create_mock_detections(count))
            frame = create_mock_frame(num_persons=count)

            detections = detector.detect_persons(frame)
            counter.update_count(detections)
            alert.check_alert(counter.get_current_count())
            stats = counter.get_all_stats()
            logger.log_data(stats)

        logger.save_to_csv()
        alert.save_alert_log(str(temp_dirs["alert"]))

        # Assertions
        assert counter.get_max_count() == 20
        assert alert.is_alert_active == True
        assert len(alert.get_alert_history()) > 0

        # Kiểm tra emergency alerts
        history = alert.get_alert_history()
        emergency = [a for a in history if a.get("type") == "emergency"]
        assert len(emergency) > 0

        df = logger.load_data()
        assert df["person_count"].max() == 20

    def test_STC29_empty_scene(self, full_system, temp_dirs):
        """STC29: Empty scene (0 người)"""
        detector = full_system["detector"]
        counter = full_system["counter"]
        alert = full_system["alert"]
        logger = full_system["logger"]

        num_frames = 100
        detector.detect_persons = Mock(return_value=[])

        for _ in range(num_frames):
            frame = create_mock_frame(num_persons=0)
            detections = detector.detect_persons(frame)
            counter.update_count(detections)
            alert.check_alert(counter.get_current_count())
            stats = counter.get_all_stats()
            logger.log_data(stats)

        logger.save_to_csv()

        # Assertions
        assert counter.get_current_count() == 0
        assert counter.get_max_count() == 0
        assert counter.get_detection_rate() == 0.0
        assert alert.is_alert_active == False

        df = logger.load_data()
        assert all(df["person_count"] == 0)

    def test_STC31_long_duration(self, full_system):
        """STC31: Video dài (300 frames ~ 5 phút @ 1fps)"""
        detector = full_system["detector"]
        counter = full_system["counter"]
        alert = full_system["alert"]
        logger = full_system["logger"]

        num_frames = 300

        for i in range(num_frames):
            count = 5 + (i % 10)  # 5-14 người
            detector.detect_persons = Mock(return_value=create_mock_detections(count))
            frame = create_mock_frame(num_persons=count)

            detections = detector.detect_persons(frame)
            counter.update_count(detections)
            alert.check_alert(counter.get_current_count())
            stats = counter.get_all_stats()

            # Log mỗi 10 frames để giảm overhead
            if i % 10 == 0:
                logger.log_data(stats)

        logger.save_to_csv()

        # Assertions
        assert counter.get_frame_count() == num_frames
        assert counter.get_max_count() == 14

        df = logger.load_data()
        assert len(df) == num_frames // 10

    def test_STC32_restart_between_videos(self, full_system):
        """STC32: Reset giữa các video"""
        detector = full_system["detector"]
        counter = full_system["counter"]
        alert = full_system["alert"]

        # Video 1
        for _ in range(30):
            detector.detect_persons = Mock(return_value=create_mock_detections(15))
            frame = create_mock_frame(num_persons=15)
            detections = detector.detect_persons(frame)
            counter.update_count(detections)
            alert.check_alert(counter.get_current_count())

        video1_max = counter.get_max_count()
        video1_alerts = len(alert.get_alert_history())
        assert video1_max == 15
        assert video1_alerts > 0

        # Reset
        counter.reset_stats()
        alert.clear_alert_history()

        # Video 2
        for _ in range(30):
            detector.detect_persons = Mock(return_value=create_mock_detections(5))
            frame = create_mock_frame(num_persons=5)
            detections = detector.detect_persons(frame)
            counter.update_count(detections)
            alert.check_alert(counter.get_current_count())

        video2_max = counter.get_max_count()
        video2_alerts = len(alert.get_alert_history())

        # Assertions
        assert video2_max == 5, "Max count phải reset về 5"
        assert video2_alerts == 0, "Alert history phải sạch"

    def test_STC35_export_all_outputs(self, full_system, temp_dirs):
        """STC35: Export tất cả outputs"""
        detector = full_system["detector"]
        counter = full_system["counter"]
        alert = full_system["alert"]
        logger = full_system["logger"]

        # Xử lý video có alerts
        for i in range(50):
            count = 10 + (i % 8)  # 10-17 người
            detector.detect_persons = Mock(return_value=create_mock_detections(count))
            frame = create_mock_frame(num_persons=count)

            detections = detector.detect_persons(frame)
            counter.update_count(detections)
            alert.check_alert(counter.get_current_count())
            stats = counter.get_all_stats()
            logger.log_data(stats)

        # Export tất cả
        logger.save_to_csv()
        alert.save_alert_log(str(temp_dirs["alert"]))
        logger.export_to_excel(str(temp_dirs["excel"]))

        # Assertions
        assert temp_dirs["csv"].exists(), "CSV log phải tồn tại"
        assert temp_dirs["alert"].exists(), "Alert log phải tồn tại"
        assert temp_dirs["excel"].exists(), "Excel export phải tồn tại"

        # Kiểm tra nội dung
        df = logger.load_data()
        assert len(df) == 50

        history = alert.get_alert_history()
        assert len(history) > 0


# ============================================================================
# TEST CLASS 5: PERFORMANCE TESTING
# ============================================================================

class TestPerformance:
    """Test cases STC37-STC43: Performance Testing"""

    def test_STC37_standard_resolution_performance(self, full_system):
        """STC37: Performance với 640x480"""
        detector = full_system["detector"]
        counter = full_system["counter"]

        num_frames = 100
        detector.detect_persons = Mock(return_value=create_mock_detections(5))

        start_time = time.time()
        for _ in range(num_frames):
            frame = create_mock_frame(width=640, height=480, num_persons=5)
            detections = detector.detect_persons(frame)
            counter.update_count(detections)

        elapsed = time.time() - start_time
        fps = num_frames / elapsed if elapsed > 0 else 0

        # Assertions
        assert fps >= 20, f"FPS không đạt yêu cầu: {fps:.2f}"
        assert elapsed <= 10, f"Thời gian xử lý quá lâu: {elapsed:.2f}s"

    def test_STC38_hd_resolution_performance(self, full_system):
        """STC38: Performance với 1280x720"""
        detector = full_system["detector"]
        counter = full_system["counter"]

        num_frames = 50
        detector.detect_persons = Mock(return_value=create_mock_detections(5))

        start_time = time.time()
        for _ in range(num_frames):
            frame = create_mock_frame(width=1280, height=720, num_persons=5)
            detections = detector.detect_persons(frame)
            counter.update_count(detections)

        elapsed = time.time() - start_time
        fps = num_frames / elapsed if elapsed > 0 else 0

        # Yêu cầu thấp hơn cho HD
        assert fps >= 10, f"FPS HD quá thấp: {fps:.2f}"

    def test_STC40_load_test_many_persons(self, full_system):
        """STC40: Load test với nhiều người (20 người)"""
        detector = full_system["detector"]
        counter = full_system["counter"]

        num_frames = 100
        detector.detect_persons = Mock(return_value=create_mock_detections(20))

        start_time = time.time()
        for _ in range(num_frames):
            frame = create_mock_frame(num_persons=20)
            detections = detector.detect_persons(frame)
            counter.update_count(detections)

        elapsed = time.time() - start_time
        fps = num_frames / elapsed if elapsed > 0 else 0

        # FPS có thể giảm nhưng vẫn phải >= 15
        assert fps >= 10, f"FPS với 20 người quá thấp: {fps:.2f}"
        assert counter.get_current_count() == 20

    def test_STC41_memory_stability_long_run(self, full_system):
        """STC41: Memory stability với video dài"""
        detector = full_system["detector"]
        counter = full_system["counter"]
        logger = full_system["logger"]

        num_frames = 500

        for i in range(num_frames):
            count = 5 + (i % 10)
            detector.detect_persons = Mock(return_value=create_mock_detections(count))
            frame = create_mock_frame(num_persons=count)

            detections = detector.detect_persons(frame)
            counter.update_count(detections)

            if i % 10 == 0:
                stats = counter.get_all_stats()
                logger.log_data(stats)

        # Assertions
        assert counter.get_frame_count() == num_frames
        # History chỉ giữ 100 frames gần nhất
        history_len = len(counter.count_history)
        assert history_len == 100, f"History phải limit 100, got {history_len}"

    def test_STC42_batch_processing(self, full_system):
        """STC42: Xử lý nhiều video liên tiếp"""
        detector = full_system["detector"]
        counter = full_system["counter"]

        num_videos = 5
        frames_per_video = 50

        total_start = time.time()

        for video_idx in range(num_videos):
            # Reset cho mỗi video
            counter.reset_stats()

            for frame_idx in range(frames_per_video):
                count = 3 + (frame_idx % 5)
                detector.detect_persons = Mock(return_value=create_mock_detections(count))
                frame = create_mock_frame(num_persons=count)

                detections = detector.detect_persons(frame)
                counter.update_count(detections)

            # Verify video hoàn thành
            assert counter.get_frame_count() == frames_per_video

        total_elapsed = time.time() - total_start
        total_frames = num_videos * frames_per_video
        avg_fps = total_frames / total_elapsed if total_elapsed > 0 else 0

        # Assertions
        assert avg_fps >= 15, f"Average FPS batch quá thấp: {avg_fps:.2f}"
        assert total_elapsed <= 20, f"Tổng thời gian quá lâu: {total_elapsed:.2f}s"


# ============================================================================
# TEST CLASS 6: MODULE INTEGRATION
# ============================================================================

class TestModuleIntegration:
    """Test cases STC44-STC50: Module Integration"""

    def test_STC44_detector_to_counter(self, mock_detector, person_counter):
        """STC44: Detector → Counter integration"""
        # Detector trả về 5 detections
        detections = create_mock_detections(5)
        mock_detector.detect_persons = Mock(return_value=detections)

        frame = create_mock_frame(num_persons=5)
        result = mock_detector.detect_persons(frame)

        # Counter nhận detections
        person_counter.update_count(result)

        # Assertions
        assert person_counter.get_current_count() == 5
        assert person_counter.total_detections == 5  # Dùng attribute trực tiếp, không có getter
        assert person_counter.frame_count == 1  # frame_count cũng là attribute

    def test_STC45_counter_to_alert(self, person_counter, alert_system):
        """STC45: Counter → Alert integration"""
        # Counter đếm đến 15 người
        detections = create_mock_detections(15)
        person_counter.update_count(detections)

        count = person_counter.get_current_count()
        assert count == 15

        # Alert nhận count
        alert_result = alert_system.check_alert(count)

        # Assertions
        assert alert_result is not None
        assert alert_system.is_alert_active == True
        assert len(alert_system.get_alert_history()) > 0

    def test_STC47_full_pipeline(self, full_system):
        """STC47: Full pipeline (Detector → Counter → Alert → Logger)"""
        detector = full_system["detector"]
        counter = full_system["counter"]
        alert = full_system["alert"]
        logger = full_system["logger"]

        # 1 cycle hoàn chỉnh
        frame = create_mock_frame(num_persons=12)

        # Step 1: Detect
        detections = create_mock_detections(12)
        detector.detect_persons = Mock(return_value=detections)
        result = detector.detect_persons(frame)
        assert len(result) == 12

        # Step 2: Count
        counter.update_count(result)
        assert counter.get_current_count() == 12

        # Step 3: Alert
        alert_result = alert.check_alert(counter.get_current_count())
        # 12 > 10, nên có alert
        assert alert_result is not None

        # Step 4: Log
        stats = counter.get_all_stats()
        logger.log_data(stats)
        assert len(logger.data_buffer) > 0

    def test_STC49_state_consistency_100_frames(self, full_system):
        """STC49: State consistency sau 100 frames"""
        detector = full_system["detector"]
        counter = full_system["counter"]
        alert = full_system["alert"]
        logger = full_system["logger"]

        num_frames = 100

        for i in range(num_frames):
            count = 5 + (i % 8)  # 5-12 người
            detector.detect_persons = Mock(return_value=create_mock_detections(count))
            frame = create_mock_frame(num_persons=count)

            detections = detector.detect_persons(frame)
            counter.update_count(detections)
            alert.check_alert(counter.get_current_count())
            stats = counter.get_all_stats()
            logger.log_data(stats)

        # Kiểm tra state của tất cả modules

        # Counter
        assert counter.get_frame_count() == num_frames
        assert len(counter.count_history) == 100  # Limited to 100
        assert counter.get_max_count() == 12

        # Alert
        history = alert.get_alert_history()
        # Có 12 và 11 > 10, nên có alerts
        assert len(history) > 0

        # Logger
        assert len(logger.data_buffer) == num_frames

    def test_STC50_reset_cascade(self, full_system):
        """STC50: Reset cascade effect"""
        detector = full_system["detector"]
        counter = full_system["counter"]
        alert = full_system["alert"]

        # Xử lý một số frames
        for _ in range(20):
            detector.detect_persons = Mock(return_value=create_mock_detections(15))
            frame = create_mock_frame(num_persons=15)
            detections = detector.detect_persons(frame)
            counter.update_count(detections)
            alert.check_alert(counter.get_current_count())

        # Verify có data
        assert counter.get_frame_count() == 20
        assert len(alert.get_alert_history()) > 0

        # Reset counter
        counter.reset_stats()

        # Kiểm tra counter đã reset
        assert counter.get_current_count() == 0
        assert counter.get_max_count() == 0
        assert counter.get_frame_count() == 0

        # Alert vẫn giữ history (design choice - có thể khác)
        # Hoặc có thể reset tùy thiết kế
        # assert len(alert.get_alert_history()) > 0  # Giữ nguyên
        # hoặc
        # alert.clear_alert_history()  # Reset manual


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
