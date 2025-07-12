import yt_dlp
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading


class YouTubeDownloader:
    def __init__(self):
        self.downloaded_videos = 0
        self.total_videos = 0
        self.window = tk.Tk()
        self.window.geometry("600x400")
        self.window.title("YouTube Downloader (с прогрессом загрузки)")

        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        # Поля для URL и пути
        ttk.Label(frame, text="URL плейлиста/видео:").grid(row=0, column=0, sticky=tk.W)
        self.entry_url = ttk.Entry(frame, width=50)
        self.entry_url.grid(row=0, column=1, pady=5, padx=5)
        self.entry_url.insert(0, "https://youtube.com/playlist?list=...")

        ttk.Label(frame, text="Путь сохранения:").grid(row=1, column=0, sticky=tk.W)
        self.entry_path = ttk.Entry(frame, width=50)
        self.entry_path.grid(row=1, column=1, pady=5, padx=5)
        self.entry_path.insert(0, "D:/downloads")

        ttk.Button(frame, text="Обзор", command=self.browse_path).grid(row=1, column=2, padx=5)

        # Ограничение скорости
        ttk.Label(frame, text="Ограничение скорости (КБ/с):").grid(row=2, column=0, sticky=tk.W)
        self.entry_speed = ttk.Entry(frame, width=10)
        self.entry_speed.grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        self.entry_speed.insert(0, "100")

        # Кнопка загрузки
        self.button_download = ttk.Button(frame, text="Скачать", command=self.start_download)
        self.button_download.grid(row=3, column=1, pady=10)

        # Прогресс-бар
        self.progress_bar = ttk.Progressbar(frame, mode="indeterminate", length=400)
        self.progress_bar.grid(row=4, column=0, columnspan=3, pady=10)

        # Лейбл статуса загрузки
        self.status_label = ttk.Label(frame, text="Скачано: 0/0", font=('Arial', 10))
        self.status_label.grid(row=5, column=0, columnspan=3)

    def start_download(self):
        threading.Thread(target=self.download_video, daemon=True).start()

    def download_video(self):
        self.downloaded_videos = 0
        self.total_videos = 0
        self.button_download.config(state=tk.DISABLED)
        self.progress_bar.start()
        self.update_status_label()

        url = self.entry_url.get()
        save_path = self.entry_path.get()
        speed_limit = self.entry_speed.get()

        ydl_opts = {
            'outtmpl': f'{save_path}/%(title)s.%(ext)s',
            'format': 'bestvideo+bestaudio/best',
            'ignoreerrors': True,
            'ratelimit': int(speed_limit) * 1024 if speed_limit else None,
            'progress_hooks': [self.update_progress],
            'quiet': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if 'entries' in info:
                    self.total_videos = len(info['entries'])
                else:
                    self.total_videos = 1
                self.update_status_label()
                ydl.download([url])
            messagebox.showinfo("Успех", "Загрузка завершена!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки: {e}")
        finally:
            self.progress_bar.stop()
            self.button_download.config(state=tk.NORMAL)

    def update_progress(self, d):
        if d['status'] == 'finished':
            self.downloaded_videos += 1
            self.update_status_label()

    def update_status_label(self):
        self.status_label.config(text=f"Скачано: {self.downloaded_videos}/{self.total_videos}")
        self.window.update_idletasks()

    def browse_path(self):
        folder = filedialog.askdirectory()
        if folder:
            self.entry_path.delete(0, tk.END)
            self.entry_path.insert(0, folder)

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    app = YouTubeDownloader()
    app.run()