# 📄 项目 README

## 📦 项目简介

本项目集成了**气味识别**、**视觉识别**、**数据收集**和**摄影功能**，适用于 **Rockchip RK3588** 设备。

---

## ⚙️ 使用步骤

### 1. 准备工作

#### 1.1 解压 Edge Impulse 项目文件
- 从 [Edge Impulse](https://www.edgeimpulse.com/) 下载 TensorFlow Lite C 项目。
- 解压后会得到三个主要文件夹：
  - `model-parameters/`
  - `tflite/`
  - `src/`
- 将这三个文件夹复制到本项目的根目录中。

#### 1.2 设置脚本可执行权限
```bash
sudo chmod +x ./build.sh
sudo chmod +x ./run.sh
```

---

### 2. 构建程序

使用 `build.sh` 编译程序：

```bash
./build.sh all
```

支持参数：
- `smell`：仅构建气味识别程序  
- `collect`：仅构建数据收集程序  
- `all`：同时构建气味识别和数据收集程序  

构建完成后将生成两个可执行文件：
- `app`：气味识别主程序  
- `collect_program`：数据收集程序  

---

### 3. 运行程序

使用 `run.sh` 启动不同功能：

```bash
./run.sh [command]
```

支持命令如下：

| 命令       | 功能描述             |
|------------|----------------------|
| `collect`  | 启动数据收集程序     |
| `smell`    | 启动气味识别程序     |
| `vision`   | 启动视觉识别程序     |
| `shot`     | 启动摄影程序         |
| `all`      | 同时启动气味识别和视觉识别程序 |

#### 示例：
```bash
./run.sh smell       # 单独运行气味识别
./run.sh vision      # 单独运行视觉识别
./run.sh all         # 同时运行气味识别和视觉识别
```

> 注意：所有程序默认在后台运行。

---

## 🔁 替换模型（YOLOv11 -> RKNN）

以下步骤用于**替换视觉识别模块中的 YOLO 模型为自定义训练模型**，并将其转换为适用于 RK3588 的 `.rknn` 格式。

> ⚠️ 此步骤必须在 **x64 架构的 Ubuntu 系统** 上进行！

### 1. 配置 Conda 环境
- 将项目文件夹 `env/` 中的 `yolo11.zip` 解压，并导入你的 Conda 环境中，此处的env/路径替换成你自己的：
  ```bash
  unzip env/yolo11.zip -d env/
  conda env create -f env/yolo11/environment.yml
  ```
- 激活环境：
  ```bash
  conda activate yolo11
  ```

### 2. 模型转换
- 将你训练好并导出的 YOLOv11 模型（如 `best.pt`）放入 `pt2rknn/` 文件夹。
- 执行转换脚本：
  ```bash
  python pt2rknn.py
  ```

如果转换成功，将在当前目录生成：
- `best_rknn_model/` 文件夹
  - 包含 `best.rknn` 和 `metadata.yaml`

### 3. 替换模型
- 将整个 `best_rknn_model/` 文件夹移动至项目根目录，替换原有模型即可。

---

## 🧪 版本要求（重要）

为确保 RKNN 模型正常运行，请确认以下工具版本一致且均为 **2.3.2**：

| 工具名称             | 版本号  |
|----------------------|---------|
| `rknpu2`             | 2.3.2   |
| `rknn-toolkit2`      | 2.3.2   |
| `rknn-toolkit2-lite` | 2.3.2   |

如果不一致，请更新相关库或 SDK 至统一版本。

---

## 📁 目录结构说明

```
project_root/
├── ADS1X15include/        # Adafruit ADS1X15 库文件
│   ├── Adafruit_ADS1X15.cpp
│   └── Adafruit_ADS1X15.h
├── env/                   # Conda 环境配置
│   └── yolo11.zip
├── pt2rknn/               # 模型转换脚本
│   └── pt2rknn.py
├── vision/                # 视觉识别模块
│   ├── best_rknn_model/   # 转换后的 RKNN 模型
│   │   ├── best.rknn
│   │   └── metadata.yaml
│   ├── run.py             # 视觉识别主程序
│   └── shot.py            # 摄影程序
│─── voices/               # 语音文件识别到成熟度xx的香蕉
│    ├── maturity_1.mp3
│    ├── maturity_2.mp3
│    ├── maturity_3.mp3
│    ├── maturity_4.mp3
│    └── maturity_5.mp3
├── build.sh               # 构建脚本
├── collect.cpp            # 数据收集源代码
├── gui.py                 # GUI 界面脚本
├── main.cpp               # 主程序源代码
├── Makefile               # Makefile 文件
├── README.md              # 项目说明文档
└── run.sh                 # 运行脚本
```
---

如有任何疑问或改进意见，欢迎提交 Issue 或 Pull Request！