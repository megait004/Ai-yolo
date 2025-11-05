# Hướng dẫn Train Model YOLOv8 - Phát hiện Người

## 1. Chuẩn bị Dataset (Roboflow)

1. Vào [Roboflow Universe](https://universe.roboflow.com/)
2. Chọn Project Type: Object Detection, Class: person
3. Upload ảnh → Annotate (vẽ bbox) → Chia train/val (80/20)
4. Generate → Export format "YOLOv8 (Ultralytics)" → Download

## 2. Giải nén Dataset

Giải nén vào: `datasets/person/`

Cấu trúc:

```
datasets/person/
├── images/train/
├── images/val/
├── labels/train/
├── labels/val/
└── data.yaml
```

Kiểm tra `data.yaml`:

```yaml
path: datasets/person
train: images/train
val: images/val
nc: 1
names: [person]
```

## 3. Train

```cmd
cd C:\Users\GiapHue04\Desktop\yolo\Ai-yolo
```

### Lệnh train cơ bản

```cmd
yolo task=detect mode=train model=models/pretrained/yolov8n.pt data=datasets/person/data.yaml project=models/trained name=giapzech epochs=50 imgsz=640 batch=16 workers=0
```

### Máy yếu

```cmd
yolo task=detect mode=train model=models/pretrained/yolov8n.pt data=datasets/person/data.yaml project=models/trained name=giapzech epochs=50 imgsz=512 batch=8 workers=0 device=cpu
```

Kết quả: `models/trained/giapzech/weights/best.pt`

## 4. Test

### Val

```cmd
yolo task=detect mode=val model=models/trained/giapzech/weights/best.pt data=datasets/person/data.yaml
```

### Predict

```cmd
yolo task=detect mode=predict model=models/trained/giapzech/weights/best.pt source="path\to\image_or_video"
```

### Webcam

```cmd
yolo task=detect mode=predict model=models/trained/giapzech/weights/best.pt source=0
```

## 5. Dùng trong App

Sửa `config/settings.py`:

```python
YOLO_MODEL = "models/trained/giapzech/weights/best.pt"
```
