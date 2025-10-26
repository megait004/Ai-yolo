"""
Module lưu dữ liệu thống kê vào file CSV
"""

import csv
import os
from datetime import datetime

import pandas as pd

from config.settings import CSV_FILENAME, DATA_DIR, SAVE_TO_CSV


class DataLogger:
    """
    Lớp lưu dữ liệu thống kê vào file CSV
    """

    def __init__(self, filename=None, enabled=SAVE_TO_CSV):
        """
        Khởi tạo data logger

        Args:
            filename (str): Tên file CSV để lưu dữ liệu
            enabled (bool): Bật/tắt chức năng lưu dữ liệu
        """
        self.filename = filename or str(DATA_DIR / CSV_FILENAME)
        self.enabled = enabled
        self.data_buffer = []

        # Tạo file CSV với header nếu chưa tồn tại
        if self.enabled and not os.path.exists(self.filename):
            self._create_csv_file()

    def _create_csv_file(self):
        """
        Tạo file CSV với header
        """
        try:
            with open(self.filename, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = [
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
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
            print(f"Đã tạo file CSV: {self.filename}")
        except Exception as e:
            print(f"Lỗi khi tạo file CSV: {e}")

    def log_data(self, stats):
        """
        Lưu dữ liệu thống kê vào buffer

        Args:
            stats (dict): Dictionary chứa thống kê
        """
        if not self.enabled:
            return

        try:
            # Tạo record mới
            record = {
                "timestamp": datetime.now().timestamp(),
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "person_count": stats.get("current_count", 0),
                "max_count": stats.get("max_count", 0),
                "average_count": round(stats.get("average_count", 0), 2),
                "total_detections": stats.get("total_detections", 0),
                "total_frames": stats.get("total_frames", 0),
                "frames_with_persons": stats.get("frames_with_persons", 0),
                "detection_rate": round(stats.get("detection_rate", 0), 3),
                "fps": round(stats.get("fps", 0), 2),
                "running_time": round(stats.get("running_time", 0), 2),
            }

            # Thêm vào buffer
            self.data_buffer.append(record)

        except Exception as e:
            print(f"Lỗi khi lưu dữ liệu vào buffer: {e}")

    def save_to_csv(self):
        """
        Lưu dữ liệu từ buffer vào file CSV
        """
        if not self.enabled or not self.data_buffer:
            return

        try:
            # Kiểm tra xem file có tồn tại không
            file_exists = os.path.exists(self.filename)

            with open(self.filename, "a", newline="", encoding="utf-8") as csvfile:
                fieldnames = [
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
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                # Ghi header nếu file mới tạo
                if not file_exists:
                    writer.writeheader()

                # Ghi dữ liệu
                for record in self.data_buffer:
                    writer.writerow(record)

            # Xóa buffer sau khi lưu
            self.data_buffer.clear()
            print(f"Đã lưu {len(self.data_buffer)} records vào {self.filename}")

        except Exception as e:
            print(f"Lỗi khi lưu dữ liệu vào CSV: {e}")

    def save_immediate(self, stats):
        """
        Lưu dữ liệu ngay lập tức vào file CSV

        Args:
            stats (dict): Dictionary chứa thống kê
        """
        if not self.enabled:
            return

        try:
            record = {
                "timestamp": datetime.now().timestamp(),
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "person_count": stats.get("current_count", 0),
                "max_count": stats.get("max_count", 0),
                "average_count": round(stats.get("average_count", 0), 2),
                "total_detections": stats.get("total_detections", 0),
                "total_frames": stats.get("total_frames", 0),
                "frames_with_persons": stats.get("frames_with_persons", 0),
                "detection_rate": round(stats.get("detection_rate", 0), 3),
                "fps": round(stats.get("fps", 0), 2),
                "running_time": round(stats.get("running_time", 0), 2),
            }

            file_exists = os.path.exists(self.filename)

            with open(self.filename, "a", newline="", encoding="utf-8") as csvfile:
                fieldnames = list(record.keys())
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                if not file_exists:
                    writer.writeheader()

                writer.writerow(record)

        except Exception as e:
            print(f"Lỗi khi lưu dữ liệu ngay lập tức: {e}")

    def load_data(self):
        """
        Đọc dữ liệu từ file CSV

        Returns:
            pandas.DataFrame: DataFrame chứa dữ liệu đã lưu
        """
        try:
            if os.path.exists(self.filename):
                df = pd.read_csv(self.filename)
                return df
            else:
                print(f"File {self.filename} không tồn tại")
                return pd.DataFrame()
        except Exception as e:
            print(f"Lỗi khi đọc dữ liệu từ CSV: {e}")
            return pd.DataFrame()

    def get_summary_stats(self):
        """
        Lấy thống kê tổng quan từ dữ liệu đã lưu

        Returns:
            dict: Dictionary chứa thống kê tổng quan
        """
        try:
            df = self.load_data()
            if df.empty:
                return {}

            summary = {
                "total_records": len(df),
                "max_person_count": df["person_count"].max(),
                "avg_person_count": round(df["person_count"].mean(), 2),
                "total_detections": (
                    df["total_detections"].iloc[-1] if len(df) > 0 else 0
                ),
                "avg_fps": round(df["fps"].mean(), 2),
                "total_running_time": df["running_time"].iloc[-1] if len(df) > 0 else 0,
                "first_record": df["datetime"].iloc[0] if len(df) > 0 else None,
                "last_record": df["datetime"].iloc[-1] if len(df) > 0 else None,
            }

            return summary

        except Exception as e:
            print(f"Lỗi khi tính thống kê tổng quan: {e}")
            return {}

    def clear_data(self):
        """
        Xóa tất cả dữ liệu trong file CSV
        """
        try:
            if os.path.exists(self.filename):
                os.remove(self.filename)
                print(f"Đã xóa file {self.filename}")
                # Tạo lại file với header
                self._create_csv_file()
        except Exception as e:
            print(f"Lỗi khi xóa dữ liệu: {e}")

    def export_to_excel(self, excel_filename=None):
        """
        Xuất dữ liệu CSV sang file Excel

        Args:
            excel_filename (str): Tên file Excel (mặc định là tên CSV + .xlsx)
        """
        try:
            if excel_filename is None:
                excel_filename = self.filename.replace(".csv", ".xlsx")

            df = self.load_data()
            if not df.empty:
                df.to_excel(excel_filename, index=False)
                print(f"Đã xuất dữ liệu sang {excel_filename}")
            else:
                print("Không có dữ liệu để xuất")

        except Exception as e:
            print(f"Lỗi khi xuất sang Excel: {e}")

    def set_enabled(self, enabled):
        """
        Bật/tắt chức năng lưu dữ liệu

        Args:
            enabled (bool): True để bật, False để tắt
        """
        self.enabled = enabled
        print(f"Data logging {'bật' if enabled else 'tắt'}")
