# Integration Test Cases - AI-YOLO

## Tổng quan

File này mô tả các test case tích hợp (Integration Tests) cho ứng dụng AI-YOLO. Các test này đảm bảo rằng các thành phần cốt lõi của hệ thống hoạt động đúng và có thể tích hợp với nhau một cách mượt mà.

## Cấu trúc Test

-   **File test**: `tests/integration/integration_test.py`
-   **Framework**: pytest
-   **Số lượng test cases**: 9
-   **Thành phần được test**: PersonDetector, PersonCounter, Visualizer, AlertSystem

---

## Bảng Mô Tả Chi Tiết Test Cases

### 1. Test Tích Hợp Các Component Đơn Lẻ

| STT | Tên Test Case                      | Mục đích                                         | Thành phần kiểm tra | Điều kiện pass                                                                                                         |
| --- | ---------------------------------- | ------------------------------------------------ | ------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| 1   | `test_person_detector_integration` | Kiểm tra khởi tạo và cấu hình của PersonDetector | PersonDetector      | - Detector được khởi tạo thành công<br>- confidence_threshold = 0.5<br>- iou_threshold = 0.35<br>- person_class_id = 0 |
| 2   | `test_person_counter_integration`  | Kiểm tra khởi tạo của PersonCounter              | PersonCounter       | - Counter được khởi tạo thành công<br>- current_count = 0                                                              |
| 3   | `test_visualizer_integration`      | Kiểm tra khởi tạo của Visualizer                 | Visualizer          | - Visualizer được khởi tạo thành công                                                                                  |
| 4   | `test_alert_system_integration`    | Kiểm tra khởi tạo của AlertSystem                | AlertSystem         | - AlertSystem được khởi tạo thành công<br>- max_count = 5 (theo config)                                                |

### 2. Test Tích Hợp Giữa Các Component

| STT | Tên Test Case                        | Mục đích                                                                | Thành phần kiểm tra                                    | Dữ liệu đầu vào                                                                                                              | Kết quả mong đợi                                                                                                         |
| --- | ------------------------------------ | ----------------------------------------------------------------------- | ------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| 5   | `test_components_work_together`      | Kiểm tra khả năng khởi tạo và hoạt động đồng thời của tất cả components | PersonDetector, PersonCounter, Visualizer, AlertSystem | Không có dữ liệu đầu vào                                                                                                     | - Tất cả components khởi tạo thành công<br>- Detector trả về model_info<br>- Counter có current_count = 0, max_count = 0 |
| 6   | `test_detector_and_counter_workflow` | Kiểm tra quy trình làm việc giữa detector và counter                    | PersonCounter                                          | 2 detections giả lập:<br>- Detection 1: bbox [100,100,200,200], conf 0.9<br>- Detection 2: bbox [300,300,400,400], conf 0.85 | - current_count = 2<br>- count trả về = 2                                                                                |
| 7   | `test_visualizer_with_frame`         | Kiểm tra visualizer xử lý frame và vẽ detections                        | Visualizer                                             | - Frame 480x640x3 (đen)<br>- 1 detection: bbox [100,100,200,200], conf 0.9                                                   | - result_frame không null<br>- Chiều rộng giữ nguyên<br>- Số channels giữ nguyên                                         |

### 3. Test Workflow Hoàn Chỉnh

| STT | Tên Test Case                   | Mục đích                                    | Thành phần kiểm tra                    | Dữ liệu đầu vào                                                                                   | Kịch bản test                                                                  | Kết quả mong đợi                                                                           |
| --- | ------------------------------- | ------------------------------------------- | -------------------------------------- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------ |
| 8   | `test_alert_system_workflow`    | Kiểm tra quy trình cảnh báo của AlertSystem | AlertSystem (max_count=3)              | - Test 1: count = 2<br>- Test 2: count = 5                                                        | 1. Kiểm tra với số lượng dưới ngưỡng<br>2. Kiểm tra với số lượng vượt ngưỡng   | - Test 1: Không có alert<br>- Test 2: Có alert trong lịch sử                               |
| 9   | `test_full_pipeline_simulation` | Kiểm tra toàn bộ pipeline từ đầu đến cuối   | PersonCounter, Visualizer, AlertSystem | - Frame 480x640x3<br>- 4 detections giả lập tại các vị trí khác nhau<br>- AlertSystem max_count=3 | 1. Update counter với detections<br>2. Vẽ visualizations<br>3. Kiểm tra alerts | - Counter đếm đúng 4 người<br>- Frame được vẽ thành công<br>- Alert được kích hoạt (4 > 3) |

---

## Chi Tiết Test Full Pipeline (Test Case #9)

### Input Data

```python
detections = [
    {"bbox": [100, 100, 200, 200], "confidence": 0.9, "class_id": 0},
    {"bbox": [300, 300, 400, 400], "confidence": 0.85, "class_id": 0},
    {"bbox": [500, 100, 600, 200], "confidence": 0.8, "class_id": 0},
    {"bbox": [200, 400, 300, 500], "confidence": 0.95, "class_id": 0}
]
```

### Workflow

1. **Counter Update**: `counter.update_count(detections)` → count = 4
2. **Visualization**: `visualizer.draw_detections(frame, detections, person_count=4)` → result_frame
3. **Alert Check**: `alert_system.check_alert(4)` → trigger alert (4 > 3)

### Assertions

-   ✅ `counter.current_count == 4`
-   ✅ `count == 4`
-   ✅ `result_frame is not None`
-   ✅ `len(alerts) > 0` (alert được tạo)

---

## Cách Chạy Tests

### Chạy tất cả integration tests

```bash
pytest tests/integration/integration_test.py -v
```

### Chạy với coverage

```bash
pytest tests/integration/integration_test.py --cov=src --cov-report=html
```

---

## Tóm Tắt Kết Quả

| Loại Test                    | Số lượng | Mô tả                                     |
| ---------------------------- | -------- | ----------------------------------------- |
| **Component Initialization** | 4        | Kiểm tra khởi tạo từng component riêng lẻ |
| **Component Integration**    | 3        | Kiểm tra tích hợp giữa các components     |
| **Full Workflow**            | 2        | Kiểm tra quy trình làm việc đầy đủ        |
| **Tổng cộng**                | **9**    | **Tất cả test cases**                     |

---

## Dependencies

Các thư viện cần thiết để chạy integration tests:

```python
import pytest          # Framework testing
import numpy as np     # Xử lý array và frame
import os, sys         # Path management
```

Các module được test:

-   `src.core.alert_system.AlertSystem`
-   `src.core.person_counter.PersonCounter`
-   `src.core.person_detector.PersonDetector`
-   `src.core.visualizer.Visualizer`

---

## Ghi Chú

1. **Mock Data**: Tất cả tests sử dụng dữ liệu giả lập (dummy data) để không phụ thuộc vào model YOLO thực tế
2. **Scope**: Tests tập trung vào việc kiểm tra tích hợp giữa các components, không test logic bên trong từng component chi tiết
3. **Performance**: Tests này không đo lường hiệu suất, chỉ đảm bảo tính đúng đắn của tích hợp
4. **Coverage**: Tests bao phủm các luồng chính của ứng dụng từ detection → counting → visualization → alerting

---
