"""
Script sửa lỗi cài đặt và xung đột thư viện
"""

import subprocess
import sys
import os


def uninstall_conflicting_packages():
    """
    Gỡ cài đặt các package có thể gây xung đột
    """
    print("=== GỠ CÀI ĐẶT CÁC PACKAGE XUNG ĐỘT ===")

    packages_to_uninstall = [
        "numpy",
        "opencv-python",
        "opencv-contrib-python",
        "ultralytics",
        "torch",
        "torchvision",
        "matplotlib",
        "pillow",
        "pandas",
        "scikit-learn",
        "albumentations"
    ]

    for package in packages_to_uninstall:
        try:
            print(f"Đang gỡ cài đặt {package}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "uninstall", package, "-y"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"✓ Đã gỡ cài đặt {package}")
        except subprocess.CalledProcessError:
            print(f"⚠ {package} không được cài đặt hoặc đã được gỡ")
        except Exception as e:
            print(f"✗ Lỗi khi gỡ {package}: {e}")


def install_packages_step_by_step():
    """
    Cài đặt từng package một cách tuần tự
    """
    print("\n=== CÀI ĐẶT TỪNG PACKAGE ===")

    # Thứ tự cài đặt quan trọng
    packages = [
        ("numpy", "1.24.3"),
        ("pillow", ">=10.0.0"),
        ("matplotlib", ">=3.7.0"),
        ("pandas", ">=2.0.0"),
        ("opencv-python", ">=4.8.0"),
        ("torch", ">=2.0.0"),
        ("torchvision", ">=0.15.0"),
        ("scikit-learn", ">=1.3.0"),
        ("albumentations", ">=1.3.0"),
        ("ultralytics", ">=8.0.0")
    ]

    for package, version in packages:
        try:
            print(f"Đang cài đặt {package} {version}...")
            if version.startswith(">="):
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", f"{package}{version}"
                ])
            else:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", f"{package}=={version}"
                ])
            print(f"✓ Đã cài đặt {package}")
        except subprocess.CalledProcessError as e:
            print(f"✗ Lỗi khi cài đặt {package}: {e}")
            return False

    return True


def clear_pip_cache():
    """
    Xóa cache pip
    """
    print("\n=== XÓA CACHE PIP ===")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "cache", "purge"])
        print("✓ Đã xóa cache pip")
    except Exception as e:
        print(f"⚠ Không thể xóa cache: {e}")


def upgrade_pip():
    """
    Nâng cấp pip
    """
    print("\n=== NÂNG CẤP PIP ===")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip"
        ])
        print("✓ Đã nâng cấp pip")
    except Exception as e:
        print(f"⚠ Không thể nâng cấp pip: {e}")


def test_imports():
    """
    Test import các thư viện
    """
    print("\n=== TEST IMPORT THƯ VIỆN ===")

    test_modules = [
        ("numpy", "np"),
        ("cv2", "cv2"),
        ("torch", "torch"),
        ("matplotlib.pyplot", "plt"),
        ("pandas", "pd"),
        ("ultralytics", "YOLO")
    ]

    success_count = 0
    for module_name, import_name in test_modules:
        try:
            exec(f"import {module_name} as {import_name}")
            print(f"✓ {module_name} import thành công")
            success_count += 1
        except Exception as e:
            print(f"✗ {module_name} import thất bại: {e}")

    print(f"\nKết quả: {success_count}/{len(test_modules)} thư viện import thành công")
    return success_count == len(test_modules)


def main():
    """
    Hàm main để sửa lỗi cài đặt
    """
    print("=== SỬA LỖI CÀI ĐẶT HỆ THỐNG ===")
    print("Lỗi: numpy.dtype size changed - xung đột phiên bản thư viện")
    print()

    # Bước 1: Nâng cấp pip
    upgrade_pip()

    # Bước 2: Xóa cache
    clear_pip_cache()

    # Bước 3: Gỡ cài đặt các package xung đột
    uninstall_conflicting_packages()

    # Bước 4: Cài đặt lại từng package
    if install_packages_step_by_step():
        print("\n=== KIỂM TRA KẾT QUẢ ===")
        if test_imports():
            print("\n🎉 SỬA LỖI THÀNH CÔNG!")
            print("Tất cả thư viện đã được cài đặt và hoạt động bình thường.")
            print("\nBây giờ bạn có thể chạy:")
            print("  python setup.py")
            print("  python main.py")
        else:
            print("\n⚠ Một số thư viện vẫn có vấn đề.")
            print("Vui lòng thử cài đặt thủ công từng thư viện.")
    else:
        print("\n✗ Có lỗi trong quá trình cài đặt.")
        print("Vui lòng kiểm tra kết nối internet và thử lại.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nQuá trình sửa lỗi bị gián đoạn.")
    except Exception as e:
        print(f"\nLỗi không mong muốn: {e}")
