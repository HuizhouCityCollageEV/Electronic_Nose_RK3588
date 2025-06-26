#include <stdio.h>
#include "edge-impulse-sdk/classifier/ei_run_classifier.h"
#include "ADS1X15include/Adafruit_ADS1X15.h"

Adafruit_ADS1115 ads;

// 回调函数声明
int get_signal_data(size_t offset, size_t length, float *out_ptr);

// 定义全局缓冲区（大小为12）
static float input_buf[12];

int main(int argc, char **argv) {
    // 初始化ADS1115
    if (!ads.begin(0x48, 4)) 
    {
        printf("ADS1115 初始化失败. (\n");
        return 1;
    }
    printf("ADS1115 初始化成功!.\n");
    
    signal_t signal;            // 原始输入数据的封装
    ei_impulse_result_t result; // 存储推理结果
    EI_IMPULSE_ERROR res;       // 推理返回码

    // 配置信号结构体
    signal.total_length = 12; // 固定为12个数据点
    signal.get_data = &get_signal_data;

    // 主循环
    while(1) {
        // 读取3组数据（每组4个通道，共12个数据点）
        for(int i = 0; i < 3; i++) {
            // 读取四个通道的原始ADC值
            float adc0 = ads.readADC_SingleEnded(0);
            float adc1 = ads.readADC_SingleEnded(1);
            float adc2 = ads.readADC_SingleEnded(2);
            float adc3 = ads.readADC_SingleEnded(3);

            // 转换为电压值并填充缓冲区
            input_buf[i*4 + 0] = adc0;
            input_buf[i*4 + 1] = adc1;
            input_buf[i*4 + 2] = adc2;
            input_buf[i*4 + 3] = adc3;
            
            // 打印当前读数
            printf("Group %d: AIN0:%d, AIN1:%df, AIN2:%df, AIN3:%.d\n",
                   i, input_buf[i*4+0], input_buf[i*4+1],
                   input_buf[i*4+2], input_buf[i*4+3]);

            // 每组读数之间短暂延迟（10ms）- 与原始代码一致
            delay(10);
        }

        // 执行推理
        res = run_classifier(&signal, &result, false);
        printf("识别结果: %d\n", res);

        // 打印预测结果
        printf("预测: \n");
        for (uint16_t i = 0; i < EI_CLASSIFIER_LABEL_COUNT; i++) {
            printf("  %s : %.5f \n", 
                   ei_classifier_inferencing_categories[i],
                   result.classification[i].value);
        }

#if EI_CLASSIFIER_HAS_ANOMALY == 1
        printf("Anomaly score: %.3f\n", result.anomaly);
#endif

        // 每1s更新一次 - 与原始代码一致
        delay(1000);
    }
    return 0;
}

// 回调函数：提供最新的ADC数据
int get_signal_data(size_t offset, size_t length, float *out_ptr) {
    for (size_t i = 0; i < length; i++) {
        out_ptr[i] = input_buf[offset + i];
    }
    return EIDSP_OK;
}