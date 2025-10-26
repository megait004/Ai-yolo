"""
Validation functions
"""

import re
from typing import Any, Dict, List


def validate_email(email: str) -> bool:
    """
    Validate email format

    Args:
        email: Email address

    Returns:
        bool: True if valid, False otherwise
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """
    Validate phone number format

    Args:
        phone: Phone number

    Returns:
        bool: True if valid, False otherwise
    """
    # Remove all non-digit characters
    digits = re.sub(r"\D", "", phone)
    # Check if it's a valid length (7-15 digits)
    return 7 <= len(digits) <= 15


def validate_config(config: Dict[str, Any]) -> List[str]:
    """
    Validate configuration dictionary

    Args:
        config: Configuration dictionary

    Returns:
        List[str]: List of validation errors (empty if valid)
    """
    errors = []

    # Required fields
    required_fields = ["YOLO_MODEL", "CONFIDENCE_THRESHOLD", "MAX_PERSON_COUNT"]
    for field in required_fields:
        if field not in config:
            errors.append(f"Missing required field: {field}")

    # Validate confidence threshold
    if "CONFIDENCE_THRESHOLD" in config:
        conf = config["CONFIDENCE_THRESHOLD"]
        if not isinstance(conf, (int, float)) or not 0 <= conf <= 1:
            errors.append("CONFIDENCE_THRESHOLD must be between 0 and 1")

    # Validate max person count
    if "MAX_PERSON_COUNT" in config:
        max_count = config["MAX_PERSON_COUNT"]
        if not isinstance(max_count, int) or max_count < 0:
            errors.append("MAX_PERSON_COUNT must be a non-negative integer")

    return errors


def validate_detection_result(detection: Dict[str, Any]) -> bool:
    """
    Validate detection result format

    Args:
        detection: Detection result dictionary

    Returns:
        bool: True if valid, False otherwise
    """
    required_fields = ["bbox", "confidence", "class_id"]

    for field in required_fields:
        if field not in detection:
            return False

    # Validate bbox format
    bbox = detection["bbox"]
    if not isinstance(bbox, list) or len(bbox) != 4:
        return False

    # Validate confidence
    confidence = detection["confidence"]
    if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
        return False

    # Validate class_id
    class_id = detection["class_id"]
    if not isinstance(class_id, int) or class_id < 0:
        return False

    return True


def validate_stats(stats: Dict[str, Any]) -> bool:
    """
    Validate statistics dictionary

    Args:
        stats: Statistics dictionary

    Returns:
        bool: True if valid, False otherwise
    """
    required_fields = [
        "current_count",
        "max_count",
        "total_frames",
        "fps",
        "running_time",
    ]

    for field in required_fields:
        if field not in stats:
            return False

        value = stats[field]
        if not isinstance(value, (int, float)) or value < 0:
            return False

    return True


def validate_file_path(file_path: str, must_exist: bool = False) -> bool:
    """
    Validate file path

    Args:
        file_path: File path to validate
        must_exist: Whether file must exist

    Returns:
        bool: True if valid, False otherwise
    """
    if not isinstance(file_path, str) or not file_path.strip():
        return False

    if must_exist:
        import os

        return os.path.exists(file_path)

    return True
