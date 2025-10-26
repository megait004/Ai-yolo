# ⚙️ Tính Năng Hệ Thống

Danh sách đầy đủ các chức năng của Hệ Thống Nhận Dạng và Đếm Người.

## 🎯 Tính Năng Chính

### 1. Nhận Dạng Người (Person Detection)

-   ✅ Sử dụng mô hình YOLOv8 mạnh mẽ
-   ✅ Phát hiện người theo thời gian thực
-   ✅ Độ chính xác cao (>95%)
-   ✅ Hỗ trợ nhiều góc độ và khoảng cách
-   ✅ Tự động adapt với điều kiện ánh sáng

**Công nghệ:**

-   Model: YOLOv8n (nano) / YOLOv8s (small)
-   Framework: Ultralytics
-   Inference: GPU-accelerated

### 2. Đếm Người (Person Counting)

-   ✅ Đếm số lượng người trong khung hình
-   ✅ Cập nhật real-time
-   ✅ Thống kê tổng detections
-   ✅ Tracking người qua các frame
-   ✅ Tránh double-counting

**Số liệu:**

-   Số người hiện tại
-   Tổng detections
-   FPS (Frames Per Second)
-   Thời gian xử lý

### 3. Giao Diện Người Dùng (GUI)

-   ✅ Giao diện trực quan, dễ sử dụng
-   ✅ Công nghệ: PyQt6
-   ✅ Hiển thị video real-time
-   ✅ Bounding boxes và nhãn
-   ✅ Thông tin thống kê
-   ✅ Control panel
-   ✅ Responsive design

**Thành phần:**

-   Video display panel (70% màn hình)
-   Control panel (bên phải)
-   Information panel (thông tin & cảnh báo)
-   Stats bar (dưới cùng)

### 4. Hệ Thống Cảnh Báo (Alert System)

-   ✅ Cảnh báo khi vượt ngưỡng
-   ✅ Ngưỡng tùy chỉnh được
-   ✅ Ba mức độ: Normal, Warning, Alert
-   ✅ Đổi màu UI theo mức độ
-   ✅ Thống kê cảnh báo

**Mức độ:**

-   🟢 Normal: Số người < ngưỡng
-   🟡 Warning: Số người ≥ 80% ngưỡng
-   🔴 Alert: Số người ≥ ngưỡng

### 5. Lưu Trữ Dữ Liệu

-   ✅ Tự động lưu CSV
-   ✅ Log chi tiết từng frame
-   ✅ Export report
-   ✅ Timestamp đầy đủ
-   ✅ Format chuẩn

**Dữ liệu lưu:**

```csv
timestamp,person_count,total_detections,alert_status
2024-01-01 12:00:00,3,150,Normal
2024-01-01 12:00:01,4,154,Warning
```

### 6. Xử Lý Video

-   ✅ Webcam input
-   ✅ Video file input
-   ✅ RTSP stream support
-   ✅ Multiple camera support
-   ✅ Auto-resolution

**Định dạng hỗ trợ:**

-   MP4, AVI, MOV
-   RTSP, HTTP stream
-   USB cameras

## 🚀 Tính Năng Nâng Cao

### 7. Tối Ưu Hiệu Năng

-   ✅ GPU acceleration (CUDA)
-   ✅ FP16 precision (GPU)
-   ✅ Frame resizing
-   ✅ Multi-threading
-   ✅ Lazy model loading

**Performance:**

-   CPU: 5-10 FPS
-   GPU: 30-60 FPS
-   VRAM usage: ~1-2 GB

### 8. Thống Kê Chi Tiết

-   ✅ FPS real-time
-   ✅ Person count history
-   ✅ Detection accuracy
-   ✅ Alert count
-   ✅ Runtime statistics

### 9. Cấu Hình Linh Hoạt

-   ✅ Confidence threshold
-   ✅ IOU threshold
-   ✅ Max person count
-   ✅ Alert threshold
-   ✅ Model selection

### 10. Export & Báo Cáo

-   ✅ Export CSV
-   ✅ Export statistics
-   ✅ Visual charts
-   ✅ Report generation

## 📊 Dữ Liệu Thu Thập

### Metrics Được Thu Thập

1. **Từng Frame:**

    - Timestamp
    - Số người phát hiện
    - Bounding boxes
    - Confidence scores
    - Alert status

2. **Tổng Hợp:**
    - Tổng số frames
    - Tổng detections
    - Số lần cảnh báo
    - FPS trung bình
    - Thời gian chạy

## 🔧 Tính Năng Kỹ Thuật

### Phát Hiện (Detection)

-   **Model:** YOLOv8
-   **Classes:** Person (class 0)
-   **Confidence Threshold:** 0.25 (mặc định)
-   **IOU Threshold:** 0.45
-   **Input Size:** 640x640

### Xử Lý Ảnh

-   **Preprocessing:** Resize, normalize
-   **Postprocessing:** NMS, confidence filtering
-   **Visualization:** Bounding boxes, labels, colors

### Đếm Người

-   **Method:** Frame-by-frame detection
-   **Tracking:** IoU-based tracking
-   **Deduplication:** Sử dụng IoU overlap

### Cảnh Báo

-   **Trigger:** Người ≥ threshold
-   **Modes:** Soft warning, hard alert
-   **Visual:** Color coding, icons
-   **Audio:** (Có thể thêm)

## 🎨 UI/UX Features

### Giao Diện

-   **Design:** Modern, minimalist
-   **Colors:** Dark/Light theme support
-   **Fonts:** Clear, readable
-   **Layout:** Responsive, adaptive

### Tương Tác

-   **Buttons:** Start/Stop, Select source, Settings
-   **Dropdowns:** Camera selection, resolution
-   **Spinners:** Threshold adjustment
-   **Status:** Real-time updates

### Thông Tin

-   **Current stats:** Số người, FPS
-   **History:** Scrollable logs
-   **Alerts:** Prominent warnings
-   **Help:** Tooltips, hints

## 🔒 Tính Năng Bảo Mật

-   ✅ Local processing (không gửi dữ liệu lên cloud)
-   ✅ Privacy-first design
-   ✅ Mã nguồn mở, auditable
-   ✅ Không tracking

## 📈 Roadmap

### Phiên bản Tương Lai

-   [ ] Multi-person tracking với ID
-   [ ] Heatmap visualization
-   [ ] Audio alerts
-   [ ] Cloud sync
-   [ ] Mobile app
-   [ ] API server
-   [ ] Multi-camera view
-   [ ] AI-powered analysis

## 🎓 Use Cases

### 1. An Ninh & Giám Sát

-   Đếm người vào/ra
-   Phát hiện đông người
-   Giám sát công cộng

### 2. Quản Lý Không Gian

-   Giám sát sức chứa
-   Quản lý đám đông
-   Tối ưu không gian

### 3. Phân Tích & Báo Cáo

-   Thống kê khách hàng
-   Xu hướng traffic
-   Báo cáo hiệu suất

### 4. Nghiên Cứu

-   Analytics
-   Data collection
-   Algorithm testing

## 💡 Tip & Tricks

1. **Để có FPS cao:** Sử dụng GPU + model YOLOv8n
2. **Để có độ chính xác cao:** Tăng confidence threshold
3. **Để giảm false positive:** Giảm IOU threshold
4. **Để xử lý nhiều người:** Tăng model size (yolov8s, yolov8m)

## 🆘 Hỗ Trợ

Cần thêm tính năng? Tạo issue trên GitHub!
