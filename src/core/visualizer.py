"""
Module hiển thị kết quả trực quan với bounding box và thông tin
"""

import cv2
import numpy as np

from config.settings import (
    BOUNDING_BOX_COLOR,
    FONT_SCALE,
    FONT_THICKNESS,
    TEXT_COLOR,
)


class Visualizer:
    """
    Lớp hiển thị kết quả trực quan
    """

    def __init__(self):
        """
        Khởi tạo visualizer
        """
        self.bbox_color = BOUNDING_BOX_COLOR
        self.text_color = TEXT_COLOR
        self.font_scale = FONT_SCALE
        self.font_thickness = FONT_THICKNESS
        self.font = cv2.FONT_HERSHEY_SIMPLEX

    def draw_detections(self, frame, detections, person_count):
        """
        Vẽ bounding box và thông tin lên frame

        Args:
            frame (numpy.ndarray): Khung hình gốc
            detections (list): Danh sách các detection
            person_count (int): Số lượng người

        Returns:
            numpy.ndarray: Frame đã được vẽ thông tin
        """
        # Tạo bản sao của frame để không thay đổi frame gốc
        display_frame = frame.copy()

        # Vẽ bounding box cho mỗi detection
        for i, detection in enumerate(detections):
            bbox = detection["bbox"]
            confidence = detection["confidence"]

            x1, y1, x2, y2 = bbox

            # Vẽ bounding box
            cv2.rectangle(
                display_frame, (x1, y1), (x2, y2), self.bbox_color, self.font_thickness
            )

            # Tạo label với confidence
            label = f"Person {i+1}: {confidence:.2f}"

            # Tính kích thước text để vẽ background
            (text_width, text_height), baseline = cv2.getTextSize(
                label, self.font, self.font_scale, self.font_thickness
            )

            # Vẽ background cho text
            cv2.rectangle(
                display_frame,
                (x1, y1 - text_height - 10),
                (x1 + text_width, y1),
                self.bbox_color,
                -1,
            )

            # Vẽ text
            cv2.putText(
                display_frame,
                label,
                (x1, y1 - 5),
                self.font,
                self.font_scale,
                self.text_color,
                self.font_thickness,
            )

        # Vẽ thông tin tổng quan
        display_frame = self._draw_info_panel(
            display_frame, person_count, len(detections)
        )

        return display_frame

    def _draw_info_panel(self, frame, person_count, detection_count):
        """
        Vẽ panel thông tin tổng quan

        Args:
            frame (numpy.ndarray): Frame hiện tại
            person_count (int): Số lượng người
            detection_count (int): Số lượng detection

        Returns:
            numpy.ndarray: Frame với panel thông tin
        """
        # Tạo background cho panel thông tin
        panel_height = 80
        panel = np.zeros((panel_height, frame.shape[1], 3), dtype=np.uint8)
        panel[:] = (0, 0, 0)  # Màu đen

        # Thông tin hiển thị
        info_texts = [
            f"Person Count: {person_count}",
            f"Detections: {detection_count}",
            f"Frame Size: {frame.shape[1]}x{frame.shape[0]}",
        ]

        # Vẽ các dòng text
        y_offset = 25
        for text in info_texts:
            cv2.putText(
                panel,
                text,
                (10, y_offset),
                self.font,
                self.font_scale,
                self.text_color,
                self.font_thickness,
            )
            y_offset += 25

        # Ghép panel vào frame
        result_frame = np.vstack([panel, frame])

        return result_frame

    def draw_stats(self, frame, stats):
        """
        Vẽ thống kê chi tiết lên frame

        Args:
            frame (numpy.ndarray): Frame hiện tại
            stats (dict): Dictionary chứa thống kê

        Returns:
            numpy.ndarray: Frame với thống kê
        """
        # Tạo panel thống kê ở góc phải
        panel_width = 300
        panel_height = 200
        panel = np.zeros((panel_height, panel_width, 3), dtype=np.uint8)
        panel[:] = (50, 50, 50)  # Màu xám đậm

        # Thông tin thống kê
        stats_texts = [
            f"Max Count: {stats.get('max_count', 0)}",
            f"Avg Count: {stats.get('average_count', 0):.1f}",
            f"FPS: {stats.get('fps', 0):.1f}",
            f"Detection Rate: {stats.get('detection_rate', 0):.1%}",
            f"Running Time: {stats.get('running_time', 0):.1f}s",
        ]

        # Vẽ thống kê
        y_offset = 25
        for text in stats_texts:
            cv2.putText(panel, text, (10, y_offset), self.font, 0.5, self.text_color, 1)
            y_offset += 30

        # Đặt panel vào góc phải trên của frame
        frame_height, frame_width = frame.shape[:2]
        start_y = 0
        start_x = frame_width - panel_width

        # Đảm bảo panel không vượt quá kích thước frame
        if start_x >= 0 and start_y + panel_height <= frame_height:
            frame[start_y : start_y + panel_height, start_x : start_x + panel_width] = (
                panel
            )

        return frame

    def draw_alert(self, frame, message, alert_type="warning"):
        """
        Vẽ cảnh báo lên frame

        Args:
            frame (numpy.ndarray): Frame hiện tại
            message (str): Thông điệp cảnh báo
            alert_type (str): Loại cảnh báo ("warning", "error", "info")

        Returns:
            numpy.ndarray: Frame với cảnh báo
        """
        # Màu sắc theo loại cảnh báo
        colors = {
            "warning": (0, 255, 255),  # Vàng
            "error": (0, 0, 255),  # Đỏ
            "info": (255, 0, 0),  # Xanh dương
        }

        alert_color = colors.get(alert_type, colors["warning"])

        # Tạo background cho cảnh báo
        text_size = cv2.getTextSize(
            message, self.font, self.font_scale + 0.3, self.font_thickness + 1
        )[0]
        text_width, text_height = text_size

        # Vị trí cảnh báo (giữa màn hình)
        frame_height, frame_width = frame.shape[:2]
        x = (frame_width - text_width) // 2
        y = (frame_height + text_height) // 2

        # Vẽ background
        cv2.rectangle(
            frame,
            (x - 10, y - text_height - 10),
            (x + text_width + 10, y + 10),
            alert_color,
            -1,
        )

        # Vẽ text cảnh báo
        cv2.putText(
            frame,
            message,
            (x, y),
            self.font,
            self.font_scale + 0.3,
            self.text_color,
            self.font_thickness + 1,
        )

        return frame

    def create_legend(self, frame):
        """
        Tạo chú thích cho các màu sắc và ký hiệu

        Args:
            frame (numpy.ndarray): Frame hiện tại

        Returns:
            numpy.ndarray: Frame với chú thích
        """
        legend_items = [
            ("Green Box", self.bbox_color, "Detected Person"),
            ("White Text", self.text_color, "Information"),
        ]

        # Vị trí chú thích (góc trái dưới)
        start_x = 10
        start_y = frame.shape[0] - 60

        for i, (item_name, color, description) in enumerate(legend_items):
            y_pos = start_y + i * 20

            # Vẽ màu mẫu
            cv2.rectangle(
                frame, (start_x, y_pos - 10), (start_x + 15, y_pos + 5), color, -1
            )

            # Vẽ text mô tả
            cv2.putText(
                frame,
                f"{item_name}: {description}",
                (start_x + 20, y_pos),
                self.font,
                0.4,
                self.text_color,
                1,
            )

        return frame
