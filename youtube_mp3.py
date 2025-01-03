import sys
import os
import threading
import tkinter as tk
from tkinter import messagebox, filedialog
import yt_dlp

class YouTubeDownloader(tk.Tk):
    def __init__(self):
        super().__init__()
        wd = 500
        self.title("쏜칩 YouTube MP3 Downloader")
        self.geometry(f"{wd}x220")
        self.resizable(False,False)

        self.url_label = tk.Label(self, text="YouTube URL:")
        self.url_label.pack(pady=5)

        self.url_entry = tk.Entry(self, width=50)
        self.url_entry.pack(pady=5)

        self.download_button = tk.Button(self, text="다운로드 시작", command=self.start_download)
        self.download_button.pack(pady=10)
        
        self.stop_button = tk.Button(self, text="다운로드 종료", command=self.stop_download)
        self.stop_button.pack(pady=5)

        # Progress Label: 크기 조정 및 줄바꿈 설정
        self.progress_label = tk.Label(self, text="상태: 대기중...", wraplength=wd, justify="left", anchor="w")  # 줄바꿈 및 왼쪽 정렬
        self.progress_label.pack(pady=10, fill="x", padx=10)
        
        self.stop_yn = False
        self.download_thread = None
        self.stop_event = threading.Event()

    def resource_path(self, relative_path):
        """ 필수 파일의 절대 경로를 반환 """
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller로 빌드된 경우
            return os.path.join(sys._MEIPASS, relative_path)
        # 개발 환경
        return os.path.join(os.path.abspath("."), relative_path)
        
    def start_download(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showwarning("Input Error", "Please enter a YouTube URL")
            return

        download_path = filedialog.askdirectory()
        if not download_path:
            messagebox.showwarning("Input Error", "Please select a directory")
            return

        try:
            self.stop_yn = False
            # self.down(url, download_path)
            
            # 스레드 생성
            self.download_thread = threading.Thread(target=self.down, args=(url, download_path))
            
            # 스레드 시작
            self.download_thread.start()

            # messagebox.showinfo("알림", "Download Start!")
        except Exception as e:
            messagebox.showerror("Download Error", f"An error occurred: {e}")    
            

    def down(self, url, download_path):
        def progress_hook(d):
            if self.stop_event.is_set():
                raise yt_dlp.utils.DownloadError("상태: 다운로드 종료.")
            
            if d['status'] == 'downloading':
                progress = d['_percent_str']
                speed = d['_speed_str']
                self.progress_label.config(text=f"상태: 다운로드중.. = {progress} at {speed}")
            elif d['status'] == 'finished':
                filename = d['filename']
                elapsed = d['elapsed']
                
                current_text = self.progress_label.cget("text")
                self.progress_label.config(text=f"{current_text} / 다운로드 완료 = {filename} (Elapsed time: {elapsed:.2f} seconds)")
                
        # yt-dlp 옵션 설정
        ffmpeg_dir = self.resource_path("ffmpeg")
        print(ffmpeg_dir)
        
        ydl_opts = {
            # 'ffmpeg_location': r'H:\workspace\python\joker\youtubeToMp3\ffmpeg',
            'ffmpeg_location': ffmpeg_dir,
            'format': 'bestaudio/best',  # 최상의 오디오 품질 선택
            'extractaudio': True,         # 오디오만 추출
            'audioformat': 'mp3',         # 오디오 형식 설정
            'outtmpl': f'{download_path}/%(title)s.%(ext)s',  # 저장 경로 및 파일 이름 설정
            'postprocessors': [{           # MP3로 변환
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',  # 비트레이트 설정
            }],
            'progress_hooks': [progress_hook],  # 진행 상태를 업데이트하는 훅
        }

        try:
            print("스레드 시작: 작업을 수행합니다.")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
            print("스레드 종료: 작업이 중단되었습니다.")
            # 스레드가 종료될 때까지 대기
            self.download_thread.join()   
                 
        except yt_dlp.utils.DownloadError as e:
            self.progress_label.config(text=str(e))
                
            
    def stop_download(self):
        self.stop_yn = True
        self.stop_event.set()


if __name__ == "__main__":
    app = YouTubeDownloader()
    app.mainloop()