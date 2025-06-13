import os
import subprocess
import cv2
from rembg import remove
import shutil

# 定義路徑
input_video = "/home/*/oop-2025-proj-TBC/Pending videos/tank/螢幕錄製 2025-06-13 125458.mp4"
output_folder = "/home/*/oop-2025-proj-TBC/cat_folder/eraser/attacking"
temp_frames_folder = os.path.join(output_folder, "temp_frames")

# 設定 FFmpeg 提取幀的參數
fps = 30  # 每秒提取的幀數，可根據需要調整

def create_folders():
    """創建輸出和臨時資料夾"""
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(temp_frames_folder, exist_ok=True)

def extract_frames():
    """使用 FFmpeg 提取影片幀"""
    output_pattern = os.path.join(temp_frames_folder, "frame_%04d.png")
    ffmpeg_cmd = [
        "ffmpeg",
        "-i", input_video,
        "-vf", f"fps={fps}",
        output_pattern
    ]
    try:
        subprocess.run(ffmpeg_cmd, check=True, stderr=subprocess.PIPE, text=True)
        print("幀提取完成")
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg 錯誤：{e.stderr}")
        raise

def remove_background():
    """對每張圖片進行去背處理"""
    for filename in os.listdir(temp_frames_folder):
        if filename.endswith(".png"):
            input_path = os.path.join(temp_frames_folder, filename)
            output_path = os.path.join(output_folder, f"processed_{filename}")

            # 讀取圖片
            input_image = cv2.imread(input_path)
            if input_image is None:
                print(f"無法讀取圖片：{filename}")
                continue

            # 去背
            output_image = remove(input_image)

            # 儲存去背後的圖片
            cv2.imwrite(output_path, output_image)
            print(f"已處理：{filename}")

def cleanup():
    """刪除臨時資料夾"""
    if os.path.exists(temp_frames_folder):
        shutil.rmtree(temp_frames_folder)
        print("臨時資料夾已清理")

def main():
    try:
        print("開始處理...")
        create_folders()
        extract_frames()
        remove_background()
        cleanup()
        print("處理完成！")
    except Exception as e:
        print(f"發生錯誤：{e}")
        cleanup()  # 確保即使出錯也清理臨時資料

if __name__ == "__main__":
    main()