# Hướng Dẫn Sử Dụng Giao Diện GUI

## Tổng Quan

Giao diện người dùng (GUI) được xây dựng bằng **PyQt6**, cung cấp giao diện trực quan, dễ sử dụng cho hệ thống nhận dạng và đếm người.

## Cài Đặt

### 1. Cài đặt PyQt6

```bash
pip install PyQt6
```

Hoặc cài đặt tất cả dependencies:

```bash
pip install -r requirements.txt
```

### 2. Chạy Ứng Dụng

**Cách 1: Sử dụng script**

```bash
python scripts/run_gui.py
```

**Cách 2: Chạy trực tiếp từ module**

```bash
python -m src.ui.gui
```

## Cấu Trúc Giao Diện

Giao diện được chia thành **3 vùng chính**:

### 1. Vùng Hiển Thị Video (Main Video Panel)

-   **Vị trí**: Bên trái, chiếm ~70-80% màn hình
-   **Chức năng**:
    -   Hiển thị luồng video trực tiếp từ camera hoặc file video
    -   Hiển thị bounding box xung quanh người
    -   Hiển thị nhãn "Person" và độ tin cậy (%)
    -   Hiển thị số lượng người ở góc trên

**Thanh thống kê dưới video**:

-   Số người hiện tại
-   FPS (Frame per second)
-   Thời gian chạy

### 2. Thanh Điều Khiển (Control Panel)

Nằm bên phải màn hình, gồm các nút:

#### **Bắt Đầu Nhận Dạng / Dừng Nhận Dạng**

-   Bật/tắt hệ thống nhận dạng
-   Nút sẽ đổi màu: Xanh lá (Start) → Đỏ (Stop)

#### **Chọn Video / Camera**

-   **📁 Chọn Video**: Mở file video (.mp4, .avi, .mov, .mkv)
-   **ComboBox**: Chọn camera (Camera 0, 1, 2, ...)

#### **Ngưỡng Cảnh Báo**

-   Thiết lập số người tối đa cho phép
-   Mặc định: 5 người
-   Phạm vi: 1-100

#### **💾 Lưu Dữ Liệu**

-   Lưu thống kê vào file CSV ngay lập tức

#### **📊 Xuất Báo Cáo**

-   Xuất báo cáo thống kê ra file CSV

### 3. Vùng Thông Tin & Cảnh Báo (Information Panel)

#### **Trạng thái Camera**

-   🔴 Chưa kết nối
-   🟢 Đang chạy
-   🟡 Đang kết nối...

#### **Thống Kê Chi Tiết**

-   Số người hiện tại
-   Số người tối đa
-   Trung bình
-   Tổng detections
-   Tỷ lệ phát hiện

#### **Trạng thái Cảnh Báo**

-   ⚪ **Trạng thái: Bình thường** (nền xám đen)
-   🟡 **Cảnh báo** (nền vàng) - vượt ngưỡng ít
-   🔴 **Cảnh báo khẩn cấp** (nền đỏ) - vượt ngưỡng nhiều

## Hướng Dẫn Sử Dụng

### Bước 1: Khởi Động Ứng Dụng

```bash
python scripts/run_gui.py
```

### Bước 2: Chọn Nguồn Video

**Option 1: Sử dụng Camera**

1. Chọn camera từ dropdown (Camera 0, 1, 2, ...)
2. Mặc định: Camera 0

**Option 2: Sử dụng File Video**

1. Click nút "📁 Chọn Video"
2. Chọn file video từ máy tính
3. Hỗ trợ: .mp4, .avi, .mov, .mkv

### Bước 3: Thiết Lập Ngưỡng Cảnh Báo

1. Điều chỉnh số trong ô "Ngưỡng"
2. Giá trị mặc định: 5 người
3. Hệ thống sẽ cảnh báo khi số người vượt quá ngưỡng này

### Bước 4: Bắt Đầu Nhận Dạng

1. Click nút "▶ Bắt Đầu Nhận Dạng"
2. Video sẽ hiển thị trong Main Panel
3. Bounding box sẽ xuất hiện xung quanh mỗi người
4. Thông tin sẽ được cập nhật theo thời gian thực

### Bước 5: Quan Sát Kết Quả

-   **Main Panel**: Xem video trực tiếp với bounding box
-   **Stats Bar**: Theo dõi số người, FPS, thời gian
-   **Information Panel**: Xem thống kê chi tiết và cảnh báo

### Bước 6: Lưu Dữ Liệu

-   Click "💾 Lưu Dữ Liệu" để lưu thống kê ngay lập tức
-   Hoặc "📊 Xuất Báo Cáo" để xuất ra file CSV

### Bước 7: Dừng Nhận Dạng

1. Click nút "⏸ Dừng Nhận Dạng"
2. Hệ thống sẽ tự động lưu dữ liệu cuối cùng

## Tính Năng Cảnh Báo

### Mức Độ Cảnh Báo

1. **Bình thường** (⚪)

    - Số người ≤ Ngưỡng
    - Màu nền: Xám đen

2. **Cảnh báo** (🟡)

    - Số người vượt ngưỡng 1-2 người
    - Màu nền: Vàng

3. **Khẩn cấp** (🔴)
    - Số người vượt ngưỡng > 2 người
    - Màu nền: Đỏ

### Khi Cảnh Báo Kích Hoạt

-   Vùng cảnh báo đổi màu nền theo mức độ
-   Thông điệp cảnh báo hiển thị trên video
-   Ghi nhận vào lịch sử cảnh báo

## Lưu Ý

### Yêu Cầu Hệ Thống

-   **Python**: 3.8+
-   **RAM**: Tối thiểu 4GB (khuyến nghị 8GB+)
-   **Camera**: USB hoặc webcam tích hợp
-   **Màn hình**: Tối thiểu 1280x720

### Hiệu Suất

-   **FPS**: 15-30 fps tùy vào hardware
-   **GPU**: Không bắt buộc, nhưng khuyến nghị sử dụng GPU để tăng tốc

### Khắc Phục Sự Cố

1. **Camera không hoạt động**

    - Kiểm tra camera đã kết nối
    - Thử chọn camera khác (1, 2, ...)

2. **FPS thấp**

    - Giảm độ phân giải camera
    - Tắt các ứng dụng khác
    - Sử dụng GPU nếu có

3. **Video không hiển thị**
    - Kiểm tra file video có đúng format
    - Kiểm tra đường dẫn file

## Build Thành Ứng Dụng Standalone

Để build thành file .exe (Windows) hoặc .app (Mac):

```bash
pip install pyinstaller

# Build
pyinstaller --name PersonDetection --windowed --onefile scripts/run_gui.py

# File .exe sẽ có trong thư mục dist/
```

## Phím Tắt

Trong tương lai có thể thêm:

-   `Space`: Start/Stop
-   `S`: Lưu dữ liệu
-   `R`: Reset thống kê
-   `Esc`: Thoát

## Hỗ Trợ

Nếu gặp vấn đề, vui lòng:

1. Kiểm tra file `TROUBLESHOOTING.md`
2. Xem log trong thư mục `logs/`
3. Tạo issue trên GitHub

---

**Chúc bạn sử dụng hiệu quả!** 🎉
