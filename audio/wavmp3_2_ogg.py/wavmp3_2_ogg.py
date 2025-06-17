import tkinter as tk
from tkinter import filedialog, messagebox
from pydub import AudioSegment
import os

class AudioConverterApp:
    def __init__(self, master):
        self.master = master
        master.title("Audio Converter (MP3/WAV to OGG)")
        master.geometry("550x300") # 稍微加大視窗以容納更多元素
        master.resizable(False, False) # 禁用視窗大小調整

        self.input_file_path = ""
        self.output_folder_path = "" # 新增一個變數來儲存輸出資料夾的路徑

        # --- Widgets ---
        self.label_title = tk.Label(master, text="Convert MP3/WAV to OGG", font=("Helvetica", 16, "bold"))
        self.label_title.pack(pady=10)

        # 輸入檔案選擇區塊
        self.frame_input = tk.LabelFrame(master, text="Select Input File", padx=10, pady=10)
        self.frame_input.pack(pady=5, padx=20, fill="x")

        self.label_input_file = tk.Label(self.frame_input, text="No input file selected", wraplength=380, justify="left")
        self.label_input_file.pack(side=tk.LEFT, expand=True, fill="x")

        self.button_browse_input = tk.Button(self.frame_input, text="Browse File", command=self.browse_input_file)
        self.button_browse_input.pack(side=tk.RIGHT, padx=5)

        # 輸出資料夾選擇區塊
        self.frame_output = tk.LabelFrame(master, text="Select Output Folder", padx=10, pady=10)
        self.frame_output.pack(pady=5, padx=20, fill="x")

        self.label_output_folder = tk.Label(self.frame_output, text="No output folder selected (will use input folder by default)", wraplength=380, justify="left")
        self.label_output_folder.pack(side=tk.LEFT, expand=True, fill="x")

        self.button_browse_output = tk.Button(self.frame_output, text="Browse Folder", command=self.browse_output_folder)
        self.button_browse_output.pack(side=tk.RIGHT, padx=5)

        # 轉換按鈕
        self.button_convert = tk.Button(master, text="Convert to OGG", command=self.convert_file, state=tk.DISABLED)
        self.button_convert.pack(pady=10)

        # 狀態顯示
        self.label_status = tk.Label(master, text="Status: Ready", fg="blue")
        self.label_status.pack(pady=5)

    def browse_input_file(self):
        filetypes = [("Audio Files", "*.mp3 *.wav"), ("MP3 Files", "*.mp3"), ("WAV Files", "*.wav"), ("All Files", "*.*")]
        chosen_file_path = filedialog.askopenfilename(
            title="Select an Audio File",
            filetypes=filetypes
        )
        if chosen_file_path:
            self.input_file_path = chosen_file_path
            self.label_input_file.config(text=f"Selected: {os.path.basename(self.input_file_path)}")
            self.update_convert_button_state() # 更新轉換按鈕狀態
            self.label_status.config(text="Status: Input file selected.", fg="blue")
        else:
            self.input_file_path = ""
            self.label_input_file.config(text="No input file selected")
            self.update_convert_button_state()
            self.label_status.config(text="Status: Ready", fg="blue")

    def browse_output_folder(self):
        chosen_folder_path = filedialog.askdirectory(
            title="Select Output Folder"
        )
        if chosen_folder_path:
            self.output_folder_path = chosen_folder_path
            self.label_output_folder.config(text=f"Selected: {os.path.basename(self.output_folder_path)}")
            self.label_status.config(text="Status: Output folder selected.", fg="blue")
        else:
            self.output_folder_path = ""
            self.label_output_folder.config(text="No output folder selected (will use input folder by default)")
            self.label_status.config(text="Status: Ready", fg="blue")

    def update_convert_button_state(self):
        # 只有在選擇了輸入檔案後才啟用轉換按鈕
        if self.input_file_path:
            self.button_convert.config(state=tk.NORMAL)
        else:
            self.button_convert.config(state=tk.DISABLED)

    def convert_file(self):
        if not self.input_file_path:
            messagebox.showwarning("No Input File", "Please select an input audio file first.")
            return

        self.label_status.config(text="Status: Converting...", fg="orange")
        self.master.update_idletasks() # 強制更新 GUI 顯示狀態

        try:
            # 載入音訊檔案
            audio = AudioSegment.from_file(self.input_file_path)

            # 決定輸出資料夾：如果使用者有選，就用選的；沒有選，就用輸入檔案的所在資料夾
            if self.output_folder_path:
                output_dir = self.output_folder_path
            else:
                output_dir = os.path.dirname(self.input_file_path)

            # 建立輸出檔案路徑
            input_filename_without_ext = os.path.splitext(os.path.basename(self.input_file_path))[0]
            output_ogg_path = os.path.join(output_dir, f"{input_filename_without_ext}.ogg")

            # 匯出為 OGG 格式
            audio.export(output_ogg_path, format="ogg")

            self.label_status.config(text=f"Status: Conversion successful! Saved to:\n{output_ogg_path}", fg="green")
            messagebox.showinfo("Conversion Complete", f"Successfully converted to OGG!\nFile saved at: {output_ogg_path}")
            
            # 轉換成功後重置選擇
            self.input_file_path = ""
            self.output_folder_path = ""
            self.label_input_file.config(text="No input file selected")
            self.label_output_folder.config(text="No output folder selected (will use input folder by default)")
            self.update_convert_button_state()
            self.label_status.config(text="Status: Ready", fg="blue")

        except FileNotFoundError:
            self.label_status.config(text="Status: Error - FFmpeg/Libav not found. See console for instructions.", fg="red")
            messagebox.showerror("Error", "FFmpeg or Libav not found.\n\nPlease install FFmpeg and ensure it's in your system's PATH. You can download it from https://ffmpeg.org/download.html")
        except Exception as e:
            self.label_status.config(text=f"Status: Conversion failed! Error: {e}", fg="red")
            messagebox.showerror("Error", f"An error occurred during conversion:\n{e}")


def main():
    print("-----------------------------------------------------------------------")
    print("IMPORTANT: This application requires 'pydub' and 'FFmpeg' (or Libav).")
    print("If you haven't already, please install them:")
    print("1. Install pydub: pip install pydub")
    print("2. Install FFmpeg: Download from https://ffmpeg.org/download.html")
    print("   (Ensure FFmpeg executable is in your system's PATH environmental variable)")
    print("-----------------------------------------------------------------------")

    root = tk.Tk()
    app = AudioConverterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()