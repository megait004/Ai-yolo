"""
Helper functions for the application
"""

import os
import time
from datetime import datetime
from typing import Optional, Tuple, Union

import cv2
import numpy as np


def validate_video_source(source: Union[str, int]) -> bool:
    """
    Validate if video source is accessible

    Args:
        source: Video source (camera index or file path)

    Returns:
        bool: True if source is valid, False otherwise
    """
    try:
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            return False

        # Try to read a frame
        ret, _ = cap.read()
        cap.release()
        return ret
    except Exception:
        return False


def format_timestamp(timestamp: Optional[float] = None) -> str:
    """
    Format timestamp to readable string

    Args:
        timestamp: Unix timestamp (default: current time)

    Returns:
        str: Formatted timestamp
    """
    if timestamp is None:
        timestamp = time.time()

    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def calculate_fps(start_time: float, frame_count: int) -> float:
    """
    Calculate FPS based on start time and frame count

    Args:
        start_time: Start time in seconds
        frame_count: Number of frames processed

    Returns:
        float: FPS value
    """
    elapsed_time = time.time() - start_time
    if elapsed_time > 0:
        return frame_count / elapsed_time
    return 0.0


def resize_frame(
    frame, target_size: Tuple[int, int]
) -> "np.ndarray":  # pyright: ignore[reportMissingTypeArgument]
    """
    Resize frame to target size

    Args:
        frame: Input frame
        target_size: Target size (width, height)

    Returns:
        np.ndarray: Resized frame
    """
    return cv2.resize(frame, target_size)


def create_directory(path: str) -> bool:
    """
    Create directory if it doesn't exist

    Args:
        path: Directory path

    Returns:
        bool: True if created or exists, False otherwise
    """
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception:
        return False


def get_file_size_mb(file_path: str) -> float:
    """
    Get file size in MB

    Args:
        file_path: Path to file

    Returns:
        float: File size in MB
    """
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except Exception:
        return 0.0


def is_valid_image_file(file_path: str) -> bool:
    """
    Check if file is a valid image

    Args:
        file_path: Path to file

    Returns:
        bool: True if valid image, False otherwise
    """
    valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"}
    _, ext = os.path.splitext(file_path.lower())
    return ext in valid_extensions


def is_valid_video_file(file_path: str) -> bool:
    """
    Check if file is a valid video

    Args:
        file_path: Path to file

    Returns:
        bool: True if valid video, False otherwise
    """
    valid_extensions = {".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".webm"}
    _, ext = os.path.splitext(file_path.lower())
    return ext in valid_extensions
