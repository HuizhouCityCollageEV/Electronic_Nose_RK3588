#!/bin/bash

# 检查是否传入了参数
if [ $# -eq 0 ]; then
    echo "错误：请提供一个参数。"
    echo "用法: $0 <参数>"
    echo "可用参数:"
    echo "  collect    - 数据收集程序"
    echo "  collect    - 数据收集程序"
    echo "  smell      - 气味识别程序"
    echo "  vision     - 视觉识别程序"
    echo "  all        - 气味&视觉识别程序"
    exit 1
fi

# 获取第一个参数
command="$1"

case "$command" in
    collect)
        # 检查是否提供了第二个参数（运行时间）
        if [ $# -lt 2 ]; then
            echo "错误：使用 '$0 collect' 时必须指定运行时间（分钟）"
            echo "用法: $0 collect <minutes_to_run>"
            echo "示例: $0 collect 5"
            exit 1
        fi

        # 检查第二个参数是否是数字
        re='^[0-9]+$'
        if ! [[ $2 =~ $re ]]; then
            echo "错误：'$2' 不是一个有效的参数(数字)"
            exit 1
        fi
        echo "正在启动数据收集程序，运行 $2 分钟..."
        sudo ./collect "$2"
        ;;
    smell)
        echo "正在启动气味识别程序..."
        sudo ./app
        ;;
   vision)
        echo "正在启动视觉识别程序..."
        python ./banana_vision/run.py
        ;;
   all)
        echo "正在启动气味&视觉识别程序..."
        sudo ./app && python ./banana_vision/run.py
        ;;
    *)
        echo "无效的参数: $command"
        echo "可用参数:"
        echo "  collect    - 数据收集程序"
        echo "  smell      - 气味识别程序"
        echo "  vision     - 视觉识别程序"
        echo "  all        - 气味&视觉识别程序"
        exit 1
        ;;
esac
