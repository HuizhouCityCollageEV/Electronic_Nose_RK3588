import cv2
import os

def take_photo_on_keypress(camera_index, base_filename='photo'):
    """
    打开摄像头并持续显示视频流，按'a'键拍照。
    文件名会根据已有照片自动递增，如 photo_001.jpg, photo_002.jpg...

    参数:
    camera_index (int): 摄像头设备索引。
    base_filename (str): 基础文件名（不含序号和扩展名）。
    """

    # 获取当前目录下所有以 base_filename 开头的照片
    existing_files = [f for f in os.listdir('.') if f.startswith(base_filename) and f.endswith('.jpg')]
    counter = len(existing_files) + 1  # 下一个要使用的编号

    # 打开摄像头
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"无法打开摄像头: {camera_index}")
        return

    print(f"正在打开摄像头... 按下 'a' 键进行拍照（将保存为 {base_filename}_XXX.jpg）")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("无法获取摄像头画面.")
            break

        # 显示当前帧
        cv2.imshow('Camera', frame)

        # 等待按键
        key = cv2.waitKey(1) & 0xFF
        if key == ord('a'):  # 按 a 键拍照
            filename = f"{base_filename}_{counter:03d}.jpg"
            cv2.imwrite(filename, frame)
            print(f"📸 照片已保存为: {filename}")
            counter += 1  # 编号递增

        elif key == ord('q'):  # 按 q 键退出程序
            print("退出程序")
            break

    # 释放资源
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    camera_device = '/dev/video11'   # 可改为 0 或其他设备路径
    base_name = 'photo'              # 照片基础名

    take_photo_on_keypress(camera_device, base_name)