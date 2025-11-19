"""
Unit tests for DataLogger - 23 Test Cases theo đặc tả
"""

import os
import time

import pandas as pd
import pytest

from src.core.data_logger import DataLogger


class TestDataLogger:
    """Test cases for DataLogger class"""

    @pytest.fixture
    def temp_csv_file(self, tmp_path):
        """Fixture tạo file CSV tạm thời"""
        return str(tmp_path / "test_data.csv")

    @pytest.fixture
    def logger(self, temp_csv_file):
        """Fixture tạo DataLogger với file tạm"""
        return DataLogger(filename=temp_csv_file, enabled=True)

    @pytest.fixture
    def sample_stats(self):
        """Fixture tạo dữ liệu stats mẫu"""
        return {
            "current_count": 5,
            "max_count": 10,
            "average_count": 7.5,
            "total_detections": 150,
            "total_frames": 100,
            "frames_with_persons": 80,
            "detection_rate": 0.8,
            "fps": 30.5,
            "running_time": 120.5,
        }

    def test_init_creates_csv_file(self, temp_csv_file):
        """TC1: Test khởi tạo DataLogger tạo file CSV với header"""
        DataLogger(filename=temp_csv_file, enabled=True)

        assert os.path.exists(temp_csv_file)

        # Kiểm tra header
        df = pd.read_csv(temp_csv_file)
        expected_columns = [
            "timestamp",
            "datetime",
            "person_count",
            "max_count",
            "average_count",
            "total_detections",
            "total_frames",
            "frames_with_persons",
            "detection_rate",
            "fps",
            "running_time",
        ]
        assert list(df.columns) == expected_columns
        assert len(df) == 0  # File mới không có dữ liệu

    def test_init_disabled_does_not_create_file(self, temp_csv_file):
        """TC2: Test khi disabled=False không tạo file"""
        DataLogger(filename=temp_csv_file, enabled=False)

        assert not os.path.exists(temp_csv_file)

    def test_log_data_adds_to_buffer_with_proper_formatting(self, logger, sample_stats):
        """TC3: Test log_data thêm record vào buffer với format đúng"""
        logger.log_data(sample_stats)

        assert len(logger.data_buffer) == 1

        record = logger.data_buffer[0]
        assert record["person_count"] == 5
        assert record["max_count"] == 10
        assert abs(record["average_count"] - 7.5) < 0.01
        assert record["total_detections"] == 150
        assert abs(record["fps"] - 30.5) < 0.01

    def test_handles_missing_stats_keys_gracefully(self, logger):
        """TC4: Test xử lý stats thiếu key không crash"""
        incomplete_stats = {
            "current_count": 5,
            # Thiếu các key khác
        }

        logger.log_data(incomplete_stats)

        assert len(logger.data_buffer) == 1
        record = logger.data_buffer[0]

        # Các key thiếu sẽ mặc định là 0
        assert record["max_count"] == 0
        assert abs(record["average_count"] - 0.0) < 0.001

    def test_log_data_disabled_does_nothing(self, temp_csv_file, sample_stats):
        """TC5: Test log_data không làm gì khi disabled"""
        logger = DataLogger(filename=temp_csv_file, enabled=False)
        logger.log_data(sample_stats)

        assert len(logger.data_buffer) == 0

    def test_save_to_csv_empty_buffer_does_nothing(self, logger):
        """TC6: Test save_to_csv với buffer rỗng không làm gì"""
        logger.save_to_csv()

        df = pd.read_csv(logger.filename)
        assert len(df) == 0

    def test_save_to_csv_disabled_keeps_buffer(self, temp_csv_file, sample_stats):
        """TC7: Test save_to_csv khi disabled không xóa buffer"""
        logger = DataLogger(filename=temp_csv_file, enabled=False)
        logger.data_buffer.append(sample_stats)
        logger.data_buffer.append(sample_stats)

        initial_buffer_len = len(logger.data_buffer)

        logger.save_to_csv()

        # File không được tạo
        assert not os.path.exists(temp_csv_file)

        # Buffer giữ nguyên
        assert len(logger.data_buffer) == initial_buffer_len

    def test_save_to_csv_creates_file_when_missing(self, logger, sample_stats):
        """TC8: Test save_to_csv tạo file mới với header khi file không tồn tại"""
        # Xóa file nếu tồn tại
        if os.path.exists(logger.filename):
            os.remove(logger.filename)

        # Thêm vào buffer
        logger.log_data(sample_stats)
        logger.log_data(sample_stats)

        assert len(logger.data_buffer) == 2

        # Gọi save_to_csv
        logger.save_to_csv()

        # Kiểm tra file được tạo
        assert os.path.exists(logger.filename)

        # Kiểm tra có header + 2 dòng dữ liệu
        df = pd.read_csv(logger.filename)
        assert len(df) == 2
        assert len(df.columns) == 11  # 11 cột theo spec

        # Buffer đã bị clear
        assert len(logger.data_buffer) == 0

    def test_save_to_csv_appends_to_existing_file(self, logger, sample_stats):
        """TC9: Test save_to_csv append vào file đã có"""
        # Lưu lần 1
        logger.log_data(sample_stats)
        logger.save_to_csv()

        # Lưu lần 2
        logger.log_data(sample_stats)
        logger.save_to_csv()

        # Kiểm tra có 2 records
        df = pd.read_csv(logger.filename)
        assert len(df) == 2

    def test_save_immediate_creates_file_with_header(self, temp_csv_file, sample_stats):
        """TC10: Test save_immediate tạo file mới với header"""
        # Xóa file nếu tồn tại
        if os.path.exists(temp_csv_file):
            os.remove(temp_csv_file)

        logger = DataLogger(filename=temp_csv_file, enabled=True)
        # Xóa file được tạo tự động
        os.remove(temp_csv_file)

        logger.save_immediate(sample_stats)

        # Kiểm tra file được tạo
        assert os.path.exists(temp_csv_file)

        df = pd.read_csv(temp_csv_file)
        assert len(df) == 1
        assert df["person_count"].iloc[0] == 5

    def test_save_immediate_appends_to_existing(self, logger, sample_stats):
        """TC11: Test save_immediate append vào file đã có"""
        logger.save_immediate(sample_stats)
        logger.save_immediate(sample_stats)

        df = pd.read_csv(logger.filename)
        assert len(df) == 2

    def test_save_immediate_disabled_does_nothing(self, temp_csv_file, sample_stats):
        """TC12: Test save_immediate không làm gì khi disabled"""
        if os.path.exists(temp_csv_file):
            os.remove(temp_csv_file)

        logger = DataLogger(filename=temp_csv_file, enabled=False)
        logger.save_immediate(sample_stats)

        assert not os.path.exists(temp_csv_file)

    def test_load_data_returns_dataframe(self, logger, sample_stats):
        """TC13: Test load_data trả về DataFrame"""
        logger.save_immediate(sample_stats)

        df = logger.load_data()

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert "person_count" in df.columns

    def test_load_data_nonexistent_file_returns_empty(self, temp_csv_file):
        """TC14: Test load_data với file không tồn tại trả về DataFrame rỗng"""
        if os.path.exists(temp_csv_file):
            os.remove(temp_csv_file)

        logger = DataLogger(filename=temp_csv_file, enabled=False)
        df = logger.load_data()

        assert isinstance(df, pd.DataFrame)
        assert df.empty

    def test_get_summary_stats_returns_correct_stats(self, logger, sample_stats):
        """TC15: Test get_summary_stats tính toán đúng"""
        # Lưu nhiều records với giá trị khác nhau
        stats1 = sample_stats.copy()
        stats1["current_count"] = 3
        stats1["running_time"] = 100

        stats2 = sample_stats.copy()
        stats2["current_count"] = 7
        stats2["running_time"] = 200

        logger.save_immediate(stats1)
        logger.save_immediate(stats2)

        summary = logger.get_summary_stats()

        assert summary["total_records"] == 2
        assert summary["max_person_count"] == 7
        assert abs(summary["avg_person_count"] - 5.0) < 0.01  # (3+7)/2
        assert abs(summary["total_running_time"] - 200) < 0.01  # Lấy record cuối
        assert "first_record" in summary
        assert "last_record" in summary

    def test_get_summary_stats_empty_returns_empty_dict(self, temp_csv_file):
        """TC16: Test get_summary_stats với file rỗng trả về dict rỗng"""
        logger = DataLogger(filename=temp_csv_file, enabled=True)

        summary = logger.get_summary_stats()

        assert summary == {}

    def test_clear_data_removes_and_recreates_file(self, logger, sample_stats):
        """TC17: Test clear_data xóa file và tạo lại với header"""
        logger.save_immediate(sample_stats)

        # Kiểm tra có dữ liệu
        df = pd.read_csv(logger.filename)
        assert len(df) == 1

        # Clear
        logger.clear_data()

        # Kiểm tra file mới rỗng nhưng có header
        assert os.path.exists(logger.filename)
        df = pd.read_csv(logger.filename)
        assert len(df) == 0
        assert len(df.columns) > 0  # Có header

    def test_export_to_excel_creates_xlsx(self, logger, sample_stats, tmp_path):
        """TC18: Test export_to_excel tạo file Excel"""
        logger.save_immediate(sample_stats)

        excel_file = str(tmp_path / "test_export.xlsx")
        logger.export_to_excel(excel_file)

        assert os.path.exists(excel_file)

        # Kiểm tra nội dung
        df = pd.read_excel(excel_file)
        assert len(df) == 1
        assert df["person_count"].iloc[0] == 5

    def test_export_to_excel_empty_data_does_not_crash(self, logger, tmp_path):
        """TC19: Test export_to_excel với dữ liệu rỗng không crash"""
        excel_file = str(tmp_path / "should_not_exist.xlsx")

        # Gọi export với dữ liệu rỗng
        logger.export_to_excel(excel_file)

        # Kiểm tra không crash (passed nếu đến được đây)
        if os.path.exists(excel_file):
            df = pd.read_excel(excel_file)
            assert len(df) == 0

    def test_set_enabled_toggles_logging(self, logger, sample_stats):
        """TC20: Test set_enabled bật/tắt logging"""
        logger.set_enabled(False)
        assert logger.enabled is False

        logger.log_data(sample_stats)
        assert len(logger.data_buffer) == 0  # Không thêm vào buffer

        logger.set_enabled(True)
        assert logger.enabled is True

        logger.log_data(sample_stats)
        assert len(logger.data_buffer) == 1  # Thêm vào buffer

    def test_multiple_logs_preserve_order(self, logger, sample_stats):
        """TC21: Test nhiều lần log giữ đúng thứ tự"""
        for i in range(5):
            stats = sample_stats.copy()
            stats["current_count"] = i
            logger.log_data(stats)

        logger.save_to_csv()

        df = pd.read_csv(logger.filename)
        assert len(df) == 5
        assert list(df["person_count"]) == [0, 1, 2, 3, 4]

    def test_log_data_adds_timestamp_correctly(self, logger, sample_stats):
        """TC22: Test log_data thêm timestamp tự động"""
        before_time = time.time()
        logger.log_data(sample_stats)
        after_time = time.time()

        record = logger.data_buffer[0]
        assert "timestamp" in record
        assert "datetime" in record
        # Cho phép sai số nhỏ trong timestamp
        assert before_time - 0.1 <= record["timestamp"] <= after_time + 0.1

    def test_log_data_rounds_values_correctly(self, logger, sample_stats):
        """TC23: Test log_data làm tròn giá trị đúng"""
        logger.log_data(sample_stats)

        record = logger.data_buffer[0]
        assert abs(record["average_count"] - 7.5) < 0.01  # round 2 chữ số
        assert abs(record["detection_rate"] - 0.8) < 0.001  # round 3 chữ số
        assert abs(record["fps"] - 30.5) < 0.01  # round 2 chữ số
        assert abs(record["running_time"] - 120.5) < 0.01  # round 2 chữ số
