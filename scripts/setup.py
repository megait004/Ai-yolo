"""
Script cài đặt và thiết lập hệ thống
"""

import os
import sys
import subprocess
from ultralytics import YOLO


def install_requirements():
    """
    Cài đặt các thư viện cần thiết
    """
    print("=== CÀI ĐẶT THƯ VIỆN ===")

    try:
        # Nâng cấp pip trước
        print("Đang nâng cấp pip...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])

        # Cài đặt numpy trước (phiên bản cố định)
        print("Đang cài đặt numpy...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy==1.24.3"])

        # Cài đặt các thư viện còn lại
        print("Đang cài đặt các thư viện còn lại...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

        print("✓ Đã cài đặt thành công các thư viện")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Lỗi khi cài đặt thư viện: {e}")
        print("Vui lòng chạy: python fix_installation.py để sửa lỗi")
        return False


def download_yolo_model():
    """
    Tải mô hình YOLOv8
    """
    print("=== TẢI MÔ HÌNH YOLOv8 ===")

    try:
        # Tải mô hình YOLOv8n (nano) - nhẹ nhất
        print("Đang tải mô hình YOLOv8n...")
        model = YOLO("yolov8n.pt")
        print("✓ Đã tải thành công mô hình YOLOv8n")

        # Test mô hình
        print("Đang test mô hình...")
        # Tạo một ảnh test đơn giản
        import numpy as np
        test_image = np.zeros((640, 640, 3), dtype=np.uint8)
        results = model(test_image, verbose=False)
        print("✓ Mô hình hoạt động bình thường")

        return True

    except Exception as e:
        print(f"✗ Lỗi khi tải mô hình: {e}")
        return False


def create_directories():
    """
    Tạo các thư mục cần thiết
    """
    print("=== TẠO THƯ MỤC ===")

    directories = [
        "data",
        "output",
        "logs",
        "models"
    ]

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✓ Đã tạo thư mục: {directory}")
        else:
            print(f"✓ Thư mục đã tồn tại: {directory}")


def test_system():
    """
    Test hệ thống
    """
    print("=== TEST HỆ THỐNG ===")

    try:
        # Test import các module
        print("Đang test import modules...")
        from person_detector import PersonDetector  # pyright: ignore[reportMissingImports]
        from person_counter import PersonCounter  # pyright: ignore[reportMissingImports]
        from visualizer import Visualizer  # pyright: ignore[reportMissingImports]
        from data_logger import DataLogger  # pyright: ignore[reportMissingImports]
        from alert_system import AlertSystem  # pyright: ignore[reportMissingImports]
        print("✓ Import modules thành công")

        # Test khởi tạo các class
        print("Đang test khởi tạo classes...")
        detector = PersonDetector()
        counter = PersonCounter()
        visualizer = Visualizer()
        data_logger = DataLogger(enabled=False)  # Tắt để không tạo file
        alert_system = AlertSystem()
        print("✓ Khởi tạo classes thành công")

        # Test OpenCV
        print("Đang test OpenCV...")
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✓ OpenCV hoạt động bình thường")
            cap.release()
        else:
            print("⚠ Không thể truy cập webcam (có thể không có webcam)")

        print("✓ Test hệ thống hoàn thành")
        return True

    except Exception as e:
        print(f"✗ Lỗi trong test hệ thống: {e}")
        return False


def show_system_info():
    """
    Hiển thị thông tin hệ thống
    """
    print("=== THÔNG TIN HỆ THỐNG ===")

    import platform
    import sys

    print(f"Hệ điều hành: {platform.system()} {platform.release()}")
    print(f"Python version: {sys.version}")
    print(f"Architecture: {platform.architecture()[0]}")

    # Kiểm tra GPU
    try:
        import torch
        if torch.cuda.is_available():
            print(f"CUDA available: Yes (GPU: {torch.cuda.get_device_name(0)})")
        else:
            print("CUDA available: No (sử dụng CPU)")
    except ImportError:
        print("PyTorch not installed")


def main():
    """
    Hàm main cho setup
    """
    print("=== THIẾT LẬP HỆ THỐNG NHẬN DẠNG VÀ ĐẾM NGƯỜI ===")
    print("Phiên bản: 1.0")
    print("Sử dụng YOLOv8")
    print()

    # Hiển thị thông tin hệ thống
    show_system_info()
    print()

    # Cài đặt thư viện
    if not install_requirements():
        print("Không thể cài đặt thư viện. Vui lòng kiểm tra kết nối internet.")
        return

    print()

    # Tạo thư mục
    create_directories()
    print()

    # Tải mô hình YOLO
    if not download_yolo_model():
        print("Không thể tải mô hình YOLO. Vui lòng kiểm tra kết nối internet.")
        return

    print()

    # Test hệ thống
    if not test_system():
        print("Có lỗi trong quá trình test hệ thống.")
        return

    print()
    print("=== THIẾT LẬP HOÀN TẤT ===")
    print("Hệ thống đã sẵn sàng sử dụng!")
    print()
    print("Để chạy hệ thống:")
    print("  python main.py                    # Chạy với webcam")
    print("  python main.py --source video.mp4 # Chạy với file video")
    print("  python demo.py                    # Chạy demo tương tác")
    print()
    print("Để xem trợ giúp:")
    print("  python main.py --help")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nThiết lập bị gián đoạn bởi người dùng")
    except Exception as e:
        print(f"Lỗi trong quá trình thiết lập: {e}")
