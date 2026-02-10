import tkinter as tk
from tkinter import messagebox
import pygame
import os
import requests
import io
from PIL import Image, ImageTk

# Configuration Links
link1 = "https://github.com/Varomine/Korn-ON-piano/raw/refs/heads/sound/piano/"
link2 = "https://github.com/Varomine/Korn-ON-piano/raw/refs/heads/sound/Guitar/"
link3 = "https://github.com/Varomine/Korn-ON-piano/raw/refs/heads/sound/Poon/"
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

class SplashScreen:
    def __init__(self, root, on_finished):
        self.root = root
        self.on_finished = on_finished
        self.root.title("Korn-ON! Piano Loading...")
        self.root.geometry("500x550")
        self.root.configure(bg='#1a1a1a')
        self.root.eval('tk::PlaceWindow . center')
        
        self.img_url = ICON_URL # ใช้ลิงก์เดียวกัน
        self.display_logo()

        tk.Label(self.root, text="KORN-ON! PIANO", font=("Helvetica", 24, "bold"), 
                 fg='#00ADB5', bg='#1a1a1a').pack(pady=10)

        self.label_status = tk.Label(self.root, text="กำลังเตรียมเสียงเปียโนระดับพรีเมียม...", 
                                     font=("Tahoma", 11), fg='white', bg='#1a1a1a')
        self.label_status.pack(pady=5)

        self.audio_url = "https://github.com/Varomine/Korn-ON-piano/raw/refs/heads/sound/start.MP3"
        self.prepare_app()

    def display_logo(self):
        try:
            response = requests.get(self.img_url, timeout=10)
            img_data = Image.open(io.BytesIO(response.content))
            
            # เก็บรูปต้นฉบับไว้ทำ Icon
            self.icon_image = ImageTk.PhotoImage(img_data)
            self.root.iconphoto(False, self.icon_image) # <-- ตั้งค่าไอคอนตรงนี้

            # ย่อรูปเพื่อแสดงโลโก้ตรงกลาง
            img_resized = img_data.resize((280, 280), Image.Resampling.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(img_resized)
            tk.Label(self.root, image=self.logo_img, bg='#1a1a1a', bd=0).pack(pady=(30, 10))
        except Exception as e:
            print(f"Error loading logo: {e}")
            tk.Label(self.root, text="🎹", font=("Arial", 80), bg='#1a1a1a', fg='#00ADB5').pack(pady=40)

    def prepare_app(self):
        try:
            pygame.mixer.pre_init(44100, -16, 2, 512)
            pygame.mixer.init()
            
            response = requests.get(self.audio_url, timeout=10)
            if response.status_code == 200:
                audio_data = io.BytesIO(response.content)
                pygame.mixer.music.load(audio_data)
                pygame.mixer.music.set_volume(0.8)
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
        self.root.title("Korn-ON! Piano")
        self.root.geometry("1250x600")
        self.root.configure(bg='#121212')
        
        # ตั้งค่าไอคอนแอป
        self.set_app_icon()

        # 1. Title
        tk.Label(self.root, text="KORN-ON! PIANO", font=("Helvetica", 30, "bold"), 
                 bg='#121212', fg='#00ADB5').pack(pady=(20, 10))

        # 2. Control Frame (Radio Buttons)
        self.control_frame = tk.Frame(self.root, bg='#121212')
        self.control_frame.pack(pady=5)

        self.instrument_var = tk.StringVar(value="Piano")
        
        # Style for radio buttons
        rb_style = {
            'bg': '#121212', 'fg': 'white', 
            'selectcolor': '#333333', 
            'activebackground': '#121212', 
            'activeforeground': '#00ADB5', 
            'font': ("Arial", 12)
        }

        self.rb_piano = tk.Radiobutton(self.control_frame, text="Piano (Default)", 
                                     variable=self.instrument_var, value="Piano", 
                                     command=self.change_instrument, **rb_style)
        
        self.rb_guitar = tk.Radiobutton(self.control_frame, text="Guitar", 
                                      variable=self.instrument_var, value="Guitar", 
                                      command=self.change_instrument, **rb_style)
        self.rb_poon = tk.Radiobutton(self.control_frame, text="Poon", 
                                      variable=self.instrument_var, value="Poon", 
                                      command=self.change_instrument, **rb_style)

        self.rb_piano.pack(side=tk.LEFT, padx=15)
        self.rb_guitar.pack(side=tk.LEFT, padx=15)
        self.rb_poon.pack(side=tk.LEFT, padx=15)

        # Status Label to show loading state
        self.status_label = tk.Label(self.root, text="", bg='#121212', fg='#888', font=("Arial", 10))
        self.status_label.pack()

        self.sounds = {}
        # Initial load
        self.load_samples()
        
        self.piano_container = tk.Frame(self.root, bg='#121212', height=300)
        self.piano_container.pack(pady=20, fill=tk.X, expand=True)

        self.create_keys()

    def set_app_icon(self):
        """ฟังก์ชันสำหรับโหลดและตั้งค่าไอคอน"""
        try:
            response = requests.get(ICON_URL, timeout=5)
            if response.status_code == 200:
                img_data = Image.open(io.BytesIO(response.content))
                self.app_icon = ImageTk.PhotoImage(img_data)
                self.root.iconphoto(False, self.app_icon)
        except Exception as e:
            print(f"Could not set app icon: {e}")

    def change_instrument(self):
        """Handle Radio Button Change"""
        selection = self.instrument_var.get()
        global SAMPLE_BASE_URL
        
        if selection == "Piano":
            SAMPLE_BASE_URL = link1
        elif selection == "Guitar":
            SAMPLE_BASE_URL = link2
        elif selection == "Poon":
            SAMPLE_BASE_URL = link3
            
        # Update status
        self.status_label.config(text=f"Loading {selection} sounds... please wait.")
        self.root.update() # Force UI update
        
        # Clear current sounds and reload
        self.sounds.clear()
        self.load_samples()
        
        self.status_label.config(text=f"{selection} Ready!")

    def load_samples(self):
        """Loads samples into specific folders so Piano/Guitar don't overwrite each other"""
        current_instrument = self.instrument_var.get()
        base_folder = f"samples/{current_instrument}"

        if not os.path.exists(base_folder):
            os.makedirs(base_folder)

        for note_name, file_name in NOTES_MAPPING.items():
            sample_path = f"{base_folder}/{file_name}.mp3"
            
            # Download if doesn't exist
            if not os.path.exists(sample_path):
                try:
                    url = f"{SAMPLE_BASE_URL}{file_name}.mp3"
                    headers = {'User-Agent': 'Mozilla/5.0'} 
                    r = requests.get(url, headers=headers, timeout=5)
                    
                    if r.status_code == 200:
                        with open(sample_path, 'wb') as f:
                            f.write(r.content)
                    else:
                        messagebox.showerror("Download Error", f"Failed to download {url}\n\nStatus : {r.status_code}")
                        break
                    
                except Exception as e:
                    print(f"Error loading {note_name}: {e}")
            
            # Load into Pygame mixer
            if os.path.exists(sample_path):
                try:
                    s = pygame.mixer.Sound(sample_path)
                    s.set_volume(1.0)
                    self.sounds[note_name] = s
                except pygame.error as e:
                    print(f"Pygame could not load {sample_path}: {e}")

    def create_keys(self):
        w_width = 50 
        w_height = 200
        b_width = 30   
        b_height = 120
        
        white_notes_base = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
        black_notes_data = [('C#', 0.7, 'Db'), ('D#', 1.7, 'Eb'), ('F#', 3.7, 'Gb'), ('G#', 4.7, 'Ab'), ('A#', 5.7, 'Bb')]
        
        key_maps = {
            3: { 'white': ['q', 'w', 'e', 'r', 't', 'y', 'u'], 'black': ['2', '3', '5', '6', '7'] },
            4: { 'white': ['i', 'o', 'p', 'z', 'x', 'c', 'v'], 'black': ['9', '0', 's', 'd', 'f'] },
            5: { 'white': ['b', 'n', 'm', ',', '.', '/', ']'], 'black': ['h', 'j', 'l', ';', "'"] }
        }
      
        total_offset_x = 50 
        
        for octave in [3, 4, 5]:
            # (White Keys)
            current_map = key_maps.get(octave, {'white': [], 'black': []})
            
            for i, note in enumerate(white_notes_base):
                note_name = f"{note}{octave}"
                display_key = ""
                if i < len(current_map['white']):
                    display_key = current_map['white'][i].upper()
                    self.root.bind(display_key.lower(), lambda e, n=note_name: self.play_note(n))
                    self.root.bind(display_key.upper(), lambda e, n=note_name: self.play_note(n))

                text = f"{note}{octave}\n({display_key})"
                abs_x = total_offset_x + (i * (w_width + 2))

                btn = tk.Button(self.piano_container, text=text, font=("Arial", 8, "bold"),
                                bg='white', fg='black', activebackground='#ddd',
                                relief=tk.RAISED, anchor=tk.S, pady=10,
                                command=lambda n=note_name: self.play_note(n))
                btn.place(x=abs_x, y=0, width=w_width, height=w_height)

            # (Black Keys)
            for note_char, pos_mult, alt_name in black_notes_data:
                note_name = f"{note_char}{octave}"
                
                idx = 0
                if note_char == 'C#': idx = 0
                elif note_char == 'D#': idx = 1
                elif note_char == 'F#': idx = 2
                elif note_char == 'G#': idx = 3
                elif note_char == 'A#': idx = 4
                
                display_key = ""
                if idx < len(current_map['black']):
                    display_key = current_map['black'][idx].upper()
                    self.root.bind(display_key.lower(), lambda e, n=note_name: self.play_note(n))
                    self.root.bind(display_key.upper(), lambda e, n=note_name: self.play_note(n))

                text = f"{note_char}\n({display_key})"
                abs_x = total_offset_x + (pos_mult * (w_width + 2)) - (b_width / 2) + 2

                btn = tk.Button(self.piano_container, text=text, font=("Arial", 7, "bold"),
                                bg='black', fg='white', activebackground='#333',
                                relief=tk.RAISED, anchor=tk.S, pady=5,
                                command=lambda n=note_name: self.play_note(n))
                btn.place(x=abs_x, y=0, width=b_width, height=b_height)
                btn.lift()

            total_offset_x += (7 * (w_width + 2))

    def play_note(self, note):
        if note in self.sounds:
            self.sounds[note].stop() 
            self.sounds[note].play()
        else:
            print(f"Sound not found: {note}")

def launch_app():
    main_root = tk.Tk()
    app = PianoApp(main_root)
    main_root.mainloop()

if __name__ == "__main__":
    splash_root = tk.Tk()
    splash = SplashScreen(splash_root, launch_app)
    splash_root.mainloop()