# Person Detection and Counting System

[![CI/CD Pipeline](https://github.com/yourusername/person-detection-yolo/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/yourusername/person-detection-yolo/actions)
[![codecov](https://codecov.io/gh/yourusername/person-detection-yolo/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/person-detection-yolo)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Hệ thống nhận dạng và đếm người theo thời gian thực sử dụng YOLOv8, được thiết kế với kiến trúc modular và hỗ trợ đầy đủ cho phát triển UI, testing và CI/CD.

## 🚀 Tính năng chính

-   **Nhận dạng người**: Sử dụng YOLOv8 để phát hiện người trong video/camera
-   **Đếm thời gian thực**: Đếm và hiển thị số lượng người theo thời gian thực
-   **Giao diện người dùng (GUI)**: Giao diện trực quan, dễ sử dụng với PyQt6
-   **Hiển thị trực quan**: Vẽ bounding box, nhãn và thông tin chi tiết
-   **Lưu trữ dữ liệu**: Tự động lưu thống kê vào CSV và có thể xuất Excel
-   **Hệ thống cảnh báo**: Cảnh báo khi số người vượt ngưỡng cho phép
-   **Kiến trúc modular**: Dễ dàng mở rộng và bảo trì
-   **Hỗ trợ testing**: Unit tests, integration tests, và E2E tests
-   **CI/CD ready**: Pipeline tự động cho testing, building và deployment

## 📁 Cấu trúc dự án

```
person-detection-yolo/
├── src/                          # Source code chính
│   ├── core/                     # Core modules
│   │   ├── person_detector.py    # YOLOv8 person detection
│   │   ├── person_counter.py     # Person counting logic
│   │   ├── visualizer.py         # Visualization components
│   │   ├── data_logger.py        # Data logging utilities
│   │   └── alert_system.py       # Alert system
│   ├── ui/                       # UI components (future)
│   ├── utils/                    # Utility functions
│   │   ├── helpers.py            # Helper functions
│   │   ├── validators.py         # Validation functions
│   │   └── formatters.py         # Formatting functions
│   └── main.py                   # Main application
├── tests/                        # Test suite
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── e2e/                      # End-to-end tests
├── config/                       # Configuration files
│   └── settings.py               # Application settings
├── scripts/                      # Utility scripts
│   ├── setup.py                  # Setup script
│   ├── demo.py                   # Demo script
│   └── fix_installation.py       # Installation fix script
├── docs/                         # Documentation
│   ├── README.md                 # Main documentation
│   ├── USAGE_GUIDE.md            # Usage guide
│   └── TROUBLESHOOTING.md        # Troubleshooting guide
├── data/                         # Data storage
│   ├── raw/                      # Raw data
│   └── processed/                # Processed data
├── models/                       # Model storage
│   ├── pretrained/               # Pretrained models
│   └── trained/                  # Custom trained models
├── output/                       # Output files
│   ├── images/                   # Output images
│   ├── videos/                   # Output videos
│   └── reports/                  # Analysis reports
├── logs/                         # Log files
├── .github/                      # GitHub workflows
│   └── workflows/                # CI/CD pipelines
├── requirements.txt              # Production dependencies
├── requirements-dev.txt          # Development dependencies
├── pyproject.toml               # Project configuration
└── README.md                    # This file
```

## 📚 Tài Liệu

Tất cả tài liệu chi tiết được tổ chức trong thư mục `docs/`:

-   **[📋 INSTALLATION.md](docs/INSTALLATION.md)** - Hướng dẫn cài đặt chi tiết
-   **[🏃 USAGE.md](docs/USAGE.md)** - Hướng dẫn sử dụng
-   **[🎨 GUI_GUIDE.md](docs/GUI_GUIDE.md)** - Hướng dẫn giao diện GUI
-   **[⚙️ FEATURES.md](docs/FEATURES.md)** - Tính năng hệ thống

## 🛠️ Cài Đặt Nhanh

### Yêu cầu hệ thống

-   Python 3.8+
-   OpenCV
-   CUDA (khuyến nghị cho GPU)

### Cài đặt cơ bản

```bash
# Clone repository
git clone https://github.com/yourusername/person-detection-yolo.git
cd person-detection-yolo

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy GUI
python scripts/run_gui.py
```

**Chi tiết:** Xem [docs/INSTALLATION.md](docs/INSTALLATION.md)

### Cài đặt cho development

```bash
# Cài đặt development dependencies
pip install -r requirements-dev.txt

# Cài đặt pre-commit hooks
pre-commit install

# Chạy tests
pytest
```

## 🚀 Sử dụng

### Chạy với Giao Diện GUI (Khuyến nghị)

```bash
python scripts/run_gui.py
```

Xem hướng dẫn chi tiết tại [GUI Guide](docs/GUI_GUIDE.md)

### Chạy với Command Line

**Chạy với webcam:**

```bash
python src/main.py
```

**Chạy với file video:**

```bash
python src/main.py --source path/to/video.mp4
```

**Chạy demo tương tác:**

```bash
python scripts/demo.py
```

**Các phím điều khiển:**

-   **q**: Thoát ứng dụng
-   **r**: Reset thống kê
-   **s**: Lưu dữ liệu ngay lập tức
-   **h**: Hiển thị trợ giúp
-   **a**: Bật/tắt hệ thống cảnh báo
-   **d**: Bật/tắt lưu dữ liệu

## 🧪 Testing

### Chạy tất cả tests

```bash
pytest
```

### Chạy unit tests

```bash
pytest tests/unit/
```

### Chạy integration tests

```bash
pytest tests/integration/
```

### Chạy với coverage

```bash
pytest --cov=src --cov-report=html
```

## 🔧 Development

### Code formatting

```bash
# Format code với black
black src tests

# Sort imports với isort
isort src tests

# Lint với flake8
flake8 src tests
```

### Type checking

```bash
mypy src
```

### Pre-commit hooks

```bash
pre-commit run --all-files
```

## 📊 CI/CD Pipeline

Dự án sử dụng GitHub Actions với pipeline bao gồm:

1. **Testing**: Unit tests, integration tests
2. **Code Quality**: Linting, formatting, type checking
3. **Security**: Security scanning với bandit và safety
4. **Building**: Package building và validation
5. **Deployment**: Tự động deploy khi merge vào main

## 🎯 Roadmap

### Phase 1: Core System ✅

-   [x] YOLOv8 person detection
-   [x] Real-time counting
-   [x] Data logging
-   [x] Alert system
-   [x] Modular architecture

### Phase 2: UI Development ✅

-   [x] Desktop GUI với PyQt6
-   [ ] Streamlit web interface
-   [ ] Gradio demo interface
-   [ ] Mobile-responsive design

### Phase 3: Advanced Features 📋

-   [ ] Multi-camera support
-   [ ] Person tracking
-   [ ] Heatmap generation
-   [ ] API endpoints
-   [ ] Database integration

### Phase 4: Production Ready 🎯

-   [ ] Docker containerization
-   [ ] Kubernetes deployment
-   [ ] Monitoring và logging
-   [ ] Performance optimization
-   [ ] Documentation website

## 🤝 Contributing

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Tạo Pull Request

## 📝 License

Dự án được phân phối dưới MIT License. Xem file `LICENSE` để biết thêm chi tiết.

## 📞 Liên hệ

-   **Author**: Your Name
-   **Email**: <your.email@example.com>
-   **GitHub**: [@yourusername](https://github.com/yourusername)

## 🙏 Acknowledgments

-   [Ultralytics](https://github.com/ultralytics/ultralytics) cho YOLOv8
-   [OpenCV](https://opencv.org/) cho computer vision
-   [PyTorch](https://pytorch.org/) cho deep learning framework

---

⭐ Nếu dự án hữu ích, hãy cho một star!
