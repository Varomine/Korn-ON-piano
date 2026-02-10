import tkinter as tk
from tkinter import messagebox
import pygame
import os
import numpy as np
import requests
import io

class SplashScreen:
    def __init__(self, root, on_finished):
        self.root = root
        self.on_finished = on_finished
        self.root.title("Korn-ON! Piano Loading...")
        self.root.geometry("400x300")
        self.root.configure(bg='#1a1a1a')
        self.audio_url = "https://github.com/Varomine/Korn-ON-piano/raw/refs/heads/sound/start.MP3"
        self.play_startup_and_wait()
        
        self.root.eval('tk::PlaceWindow . center')
        
        tk.Label(self.root, text="🎹", font=("Arial", 60), bg='#1a1a1a').pack(pady=(50, 10))
        tk.Label(self.root, text="Korn-ON! Piano", font=("Arial", 20, "bold"), 
                 fg='white', bg='#1a1a1a').pack()
        tk.Label(self.root, text="แอปสุดโหด 🎶", font=("Arial", 14),
                 fg='#888', bg='#1a1a1a').pack(pady=20)

        self.play_startup_and_wait()

    def play_startup_and_wait(self):
        try:
            pygame.mixer.init()
            response = requests.get(self.audio_url, timeout=10)
            if response.status_code == 200:
                audio_data = io.BytesIO(response.content)
                pygame.mixer.music.load(audio_data)
                pygame.mixer.music.play()
                
                self.check_music_status()
            else:
                print("ดาวน์โหลดเสียงไม่สำเร็จ")
                self.root.after(2000, self.finish)
        except Exception as e:
            print(f"Internet Error: {e}")
            self.root.after(2000, self.finish)
        """try:
            pygame.mixer.init()
            current_dir = os.path.dirname(__file__)
            sound_path = os.path.join(current_dir, "sound", "start.mp3")
            
            if os.path.exists(sound_path):
                pygame.mixer.music.load(sound_path)
                pygame.mixer.music.play()
                # ตรวจสอบสถานะการเล่นเพลงทุกๆ 100 มิลลิวินาที
                self.check_music_status()
            else:
                # ถ้าไม่เจอไฟล์เสียง ให้รอ 2 วินาทีแล้วเข้าแอปเลย
                self.root.after(2000, self.finish)
        except Exception as e:
            print(f"Error: {e}")
            self.finish()"""

    def check_music_status(self):
        # ถ้าเพลงยังเล่นอยู่ (get_busy() เป็น True) ให้เช็คต่อgit
        if pygame.mixer.music.get_busy():
            self.root.after(100, self.check_music_status)
        else:
            # ถ้าเพลงจบแล้ว ให้เข้าแอปหลัก
            self.finish()

    def finish(self):
        self.root.destroy() # ทำลายหน้า SplashScreen
        self.on_finished() # เรียก Callback เพื่อเปิดหน้าเปียโน

class PianoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Korn-ON! Piano")
        self.root.geometry("800x400")
        self.root.configure(bg='#2c3e50')
        
        # ไม่ต้อง init mixer ซ้ำ เพราะทำจากหน้าโหลดแล้ว
        self.create_keys()

    def create_keys(self):
        title = tk.Label(self.root, text="🎹 Korn-ON! Piano", font=("Arial", 24, "bold"), 
                         bg='#2c3e50', fg='white')
        title.pack(pady=10)
        
        frame = tk.Frame(self.root, bg='#2c3e50')
        frame.pack(pady=20)

        # Black Keys
        black_keys = ['C#', 'D#', 'F#', 'G#', 'A#']
        black_frame = tk.Frame(frame, bg='#2c3e50')
        black_frame.pack()
        for key in black_keys:
            btn = tk.Button(black_frame, text=key, width=6, height=5, bg='black', fg='white',
                           activebackground='gray', command=lambda k=key: self.play_note(k))
            btn.pack(side=tk.LEFT, padx=1)
            self.root.bind(key.lower(), lambda e, k=key: self.play_note(k))

        # White Keys
        white_keys = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
        white_frame = tk.Frame(frame, bg='#2c3e50')
        white_frame.pack()
        for key in white_keys:
            btn = tk.Button(white_frame, text=key, width=8, height=10, bg='white',
                           activebackground='lightgray', command=lambda k=key: self.play_note(k))
            btn.pack(side=tk.LEFT, padx=2)
            self.root.bind(key.lower(), lambda e, k=key: self.play_note(k))

    def play_note(self, note):
        try:
            freq = self.get_frequency(note)
            self.generate_sound(freq)
        except Exception as e:
            messagebox.showerror("Error", f"Could not play note: {e}")

    def get_frequency(self, note):
        frequencies = {
            'C': 261.63, 'D': 293.66, 'E': 329.63, 'F': 349.23,
            'G': 391.99, 'A': 440.00, 'B': 493.88,
            'C#': 277.18, 'D#': 311.13, 'F#': 369.99, 'G#': 415.30, 'A#': 466.16
        }
        return frequencies.get(note, 440)

    def generate_sound(self, frequency, duration=0.5):
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = np.sin(2.0 * np.pi * frequency * np.linspace(0, duration, frames)).astype(np.float32)
        arr_stereo = np.column_stack((arr, arr))
        sound = pygame.sndarray.make_sound((arr_stereo * 32767).astype(np.int16))
        sound.play()

def launch_app():
    # ฟังก์ชันเปิดหน้าแอปหลัก
    main_root = tk.Tk()
    app = PianoApp(main_root)
    main_root.mainloop()

if __name__ == "__main__":
    # เริ่มต้นด้วย SplashScreen
    splash_root = tk.Tk()
    splash = SplashScreen(splash_root, launch_app)
    splash_root.mainloop()