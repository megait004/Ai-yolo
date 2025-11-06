"""
Unit tests for AlertSystem
"""

import os
import time

import pytest

from src.core.alert_system import AlertSystem


class TestAlertSystem:
    """Test cases for AlertSystem class"""

    @pytest.fixture
    def alert_system(self):
        """Fixture tạo AlertSystem với ngưỡng mặc định"""
        return AlertSystem(max_count=10, enabled=True)

    @pytest.fixture
    def temp_log_file(self, tmp_path):
        """Fixture tạo file log tạm thời"""
        return str(tmp_path / "alert_log.txt")

    def test_init_default_values(self):
        """Test khởi tạo với giá trị mặc định"""
        alert_sys = AlertSystem(max_count=5, enabled=True)

        assert alert_sys.max_count == 5
        assert alert_sys.enabled is True
        assert alert_sys.alert_history == []
        assert alert_sys.last_alert_time == 0
        assert alert_sys.alert_cooldown == 5
        assert alert_sys.is_alert_active is False

    def test_check_alert_disabled_returns_none(self, alert_system):
        """Test check_alert trả về None khi disabled"""
        alert_system.set_enabled(False)

        result = alert_system.check_alert(15)  # Vượt ngưỡng

        assert result is None
        assert len(alert_system.alert_history) == 0

    def test_check_alert_below_threshold_no_alert(self, alert_system):
        """Test không có cảnh báo khi dưới ngưỡng"""
        result = alert_system.check_alert(5)  # Dưới ngưỡng 10

        assert result is None
        assert len(alert_system.alert_history) == 0

    def test_check_alert_exceeds_threshold_creates_warning(self, alert_system):
        """Test cảnh báo warning khi vượt ngưỡng 1-2 người"""
        result = alert_system.check_alert(11)  # Vượt 1 người

        assert result is not None
        assert result["type"] == "warning"
        assert result["person_count"] == 11
        assert result["max_count"] == 10
        assert result["excess_count"] == 1
        assert result["is_active"] is True
        assert len(alert_system.alert_history) == 1

    def test_check_alert_exceeds_threshold_creates_critical(self, alert_system):
        """Test cảnh báo critical khi vượt ngưỡng 3-5 người"""
        result = alert_system.check_alert(14)  # Vượt 4 người

        assert result is not None
        assert result["type"] == "critical"
        assert result["excess_count"] == 4

    def test_check_alert_exceeds_threshold_creates_emergency(self, alert_system):
        """Test cảnh báo emergency khi vượt ngưỡng >5 người"""
        result = alert_system.check_alert(17)  # Vượt 7 người

        assert result is not None
        assert result["type"] == "emergency"
        assert result["excess_count"] == 7

    def test_check_alert_cooldown_prevents_spam(self, alert_system):
        """Test cooldown ngăn spam cảnh báo"""
        # Cảnh báo đầu tiên
        result1 = alert_system.check_alert(15)
        assert result1 is not None
        assert len(alert_system.alert_history) == 1

        # Cảnh báo ngay sau (trong cooldown)
        result2 = alert_system.check_alert(15)
        assert result2 is not None
        assert result2["is_active"] is True
        assert len(alert_system.alert_history) == 1  # Không thêm vào history

    def test_check_alert_after_cooldown_creates_new_alert(self, alert_system):
        """Test tạo cảnh báo mới sau khi hết cooldown"""
        alert_system.set_alert_cooldown(1)  # 1 giây

        # Cảnh báo đầu tiên
        result1 = alert_system.check_alert(15)
        assert len(alert_system.alert_history) == 1

        # Đợi hết cooldown
        time.sleep(1.1)

        # Cảnh báo mới
        result2 = alert_system.check_alert(15)
        assert len(alert_system.alert_history) == 2

    def test_check_alert_returns_info_when_normalized(self, alert_system):
        """Test trả về info khi số người trở về bình thường"""
        # Tạo cảnh báo
        alert_system.check_alert(15)
        assert alert_system.is_alert_active is True

        # Số người giảm xuống
        result = alert_system.check_alert(5)

        assert result is not None
        assert result["type"] == "info"
        assert result["is_active"] is False
        assert alert_system.is_alert_active is False

    def test_get_alert_history_returns_all(self, alert_system):
        """Test get_alert_history trả về tất cả lịch sử"""
        alert_system.set_alert_cooldown(0)  # Tắt cooldown

        alert_system.check_alert(11)
        time.sleep(0.1)
        alert_system.check_alert(12)
        time.sleep(0.1)
        alert_system.check_alert(13)

        history = alert_system.get_alert_history()

        assert len(history) == 3
        assert isinstance(history, list)

    def test_get_alert_history_with_limit(self, alert_system):
        """Test get_alert_history với limit"""
        alert_system.set_alert_cooldown(0)

        for i in range(5):
            alert_system.check_alert(11 + i)
            time.sleep(0.1)

        history = alert_system.get_alert_history(limit=3)

        assert len(history) == 3
        # Lấy 3 cảnh báo gần nhất
        assert history[0]["person_count"] == 13

    def test_get_alert_history_returns_copy(self, alert_system):
        """Test get_alert_history trả về copy không shared reference"""
        alert_system.check_alert(15)

        history1 = alert_system.get_alert_history()
        history2 = alert_system.get_alert_history()

        assert history1 is not history2  # Khác reference
        assert history1 == history2  # Nhưng nội dung giống nhau

    def test_get_alert_stats_empty_history(self, alert_system):
        """Test get_alert_stats với lịch sử rỗng"""
        stats = alert_system.get_alert_stats()

        assert stats["total_alerts"] == 0
        assert stats["active_alerts"] == 0
        assert stats["max_person_count"] == 0
        assert stats["last_alert_time"] is None

    def test_get_alert_stats_with_alerts(self, alert_system):
        """Test get_alert_stats tính toán đúng"""
        alert_system.set_alert_cooldown(0)

        alert_system.check_alert(11)  # warning
        time.sleep(0.1)
        alert_system.check_alert(14)  # critical
        time.sleep(0.1)
        alert_system.check_alert(17)  # emergency

        stats = alert_system.get_alert_stats()

        assert stats["total_alerts"] == 3
        assert stats["max_person_count"] == 17
        assert stats["last_alert_time"] is not None
        assert stats["is_alert_active"] is True

        # Kiểm tra severity counts
        severity_counts = stats["severity_counts"]
        assert severity_counts["warning"] == 1
        assert severity_counts["critical"] == 1
        assert severity_counts["emergency"] == 1

    def test_save_alert_log_creates_file(self, alert_system, temp_log_file):
        """Test save_alert_log tạo file log"""
        alert_system.check_alert(15)

        alert_system.save_alert_log(temp_log_file)

        assert os.path.exists(temp_log_file)

        # Kiểm tra nội dung
        with open(temp_log_file, "r", encoding="utf-8") as f:
            content = f.read()

        assert "=== LỊCH SỬ CẢNH BÁO ===" in content
        assert "Cảnh báo #1:" in content
        assert "=== THỐNG KÊ ===" in content
        assert "Tổng số cảnh báo: 1" in content

    def test_save_alert_log_empty_history(self, alert_system, temp_log_file):
        """Test save_alert_log với lịch sử rỗng"""
        alert_system.save_alert_log(temp_log_file)

        assert os.path.exists(temp_log_file)

        with open(temp_log_file, "r", encoding="utf-8") as f:
            content = f.read()

        assert "Không có cảnh báo nào." in content

    def test_save_alert_log_multiple_alerts(self, alert_system, temp_log_file):
        """Test save_alert_log với nhiều cảnh báo"""
        alert_system.set_alert_cooldown(0)

        alert_system.check_alert(11)
        time.sleep(0.1)
        alert_system.check_alert(14)
        time.sleep(0.1)
        alert_system.check_alert(17)

        alert_system.save_alert_log(temp_log_file)

        with open(temp_log_file, "r", encoding="utf-8") as f:
            content = f.read()

        assert "Cảnh báo #1:" in content
        assert "Cảnh báo #2:" in content
        assert "Cảnh báo #3:" in content
        assert "Tổng số cảnh báo: 3" in content

    def test_save_alert_log_includes_alert_details(self, alert_system, temp_log_file):
        """Test save_alert_log bao gồm chi tiết cảnh báo"""
        alert_system.check_alert(15)

        alert_system.save_alert_log(temp_log_file)

        with open(temp_log_file, "r", encoding="utf-8") as f:
            content = f.read()

        assert "Thời gian:" in content
        assert "Loại:" in content
        assert "Thông điệp:" in content
        assert "Số người: 15" in content
        assert "Trạng thái:" in content

    def test_set_max_count_changes_threshold(self, alert_system):
        """Test set_max_count thay đổi ngưỡng"""
        alert_system.set_max_count(20)

        assert alert_system.max_count == 20

        # Kiểm tra cảnh báo mới dùng ngưỡng mới
        result = alert_system.check_alert(15)
        assert result is None  # Không cảnh báo vì 15 < 20

        result = alert_system.check_alert(21)
        assert result is not None  # Cảnh báo vì 21 > 20

    def test_set_enabled_toggles_alert_system(self, alert_system):
        """Test set_enabled bật/tắt hệ thống"""
        alert_system.set_enabled(False)
        assert alert_system.enabled is False

        result = alert_system.check_alert(15)
        assert result is None

        alert_system.set_enabled(True)
        assert alert_system.enabled is True

        result = alert_system.check_alert(15)
        assert result is not None

    def test_set_alert_cooldown_changes_cooldown(self, alert_system):
        """Test set_alert_cooldown thay đổi thời gian chờ"""
        alert_system.set_alert_cooldown(10)

        assert alert_system.alert_cooldown == 10

    def test_clear_alert_history_resets_state(self, alert_system):
        """Test clear_alert_history xóa lịch sử và reset state"""
        alert_system.check_alert(15)
        assert len(alert_system.alert_history) > 0
        assert alert_system.is_alert_active is True

        alert_system.clear_alert_history()

        assert len(alert_system.alert_history) == 0
        assert alert_system.is_alert_active is False

    def test_alert_message_format_warning(self, alert_system):
        """Test format thông điệp cảnh báo warning"""
        result = alert_system.check_alert(11)

        assert "Cảnh báo" in result["message"]
        assert "11 người" in result["message"]
        assert "vượt 1" in result["message"]

    def test_alert_message_format_critical(self, alert_system):
        """Test format thông điệp cảnh báo critical"""
        result = alert_system.check_alert(14)

        assert "nghiêm trọng" in result["message"]
        assert "14 người" in result["message"]
        assert "vượt 4" in result["message"]

    def test_alert_message_format_emergency(self, alert_system):
        """Test format thông điệp cảnh báo emergency"""
        result = alert_system.check_alert(17)

        assert "khẩn cấp" in result["message"]
        assert "17 người" in result["message"]
        assert "vượt 7" in result["message"]

    def test_alert_contains_timestamp_and_datetime(self, alert_system):
        """Test cảnh báo chứa timestamp và datetime"""
        result = alert_system.check_alert(15)

        assert "timestamp" in result
        assert "datetime" in result
        assert isinstance(result["timestamp"], (int, float))
        assert isinstance(result["datetime"], str)

    def test_consecutive_alerts_update_is_active_correctly(self, alert_system):
        """Test liên tiếp cảnh báo và bình thường hóa"""
        # Vượt ngưỡng
        result1 = alert_system.check_alert(15)
        assert result1["is_active"] is True
        assert alert_system.is_alert_active is True

        # Về bình thường
        result2 = alert_system.check_alert(5)
        assert result2["is_active"] is False
        assert alert_system.is_alert_active is False

        # Vượt lại
        alert_system.set_alert_cooldown(0)
        result3 = alert_system.check_alert(15)
        assert result3["is_active"] is True
        assert alert_system.is_alert_active is True

    def test_get_alert_severity_levels(self, alert_system):
        """Test phân loại severity đúng theo mức vượt"""
        # Warning: vượt 1-2
        severity1 = alert_system._get_alert_severity(11)
        assert severity1 == "warning"

        severity2 = alert_system._get_alert_severity(12)
        assert severity2 == "warning"

        # Critical: vượt 3-5
        severity3 = alert_system._get_alert_severity(13)
        assert severity3 == "critical"

        severity4 = alert_system._get_alert_severity(15)
        assert severity4 == "critical"

        # Emergency: vượt >5
        severity5 = alert_system._get_alert_severity(16)
        assert severity5 == "emergency"

        severity6 = alert_system._get_alert_severity(20)
        assert severity6 == "emergency"
