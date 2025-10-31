"""
Module phát hiện người sử dụng YOLOv8
"""

import os

# CRITICAL: Must be first, before any torch/ultralytics imports
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from config.settings import (
    CONFIDENCE_THRESHOLD,
    IOU_THRESHOLD,
    PERSON_CLASS_ID,
    VIDEO_HEIGHT,
    VIDEO_WIDTH,
    YOLO_MODEL,
)

# Lazy import - chỉ import khi cần
_YOLO = None


def _get_yolo():
    """Lazy load YOLO model"""
    global _YOLO
    if _YOLO is None:
        # Kiểm tra CUDA trước khi load model
        try:
            import torch

            if not torch.cuda.is_available():
                # Force CPU mode nếu không có CUDA
                os.environ["CUDA_VISIBLE_DEVICES"] = ""
        except Exception:
            # Nếu có lỗi gì, force CPU để an toàn
            os.environ["CUDA_VISIBLE_DEVICES"] = ""

        from ultralytics import YOLO

        _YOLO = YOLO(YOLO_MODEL)  # pyright: ignore[reportConstantRedefinition]
    return _YOLO


class PersonDetector:
    """
    Lớp phát hiện người sử dụng mô hình YOLOv8
    """

    def __init__(self, model_path=YOLO_MODEL):
        """
        Khởi tạo detector

        Args:
            model_path (str): Đường dẫn đến file mô hình YOLOv8
        """
        # Không load model ngay, sẽ load khi cần
        self.model_path = model_path
        self.model = None
        self.confidence_threshold = CONFIDENCE_THRESHOLD
        self.iou_threshold = IOU_THRESHOLD
        self.person_class_id = PERSON_CLASS_ID

    def _ensure_model_loaded(self):
        """Đảm bảo model đã được load"""
        if self.model is None:
            self.model = _get_yolo()

    def detect_persons(self, frame):
        """
        Phát hiện người trong khung hình

        Args:
            frame (numpy.ndarray): Khung hình đầu vào

        Returns:
            list: Danh sách các bounding box của người được phát hiện
        """
        try:
            # Load model lần đầu (lazy loading)
            self._ensure_model_loaded()

            # Kiểm tra GPU có sẵn - AN TOÀN với fallback
            use_gpu = False
            device = "cpu"

            try:
                import torch

                # Kiểm tra CUDA có thực sự hoạt động không
                if torch.cuda.is_available():
                    try:
                        # Test CUDA bằng cách tạo tensor nhỏ
                        _ = torch.cuda.FloatTensor(
                            1
                        )  # pyright: ignore[reportAttributeAccessIssue]
                        use_gpu = True
                        device = "0"
                    except Exception as cuda_err:
                        print(f"⚠️ CUDA có nhưng không hoạt động: {cuda_err}")
                        print("   → Chuyển sang CPU mode")
            except Exception as torch_err:
                print(f"⚠️ Lỗi khi import torch hoặc kiểm tra CUDA: {torch_err}")
                print("   → Sử dụng CPU mode")

            # Log device info (chỉ log lần đầu)
            if not hasattr(self, "_device_logged"):
                if use_gpu:
                    try:
                        print(
                            f"🚀 Using GPU: {torch.cuda.get_device_name(0)}"
                        )  # pyright: ignore[reportPossiblyUnboundVariable]
                        cuda_version = getattr(
                            torch.version, "cuda", "N/A"
                        )  # pyright: ignore[reportAttributeAccessIssue, reportPossiblyUnboundVariable]
                        print(f"   CUDA Version: {cuda_version}")
                    except:
                        print("🚀 Using GPU")
                else:
                    print("💻 Using CPU (no GPU or CUDA unavailable)")
                self._device_logged = (
                    True  # pyright: ignore[reportUninitializedInstanceVariable]
                )

            # Chạy inference với tối ưu cho speed
            inference_kwargs = {
                "conf": self.confidence_threshold,
                "iou": self.iou_threshold,
                "verbose": False,
                "device": device,
                "imgsz": 640,  # Kích thước inference cố định để tăng tốc
            }

            # Chỉ dùng FP16 trên GPU
            if use_gpu:
                inference_kwargs["half"] = True

            # Model is guaranteed to be loaded by _ensure_model_loaded()
            results = self.model(  # pyright: ignore[reportOptionalCall]
                frame, **inference_kwargs  # pyright: ignore[reportArgumentType]
            )

            # Lọc kết quả chỉ lấy class "person"
            person_detections = []

            for result in results:
                if result.boxes is not None:
                    boxes = result.boxes.xyxy.cpu().numpy()  # Bounding boxes
                    confidences = result.boxes.conf.cpu().numpy()  # Confidence scores
                    class_ids = result.boxes.cls.cpu().numpy()  # Class IDs

                    # Lọc chỉ lấy detections của class "person"
                    for i, class_id in enumerate(class_ids):
                        if int(class_id) == self.person_class_id:
                            x1, y1, x2, y2 = boxes[i]
                            confidence = confidences[i]

                            person_detections.append(
                                {
                                    "bbox": [int(x1), int(y1), int(x2), int(y2)],
                                    "confidence": float(confidence),
                                    "class_id": int(class_id),
                                }
                            )

            return person_detections

        except Exception as e:
            print(f"Lỗi trong quá trình phát hiện: {e}")
            return []

    def preprocess_frame(self, frame):
        """
        Tiền xử lý khung hình trước khi đưa vào mô hình

        Args:
            frame (numpy.ndarray): Khung hình gốc

        Returns:
            numpy.ndarray: Khung hình đã được tiền xử lý
        """
        # Không cần resize vì đã set ở camera level
        return frame

    def get_model_info(self):
        """
        Lấy thông tin về mô hình đang sử dụng

        Returns:
            dict: Thông tin mô hình
        """
        return {
            "model_name": YOLO_MODEL,
            "confidence_threshold": self.confidence_threshold,
            "iou_threshold": self.iou_threshold,
            "input_size": f"{VIDEO_WIDTH}x{VIDEO_HEIGHT}",
        }
