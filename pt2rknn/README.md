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