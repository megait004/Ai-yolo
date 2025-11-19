"""
Pytest configuration và fixtures cho System Tests
"""

import pytest
import sys
from pathlib import Path
import numpy as np
import cv2

# Thêm thư mục gốc vào Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


# ============================================================================
# SHARED FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def project_paths():
    """Các đường dẫn quan trọng trong project"""
    root = Path(__file__).parent.parent.parent
    return {
        "root": root,
        "data": root / "datasets",
        "output": root / "output",
        "models": root / "models",
        "tests": root / "tests",
        "system_tests": root / "tests" / "system"
    }


@pytest.fixture(scope="function")
def temp_output_dir(tmp_path):
    """Thư mục output tạm cho mỗi test"""
    output_dir = tmp_path / "output"
    output_dir.mkdir(exist_ok=True)
    return output_dir


@pytest.fixture
def sample_frame_640x480():
    """Frame mẫu 640x480"""
    return np.zeros((480, 640, 3), dtype=np.uint8)


@pytest.fixture
def sample_frame_1280x720():
    """Frame mẫu 1280x720 HD"""
    return np.zeros((720, 1280, 3), dtype=np.uint8)


@pytest.fixture
def sample_frame_320x240():
    """Frame mẫu 320x240 low resolution"""
    return np.zeros((240, 320, 3), dtype=np.uint8)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_test_video(output_path, num_frames=30, fps=25, width=640, height=480):
    """
    Tạo video test đơn giản

    Args:
        output_path: Đường dẫn lưu video
        num_frames: Số frames
        fps: Frames per second
        width, height: Kích thước video
    """
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

    for i in range(num_frames):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        # Vẽ số frame lên góc
        cv2.putText(frame, f"Frame {i}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        out.write(frame)

    out.release()
    return output_path


@pytest.fixture
def video_creator(tmp_path):
    """Factory fixture để tạo video test"""
    def _create(num_frames=30, fps=25, width=640, height=480, name="test_video.mp4"):
        output_path = tmp_path / name
        return create_test_video(output_path, num_frames, fps, width, height)
    return _create


# ============================================================================
# MARKERS
# ============================================================================

def pytest_configure(config):
    """Đăng ký custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )
