#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <arpa/inet.h>

#include "edge-impulse-sdk/classifier/ei_run_classifier.h"
#include "ADS1X15include/Adafruit_ADS1X15.h"

// 假设你用的是 Adafruit ADS1115
Adafruit_ADS1115 ads;

// 回调函数声明
int get_signal_data(size_t offset, size_t length, float *out_ptr);

// 定义全局缓冲区（大小为12）
static float input_buf[12];

// 新增：UDP广播初始化
int init_udp_broadcast(int port)
{
    int sock;
    struct sockaddr_in broadcastAddr;
    int broadcastEnable = 1;

    // 创建UDP socket
    if ((sock = socket(PF_INET, SOCK_DGRAM, IPPROTO_UDP)) < 0)
    {
        perror("Socket创建失败");
        return -1;
    }

    // 设置广播权限
    if (setsockopt(sock, SOL_SOCKET, SO_BROADCAST, &broadcastEnable, sizeof(broadcastEnable)) < 0)
    {
        perror("设置广播权限失败");
        close(sock);
        return -1;
    }

    memset(&broadcastAddr, 0, sizeof(broadcastAddr));
    broadcastAddr.sin_family = AF_INET;
    broadcastAddr.sin_addr.s_addr = inet_addr("255.255.255.255"); // 广播地址
    broadcastAddr.sin_port = htons(port);

    printf("UDP广播已启动，发送至端口 %d\n", port);
    return sock;
}

// 新增：发送JSON格式的推理结果
void send_inference_result(int sock, const ei_impulse_result_t *result)
{
    char buffer[1024];
    struct sockaddr_in destAddr;
    destAddr.sin_family = AF_INET;
    destAddr.sin_addr.s_addr = inet_addr("255.255.255.255");
    destAddr.sin_port = htons(19198);

    // 构造完整的JSON对象 {"smell": {...}}
    strcpy(buffer, "{\"smell\":{");

    for (uint16_t i = 0; i < EI_CLASSIFIER_LABEL_COUNT; i++)
    {
        strcat(buffer, "\"");
        strcat(buffer, ei_classifier_inferencing_categories[i]);
        strcat(buffer, "\":");
        char temp[32];
        sprintf(temp, "%.5f", result->classification[i].value);
        strcat(buffer, temp);
        if (i != EI_CLASSIFIER_LABEL_COUNT - 1)
        {
            strcat(buffer, ",");
        }
    }

    strcat(buffer, "}}");

    // 发送广播
    if (sendto(sock, buffer, strlen(buffer), 0, (struct sockaddr *)&destAddr, sizeof(destAddr)) < 0)
    {
        perror("发送失败");
    }
    else
    {
        printf("已广播: %s\n", buffer);
    }
}

int main(int argc, char **argv)
{
    // 初始化ADS1115
    if (!ads.begin(0x48, 4))
    {
        printf("ADS1115 初始化失败.\n");
        return 1;
    }
    printf("ADS1115 初始化成功!\n");

    signal_t signal;            // 原始输入数据的封装
    ei_impulse_result_t result; // 存储推理结果
    EI_IMPULSE_ERROR res;       // 推理返回码

    // 配置信号结构体
    signal.total_length = 12; // 固定为12个数据点
    signal.get_data = &get_signal_data;

    // 初始化UDP广播
    int udp_sock = init_udp_broadcast(19198);
    if (udp_sock < 0)
    {
        printf("UDP初始化失败，继续运行但不广播。\n");
    }

    // 主循环
    while (1)
    {
        // 读取3组数据（每组4个通道，共12个数据点）
        for (int i = 0; i < 3; i++)
        {
            // 读取四个通道的原始ADC值
            float adc0 = ads.readADC_SingleEnded(0);
            float adc1 = ads.readADC_SingleEnded(1);
            float adc2 = ads.readADC_SingleEnded(2);
            float adc3 = ads.readADC_SingleEnded(3);

            // 转换为电压值并填充缓冲区
            input_buf[i * 4 + 0] = adc0;
            input_buf[i * 4 + 1] = adc1;
            input_buf[i * 4 + 2] = adc2;
            input_buf[i * 4 + 3] = adc3;

            // 打印当前读数
            printf("Group %d: AIN0:%.2f, AIN1:%.2f, AIN2:%.2f, AIN3:%.2f\n",
                   i, input_buf[i * 4 + 0], input_buf[i * 4 + 1],
                   input_buf[i * 4 + 2], input_buf[i * 4 + 3]);

            // 每组读数之间短暂延迟（10ms）
            usleep(10000); // usleep单位是微秒
        }

        // 执行推理
        res = run_classifier(&signal, &result, false);
        printf("识别结果: %d\n", res);

        // 打印预测结果
        printf("预测: \n");
        for (uint16_t i = 0; i < EI_CLASSIFIER_LABEL_COUNT; i++)
        {
            printf("  %s : %.5f \n",
                   ei_classifier_inferencing_categories[i],
                   result.classification[i].value);
        }

#if EI_CLASSIFIER_HAS_ANOMALY == 1
        printf("Anomaly score: %.3f\n", result.anomaly);
#endif

        // 如果UDP初始化成功，就发送广播
        if (udp_sock >= 0)
        {
            send_inference_result(udp_sock, &result);
        }

        // 每1秒更新一次
        usleep(1000000);
    }

    close(udp_sock);
    return 0;
}

// 回调函数：提供最新的ADC数据
int get_signal_data(size_t offset, size_t length, float *out_ptr)
{
    for (size_t i = 0; i < length; i++)
    {
        out_ptr[i] = input_buf[offset + i];
    }
    return EIDSP_OK;
}