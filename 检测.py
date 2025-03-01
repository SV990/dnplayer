import cv2
import pyautogui
import numpy as np
import time
import os
from pyautogui import Window

# 雷电模拟器的启动路径
LDPLAYER_PATH = r'"D:\软件安装位置\leidian\LDPlayer9\dnplayer.exe"'

def restart_ldplayer():
    """
    重启雷电模拟器
    """
    try:
        # 终止雷电模拟器进程
        os.system("taskkill /F /IM LDPlayer.exe")
        time.sleep(5)  # 等待进程完全终止
        # 启动雷电模拟器
        os.system(LDPLAYER_PATH)
        print("雷电模拟器已重启！")
        # 等待模拟器启动完成
        time.sleep(60)
    except Exception as e:
        print(f"重启雷电模拟器时发生错误：{e}")

def detect_black_screen(window_title_part="主号"):
    """
    检测模拟器是否卡死（黑屏）

    :param window_title_part: 窗口标题的匹配部分
    :return: (是否卡死, 灰度标准差)
    """
    try:
        # 获取雷电模拟器窗口
        window = None
        # 遍历所有窗口，找到标题包含“主号”的窗口
        for w in pyautogui.getAllTitles():
            if "主号" in w:
                window = pyautogui.getWindowsWithTitle(w)[0]
                break
        if not window:
            # 如果未找到窗口，启动雷电模拟器
            print("未找到雷电模拟器窗口，尝试启动雷电模拟器...")
            os.system(LDPLAYER_PATH)
            time.sleep(60)  # 等待模拟器启动完成
            # 再次尝试获取窗口
            for w in pyautogui.getAllTitles():
                if "主号" in w:
                    window = pyautogui.getWindowsWithTitle(w)[0]
                    break
            if not window:
                raise ValueError("启动雷电模拟器后仍未找到窗口")

        # 如果窗口最小化则恢复窗口
        if window.isMinimized:
            window.restore()
            time.sleep(1)  # 恢复窗口需要一定时间

        # 激活窗口
        window.activate()

        # 截图并处理
        screenshot = pyautogui.screenshot()
        left, top = window.left, window.top
        width, height = window.width, window.height
        screenshot_region = screenshot.crop((left, top, left + width, top + height))

        # 转换为OpenCV格式
        screenshot = cv2.cvtColor(np.array(screenshot_region), cv2.COLOR_RGB2BGR)

        # 转换为灰度图像
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

        # 计算灰度图像的标准差
        std_dev = np.std(gray)

        # 判断是否黑屏
        is_black = std_dev < 5
        return is_black, std_dev

    except Exception as e:
        print(f"检测时发生错误：{e}")
        return False, 0

def main():
    # 持续检测卡死
    normal_interval = 60 * 60  # 1小时
    emergency_interval = 60  # 1分钟
    emergency_checks = 3
    black_streak = 0
    black_screen_detected = False

    while True:
        time.sleep(5)  # 每隔 5 秒检测一次
        current_time = time.time()

        if not black_screen_detected:
            # 正常检测：每隔1小时检测一次
            if current_time % normal_interval >= 1:
                is_black, std_dev = detect_black_screen()
                print(f"灰度标准差: {std_dev:.2f}")
                if is_black:
                    print("检测到模拟器疑似卡死（黑屏）！")
                    black_screen_detected = True
                    # 连续检测3次
                    check_count = 0
                    for _ in range(emergency_checks):
                        time.sleep(20)  # 每隔20秒检测一次
                        is_black_temp, std_dev_temp = detect_black_screen()
                        print(f"灰度标准差: {std_dev_temp:.2f}")
                        if is_black_temp:
                            check_count +=1
                        else:
                            break  # 只要有一次正常，退出检测
                    if check_count >= emergency_checks:
                        print("连续多次检测到卡死，确认模拟器卡死！")
                        restart_ldplayer()
                        # 重启后重置
                        black_screen_detected = False
                    else:
                        print("部分检测结果正常，模拟器未卡死。")
                        black_screen_detected = False
                else:
                    print("检测到模拟器正常运行。")
        else:
            # 应急检测
            pass

if __name__ == "__main__":
    main()