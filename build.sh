#!/bin/bash

# 检查是否传入了参数
if [ $# -eq 0 ]; then
    echo "错误：请提供一个参数。"
    echo "用法: $0 <参数>"
    echo "可用参数:"
    echo "  collect    - 构建数据收集程序"
    echo "  smell      - 构建气味识别程序"
    echo "  all        - 构建全部程序"
    echo "  clean      - 清理编译文件"
    echo "  clean-all  - 清理编译文件&生成的程序"
    exit 1
fi

# 获取第一个参数
command="$1"

# 根据参数执行不同操作
case "$command" in
    collect)
        echo "正在构建数据收集 程序..."
        gcc -o collect collect.cpp ./ADS1X15include/Adafruit_ADS1X15.cpp
        echo "构建数据收集程序任务 完成..."
        ;;
    smell)
        echo "正在构建气味识别 程序..."
        make -j4
        mv ./build/app ./
        echo "构建气味识别程序任务 完成..."
        ;;
    all)
        echo "正在构建全部 程序..."
        make -j4 && gcc -o collect collect.cpp ./ADS1X15include/Adafruit_ADS1X15.cpp
        mv ./build/app ./
        echo "构建全部程序任务 完成..."
        ;;
   clean)
        echo "清理编译文件..."
        make clean
        echo "清理编译文件 完成..."
        ;;
   clean-all)
        echo "清理编译文件&生成的程序..."
        make clean
        rm -rf ./build
        rm -rf ./collect
        rm -rf ./app
        echo "清理编译文件&生成的程序 完成..."
        ;;
    *)
        echo "无效的参数: $command"
        echo "可用参数:"
        echo "  collect    - 构建数据收集程序"
        echo "  smell      - 构建气味识别程序"
        echo "  all        - 构建全部程序"
        echo "  clean      - 清理编译文件"
        echo "  clean-all  - 清理编译文件&生成的程序"
        exit 1
        ;;
esac
