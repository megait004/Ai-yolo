# System Test Cases Documentation

## Tài liệu Test Case cho System Tests

Tài liệu này mô tả chi tiết các test cases cho System Testing (kiểm thử tích hợp toàn hệ thống).

System Testing tập trung vào:

-   **End-to-End Testing**: Kiểm tra luồng hoàn chỉnh từ đầu vào đến đầu ra
-   **Integration Testing**: Kiểm tra tương tác giữa các module
-   **Performance Testing**: Kiểm tra hiệu suất, FPS, thời gian xử lý
-   **Real-world Scenarios**: Kiểm tra với dữ liệu và tình huống thực tế

---

## 1. Video Processing System

### 1.1. Xác định phân vùng

**Chức năng được test:** Xử lý video từ file hoặc webcam, phát hiện người, đếm số lượng, cảnh báo, và lưu log

**Các phân vùng theo nguồn input:**

```
          Valid              Valid              Invalid
             |                 |                  |
    ─────────┼─────────────────┼──────────────────┼─────────
          Video file         Webcam            Invalid source
             |                 |                  |
        Partition V1       Partition V2       Partition V3
      (File video)        (Stream webcam)    (Nguồn lỗi)
```

**Các phân vùng theo chất lượng video:**

```
          Valid              Valid              Valid              Invalid
             |                 |                  |                  |
    ─────────┼─────────────────┼──────────────────┼──────────────────┼─────────
         Low quality        Medium quality     High quality      Corrupted
        (320x240, <20fps)  (640x480, 25fps)  (1920x1080, 30fps)  (Invalid)
             |                 |                  |                  |
        Partition Q1       Partition Q2       Partition Q3       Partition Q4
```

**Các phân vùng theo số lượng người trong video:**

```
          Valid              Valid              Valid              Valid
             |                 |                  |                  |
    ─────────┼─────────────────┼──────────────────┼──────────────────┼─────────
             0               1-5                6-10             >10 (vượt ngưỡng)
             |                 |                  |                  |
        Partition N0       Partition N1       Partition N2       Partition N3
      (Không có người)   (Ít người)         (Vừa phải)         (Đông người, cảnh báo)
```

### 1.2. Bảng Test Cases - Video Processing

| TC        | Phân vùng        | Giá trị Input                                                     | Kết quả Output mong đợi                                                                         |
| --------- | ---------------- | ----------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| **STC1**  | V1 + Q2 + N0     | Video file 640x480, 10s, không có người                           | Xử lý thành công, FPS ≥ 20, person_count=0 cho tất cả frames, không có cảnh báo                 |
| **STC2**  | V1 + Q2 + N1     | Video file 640x480, 10s, 1-3 người xuất hiện                      | Phát hiện đúng số người, log ghi nhận person_count=[1,2,3], không cảnh báo                      |
| **STC3**  | V1 + Q2 + N3     | Video file 640x480, 10s, 15 người (vượt ngưỡng 10)                | Phát hiện đúng 15 người, AlertSystem kích hoạt, tạo cảnh báo emergency, lưu alert log           |
| **STC4**  | V1 + Q1          | Video file 320x240, low quality, 5s, 2 người                      | Xử lý thành công nhưng FPS có thể thấp, vẫn phát hiện được người (có thể không chính xác 100%)  |
| **STC5**  | V1 + Q3          | Video file 1920x1080 HD, 5s, 3 người                              | Xử lý thành công, FPS ≥ 15, phát hiện người chính xác cao                                       |
| **STC6**  | V3 (invalid)     | Video file không tồn tại hoặc đường dẫn sai                       | Raise exception hoặc return error, không crash                                                  |
| **STC7**  | V1 + Transition  | Video 30s: 0-10s (0 người) → 10-20s (5 người) → 20-30s (15 người) | Đếm đúng từng giai đoạn, max_count=15, có cảnh báo khi vượt ngưỡng, average_count phản ánh đúng |
| **STC8**  | V1 + Occlusion   | Video có người bị che khuất một phần (occlusion)                  | Vẫn phát hiện được người (có thể bị mất 1-2 detection tùy mức che khuất)                        |
| **STC9**  | V1 + Fast motion | Video có người di chuyển nhanh                                    | Vẫn xử lý được, có thể có frame bỏ sót nhưng không crash                                        |
| **STC10** | V1 + Dark scene  | Video cảnh tối (low lighting)                                     | Xử lý được nhưng độ chính xác detection giảm, không crash                                       |

---

## 2. Alert System Integration

### 2.1. Xác định phân vùng

**Chức năng được test:** Tích hợp AlertSystem với PersonCounter trong luồng xử lý thực tế

**Các phân vùng theo kịch bản cảnh báo:**

```
          Valid              Valid              Valid              Valid
             |                 |                  |                  |
    ─────────┼─────────────────┼──────────────────┼──────────────────┼─────────
       No trigger          Warning             Critical          Emergency
      count ≤ 10         count 11-12          count 13-15        count > 15
             |                 |                  |                  |
        Partition A1       Partition A2       Partition A3       Partition A4
```

### 2.2. Bảng Test Cases - Alert Integration

| TC        | Phân vùng | Giá trị Input                                                         | Kết quả Output mong đợi                                                               |
| --------- | --------- | --------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| **STC11** | A1        | Video với person_count luôn ≤ 10                                      | Không có cảnh báo nào được tạo, alert_history rỗng, is_alert_active=False             |
| **STC12** | A2        | Video: count tăng từ 8 → 11 → 12 → 10                                 | Tạo warning alert khi 11-12, sau đó info alert khi về 10 (normalized)                 |
| **STC13** | A3        | Video: count tăng từ 10 → 13 → 15 → 12                                | Tạo critical alert khi 13-15, severity đúng, alert log được lưu                       |
| **STC14** | A4        | Video: count tăng từ 10 → 18 (emergency)                              | Tạo emergency alert, excess_count=8, history có record, save_alert_log() thành công   |
| **STC15** | Cooldown  | Video: count 15 → trigger alert → 2s sau vẫn 15                       | Alert đầu ghi history, alert thứ 2 trong cooldown không ghi history (spam prevention) |
| **STC16** | Toggle    | Bật alert → video 15 người → tắt alert → video 15 người               | Lần 1: có alert; Lần 2: không alert                                                   |
| **STC17** | Threshold | set_max_count(15) → video 12 người → set_max_count(10) → replay video | Lần 1: không alert (12 < 15); Lần 2: có alert (12 > 10)                               |
| **STC18** | Multiple  | Video 60s với nhiều lần vượt ngưỡng (10 → 15 → 8 → 18 → 5)            | Tất cả alerts được ghi đúng, stats cho thấy đúng số lượng alerts, max_person_count=18 |

---

## 3. Data Logging Integration

### 3.1. Xác định phân vùng

**Chức năng được test:** Tích hợp DataLogger với PersonCounter, ghi log liên tục trong quá trình xử lý

**Các phân vùng theo chế độ logging:**

```
          Valid              Valid              Valid
             |                 |                  |
    ─────────┼─────────────────┼──────────────────┼─────────
        Buffered          Immediate           Disabled
      (buffer mode)    (immediate mode)     (enabled=False)
             |                 |                  |
        Partition L1       Partition L2       Partition L3
```

### 3.2. Bảng Test Cases - Data Logging Integration

| TC        | Phân vùng | Giá trị Input                                                | Kết quả Output mong đợi                                                                    |
| --------- | --------- | ------------------------------------------------------------ | ------------------------------------------------------------------------------------------ |
| **STC19** | L1        | Video 30s, log_data() mỗi 5 frames, save_to_csv() cuối video | CSV file có đúng số dòng (≈ total_frames/5), dữ liệu đầy đủ 11 cột, order đúng             |
| **STC20** | L2        | Video 30s, save_immediate() mỗi frame                        | CSV file có đúng total_frames dòng, không bỏ sót dữ liệu                                   |
| **STC21** | L3        | Video 30s, enabled=False                                     | CSV file không được tạo hoặc empty, buffer length = 0                                      |
| **STC22** | Order     | Video 30s, log theo thứ tự person_count=[5,10,15,20,15,10,5] | CSV có 7 dòng với person_count theo đúng thứ tự, timestamp tăng dần                        |
| **STC23** | Stats     | Video 30s → load_data() → get_summary_stats()                | Stats đúng: total_records, max_person_count, avg_person_count, avg_fps, total_running_time |
| **STC24** | Export    | Video 30s → save_to_csv() → export_to_excel()                | File Excel được tạo, có đủ dữ liệu, format đúng 11 cột                                     |
| **STC25** | Rounding  | Video với fps=30.789, detection_rate=0.8234, avg_count=7.567 | CSV lưu đúng format: fps=30.79, rate=0.823, avg=7.57 (đã làm tròn)                         |
| **STC26** | Clear     | Video 10s → log data → clear_data() → video 10s tiếp         | Sau clear: CSV chỉ có header, sau video 2: CSV có dữ liệu mới (không còn dữ liệu cũ)       |

---

## 4. End-to-End Full System

### 4.1. Xác định phân vùng

**Chức năng được test:** Toàn bộ hệ thống hoạt động cùng lúc (Detection + Counting + Alert + Logging)

**Các phân vùng theo kịch bản thực tế:**

```
          Valid              Valid              Valid              Valid
             |                 |                  |                  |
    ─────────┼─────────────────┼──────────────────┼──────────────────┼─────────
      Normal scene        Crowded scene      Empty scene        Edge cases
     (1-10 người)         (>10 người)        (0 người)        (nhiễu, tối, mờ)
             |                 |                  |                  |
        Partition S1       Partition S2       Partition S3       Partition S4
```

### 4.2. Bảng Test Cases - Full System E2E

| TC        | Phân vùng | Giá trị Input                                                  | Kết quả Output mong đợi                                                                              |
| --------- | --------- | -------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| **STC27** | S1        | Video 60s, 3-8 người, tất cả modules bật                       | Detection OK, counting chính xác, không alert, CSV log đầy đủ, FPS ≥ 20                              |
| **STC28** | S2        | Video 60s, 15-20 người (vượt ngưỡng), tất cả modules bật       | Detection OK, alert emergency được tạo và lưu, CSV log có person_count=15-20, history có alerts      |
| **STC29** | S3        | Video 60s, 0 người (empty scene), tất cả modules bật           | Không crash, person_count=0 cho tất cả frames, detection_rate=0.0, không alert, CSV log đúng         |
| **STC30** | S4        | Video với nhiễu, mờ, tối, người bị che khuất                   | Hệ thống vẫn chạy, có thể có detection không chính xác nhưng không crash, log được lưu               |
| **STC31** | Duration  | Video dài 5 phút (300s)                                        | Xử lý hoàn tất không crash, memory không leak, log file size hợp lý, FPS stable                      |
| **STC32** | Restart   | Chạy video 1 → stop → reset_stats() → chạy video 2             | Video 2 bắt đầu với stats sạch (count=0, history rỗng), không bị ảnh hưởng bởi video 1               |
| **STC33** | Config    | Đổi config giữa chừng: confidence=0.5 → 0.7, max_count=10 → 15 | Config mới được áp dụng ngay, detection và alert thay đổi theo                                       |
| **STC34** | Multi-run | Chạy 3 video liên tiếp mà không restart                        | Mỗi video có stats riêng nếu reset, hoặc stats cộng dồn nếu không reset, không bị conflict           |
| **STC35** | Export    | Video 60s → lưu tất cả logs → export alert log + CSV + Excel   | 3 files được tạo: alert_log.txt (có alerts), data.csv (có records), data.xlsx (Excel format)         |
| **STC36** | Error     | Video bị corrupt ở giữa (50% video OK, 50% lỗi)                | Xử lý được phần OK, detect lỗi ở phần corrupt, log phần đã xử lý, raise exception có message rõ ràng |

---

## 5. Performance Testing

### 5.1. Xác định phân vùng

**Chức năng được test:** Hiệu suất xử lý, FPS, thời gian phản hồi, resource usage

**Các phân vùng theo FPS requirement:**

```
          Invalid            Valid              Valid              Valid
             |                 |                  |                  |
    ─────────┼─────────────────┼──────────────────┼──────────────────┼─────────
           < 15              15-20              20-30              > 30
             |                 |                  |                  |
        Partition P1       Partition P2       Partition P3       Partition P4
      (Không đạt)        (Chấp nhận được)     (Tốt)            (Rất tốt)
```

### 5.2. Bảng Test Cases - Performance

| TC        | Phân vùng     | Giá trị Input                                 | Kết quả Output mong đợi                                                          |
| --------- | ------------- | --------------------------------------------- | -------------------------------------------------------------------------------- |
| **STC37** | P3 (640x480)  | Video 640x480, 30s, 5 người                   | FPS ≥ 20, processing time ≤ 30s, CPU < 80%, memory stable                        |
| **STC38** | P2 (1280x720) | Video 1280x720 HD, 30s, 5 người               | FPS ≥ 15, processing time ≤ 40s, vẫn xử lý được                                  |
| **STC39** | P4 (320x240)  | Video 320x240 low res, 30s, 5 người           | FPS ≥ 30 (rất nhanh vì resolution thấp)                                          |
| **STC40** | Load test     | Video 60s, 20 người (nhiều detection)         | FPS ≥ 15, không giảm quá nhiều so với video ít người, memory không tăng liên tục |
| **STC41** | Long duration | Video 10 phút (600s)                          | FPS stable suốt quá trình, memory không leak, log file size tăng tuyến tính      |
| **STC42** | Batch         | Xử lý 10 video ngắn (mỗi video 10s) liên tiếp | Mỗi video có FPS ≥ 20, tổng thời gian ≤ 120s, không crash giữa chừng             |
| **STC43** | Real-time     | Webcam stream 60s (giả lập)                   | FPS ≥ 20, latency < 100ms, display mượt không giật lag                           |

---

## 6. Integration Testing (Module Interactions)

### 6.1. Xác định phân vùng

**Chức năng được test:** Tương tác giữa các module: PersonDetector → PersonCounter → AlertSystem → DataLogger

**Sơ đồ luồng:**

```
PersonDetector.detect_persons(frame)
         ↓
PersonCounter.update_count(detections)
         ↓
AlertSystem.check_alert(person_count)
         ↓
DataLogger.log_data(stats)
```

### 6.2. Bảng Test Cases - Module Integration

| TC        | Phân vùng         | Giá trị Input                                              | Kết quả Output mong đợi                                                                  |
| --------- | ----------------- | ---------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| **STC44** | Detector→Counter  | Detection trả về 5 boxes → update_count()                  | PersonCounter có current_count=5, total_detections tăng 5                                |
| **STC45** | Counter→Alert     | PersonCounter có count=15 → check_alert()                  | AlertSystem tạo emergency alert, is_active=True                                          |
| **STC46** | Alert→Logger      | Alert được tạo → log_data() với alert_status               | DataLogger ghi record có thông tin alert (nếu có field tương ứng)                        |
| **STC47** | Full pipeline     | Frame → detect → count → alert → log (1 cycle hoàn chỉnh)  | Tất cả modules hoạt động đúng, data flow từ đầu đến cuối, không mất dữ liệu              |
| **STC48** | Error propagation | PersonDetector raise exception → kiểm tra các module sau   | Exception được handle, các module khác không bị crash, log có error message              |
| **STC49** | State consistency | 100 frames xử lý liên tục → check state của tất cả modules | Counter history=100, Alert có đúng số alerts, Logger có đúng số records, không bị desync |
| **STC50** | Reset cascade     | reset PersonCounter → kiểm tra AlertSystem và DataLogger   | Tất cả modules đều reset (nếu thiết kế cascade) hoặc độc lập (nếu thiết kế isolated)     |

---

## 7. Bảng quyết định (Decision Table) - System Level

### 7.1. Decision Table cho Video Processing System

| Conditions / Rules     | R1   | R2   | R3   | R4  | R5  | R6  | R7  | R8   |
| ---------------------- | ---- | ---- | ---- | --- | --- | --- | --- | ---- |
| **Video source valid** | T    | T    | T    | T   | T   | T   | T   | F    |
| **Person count = 0**   | T    | F    | F    | F   | F   | F   | F   | -    |
| **Person count 1-10**  | F    | T    | F    | F   | F   | F   | F   | -    |
| **Person count > 10**  | F    | F    | T    | T   | T   | T   | T   | -    |
| **Alert enabled**      | T    | T    | T    | T   | F   | T   | T   | -    |
| **Logging enabled**    | T    | T    | T    | F   | T   | F   | F   | -    |
| **Actions:**           |      |      |      |     |     |     |     |      |
| Process video          | ✓    | ✓    | ✓    | ✓   | ✓   | ✓   | ✓   |      |
| Detect persons         | ✓    | ✓    | ✓    | ✓   | ✓   | ✓   | ✓   |      |
| Update counter         | ✓    | ✓    | ✓    | ✓   | ✓   | ✓   | ✓   |      |
| Create alert           |      |      | ✓    | ✓   |     |     |     |      |
| Log to CSV             | ✓    | ✓    | ✓    |     | ✓   |     |     |      |
| Save alert log         |      |      | ✓    | ✓   |     |     |     |      |
| Raise error            |      |      |      |     |     |     |     | ✓    |
| **Test Cases:**        | STC1 | STC2 | STC3 | -   | -   | -   | -   | STC6 |

### 7.2. Decision Table cho Alert Integration

| Conditions / Rules        | R1    | R2    | R3    | R4    | R5    | R6    |
| ------------------------- | ----- | ----- | ----- | ----- | ----- | ----- |
| **count ≤ max_count**     | T     | F     | F     | F     | F     | F     |
| **count > max_count**     | F     | T     | T     | T     | T     | T     |
| **Severity: warning**     | -     | T     | F     | F     | F     | F     |
| **Severity: critical**    | -     | F     | T     | F     | F     | F     |
| **Severity: emergency**   | -     | F     | F     | T     | T     | T     |
| **In cooldown**           | -     | F     | F     | F     | T     | F     |
| **Alert enabled**         | T     | T     | T     | T     | T     | F     |
| **Actions:**              |       |       |       |       |       |       |
| No alert                  | ✓     |       |       |       |       | ✓     |
| Create warning            |       | ✓     |       |       |       |       |
| Create critical           |       |       | ✓     |       |       |       |
| Create emergency          |       |       |       | ✓     |       |       |
| Add to history            |       | ✓     | ✓     | ✓     |       |       |
| Return alert (no history) |       |       |       |       | ✓     |       |
| **Test Cases:**           | STC11 | STC12 | STC13 | STC14 | STC15 | STC16 |

---

## 8. Mapping System Test Cases với Implementation

### 8.1. System Tests Structure

```
tests/system/
├── __init__.py
├── SYSTEM_TEST_CASES.md (tài liệu này)
├── system_test.py (implementation)
├── conftest.py (fixtures)
└── test_data/ (sample videos)
    ├── empty_scene.mp4
    ├── normal_scene.mp4
    ├── crowded_scene.mp4
    └── test_video.mp4
```

### 8.2. Test Cases Mapping

| System TC | Test Function Name                | Module Tested                               |
| --------- | --------------------------------- | ------------------------------------------- |
| STC1-10   | `test_video_processing_*`         | Video processing với các kịch bản khác nhau |
| STC11-18  | `test_alert_integration_*`        | Alert system tích hợp với video processing  |
| STC19-26  | `test_data_logging_integration_*` | Data logging tích hợp với video processing  |
| STC27-36  | `test_end_to_end_*`               | Full system end-to-end testing              |
| STC37-43  | `test_performance_*`              | Performance và load testing                 |
| STC44-50  | `test_module_integration_*`       | Module interactions và data flow            |

### 8.3. Tổng kết System Test Cases

| Category                 | Số Test Cases | Độ ưu tiên | Complexity |
| ------------------------ | ------------- | ---------- | ---------- |
| Video Processing         | 10            | HIGH       | Medium     |
| Alert Integration        | 8             | HIGH       | Medium     |
| Data Logging Integration | 8             | MEDIUM     | Low        |
| End-to-End Full System   | 10            | CRITICAL   | High       |
| Performance Testing      | 7             | MEDIUM     | High       |
| Module Integration       | 7             | HIGH       | Medium     |
| **TỔNG CỘNG**            | **50**        | -          | -          |

---

## 9. Chạy System Tests

### Chạy tất cả system tests

```bash
pytest tests/system/ -v
```

### Chạy từng category

```bash
pytest tests/system/system_test.py::TestVideoProcessing -v
pytest tests/system/system_test.py::TestAlertIntegration -v
pytest tests/system/system_test.py::TestEndToEnd -v
```

### Chạy với performance report

```bash
pytest tests/system/ -v --durations=10
```

### Chạy với coverage

```bash
pytest tests/system/ --cov=src --cov-report=html
```

---

## 10. Yêu cầu cho System Tests

### 10.1. Test Data Requirements

-   **Video files**: Cần có ít nhất 5 video mẫu với các kịch bản khác nhau
-   **Video duration**: 10-60 giây (không quá dài để tests chạy nhanh)
-   **Video quality**: Các resolution khác nhau (320x240, 640x480, 1920x1080)
-   **Content**: Empty scene, 1-5 người, 10+ người, người di chuyển nhanh, etc.
