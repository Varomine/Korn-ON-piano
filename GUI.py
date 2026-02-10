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
            # ปรับแต่ง mixer: frequency=44100 (standard), buffer=512 (low latency/clearer)
            pygame.mixer.pre_init(44100, -16, 2, 512)
            pygame.mixer.init()
            
            # เล่นเพลง Startup
            response = requests.get(self.audio_url, timeout=10)
            if response.status_code == 200:
                audio_data = io.BytesIO(response.content)
                pygame.mixer.music.load(audio_data)
                pygame.mixer.music.set_volume(0.8) # ปรับความดังเพลงตอนเริ่ม
                pygame.mixer.music.play()
                
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
        """โหลดไฟล์เสียงเปียโนจากเน็ตและตั้งค่าระดับเสียงสูงสุด"""
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
                sound = pygame.mixer.Sound(sample_path)
                # --- ตั้งค่าความดังที่นี่ (0.0 ถึง 1.0) ---
                sound.set_volume(1.0) 
                self.sounds[note_name] = sound
            
            if os.path.exists(sample_path):
                self.sounds[note_name] = pygame.mixer.Sound(sample_path)

    def create_keys(self):
        # --- 1. การแมปปิ้งปุ่มกดสำหรับโน้ตขาว (A-S-D-F-G-H-J) ---
        white_key_map = {
            'a': 'C', 's': 'D', 'd': 'E', 'f': 'F', 
            'g': 'G', 'h': 'A', 'j': 'B'
        }
        
        # --- 2. การแมปปิ้งปุ่มกดสำหรับโน้ตดำ/Sharp (W-E-T-Y-U) ---
        # แมปปิ้งตามตำแหน่งปุ่มบนคีย์บอร์ดที่อยู่เยื้องขึ้นไปด้านบน
        black_key_map = {
            'w': 'C#', 'e': 'D#', 
            't': 'F#', 'y': 'G#', 'u': 'A#'
        }
        
        white_keys = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
        w_width, w_height = 70, 220
        
        # สร้างปุ่มขาวและ Binding
        for i, key in enumerate(white_keys):
            display_text = f"{key}\n({list(white_key_map.keys())[i].upper()})"
            btn = tk.Button(self.piano_container, text=display_text, font=("Arial", 10, "bold"),
                           bg='#F5F5F5', fg='#333', activebackground='#CCC',
                           relief=tk.FLAT, anchor=tk.S, pady=15,
                           command=lambda k=key: self.play_note(k))
            btn.place(x=i * (w_width + 4), y=0, width=w_width, height=w_height)
            
        # ผูกปุ่มคีย์บอร์ดสำหรับโน้ตขาว
        for char, note in white_key_map.items():
            self.root.bind(char, lambda e, k=note: self.play_note(k))
            self.root.bind(char.upper(), lambda e, k=note: self.play_note(k))

        # --- 3. สร้างลิ่มโน้ตดำพร้อม Binding (W-E-T-Y-U) ---
        black_keys_info = [
            ('C#', 0.72, 'w'), ('D#', 1.72, 'e'), 
            ('F#', 3.72, 't'), ('G#', 4.72, 'y'), ('A#', 5.72, 'u')
        ]
        b_width, b_height = 45, 135

        for key, pos, char in black_keys_info:
            # แสดงชื่อโน้ตและปุ่มกด เช่น "C#\n(W)"
            display_text = f"{key}\n({char.upper()})"
            btn = tk.Button(self.piano_container, text=display_text, font=("Arial", 8, "bold"),
                           bg='#222', fg='white', activebackground='#444',
                           relief=tk.FLAT, anchor=tk.S, pady=10,
                           command=lambda k=key: self.play_note(k))
            
            x_pos = pos * (w_width + 4)
            btn.place(x=x_pos, y=0, width=b_width, height=b_height)
            
            # ผูกปุ่มคีย์บอร์ดสำหรับโน้ตดำ (เพิ่มส่วนนี้เข้ามาเพื่อให้กด Sharp ได้)
            self.root.bind(char, lambda e, k=key: self.play_note(k))
            self.root.bind(char.upper(), lambda e, k=key: self.play_note(k))

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