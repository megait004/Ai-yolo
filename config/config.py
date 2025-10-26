"""
File cấu hình cho hệ thống nhận dạng và đếm người
"""

# Cấu hình YOLOv8
YOLO_MODEL = "yolov8n.pt"  # Có thể thay đổi: yolov8s.pt, yolov8m.pt, yolov8l.pt, yolov8x.pt
CONFIDENCE_THRESHOLD = 0.5  # Ngưỡng tin cậy cho phát hiện
IOU_THRESHOLD = 0.45        # Ngưỡng IoU cho NMS

# Cấu hình video/camera
DEFAULT_CAMERA_INDEX = 0    # Index của webcam (thường là 0)
VIDEO_WIDTH = 640          # Chiều rộng video
VIDEO_HEIGHT = 480         # Chiều cao video
FPS = 30                   # Frames per second

# Cấu hình hiển thị
BOUNDING_BOX_COLOR = (0, 255, 0)  # Màu xanh lá cho bounding box
TEXT_COLOR = (255, 255, 255)      # Màu trắng cho text
FONT_SCALE = 0.7                  # Kích thước font
FONT_THICKNESS = 2                # Độ dày font

# Cấu hình cảnh báo
MAX_PERSON_COUNT = 10      # Số lượng người tối đa cho phép
ALERT_ENABLED = True       # Bật/tắt hệ thống cảnh báo

# Cấu hình lưu dữ liệu
SAVE_TO_CSV = True         # Bật/tắt lưu dữ liệu vào CSV
CSV_FILENAME = "person_count_data.csv"  # Tên file CSV
SAVE_INTERVAL = 1          # Lưu dữ liệu mỗi N giây

# Cấu hình class ID cho YOLO
PERSON_CLASS_ID = 0        # Class ID của "person" trong COCO dataset
