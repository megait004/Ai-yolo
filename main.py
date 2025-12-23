"""
Script để chạy ứng dụng GUI
"""

import os
import sys

# CRITICAL FIX: Set this BEFORE any imports
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:128'

# Thêm thư mục gốc vào path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ui import PersonDetectionGUI
from PyQt6.QtWidgets import QApplication


def main():
    """Chạy ứng dụng GUI"""
    app = QApplication(sys.argv)

    # Thiết lập style
    app.setStyle('Fusion')

    window = PersonDetectionGUI()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
