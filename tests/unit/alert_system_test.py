"""
Unit tests for AlertSystem - 20 Test Cases theo đặc tả
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

    def test_check_alert_disabled_returns_none(self, alert_system):
        """TC1: Test check_alert trả về None khi disabled"""
        alert_system.set_enabled(False)

        result = alert_system.check_alert(15)  # Vượt ngưỡng

        assert result is None
        assert len(alert_system.alert_history) == 0

    def test_check_alert_below_threshold_no_alert(self, alert_system):
        """TC2: Test không có cảnh báo khi dưới ngưỡng"""
        result = alert_system.check_alert(5)  # Dưới ngưỡng 10

        assert result is None
        assert len(alert_system.alert_history) == 0

    def test_check_alert_returns_info_when_normalized(self, alert_system):
        """TC3: Test trả về info khi số người trở về bình thường"""
        # Tạo cảnh báo
        alert_system.check_alert(15)
        assert alert_system.is_alert_active is True

        # Số người giảm xuống
        result = alert_system.check_alert(5)

        assert result is not None
        assert result["type"] == "info"
        assert result["is_active"] is False
        assert alert_system.is_alert_active is False

    def test_check_alert_warning_lower_boundary(self, alert_system):
        """TC4: Test cảnh báo warning ở biên trái (count=11, vượt 1)"""
        result = alert_system.check_alert(11)
        assert result is not None
        assert result["type"] == "warning"
        assert result["excess_count"] == 1

    def test_check_alert_warning_upper_boundary(self, alert_system):
        """TC5: Test cảnh báo warning ở biên phải (count=12, vượt 2)"""
        result = alert_system.check_alert(12)
        assert result is not None
        assert result["type"] == "warning"
        assert result["excess_count"] == 2

    def test_check_alert_critical_lower_boundary(self, alert_system):
        """TC6: Test cảnh báo critical ở biên trái (count=13, vượt 3)"""
        result = alert_system.check_alert(13)
        assert result is not None
        assert result["type"] == "critical"
        assert result["excess_count"] == 3

    def test_check_alert_critical_upper_boundary(self, alert_system):
        """TC7: Test cảnh báo critical ở biên phải (count=15, vượt 5)"""
        result = alert_system.check_alert(15)
        assert result is not None
        assert result["type"] == "critical"
        assert result["excess_count"] == 5

    def test_check_alert_emergency_lower_boundary(self, alert_system):
        """TC8: Test cảnh báo emergency ở biên trái (count=16, vượt 6)"""
        result = alert_system.check_alert(16)
        assert result is not None
        assert result["type"] == "emergency"
        assert result["excess_count"] == 6

    def test_check_alert_emergency_high_count(self, alert_system):
        """TC9: Test cảnh báo emergency với count cao (count=20, vượt 10)"""
        result = alert_system.check_alert(20)
        assert result is not None
        assert result["type"] == "emergency"
        assert result["excess_count"] == 10

    def test_check_alert_cooldown_prevents_spam(self, alert_system):
        """TC10: Test cooldown ngăn spam cảnh báo"""
        # Cảnh báo đầu tiên
        result1 = alert_system.check_alert(15)
        assert result1 is not None
        assert len(alert_system.alert_history) == 1

        # Cảnh báo ngay sau (trong cooldown)
        result2 = alert_system.check_alert(15)
        assert result2 is not None
        assert result2["is_active"] is True
        assert len(alert_system.alert_history) == 1  # Không thêm vào history

    def test_check_alert_zero_people_no_alert(self, alert_system):
        """TC11: Test với count=0 (biên trái invalid)"""
        result = alert_system.check_alert(0)
        assert result is None

    def test_check_alert_at_threshold_no_alert(self, alert_system):
        """TC12: Test với count=10 (đúng bằng ngưỡng)"""
        result = alert_system.check_alert(10)
        assert result is None

    def test_get_alert_history_with_limit(self, alert_system):
        """TC13: Test get_alert_history với limit"""
        alert_system.set_alert_cooldown(0)

        for i in range(5):
            alert_system.check_alert(11 + i)
            time.sleep(0.01)

        history = alert_system.get_alert_history(limit=3)

        assert len(history) == 3
        # Lấy 3 cảnh báo cuối cùng
        assert history[0]["person_count"] >= 13

    def test_get_alert_stats_with_multiple_severity_alerts(self, alert_system):
        """TC14: Test stats sau 7 alerts với phân bố severity cụ thể"""
        alert_system.set_alert_cooldown(0)

        # Tạo 7 alerts: 2 warning, 2 critical, 3 emergency
        alert_system.check_alert(11)  # warning
        time.sleep(0.01)
        alert_system.check_alert(12)  # warning
        time.sleep(0.01)
        alert_system.check_alert(13)  # critical
        time.sleep(0.01)
        alert_system.check_alert(14)  # critical
        time.sleep(0.01)
        alert_system.check_alert(16)  # emergency
        time.sleep(0.01)
        alert_system.check_alert(17)  # emergency
        time.sleep(0.01)
        alert_system.check_alert(20)  # emergency

        stats = alert_system.get_alert_stats()

        assert stats["total_alerts"] == 7
        assert stats["max_person_count"] == 20
        assert stats["is_alert_active"] is True

        # Kiểm tra phân bố severity
        severity_counts = stats["severity_counts"]
        assert severity_counts["warning"] == 2
        assert severity_counts["critical"] == 2
        assert severity_counts["emergency"] == 3

    def test_save_alert_log_empty_history(self, alert_system, temp_log_file):
        """TC15: Test save_alert_log với lịch sử rỗng"""
        alert_system.save_alert_log(temp_log_file)

        assert os.path.exists(temp_log_file)

        with open(temp_log_file, "r", encoding="utf-8") as f:
            content = f.read()

        assert "=== LỊCH SỬ CẢNH BÁO ===" in content
        assert "Không có cảnh báo nào." in content

    def test_save_alert_log_multiple_alerts(self, alert_system, temp_log_file):
        """TC16: Test save_alert_log với nhiều cảnh báo"""
        alert_system.set_alert_cooldown(0)

        alert_system.check_alert(11)
        time.sleep(0.01)
        alert_system.check_alert(14)
        time.sleep(0.01)
        alert_system.check_alert(17)

        alert_system.save_alert_log(temp_log_file)

        with open(temp_log_file, "r", encoding="utf-8") as f:
            content = f.read()

        assert "Cảnh báo #1:" in content
        assert "Cảnh báo #2:" in content
        assert "Cảnh báo #3:" in content
        assert "Tổng số cảnh báo: 3" in content

    def test_set_max_count_changes_threshold(self, alert_system):
        """TC17: Test set_max_count thay đổi ngưỡng"""
        alert_system.set_max_count(20)

        assert alert_system.max_count == 20

        # Kiểm tra cảnh báo mới dùng ngưỡng mới
        result = alert_system.check_alert(15)
        assert result is None  # Không cảnh báo vì 15 < 20

        result = alert_system.check_alert(21)
        assert result is not None  # Cảnh báo vì 21 > 20

    def test_set_alert_cooldown_allows_new_alert_after_wait(self, alert_system):
        """TC18: Test set_alert_cooldown với thời gian chờ ngắn"""
        alert_system.set_alert_cooldown(1)  # 1 giây

        # Cảnh báo đầu tiên
        alert_system.check_alert(15)
        assert len(alert_system.alert_history) == 1

        # Đợi hết cooldown
        time.sleep(1.1)

        # Cảnh báo mới
        alert_system.check_alert(15)
        assert len(alert_system.alert_history) == 2

    def test_clear_alert_history_resets_state(self, alert_system):
        """TC19: Test clear_alert_history xóa lịch sử và reset state"""
        alert_system.check_alert(15)
        assert len(alert_system.alert_history) > 0
        assert alert_system.is_alert_active is True

        alert_system.clear_alert_history()

        assert len(alert_system.alert_history) == 0
        assert alert_system.is_alert_active is False

    def test_set_enabled_toggles_alert_system(self, alert_system):
        """TC20: Test set_enabled bật/tắt hệ thống"""
        # Tắt hệ thống
        alert_system.set_enabled(False)
        assert alert_system.enabled is False

        result = alert_system.check_alert(15)
        assert result is None

        # Bật lại hệ thống
        alert_system.set_enabled(True)
        assert alert_system.enabled is True

        result = alert_system.check_alert(15)
        assert result is not None
