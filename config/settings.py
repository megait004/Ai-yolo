"""
Application settings and configuration
"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
SRC_ROOT = PROJECT_ROOT / "src"
DATA_ROOT = PROJECT_ROOT / "data"
MODELS_ROOT = PROJECT_ROOT / "models"
OUTPUT_ROOT = PROJECT_ROOT / "output"
LOGS_ROOT = PROJECT_ROOT / "logs"

# YOLO Configuration
YOLO_MODEL = "C:/Users/GiapHue04/Desktop/yolo/Ai-yolo/models/trained/giapzech3/weights/best.pt"  # Options: yolov8n.pt, yolov8s.pt, yolov8m.pt, yolov8l.pt, yolov8x.pt
CONFIDENCE_THRESHOLD = 0.5  # Tăng nhẹ từ 0.5 -> 0.55 để giảm False Positive
IOU_THRESHOLD = 0.35
PERSON_CLASS_ID = 0  # Class ID for "person" in COCO dataset

# Detection Filter (để debug khi cần)
MIN_DETECTION_AREA = 800  # Diện tích tối thiểu (pixels²) - có thể dùng sau
MIN_DETECTION_WIDTH = 25  # Chiều rộng tối thiểu
MIN_DETECTION_HEIGHT = 50  # Chiều cao tối thiểu

# Video/Camera Configuration
DEFAULT_CAMERA_INDEX = 0
VIDEO_WIDTH = 640
VIDEO_HEIGHT = 480
FPS = 30

# Display Configuration
BOUNDING_BOX_COLOR = (0, 255, 0)  # Green
TEXT_COLOR = (255, 255, 255)      # White
FONT_SCALE = 0.7
FONT_THICKNESS = 2

# Alert System Configuration
MAX_PERSON_COUNT = 10
ALERT_ENABLED = True
ALERT_COOLDOWN = 5  # seconds

# Data Logging Configuration
SAVE_TO_CSV = True
CSV_FILENAME = "person_count_data.csv"
SAVE_INTERVAL = 1  # seconds
DATA_DIR = DATA_ROOT / "processed"

# Output Configuration
OUTPUT_IMAGES_DIR = OUTPUT_ROOT / "images"
OUTPUT_VIDEOS_DIR = OUTPUT_ROOT / "videos"
OUTPUT_REPORTS_DIR = OUTPUT_ROOT / "reports"

# Model Configuration
MODEL_PRETRAINED_DIR = MODELS_ROOT / "pretrained"
MODEL_TRAINED_DIR = MODELS_ROOT / "trained"

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = LOGS_ROOT / "app.log"

# UI Configuration (for future UI development)
UI_THEME = "dark"
UI_WINDOW_SIZE = (1200, 800)
UI_REFRESH_RATE = 30  # FPS

# Testing Configuration
TEST_DATA_DIR = DATA_ROOT / "raw" / "test"
TEST_OUTPUT_DIR = OUTPUT_ROOT / "test_results"

# Performance Configuration
MAX_FPS = 60
ENABLE_GPU = True
BATCH_SIZE = 1

# Security Configuration
ALLOWED_VIDEO_FORMATS = ['.mp4', '.avi', '.mov', '.mkv', '.wmv']
ALLOWED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']

# API Configuration (for future API development)
API_HOST = "localhost"
API_PORT = 8000
API_DEBUG = False

# Database Configuration (for future database integration)
DATABASE_URL = "sqlite:///data/person_detection.db"

# Environment Configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Create directories if they don't exist
for directory in [
    DATA_ROOT, MODELS_ROOT, OUTPUT_ROOT, LOGS_ROOT,
    DATA_DIR, OUTPUT_IMAGES_DIR, OUTPUT_VIDEOS_DIR, OUTPUT_REPORTS_DIR,
    MODEL_PRETRAINED_DIR, MODEL_TRAINED_DIR, TEST_DATA_DIR, TEST_OUTPUT_DIR
]:
    directory.mkdir(parents=True, exist_ok=True)
