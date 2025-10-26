# 🏃 Cách Chạy Ứng Dụng

Hướng dẫn chi tiết các cách chạy hệ thống nhận dạng và đếm người.

## 🎨 Chạy với GUI (Khuyến nghị)

Giao diện đồ họa dễ sử dụng, trực quan.

### Cách 1: Sử dụng Script

```bash
python scripts/run_gui.py
```

### Cách 2: Chạy trực tiếp

```bash
python -m src.ui.gui
```

### Cách 3: Double-click (Windows)

Tạo file `run.bat`:
```batch
@echo off
cd /d %~dp0
python scripts/run_gui.py
pause
```

## 💻 Chạy với Command Line

### Chạy với Webcam

```bash
python src/main.py
```

Sử dụng webcam mặc định (camera 0).

### Chạy với File Video

```bash
python src/main.py --source path/to/video.mp4
```

### Chọn Camera Khác

```bash
python src/main.py --source 1  # Camera 1
python src/main.py --source 2  # Camera 2
```

### Các Tùy Chọn Khác

```bash
python src/main.py --help
```

## 🧪 Chạy Demo Tương Tác

```bash
python scripts/demo.py
```

Menu demo với các tùy chọn:
1. Test với webcam
2. Test với video file
3. Test components
4. Xem thống kê

## ⌨️ Các Phím Điều Khiển (Command Line)

Khi chạy command line, bạn có thể sử dụng:

- **`q`** - Thoát ứng dụng
- **`r`** - Reset thống kê
- **`s`** - Lưu dữ liệu ngay lập tức
- **`h`** - Hiển thị trợ giúp
- **`a`** - Bật/tắt hệ thống cảnh báo
- **`d`** - Bật/tắt lưu dữ liệu
- **`+`** - Tăng ngưỡng cảnh báo
- **`-`** - Giảm ngưỡng cảnh báo

## 📂 Nguồn Video

### Camera

```python
# Camera 0 (mặc định)
source = 0

# Camera 1
source = 1

# Camera 2
source = 2
```

### File Video

```python
source = "path/to/video.mp4"
source = "path/to/video.avi"
source = "path/to/video.mov"
```

### RTSP Stream

```python
source = "rtsp://username:password@ip:port/stream"
```

## 🔧 Chạy với Môi Trường Variables

### Windows

```bash
set KMP_DUPLICATE_LIB_OK=TRUE
python scripts/run_gui.py
```

### Linux/Mac

```bash
export KMP_DUPLICATE_LIB_OK=TRUE
python scripts/run_gui.py
```

## 📊 Chạy với Cấu Hình Tùy Chỉnh

Tạo file `custom_config.py`:

```python
# config/settings.py
YOLO_MODEL = "yolov8s.pt"  # Thay đổi model
CONFIDENCE_THRESHOLD = 0.3  # Giảm threshold
MAX_PERSON_COUNT = 20      # Tăng max count
```

## 🚀 Chạy trong Background

### Linux/Mac

```bash
nohup python scripts/run_gui.py > output.log 2>&1 &
```

### Windows

Sử dụng Task Scheduler hoặc `run_background.bat`:

```batch
@echo off
start /B python scripts/run_gui.py > output.log 2>&1
```

## 🧪 Testing

### Chạy All Tests

```bash
pytest
```

### Chạy Specific Test

```bash
pytest tests/test_person_detector.py
```

### Coverage Report

```bash
pytest --cov=src tests/
```

## 📝 Logging

### Xem Log

```bash
# Windows
type logs\app.log

# Linux/Mac
cat logs/app.log
```

### Tail Log

```bash
# Linux/Mac
tail -f logs/app.log

# Windows PowerShell
Get-Content logs\app.log -Wait -Tail 20
```

## 🎯 Ví Dụ Sử Dụng

### Ví dụ 1: Giám sát camera trong nhà

```bash
# Chạy GUI với camera 0
python scripts/run_gui.py
```

### Ví dụ 2: Phân tích video có sẵn

```bash
python src/main.py --source video_sample.mp4
```

### Ví dụ 3: Chạy demo tương tác

```bash
python scripts/demo.py
# Chọn option 2 để test với video file
```

## ⚠️ Lưu Ý Quan Trọng

1. **First Run**: Mô hình YOLO sẽ tự động tải (khoảng 10-20MB)
2. **GPU Setup**: Đảm bảo đã cài PyTorch với CUDA để có FPS cao
3. **Camera Permission**: Cho phép ứng dụng truy cập camera
4. **Background Processes**: Đóng các ứng dụng nặng để tối ưu performance

## 🆘 Gặp Vấn Đề?

Xem [TROUBLESHOOTING.md](TROUBLESHOOTING.md) để giải quyết các vấn đề thường gặp.
