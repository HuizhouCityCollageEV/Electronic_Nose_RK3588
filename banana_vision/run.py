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
    使用YOLO物件偵測處理來自攝影機的影像串流，
    用邊界框包圍偵測物件、顯示物件名稱和FPS。
    """

    try:
        model = YOLO(model_path)       # 載入YOLO模型檔
    except Exception as e:
        print(f"載入YOLO模型時出錯了：{e}")
        return

    cap = cv2.VideoCapture(camera_index)  # 開啟攝影機

    if not cap.isOpened():  # 檢查攝影機是否開啟成功
        print(f"無法開啟攝影機：{camera_index}.")
        return

    # 獲取影片的解析度和FPS
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps_original = int(cap.get(cv2.CAP_PROP_FPS))

    print(f"攝影機輸入尺寸：{frame_width}x{frame_height}, FPS：{fps_original}")

    prev_frame_time = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 偵測畫面裡的物件
        results = model(frame, stream=True)

        # 用于保存每个类别的最高置信度
        confidences = {}

        # 定义需要过滤的标签
        target_labels = ["chengshu", "guoshu", "weishu"]

        # 處理每個偵測結果
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

                    # 繪製邊界框
                    color = (0, 255, 0)  # 綠色邊界框
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                    # 標示分類和置信度
                    text = f"{label}: {confidence:.2f}"
                    cv2.putText(frame, text, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # ========== 新增：发送融合格式的 JSON ==========
        if confidences:
            send_udp_broadcast(confidences, port=19198)  # 发送到端口 19198

        # 計算FPS
        new_frame_time = time.time()
        fps = 1 / (new_frame_time - prev_frame_time)
        prev_frame_time = new_frame_time

        # 在畫面左下方顯示FPS（取到小數點後兩位）
        cv2.putText(frame, f"FPS: {fps:.2f}",
                    (10, frame_height - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (255, 255, 255), 2)  # 白色文字

        # 顯示處理後的畫面
        cv2.imshow('Real-time Object Detection', frame)

        # 按 'q' 鍵退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()           # 釋放資源
    cv2.destroyAllWindows() # 關閉視窗
    print("實時監測已結束")

if __name__ == "__main__":
    camera_device = '/dev/video11'      # 指定攝影機裝置
    yolo_model = './best_rknn_model'    # 指定YOLO模型檔的名稱路徑

    # 開始實時監測
    process_camera(camera_device, yolo_model)