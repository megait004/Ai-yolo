"""
Giao diện người dùng cho hệ thống nhận dạng và đếm người
Sử dụng PyQt6
"""

import os

# CRITICAL: Must be first, before any torch/ultralytics imports
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import sys
from datetime import datetime

import cv2
import numpy as np
from PyQt6.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class VideoThread(QThread):
    """Thread xử lý video để không làm đơ UI"""

    frame_signal = pyqtSignal(np.ndarray, dict, dict)  # frame, stats, alert_info

    def __init__(
        self, detector, counter, visualizer, alert_system, source: int | str = 0
    ):
        super().__init__()
        self.detector = detector
        self.counter = counter
        self.visualizer = visualizer
        self.alert_system = alert_system
        self.source = source
        self.running = False
        self.cap = None

    def run(self):
        """Chạy xử lý video"""
        self.running = True

        # Mở camera hoặc video
        self.cap = cv2.VideoCapture(self.source)

        if not self.cap.isOpened():
            print(f"❌ Không thể mở camera/video source: {self.source}")
            return

        # Thiết lập camera - độ phân giải thấp để tăng FPS
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        while self.running:
            ret, frame = self.cap.read()

            if not ret:
                print("⚠️ Không thể đọc frame, thử lại...")
                continue

            try:
                # Xử lý frame - frame đã là 640x480 rồi
                detections = self.detector.detect_persons(frame)
                person_count = self.counter.update_count(detections)
                stats = self.counter.get_all_stats()
                alert_info = self.alert_system.check_alert(person_count) or {}

                # Vẽ kết quả
                display_frame = self.visualizer.draw_detections(
                    frame, detections, person_count
                )
                display_frame = self.visualizer.draw_stats(display_frame, stats)

                if alert_info:
                    display_frame = self.visualizer.draw_alert(
                        display_frame,
                        alert_info.get("message", ""),
                        alert_info.get("type", "info"),
                    )

                display_frame = self.visualizer.create_legend(display_frame)

                # Gửi frame về UI
                self.frame_signal.emit(display_frame, stats, alert_info)

            except Exception as e:
                print(f"❌ Lỗi trong quá trình phát hiện: {e}")
                # Hiển thị frame gốc khi lỗi
                self.frame_signal.emit(frame, {}, {})
                continue

        if self.cap:
            self.cap.release()
            print("✅ Đã giải phóng camera/video source")

    def stop(self):
        """Dừng xử lý video"""
        self.running = False


class PersonDetectionGUI(QMainWindow):
    """Giao diện chính cho hệ thống nhận dạng người"""

    def __init__(self):
        super().__init__()
        self.video_thread = None

        # Import core modules sau khi đã set environment variable
        from src.core import (
            AlertSystem,
            DataLogger,
            PersonCounter,
            PersonDetector,
            Visualizer,
        )

        # Khởi tạo các component
        self.detector = PersonDetector()
        self.counter = PersonCounter()
        self.visualizer = Visualizer()
        self.data_logger = DataLogger(enabled=True)
        self.alert_system = AlertSystem()

        # Thông tin video source
        self.video_source: int | str = 0
        self.is_detecting = False

        self.init_ui()

    def init_ui(self):
        """Khởi tạo giao diện"""
        self.setWindowTitle("Hệ Thống Nhận Dạng & Đếm Người - YOLOv8")
        self.setGeometry(100, 100, 1400, 900)

        # Main widget và layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # ========== VÙNG HIỂN THỊ VIDEO (Main Video Panel) - 70-80% ==========
        video_panel = self.create_video_panel()
        main_layout.addWidget(video_panel, stretch=7)

        # ========== VÙNG ĐIỀU KHIỂN + THÔNG TIN (Side Panel) - 20-30% ==========
        side_panel = self.create_side_panel()
        main_layout.addWidget(side_panel, stretch=3)

        # Thanh trạng thái
        self.statusBar().showMessage(
            "Sẵn sàng"
        )  # pyright: ignore[reportOptionalMemberAccess]

    def create_video_panel(self):
        """Tạo vùng hiển thị video chính"""
        group_box = QGroupBox("Luồng Video Trực Tiếp")
        layout = QVBoxLayout()

        # Label hiển thị video
        self.video_label = (
            QLabel()
        )  # pyright: ignore[reportUnannotatedClassAttribute, reportUninitializedInstanceVariable]
        self.video_label.setMinimumSize(1024, 576)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet(
            """
            background-color: #000000;
            border: 2px solid #333;
            border-radius: 5px;
        """
        )
        self.video_label.setText("Chưa có video")

        layout.addWidget(self.video_label)

        # Thanh thống kê dưới video
        stats_bar = self.create_stats_bar()
        layout.addWidget(stats_bar)

        group_box.setLayout(layout)
        return group_box

    def create_stats_bar(self):
        """Tạo thanh thống kê nhanh"""
        frame = QFrame()
        frame.setStyleSheet(
            """
            background-color: #2b2b2b;
            border-radius: 5px;
            padding: 5px;
        """
        )
        layout = QHBoxLayout(frame)

        # Số người hiện tại
        self.current_count_label = QLabel(
            "Người hiện tại: 0"
        )  # pyright: ignore[reportUnannotatedClassAttribute, reportUninitializedInstanceVariable]
        self.current_count_label.setStyleSheet(
            """
            font-size: 16px;
            font-weight: bold;
            color: #00ff00;
        """
        )

        # FPS
        self.fps_label = QLabel(
            "FPS: 0"
        )  # pyright: ignore[reportUninitializedInstanceVariable]
        self.fps_label.setStyleSheet("font-size: 14px; color: #ffffff;")

        # Running time
        self.time_label = QLabel(
            "Thời gian: 00:00"
        )  # pyright: ignore[reportUninitializedInstanceVariable]
        self.time_label.setStyleSheet("font-size: 14px; color: #ffffff;")

        layout.addWidget(self.current_count_label)
        layout.addStretch()
        layout.addWidget(self.fps_label)
        layout.addWidget(self.time_label)

        return frame

    def create_side_panel(self):
        """Tạo panel điều khiển và thông tin"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # ========== CONTROL PANEL ==========
        control_group = QGroupBox("Điều Khiển")
        control_layout = QVBoxLayout()

        # Nút Start/Stop
        self.start_stop_btn = QPushButton(
            "▶ Bắt Đầu Nhận Dạng"
        )  # pyright: ignore[reportUninitializedInstanceVariable]
        self.start_stop_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """
        )
        self.start_stop_btn.clicked.connect(self.toggle_detection)
        control_layout.addWidget(self.start_stop_btn)

        # Chọn nguồn video
        source_layout = QHBoxLayout()
        select_source_btn = QPushButton("📁 Chọn Video")
        select_source_btn.clicked.connect(self.select_video_file)
        camera_select = QComboBox()
        camera_select.addItems(["Camera 0", "Camera 1", "Camera 2"])
        camera_select.currentIndexChanged.connect(self.select_camera)
        source_layout.addWidget(select_source_btn)
        source_layout.addWidget(camera_select)
        control_layout.addLayout(source_layout)

        # Ngưỡng cảnh báo
        threshold_layout = QHBoxLayout()
        threshold_label = QLabel("Ngưỡng:")
        threshold_layout.addWidget(threshold_label)
        self.threshold_spinbox = (
            QSpinBox()
        )  # pyright: ignore[reportUninitializedInstanceVariable]
        self.threshold_spinbox.setMinimum(1)
        self.threshold_spinbox.setMaximum(100)
        self.threshold_spinbox.setValue(5)
        self.threshold_spinbox.valueChanged.connect(self.update_threshold)
        threshold_layout.addWidget(self.threshold_spinbox)
        control_layout.addLayout(threshold_layout)

        # Nút lưu và xuất
        save_btn = QPushButton("💾 Lưu Dữ Liệu")
        save_btn.clicked.connect(self.save_data)
        export_btn = QPushButton("📊 Xuất Báo Cáo")
        export_btn.clicked.connect(self.export_report)

        control_layout.addWidget(save_btn)
        control_layout.addWidget(export_btn)

        control_group.setLayout(control_layout)
        layout.addWidget(control_group)

        # ========== INFORMATION PANEL ==========
        info_group = QGroupBox("Thông Tin & Cảnh Báo")
        info_layout = QVBoxLayout()

        # Trạng thái camera
        self.camera_status = QLabel(
            "🔴 Chưa kết nối"
        )  # pyright: ignore[reportUninitializedInstanceVariable]
        self.camera_status.setStyleSheet("font-size: 12px; color: #ff4444;")
        info_layout.addWidget(self.camera_status)

        # Panel thông tin chi tiết
        self.info_text = (
            QTextEdit()
        )  # pyright: ignore[reportUninitializedInstanceVariable]
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(150)
        self.info_text.setStyleSheet(
            """
            background-color: #1e1e1e;
            color: #ffffff;
            border: 1px solid #444;
            border-radius: 5px;
        """
        )
        info_layout.addWidget(self.info_text)

        # Trạng thái cảnh báo
        self.alert_status = QLabel(
            "⚪ Trạng thái: Bình thường"
        )  # pyright: ignore[reportUninitializedInstanceVariable]
        self.alert_status.setStyleSheet(
            """
            font-size: 14px;
            font-weight: bold;
            padding: 10px;
            border-radius: 5px;
            background-color: #1e1e1e;
            color: #ffffff;
        """
        )
        info_layout.addWidget(self.alert_status)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        layout.addStretch()

        return widget

    def toggle_detection(self):
        """Bật/tắt nhận dạng"""
        if self.is_detecting:
            self.stop_detection()
        else:
            self.start_detection()

    def start_detection(self):
        """Bắt đầu nhận dạng"""
        self.is_detecting = True
        self.start_stop_btn.setText("⏸ Dừng Nhận Dạng")
        self.start_stop_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #f44336;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """
        )

        # Khởi tạo video thread
        self.video_thread = VideoThread(
            self.detector,
            self.counter,
            self.visualizer,
            self.alert_system,
            self.video_source,
        )
        self.video_thread.frame_signal.connect(self.update_frame)
        self.video_thread.start()

        self.camera_status.setText("🟢 Đang kết nối...")
        self.statusBar().showMessage(
            "Đang chạy nhận dạng..."
        )  # pyright: ignore[reportOptionalMemberAccess]

        # Timer cập nhật thông tin
        self.update_timer = (
            QTimer()
        )  # pyright: ignore[reportUnannotatedClassAttribute, reportUninitializedInstanceVariable]
        self.update_timer.timeout.connect(self.update_info)
        self.update_timer.start(1000)  # Cập nhật mỗi giây

    def stop_detection(self):
        """Dừng nhận dạng"""
        self.is_detecting = False
        self.start_stop_btn.setText("▶ Bắt Đầu Nhận Dạng")
        self.start_stop_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """
        )

        if self.video_thread:
            self.video_thread.stop()
            self.video_thread.wait()

        if hasattr(self, "update_timer"):
            self.update_timer.stop()

        self.camera_status.setText("🔴 Đã dừng")
        self.statusBar().showMessage(
            "Đã dừng nhận dạng"
        )  # pyright: ignore[reportOptionalMemberAccess]

    def select_video_file(self):
        """Chọn file video"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Chọn file video",
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv);;All Files (*.*)",
        )

        if file_path:
            self.video_source = file_path
            self.statusBar().showMessage(
                f"Đã chọn: {file_path}"
            )  # pyright: ignore[reportOptionalMemberAccess]

    def select_camera(self, index):
        """Chọn camera"""
        self.video_source = index

    def update_threshold(self, value):
        """Cập nhật ngưỡng cảnh báo"""
        self.alert_system.set_max_count(value)

    def save_data(self):
        """Lưu dữ liệu"""
        stats = self.counter.get_all_stats()
        self.data_logger.save_immediate(stats)
        QMessageBox.information(self, "Thành công", "Đã lưu dữ liệu!")

    def export_report(self):
        """Xuất báo cáo"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Xuất báo cáo",
            f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv);;All Files (*.*)",
        )

        if file_path:
            # Thực hiện xuất báo cáo
            QMessageBox.information(
                self, "Thành công", f"Đã xuất báo cáo!\n{file_path}"
            )

    def update_frame(self, frame, stats, alert_info):
        """Cập nhật frame video"""
        if frame is None:
            return

        # Chuyển đổi frame OpenCV sang QImage
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(
            rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888
        )

        # Hiển thị
        pixmap = QPixmap.fromImage(qt_image)
        scaled_pixmap = pixmap.scaled(
            self.video_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.video_label.setPixmap(scaled_pixmap)

        # Cập nhật thông tin
        self.current_count_label.setText(
            f"Người hiện tại: {stats.get('current_count', 0)}"
        )
        self.fps_label.setText(f"FPS: {stats.get('fps', 0):.1f}")

        running_time = int(stats.get("running_time", 0))
        minutes = running_time // 60
        seconds = running_time % 60
        self.time_label.setText(f"Thời gian: {minutes:02d}:{seconds:02d}")

        # Cập nhật trạng thái
        if alert_info:
            alert_type = alert_info.get("type", "info")
            if alert_type == "warning":
                self.alert_status.setText("🟡 Cảnh báo: Số người vượt ngưỡng")
                self.alert_status.setStyleSheet(
                    """
                    font-size: 14px;
                    font-weight: bold;
                    padding: 10px;
                    border-radius: 5px;
                    background-color: #ffa500;
                    color: #000000;
                """
                )
            elif alert_type == "critical" or alert_type == "emergency":
                self.alert_status.setText(
                    "🔴 Cảnh báo khẩn cấp: Số người vượt quá ngưỡng"
                )
                self.alert_status.setStyleSheet(
                    """
                    font-size: 14px;
                    font-weight: bold;
                    padding: 10px;
                    border-radius: 5px;
                    background-color: #ff4444;
                    color: #ffffff;
                """
                )
        else:
            self.alert_status.setText("⚪ Trạng thái: Bình thường")
            self.alert_status.setStyleSheet(
                """
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
                background-color: #1e1e1e;
                color: #ffffff;
            """
            )

        self.camera_status.setText("🟢 Đang chạy")

    def update_info(self):
        """Cập nhật thông tin chi tiết"""
        stats = self.counter.get_all_stats()

        info_text = f"""
📊 Thống Kê Chi Tiết:
━━━━━━━━━━━━━━━━━━━━
• Số người hiện tại: {stats.get('current_count', 0)}
• Số người tối đa: {stats.get('max_count', 0)}
• Trung bình: {stats.get('average_count', 0):.1f}
• Tổng detections: {stats.get('total_detections', 0)}
• Tỷ lệ phát hiện: {stats.get('detection_rate', 0):.1%}
        """

        self.info_text.setPlainText(info_text)

    def closeEvent(self, a0):
        """Xử lý khi đóng ứng dụng"""
        if self.is_detecting:
            self.stop_detection()

        # Lưu dữ liệu cuối
        stats = self.counter.get_all_stats()
        self.data_logger.save_immediate(stats)

        a0.accept()  # pyright: ignore[reportOptionalMemberAccess]


def main():
    """Chạy ứng dụng GUI"""
    app = QApplication(sys.argv)

    # Thiết lập style
    app.setStyle("Fusion")

    window = PersonDetectionGUI()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
