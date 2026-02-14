import tkinter as tk
from tkinter import messagebox, ttk
import pygame
import os
import requests
import io
import threading
import concurrent.futures
from PIL import Image, ImageTk

link1 = "https://github.com/Varomine/Korn-ON-piano/raw/refs/heads/sound/piano/"
link2 = "https://github.com/Varomine/Korn-ON-piano/raw/refs/heads/sound/Guitar/"
link3 = "https://github.com/Varomine/Korn-ON-piano/raw/refs/heads/sound/Poon/"
link4 = "https://github.com/Varomine/Korn-ON-piano/raw/refs/heads/sound/Meowsynth/"
link5 = "https://github.com/Varomine/Korn-ON-piano/raw/refs/heads/sound/Organ/"
link6 = "https://github.com/Varomine/Korn-ON-piano/raw/refs/heads/sound/Plastic/"

links = {
    "Piano": link1,
    "Guitar": link2,
    "Poon": link3,
    "Meowsynth": link4,
    "Organ": link5,
    "Plastic": link6
}
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

        tk.Label(self.root, text="Checking audio...", 
                 fg='#00ADB5', bg='#1a1a1a', font=("Tahoma", 10, "bold")).pack(pady=20)

        self.progress = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, length=300, mode='determinate')
        self.progress.pack(pady=10)

        self.label_status = tk.Label(self.root, text="Launching...", fg='white', bg='#1a1a1a', font=("Tahoma", 8))
        self.label_status.pack()

        threading.Thread(target=self.start_download, daemon=True).start()

    def download_task(self, info):
        folder, note, url_base = info
        path = f"samples/{folder}/{note}.mp3"
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
        instruments = links
        all_tasks = []
        
        for name, url in instruments.items():
            if not os.path.exists(f"samples/{name}"):
                os.makedirs(f"samples/{name}")
            for note_file in NOTES_MAPPING.values():
                all_tasks.append((name, note_file, url))

        total = len(all_tasks)
 
        with concurrent.futures.ThreadPoolExecutor(max_workers=216) as executor:
            futures = [executor.submit(self.download_task, task) for task in all_tasks]
            done_count = 0
            for _ in concurrent.futures.as_completed(futures):
                done_count += 1
                percent = int((done_count / total) * 100)
                self.root.after(0, self.update_ui, percent, done_count, total)

        self.root.after(200, self.finish)

    def update_ui(self, percent, count, total):
        self.progress['value'] = percent
        self.label_status.config(text=f"Downloading {count}/{total} files ({percent}%)")

    def finish(self):
        self.root.destroy()
        self.on_finished()


class SplashScreen:
    def __init__(self, root, on_finished):
        self.root = root
        self.on_finished = on_finished
        self.root.title("Korn-ON! Piano Loading...")
        self.root.geometry("500x550")
        self.root.configure(bg='#1a1a1a')
        self.root.eval('tk::PlaceWindow . center')
        
        self.img_url = ICON_URL
        self.display_logo()

        tk.Label(self.root, text="KORN-ON! PIANO", font=("Helvetica", 24, "bold"), 
                 fg='#00ADB5', bg='#1a1a1a').pack(pady=10)

        self.label_status = tk.Label(self.root, text="Preparing application...", 
                                     font=("Tahoma", 11), fg='white', bg='#1a1a1a')
        self.label_status.pack(pady=5)

        self.skip_btn = tk.Button(self.root, text="Skip Intro ▶", font=("Tahoma", 10, "bold"), 
                                  bg='#333333', fg='white', activebackground='#00ADB5', 
                                  activeforeground='black', command=self.finish, bd=0, padx=15, pady=5)
        self.skip_btn.pack(pady=10)

        self.audio_url = "https://github.com/Varomine/Korn-ON-piano/raw/refs/heads/sound/start.MP3"
        self.prepare_app()

    def display_logo(self):
        try:
            response = requests.get(self.img_url, timeout=10)
            img_data = Image.open(io.BytesIO(response.content))

            self.icon_image = ImageTk.PhotoImage(img_data)
            self.root.iconphoto(False, self.icon_image)

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
                
            
            self.check_music_status()
        except:
            self.root.after(2000, self.finish)

    def check_music_status(self):
        if pygame.mixer.music.get_busy():
            self.root.after(100, self.check_music_status)
        else:
            self.finish()

    def finish(self):
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
            self.root.destroy()
            self.on_finished()

class PianoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Korn-ON! Piano")
        self.root.geometry("1250x600")
        self.root.configure(bg='#121212')

        self.set_app_icon()

        self.master_volume = 1.0
        self.create_menu()
        # ----------------------------------------

        tk.Label(self.root, text="KORN-ON! PIANO", font=("Helvetica", 30, "bold"), 
                 bg='#121212', fg='#00ADB5').pack(pady=(20, 10))

        self.control_frame = tk.Frame(self.root, bg='#121212')
        self.control_frame.pack(pady=5)

        self.instrument_var = tk.StringVar(value="Piano")

        rb_style = {
            'bg': '#121212', 'fg': 'white', 
            'selectcolor': '#333333', 
            'activebackground': '#121212', 
            'activeforeground': '#00ADB5', 
            'font': ("Arial", 12)
        }

        self.rb_piano = tk.Radiobutton(self.control_frame, text="Piano (Default)", variable=self.instrument_var, value="Piano", command=self.change_instrument, **rb_style)
        self.rb_guitar = tk.Radiobutton(self.control_frame, text="Guitar", variable=self.instrument_var, value="Guitar", command=self.change_instrument, **rb_style)
        self.rb_poon = tk.Radiobutton(self.control_frame, text="Poon", variable=self.instrument_var, value="Poon", command=self.change_instrument, **rb_style)
        self.rb_meowsynth = tk.Radiobutton(self.control_frame, text="Meowsynth", variable=self.instrument_var, value="Meowsynth", command=self.change_instrument, **rb_style)
        self.rb_plastic = tk.Radiobutton(self.control_frame, text="Plastic", variable=self.instrument_var, value="Plastic", command=self.change_instrument, **rb_style)
        self.rb_organ = tk.Radiobutton(self.control_frame, text="Organ", variable=self.instrument_var, value="Organ", command=self.change_instrument, **rb_style)
        self.bt_sheet = tk.Button(self.control_frame, text="Sheet Music", command=self.sheet, bg='#00ADB5', fg='black', font=("Arial", 12, "bold"))

        self.rb_piano.pack(side=tk.LEFT, padx=10)
        self.rb_guitar.pack(side=tk.LEFT, padx=10)
        self.rb_poon.pack(side=tk.LEFT, padx=10)
        self.rb_meowsynth.pack(side=tk.LEFT, padx=10)
        self.rb_plastic.pack(side=tk.LEFT, padx=10)
        self.rb_organ.pack(side=tk.LEFT, padx=10)
        self.bt_sheet.pack(side=tk.LEFT, padx=20)

        self.status_label = tk.Label(self.root, text="", bg='#121212', fg='#888', font=("Arial", 10))
        self.status_label.pack()

        self.sounds = {}
        self.load_samples()
        
        self.piano_container = tk.Frame(self.root, bg='#121212', height=300)
        self.piano_container.pack(pady=20, fill=tk.X, expand=True)

        self.create_keys()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Volume Settings", command=self.open_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.destroy)
        menubar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menubar)

    def open_settings(self):
        win = tk.Toplevel(self.root)
        win.title("Volume Settings")
        win.geometry("300x120")
        win.configure(bg='#121212')

        tk.Label(win, text="Master Volume", fg='white', bg='#121212', font=("Arial", 12)).pack(pady=10)
        
        slider = tk.Scale(win, from_=0, to=100, orient=tk.HORIZONTAL,
                          bg='#121212', fg='white', length=200,
                          command=self.change_volume)
        slider.set(self.master_volume * 100)
        slider.pack()

    def sheet(self):
        win = tk.Toplevel(self.root)
        win.title("Sheet Music")
        win.geometry("1000x400")
        sheet = {
            "rv": '[YB] [P]] [CB] ] [RB] [I.] [XB] , B M [YB] [P]] [CB] ] [RB] [I.] [XB] , B M [YB] [P]] B C B ] B R B [I.] B X B , B [QN] M [E,] [PB.] M [UVN] O X B V [YB] P C X B N [RM] I X M , [Q.] T P , M [TN] O V [YB] M B [P]] B C B ] B R B [I.] B X B [R,] B [QN] M [T,] [P.] [QM] [TN] [O.] [XB] N N B ] [Y.B] P C B N [RM] [IX] [XB] M , [Q.] [TX] [PM] , M [TN] O [XB] N B ] [YB] B [P.] B [CB] N [YB] ] [RB] B [I.] B [XB] N [TB] ] [QB] N [TM] , [P.] M [QN] B [T]] [ON] [XB] N [TB] ] [YB] B [P.] B [CB] N [YB] ] [RB] B [I.] B [XB] N [RB] ] [QB] N [TM] , [P.] M [QN] B [T]] [ON] [XB] B N [TB] ] [YB] B [P.] B [CB] N [YB] ] [RB] B [I.] B [XB] N [RB] ] [QB] N [TM] , [P.] M [QN] B [T]] [RN] [UB] N [TB] ] [YB] B [P.] B [CB] N [YB] ] [RB] B [I.] B [XB] N [RB] ] [QB] N [TM] , [P.] M [QN] B [T]] [WN] [UV] X B M [YB] [P]] B C B ] B R B [I.] B X B [R,] B [QN] M [T,] [PV.] [QM] [TVN] O X B V [YXB] P X B N [RM] X [XB] N M X [XM] , [Q.] X [TM] , [P.] X [Q,] M [TN] X [O,] M [XN] V [YM] B [P]] B C B [Y]] B R B [I.] B X B [R,] B [QN] M [T,] [P.] [QM] [TN] [O.] [XN] M N [TB] ] [Y.B] P C B N [RM] X [IB] N [XM] X [RM] , [Q.] X [TM] , [P.] X [Q,] M [TN] X [OV] N [UB] N [TB] ] [Y]] B B [P.] B [YB] B N [YB] ] [RB] B [I.] B [XB] B N [RB] ] [QB] N [TM] , [P.] M [QN] B [T]] N [R.] N [UB] B N [TB] ] [Y]] B B [P.] B [YB] B N [YB] ] [RB] B [I.] B [XB] B N [RB] ] [QB] N [TM] , [P.] M [QN] B [T]] N [W.] N [UB] B N [TB] ] [YB] B [P.] B [YB] B N [YB] ] [RB] B [I.] B [XB] B N [RB] ] [QB] N [TM] , [P.] M [QN] B [T]] [WN] [UV] X [YPB] M B ] B ] [YBB] [Z.] [CB] [Y,] [TM] [P,] [B.] M [XVN] B V [YP] X B E X B N [RM] [IX] [XB] M , [Q.] [TX] [PM] , M [TN] O V B M [YB] [P]] [CB] ] [RB] . B [I.] [XB] [R,] [QN] M [T,] [P.] M [T.N] O V B V [YXB] E C B N [RM] [IX] [ZB] M , [Q.] [TX] [PB] , M [TN] W [UX] [YB] [EI] [YP] C B',
            "bd": 'I I O I Z P I I O I X Z I I B C Z P O V V C Z X Z'
        }
        win.configure(bg='#121212')
        def music(song):
            self.text_area['text'] = song
        self.bt_river_flow_in_you = tk.Button(win, text="River Flows in You - Yiruma", bg='#00ADB5', fg='black', font=("Arial", 12, "bold"),command=lambda: music(sheet["rv"]))
        self.bt_river_flow_in_you.place(x=25,y=25)
        self.Happy_Birthday_to_You = tk.Button(win, text="Happy Birthday to You", bg='#00ADB5', fg='black', font=("Arial", 12, "bold"),command=lambda: music(sheet["bd"]))
        self.Happy_Birthday_to_You.place(x=250,y=25)
        self.text_area = tk.Label(win, text="(Sheet music content goes here)", bg='#121212', fg='white', font=("Arial", 12),wraplength=950, justify=tk.LEFT,pady=30)
        self.text_area.place(x=25,y=70)
        

    def change_volume(self, val):
        volume = int(val) / 100
        self.master_volume = volume

        for sound in self.sounds.values():
            sound.set_volume(self.master_volume)

    def set_app_icon(self):
        try:
            response = requests.get(ICON_URL, timeout=5)
            if response.status_code == 200:
                img_data = Image.open(io.BytesIO(response.content))
                self.app_icon = ImageTk.PhotoImage(img_data)
                self.root.iconphoto(False, self.app_icon)
        except Exception as e:
            print(f"Could not set app icon: {e}")

    def change_instrument(self):
        selection = self.instrument_var.get()
        global SAMPLE_BASE_URL
        
        if selection == "Piano":
            SAMPLE_BASE_URL = link1
        elif selection == "Guitar":
            SAMPLE_BASE_URL = link2
        elif selection == "Poon":
            SAMPLE_BASE_URL = link3
        elif selection == "Meowsynth":
            SAMPLE_BASE_URL = link4
        elif selection == "Organ":
            SAMPLE_BASE_URL = link5
        elif selection == "Plastic":
            SAMPLE_BASE_URL = link6
            
        self.status_label.config(text=f"Loading {selection} sounds... please wait.")
        self.root.update()
        
        self.sounds.clear()
        self.load_samples()
        
        self.status_label.config(text=f"{selection} Ready!")

    def load_samples(self):
        current_instrument = self.instrument_var.get()
        base_folder = f"samples/{current_instrument}"

        if not os.path.exists(base_folder):
            os.makedirs(base_folder)

        for note_name, file_name in NOTES_MAPPING.items():
            sample_path = f"{base_folder}/{file_name}.mp3"

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

            if os.path.exists(sample_path):
                try:
                    s = pygame.mixer.Sound(sample_path)
                    s.set_volume(self.master_volume) 
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
    PianoApp(main_root)
    main_root.mainloop()

def launch_splash():
    splash_root = tk.Tk()
    SplashScreen(splash_root, launch_app)
    splash_root.mainloop()


splash_root = tk.Tk()
splash = PreLoader(splash_root, launch_splash)
splash_root.mainloop()