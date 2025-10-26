# 📋 Cài Đặt & Thiết Lập

Hướng dẫn chi tiết cài đặt Hệ Thống Nhận Dạng và Đếm Người từ đầu đến cuối.

## 📋 Yêu Cầu Hệ Thống

### Yêu Cầu Tối Thiểu

-   **Hệ điều hành**: Windows 10/11, Linux, macOS
-   **Python**: 3.8 trở lên
-   **RAM**: Tối thiểu 4GB (khuyến nghị 8GB)
-   **GPU**: NVIDIA GPU với CUDA (tùy chọn nhưng khuyến nghị)

### Yêu Cầu Được Khuyến Nghị

-   **GPU**: NVIDIA GeForce GTX 1060 trở lên
-   **RAM**: 16GB
-   **CUDA**: 11.8 hoặc 12.0+
-   **VRAM**: 4GB+

## 🔧 Cài Đặt

### Bước 1: Clone Repository

```bash
git clone <repository-url>
cd Ai-yolo
```

### Bước 2: Tạo Virtual Environment (Khuyến nghị)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Bước 3: Cài Đặt Dependencies

#### Cài đặt cơ bản

```bash
pip install -r requirements.txt
```

#### Cài đặt với GPU Support (NVIDIA)

**Windows:**

1. Gỡ PyTorch CPU:

```bash
pip uninstall torch torchvision -y
```

2. Cài PyTorch với CUDA:

```bash
# Cho CUDA 11.8
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Hoặc cho CUDA 12.1+
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

#### Kiểm tra GPU

```bash
python -c "import torch; print('CUDA Available:', torch.cuda.is_available())"
```

Nếu hiển thị `True` → GPU đã sẵn sàng! ✅

### Bước 4: Tải Mô Hình YOLO

Mô hình sẽ tự động tải lần đầu chạy, hoặc tải thủ công:

```bash
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

### Bước 5: Kiểm Tra Cài Đặt

```bash
python scripts/test_torch.py
```

Kiểm tra:

-   ✅ PyTorch version
-   ✅ CUDA available
-   ✅ Model tải thành công

## 🎯 Cài Đặt Nhanh (One-liner)

### Windows (với GPU)

````bash
pip install -r requirements.txt && pip uninstall torch torchvision -y && pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

## 🐛 Xử Lý Lỗi Cài Đặt

### Lỗi: "No module named 'PyQt6'"

```bash
pip install PyQt6
````

### Lỗi: "CUDA out of memory"

Giải pháp:

1. Giảm độ phân giải: 640x480 → 480x360
2. Đóng các ứng dụng khác
3. Sử dụng model nhỏ hơn (`yolov8n.pt`)

### Lỗi: "DLL initialization failed" (Windows)

Thêm vào đầu script:

```python
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
```

## ✅ Xác Nhận Cài Đặt Thành Công

Chạy lệnh kiểm tra:

```bash
python scripts/setup.py
```

Bạn sẽ thấy:

```
✅ Python: 3.x.x
✅ PyTorch: 2.x.x
✅ CUDA: Available (GPU: NVIDIA ...)
✅ OpenCV: 4.x.x
✅ PyQt6: Installed
```

## 🚀 Bước Tiếp Theo

Sau khi cài đặt thành công:

1. Xem [USAGE.md](USAGE.md) - Cách chạy ứng dụng
2. Xem [GUI_GUIDE.md](GUI_GUIDE.md) - Hướng dẫn sử dụng GUI
3. Xem [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Nếu có vấn đề
