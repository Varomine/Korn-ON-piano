import tkinter as tk
from tkinter import messagebox
import pygame
import os
import requests
import io
from PIL import Image, ImageTk

# --- ตั้งค่าทรัพยากรเสียงเปียโนจริง ---
# ดึงไฟล์เสียง .mp3 จากคลังเสียงเปียโนคุณภาพสูง
SAMPLE_BASE_URL = "https://raw.githubusercontent.com/fuhton/piano-mp3/master/piano-mp3/"
NOTES_MAPPING = {
    'C': 'C4', 'C#': 'Db4', 'D': 'D4', 'D#': 'Eb4',
    'E': 'E4', 'F': 'F4', 'F#': 'Gb4', 'G': 'G4',
    'G#': 'Ab4', 'A': 'A4', 'A#': 'Bb4', 'B': 'B4'
}

class SplashScreen:
    def __init__(self, root, on_finished):
        self.root = root
        self.on_finished = on_finished
        self.root.title("Korn-ON! Piano Loading...")
        self.root.geometry("500x550")
        self.root.configure(bg='#1a1a1a')
        self.root.eval('tk::PlaceWindow . center')
        
        # 1. แสดงโลโก้จาก URL
        self.img_url = "https://github.com/Varomine/Korn-ON-piano/blob/main/images/korn.PNG?raw=true"
        self.display_logo()

        # 2. หัวข้อแอป
        tk.Label(self.root, text="KORN-ON! PIANO", font=("Helvetica", 24, "bold"), 
                 fg='#00ADB5', bg='#1a1a1a').pack(pady=10)

        # 3. สถานะการโหลด (แก้บั๊กสีเรียบร้อย)
        self.label_status = tk.Label(self.root, text="กำลังเตรียมเสียงเปียโนระดับพรีเมียม...", 
                                     font=("Tahoma", 11), fg='white', bg='#1a1a1a')
        self.label_status.pack(pady=5)

        # 4. เริ่มโหลดเพลงประกอบและเตรียมระบบ
        self.audio_url = "https://github.com/Varomine/Korn-ON-piano/raw/refs/heads/sound/start.MP3"
        self.prepare_app()

    def display_logo(self):
        try:
            response = requests.get(self.img_url, timeout=10)
            img_data = Image.open(io.BytesIO(response.content))
            img_data = img_data.resize((280, 280), Image.Resampling.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(img_data)
            tk.Label(self.root, image=self.logo_img, bg='#1a1a1a', bd=0).pack(pady=(30, 10))
        except:
            tk.Label(self.root, text="🎹", font=("Arial", 80), bg='#1a1a1a', fg='#00ADB5').pack(pady=40)

    def prepare_app(self):
        try:
            pygame.mixer.init()
            # เล่นเพลง Startup
            response = requests.get(self.audio_url, timeout=10)
            if response.status_code == 200:
                audio_data = io.BytesIO(response.content)
                pygame.mixer.music.load(audio_data)
                pygame.mixer.music.play()
                
            # สร้างโฟลเดอร์สำหรับเก็บเสียงตัวอย่างถ้ายังไม่มี
            if not os.path.exists('samples'):
                os.makedirs('samples')
            
            self.check_music_status()
        except:
            self.root.after(2000, self.finish)

    def check_music_status(self):
        if pygame.mixer.music.get_busy():
            self.root.after(100, self.check_music_status)
        else:
            self.finish()

    def finish(self):
        try:
            self.root.destroy()
            self.on_finished()
        except:
            pass

class PianoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Korn-ON! Piano - Pro Realistic")
        self.root.geometry("850x500")
        self.root.configure(bg='#121212') # Dark Mode
        
        # ส่วน Header
        tk.Label(self.root, text="KORN-ON! PIANO", font=("Helvetica", 30, "bold"), 
                 bg='#121212', fg='#00ADB5').pack(pady=20)

        # โหลดคลังเสียงเปียโน
        self.sounds = {}
        self.load_samples()

        # เฟรมเปียโน
        self.piano_container = tk.Frame(self.root, bg='#121212', width=750, height=250)
        self.piano_container.pack(pady=20)

        self.create_keys()

    def load_samples(self):
        """โหลดไฟล์เสียงเปียโนจากเน็ตมาเก็บไว้ในเครื่อง (ถ้ายังไม่มี)"""
        for note_name, file_name in NOTES_MAPPING.items():
            sample_path = f"samples/{file_name}.mp3"
            
            if not os.path.exists(sample_path):
                try:
                    url = f"{SAMPLE_BASE_URL}{file_name}.mp3"
                    r = requests.get(url, timeout=5)
                    with open(sample_path, 'wb') as f:
                        f.write(r.content)
                except:
                    print(f"โหลดโน้ต {note_name} ไม่สำเร็จ")
            
            if os.path.exists(sample_path):
                self.sounds[note_name] = pygame.mixer.Sound(sample_path)

    def create_keys(self):
        # 1. สร้างปุ่มขาว (White Keys)
        white_keys = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
        w_width, w_height = 70, 220
        
        for i, key in enumerate(white_keys):
            btn = tk.Button(self.piano_container, text=key, font=("Arial", 12, "bold"),
                           bg='#F5F5F5', fg='#333', activebackground='#CCC',
                           relief=tk.FLAT, anchor=tk.S, pady=15,
                           command=lambda k=key: self.play_note(k))
            
            btn.place(x=i * (w_width + 4), y=0, width=w_width, height=w_height)
            self.root.bind(key.lower(), lambda e, k=key: self.play_note(k))

        # 2. สร้างปุ่มดำ (Black Keys) - วางแทรกกึ่งกลางระหว่างปุ่มขาว
        # ใช้ตำแหน่ง 0.75, 1.75... เพื่อให้ปุ่มดำอยู่ระหว่างช่อง
        black_keys_info = [
            ('C#', 0.72), ('D#', 1.72), 
            ('F#', 3.72), ('G#', 4.72), ('A#', 5.72)
        ]
        b_width, b_height = 45, 135

        for key, pos in black_keys_info:
            btn = tk.Button(self.piano_container, text=key, font=("Arial", 9, "bold"),
                           bg='#222', fg='white', activebackground='#444',
                           relief=tk.FLAT, anchor=tk.S, pady=10,
                           command=lambda k=key: self.play_note(k))
            
            x_pos = pos * (w_width + 4)
            btn.place(x=x_pos, y=0, width=b_width, height=b_height)
            
            # การตั้งค่าปุ่มลัด (เช่น C# กด c)
            self.root.bind(key[0].lower(), lambda e, k=key: self.play_note(k))

    def play_note(self, note):
        if note in self.sounds:
            # ใช้ Sound.play() เพื่อให้เล่นซ้อนกันเป็นคอร์ดได้
            self.sounds[note].play()

def launch_app():
    main_root = tk.Tk()
    app = PianoApp(main_root)
    main_root.mainloop()

if __name__ == "__main__":
    splash_root = tk.Tk()
    splash = SplashScreen(splash_root, launch_app)
    splash_root.mainloop()