"""
Module đếm số lượng người và quản lý thống kê
"""

import time
from collections import deque
from datetime import datetime

import numpy as np


class PersonCounter:
    """
    Lớp đếm và quản lý thống kê số lượng người
    """

    def __init__(self, max_history=100):
        """
        Khởi tạo counter

        Args:
            max_history (int): Số lượng frame tối đa để lưu lịch sử
        """
        self.current_count = 0
        self.max_count = 0
        self.total_detections = 0
        self.frame_count = 0
        self.start_time = time.time()

        # Lưu lịch sử số lượng người
        self.count_history = deque(maxlen=max_history)
        self.timestamp_history = deque(maxlen=max_history)

        # Thống kê
        self.stats = {
            "total_frames": 0,
            "frames_with_persons": 0,
            "average_count": 0.0,
            "max_count_reached": 0,
        }

    def update_count(self, detections):
        """
        Cập nhật số lượng người hiện tại

        Args:
            detections (list): Danh sách các detection của người

        Returns:
            int: Số lượng người hiện tại
        """
        self.current_count = len(detections)
        self.total_detections += self.current_count
        self.frame_count += 1

        # Cập nhật max count
        if self.current_count > self.max_count:
            self.max_count = self.current_count

        # Lưu vào lịch sử
        self.count_history.append(self.current_count)
        self.timestamp_history.append(datetime.now())

        # Cập nhật thống kê
        self._update_stats()

        return self.current_count

    def _update_stats(self):
        """
        Cập nhật các thống kê
        """
        self.stats["total_frames"] = self.frame_count

        if self.current_count > 0:
            self.stats["frames_with_persons"] += 1

        # Tính trung bình số lượng người
        if len(self.count_history) > 0:
            self.stats["average_count"] = np.mean(list(self.count_history))

        # Cập nhật max count đã đạt được
        self.stats["max_count_reached"] = self.max_count

    def get_current_count(self):
        """
        Lấy số lượng người hiện tại

        Returns:
            int: Số lượng người hiện tại
        """
        return self.current_count

    def get_max_count(self):
        """
        Lấy số lượng người tối đa đã phát hiện

        Returns:
            int: Số lượng người tối đa
        """
        return self.max_count

    def get_average_count(self):
        """
        Lấy số lượng người trung bình

        Returns:
            float: Số lượng người trung bình
        """
        return self.stats["average_count"]

    def get_running_time(self):
        """
        Lấy thời gian chạy của hệ thống

        Returns:
            float: Thời gian chạy (giây)
        """
        return time.time() - self.start_time

    def get_fps(self):
        """
        Lấy FPS hiện tại

        Returns:
            float: FPS
        """
        running_time = self.get_running_time()
        if running_time > 0:
            return self.frame_count / running_time
        return 0.0

    def get_detection_rate(self):
        """
        Lấy tỷ lệ frame có phát hiện người

        Returns:
            float: Tỷ lệ (0-1)
        """
        if self.stats["total_frames"] > 0:
            return self.stats["frames_with_persons"] / self.stats["total_frames"]
        return 0.0

    def get_all_stats(self):
        """
        Lấy tất cả thống kê

        Returns:
            dict: Dictionary chứa tất cả thống kê
        """
        return {
            "current_count": self.current_count,
            "max_count": self.max_count,
            "average_count": self.get_average_count(),
            "total_detections": self.total_detections,
            "total_frames": self.stats["total_frames"],
            "frames_with_persons": self.stats["frames_with_persons"],
            "detection_rate": self.get_detection_rate(),
            "fps": self.get_fps(),
            "running_time": self.get_running_time(),
        }

    def get_count_history(self):
        """
        Lấy lịch sử số lượng người

        Returns:
            tuple: (counts, timestamps)
        """
        return list(self.count_history), list(self.timestamp_history)

    def reset_stats(self):
        """
        Reset tất cả thống kê
        """
        self.current_count = 0
        self.max_count = 0
        self.total_detections = 0
        self.frame_count = 0
        self.start_time = time.time()

        self.count_history.clear()
        self.timestamp_history.clear()

        self.stats = {
            "total_frames": 0,
            "frames_with_persons": 0,
            "average_count": 0.0,
            "max_count_reached": 0,
        }
