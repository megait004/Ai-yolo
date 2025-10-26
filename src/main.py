"""
Ứng dụng chính - Hệ thống nhận dạng và đếm người theo thời gian thực bằng YOLOv8
"""

import argparse
import time

import cv2

from config.settings import (
    DEFAULT_CAMERA_INDEX,
    FPS,
    SAVE_INTERVAL,
    VIDEO_HEIGHT,
    VIDEO_WIDTH,
)

# Import các module đã tạo
from src.core import AlertSystem, DataLogger, PersonCounter, PersonDetector, Visualizer


class PersonDetectionApp:
    """
    Lớp ứng dụng chính tích hợp tất cả các chức năng
    """

    def __init__(self, source=0, save_data=True):
        """
        Khởi tạo ứng dụng

        Args:
            source: Nguồn video (0 cho webcam, hoặc đường dẫn file video)
            save_data (bool): Có lưu dữ liệu hay không
        """
        self.source = source
        self.running = False

        # Khởi tạo các component
        print("Đang khởi tạo hệ thống...")
        self.detector = PersonDetector()
        self.counter = PersonCounter()
        self.visualizer = Visualizer()
        self.data_logger = DataLogger(enabled=save_data)
        self.alert_system = AlertSystem()

        # Khởi tạo video capture
        self.cap = None
        self.last_save_time = time.time()

        print("Hệ thống đã sẵn sàng!")

    def initialize_camera(self):
        """
        Khởi tạo camera hoặc video source
        """
        try:
            self.cap = cv2.VideoCapture(self.source)

            if not self.cap.isOpened():
                raise Exception(f"Không thể mở video source: {self.source}")

            # Thiết lập kích thước frame
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, VIDEO_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, VIDEO_HEIGHT)
            self.cap.set(cv2.CAP_PROP_FPS, FPS)

            print(f"Đã khởi tạo video source: {self.source}")
            return True

        except Exception as e:
            print(f"Lỗi khi khởi tạo camera: {e}")
            return False

    def process_frame(self, frame):
        """
        Xử lý một frame

        Args:
            frame: Frame đầu vào

        Returns:
            tuple: (processed_frame, stats, alert_info)
        """
        # Tiền xử lý frame
        processed_frame = self.detector.preprocess_frame(frame)

        # Phát hiện người
        detections = self.detector.detect_persons(processed_frame)

        # Cập nhật số lượng người
        person_count = self.counter.update_count(detections)

        # Lấy thống kê
        stats = self.counter.get_all_stats()

        # Kiểm tra cảnh báo
        alert_info = self.alert_system.check_alert(person_count)

        # Vẽ kết quả lên frame
        display_frame = self.visualizer.draw_detections(
            processed_frame, detections, person_count
        )

        # Vẽ thống kê
        display_frame = self.visualizer.draw_stats(display_frame, stats)

        # Vẽ cảnh báo nếu có
        if alert_info:
            display_frame = self.visualizer.draw_alert(
                display_frame, alert_info["message"], alert_info["type"]
            )

        # Vẽ chú thích
        display_frame = self.visualizer.create_legend(display_frame)

        return display_frame, stats, alert_info

    def save_data_if_needed(self, stats):
        """
        Lưu dữ liệu nếu đã đến thời gian

        Args:
            stats (dict): Thống kê hiện tại
        """
        current_time = time.time()
        if current_time - self.last_save_time >= SAVE_INTERVAL:
            self.data_logger.save_immediate(stats)
            self.last_save_time = current_time

    def run(self):
        """
        Chạy ứng dụng chính
        """
        if not self.initialize_camera():
            return

        self.running = True
        print("\n=== HỆ THỐNG NHẬN DẠNG VÀ ĐẾM NGƯỜI ===")
        print("Nhấn 'q' để thoát")
        print("Nhấn 'r' để reset thống kê")
        print("Nhấn 's' để lưu dữ liệu ngay")
        print("Nhấn 'h' để hiển thị trợ giúp")
        print("=" * 50)

        try:
            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    print("Không thể đọc frame từ video source")
                    break

                # Xử lý frame
                display_frame, stats, alert_info = self.process_frame(frame)

                # Lưu dữ liệu nếu cần
                self.save_data_if_needed(stats)

                # Hiển thị frame
                cv2.imshow("Person Detection & Counting", display_frame)

                # Xử lý phím nhấn
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
                elif key == ord("r"):
                    self.reset_system()
                elif key == ord("s"):
                    self.data_logger.save_immediate(stats)
                    print("Đã lưu dữ liệu ngay lập tức")
                elif key == ord("h"):
                    self.show_help()
                elif key == ord("a"):
                    self.toggle_alert_system()
                elif key == ord("d"):
                    self.toggle_data_logging()

                # In thông tin cảnh báo nếu có
                if alert_info:
                    print(f"[{alert_info['datetime']}] {alert_info['message']}")

        except KeyboardInterrupt:
            print("\nĐang dừng hệ thống...")

        finally:
            self.cleanup()

    def reset_system(self):
        """
        Reset hệ thống
        """
        self.counter.reset_stats()
        self.alert_system.clear_alert_history()
        print("Đã reset hệ thống")

    def toggle_alert_system(self):
        """
        Bật/tắt hệ thống cảnh báo
        """
        current_status = self.alert_system.enabled
        self.alert_system.set_enabled(not current_status)

    def toggle_data_logging(self):
        """
        Bật/tắt lưu dữ liệu
        """
        current_status = self.data_logger.enabled
        self.data_logger.set_enabled(not current_status)

    def show_help(self):
        """
        Hiển thị trợ giúp
        """
        help_text = """
=== TRỢ GIÚP ===
q - Thoát ứng dụng
r - Reset thống kê
s - Lưu dữ liệu ngay lập tức
h - Hiển thị trợ giúp này
a - Bật/tắt hệ thống cảnh báo
d - Bật/tắt lưu dữ liệu

=== THÔNG TIN HỆ THỐNG ===
"""
        print(help_text)

        # Hiển thị thông tin mô hình
        model_info = self.detector.get_model_info()
        print("Thông tin mô hình:")
        for key, value in model_info.items():
            print(f"  {key}: {value}")

        # Hiển thị thống kê hiện tại
        stats = self.counter.get_all_stats()
        print("\nThống kê hiện tại:")
        for key, value in stats.items():
            print(f"  {key}: {value}")

    def cleanup(self):
        """
        Dọn dẹp tài nguyên
        """
        self.running = False

        if self.cap:
            self.cap.release()

        cv2.destroyAllWindows()

        # Lưu dữ liệu cuối cùng
        if self.data_logger.enabled:
            final_stats = self.counter.get_all_stats()
            self.data_logger.save_immediate(final_stats)
            print("Đã lưu dữ liệu cuối cùng")

        # Hiển thị thống kê cuối
        self.show_final_stats()

        print("Hệ thống đã dừng")

    def show_final_stats(self):
        """
        Hiển thị thống kê cuối cùng
        """
        print("\n=== THỐNG KÊ CUỐI CÙNG ===")

        # Thống kê từ counter
        stats = self.counter.get_all_stats()
        print("Thống kê tổng quan:")
        for key, value in stats.items():
            print(f"  {key}: {value}")

        # Thống kê cảnh báo
        alert_stats = self.alert_system.get_alert_stats()
        print("\nThống kê cảnh báo:")
        for key, value in alert_stats.items():
            print(f"  {key}: {value}")

        # Thống kê từ file CSV
        if self.data_logger.enabled:
            csv_stats = self.data_logger.get_summary_stats()
            if csv_stats:
                print("\nThống kê từ dữ liệu đã lưu:")
                for key, value in csv_stats.items():
                    print(f"  {key}: {value}")


def main():
    """
    Hàm main
    """
    parser = argparse.ArgumentParser(
        description="Hệ thống nhận dạng và đếm người bằng YOLOv8"
    )
    parser.add_argument(
        "--source",
        type=str,
        default=str(DEFAULT_CAMERA_INDEX),
        help="Nguồn video (0 cho webcam, hoặc đường dẫn file video)",
    )
    parser.add_argument(
        "--no-save", action="store_true", help="Không lưu dữ liệu vào CSV"
    )

    args = parser.parse_args()

    # Xử lý source
    if args.source.isdigit():
        source = int(args.source)
    else:
        source = args.source

    # Tạo và chạy ứng dụng
    app = PersonDetectionApp(source=source, save_data=not args.no_save)
    app.run()


if __name__ == "__main__":
    main()
