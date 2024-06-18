import tkinter as tk
from tkinter import font as tkfont, messagebox
import subprocess
from PIL import Image, ImageTk

def run_scrcpy(command):
    
        # Запуск scrcpy с заданным набором параметров
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Даем scrcpy немного времени, чтобы запуститься
        process.communicate(timeout=1)  # Ждем до 10 секунд, чтобы увидеть вывод

        

def find_device_and_connect():
    try:
        # Отключаем все текущие ADB соединения
        subprocess.run("adb disconnect", shell=True, check=True)
        # Получаем список подключенных устройств
        devices_output = subprocess.run("adb devices", shell=True, text=True, capture_output=True).stdout
        device_id = None
        for line in devices_output.splitlines():
            parts = line.split()
            if len(parts) == 2 and parts[1] == "device":
                device_id = parts[0]
                break
        
        if device_id:
            # Получаем IP-адрес устройства
            ip_result = subprocess.run(f"adb -s {device_id} shell ip -f inet addr show wlan0 | findstr inet", shell=True, text=True, capture_output=True)
            ip_address = ip_result.stdout.split()[1].split('/')[0]

            # Переводим устройство в режим приема подключений через Wi-Fi
            subprocess.run(f"adb -s {device_id} tcpip 5555", shell=True, check=True)

            # Подключаемся к устройству по Wi-Fi
            connect_result = subprocess.run(f"adb connect {ip_address}:5555", shell=True, text=True, capture_output=True)
            if "connected" in connect_result.stdout:
                # Запускаем scrcpy с IP-адресом устройства
                subprocess.Popen(f"scrcpy -s {ip_address}:5555 --video-bit-rate 8M --crop 1600:900:2017:510", shell=True)
            else:
                raise Exception("Failed to connect to device over Wi-Fi.")
        else:
            raise Exception("Device not found.")
            
    except Exception as e:
        messagebox.showerror("Connection Error", f"Failed to connect: {str(e)}")

app = tk.Tk()
app.title("Nursing Spectator")
app.geometry("600x600")
app.resizable(False, False)
app.attributes('-toolwindow', True)

# Загрузите и масштабируйте изображение фона
background_image = Image.open("back.jpg")
background_image = background_image.resize((600, 600), Image.Resampling.LANCZOS)
background_photo = ImageTk.PhotoImage(background_image)

# Установите изображение фона
background_label = tk.Label(app, image=background_photo)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

# Устанавливаем шрифт для элементов
app_font = tkfont.Font(family="Helvetica", size=12, weight="bold")

# Конфигурация кнопки "WIRED CONNECTION"
wired_command = 'cmd /c "@echo off & setlocal enabledelayedexpansion & adb disconnect > nul & scrcpy --video-bit-rate 8M --crop 1600:900:2017:510 & pause & endlocal"'
wired_button = tk.Button(app, text="WIRED CONNECTION", font=app_font,
                         command=lambda: run_scrcpy(wired_command),
                         height=2, width=20, bg="#4CAF50", fg="white", relief=tk.FLAT)
wired_button.place(x=75, y=500)

# Конфигурация кнопки "WIRELESS CONNECTION"
wireless_button = tk.Button(app, text="WIRELESS CONNECTION", font=app_font,
                            command=find_device_and_connect,
                            height=2, width=20, bg="#2196F3", fg="white", relief=tk.FLAT)
wireless_button.place(x=325, y=500)

app.mainloop()
