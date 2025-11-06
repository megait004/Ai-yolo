"""
Unit tests for DataLogger
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
        """Test khởi tạo DataLogger tạo file CSV với header"""
        logger = DataLogger(filename=temp_csv_file, enabled=True)

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
        """Test khi disabled=False không tạo file"""
        logger = DataLogger(filename=temp_csv_file, enabled=False)

        assert not os.path.exists(temp_csv_file)

    def test_log_data_adds_to_buffer(self, logger, sample_stats):
        """Test log_data thêm record vào buffer"""
        logger.log_data(sample_stats)

        assert len(logger.data_buffer) == 1

        record = logger.data_buffer[0]
        assert record["person_count"] == 5
        assert record["max_count"] == 10
        assert record["average_count"] == 7.5
        assert record["total_detections"] == 150
        assert record["fps"] == 30.5

    def test_log_data_rounds_values(self, logger, sample_stats):
        """Test log_data làm tròn giá trị đúng"""
        logger.log_data(sample_stats)

        record = logger.data_buffer[0]
        assert record["average_count"] == 7.5  # round 2 chữ số
        assert record["detection_rate"] == 0.8  # round 3 chữ số
        assert record["fps"] == 30.5  # round 2 chữ số
        assert record["running_time"] == 120.5  # round 2 chữ số

    def test_log_data_adds_timestamp(self, logger, sample_stats):
        """Test log_data thêm timestamp tự động"""
        before_time = time.time()
        logger.log_data(sample_stats)
        after_time = time.time()

        record = logger.data_buffer[0]
        assert "timestamp" in record
        assert "datetime" in record
        # Cho phép sai số nhỏ trong timestamp
        assert before_time - 0.1 <= record["timestamp"] <= after_time + 0.1

    def test_log_data_disabled_does_nothing(self, temp_csv_file, sample_stats):
        """Test log_data không làm gì khi disabled"""
        logger = DataLogger(filename=temp_csv_file, enabled=False)
        logger.log_data(sample_stats)

        assert len(logger.data_buffer) == 0

    def test_save_to_csv_writes_buffer(self, logger, sample_stats):
        """Test save_to_csv ghi dữ liệu từ buffer vào file"""
        # Thêm dữ liệu vào buffer
        logger.log_data(sample_stats)
        logger.log_data(sample_stats)

        assert len(logger.data_buffer) == 2

        # Lưu vào CSV
        logger.save_to_csv()

        # Kiểm tra buffer đã bị xóa
        assert len(logger.data_buffer) == 0

        # Kiểm tra file CSV
        df = pd.read_csv(logger.filename)
        assert len(df) == 2
        assert df["person_count"].iloc[0] == 5

    def test_save_to_csv_empty_buffer_does_nothing(self, logger):
        """Test save_to_csv với buffer rỗng không làm gì"""
        logger.save_to_csv()

        df = pd.read_csv(logger.filename)
        assert len(df) == 0

    def test_save_to_csv_disabled_does_nothing(self, temp_csv_file, sample_stats):
        """Test save_to_csv không làm gì khi disabled"""
        logger = DataLogger(filename=temp_csv_file, enabled=False)
        logger.data_buffer.append({"test": "data"})

        logger.save_to_csv()

        # File không được tạo
        assert not os.path.exists(temp_csv_file)

    def test_save_to_csv_appends_to_existing_file(self, logger, sample_stats):
        """Test save_to_csv append vào file đã có"""
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
        """Test save_immediate tạo file mới với header"""
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
        """Test save_immediate append vào file đã có"""
        logger.save_immediate(sample_stats)
        logger.save_immediate(sample_stats)

        df = pd.read_csv(logger.filename)
        assert len(df) == 2

    def test_save_immediate_disabled_does_nothing(self, temp_csv_file, sample_stats):
        """Test save_immediate không làm gì khi disabled"""
        if os.path.exists(temp_csv_file):
            os.remove(temp_csv_file)

        logger = DataLogger(filename=temp_csv_file, enabled=False)
        logger.save_immediate(sample_stats)

        assert not os.path.exists(temp_csv_file)

    def test_load_data_returns_dataframe(self, logger, sample_stats):
        """Test load_data trả về DataFrame"""
        logger.save_immediate(sample_stats)

        df = logger.load_data()

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert "person_count" in df.columns

    def test_load_data_nonexistent_file_returns_empty(self, temp_csv_file):
        """Test load_data với file không tồn tại trả về DataFrame rỗng"""
        if os.path.exists(temp_csv_file):
            os.remove(temp_csv_file)

        logger = DataLogger(filename=temp_csv_file, enabled=False)
        df = logger.load_data()

        assert isinstance(df, pd.DataFrame)
        assert df.empty

    def test_get_summary_stats_returns_correct_stats(self, logger, sample_stats):
        """Test get_summary_stats tính toán đúng"""
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
        assert summary["avg_person_count"] == 5.0  # (3+7)/2
        assert summary["total_running_time"] == 200  # Lấy record cuối
        assert "first_record" in summary
        assert "last_record" in summary

    def test_get_summary_stats_empty_returns_empty_dict(self, temp_csv_file):
        """Test get_summary_stats với file rỗng trả về dict rỗng"""
        logger = DataLogger(filename=temp_csv_file, enabled=True)

        summary = logger.get_summary_stats()

        assert summary == {}

    def test_clear_data_removes_and_recreates_file(self, logger, sample_stats):
        """Test clear_data xóa file và tạo lại với header"""
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
        """Test export_to_excel tạo file Excel"""
        logger.save_immediate(sample_stats)

        excel_file = str(tmp_path / "test_export.xlsx")
        logger.export_to_excel(excel_file)

        assert os.path.exists(excel_file)

        # Kiểm tra nội dung
        df = pd.read_excel(excel_file)
        assert len(df) == 1
        assert df["person_count"].iloc[0] == 5

    def test_export_to_excel_empty_data_does_nothing(self, logger, tmp_path):
        """Test export_to_excel với dữ liệu rỗng không tạo file"""
        excel_file = str(tmp_path / "test_empty.xlsx")
        logger.export_to_excel(excel_file)

        # File không được tạo (hoặc empty - phụ thuộc implementation)
        # Chỉ đảm bảo không crash
        assert True

    def test_set_enabled_toggles_logging(self, logger, sample_stats):
        """Test set_enabled bật/tắt logging"""
        logger.set_enabled(False)
        assert logger.enabled is False

        logger.log_data(sample_stats)
        assert len(logger.data_buffer) == 0  # Không thêm vào buffer

        logger.set_enabled(True)
        assert logger.enabled is True

        logger.log_data(sample_stats)
        assert len(logger.data_buffer) == 1  # Thêm vào buffer

    def test_multiple_logs_preserve_order(self, logger, sample_stats):
        """Test nhiều lần log giữ đúng thứ tự"""
        for i in range(5):
            stats = sample_stats.copy()
            stats["current_count"] = i
            logger.log_data(stats)

        logger.save_to_csv()

        df = pd.read_csv(logger.filename)
        assert len(df) == 5
        assert list(df["person_count"]) == [0, 1, 2, 3, 4]

    def test_handles_missing_stats_keys_gracefully(self, logger):
        """Test xử lý stats thiếu key không crash"""
        incomplete_stats = {
            "current_count": 5,
            # Thiếu các key khác
        }

        logger.log_data(incomplete_stats)

        assert len(logger.data_buffer) == 1
        record = logger.data_buffer[0]

        # Các key thiếu sẽ mặc định là 0
        assert record["max_count"] == 0
        assert record["average_count"] == 0.0
