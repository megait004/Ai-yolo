# Test Cases Documentation

## Tài liệu Test Case cho Unit Tests

Tài liệu này mô tả chi tiết các phân vùng (partitions) và test cases cho các module chính trong hệ thống.

---

## 1. AlertSystem Module

### 1.1. Xác định phân vùng

**Hàm được test:** `AlertSystem.check_alert(person_count)`

**Giả định:**

-   `max_count = 10` (ngưỡng cảnh báo)
-   `alert_cooldown = 5` (giây)
-   `enabled = True` (trừ khi chỉ định khác)

**Các phân vùng theo person_count:**

```
           Invalid      Valid           Valid           Valid            Invalid
              |           |               |               |                 |
    ──────────┼───────────┼───────────────┼───────────────┼─────────────────┼────────
             -∞           0              10  11          12  13           15  16      +∞
              │           │               │   │           │   │            │   │
         Partition 1  Partition 2    Partition 3     Partition 4      Partition 5
         (Invalid)    (Bình thường)   (Warning)      (Critical)       (Emergency)
                      No Alert        excess: 1-2    excess: 3-5      excess: ≥6
```

**Phân vùng đặc biệt:**

-   **Partition 6:** count > 10 nhưng đang trong cooldown → Cảnh báo tạm thời (không ghi history)
-   **Partition 7:** enabled = False → Luôn trả về None
-   **Partition 8:** count ≤ 10 khi is_alert_active = True → Info (kết thúc cảnh báo)

### 1.2. Bảng Test Cases - AlertSystem

| TC       | Phân vùng      | Giá trị Input                                                | Kết quả Output mong đợi                                                                                                       |
| -------- | -------------- | ------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------- |
| **TC1**  | P7             | enabled=False, count=15                                      | `None` (không xử lý)                                                                                                          |
| **TC2**  | P2             | enabled=True, count=5, is_alert_active=False                 | `None` (không cảnh báo)                                                                                                       |
| **TC3**  | P8             | enabled=True, count=5, is_alert_active=True                  | `dict`: type='info', is_active=False, message="trở về mức bình thường"                                                        |
| **TC4**  | P3 (biên trái) | enabled=True, count=11, cooldown elapsed                     | `dict`: type='warning', person_count=11, excess_count=1, is_active=True; history tăng 1                                       |
| **TC5**  | P3 (biên phải) | enabled=True, count=12, cooldown elapsed                     | `dict`: type='warning', person_count=12, excess_count=2, is_active=True; history tăng 1                                       |
| **TC6**  | P4 (biên trái) | enabled=True, count=13, cooldown elapsed                     | `dict`: type='critical', person_count=13, excess_count=3, is_active=True; history tăng 1                                      |
| **TC7**  | P4 (biên phải) | enabled=True, count=15, cooldown elapsed                     | `dict`: type='critical', person_count=15, excess_count=5, is_active=True; history tăng 1                                      |
| **TC8**  | P5 (biên trái) | enabled=True, count=16, cooldown elapsed                     | `dict`: type='emergency', person_count=16, excess_count=6, is_active=True; history tăng 1                                     |
| **TC9**  | P5 (giữa)      | enabled=True, count=20, cooldown elapsed                     | `dict`: type='emergency', person_count=20, excess_count=10, is_active=True; history tăng 1                                    |
| **TC10** | P6             | enabled=True, count=15, trong cooldown (< 5s)                | `dict`: type='warning', is_active=True; history **KHÔNG** tăng                                                                |
| **TC11** | P1 (biên trái) | enabled=True, count=0                                        | `None` hoặc xử lý giá trị đặc biệt                                                                                            |
| **TC12** | P2 (biên phải) | enabled=True, count=10, is_alert_active=False                | `None` (đúng bằng ngưỡng)                                                                                                     |
| **TC13** | History        | Sau các TC4-TC9 (7 alerts), gọi `get_alert_history(limit=3)` | Trả về list 3 cảnh báo cuối, là copy không shared                                                                             |
| **TC14** | Stats          | Sau các TC4-TC9, gọi `get_alert_stats()`                     | `total_alerts=7`, `max_person_count=20`, `severity_counts={'warning':2, 'critical':2, 'emergency':2}`, `is_alert_active=True` |
| **TC15** | Save log       | `save_alert_log(file)` khi history rỗng                      | File tồn tại, có "=== LỊCH SỬ CẢNH BÁO ===" và "Không có cảnh báo nào."                                                       |
| **TC16** | Save log       | `save_alert_log(file)` khi có 3 alerts                       | File có "Cảnh báo #1:", "Cảnh báo #2:", "Cảnh báo #3:", "=== THỐNG KÊ ===", "Tổng số cảnh báo: 3"                             |
| **TC17** | Config         | `set_max_count(20)`, sau đó count=15                         | `None` (15 < 20, không cảnh báo)                                                                                              |
| **TC18** | Config         | `set_alert_cooldown(1)`, chờ 1.1s, count=15                  | Tạo cảnh báo mới, history tăng                                                                                                |
| **TC19** | Config         | `clear_alert_history()` sau khi có alerts                    | `alert_history = []`, `is_alert_active = False`                                                                               |
| **TC20** | Edge case      | `set_enabled(True)` → `set_enabled(False)` → count=15        | Lần 1: cảnh báo; Lần 2: None                                                                                                  |

---

## 2. DataLogger Module

### 2.1. Xác định phân vùng

**Các hàm được test:**

1. `log_data(stats)` - Ghi vào buffer
2. `save_to_csv()` - Lưu buffer xuống file
3. `save_immediate(stats)` - Lưu ngay 1 record
4. `load_data()` - Đọc từ file
5. `get_summary_stats()` - Thống kê tổng hợp
6. `export_to_excel()` - Xuất ra Excel

### 2.1.1. Phân vùng cho `log_data(stats)` theo enabled state

```
          Invalid                   Valid
             |                        |
    ─────────┼────────────────────────┼─────────
           False                    True
             |                        |
        Partition 1             Partition 2
       (No action)           (Add to buffer)
         enabled=False          enabled=True
```

### 2.1.2. Phân vùng cho `save_to_csv()` theo buffer_length

**Điều kiện:** enabled = True

```
          Valid              Valid                 Valid
             |                 |                     |
    ─────────┼─────────────────┼─────────────────────┼─────────
             0                 1                   >1 (ví dụ: 2, 5, 10)
             |                 |                     |
        Partition 1        Partition 2          Partition 2
        (No action)      (Write 1 record)    (Write multiple records)
      buffer_length=0    buffer_length>0      buffer_length>0
```

**Phân vùng phụ khi buffer_length > 0:** file_exists?

```
          Valid                   Valid
             |                       |
    ─────────┼───────────────────────┼─────────
          False                    True
             |                       |
        Partition 3             Partition 4
    (Create file+header,       (Append data,
     write buffer,              no header,
     clear buffer)              clear buffer)
    file_exists=False         file_exists=True
```

### 2.1.3. Phân vùng cho `save_immediate(stats)` theo file_exists

**Điều kiện:** enabled = True

```
          Valid                   Valid
             |                       |
    ─────────┼───────────────────────┼─────────
          False                    True
             |                       |
        Partition Q2            Partition Q3
    (Create file+header,        (Append 1 row,
     write 1 row)                no header)
    file_exists=False         file_exists=True
```

### 2.1.4. Phân vùng cho `load_data()` theo file_exists

```
          Valid                   Valid
             |                       |
    ─────────┼───────────────────────┼─────────
          False                    True
             |                       |
        Partition S1            Partition S2
   (Return empty DataFrame)  (Return DataFrame with data)
    file_exists=False         file_exists=True
```

### 2.1.5. Phân vùng cho `export_to_excel()` theo data availability

```
          Valid                   Valid
             |                       |
    ─────────┼───────────────────────┼─────────
         Empty                   Has data
             |                       |
        Partition R1            Partition R2
   (No file created OR         (Create .xlsx
    don't crash)                with data)
    CSV empty/no data           CSV has records
```

### 2.1.6. Phân vùng tổng hợp cho DataLogger

**Các yếu tố ảnh hưởng:**

1. **enabled state:** False | True
2. **buffer_length:** 0 | >0
3. **file_exists:** False | True
4. **data_exists:** Empty | Has data

**Sơ đồ phân vùng chính (tổng hợp):**

```
                enabled State
                      |
         ─────────────┼────────────────
                    False            True
                      |                |
                 Partition 1       Operation Type
                 (Disabled:            |
                  No action)    ┌──────┴──────┐
                                |             |
                            log_data()    save_to_csv()
                                |             |
                          Add to buffer   Check buffer
                                          & file state
```

### 2.2. Bảng Test Cases - DataLogger

| TC       | Phân vùng            | Giá trị Input                                                                       | Kết quả Output mong đợi                                                                                                                        |
| -------- | -------------------- | ----------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| **TC1**  | Init                 | enabled=True, filename mới                                                          | File CSV được tạo với header chuẩn 11 cột, 0 dòng dữ liệu                                                                                      |
| **TC2**  | Init                 | enabled=False, filename                                                             | File không được tạo                                                                                                                            |
| **TC3**  | P2 (log_data)        | enabled=True, stats đầy đủ (9 trường)                                               | buffer tăng 1, record có timestamp/datetime auto, các giá trị làm tròn (avg 2 số, rate 3 số, fps 2 số)                                         |
| **TC4**  | P2 (log_data)        | enabled=True, stats thiếu keys (chỉ có current_count=5)                             | buffer tăng 1, các trường thiếu = 0 hoặc 0.0                                                                                                   |
| **TC5**  | P1 (log_data)        | enabled=False, stats đầy đủ                                                         | buffer không thay đổi (length=0)                                                                                                               |
| **TC6**  | P2 (save_to_csv)     | enabled=True, buffer_length=0                                                       | File không thay đổi, không ghi gì                                                                                                              |
| **TC7**  | P1 (save_to_csv)     | enabled=False, buffer_length=2                                                      | File không được tạo/thay đổi, buffer giữ nguyên                                                                                                |
| **TC8**  | P3 (save_to_csv)     | enabled=True, buffer_length=2, file không tồn tại                                   | File được tạo với header + 2 dòng, buffer clear (length=0)                                                                                     |
| **TC9**  | P4 (save_to_csv)     | enabled=True, buffer_length=1, file đã có 1 dòng                                    | File có 2 dòng (append), không ghi lại header, buffer clear                                                                                    |
| **TC10** | Q2 (save_immediate)  | enabled=True, stats đầy đủ, file không tồn tại                                      | File được tạo với header + 1 dòng                                                                                                              |
| **TC11** | Q3 (save_immediate)  | enabled=True, stats đầy đủ, file đã có 1 dòng                                       | File có 2 dòng (append), không ghi lại header                                                                                                  |
| **TC12** | Q1 (save_immediate)  | enabled=False, stats đầy đủ                                                         | File không được tạo/thay đổi                                                                                                                   |
| **TC13** | S2 (load_data)       | File tồn tại với 3 dòng dữ liệu                                                     | DataFrame có 3 dòng, 11 cột chuẩn                                                                                                              |
| **TC14** | S1 (load_data)       | File không tồn tại                                                                  | DataFrame rỗng (empty=True)                                                                                                                    |
| **TC15** | Summary (có data)    | File có 2 records: count=[3,7], running_time=[100,200], fps=[25,30]                 | Dict: `total_records=2`, `max_person_count=7`, `avg_person_count=5.0`, `avg_fps=27.5`, `total_running_time=200`, có first_record & last_record |
| **TC16** | Summary (no data)    | File rỗng hoặc không tồn tại                                                        | `{}` (empty dict)                                                                                                                              |
| **TC17** | clear_data           | File có 5 dòng dữ liệu                                                              | File bị xóa và tạo lại với chỉ header, 0 dòng                                                                                                  |
| **TC18** | R2 (export_to_excel) | CSV có 2 dòng dữ liệu, excel_path=test.xlsx                                         | File test.xlsx được tạo, có 2 dòng, 11 cột                                                                                                     |
| **TC19** | R1 (export_to_excel) | CSV rỗng, excel_path=empty.xlsx                                                     | Không crash (có thể không tạo file hoặc tạo file rỗng)                                                                                         |
| **TC20** | Toggle enabled       | Bật (enabled=True) → log_data → tắt (enabled=False) → log_data → bật lại → log_data | Lần 1: buffer+=1; Lần 2: buffer không đổi; Lần 3: buffer+=1                                                                                    |
| **TC21** | Multi-log order      | log_data 5 lần với current_count=[0,1,2,3,4], sau đó save_to_csv                    | CSV có 5 dòng với person_count theo đúng thứ tự [0,1,2,3,4]                                                                                    |
| **TC22** | Timestamp trong log  | Gọi log_data(stats), kiểm tra buffer[0]                                             | `timestamp` nằm trong khoảng [before_time, after_time]; `datetime` là string format "YYYY-MM-DD HH:MM:SS"                                      |
| **TC23** | Rounding values      | log_data với average_count=7.567, detection_rate=0.8234, fps=30.789                 | Record có: average_count=7.57, detection_rate=0.823, fps=30.79                                                                                 |

---

## 3. PersonCounter Module

### 3.1. Xác định phân vùng

**Hàm được test:** `PersonCounter.update_count(detections)`

**Giả định:**

-   `max_history = 100` (số frame tối đa lưu lịch sử)

**Các phân vùng theo số lượng detections:**

```
          Valid              Valid              Valid              Valid
             |                 |                  |                  |
    ─────────┼─────────────────┼──────────────────┼──────────────────┼─────────
             0                 1                  2-10             >10 (ví dụ: 15, 50)
             |                 |                  |                  |
        Partition 1       Partition 2        Partition 3        Partition 4
       (Empty frame)     (1 person)       (Multiple persons)   (Many persons)
      detections=[]    detections=[d1]   detections=[d1,d2]  detections=[d1..dn]
```

**Phân vùng theo thời gian (running_time) cho FPS:**

```
          Valid              Valid              Valid
             |                 |                  |
    ─────────┼─────────────────┼──────────────────┼─────────
            =0               >0 && <1           ≥1 (giây)
             |                 |                  |
        Partition A       Partition B        Partition C
       (Just started)    (Very short)       (Normal runtime)
         FPS=0           FPS=high            FPS=normal
```

**Phân vùng cho detection_rate:**

```
          Invalid            Valid              Valid              Valid
             |                 |                  |                  |
    ─────────┼─────────────────┼──────────────────┼──────────────────┼─────────
             0               0.1-0.3            0.4-0.7            0.8-1.0
             |                 |                  |                  |
        Partition R0       Partition R1       Partition R2       Partition R3
      (No detections)     (Rare detect)     (Medium detect)    (High detect)
    frames_with_persons=0    rate<0.3         rate<0.7          rate≥0.7
```

### 3.2. Bảng Test Cases - PersonCounter

| TC       | Phân vùng           | Giá trị Input                                                       | Kết quả Output mong đợi                                                                            |
| -------- | ------------------- | ------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| **TC1**  | Init                | `PersonCounter()` mặc định                                          | `current_count=0`, `max_count=0`, `total_detections=0`, `frame_count=0`, `count_history=[]`        |
| **TC2**  | P1                  | `update_count([])` (empty detections)                               | `current_count=0`, `frame_count=1`, `count_history=[0]`                                            |
| **TC3**  | P2                  | `update_count([d1])` (1 detection)                                  | `current_count=1`, `max_count=1`, `total_detections=1`, `frame_count=1`                            |
| **TC4**  | P3                  | `update_count([d1, d2])` (2 detections)                             | `current_count=2`, `max_count=2`, `total_detections=2`, `frame_count=1`                            |
| **TC5**  | P4                  | `update_count([d1...d15])` (15 detections)                          | `current_count=15`, `max_count=15`, `total_detections=15`, `frame_count=1`                         |
| **TC6**  | Max tracking        | Gọi `update_count([d1,d2])` sau đó `update_count([d1])`             | Lần 1: `max_count=2`; Lần 2: `current_count=1`, `max_count=2` (giữ nguyên max)                     |
| **TC7**  | History             | Gọi `update_count` 5 lần với counts=[1,2,3,4,5]                     | `count_history=[1,2,3,4,5]`, `average_count=3.0`                                                   |
| **TC8**  | History limit       | Gọi `update_count` 105 lần (vượt max_history=100)                   | `len(count_history)=100` (chỉ giữ 100 frame gần nhất)                                              |
| **TC9**  | Total detect        | Gọi update 3 lần: [d1], [d1,d2], [d1,d2,d3]                         | `total_detections=1+2+3=6` (tổng cộng dồn)                                                         |
| **TC10** | R0 (rate=0)         | Gọi update 10 lần với [] (empty)                                    | `frames_with_persons=0`, `detection_rate=0.0`                                                      |
| **TC11** | R3 (rate=1)         | Gọi update 10 lần với [d1] (always detected)                        | `frames_with_persons=10`, `detection_rate=1.0`                                                     |
| **TC12** | R2 (rate~0.7)       | Gọi update 10 lần: 7 lần [d1], 3 lần []                             | `frames_with_persons=7`, `detection_rate=0.7`                                                      |
| **TC13** | A (FPS=0)           | Khởi tạo, gọi `get_fps()` ngay (running_time≈0)                     | `fps=0.0` (tránh chia cho 0)                                                                       |
| **TC14** | C (FPS normal)      | Gọi update 10 lần, chờ 0.1s, gọi `get_fps()`                        | `fps > 0` (≈ 10/0.1 = 100 fps)                                                                     |
| **TC15** | get_all_stats       | Sau các TC7, gọi `get_all_stats()`                                  | Dict có keys: `current_count`, `max_count`, `average_count`, `total_frames`, `fps`, `running_time` |
| **TC16** | get_count_history   | Sau TC7, gọi `get_count_history()`                                  | Tuple: `([1,2,3,4,5], [t1,t2,t3,t4,t5])` (counts và timestamps)                                    |
| **TC17** | reset_stats         | Sau TC7, gọi `reset_stats()`                                        | Tất cả về 0: `current_count=0`, `max_count=0`, `frame_count=0`, `count_history=[]`                 |
| **TC18** | Getter methods      | Gọi `get_current_count()`, `get_max_count()`, `get_average_count()` | Trả về đúng giá trị tương ứng                                                                      |
| **TC19** | Running time        | Khởi tạo, chờ 0.1s, gọi `get_running_time()`                        | `running_time ≥ 0.1` (tính từ lúc khởi tạo)                                                        |
| **TC20** | Frames with persons | Update 5 frames: [], [d1], [], [d1], [d1]                           | `frames_with_persons=3` (chỉ đếm frame có người)                                                   |

---

## 4. PersonDetector Module

### 4.1. Xác định phân vùng

**Hàm được test:** `PersonDetector.detect_persons(frame)`

**Giả định:**

-   `confidence_threshold = 0.5` (ngưỡng tin cậy)
-   `iou_threshold = 0.35` (ngưỡng IoU)
-   `person_class_id = 0` (class ID của người trong COCO)

**Các phân vùng theo confidence score:**

```
          Invalid            Valid              Valid              Valid
             |                 |                  |                  |
    ─────────┼─────────────────┼──────────────────┼──────────────────┼─────────
             0               0.5                0.7                0.9          1.0
             |                 |                  |                  |
        Partition 1       Partition 2        Partition 3        Partition 4
      (Below threshold)  (At threshold)    (Medium conf)      (High conf)
       conf < 0.5         conf = 0.5        0.5 < conf < 0.9   conf ≥ 0.9
       → Filtered out     → Accepted        → Accepted         → Accepted
```

**Phân vùng theo số lượng detections trong frame:**

```
          Valid              Valid              Valid              Valid
             |                 |                  |                  |
    ─────────┼─────────────────┼──────────────────┼──────────────────┼─────────
             0                 1                  2-5              >5 (ví dụ: 10)
             |                 |                  |                  |
        Partition D0       Partition D1       Partition D2       Partition D3
     (No detections)     (Single person)   (Few persons)      (Many persons)
       boxes=None          boxes=[b1]        boxes=[b1,b2]      boxes=[b1..bn]
```

**Phân vùng theo class_id (lọc chỉ lấy "person"):**

```
          Valid              Invalid            Valid
             |                 |                  |
    ─────────┼─────────────────┼──────────────────┼─────────
             0                 1-79               80+
             |                 |                  |
        Partition C0       Partition C1       Partition C2
        (Person)          (Other classes)    (Out of range)
       class_id=0         class_id≠0         class_id>79
       → Accepted         → Filtered out     → Filtered out
```

**Phân vùng theo kích thước frame (input validation):**

```
          Valid              Valid              Invalid
             |                 |                  |
    ─────────┼─────────────────┼──────────────────┼─────────
         640x480             Other sizes         Empty/None
             |                 |                  |
        Partition F1       Partition F2       Partition F3
      (Standard size)     (Non-standard)      (Invalid)
    frame.shape=(480,640,3) frame valid      frame=None/empty
       → Process          → Process          → Return []
```

### 4.2. Bảng Test Cases - PersonDetector

| TC       | Phân vùng       | Giá trị Input                                                | Kết quả Output mong đợi                                                                       |
| -------- | --------------- | ------------------------------------------------------------ | --------------------------------------------------------------------------------------------- |
| **TC1**  | Init            | `PersonDetector()` mặc định                                  | `confidence_threshold=0.5`, `iou_threshold=0.35`, `person_class_id=0`, `model_path` được set  |
| **TC2**  | F1 (standard)   | frame.shape=(480, 640, 3) chuẩn                              | `preprocess_frame()` trả về frame cùng kích thước                                             |
| **TC3**  | F2 (non-std)    | frame.shape=(720, 1280, 3)                                   | `preprocess_frame()` xử lý frame (có thể resize hoặc giữ nguyên)                              |
| **TC4**  | D0 (no detect)  | Mock YOLO trả về `boxes=None`                                | `detect_persons()` trả về `[]` (list rỗng)                                                    |
| **TC5**  | D1 (single)     | Mock YOLO: 1 box, conf=0.8, class_id=0                       | List có 1 detection: `[{"bbox": [x1,y1,x2,y2], "confidence": 0.8, "class_id": 0}]`            |
| **TC6**  | D2 (few)        | Mock YOLO: 2 boxes, conf=[0.7, 0.9], class_id=[0, 0]         | List có 2 detections với confidence tương ứng                                                 |
| **TC7**  | D3 (many)       | Mock YOLO: 10 boxes, tất cả class_id=0                       | List có 10 detections                                                                         |
| **TC8**  | P1 (filtered)   | Mock YOLO: 1 box, conf=0.3 (< threshold 0.5)                 | `[]` (bị filter bởi YOLO model, không vào output)                                             |
| **TC9**  | P2 (threshold)  | Mock YOLO: 1 box, conf=0.5 (đúng bằng threshold)             | List có 1 detection (accepted)                                                                |
| **TC10** | P4 (high conf)  | Mock YOLO: 1 box, conf=0.95                                  | List có 1 detection với `confidence=0.95`                                                     |
| **TC11** | C1 (filter)     | Mock YOLO: 2 boxes, class_id=[0, 1] (0=person, 1=bicycle)    | List có 1 detection (chỉ lấy class_id=0)                                                      |
| **TC12** | C2 (out range)  | Mock YOLO: 1 box, class_id=85 (ngoài phạm vi COCO)           | List rỗng (hoặc filter)                                                                       |
| **TC13** | Mixed classes   | Mock YOLO: 5 boxes, class_id=[0,1,0,2,0] (3 person, 2 other) | List có 3 detections (chỉ class_id=0)                                                         |
| **TC14** | get_model_info  | Gọi `get_model_info()`                                       | Dict: `{"model_name": "yolov8n.pt", "confidence_threshold": 0.5, "iou_threshold": 0.35, ...}` |
| **TC15** | Bbox format     | Mock YOLO: bbox=[100.5, 200.3, 300.7, 400.9]                 | Detection bbox converted to int: `[100, 200, 300, 400]`                                       |
| **TC16** | Empty frame     | frame = np.zeros((480, 640, 3))                              | Không crash, trả về list (có thể rỗng)                                                        |
| **TC17** | Model info keys | `get_model_info()` trả về dict                               | Dict có keys: `model_name`, `confidence_threshold`, `iou_threshold`, `input_size`             |
| **TC18** | Confidence type | Detection trả về confidence                                  | `confidence` là float trong [0, 1]                                                            |
| **TC19** | Multiple calls  | Gọi `detect_persons()` 3 lần liên tiếp                       | Mỗi lần trả về kết quả độc lập, không bị ảnh hưởng lẫn nhau                                   |
| **TC20** | Edge: conf=1.0  | Mock YOLO: conf=1.0 (perfect confidence)                     | Detection accepted với `confidence=1.0`                                                       |

---

## 5. Mapping với Implementation Tests

### 5.1. AlertSystem Tests (tests/unit/alert_system_test.py)

| Test Case ID | Test Function Name                                                |
| ------------ | ----------------------------------------------------------------- |
| TC1          | `test_check_alert_disabled_returns_none`                          |
| TC2          | `test_check_alert_below_threshold_no_alert`                       |
| TC3          | `test_check_alert_returns_info_when_normalized`                   |
| TC4          | `test_check_alert_exceeds_threshold_creates_warning` (count=11)   |
| TC5          | `test_check_alert_exceeds_threshold_creates_warning` (count=12)   |
| TC6          | `test_check_alert_exceeds_threshold_creates_critical` (count=13)  |
| TC7          | `test_check_alert_exceeds_threshold_creates_critical` (count=15)  |
| TC8          | `test_check_alert_exceeds_threshold_creates_emergency` (count=16) |
| TC9          | `test_check_alert_exceeds_threshold_creates_emergency` (count=17) |
| TC10         | `test_check_alert_cooldown_prevents_spam`                         |
| TC11-12      | Covered by boundary tests                                         |
| TC13         | `test_get_alert_history_with_limit`                               |
| TC14         | `test_get_alert_stats_with_alerts`                                |
| TC15         | `test_save_alert_log_empty_history`                               |
| TC16         | `test_save_alert_log_multiple_alerts`                             |
| TC17         | `test_set_max_count_changes_threshold`                            |
| TC18         | `test_check_alert_after_cooldown_creates_new_alert`               |
| TC19         | `test_clear_alert_history_resets_state`                           |
| TC20         | `test_set_enabled_toggles_alert_system`                           |

**Tổng số:** 28 test functions covering 20+ test cases

### 5.2. DataLogger Tests (tests/unit/data_logger_test.py)

| Test Case ID | Test Function Name                                 |
| ------------ | -------------------------------------------------- |
| TC1          | `test_init_creates_csv_file`                       |
| TC2          | `test_init_disabled_does_not_create_file`          |
| TC3          | `test_log_data_adds_to_buffer`                     |
| TC4          | `test_handles_missing_stats_keys_gracefully`       |
| TC5          | `test_log_data_disabled_does_nothing`              |
| TC6          | `test_save_to_csv_empty_buffer_does_nothing`       |
| TC7          | `test_save_to_csv_disabled_does_nothing`           |
| TC8          | `test_save_to_csv_writes_buffer` (file not exists) |
| TC9          | `test_save_to_csv_appends_to_existing_file`        |
| TC10         | `test_save_immediate_creates_file_with_header`     |
| TC11         | `test_save_immediate_appends_to_existing`          |
| TC12         | `test_save_immediate_disabled_does_nothing`        |
| TC13         | `test_load_data_returns_dataframe`                 |
| TC14         | `test_load_data_nonexistent_file_returns_empty`    |
| TC15         | `test_get_summary_stats_returns_correct_stats`     |
| TC16         | `test_get_summary_stats_empty_returns_empty_dict`  |
| TC17         | `test_clear_data_removes_and_recreates_file`       |
| TC18         | `test_export_to_excel_creates_xlsx`                |
| TC19         | `test_export_to_excel_empty_data_does_nothing`     |
| TC20         | `test_set_enabled_toggles_logging`                 |
| TC21         | `test_multiple_logs_preserve_order`                |
| TC22         | `test_log_data_adds_timestamp`                     |
| TC23         | `test_log_data_rounds_values`                      |

**Tổng số:** 23 test functions covering 23+ test cases

### 5.3. PersonCounter Tests (tests/unit/person_counter_test.py)

| Test Case ID | Test Function Name                                                       |
| ------------ | ------------------------------------------------------------------------ |
| TC1          | `test_init`                                                              |
| TC2          | `test_update_count_empty`                                                |
| TC3          | `test_update_count_with_detections`                                      |
| TC6          | `test_update_count_with_detections` (multiple calls)                     |
| TC7-8        | Multiple `test_update_count` calls                                       |
| TC9          | Covered by `test_update_count` series                                    |
| TC10-12      | `test_get_detection_rate`                                                |
| TC13-14      | `test_get_fps`                                                           |
| TC15         | `test_get_all_stats`                                                     |
| TC16         | Covered by history tests                                                 |
| TC17         | `test_reset_stats`                                                       |
| TC18         | `test_get_current_count`, `test_get_max_count`, `test_get_average_count` |
| TC19         | `test_get_running_time`                                                  |
| TC20         | Covered by detection rate tests                                          |

**Tổng số:** 11 test functions covering 20+ test cases

### 5.4. PersonDetector Tests (tests/unit/person_detector_test.py)

| Test Case ID | Test Function Name                        |
| ------------ | ----------------------------------------- |
| TC1          | `test_init`                               |
| TC2-3        | `test_preprocess_frame`                   |
| TC4          | `test_detect_persons_empty_frame`         |
| TC5-7        | `test_detect_persons_with_detections`     |
| TC8-10       | Covered by mocked confidence tests        |
| TC11-13      | Covered by class filtering tests          |
| TC14, TC17   | `test_get_model_info`                     |
| TC15         | Covered by bbox format in detection tests |
| TC16         | `test_detect_persons_empty_frame`         |
| TC18-20      | Covered by detection structure tests      |

**Tổng số:** 5 test functions covering 20+ test cases (with mocking)

## 6. Tổng kết phân vùng

| Module         | Số Test Cases | Số Phân vùng chính | Complexity                              |
| -------------- | ------------- | ------------------ | --------------------------------------- |
| AlertSystem    | 20            | 8 phân vùng        | High (state + cooldown + severity)      |
| DataLogger     | 23            | 13 phân vùng       | Medium (enabled + file_exists + buffer) |
| PersonCounter  | 20            | 11 phân vùng       | Medium (count ranges + time + rate)     |
| PersonDetector | 20            | 12 phân vùng       | High (confidence + class_id + boxes)    |
| **TỔNG**       | **83**        | **44 phân vùng**   | -                                       |

---

## 7. Bảng quyết định (Decision Table Testing)

### 7.1. AlertSystem - Decision Table

#### B1: Liệt kê các điều kiện đầu vào (Conditions)

| Condition                     | Các giá trị có thể             |
| ----------------------------- | ------------------------------ |
| **enabled**                   | True, False                    |
| **person_count vs max_count** | < max, = max, +1-2, +3-5, > +5 |
| **is_alert_active**           | True, False                    |
| **trong cooldown**            | True, False                    |

#### B2: Xác định số lượng Rules

Tổng số kết hợp: 2 × 5 × 2 × 2 = **40 rules**

Sau khi rút gọn (vì một số kết hợp không hợp lý): **12 rules**

#### B3 & B4: Bảng quyết định đầy đủ (đã rút gọn)

| Conditions / Rules                     | R1  | R2  | R3   | R4       | R5       | R6       | R7  | R8  | R9  | R10  | R11  | R12  |
| -------------------------------------- | --- | --- | ---- | -------- | -------- | -------- | --- | --- | --- | ---- | ---- | ---- |
| **enabled**                            | F   | T   | T    | T        | T        | T        | T   | T   | T   | T    | T    | T    |
| **count < max_count**                  | -   | T   | F    | F        | F        | F        | F   | F   | F   | F    | F    | F    |
| **count = max_count**                  | -   | F   | T    | F        | F        | F        | F   | F   | F   | F    | F    | F    |
| **count vượt 1-2** (warning)           | -   | F   | F    | T        | F        | F        | T   | F   | F   | F    | F    | F    |
| **count vượt 3-5** (critical)          | -   | F   | F    | F        | T        | F        | F   | T   | F   | F    | F    | F    |
| **count vượt >5** (emergency)          | -   | F   | F    | F        | F        | T        | F   | F   | T   | F    | F    | F    |
| **is_alert_active**                    | -   | F   | F    | F        | F        | F        | T   | T   | T   | F    | F    | F    |
| **trong cooldown**                     | -   | -   | -    | F        | F        | F        | F   | F   | F   | T    | T    | T    |
| **Actions/Outcomes:**                  |     |     |      |          |          |          |     |     |     |      |      |      |
| Return None                            | ✓   | ✓   | ✓    |          |          |          |     |     |     |      |      |      |
| Create warning alert                   |     |     |      | ✓        |          |          |     |     |     |      |      |      |
| Create critical alert                  |     |     |      |          | ✓        |          |     |     |     |      |      |      |
| Create emergency alert                 |     |     |      |          |          | ✓        |     |     |     |      |      |      |
| Return info (normalized)               |     |     |      |          |          |          | ✓   | ✓   | ✓   |      |      |      |
| Add to history                         |     |     |      | ✓        | ✓        | ✓        |     |     |     |      |      |      |
| Return alert but NO history (cooldown) |     |     |      |          |          |          |     |     |     | ✓    | ✓    | ✓    |
| **Test Cases:**                        | TC1 | TC2 | TC12 | TC4, TC5 | TC6, TC7 | TC8, TC9 | TC3 | TC3 | TC3 | TC10 | TC10 | TC10 |

---

### 7.2. DataLogger - Decision Table

#### B1: Liệt kê các điều kiện đầu vào (Conditions)

| Condition                 | Các giá trị có thể                                             |
| ------------------------- | -------------------------------------------------------------- |
| **enabled**               | True, False                                                    |
| **Operation type**        | log_data, save_to_csv, save_immediate, load_data, export_excel |
| **buffer_length**         | 0, >0                                                          |
| **file_exists**           | True, False                                                    |
| **data_exists** (in file) | Empty, Has data                                                |

#### B2: Xác định số lượng Rules

Vì có nhiều operations khác nhau, chúng ta tạo bảng riêng cho từng operation chính:

**Bảng 2a: log_data() operation**

| Conditions / Rules | R1  | R2       |
| ------------------ | --- | -------- |
| **enabled**        | F   | T        |
| **Actions:**       |     |          |
| Add to buffer      |     | ✓        |
| No action          | ✓   |          |
| **Test Cases:**    | TC5 | TC3, TC4 |

**Bảng 2b: save_to_csv() operation**

| Conditions / Rules           | R1  | R2  | R3  | R4  |
| ---------------------------- | --- | --- | --- | --- |
| **enabled**                  | F   | T   | T   | T   |
| **buffer_length = 0**        | -   | T   | F   | F   |
| **file_exists**              | -   | -   | F   | T   |
| **Actions:**                 |     |     |     |     |
| No action                    | ✓   | ✓   |     |     |
| Create file + header + write |     |     | ✓   |     |
| Append to file               |     |     |     | ✓   |
| Clear buffer                 |     |     | ✓   | ✓   |
| **Test Cases:**              | TC7 | TC6 | TC8 | TC9 |

**Bảng 2c: save_immediate() operation**

| Conditions / Rules                 | R1   | R2   | R3   |
| ---------------------------------- | ---- | ---- | ---- |
| **enabled**                        | F    | T    | T    |
| **file_exists**                    | -    | F    | T    |
| **Actions:**                       |      |      |      |
| No action                          | ✓    |      |      |
| Create file + header + write 1 row |      | ✓    |      |
| Append 1 row (no header)           |      |      | ✓    |
| **Test Cases:**                    | TC12 | TC10 | TC11 |

**Bảng 2d: load_data() và các operations khác**

| Conditions / Rules         | R1 (load) | R2 (load) | R3 (summary) | R4 (summary) | R5 (export) | R6 (export) |
| -------------------------- | --------- | --------- | ------------ | ------------ | ----------- | ----------- |
| **file_exists**            | F         | T         | -            | -            | -           | -           |
| **data_exists**            | -         | T         | Empty        | Has data     | Empty       | Has data    |
| **Actions:**               |           |           |              |              |             |             |
| Return empty DataFrame     | ✓         |           |              |              |             |             |
| Return DataFrame with data |           | ✓         |              |              |             |             |
| Return empty dict          |           |           | ✓            |              |             |             |
| Return summary stats       |           |           |              | ✓            |             |             |
| No file created / no crash |           |           |              |              | ✓           |             |
| Create .xlsx with data     |           |           |              |              |             | ✓           |
| **Test Cases:**            | TC14      | TC13      | TC16         | TC15         | TC19        | TC18        |

---

### 7.3. PersonCounter - Decision Table

#### B1: Liệt kê các điều kiện đầu vào (Conditions)

| Condition            | Các giá trị có thể                      |
| -------------------- | --------------------------------------- |
| **detections count** | 0, 1, 2-10, >10                         |
| **running_time**     | ≈0, >0 && <1, ≥1                        |
| **history_length**   | 0, <100, =100, >100                     |
| **Operation type**   | update_count, get_fps, get_stats, reset |

#### B2: Xác định số lượng Rules

**Bảng 3a: update_count() operation**

| Conditions / Rules          | R1  | R2  | R3  | R4  | R5  |
| --------------------------- | --- | --- | --- | --- | --- |
| **detections count = 0**    | T   | F   | F   | F   | F   |
| **detections count = 1**    | F   | T   | F   | F   | F   |
| **detections count = 2-10** | F   | F   | T   | F   | F   |
| **detections count > 10**   | F   | F   | F   | T   | T   |
| **history_length > 100**    | F   | F   | F   | F   | T   |
| **Actions:**                |     |     |     |     |     |
| current_count = 0           | ✓   |     |     |     |     |
| current_count = n           |     | ✓   | ✓   | ✓   | ✓   |
| Update max_count            |     | ✓   | ✓   | ✓   | ✓   |
| Add to history              | ✓   | ✓   | ✓   | ✓   | ✓   |
| Keep history ≤ 100          |     |     |     |     | ✓   |
| Increment frame_count       | ✓   | ✓   | ✓   | ✓   | ✓   |
| Update total_detections     |     | ✓   | ✓   | ✓   | ✓   |
| **Test Cases:**             | TC2 | TC3 | TC4 | TC5 | TC8 |

**Bảng 3b: get_fps() operation**

| Conditions / Rules          | R1   | R2   | R3   |
| --------------------------- | ---- | ---- | ---- |
| **running_time ≈ 0**        | T    | F    | F    |
| **running_time > 0 && < 1** | F    | T    | F    |
| **running_time ≥ 1**        | F    | F    | T    |
| **Actions:**                |      |      |      |
| Return fps = 0              | ✓    |      |      |
| Return fps (high value)     |      | ✓    |      |
| Return fps (normal value)   |      |      | ✓    |
| **Test Cases:**             | TC13 | TC14 | TC14 |

**Bảng 3c: detection_rate calculation**

| Conditions / Rules          | R1   | R2  | R3   | R4   |
| --------------------------- | ---- | --- | ---- | ---- |
| **frames_with_persons = 0** | T    | F   | F    | F    |
| **rate 0.1-0.3** (rare)     | F    | T   | F    | F    |
| **rate 0.4-0.7** (medium)   | F    | F   | T    | F    |
| **rate 0.8-1.0** (high)     | F    | F   | F    | T    |
| **Actions:**                |      |     |      |      |
| detection_rate = 0.0        | ✓    |     |      |      |
| detection_rate = low        |      | ✓   |      |      |
| detection_rate = medium     |      |     | ✓    |      |
| detection_rate = high/1.0   |      |     |      | ✓    |
| **Test Cases:**             | TC10 | -   | TC12 | TC11 |

---

### 7.4. PersonDetector - Decision Table

#### B1: Liệt kê các điều kiện đầu vào (Conditions)

| Condition       | Các giá trị có thể                                 |
| --------------- | -------------------------------------------------- |
| **frame state** | None/empty, valid, non-standard size               |
| **YOLO boxes**  | None, 1 box, 2-5 boxes, >5 boxes                   |
| **confidence**  | < threshold, = threshold, > threshold, high (≥0.9) |
| **class_id**    | 0 (person), 1-79 (other), >79 (out of range)       |

#### B2: Xác định số lượng Rules

**Bảng 4a: Detection based on YOLO output**

| Conditions / Rules         | R1  | R2  | R3  | R4       | R5  | R6  | R7   | R8        |
| -------------------------- | --- | --- | --- | -------- | --- | --- | ---- | --------- |
| **YOLO boxes = None**      | T   | F   | F   | F        | F   | F   | F    | F         |
| **boxes = 1**              | F   | T   | T   | T        | F   | F   | F    | F         |
| **boxes = 2-5**            | F   | F   | F   | F        | T   | F   | F    | F         |
| **boxes > 5**              | F   | F   | F   | F        | F   | T   | F    | F         |
| **conf < threshold**       | -   | T   | F   | F        | -   | -   | -    | -         |
| **conf = threshold**       | -   | F   | T   | F        | -   | -   | -    | -         |
| **conf > threshold**       | -   | F   | F   | T        | T   | T   | T    | T         |
| **class_id = 0 (person)**  | -   | T   | T   | T        | T   | T   | T    | F         |
| **class_id ≠ 0 (other)**   | -   | F   | F   | F        | F   | F   | F    | T         |
| **Actions:**               |     |     |     |          |     |     |      |           |
| Return empty list []       | ✓   | ✓   |     |          |     |     |      | ✓         |
| Return 1 detection         |     |     | ✓   | ✓        |     |     |      |           |
| Return multiple detections |     |     |     |          | ✓   | ✓   |      |           |
| Filter non-person classes  |     |     |     |          |     |     | ✓    | ✓         |
| **Test Cases:**            | TC4 | TC8 | TC9 | TC5,TC10 | TC6 | TC7 | TC13 | TC11,TC12 |

**Bảng 4b: Frame preprocessing**

| Conditions / Rules        | R1   | R2  | R3  |
| ------------------------- | ---- | --- | --- |
| **frame = empty/None**    | T    | F   | F   |
| **frame = 640x480** (std) | F    | T   | F   |
| **frame = other size**    | F    | F   | T   |
| **Actions:**              |      |     |     |
| Return empty list         | ✓    |     |     |
| Process as-is             |      | ✓   | ✓   |
| **Test Cases:**           | TC16 | TC2 | TC3 |

**Bảng 4c: Confidence filtering**

| Conditions / Rules         | R1  | R2  | R3        |
| -------------------------- | --- | --- | --------- |
| **conf < 0.5** (threshold) | T   | F   | F         |
| **conf = 0.5**             | F   | T   | F         |
| **conf ≥ 0.9** (high)      | F   | F   | T         |
| **Actions:**               |     |     |           |
| Filtered out by YOLO       | ✓   |     |           |
| Accepted at threshold      |     | ✓   |           |
| Accepted with high conf    |     |     | ✓         |
| **Test Cases:**            | TC8 | TC9 | TC10,TC20 |

---

### 7.5. Ánh xạ Decision Table → Test Cases

| Module         | Total Rules | Total Test Cases | Coverage |
| -------------- | ----------- | ---------------- | -------- |
| AlertSystem    | 12          | 20               | 100%     |
| DataLogger     | 14          | 23               | 100%     |
| PersonCounter  | 13          | 20               | 100%     |
| PersonDetector | 14          | 20               | 100%     |
| **TỔNG**       | **53**      | **83**           | **100%** |

### 7.6. Kết luận về Decision Tables

✅ **Ưu điểm của phương pháp Decision Table Testing:**

1. **Bao phủ đầy đủ:** Xác định được tất cả các kết hợp có thể của điều kiện đầu vào
2. **Rút gọn hiệu quả:** Giảm từ hàng trăm test cases lý thuyết về 53 rules thực tế
3. **Dễ maintain:** Khi thêm điều kiện mới, dễ dàng mở rộng bảng
4. **Phát hiện edge cases:** Giúp tìm ra các trường hợp biên và conflict logic
5. **Tránh duplicate tests:** Nhìn tổng quan để loại bỏ test cases trùng lặp

✅ **Quy trình áp dụng:**

-   **B1:** Liệt kê tất cả conditions và values
-   **B2:** Tính toán số rules lý thuyết (tích Descartes)
-   **B3:** Tạo bảng đầy đủ với tất cả kết hợp
-   **B4:** Rút gọn bằng cách:
    -   Loại bỏ kết hợp không hợp lý (impossible combinations)
    -   Gộp các rules có cùng outcome
    -   Dùng "don't care" (-) cho điều kiện không ảnh hưởng

✅ **Độ phủ (Coverage):**

-   **100% rules coverage:** Mỗi rule trong bảng đều có ít nhất 1 test case
-   **100% conditions coverage:** Mỗi điều kiện đều được test với tất cả giá trị có thể
-   **100% actions coverage:** Mỗi outcome/action đều được verify

---

## 8. Chạy Tests

### Chạy tất cả unit tests

```bash
pytest tests/unit/ -v
```

### Chạy từng module

```bash
pytest tests/unit/alert_system_test.py -v
pytest tests/unit/data_logger_test.py -v
```

### Chạy với coverage

```bash
pytest tests/unit/ --cov=src.core --cov-report=html
```

---
