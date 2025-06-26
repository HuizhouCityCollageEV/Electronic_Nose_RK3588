import tkinter as tk
from tkinter import ttk
from collections import defaultdict
import threading
import socket
import json
import os

# 使用 pygame.mixer 来播放声音（跨平台兼容）
try:
    import pygame
    pygame.mixer.init()
except ImportError:
    print("请先安装 pygame: pip install pygame")
    exit(1)

# =================== 配置区域 ===================
LABELS = ["chengshu", "guoshu", "weishu"]
LABEL_TO_INDEX = {label: idx for idx, label in enumerate(LABELS)}

UDP_PORT = 19198

MATURITY_MATRIX = [
    [5, 4, 'X'],  # 嗅觉 - 过熟
    [4, 3, 2],    # 嗅觉 - 成熟
    ['X', 2, 1]   # 嗅觉 - 未熟
]
# =================================================

class FusionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🍌 多模态融合识别系统 v2.2 - 基于RK3588 版")
        self.root.geometry("1000x500")
        self.root.resizable(False, False)

        self.smell_data = {}
        self.vision_data = {}

        self.sound_enabled = True
        self.last_result = ""

        self.create_widgets()
        self.start_udp_listener()

        self.update_timer()

    def create_widgets(self):
        style = ttk.Style()
        style.configure("TLabel", font=("Arial", 12))
        style.configure("Header.TLabel", font=("Arial", 14, "bold"))
        style.configure("Custom.Horizontal.TProgressbar", thickness=20)

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 模型输入显示
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(pady=10, fill=tk.X)

        smell_frame = ttk.LabelFrame(input_frame, text="嗅觉", padding=10)
        vision_frame = ttk.LabelFrame(input_frame, text="视觉", padding=10)

        self.smell_label = ttk.Label(smell_frame, text="等待数据...", justify=tk.LEFT)
        self.vision_label = ttk.Label(vision_frame, text="等待数据...", justify=tk.LEFT)

        self.smell_label.pack(anchor=tk.W)
        self.vision_label.pack(anchor=tk.W)

        smell_frame.pack(side=tk.LEFT, expand=True, fill=tk.X)
        vision_frame.pack(side=tk.RIGHT, expand=True, fill=tk.X)

        # 置信度进度条
        pb_frame = ttk.LabelFrame(main_frame, text="置信度", padding=10)
        pb_frame.pack(fill=tk.X, pady=10)

        self.progress_bars = {}
        for label in LABELS:
            ttk.Label(pb_frame, text=label).pack(anchor=tk.W)
            pb = ttk.Progressbar(
                pb_frame,
                orient="horizontal",
                length=400,
                mode="determinate",
                maximum=100,
                style="Custom.Horizontal.TProgressbar"
            )
            pb.pack(pady=5, fill=tk.X)
            self.progress_bars[label] = pb

        # 开关选项
        self.sound_var = tk.BooleanVar(value=True)
        sound_checkbox = ttk.Checkbutton(
            main_frame,
            text="启用语音",
            variable=self.sound_var,
            command=self.toggle_sound
        )
        sound_checkbox.pack(pady=5)

        # 结果展示
        self.result_label = ttk.Label(
            main_frame,
            text="最终结果：等待分析...",
            font=("Arial", 16, "bold"),
            anchor="center"
        )
        self.result_label.pack(pady=10)

    def toggle_sound(self):
        self.sound_enabled = self.sound_var.get()

    def start_udp_listener(self):
        def udp_loop():
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(("0.0.0.0", UDP_PORT))
                print(f"Listening on UDP port {UDP_PORT}...")
            except Exception as e:
                print(f"[Error] Bind failed: {e}")
                return

            while True:
                try:
                    data, addr = sock.recvfrom(1024)
                    result = json.loads(data.decode())
                    if "smell" in result:
                        self.smell_data = result["smell"]
                    elif "vision" in result:
                        self.vision_data = result["vision"]
                except Exception as e:
                    print(f"[Error] Failed to parse JSON: {e}")

        # 启动 UDP 监听线程
        threading.Thread(target=udp_loop, daemon=True).start()

    def update_timer(self):
        self.update_fusion_result()
        self.root.after(100, self.update_timer)

    def update_fusion_result(self):
        fusion_scores = [0.0 for _ in range(len(LABELS))]

        smell_max_label = max(self.smell_data, key=self.smell_data.get) if self.smell_data else None
        vision_max_label = max(self.vision_data, key=self.vision_data.get) if self.vision_data else None

        maturity_level = 0

        if smell_max_label and vision_max_label:
            smell_idx = LABEL_TO_INDEX[smell_max_label]
            vision_idx = LABEL_TO_INDEX[vision_max_label]

            # 计算成熟度等级
            smell_maturity = smell_idx + 1
            vision_maturity = vision_idx + 1

            # 根据提供的矩阵计算成熟度等级
            try:
                level = MATURITY_MATRIX[smell_maturity - 1][vision_maturity - 1]
                if isinstance(level, int):
                    maturity_level = level
                else:
                    maturity_level = "未知"
            except IndexError:
                maturity_level = "错误"

            # 更新融合得分
            fusion_scores[smell_idx] += self.smell_data[smell_max_label]
            fusion_scores[vision_idx] += self.vision_data[vision_max_label]

        # 更新UI
        max_score = 0.0
        max_label = ""

        for i, label in enumerate(LABELS):
            score = fusion_scores[i]
            self.progress_bars[label]["value"] = int(score * 100)
            if score > max_score:
                max_score = score
                max_label = label

        smell_str = "\n".join([f"{k}: {v:.2f}" for k, v in self.smell_data.items()])
        vision_str = "\n".join([f"{k}: {v:.2f}" for k, v in self.vision_data.items()])
        self.smell_label.config(text=smell_str or "无数据")
        self.vision_label.config(text=vision_str or "无数据")

        if max_label:
            self.result_label.config(text=f"最终判定：{max_label} （总置信度：{max_score:.4f}），成熟度等级：{maturity_level}")

            # 播放语音
            if self.sound_enabled and max_label != self.last_result:
                sound_path = f"./voices/{max_label}.mp3"
                if os.path.exists(sound_path):
                    try:
                        pygame.mixer.music.load(sound_path)
                        pygame.mixer.music.play()
                    except Exception as e:
                        print(f"[Error] 播放音频失败: {e}")
                self.last_result = max_label
        else:
            self.result_label.config(text="正在等待模型输入...")

if __name__ == "__main__":
    try:
        root = tk.Tk()
        print("Tk initialized")
        app = FusionGUI(root)
        print("FusionGUI created")
        root.mainloop()
    except Exception as e:
        print(f"[Fatal Error]: {e}")