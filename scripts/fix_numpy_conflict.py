"""
Script sửa lỗi xung đột numpy cụ thể
"""

import subprocess
import sys
import os


def fix_numpy_conflict():
    """
    Sửa lỗi xung đột numpy
    """
    print("=== SỬA LỖI XUNG ĐỘT NUMPY ===")
    print("Lỗi: numpy.dtype size changed - xung đột phiên bản")
    print()

    try:
        # Bước 1: Gỡ cài đặt tất cả thư viện liên quan đến numpy
        print("1. Gỡ cài đặt các thư viện xung đột...")
        packages_to_remove = [
            "numpy", "opencv-python", "opencv-python-headless",
            "albumentations", "albucore", "scikit-image"
        ]

        for package in packages_to_remove:
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "uninstall", package, "-y"
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"   ✓ Đã gỡ {package}")
            except:
                print(f"   ⚠ {package} không có hoặc đã được gỡ")

        # Bước 2: Xóa cache pip
        print("\n2. Xóa cache pip...")
        subprocess.check_call([sys.executable, "-m", "pip", "cache", "purge"])
        print("   ✓ Đã xóa cache")

        # Bước 3: Cài đặt numpy phiên bản tương thích
        print("\n3. Cài đặt numpy phiên bản tương thích...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "numpy>=1.24.4,<2.0"
        ])
        print("   ✓ Đã cài đặt numpy")

        # Bước 4: Cài đặt opencv
        print("\n4. Cài đặt opencv...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "opencv-python>=4.8.0"
        ])
        print("   ✓ Đã cài đặt opencv")

        # Bước 5: Cài đặt các thư viện còn lại
        print("\n5. Cài đặt các thư viện còn lại...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("   ✓ Đã cài đặt tất cả thư viện")

        # Bước 6: Test import
        print("\n6. Test import...")
        test_imports()

        return True

    except Exception as e:
        print(f"\n✗ Lỗi: {e}")
        return False


def test_imports():
    """
    Test import các thư viện
    """
    test_modules = [
        ("numpy", "np"),
        ("cv2", "cv2"),
        ("torch", "torch"),
        ("ultralytics", "YOLO")
    ]

    success_count = 0
    for module_name, import_name in test_modules:
        try:
            exec(f"import {module_name} as {import_name}")
            print(f"   ✓ {module_name} import thành công")
            success_count += 1
        except Exception as e:
            print(f"   ✗ {module_name} import thất bại: {e}")

    if success_count == len(test_modules):
        print("\n🎉 SỬA LỖI THÀNH CÔNG!")
        print("Tất cả thư viện đã hoạt động bình thường.")
    else:
        print(f"\n⚠ Chỉ {success_count}/{len(test_modules)} thư viện hoạt động.")


def main():
    """
    Hàm main
    """
    print("=== SỬA LỖI XUNG ĐỘT NUMPY ===")
    print("Phiên bản: 1.0")
    print()

    if fix_numpy_conflict():
        print("\n✅ Hoàn thành! Bây giờ bạn có thể chạy:")
        print("   python setup.py")
        print("   python main.py")
    else:
        print("\n❌ Có lỗi trong quá trình sửa lỗi.")
        print("Vui lòng thử phương pháp thủ công trong TROUBLESHOOTING.md")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nQuá trình bị gián đoạn.")
    except Exception as e:
        print(f"\nLỗi không mong muốn: {e}")
