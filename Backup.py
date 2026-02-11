import tkinter as tk
from tkinter import messagebox, ttk
import pygame
import os
import requests
import io
import threading
import concurrent.futures
from PIL import Image, ImageTk

# --- Configuration Links (คงเดิม) ---
link1 = "https://github.com/Varomine/Korn-ON-piano/raw/refs/heads/sound/piano/"
link2 = "https://github.com/Varomine/Korn-ON-piano/raw/refs/heads/sound/Guitar/"
link3 = "https://github.com/Varomine/Korn-ON-piano/raw/refs/heads/sound/Poon/"
link4 = "https://github.com/Varomine/Korn-ON-piano/raw/refs/heads/sound/Meowsynth/"
ICON_URL = "https://github.com/Varomine/Korn-ON-piano/blob/main/images/korn.PNG?raw=true"

SAMPLE_BASE_URL = link1
NOTES_MAPPING = {
    'C5': 'C5',   'C#5': 'Db5',  'D5': 'D5',   'D#5': 'Eb5',
    'E5': 'E5',   'F5': 'F5',    'F#5': 'Gb5', 'G5': 'G5',
    'G#5': 'Ab5', 'A5': 'A5',    'A#5': 'Bb5', 'B5': 'B5',
    'C4': 'C4', 'C#4': 'Db4', 'D4': 'D4', 'D#4': 'Eb4',
    'E4': 'E4', 'F4': 'F4', 'F#4': 'Gb4', 'G4': 'G4',
    'G#4': 'Ab4', 'A4': 'A4', 'A#4': 'Bb4', 'B4': 'B4',
    'C3': 'C3',   'C#3': 'Db3',  'D3': 'D3',   'D#3': 'Eb3',
    'E3': 'E3',   'F3': 'F3',    'F#3': 'Gb3', 'G3': 'G3',
    'G#3': 'Ab3', 'A3': 'A3',    'A#3': 'Bb3', 'B3': 'B3',
}

class PreLoader:
    def __init__(self, root, on_finished):
        self.root = root
        self.on_finished = on_finished
        self.root.title("Checking files...")
        self.root.geometry("400x180")
        self.root.configure(bg='#1a1a1a')
        self.root.eval('tk::PlaceWindow . center')

        tk.Label(self.root, text="กำลังตรวจสอบไฟล์เสียง...", 
                 fg='#00ADB5', bg='#1a1a1a', font=("Tahoma", 10, "bold")).pack(pady=20)

        self.progress = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, length=300, mode='determinate')
        self.progress.pack(pady=10)

        self.label_status = tk.Label(self.root, text="กำลังเริ่ม...", fg='white', bg='#1a1a1a', font=("Tahoma", 8))
        self.label_status.pack()

        threading.Thread(target=self.start_download, daemon=True).start()

    def download_task(self, info):
        folder, note, url_base = info
        path = f"samples/{folder}/{note}.mp3"
        
        # --- จุดที่แก้ไข: ถ้ามีไฟล์อยู่แล้ว ให้ข้ามการดาวน์โหลดทันที ---
        if os.path.exists(path) and os.path.getsize(path) > 0:
            return True 
        
        try:
            r = requests.get(f"{url_base}{note}.mp3", timeout=10)
            if r.status_code == 200:
                with open(path, 'wb') as f:
                    f.write(r.content)
            return True
        except:
            return False

    def start_download(self):
        instruments = {"Piano": link1, "Guitar": link2, "Poon": link3, "Meowsynth": link4}
        all_tasks = []
        
        for name, url in instruments.items():
            if not os.path.exists(f"samples/{name}"):
                os.makedirs(f"samples/{name}")
            for note_file in NOTES_MAPPING.values():
                all_tasks.append((name, note_file, url))

        total = len(all_tasks)
        
        # ใช้ ThreadPool ให้ทำงานพร้อมกัน
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(self.download_task, task) for task in all_tasks]
            done_count = 0
            for _ in concurrent.futures.as_completed(futures):
                done_count += 1
                percent = int((done_count / total) * 100)
                # อัปเดต UI ให้เห็นว่ากำลังเช็คหรือโหลด
                self.root.after(0, self.update_ui, percent, done_count, total)

        self.root.after(200, self.finish)

    def update_ui(self, percent, count, total):
        self.progress['value'] = percent
        self.label_status.config(text=f"ตรวจสอบแล้ว {count}/{total} ไฟล์ ({percent}%)")

    def finish(self):
        self.root.destroy()
        self.on_finished()

# --- ส่วน SplashScreen และ PianoApp (คงเดิมตามความต้องการของคุณ) ---
# ... (ก๊อปปี้ส่วน SplashScreen และ PianoApp จากโค้ดก่อนหน้ามาใส่ได้เลยครับ) ...

class SplashScreen:
    def __init__(self, root, on_finished):
        self.root = root
        self.on_finished = on_finished
        self.root.title("Korn-ON! Piano Loading...")
        self.root.geometry("500x550")
        self.root.configure(bg='#1a1a1a')
        self.root.eval('tk::PlaceWindow . center')
        self.display_logo()
        tk.Label(self.root, text="KORN-ON! PIANO", font=("Helvetica", 24, "bold"), fg='#00ADB5', bg='#1a1a1a').pack(pady=10)
        self.label_status = tk.Label(self.root, text="กำลังเตรียมเสียงเปียโนระดับพรีเมียม...", font=("Tahoma", 11), fg='white', bg='#1a1a1a')
        self.label_status.pack(pady=5)
        self.audio_url = "https://github.com/Varomine/Korn-ON-piano/raw/refs/heads/sound/start.MP3"
        self.prepare_app()

    def display_logo(self):
        try:
            response = requests.get(ICON_URL, timeout=10)
            img_data = Image.open(io.BytesIO(response.content))
            self.icon_image = ImageTk.PhotoImage(img_data)
            self.root.iconphoto(False, self.icon_image)
            img_resized = img_data.resize((280, 280), Image.Resampling.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(img_resized)
            tk.Label(self.root, image=self.logo_img, bg='#1a1a1a', bd=0).pack(pady=(30, 10))
        except:
            tk.Label(self.root, text="🎹", font=("Arial", 80), bg='#1a1a1a', fg='#00ADB5').pack(pady=40)

    def prepare_app(self):
        try:
            pygame.mixer.pre_init(44100, -16, 2, 512)
            pygame.mixer.init()
            response = requests.get(self.audio_url, timeout=10)
            if response.status_code == 200:
                pygame.mixer.music.load(io.BytesIO(response.content))
                pygame.mixer.music.play()
            self.check_music_status()
        except: self.finish()

    def check_music_status(self):
        if pygame.mixer.music.get_busy(): self.root.after(100, self.check_music_status)
        else: self.finish()

    def finish(self):
        try:
            self.root.destroy()
            self.on_finished()
        except: pass

class PianoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Korn-ON! Piano")
        self.root.geometry("1250x600")
        self.root.configure(bg='#121212')
        self.set_app_icon()
        tk.Label(self.root, text="KORN-ON! PIANO", font=("Helvetica", 30, "bold"), bg='#121212', fg='#00ADB5').pack(pady=(20, 10))
        self.control_frame = tk.Frame(self.root, bg='#121212')
        self.control_frame.pack(pady=5)
        self.instrument_var = tk.StringVar(value="Piano")
        rb_style = {'bg': '#121212', 'fg': 'white', 'selectcolor': '#333333', 'activebackground': '#121212', 'activeforeground': '#00ADB5', 'font': ("Arial", 12)}
        tk.Radiobutton(self.control_frame, text="Piano (Default)", variable=self.instrument_var, value="Piano", command=self.change_instrument, **rb_style).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(self.control_frame, text="Guitar", variable=self.instrument_var, value="Guitar", command=self.change_instrument, **rb_style).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(self.control_frame, text="Poon", variable=self.instrument_var, value="Poon", command=self.change_instrument, **rb_style).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(self.control_frame, text="Meowsynth", variable=self.instrument_var, value="Meowsynth", command=self.change_instrument, **rb_style).pack(side=tk.LEFT, padx=10)
        self.status_label = tk.Label(self.root, text="", bg='#121212', fg='#888', font=("Arial", 10))
        self.status_label.pack()
        self.sounds = {}
        self.load_samples()
        self.piano_container = tk.Frame(self.root, bg='#121212', height=300)
        self.piano_container.pack(pady=20, fill=tk.X, expand=True)
        self.create_keys()

    def set_app_icon(self):
        try:
            response = requests.get(ICON_URL, timeout=5)
            self.app_icon = ImageTk.PhotoImage(Image.open(io.BytesIO(response.content)))
            self.root.iconphoto(False, self.app_icon)
        except: pass

    def change_instrument(self):
        self.status_label.config(text=f"Loading {self.instrument_var.get()} sounds...")
        self.root.update()
        self.sounds.clear()
        self.load_samples()
        self.status_label.config(text=f"{self.instrument_var.get()} Ready!")

    def load_samples(self):
        inst = self.instrument_var.get()
        base = f"samples/{inst}"
        if not os.path.exists(base): os.makedirs(base)
        for note_name, file_name in NOTES_MAPPING.items():
            path = f"{base}/{file_name}.mp3"
            if os.path.exists(path):
                try:
                    s = pygame.mixer.Sound(path)
                    self.sounds[note_name] = s
                except: pass

    def create_keys(self):
        w_width, w_height, b_width, b_height = 50, 200, 30, 120
        white_notes_base = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
        black_notes_data = [('C#', 0.7), ('D#', 1.7), ('F#', 3.7), ('G#', 4.7), ('A#', 5.7)]
        key_maps = {
            3: {'w': ['q','w','e','r','t','y','u'], 'b': ['2','3','5','6','7']},
            4: {'w': ['i','o','p','z','x','c','v'], 'b': ['9','0','s','d','f']},
            5: {'w': ['b','n','m',',','.','/',']'], 'b': ['h','j','l',';',"'"]}
        }
        total_offset_x = 50 
        for octave in [3, 4, 5]:
            m = key_maps[octave]
            for i, note in enumerate(white_notes_base):
                name = f"{note}{octave}"
                key = m['w'][i].upper()
                self.root.bind(key.lower(), lambda e, n=name: self.play_note(n))
                tk.Button(self.piano_container, text=f"{name}\n({key})", font=("Arial", 8, "bold"), bg='white', anchor=tk.S, command=lambda n=name: self.play_note(n)).place(x=total_offset_x+(i*52), y=0, width=w_width, height=w_height)
            for char, pos in black_notes_data:
                name = f"{char}{octave}"
                idx = ['C#','D#','F#','G#','A#'].index(char)
                key = m['b'][idx].upper()
                self.root.bind(key.lower(), lambda e, n=name: self.play_note(n))
                btn = tk.Button(self.piano_container, text=f"{char}\n({key})", font=("Arial", 7, "bold"), bg='black', fg='white', anchor=tk.S, command=lambda n=name: self.play_note(n))
                btn.place(x=total_offset_x+(pos*52)-13, y=0, width=b_width, height=b_height)
                btn.lift()
            total_offset_x += (7 * 52)

    def play_note(self, note):
        if note in self.sounds:
            self.sounds[note].stop() 
            self.sounds[note].play()

# --- Main Logic ---
def launch_main_app():
    main_root = tk.Tk()
    PianoApp(main_root)
    main_root.mainloop()

def launch_splash():
    splash_root = tk.Tk()
    SplashScreen(splash_root, launch_main_app)
    splash_root.mainloop()

if __name__ == "__main__":
    pre_root = tk.Tk()
    loader = PreLoader(pre_root, launch_splash)
    pre_root.mainloop()