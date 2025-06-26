import cv2                    # 引用OpenCV套件
from ultralytics import YOLO  # 引用YOLO套件
import time
import socket
from collections import defaultdict
import json

# ================== 新增：UDP广播函数 ==================
def send_udp_broadcast(confidence_dict, port=19198):
    """
    将包含所有类别的置信度字典以 JSON 格式广播出去
    confidence_dict: {"person":0.95, "car":0.03, ...}
    """
    # 构造符合要求的格式 {"vision": {...}}
    formatted_data = {"vision": confidence_dict}
    message = json.dumps(formatted_data)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    try:
        sock.sendto(message.encode(), ('<broadcast>', port))
        print(f'[广播] 已发送: {message}')
    except Exception as e:
        print(f'广播失败: {e}')
    finally:
        sock.close()

# ================== 主要处理函数 ==================
def process_camera(camera_index, model_path):
    """
    使用YOLO物体检测处理来自摄像头的影像串流，
    用边界框包围检测物体、显示物体名称和FPS。
    """

    try:
        model = YOLO(model_path)       # 加载YOLO模型文件
    except Exception as e:
        print(f"加载YOLO模型时出错了：{e}")
        return

    cap = cv2.VideoCapture(camera_index)  # 打开摄像头

    if not cap.isOpened():  # 检查摄像头是否打开成功
        print(f"无法打开摄像头：{camera_index}.")
        return

    # 获取视频的分辨率和FPS
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps_original = int(cap.get(cv2.CAP_PROP_FPS))

    print(f"摄像头输入尺寸：{frame_width}x{frame_height}, FPS：{fps_original}")

    prev_frame_time = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 检测画面里的物体
        results = model(frame, stream=True)

        # 用于保存每个类别的最高置信度
        confidences = {}

        # 定义需要过滤的标签
        target_labels = ["chengshu", "guoshu", "weishu"]

        # 处理每个检测结果
        for r in results:
            boxes = r.boxes
            names = r.names

            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                label = names[class_id]

                # 只保留目标标签中的最大置信度
                if label in target_labels:
                    if label not in confidences or confidence > confidences[label]:
                        confidences[label] = confidence

                    # 绘制边界框
                    color = (0, 255, 0)  # 绿色边界框
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                    # 标示分类和置信度
                    text = f"{label}: {confidence:.2f}"
                    cv2.putText(frame, text, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # ========== 新增：发送融合格式的 JSON ==========
        if confidences:
            send_udp_broadcast(confidences, port=19198)  # 发送到端口 19198

        # 计算FPS
        new_frame_time = time.time()
        fps = 1 / (new_frame_time - prev_frame_time)
        prev_frame_time = new_frame_time

        # 在画面左下方显示FPS（取到小数点后两位）
        cv2.putText(frame, f"FPS: {fps:.2f}",
                    (10, frame_height - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (255, 255, 255), 2)  # 白色文字

        # 显示处理后的画面
        cv2.imshow('Real-time Object Detection', frame)

        # 按 'q' 键退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()           # 释放资源
    cv2.destroyAllWindows() # 关闭窗口
    print("实时监测已结束")

if __name__ == "__main__":
    camera_device = '/dev/video11'      # 指定摄像头设备
    yolo_model = './best_rknn_model'    # 指定YOLO模型文件的名称路径

    # 开始实时监测
    process_camera(camera_device, yolo_model)