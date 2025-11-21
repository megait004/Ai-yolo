"""
Script vẽ sơ đồ thuật toán cho các module trong hệ thống
Sử dụng graphviz để tạo flowchart chuyên nghiệp
"""

from graphviz import Digraph
import os

# Tạo thư mục output nếu chưa có
output_dir = "flowcharts"
os.makedirs(output_dir, exist_ok=True)


def create_person_detector_flowchart():
    """Tạo sơ đồ thuật toán cho PersonDetector"""
    dot = Digraph(comment='PersonDetector Algorithm', format='png')
    dot.attr(rankdir='TB', dpi='300')
    dot.attr('node', shape='box', style='rounded,filled', fillcolor='lightblue',
             fontname='Arial', fontsize='14', width='2.5', height='0.8')

    # Bắt đầu
    dot.node('start', 'Bắt đầu', shape='oval', fillcolor='lightgreen')

    # Khởi tạo
    dot.node('init', 'Khởi tạo PersonDetector\n- model_path\n- confidence_threshold\n- iou_threshold\n- model = None',
             shape='box', fillcolor='lightyellow')

    # Nhận frame
    dot.node('input', 'Nhận frame đầu vào', shape='parallelogram', fillcolor='lightcyan')

    # Kiểm tra model
    dot.node('check_model', 'Model đã load?', shape='diamond', fillcolor='lightpink')

    # Load model
    dot.node('load_model', '_get_yolo()\n- Import torch\n- Kiểm tra CUDA',
             shape='box', fillcolor='lightyellow')

    # Kiểm tra CUDA
    dot.node('check_cuda', 'CUDA available?', shape='diamond', fillcolor='lightpink')

    # Test tensor
    dot.node('test_tensor', 'Test tạo tensor\ntrên CUDA', shape='box', fillcolor='lightyellow')

    # Kiểm tra test
    dot.node('test_ok', 'Test thành công?', shape='diamond', fillcolor='lightpink')

    # Set GPU
    dot.node('set_gpu', 'use_gpu = True\ndevice = "0"', shape='box', fillcolor='lightgreen')

    # Set CPU
    dot.node('set_cpu', 'use_gpu = False\ndevice = "cpu"', shape='box', fillcolor='orange')

    # Cấu hình inference
    dot.node('config', 'Cấu hình inference_kwargs\n- conf, iou, device\n- imgsz=640, verbose=False',
             shape='box', fillcolor='lightyellow')

    # Kiểm tra GPU cho half precision
    dot.node('check_gpu', 'use_gpu = True?', shape='diamond', fillcolor='lightpink')

    # Set half precision
    dot.node('set_half', 'kwargs["half"] = True\n(FP16 precision)',
             shape='box', fillcolor='lightgreen')

    # Chạy inference
    dot.node('inference', 'Chạy model inference\nresults = model(frame, **kwargs)',
             shape='box', fillcolor='lightcoral')

    # Khởi tạo list
    dot.node('init_list', 'person_detections = []', shape='box', fillcolor='lightyellow')

    # Lặp results
    dot.node('loop_results', 'Lặp qua từng result', shape='box', fillcolor='lightblue')

    # Kiểm tra boxes
    dot.node('check_boxes', 'result.boxes\n!= None?', shape='diamond', fillcolor='lightpink')

    # Lấy thông tin
    dot.node('get_info', 'Lấy boxes, confidences,\nclass_ids',
             shape='box', fillcolor='lightyellow')

    # Lặp detections
    dot.node('loop_det', 'Lặp qua từng detection', shape='box', fillcolor='lightblue')

    # Kiểm tra class
    dot.node('check_class', 'class_id ==\nPERSON_CLASS?', shape='diamond', fillcolor='lightpink')

    # Thêm vào list
    dot.node('append', 'Thêm vào person_detections\n{bbox, confidence, class_id}',
             shape='box', fillcolor='lightgreen')

    # Return
    dot.node('return', 'Return person_detections', shape='parallelogram', fillcolor='lightcyan')

    # Kết thúc
    dot.node('end', 'Kết thúc', shape='oval', fillcolor='lightcoral')

    # Kết nối các node
    dot.edge('start', 'init')
    dot.edge('init', 'input')
    dot.edge('input', 'check_model')
    dot.edge('check_model', 'load_model', label='Không')
    dot.edge('check_model', 'config', label='Có')
    dot.edge('load_model', 'check_cuda')
    dot.edge('check_cuda', 'test_tensor', label='Có')
    dot.edge('check_cuda', 'set_cpu', label='Không')
    dot.edge('test_tensor', 'test_ok')
    dot.edge('test_ok', 'set_gpu', label='Có')
    dot.edge('test_ok', 'set_cpu', label='Không')
    dot.edge('set_gpu', 'config')
    dot.edge('set_cpu', 'config')
    dot.edge('config', 'check_gpu')
    dot.edge('check_gpu', 'set_half', label='Có')
    dot.edge('check_gpu', 'inference', label='Không')
    dot.edge('set_half', 'inference')
    dot.edge('inference', 'init_list')
    dot.edge('init_list', 'loop_results')
    dot.edge('loop_results', 'check_boxes')
    dot.edge('check_boxes', 'get_info', label='Có')
    dot.edge('check_boxes', 'return', label='Không')
    dot.edge('get_info', 'loop_det')
    dot.edge('loop_det', 'check_class')
    dot.edge('check_class', 'append', label='Có')
    dot.edge('check_class', 'loop_det', label='Không')
    dot.edge('append', 'loop_det')
    dot.edge('loop_det', 'return', label='Hết')
    dot.edge('return', 'end')

    return dot


def create_person_counter_flowchart():
    """Tạo sơ đồ thuật toán cho PersonCounter"""
    dot = Digraph(comment='PersonCounter Algorithm', format='png')
    dot.attr(rankdir='TB', dpi='300')
    dot.attr('node', shape='box', style='rounded,filled', fillcolor='lightblue',
             fontname='Arial', fontsize='14', width='2.5', height='0.8')

    # Bắt đầu
    dot.node('start', 'Bắt đầu', shape='oval', fillcolor='lightgreen')

    # Khởi tạo
    dot.node('init', 'Khởi tạo PersonCounter\n- current_count = 0\n- max_count = 0\n- frame_count = 0\n- start_time = now()\n- count_history = deque(100)',
             shape='box', fillcolor='lightyellow')

    # Nhận detections
    dot.node('input', 'Nhận detections\ntừ PersonDetector', shape='parallelogram', fillcolor='lightcyan')

    # Đếm
    dot.node('count', 'current_count = len(detections)', shape='box', fillcolor='lightyellow')

    # Cộng dồn
    dot.node('accumulate', 'total_detections += current_count\nframe_count += 1',
             shape='box', fillcolor='lightyellow')

    # Kiểm tra max
    dot.node('check_max', 'current_count >\nmax_count?', shape='diamond', fillcolor='lightpink')

    # Update max
    dot.node('update_max', 'max_count = current_count', shape='box', fillcolor='lightgreen')

    # Lưu history
    dot.node('save_history', 'Lưu vào lịch sử:\n- count_history.append()\n- timestamp_history.append()',
             shape='box', fillcolor='lightyellow')

    # Update stats
    dot.node('update_stats', '_update_stats()', shape='box', fillcolor='lightcoral')

    # Cập nhật total frames
    dot.node('total_frames', 'stats["total_frames"] = frame_count',
             shape='box', fillcolor='lightyellow')

    # Kiểm tra có người
    dot.node('check_person', 'current_count > 0?', shape='diamond', fillcolor='lightpink')

    # Tăng frames with persons
    dot.node('inc_frames', 'stats["frames_with_persons"] += 1',
             shape='box', fillcolor='lightgreen')

    # Tính average
    dot.node('calc_avg', 'stats["average_count"] =\nnp.mean(count_history)',
             shape='box', fillcolor='lightyellow')

    # Update max reached
    dot.node('max_reached', 'stats["max_count_reached"] = max_count',
             shape='box', fillcolor='lightyellow')

    # Return
    dot.node('return', 'Return current_count', shape='parallelogram', fillcolor='lightcyan')

    # Kết thúc
    dot.node('end', 'Kết thúc', shape='oval', fillcolor='lightcoral')

    # Kết nối
    dot.edge('start', 'init')
    dot.edge('init', 'input')
    dot.edge('input', 'count')
    dot.edge('count', 'accumulate')
    dot.edge('accumulate', 'check_max')
    dot.edge('check_max', 'update_max', label='Có')
    dot.edge('check_max', 'save_history', label='Không')
    dot.edge('update_max', 'save_history')
    dot.edge('save_history', 'update_stats')
    dot.edge('update_stats', 'total_frames')
    dot.edge('total_frames', 'check_person')
    dot.edge('check_person', 'inc_frames', label='Có')
    dot.edge('check_person', 'calc_avg', label='Không')
    dot.edge('inc_frames', 'calc_avg')
    dot.edge('calc_avg', 'max_reached')
    dot.edge('max_reached', 'return')
    dot.edge('return', 'end')

    return dot


def create_alert_system_flowchart():
    """Tạo sơ đồ thuật toán cho AlertSystem"""
    dot = Digraph(comment='AlertSystem Algorithm', format='png')
    dot.attr(rankdir='TB', dpi='300')
    dot.attr('node', shape='box', style='rounded,filled', fillcolor='lightblue',
             fontname='Arial', fontsize='14', width='2.5', height='0.8')

    # Bắt đầu
    dot.node('start', 'Bắt đầu', shape='oval', fillcolor='lightgreen')

    # Khởi tạo
    dot.node('init', 'Khởi tạo AlertSystem\n- max_count\n- enabled\n- alert_cooldown = 5s',
             shape='box', fillcolor='lightyellow')

    # Nhận person count
    dot.node('input', 'Nhận person_count', shape='parallelogram', fillcolor='lightcyan')

    # Kiểm tra enabled
    dot.node('check_enabled', 'enabled = True?', shape='diamond', fillcolor='lightpink')

    # Lấy thời gian
    dot.node('get_time', 'current_time = time.time()', shape='box', fillcolor='lightyellow')

    # Kiểm tra vượt ngưỡng
    dot.node('check_exceed', 'person_count >\nmax_count?', shape='diamond', fillcolor='lightpink')

    # Kiểm tra cooldown
    dot.node('check_cooldown', 'current_time - last_alert_time\n>= cooldown?',
             shape='diamond', fillcolor='lightpink')

    # Tính excess
    dot.node('calc_excess', 'excess = person_count - max_count',
             shape='box', fillcolor='lightyellow')

    # Xác định severity
    dot.node('check_severity', 'excess <= 2?', shape='diamond', fillcolor='lightpink')
    dot.node('check_critical', 'excess <= 5?', shape='diamond', fillcolor='lightpink')

    # Set severity
    dot.node('set_warning', 'severity = "warning"', shape='box', fillcolor='yellow')
    dot.node('set_critical', 'severity = "critical"', shape='box', fillcolor='orange')
    dot.node('set_emergency', 'severity = "emergency"', shape='box', fillcolor='red')

    # Tạo alert
    dot.node('create_alert', 'Tạo alert_info:\n- type, message\n- person_count, timestamp\n- is_active = True',
             shape='box', fillcolor='lightcoral')

    # Lưu alert
    dot.node('save_alert', 'alert_history.append(alert_info)\nlast_alert_time = current_time\nis_alert_active = True',
             shape='box', fillcolor='lightyellow')

    # Return alert
    dot.node('return_alert', 'Return alert_info', shape='parallelogram', fillcolor='lightcyan')

    # Return warning trong cooldown
    dot.node('return_warning', 'Return warning\n(đang trong cooldown)',
             shape='parallelogram', fillcolor='lightyellow')

    # Kiểm tra alert active
    dot.node('check_active', 'is_alert_active\n= True?', shape='diamond', fillcolor='lightpink')

    # Kết thúc alert
    dot.node('end_alert', 'is_alert_active = False\nReturn thông báo kết thúc',
             shape='box', fillcolor='lightgreen')

    # Return None
    dot.node('return_none', 'Return None', shape='parallelogram', fillcolor='lightgray')

    # Kết thúc
    dot.node('end', 'Kết thúc', shape='oval', fillcolor='lightcoral')

    # Kết nối
    dot.edge('start', 'init')
    dot.edge('init', 'input')
    dot.edge('input', 'check_enabled')
    dot.edge('check_enabled', 'return_none', label='Không')
    dot.edge('check_enabled', 'get_time', label='Có')
    dot.edge('get_time', 'check_exceed')
    dot.edge('check_exceed', 'check_cooldown', label='Có')
    dot.edge('check_cooldown', 'calc_excess', label='Có')
    dot.edge('check_cooldown', 'return_warning', label='Không')
    dot.edge('calc_excess', 'check_severity')
    dot.edge('check_severity', 'set_warning', label='Có')
    dot.edge('check_severity', 'check_critical', label='Không')
    dot.edge('check_critical', 'set_critical', label='Có')
    dot.edge('check_critical', 'set_emergency', label='Không')
    dot.edge('set_warning', 'create_alert')
    dot.edge('set_critical', 'create_alert')
    dot.edge('set_emergency', 'create_alert')
    dot.edge('create_alert', 'save_alert')
    dot.edge('save_alert', 'return_alert')
    dot.edge('check_exceed', 'check_active', label='Không')
    dot.edge('check_active', 'end_alert', label='Có')
    dot.edge('check_active', 'return_none', label='Không')
    dot.edge('end_alert', 'end')
    dot.edge('return_alert', 'end')
    dot.edge('return_warning', 'end')
    dot.edge('return_none', 'end')

    return dot


def create_data_logger_flowchart():
    """Tạo sơ đồ thuật toán cho DataLogger"""
    dot = Digraph(comment='DataLogger Algorithm', format='png')
    dot.attr(rankdir='TB', dpi='300')
    dot.attr('node', shape='box', style='rounded,filled', fillcolor='lightblue',
             fontname='Arial', fontsize='14', width='2.5', height='0.8')

    # Bắt đầu
    dot.node('start', 'Bắt đầu', shape='oval', fillcolor='lightgreen')

    # Khởi tạo
    dot.node('init', 'Khởi tạo DataLogger\n- filename\n- enabled\n- data_buffer = []',
             shape='box', fillcolor='lightyellow')

    # Kiểm tra file exists
    dot.node('check_file', 'File CSV\ntồn tại?', shape='diamond', fillcolor='lightpink')

    # Tạo file
    dot.node('create_file', 'Tạo file CSV\nvới header', shape='box', fillcolor='lightgreen')

    # Nhận stats
    dot.node('input', 'Nhận stats dict\ntừ PersonCounter', shape='parallelogram', fillcolor='lightcyan')

    # Kiểm tra enabled
    dot.node('check_enabled', 'enabled = True?', shape='diamond', fillcolor='lightpink')

    # Tạo record
    dot.node('create_record', 'Tạo record:\n- timestamp, datetime\n- person_count, max_count\n- fps, detection_rate\n- running_time',
             shape='box', fillcolor='lightyellow')

    # Thêm vào buffer
    dot.node('append_buffer', 'data_buffer.append(record)',
             shape='box', fillcolor='lightyellow')

    # Gọi save
    dot.node('call_save', 'Gọi save_to_csv()\n(định kỳ hoặc khi kết thúc)',
             shape='box', fillcolor='lightcoral')

    # Kiểm tra buffer
    dot.node('check_buffer', 'data_buffer\nkhông rỗng?', shape='diamond', fillcolor='lightpink')

    # Mở file
    dot.node('open_file', 'Mở file CSV\n(append mode)', shape='box', fillcolor='lightyellow')

    # Ghi dữ liệu
    dot.node('write_data', 'Ghi tất cả records\ntrong buffer vào file',
             shape='box', fillcolor='lightgreen')

    # Xóa buffer
    dot.node('clear_buffer', 'data_buffer.clear()', shape='box', fillcolor='lightyellow')

    # Skip
    dot.node('skip', 'Bỏ qua (disabled\nhoặc buffer rỗng)',
             shape='box', fillcolor='lightgray')

    # Kết thúc
    dot.node('end', 'Kết thúc', shape='oval', fillcolor='lightcoral')

    # Kết nối
    dot.edge('start', 'init')
    dot.edge('init', 'check_file')
    dot.edge('check_file', 'create_file', label='Không')
    dot.edge('check_file', 'input', label='Có')
    dot.edge('create_file', 'input')
    dot.edge('input', 'check_enabled')
    dot.edge('check_enabled', 'create_record', label='Có')
    dot.edge('check_enabled', 'skip', label='Không')
    dot.edge('create_record', 'append_buffer')
    dot.edge('append_buffer', 'call_save')
    dot.edge('call_save', 'check_buffer')
    dot.edge('check_buffer', 'open_file', label='Có')
    dot.edge('check_buffer', 'skip', label='Không')
    dot.edge('open_file', 'write_data')
    dot.edge('write_data', 'clear_buffer')
    dot.edge('clear_buffer', 'end')
    dot.edge('skip', 'end')

    return dot


def create_visualizer_flowchart():
    """Tạo sơ đồ thuật toán cho Visualizer"""
    dot = Digraph(comment='Visualizer Algorithm', format='png')
    dot.attr(rankdir='TB', dpi='300')
    dot.attr('node', shape='box', style='rounded,filled', fillcolor='lightblue',
             fontname='Arial', fontsize='14', width='2.5', height='0.8')

    # Bắt đầu
    dot.node('start', 'Bắt đầu', shape='oval', fillcolor='lightgreen')

    # Khởi tạo
    dot.node('init', 'Khởi tạo Visualizer\n- bbox_color\n- text_color\n- font_scale',
             shape='box', fillcolor='lightyellow')

    # Nhận frame
    dot.node('input', 'Nhận frame, detections,\nperson_count, stats',
             shape='parallelogram', fillcolor='lightcyan')

    # Copy frame
    dot.node('copy', 'display_frame = frame.copy()', shape='box', fillcolor='lightyellow')

    # Lặp detections
    dot.node('loop_det', 'Lặp qua từng detection', shape='box', fillcolor='lightblue')

    # Lấy bbox
    dot.node('get_bbox', 'Lấy bbox, confidence', shape='box', fillcolor='lightyellow')

    # Vẽ rectangle
    dot.node('draw_rect', 'cv2.rectangle()\nVẽ bounding box',
             shape='box', fillcolor='lightgreen')

    # Tạo label
    dot.node('create_label', 'label = f"Person {i+1}: {conf:.2f}"',
             shape='box', fillcolor='lightyellow')

    # Vẽ background
    dot.node('draw_bg', 'cv2.rectangle()\nVẽ background cho text',
             shape='box', fillcolor='lightyellow')

    # Vẽ text
    dot.node('draw_text', 'cv2.putText()\nVẽ label', shape='box', fillcolor='lightgreen')

    # Kiểm tra hết
    dot.node('check_done', 'Hết detections?', shape='diamond', fillcolor='lightpink')

    # Tạo info panel
    dot.node('create_panel', 'Tạo info panel\n- Person Count\n- Detections\n- Frame Size',
             shape='box', fillcolor='lightyellow')

    # Vẽ stats
    dot.node('draw_stats', 'Vẽ stats panel\n- Max Count, Avg Count\n- FPS, Detection Rate',
             shape='box', fillcolor='lightyellow')

    # Kiểm tra alert
    dot.node('check_alert', 'Có alert?', shape='diamond', fillcolor='lightpink')

    # Vẽ alert
    dot.node('draw_alert', 'Vẽ cảnh báo\n(màu theo mức độ)',
             shape='box', fillcolor='red')

    # Ghép panel
    dot.node('combine', 'Ghép panel vào frame\nnp.vstack()',
             shape='box', fillcolor='lightcoral')

    # Return
    dot.node('return', 'Return display_frame', shape='parallelogram', fillcolor='lightcyan')

    # Kết thúc
    dot.node('end', 'Kết thúc', shape='oval', fillcolor='lightcoral')

    # Kết nối
    dot.edge('start', 'init')
    dot.edge('init', 'input')
    dot.edge('input', 'copy')
    dot.edge('copy', 'loop_det')
    dot.edge('loop_det', 'get_bbox')
    dot.edge('get_bbox', 'draw_rect')
    dot.edge('draw_rect', 'create_label')
    dot.edge('create_label', 'draw_bg')
    dot.edge('draw_bg', 'draw_text')
    dot.edge('draw_text', 'check_done')
    dot.edge('check_done', 'loop_det', label='Không')
    dot.edge('check_done', 'create_panel', label='Có')
    dot.edge('create_panel', 'draw_stats')
    dot.edge('draw_stats', 'check_alert')
    dot.edge('check_alert', 'draw_alert', label='Có')
    dot.edge('check_alert', 'combine', label='Không')
    dot.edge('draw_alert', 'combine')
    dot.edge('combine', 'return')
    dot.edge('return', 'end')

    return dot


def main():
    """Tạo tất cả các sơ đồ"""
    print("🎨 Bắt đầu tạo sơ đồ thuật toán...")

    # PersonDetector
    print("\n📊 Tạo sơ đồ PersonDetector...")
    dot = create_person_detector_flowchart()
    dot.render(f'{output_dir}/01_PersonDetector', view=False, cleanup=True)
    print(f"   ✅ Đã lưu: {output_dir}/01_PersonDetector.png")

    # PersonCounter
    print("\n📊 Tạo sơ đồ PersonCounter...")
    dot = create_person_counter_flowchart()
    dot.render(f'{output_dir}/02_PersonCounter', view=False, cleanup=True)
    print(f"   ✅ Đã lưu: {output_dir}/02_PersonCounter.png")

    # AlertSystem
    print("\n📊 Tạo sơ đồ AlertSystem...")
    dot = create_alert_system_flowchart()
    dot.render(f'{output_dir}/03_AlertSystem', view=False, cleanup=True)
    print(f"   ✅ Đã lưu: {output_dir}/03_AlertSystem.png")

    # DataLogger
    print("\n📊 Tạo sơ đồ DataLogger...")
    dot = create_data_logger_flowchart()
    dot.render(f'{output_dir}/04_DataLogger', view=False, cleanup=True)
    print(f"   ✅ Đã lưu: {output_dir}/04_DataLogger.png")

    # Visualizer
    print("\n📊 Tạo sơ đồ Visualizer...")
    dot = create_visualizer_flowchart()
    dot.render(f'{output_dir}/05_Visualizer', view=False, cleanup=True)
    print(f"   ✅ Đã lưu: {output_dir}/05_Visualizer.png")

    print("\n✨ Hoàn thành! Tất cả sơ đồ đã được lưu trong thư mục 'flowcharts/'")
    print("\n📝 Hướng dẫn:")
    print("   - Các file .png chứa sơ đồ thuật toán")
    print("   - Sử dụng để trình bày trong báo cáo hoặc thuyết trình")
    print("   - Có thể mở bằng bất kỳ trình xem ảnh nào")


if __name__ == "__main__":
    main()
