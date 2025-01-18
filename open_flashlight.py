"""
简介：
根据环境亮度自动开启或关闭闪光灯
1. 获取5个采样点的亮度值
2. 计算有效亮度值的平均值
3. 根据平均亮度值开启或关闭闪光灯

参数：
- bright_threshold: 亮度阈值，默认为50
- get_sample_points: 获取5个采样点的位置，默认为4个角落和中心点

性能：
使用默认的RGB565@QVGA，FPS约为30
使用本代码，FPS约为20

"""
import sensor, time
from pyb import LED

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)
clock = time.clock()

# 初始化LED
led = LED(4)  # 闪光灯
flash_state = False
frame_counter = 0  # 添加帧计数器

bright_threshold = 50  # 亮度阈值

def get_sample_points(img):
    # 定义5个采样点的位置（4个角落和中心点）
    margin_x = int(img.width() * 0.2)
    margin_y = int(img.height() * 0.2)
    center_x = int(img.width() / 2)   # 中心x坐标
    center_y = int(img.height() / 2)  # 中心y坐标
    
    return [
        (margin_x, margin_y),                    # 左上
        (img.width()-margin_x, margin_y),        # 右上
        (img.width()-margin_x, img.height()-margin_y),  # 右下
        (margin_x, img.height()-margin_y),       # 左下
        (center_x, center_y)                     # 中心点
    ]

while(True):
    clock.tick()
    img = sensor.snapshot()
    
    frame_counter += 1  # 增加计数器
    
    # 每50帧检测一次
    if frame_counter >= 50:
        # 获取5个采样点的亮度
        sample_points = get_sample_points(img)
        brightness_values = []
        valid_brightness_values = []  # 存储有效的亮度值
        
        for x, y in sample_points:
            pixel = img.get_pixel(x, y)
            brightness = sum(pixel) / 3  # RGB平均值作为亮度
            brightness_values.append(brightness)
            # 只添加未超过阈值4倍的亮度值
            if brightness < bright_threshold * 4:
                valid_brightness_values.append(brightness)
        
        # 计算平均亮度（使用有效值）
        if valid_brightness_values:  # 确保有有效值
            avg_brightness = sum(valid_brightness_values) / len(valid_brightness_values)
        else:  # 如果没有有效值，使用阈值作为默认值
            avg_brightness = bright_threshold
        
        # 添加调试信息
        print("所有采样点亮度值:", brightness_values)
        print("有效采样点亮度值:", valid_brightness_values)
        print("平均亮度值:", avg_brightness)
        
        # 根据亮度调整闪光灯状态
        if avg_brightness < bright_threshold:
            if not flash_state:
                led.on()
                flash_state = True
                print("光线不足，开启闪光灯")
        elif avg_brightness > bright_threshold*1.5:
            if flash_state:
                led.off()
                flash_state = False
                print("自然光充足，关闭闪光灯")
        
        print("FPS: %.2f" % clock.fps())
        print("闪光灯状态:", "开启" if flash_state else "关闭")
        print("-----------------")  # 添加分隔线便于观察
        
        frame_counter = 0  # 重置计数器