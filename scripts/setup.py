"""
Script cài đặt và thiết lập hệ thống
Tự động phát hiện GPU và cài đặt PyTorch phù hợp
"""

import os
import sys
import subprocess
import platform


def detect_nvidia_gpu():
    """Phát hiện GPU NVIDIA"""
    try:
        result = subprocess.run(
            ['nvidia-smi'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        return result.returncode == 0
    except:
        return False


def get_cuda_version():
    """Lấy phiên bản CUDA"""
    try:
        result = subprocess.run(
            ['nvidia-smi'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            import re
            match = re.search(r'CUDA Version:\s*(\d+\.\d+)', result.stdout)
            if match:
                return match.group(1)
        return None
    except:
        return None


def install_pytorch_smart():
    """Cài đặt PyTorch thông minh theo GPU"""
    print("\n" + "="*60)
    print("CÀI ĐẶT PYTORCH")
    print("="*60)

    # Kiểm tra PyTorch đã có chưa
    pytorch_installed = False
    pytorch_needs_reinstall = False

    try:
        import torch
        pytorch_installed = True
        print(f"✓ PyTorch đã có: {torch.__version__}")

        # Test PyTorch có hoạt động không (tránh lỗi DLL)
        try:
            test_tensor = torch.randn(10, 10)
            print("✓ PyTorch hoạt động bình thường")

            if torch.cuda.is_available():
                print(f"✓ CUDA đã kích hoạt: {torch.cuda.get_device_name(0)}")
                return True
            else:
                print("⚠ PyTorch hiện tại chỉ hỗ trợ CPU")
                if detect_nvidia_gpu():
                    response = input("\n💡 Có GPU nhưng không dùng CUDA. Cài lại? (y/n): ").lower()
                    if response != 'y':
                        return True
                    pytorch_needs_reinstall = True
                else:
                    return True

        except Exception as dll_error:
            print(f"✗ PyTorch có lỗi khi chạy: {dll_error}")

            # Kiểm tra xem có phải lỗi DLL không
            if "DLL" in str(dll_error) or "c10.dll" in str(dll_error):
                print("\n⚠️ PHÁT HIỆN LỖI DLL!")
                print("   Nguyên nhân: PyTorch CUDA trên máy không có GPU")
                print("   Giải pháp: Sẽ tự động cài lại PyTorch CPU")
            else:
                print("  Có thể do PyTorch không tương thích")

            pytorch_needs_reinstall = True

    except ImportError:
        print("PyTorch chưa được cài")

    # Gỡ PyTorch nếu cần
    if pytorch_needs_reinstall and pytorch_installed:
        print("\n→ Gỡ PyTorch hiện tại...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "uninstall",
                "torch", "torchvision", "-y"
            ], stdout=subprocess.DEVNULL)
            print("✓ Đã gỡ PyTorch")

            # Xóa cache
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "cache", "purge"
                ], stdout=subprocess.DEVNULL)
            except:
                pass
        except Exception as e:
            print(f"⚠ Lỗi khi gỡ: {e}")

    # Xác định phiên bản cần cài
    has_gpu = detect_nvidia_gpu()

    if has_gpu:
        cuda_ver = get_cuda_version()
        print(f"\n🚀 Phát hiện GPU NVIDIA (CUDA {cuda_ver or 'unknown'})")

        # Chọn CUDA version
        if cuda_ver:
            cuda_major = int(cuda_ver.split('.')[0])
            if cuda_major >= 12:
                index_url = "https://download.pytorch.org/whl/cu121"
                print("   → Cài PyTorch CUDA 12.1")
            elif cuda_major == 11:
                index_url = "https://download.pytorch.org/whl/cu118"
                print("   → Cài PyTorch CUDA 11.8")
            else:
                index_url = None
                print("   → CUDA quá cũ, cài CPU")
        else:
            index_url = "https://download.pytorch.org/whl/cu118"
            print("   → Cài PyTorch CUDA 11.8 (mặc định)")

        try:
            if index_url:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install",
                    "torch", "torchvision", "--index-url", index_url
                ])
            else:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install",
                    "torch>=2.0.0", "torchvision>=0.15.0"
                ])

            # Test CUDA sau khi cài
            print("→ Test CUDA...")
            try:
                import torch
                if torch.cuda.is_available():
                    # Test thực sự bằng cách tạo tensor
                    _ = torch.cuda.FloatTensor(1)
                    print("✓ CUDA hoạt động tốt")
                else:
                    print("⚠ CUDA không khả dụng, nhưng PyTorch đã cài")
            except Exception as test_err:
                print(f"⚠ CUDA test thất bại: {test_err}")
                print("  Hệ thống sẽ tự động chuyển sang CPU khi chạy")

            print("✓ Cài PyTorch thành công")
            return True
        except:
            print("✗ Lỗi cài CUDA, thử CPU...")
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install",
                    "torch>=2.0.0", "torchvision>=0.15.0",
                    "--index-url", "https://download.pytorch.org/whl/cpu"
                ])
                print("✓ Đã fallback sang PyTorch CPU")
                return True
            except:
                return False
    else:
        print("\n💻 Không có GPU, cài PyTorch CPU")

        # Thử cài phiên bản cụ thể trước
        try:
            print("→ Cài PyTorch 2.5.1 CPU...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                "torch==2.5.1", "torchvision==0.20.1",
                "--index-url", "https://download.pytorch.org/whl/cpu"
            ])
            print("✓ Cài PyTorch CPU thành công")

            # Test ngay
            try:
                import torch
                _ = torch.randn(10, 10)
                print("✓ PyTorch CPU hoạt động tốt")
            except Exception as test_err:
                print(f"⚠ Test thất bại: {test_err}")

            return True

        except:
            print("⚠ Lỗi cài phiên bản cụ thể, thử phiên bản mới nhất...")
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install",
                    "torch", "torchvision",
                    "--index-url", "https://download.pytorch.org/whl/cpu"
                ])
                print("✓ Cài PyTorch CPU (latest) thành công")
                return True
            except:
                print("⚠ Lỗi cài từ CPU index, thử cài bình thường...")
                try:
                    subprocess.check_call([
                        sys.executable, "-m", "pip", "install",
                        "torch>=2.0.0", "torchvision>=0.15.0"
                    ])
                    return True
                except:
                    return False


def install_other_packages():
    """Cài đặt các thư viện khác"""
    print("\n" + "="*60)
    print("CÀI ĐẶT CÁC THƯ VIỆN KHÁC")
    print("="*60)

    try:
        # Nâng cấp pip
        print("→ Nâng cấp pip...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip"
        ], stdout=subprocess.DEVNULL)

        # Cài numpy
        print("→ Cài numpy...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "numpy==1.24.3"
        ], stdout=subprocess.DEVNULL)

        # Cài các thư viện khác
        packages = [
            "opencv-python>=4.8.0",
            "matplotlib>=3.7.0",
            "pillow>=10.0.0,<12.0",
            "pandas>=2.0.0",
            "scikit-learn>=1.3.0",
            "albumentations>=1.3.0",
            "PyQt6>=6.5.0",
            "ultralytics>=8.0.0"
        ]

        for pkg in packages:
            print(f"→ Cài {pkg.split('>=')[0]}...")
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", pkg],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except:
                print(f"  ⚠ Lỗi cài {pkg}")

        print("✓ Cài đặt hoàn tất")
        return True
    except Exception as e:
        print(f"✗ Lỗi: {e}")
        return False


def download_yolo_model():
    """Tải mô hình YOLOv8"""
    print("\n" + "="*60)
    print("TẢI MÔ HÌNH YOLOv8")
    print("="*60)

    try:
        from ultralytics import YOLO
        import numpy as np

        print("→ Tải YOLOv8n...")
        model = YOLO("yolov8n.pt")

        print("→ Test mô hình...")
        test_img = np.zeros((640, 640, 3), dtype=np.uint8)
        _ = model(test_img, verbose=False)

        print("✓ Mô hình hoạt động tốt")
        return True
    except Exception as e:
        print(f"✗ Lỗi: {e}")
        return False


def verify_installation():
    """Xác minh cài đặt"""
    print("\n" + "="*60)
    print("XÁC MINH CÀI ĐẶT")
    print("="*60)

    try:
        # Test PyTorch
        import torch
        print(f"✓ PyTorch: {torch.__version__}")

        # Test PyTorch hoạt động
        try:
            test_tensor = torch.randn(10, 10)
            result = test_tensor.sum()
            print("✓ PyTorch hoạt động bình thường")
        except Exception as tensor_err:
            print(f"✗ PyTorch có lỗi: {tensor_err}")
            return False

        # Test CUDA
        if torch.cuda.is_available():
            try:
                cuda_tensor = torch.cuda.FloatTensor(10)
                print(f"✓ GPU: {torch.cuda.get_device_name(0)}")
                print(f"✓ VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
            except:
                print("⚠ CUDA available nhưng không hoạt động")
                print("ℹ Hệ thống sẽ tự động dùng CPU")
        else:
            print("ℹ Chạy trên CPU (không có GPU hoặc CUDA)")

        # Test OpenCV
        import cv2
        print(f"✓ OpenCV: {cv2.__version__}")

        # Test Ultralytics
        from ultralytics import YOLO
        print("✓ Ultralytics: OK")

        return True
    except Exception as e:
        print(f"⚠ Lỗi: {e}")
        return False


def create_directories():
    """Tạo thư mục cần thiết"""
    dirs = ["data", "output", "logs", "models"]
    for d in dirs:
        os.makedirs(d, exist_ok=True)


def main():
    """Hàm chính"""
    print("\n" + "="*60)
    print("   THIẾT LẬP HỆ THỐNG NHẬN DẠNG NGƯỜI - YOLOv8")
    print("="*60)

    # Hiển thị thông tin hệ thống
    print(f"\n📋 Hệ điều hành: {platform.system()} {platform.release()}")
    print(f"📋 Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print(f"📋 GPU NVIDIA: {'Có' if detect_nvidia_gpu() else 'Không'}")

    # Kiểm tra Python version
    if sys.version_info < (3, 8):
        print("\n❌ Cần Python 3.8 trở lên")
        return

    # Bước 1: Cài PyTorch
    if not install_pytorch_smart():
        print("\n❌ Không thể cài PyTorch")
        return

    # Bước 2: Cài thư viện khác
    if not install_other_packages():
        print("\n❌ Không thể cài thư viện")
        return

    # Bước 3: Tạo thư mục
    create_directories()

    # Bước 4: Tải YOLO
    if not download_yolo_model():
        print("\n⚠ Không thể tải YOLO (có thể bỏ qua)")

    # Bước 5: Xác minh
    verify_installation()

    # Hoàn thành
    print("\n" + "="*60)
    print("   ✅ CÀI ĐẶT HOÀN TẤT!")
    print("="*60)
    print("\n📚 Chạy ứng dụng:")
    print("   python scripts/run_gui.py")
    print("\n" + "="*60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Đã hủy bởi người dùng")
    except Exception as e:
        print(f"\n\n❌ Lỗi: {e}")
        print("💡 Thử chạy: python scripts/fix_installation.py")
