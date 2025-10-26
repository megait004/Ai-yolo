"""
Formatting functions
"""

import json
from datetime import datetime
from typing import Any, Dict, List


def format_detection_summary(detections: List[Dict[str, Any]]) -> str:
    """
    Format detection summary for display

    Args:
        detections: List of detections

    Returns:
        str: Formatted summary string
    """
    if not detections:
        return "No detections"

    count = len(detections)
    avg_confidence = sum(d["confidence"] for d in detections) / count

    return f"Detected {count} person(s) (avg confidence: {avg_confidence:.2f})"


def format_stats_summary(stats: Dict[str, Any]) -> str:
    """
    Format statistics summary

    Args:
        stats: Statistics dictionary

    Returns:
        str: Formatted summary string
    """
    return (
        f"Current: {stats.get('current_count', 0)} | "
        f"Max: {stats.get('max_count', 0)} | "
        f"FPS: {stats.get('fps', 0):.1f} | "
        f"Time: {stats.get('running_time', 0):.1f}s"
    )


def format_alert_message(alert: Dict[str, Any]) -> str:
    """
    Format alert message

    Args:
        alert: Alert dictionary

    Returns:
        str: Formatted alert message
    """
    alert_type = alert.get("type", "info")
    message = alert.get("message", "Unknown alert")
    timestamp = alert.get("datetime", datetime.now().strftime("%H:%M:%S"))

    return f"[{timestamp}] {alert_type.upper()}: {message}"


def format_json_output(data: Dict[str, Any], indent: int = 2) -> str:
    """
    Format data as JSON string

    Args:
        data: Data to format
        indent: JSON indentation

    Returns:
        str: Formatted JSON string
    """
    return json.dumps(data, indent=indent, default=str)


def format_csv_row(data: Dict[str, Any], headers: List[str]) -> str:
    """
    Format data as CSV row

    Args:
        data: Data dictionary
        headers: CSV headers

    Returns:
        str: CSV row string
    """
    values = []
    for header in headers:
        value = data.get(header, "")
        # Escape commas and quotes
        if isinstance(value, str) and ("," in value or '"' in value):
            escaped_value = value.replace('"', '""')
            value = f'"{escaped_value}"'
        values.append(str(value))

    return ",".join(values)


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format

    Args:
        size_bytes: Size in bytes

    Returns:
        str: Formatted size string
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes/1024:.1f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes/(1024**2):.1f} MB"
    else:
        return f"{size_bytes/(1024**3):.1f} GB"


def format_duration(seconds: float) -> str:
    """
    Format duration in human readable format

    Args:
        seconds: Duration in seconds

    Returns:
        str: Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.1f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours}h {minutes}m {secs:.1f}s"


def format_percentage(value: float, total: float) -> str:
    """
    Format percentage

    Args:
        value: Current value
        total: Total value

    Returns:
        str: Formatted percentage string
    """
    if total == 0:
        return "0.0%"

    percentage = (value / total) * 100
    return f"{percentage:.1f}%"


def format_model_info(model_info: Dict[str, Any]) -> str:
    """
    Format model information

    Args:
        model_info: Model information dictionary

    Returns:
        str: Formatted model info string
    """
    lines = ["Model Information:"]
    for key, value in model_info.items():
        lines.append(f"  {key}: {value}")

    return "\n".join(lines)
