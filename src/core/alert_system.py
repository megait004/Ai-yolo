"""
Module hệ thống cảnh báo khi số lượng người vượt ngưỡng
"""

import time
from datetime import datetime

from config.settings import ALERT_ENABLED, MAX_PERSON_COUNT


class AlertSystem:
    """
    Lớp quản lý hệ thống cảnh báo
    """

    def __init__(self, max_count=MAX_PERSON_COUNT, enabled=ALERT_ENABLED):
        """
        Khởi tạo hệ thống cảnh báo

        Args:
            max_count (int): Số lượng người tối đa cho phép
            enabled (bool): Bật/tắt hệ thống cảnh báo
        """
        self.max_count = max_count
        self.enabled = enabled
        self.alert_history = []
        self.last_alert_time = 0
        self.alert_cooldown = 5  # Thời gian chờ giữa các cảnh báo (giây)
        self.is_alert_active = False

    def check_alert(self, person_count):
        """
        Kiểm tra và xử lý cảnh báo

        Args:
            person_count (int): Số lượng người hiện tại

        Returns:
            dict: Thông tin cảnh báo hoặc None nếu không có cảnh báo
        """
        if not self.enabled:
            return None

        current_time = time.time()

        # Kiểm tra xem có vượt ngưỡng không
        if person_count > self.max_count:
            # Kiểm tra cooldown để tránh spam cảnh báo
            if current_time - self.last_alert_time >= self.alert_cooldown:
                alert_info = self._create_alert(person_count, current_time)
                self.alert_history.append(alert_info)
                self.last_alert_time = current_time
                self.is_alert_active = True
                return alert_info
            else:
                # Vẫn trong thời gian cảnh báo
                return {
                    "type": "warning",
                    "message": f"Cảnh báo: {person_count} người (vượt ngưỡng {self.max_count})",
                    "person_count": person_count,
                    "timestamp": current_time,
                    "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "is_active": True,
                }
        else:
            # Số lượng người trong ngưỡng cho phép
            if self.is_alert_active:
                # Kết thúc cảnh báo
                self.is_alert_active = False
                return {
                    "type": "info",
                    "message": f"Số lượng người đã trở về mức bình thường: {person_count}",
                    "person_count": person_count,
                    "timestamp": current_time,
                    "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "is_active": False,
                }

        return None

    def _create_alert(self, person_count, timestamp):
        """
        Tạo thông tin cảnh báo

        Args:
            person_count (int): Số lượng người
            timestamp (float): Thời gian cảnh báo

        Returns:
            dict: Thông tin cảnh báo
        """
        severity = self._get_alert_severity(person_count)

        return {
            "type": severity,
            "message": self._get_alert_message(person_count, severity),
            "person_count": person_count,
            "max_count": self.max_count,
            "excess_count": person_count - self.max_count,
            "timestamp": timestamp,
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "is_active": True,
        }

    def _get_alert_severity(self, person_count):
        """
        Xác định mức độ nghiêm trọng của cảnh báo

        Args:
            person_count (int): Số lượng người

        Returns:
            str: Mức độ nghiêm trọng ('warning', 'critical', 'emergency')
        """
        excess = person_count - self.max_count

        if excess <= 2:
            return "warning"
        elif excess <= 5:
            return "critical"
        else:
            return "emergency"

    def _get_alert_message(self, person_count, severity):
        """
        Tạo thông điệp cảnh báo

        Args:
            person_count (int): Số lượng người
            severity (str): Mức độ nghiêm trọng

        Returns:
            str: Thông điệp cảnh báo
        """
        excess = person_count - self.max_count

        messages = {
            "warning": f"Cảnh báo: Phát hiện {person_count} người (vượt {excess} so với ngưỡng {self.max_count})",
            "critical": f"Cảnh báo nghiêm trọng: {person_count} người (vượt {excess} so với ngưỡng {self.max_count})",
            "emergency": f"Cảnh báo khẩn cấp: {person_count} người (vượt {excess} so với ngưỡng {self.max_count})",
        }

        return messages.get(severity, messages["warning"])

    def get_alert_history(self, limit=None):
        """
        Lấy lịch sử cảnh báo

        Args:
            limit (int): Số lượng cảnh báo gần nhất (None để lấy tất cả)

        Returns:
            list: Danh sách lịch sử cảnh báo
        """
        if limit is None:
            return self.alert_history.copy()
        else:
            return (
                self.alert_history[-limit:]
                if len(self.alert_history) > limit
                else self.alert_history.copy()
            )

    def get_alert_stats(self):
        """
        Lấy thống kê cảnh báo

        Returns:
            dict: Thống kê cảnh báo
        """
        if not self.alert_history:
            return {
                "total_alerts": 0,
                "active_alerts": 0,
                "max_person_count": 0,
                "last_alert_time": None,
            }

        total_alerts = len(self.alert_history)
        active_alerts = sum(
            1 for alert in self.alert_history if alert.get("is_active", False)
        )
        max_person_count = max(alert["person_count"] for alert in self.alert_history)
        last_alert_time = (
            self.alert_history[-1]["datetime"] if self.alert_history else None
        )

        # Thống kê theo mức độ nghiêm trọng
        severity_counts = {}
        for alert in self.alert_history:
            severity = alert.get("type", "unknown")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        return {
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "max_person_count": max_person_count,
            "last_alert_time": last_alert_time,
            "severity_counts": severity_counts,
            "is_alert_active": self.is_alert_active,
        }

    def set_max_count(self, max_count):
        """
        Thay đổi ngưỡng tối đa

        Args:
            max_count (int): Số lượng người tối đa mới
        """
        self.max_count = max_count
        print(f"Đã thay đổi ngưỡng tối đa thành: {max_count}")

    def set_enabled(self, enabled):
        """
        Bật/tắt hệ thống cảnh báo

        Args:
            enabled (bool): True để bật, False để tắt
        """
        self.enabled = enabled
        print(f"Hệ thống cảnh báo {'bật' if enabled else 'tắt'}")

    def set_alert_cooldown(self, cooldown):
        """
        Thay đổi thời gian chờ giữa các cảnh báo

        Args:
            cooldown (int): Thời gian chờ (giây)
        """
        self.alert_cooldown = cooldown
        print(f"Đã thay đổi thời gian chờ cảnh báo thành: {cooldown} giây")

    def clear_alert_history(self):
        """
        Xóa lịch sử cảnh báo
        """
        self.alert_history.clear()
        self.is_alert_active = False
        print("Đã xóa lịch sử cảnh báo")

    def save_alert_log(self, filename="alert_log.txt"):
        """
        Lưu lịch sử cảnh báo vào file text

        Args:
            filename (str): Tên file để lưu
        """
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write("=== LỊCH SỬ CẢNH BÁO ===\n\n")

                if not self.alert_history:
                    f.write("Không có cảnh báo nào.\n")
                else:
                    for i, alert in enumerate(self.alert_history, 1):
                        f.write(f"Cảnh báo #{i}:\n")
                        f.write(f"  Thời gian: {alert['datetime']}\n")
                        f.write(f"  Loại: {alert['type']}\n")
                        f.write(f"  Thông điệp: {alert['message']}\n")
                        f.write(f"  Số người: {alert['person_count']}\n")
                        f.write(
                            f"  Trạng thái: {'Đang hoạt động' if alert.get('is_active', False) else 'Đã kết thúc'}\n"
                        )
                        f.write("\n")

                # Thêm thống kê
                stats = self.get_alert_stats()
                f.write("=== THỐNG KÊ ===\n")
                f.write(f"Tổng số cảnh báo: {stats['total_alerts']}\n")
                f.write(f"Số lượng người tối đa: {stats['max_person_count']}\n")
                f.write(f"Cảnh báo cuối: {stats['last_alert_time']}\n")

            print(f"Đã lưu lịch sử cảnh báo vào {filename}")

        except Exception as e:
            print(f"Lỗi khi lưu lịch sử cảnh báo: {e}")
