import yt_dlp
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
from datetime import datetime, timedelta


def download_video():
    url = entry_url.get()
    save_path = entry_path.get()
    speed_limit = entry_speed.get()  # Получаем значение скорости

    if not url or not save_path:
        messagebox.showerror("Ошибка", "Укажите URL и путь сохранения!")
        return

    def run_download():
        button_download.config(state=tk.DISABLED)
        progress_bar.start()

        # Создаем переменные для хранения информации о прогрессе
        download_info = {
            'start_time': None,
            'last_downloaded': 0,
            'last_time': None,
            'current_speed': 0,
            'video_title': "Инициализация..."
        }

        def update_progress(d):
            if d['status'] == 'downloading':
                # Обновляем название видео
                if '_filename' in d:
                    filename = d['_filename'].split('.')[0]  # Убираем расширение
                    download_info['video_title'] = filename

                # Рассчитываем скорость и время до завершения
                if download_info['start_time'] is None:
                    download_info['start_time'] = time.time()
                    download_info['last_time'] = time.time()
                    download_info['last_downloaded'] = d.get('downloaded_bytes', 0)
                else:
                    now = time.time()
                    time_elapsed = now - download_info['last_time']

                    if time_elapsed > 0.5:  # Обновляем статистику каждые 0.5 сек
                        downloaded = d.get('downloaded_bytes', 0)
                        delta_bytes = downloaded - download_info['last_downloaded']
                        download_info['current_speed'] = delta_bytes / time_elapsed

                        # Обновляем UI
                        window.after(0, update_ui, download_info, d)

                        download_info['last_time'] = now
                        download_info['last_downloaded'] = downloaded

        def update_ui(info, d):
            # Обновляем название видео
            label_video.config(text=f"Скачивается: {info['video_title']}")

            # Рассчитываем оставшееся время
            if info['current_speed'] > 0:
                total_bytes = d.get('total_bytes', 0)
                if total_bytes:
                    remaining_bytes = total_bytes - info['last_downloaded']
                    remaining_time = remaining_bytes / info['current_speed']

                    # Форматируем время в ЧЧ:ММ:СС
                    if remaining_time > 0:
                        remaining_str = str(timedelta(seconds=int(remaining_time)))
                        label_time.config(text=f"Осталось: {remaining_str}")
                    else:
                        label_time.config(text="Осталось: вычисление...")
                else:
                    label_time.config(text="Осталось: неизвестно")
            else:
                label_time.config(text="Осталось: вычисление...")

        ydl_opts = {
            'outtmpl': f'{save_path}/%(title)s.%(ext)s',
            'format': 'bestvideo+bestaudio/best',
            'ignoreerrors': True,
            'progress_hooks': [update_progress],
            'ratelimit': int(speed_limit) * 1024 if speed_limit else None,  # Переводим КБ/с в Б/с
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            messagebox.showinfo("Успех", "Загрузка завершена!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки: {e}")
        finally:
            progress_bar.stop()
            button_download.config(state=tk.NORMAL)
            label_video.config(text="Скачивается: ---")
            label_time.config(text="Осталось: ---")

    # Запуск в отдельном потоке
    threading.Thread(target=run_download, daemon=True).start()


def browse_path():
    folder = filedialog.askdirectory()
    if folder:
        entry_path.delete(0, tk.END)
        entry_path.insert(0, folder)


# Настройка окна
window = tk.Tk()
window.geometry("600x400")
window.title("YouTube Downloader")

# Виджеты
frame = ttk.Frame(window, padding="20")
frame.pack(fill=tk.BOTH, expand=True)

# Поле для URL
label_url = ttk.Label(frame, text="URL плейлиста/видео:")
label_url.grid(row=0, column=0, sticky=tk.W)

entry_url = ttk.Entry(frame, width=50)
entry_url.grid(row=0, column=1, pady=5, padx=5)
entry_url.insert(0, "https://youtube.com/playlist?list=...")

# Поле для пути сохранения
label_path = ttk.Label(frame, text="Путь сохранения:")
label_path.grid(row=1, column=0, sticky=tk.W)

entry_path = ttk.Entry(frame, width=50)
entry_path.grid(row=1, column=1, pady=5, padx=5)
entry_path.insert(0, "D:/downloads")

button_browse = ttk.Button(frame, text="Обзор", command=browse_path)
button_browse.grid(row=1, column=2, padx=5)

# Поле для ограничения скорости (в КБ/с)
label_speed = ttk.Label(frame, text="Ограничение скорости (КБ/с):")
label_speed.grid(row=2, column=0, sticky=tk.W)

entry_speed = ttk.Entry(frame, width=10)
entry_speed.grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
entry_speed.insert(0, "100")  # Значение по умолчанию (100 КБ/с)

# Кнопка загрузки
button_download = ttk.Button(frame, text="Скачать", command=download_video)
button_download.grid(row=3, column=1, pady=20)

# Информация о текущем видео
label_video = ttk.Label(frame, text="Скачивается: ---")
label_video.grid(row=4, column=0, columnspan=3, pady=5)

# Время до окончания
label_time = ttk.Label(frame, text="Осталось: ---")
label_time.grid(row=5, column=0, columnspan=3, pady=5)

# Прогресс-бар
progress_bar = ttk.Progressbar(frame, mode="indeterminate", length=400)
progress_bar.grid(row=6, column=0, columnspan=3)

window.mainloop()