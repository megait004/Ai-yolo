"""
Script demo để test hệ thống nhận dạng và đếm người
"""

import cv2
import time
from main import PersonDetectionApp


def demo_with_webcam():
    """
    Demo với webcam
    """
    print("=== DEMO VỚI WEBCAM ===")
    print("Đang khởi động webcam...")

    app = PersonDetectionApp(source=0, save_data=True)
    app.run()


def demo_with_video_file(video_path):
    """
    Demo với file video

    Args:
        video_path (str): Đường dẫn đến file video
    """
    print(f"=== DEMO VỚI FILE VIDEO: {video_path} ===")

    app = PersonDetectionApp(source=video_path, save_data=True)
    app.run()


def test_components():
    """
    Test từng component riêng lẻ
    """
    print("=== TEST CÁC COMPONENT ===")

    # Test PersonDetector
    print("1. Test PersonDetector...")
    from person_detector import PersonDetector
    detector = PersonDetector()
    print(f"   Model info: {detector.get_model_info()}")

    # Test PersonCounter
    print("2. Test PersonCounter...")
    from person_counter import PersonCounter
    counter = PersonCounter()

    # Simulate detections
    fake_detections = [
        {'bbox': [100, 100, 200, 300], 'confidence': 0.8, 'class_id': 0},
        {'bbox': [300, 150, 400, 350], 'confidence': 0.9, 'class_id': 0}
    ]

    count = counter.update_count(fake_detections)
    print(f"   Person count: {count}")
    print(f"   Stats: {counter.get_all_stats()}")

    # Test AlertSystem
    print("3. Test AlertSystem...")
    from alert_system import AlertSystem
    alert_system = AlertSystem(max_count=1)

    alert = alert_system.check_alert(3)  # Vượt ngưỡng
    if alert:
        print(f"   Alert: {alert['message']}")

    # Test DataLogger
    print("4. Test DataLogger...")
    from data_logger import DataLogger
    data_logger = DataLogger(enabled=True)

    stats = counter.get_all_stats()
    data_logger.save_immediate(stats)
    print("   Data saved to CSV")

    print("Test hoàn thành!")


def interactive_demo():
    """
    Demo tương tác
    """
    print("=== DEMO TƯƠNG TÁC ===")
    print("Chọn chế độ demo:")
    print("1. Webcam")
    print("2. File video")
    print("3. Test components")
    print("4. Thoát")

    while True:
        choice = input("\nNhập lựa chọn (1-4): ").strip()

        if choice == '1':
            demo_with_webcam()
            break
        elif choice == '2':
            video_path = input("Nhập đường dẫn file video: ").strip()
            if video_path:
                demo_with_video_file(video_path)
            else:
                print("Đường dẫn không hợp lệ!")
            break
        elif choice == '3':
            test_components()
            break
        elif choice == '4':
            print("Thoát demo")
            break
        else:
            print("Lựa chọn không hợp lệ! Vui lòng chọn 1-4")


if __name__ == "__main__":
    print("=== HỆ THỐNG NHẬN DẠNG VÀ ĐẾM NGƯỜI - DEMO ===")
    print("Phiên bản: 1.0")
    print("Sử dụng YOLOv8 cho phát hiện người")
    print()

    try:
        interactive_demo()
    except KeyboardInterrupt:
        print("\nDemo bị gián đoạn bởi người dùng")
    except Exception as e:
        print(f"Lỗi trong demo: {e}")

    print("Cảm ơn bạn đã sử dụng hệ thống!")
