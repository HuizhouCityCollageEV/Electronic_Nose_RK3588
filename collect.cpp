#include "./ADS1X15include/Adafruit_ADS1X15.h"
#include <cstdio>
#include <cstdlib>
#include <ctime>
#include <unistd.h>

Adafruit_ADS1115 ads; /* Use this for the 16-bit version */

int runMinutes = 0;
int line = 1;

void setup(void) 
{
  printf("获取ADC数据\n");
  printf("ADC Range: +/- 6.144V (1 bit = 3mV/ADS1015, 0.1875mV/ADS1115)\n");

  if (!ads.begin(0x48, 4)) 
  {
    printf("Failed to initialize ADS.");
    exit(1);  // 初始化失败时退出程序
  }
}

void loop(void) {
  int16_t adc0 = 0, adc1 = 0, adc2 = 0, adc3 = 0;
  float volts0 = 0, volts1 = 0, volts2 = 0, volts3 = 0;

  /*  ADC Raw Data  */
  adc0 = ads.readADC_SingleEnded(0);
  adc1 = ads.readADC_SingleEnded(1);
  adc2 = ads.readADC_SingleEnded(2);
  adc3 = ads.readADC_SingleEnded(3);
  /*  Volts  */
  volts0 = ads.computeVolts(adc0);
  volts1 = ads.computeVolts(adc1);
  volts2 = ads.computeVolts(adc2);
  volts3 = ads.computeVolts(adc3);
  
  // 同时输出到控制台和文件
  printf("ADC: %d, %d, %d, %d, %d\n", line, adc0, adc1, adc2, adc3);
  printf("电压: %d, %f, %f, %f, %f\n", line, volts0, volts1, volts2, volts3); //这个不会输入进文件
  
  // 使用C标准库文件操作
  FILE* dataFile = fopen("data.txt", "a");
  if (dataFile != NULL) {
    fprintf(dataFile, "%d,%d,%d,%d,%d\n", line, adc0, adc1, adc2, adc3);
    fclose(dataFile);
  } else {
    printf("Error opening data.txt for writing!\n");
  }
  line++;
}

int main(int argc, char *argv[]) {
  // 检查命令行参数
  if (argc < 2) {
    printf("Usage: %s <minutes_to_run>\n", argv[0]);
    printf("Example: %s 5  (run for 5 minutes)\n", argv[0]);
    return 1;
  }
  
  runMinutes = atoi(argv[1]);
  if (runMinutes <= 0) {
    printf("Invalid runtime. Please enter a positive number of minutes.\n");
    return 1;
  }

  setup();
  
  printf("目标收集 %d 分钟...\n", runMinutes);
  printf("输出格式: 次数, AIN0, AIN1, AIN2, AIN3\n");
  printf("数据保存到 data.txt\n");
  
  // 使用时间戳计算运行时间
  time_t startTime = time(NULL);
  time_t currentTime;
  int elapsedSeconds = 0;
  int targetSeconds = runMinutes * 60;
  
  while (elapsedSeconds < targetSeconds) {
    loop();
    
    // 更新已用时间
    currentTime = time(NULL);
    elapsedSeconds = difftime(currentTime, startTime);
    
    // 每秒显示一次剩余时间
    printf("Elapsed: %d/%d minutes. Remaining: %d minutes.   \r", 
           elapsedSeconds/60, runMinutes, 
           runMinutes - elapsedSeconds/60);
    fflush(stdout); // 刷新输出缓冲区
    
    // 延迟500ms
    delay(500);
  }
  
  printf("\n\nData collection completed after %d minutes.\n", runMinutes);
  printf("Total samples collected: %d\n", targetSeconds);
  printf("Data saved to data.txt\n");
  
  return 0;
}