import tkinter as tk
from tkinter import messagebox, ttk
import pygame
import os
import requests
import io
import threading
import concurrent.futures
import time
import re
from PIL import Image, ImageTk

# --- Configuration & Constants ---
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
    'C2': 'C2', 'C#2': 'Db2', 'D2': 'D2', 'D#2': 'Eb2', 'E2': 'E2', 'F2': 'F2', 'F#2': 'Gb2', 'G2': 'G2', 'G#2': 'Ab2', 'A2': 'A2', 'A#2': 'Bb2', 'B2': 'B2',
    'C3': 'C3', 'C#3': 'Db3', 'D3': 'D3', 'D#3': 'Eb3', 'E3': 'E3', 'F3': 'F3', 'F#3': 'Gb3', 'G3': 'G3', 'G#3': 'Ab3', 'A3': 'A3', 'A#3': 'Bb3', 'B3': 'B3',
    'C4': 'C4', 'C#4': 'Db4', 'D4': 'D4', 'D#4': 'Eb4', 'E4': 'E4', 'F4': 'F4', 'F#4': 'Gb4', 'G4': 'G4', 'G#4': 'Ab4', 'A4': 'A4', 'A#4': 'Bb4', 'B4': 'B4',
    'C5': 'C5', 'C#5': 'Db5', 'D5': 'D5', 'D#5': 'Eb5', 'E5': 'E5', 'F5': 'F5', 'F#5': 'Gb5', 'G5': 'G5', 'G#5': 'Ab5', 'A5': 'A5', 'A#5': 'Bb5', 'B5': 'B5',
    'C6': 'C6', 'C#6': 'Db6', 'D6': 'D6', 'D#6': 'Eb6', 'E6': 'E6', 'F6': 'F6', 'F#6': 'Gb6', 'G6': 'G6', 'G#6': 'Ab6', 'A6': 'A6', 'A#6': 'Bb6', 'B6': 'B6',
    'C7': 'C7'
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
        all_tasks = []
        for name, url in links.items():
            if not os.path.exists(f"samples/{name}"):
                os.makedirs(f"samples/{name}")
            for note_file in NOTES_MAPPING.values():
                all_tasks.append((name, note_file, url))
        
        total = len(all_tasks)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
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
        self.root.geometry("500x580") 
        self.root.configure(bg='#1a1a1a')
        self.root.eval('tk::PlaceWindow . center')
        self.img_url = ICON_URL
        self.display_logo()
        
        tk.Label(self.root, text="KORN-ON! PIANO", font=("Helvetica", 24, "bold"), 
                 fg='#00ADB5', bg='#1a1a1a').pack(pady=10)
        
        self.label_status = tk.Label(self.root, text="Preparing application...", 
                                     font=("Tahoma", 11), fg='white', bg='#1a1a1a')
        self.label_status.pack(pady=5)
        
        self.skip_btn = tk.Button(self.root, text="Skip ▶", font=("Tahoma", 10, "bold"), 
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
        try:
            if not self.root.winfo_exists(): 
                return
                
            if pygame.mixer.music.get_busy():
                self.root.after(100, self.check_music_status)
            else:
                self.finish()
        except:
            pass

    def finish(self):
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                
            self.root.destroy()
            self.on_finished()
        except:
            pass


class PianoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Korn-ON! Piano")
        self.root.configure(bg='#121212')
        self.set_app_icon()
        
        self.master_volume = 1.0 
        self.key_buttons = {} 
        self.sounds = {}
        self.instrument_radios = {}
        
        # Determine Layout Mode
        self.layout_var = tk.StringVar(value="Basic")

        self.sound_cache = {inst: {} for inst in links.keys()}

        self.macro_thread = None
        self.macro_running = False
        self.macro_paused = False
        self.autoplay_enabled = tk.BooleanVar(value=False)
        
        # --- MAPPINGS ---
        self.expert_key_to_note = {
            '1':'C2', '2':'D2', '3':'E2', '4':'F2', '5':'G2', '6':'A2', '7':'B2',
            '!':'C#2', '@':'D#2', '$':'F#2', '%':'G#2', '^':'A#2',
            '8':'C3', '9':'D3', '0':'E3', 'q':'F3', 'w':'G3', 'e':'A3', 'r':'B3',
            '*':'C#3', '(':'D#3', 'Q':'F#3', 'W':'G#3', 'E':'A#3',
            't':'C4', 'y':'D4', 'u':'E4', 'i':'F4', 'o':'G4', 'p':'A4', 'a':'B4',
            'T':'C#4', 'Y':'D#4', 'I':'F#4', 'O':'G#4', 'P':'A#4',
            's':'C5', 'd':'D5', 'f':'E5', 'g':'F5', 'h':'G5', 'j':'A5', 'k':'B5',
            'S':'C#5', 'D':'D#5', 'G':'F#5', 'H':'G#5', 'J':'A#5',
            'l':'C6', 'z':'D6', 'x':'E6', 'c':'F6', 'v':'G6', 'b':'A6', 'n':'B6',
            'L':'C#6', 'Z':'D#6', 'C':'F#6', 'V':'G#6', 'B':'A#6',
            'm':'C7'
        }

        self.basic_key_to_note = {}
        
        # FIX 2: Added missing '/' and '?' mappings for A5, and '}' for B5 to ensure robustness
        basic_mapping = [
            ('q','C3'), ('2','C#3'), ('w','D3'), ('3','D#3'), ('e','E3'), ('r','F3'), ('5','F#3'), ('t','G3'), ('6','G#3'), ('y','A3'), ('7','A#3'), ('u','B3'),
            ('i','C4'), ('9','C#4'), ('o','D4'), ('0','D#4'), ('p','E4'), ('z','F4'), ('s','F#4'), ('x','G4'), ('d','G#4'), ('c','A4'), ('f','A#4'), ('v','B4'),
            ('b','C5'), ('h','C#5'), ('n','D5'), ('j','D#5'), ('m','E5'), (',','F5'), ('l','F#5'), ('.','G5'), (';','G#5'), (':','G#5'), ('/','A5'), ('?','A5'), ("'",'A#5'), ('"','A#5'), (']','B5'), ('}','B5')
        ]
        
        # Allow case-insensitive typing for robust Basic playing
        for k, v in basic_mapping:
            self.basic_key_to_note[k] = v
            if k.isalpha():
                self.basic_key_to_note[k.upper()] = v
                
        self.key_to_note = self.basic_key_to_note 
        
        self.macros = {
            "Grand Escape (Weathering With You)": {
                "time": 155,
                "tempo": 146,
                "macro": "[zb][vm]|\n[zb][vm]|\n[zb][vm]|||\n[zb][vm]|\n[zb][vm]|||\n[zb][vm]|[zb][vm]|\n[jzb][zvm]xjzxjzxj[zb][xvm]hjlz\n[jzb][zvm]xjzxjzxj[zb][xvm]hzlv\n[jzb][zvm]xjzxjzxj[zb][xvm]hjlz\n[jzb][zvm]xjzxjzxj[zb][xvm]hzlv\n8 tt9 tt0 ww|0e4 ww5 qw8|||\n8 tt9 tt0 ww|884 095 881|||\n8 tt9 tt0 ww|0e4 ww5 qw8|||\n8 tt9 tt0 ww|884 095 881|||\n[15]|||\n[58] tt[59] tt[50] ww|0e[48] ww[59] qw[58]|||\n[58] tt[59] tt[50] ww|884 [80]95 881|||\n[58] tt[59] tt[50] ww|0e[48] ww[59] qw[58]|||\n[58] tt[59] rt[50] rt|rt[48] tuy[59] tt[58]|||\n[58]|||\n[58]|||\n[380] [sh] s sa[48qis]sdf s o[59w]o[os]sssds[60e]| w\n[380] [sh] s a [48qis]sdf s o[59wos]sssssds[60e]| w\n[380] [sh] sasa[48qis]sdf sso[59wos]ssd sdf[60e]| w\n[380] [sh] s sa[48qis]sdf sso[59wos]sss sds[59w]|||\nsds6 [3to] [6ti] [3tu]\n[4tu][tu][8i]uqt[8y]t1 [5to] [8ti] [5tu]\n[1tu][tu][5i]u8 5\n6 [3to] [6ti] [3tu]\n[4tu][tu][8i]uqt[8y]t1 [5to] [8ti] [5tu]\n1 5 8|\n[36wt]yu[14ti] uy[158wt] [1wt] [59wry]|\n[36wt]to[14to] iu[158wy] ui[59wtu]ui[25u]y\n[36wt]yu[14ti]iuy[158wt]t[1wt] [59wry]|\n[36wt]to[14to] iu[158wy]yui[59wtu]ui[25u]y\n[14qt]|w[qt] rt[13]| [0t] r[wy][25]\nyy[wy]uiu[36]| [wt]\nr[wt][14]|w[qt]yu[0t][13]|\n[ey] t[ey][25] wwy u[tu][36]|\nwtiuyt[14]| [wti]uyt[13]|\n[ti]uyt[25]|||sgfds[8wt]"
            },
            "River Flows in You": {
                "time": 369,
                "tempo": 110,
                "macro": "[bI]V[bS]V[bG]V[bS]V[yb]V[pb]V[db]x[pb]z[eL]z[uL]z[xjS]L[zu]L[xuk] a f [uj]H[jI] S G [jS]k[yL] p d [pL]z[xe] u S [zu]L[uk] a f| [bI]V[bS]V[bG]V[bS]V[yb]V[pb]V[db]x[pb]z[eL]z[uL]z[xjS]L[zu]x[un] a f [ub]V[bI] S G [jS]k[yL] p d [pL]z[xe] u S [zu]L[uk]|afaOurW0| yuyT[yrQ7]| yuyT[yw95]| yuyT[y2]69yuIoIu[eT60]| yuyT[yrQ7]| yuyT[yw95]| yuyT[y2]69yuIoIu[eT60]| yuyT[y7]| [yrQ]uyT[y5]| [yw9]uyT[y2] yu[I96]oIu[T6]| [ye0]uyT[y7] [rQ] [y7]u[yrQ]T[y5] [w9] [y5]u[yw9]T[y2]u[I96]o[p2]a[S96]d[fe60]| [ed60]f[ed60]S[d7]Q[ra]Q[d7][fQ][rd][SQ][d5]9[wp]9[d5][f9][wd][S9][d9]e[yd][fe][G9][he][yG][fe][S6]0e0[d6][f0][ed][S0][d7]Q[ra]Q[d7][fQ][rd][SQ][d5]9[wp]9[d5][f9][wd][S9][d9]e[yd][fe][G9][he][yG][fe][S6]0e0[d6][d0]f[ed][S0][d7]Q[ra]Q[d7][dQ]f[rd][SQ][d5]9[wp]9[d5][d9]f[wd][S9][d9][fe][yG][he][j9][eG][yf][ed][S6]0e0[d6][d0]f[ed][S0][d7]Q[ra]Q[d7][dQ]f[rd][SQ][d5]9[wp]9[d5][d9]f[wd][S9][d9][fe][yG][he][j9][eG][yf][ed][G6] [f0] [ed] [S0] [d7]S[dQ]S[rd]S[dQ]S[d5]S[d9]S[wd]a[d9]p[p2]a[S6]d[h9]G[f6]d[f6] 0 [ed] [S0] [d7]S[dQ]S[rd]S[dQ]S[d5]S[d9]S[wd]a[d9]p[p2]a[S6]d[j9]h[G6]f[G6] [f0] [ed] [S0] [d7]a[dQ]a[rd]a[dQ]a[d5]a[d9]a[wd]p[d9]o[I2]o[I6]o[p9]I[o6]I[u6] 0 e [y0]T[y7] Q ry[uQ]I[o5] 9 wo[p9]a[S2] [d6] [f9] [G6] [f6] 0 [ed] [S0] [d7]a[dQ]a[rd]a[dQ]a[d5]a[d9]a[wd]p[d9]o[I2]o[I6]o[p9]I[o6]p[f6] 0 e [d0]S[d7] Q rd[SQ]d[d5] 9 wd[S9]d[d2] [f6] [G9] [h6] [G6] 0 [ed]fdS[d7]$[a7]9Qr[dQ]9[a5]725[d9][wf][d9][S7][d2]$[p6]9Qe[yd][eS]d[S6]0e[dT][uf][pd][uS][d7]$[a7]9Qr[dQ]9[a5]725[d9][wf][d9][S7][d2]$[p6]9Qe[yd][eS]d[S6]0e[dT][uf][pd][uS][d7][f$][d7][S9][aQ]r[dQ][f9][d5][S7][a2]5[d9][wf][d9][S7][p2][a$][S6][d9][hQ][eG][yf][ed][f6]0e[dT][uf][pd][uS][d7][f$][d7][S9][aQ]r[dQ][f9][d5][S7][a2]5[d9][wf][d9][S7][p2][a$][S6][d9][jQ][he][yG][fe][G6][f0]e[dT]upu[d7][a$][d7][a9][dQ][ra][dQ][a9][d5][a7][d2][a5][d9][wp][d9][o7][I2][o$][I6][o9][pQ][eI][yo][eI][u6]0eTupS[d7][a$][d7][a9][dQ][ra][dQ][a9][d5][a7][d2][a5][d9][wp][d9][o7][I2][o$][I6][o9][pQ][eI][yo][pe][p6][a][S0][ed][pT][ua][pS][ud][a3][S7][d0][f7][G3][H7][j0]*[ka3]| [j3]kjH[jQ]T[IG]T[jQ][kT][jI][TH][j9]e[yf]e[j9][ke][yj][eH][j6]0[je][k0][L6][z0][eL][k0][H0]rur[j0][rk][uj][rH][jQ]T[IG]T[jQ][kT][jI][TH][j9]e[yf]e[j9][ke][yj][eH][j6]0[je][k0][L6][z0][eL][k0][H0]rur[j0][rk][uj][rH][jI]k[jS]HG [jS]k[yj]H[pG] [jd]k[pj]H[fe]G[uH]j[zp]L[uk]j[uk] a [jf]k[ja]H[jI]k[jS]HG [jS]k[yj]H[pG] [jd]k[pj]H[fe]G[uH]j[xp]z[uL]k[uL] a [jf]k[ja]H[jI]G[SH]j[jG]k[jS]H[yj]G[pH]j[jd]k[pj]H[je]f[uG]H[zp]L[uk]j[uk] a [jf]k[ja]H[jI]G[SH]j[jG]G[SH]j[yj]G[pH]j[jd]G[pH]j[je]f[uG]H[pj]f[uG]H[j0]k[rj]k[uj] [rf] a [pj30][ka][pj][OH][pj$] [IG] [Q$] [pj] [IG2]| [pj92][ka][pj][OH][pj6] [uf] [e6] [pj] [OH3]| [pj30][ka][pj][OH][pj$] [IG] [Q$] [pj] [IG2]| [pj92][ka][pj][OH][pj6] [uf] [e6] [pj] [OH3]| [pj30][ka][pj][OH][pj$] [IG] [VQH$][GC] [pj][IG2]| [pj92][ka][pj][OH][pj6] [uf] [jeb6][VH] [pj][OH3]| [pj30][ka][pj][OH][pj$] [IG] [VQH$][GC] [pj][IG2]| [pj92][ka][pj][OH][pj6] [uf] [jeb6][VH] [pj][OH3]| [pj30][ka][pj][OH][jQ] [TG] I j [G9] e [yj]kjH[je] [uf] S j [H0] r [uj]kjH[jQ]p[fT]p[jI]kjH[j9]p[fe]p[yj]kjH[je]k[uL]z[xS]Lkj[H0]| W r u O a f H k x V [bI]V[bS]V[bG]V[bS]V[yb]V[pb]V[db]x[pb]z[eL]z[uL]z[xjS]L[zu]L[xuk] a f [uj]H[jI] S G [jS]k[yj]kL p d [pL]z[eL]zx u S [zu]L[zu]Lk a f| [bI]V[bS]V[bG]V[bS]V[yb]V[pb]V[db]x[pb]z[eL]z[uL]z[xjS]L[zu]L[un] a f [ub]V[bI] S G [jS]k[yj]Lxp d [pL]z[xe]bLu S [zu]L[uf]Hk afaOurW0| bnbV[j6][eL]b"
            }
        }

        self.create_menu()
        self.build_ui()
        
        self.preload_all_sounds()
        self.root.bind("<KeyPress>", self.on_key_press)
        
        # Initialize the layout and the instrument correctly
        self.change_layout()

    def preload_all_sounds(self):
        self.status_label.config(text="Preloading all instruments into memory...")
        self.root.update()
        
        for inst_name in links.keys():
            base_folder = f"samples/{inst_name}"
            for note_name, file_name in NOTES_MAPPING.items():
                sample_path = f"{base_folder}/{file_name}.mp3"
                if os.path.exists(sample_path):
                    try:
                        s = pygame.mixer.Sound(sample_path)
                        s.set_volume(self.master_volume) 
                        self.sound_cache[inst_name][note_name] = s
                    except: 
                        pass
                        
        self.status_label.config(text="Preload complete!")

    def build_ui(self):
        # Header
        tk.Label(self.root, text="KORN-ON! PIANO", font=("Helvetica", 30, "bold"), 
                 bg='#121212', fg='#00ADB5').pack(pady=(15, 5))

        # Instrument controls
        self.control_frame = tk.Frame(self.root, bg='#121212')
        self.control_frame.pack(pady=5)
        self.instrument_var = tk.StringVar(value="Piano")
        rb_style = {'bg': '#121212', 'fg': 'white', 'selectcolor': '#333333', 
                    'activebackground': '#121212', 'activeforeground': '#00ADB5', 'font': ("Arial", 12)}
        
        for inst in ["Piano", "Guitar", "Poon", "Meowsynth", "Plastic", "Organ"]:
            rb = tk.Radiobutton(self.control_frame, text=inst, variable=self.instrument_var, 
                                value=inst, command=self.change_instrument, **rb_style)
            rb.pack(side=tk.LEFT, padx=10)
            self.instrument_radios[inst] = rb
            
        self.status_label = tk.Label(self.root, text="", bg='#121212', fg='#888', font=("Arial", 10))
        self.status_label.pack()

        # Macro Text Display
        self.macro_display = tk.Text(self.root, height=6, width=70, bg='#1c1c1c', fg='white', font=("Courier", 12), wrap=tk.WORD)
        self.macro_display.tag_configure("center", justify='center')
        self.macro_display.tag_config("highlight", background="#00ADB5", foreground="black")
        self.macro_display.insert(tk.END, "Select a macro and press play...", "center")
        self.macro_display.config(state=tk.DISABLED)

        # Piano wrapper
        self.piano_wrapper = tk.Frame(self.root, bg='#121212')
        self.piano_wrapper.pack(pady=10, fill=tk.BOTH, expand=True)
        self.piano_container = tk.Frame(self.piano_wrapper, bg='#121212')
        self.piano_container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Progress Frame
        self.progress_frame = tk.Frame(self.root, bg='#121212')
        
        self.time_label = tk.Label(self.progress_frame, text="00:00 / 00:00", fg='white', bg='#121212', font=("Arial", 10))
        self.time_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, orient=tk.HORIZONTAL, mode='determinate')
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Macro Control Bar
        self.macro_frame = tk.Frame(self.root, bg='#1c1c1c', pady=10)
        tk.Label(self.macro_frame, text="AUTOPLAY:", fg='#00ADB5', bg='#1c1c1c', font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(20, 10))
        self.song_selector = ttk.Combobox(self.macro_frame, values=list(self.macros.keys()), state="readonly", width=35)
        self.song_selector.current(0)
        self.song_selector.pack(side=tk.LEFT, padx=10)
        self.song_selector.bind("<<ComboboxSelected>>", self.on_song_select)

        btn_style = {'font': ("Arial", 12), 'width': 4, 'bg': '#333', 'fg': 'white', 'activebackground': '#444'}
        self.play_btn = tk.Button(self.macro_frame, text="▶", command=self.start_macro, **btn_style)
        self.play_btn.pack(side=tk.LEFT, padx=5)
        self.pause_btn = tk.Button(self.macro_frame, text="⏸", command=self.pause_macro, **btn_style)
        self.pause_btn.pack(side=tk.LEFT, padx=5)
        self.stop_btn = tk.Button(self.macro_frame, text="■", command=self.stop_macro, **btn_style)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        tk.Label(self.macro_frame, text="SPEED:", fg='#00ADB5', bg='#1c1c1c', font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(20, 5))
        self.speed_selector = ttk.Combobox(self.macro_frame, values=["0.25x", "0.5x", "0.75x", "1.0x", "1.25x", "1.5x", "2.0x"], state="readonly", width=7)
        self.speed_selector.set("1.0x")
        self.speed_selector.pack(side=tk.LEFT, padx=5)
        
        self.tempo_label = tk.Label(self.macro_frame, text="Tempo: 146 BPM", fg='#888', bg='#1c1c1c', font=("Arial", 10))
        self.tempo_label.pack(side=tk.RIGHT, padx=20)

    def change_layout(self):
        # Update layout properties
        if self.layout_var.get() == "Basic":
            self.key_to_note = self.basic_key_to_note
            self.file_menu.entryconfig("Autoplay", state=tk.DISABLED)
            if self.autoplay_enabled.get():
                self.autoplay_enabled.set(False)
                self.update_autoplay_visibility()
        else:
            self.key_to_note = self.expert_key_to_note
            self.file_menu.entryconfig("Autoplay", state=tk.NORMAL)
            
        self.change_instrument()

    def on_song_select(self, event=None):
        song = self.macros.get(self.song_selector.get())
        if song:
            self.tempo_label.config(text=f"Tempo: {song.get('tempo', 100)} BPM")

    def create_keys(self):
        for widget in self.piano_container.winfo_children():
            widget.destroy()
        self.key_buttons.clear()

        w_width, w_height = 50, 200
        b_width, b_height = 30, 120
        
        # FIX 1: Check both layout AND instrument correctly to restrict octaves
        is_expert = self.layout_var.get() == "Expert"
        is_piano = self.instrument_var.get() == "Piano"
        
        if is_expert and is_piano:
            octaves = [2, 3, 4, 5, 6, 7] 
        else:
            octaves = [3, 4, 5]
        
        num_white_keys = len(octaves) * 7
        if 7 in octaves:
            num_white_keys -= 6 
            
        total_px_width = num_white_keys * (w_width + 2)
        self.piano_container.config(width=total_px_width, height=w_height)

        if is_expert:
            key_maps = {
                2: { 'white': ['1', '2', '3', '4', '5', '6', '7'], 'black': ['!', '@', None, '$', '%', '^'] },
                3: { 'white': ['8', '9', '0', 'q', 'w', 'e', 'r'], 'black': ['*', '(', None, 'Q', 'W', 'E'] },
                4: { 'white': ['t', 'y', 'u', 'i', 'o', 'p', 'a'], 'black': ['T', 'Y', None, 'I', 'O', 'P'] },
                5: { 'white': ['s', 'd', 'f', 'g', 'h', 'j', 'k'], 'black': ['S', 'D', None, 'G', 'H', 'J'] },
                6: { 'white': ['l', 'z', 'x', 'c', 'v', 'b', 'n'], 'black': ['L', 'Z', None, 'C', 'V', 'B'] },
                7: { 'white': ['m'], 'black': [] }
            }
        else:
            key_maps = {
                3: { 'white': ['q', 'w', 'e', 'r', 't', 'y', 'u'], 'black': ['2', '3', None, '5', '6', '7'] },
                4: { 'white': ['i', 'o', 'p', 'z', 'x', 'c', 'v'], 'black': ['9', '0', None, 's', 'd', 'f'] },
                5: { 'white': ['b', 'n', 'm', ',', '.', '/', ']'], 'black': ['h', 'j', None, 'l', ';', "'"] }
            }

        white_notes_base = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
        black_note_offsets = [0.7, 1.7, None, 3.7, 4.7, 5.7] 
        
        total_offset_x = 0 
        for octave in octaves:
            current_map = key_maps.get(octave)
            keys_in_octave = 1 if octave == 7 else 7

            for i in range(keys_in_octave):
                note = white_notes_base[i]
                note_name = f"{note}{octave}"
                display_key = current_map['white'][i]
                abs_x = total_offset_x + (i * (w_width + 2))
                
                btn = tk.Button(self.piano_container, text=f"{note}{octave}\n({str(display_key).upper()})", font=("Arial", 8, "bold"),
                                bg='white', fg='black', anchor=tk.S, pady=10, 
                                command=lambda n=note_name: (self.play_note(n), self.visual_press(n)))
                btn.place(x=abs_x, y=0, width=w_width, height=w_height)
                self.key_buttons[note_name] = btn

            if octave != 7:
                for i in range(6):
                    if black_note_offsets[i] is None: continue
                    note_char = ['C#', 'D#', '', 'F#', 'G#', 'A#'][i]
                    note_name = f"{note_char}{octave}"
                    display_key = current_map['black'][i]
                    
                    abs_x = total_offset_x + (black_note_offsets[i] * (w_width + 2)) - (b_width / 2) + 2
                    btn = tk.Button(self.piano_container, text=f"{note_char}\n({str(display_key).upper()})", font=("Arial", 7, "bold"),
                                    bg='black', fg='white', anchor=tk.S, pady=5, 
                                    command=lambda n=note_name: (self.play_note(n), self.visual_press(n)))
                    btn.place(x=abs_x, y=0, width=b_width, height=b_height)
                    btn.lift()
                    self.key_buttons[note_name] = btn

            total_offset_x += (keys_in_octave * (w_width + 2))

    def on_key_press(self, event):
        char = event.char
        if char in self.key_to_note:
            note = self.key_to_note[char]
            self.play_note(note)
            self.visual_press(note)

    def visual_press(self, note):
        if note in self.key_buttons:
            btn = self.key_buttons[note]
            orig_bg = btn.cget("bg")
            highlight = "#00FFF2" if orig_bg == "white" else "#008B8B"
            self.root.after(0, lambda: btn.config(bg=highlight))
            self.root.after(150, lambda: btn.config(bg=orig_bg))

    def update_progress_ui(self, percent, time_str, token_start, token_end):
        self.progress_bar['value'] = percent
        self.time_label.config(text=time_str)
        
        self.macro_display.tag_remove("highlight", "1.0", tk.END)
        self.macro_display.tag_add("highlight", f"1.0+{token_start}c", f"1.0+{token_end}c")
        self.macro_display.see(f"1.0+{token_start}c")

    def run_macro_logic(self):
        song_name = self.song_selector.get()
        song_data = self.macros.get(song_name)
        macro_text = "\n".join(" " + line for line in song_data["macro"].split("\n"))
        
        total_time_sec = song_data.get("time", 155)

        tokens = list(re.finditer(r'\[.*?\]|[^ \s]', macro_text))
        total_tokens = len(tokens)
        
        base_delay = total_time_sec / total_tokens if total_tokens > 0 else 0.25

        t_m, t_s = divmod(int(total_time_sec), 60)

        for i, match in enumerate(tokens):
            if not self.macro_running: break
            while self.macro_paused:
                if not self.macro_running: break
                time.sleep(0.1)

            try:
                multiplier = float(self.speed_selector.get().replace('x', ''))
            except:
                multiplier = 1.0

            token_str = match.group(0)
            
            elapsed = (i / total_tokens) * total_time_sec
            e_m, e_s = divmod(int(elapsed), 60)
            self.root.after(0, self.update_progress_ui, (i/total_tokens)*100, f"{e_m:02d}:{e_s:02d} / {t_m:02d}:{t_s:02d}", match.start(), match.end())

            if token_str == '|':
                pass 
            elif token_str.startswith('['):
                keys = token_str[1:-1]
                for k in keys:
                    note = self.key_to_note.get(k)
                    if note: 
                        self.play_note(note)
                        self.visual_press(note)
            else:
                note = self.key_to_note.get(token_str)
                if note: 
                    self.play_note(note)
                    self.visual_press(note)
            
            time.sleep(base_delay / multiplier)
        
        self.root.after(0, self.update_progress_ui, 100, f"{t_m:02d}:{t_s:02d} / {t_m:02d}:{t_s:02d}", 0, 0)
        self.macro_display.tag_remove("highlight", "1.0", tk.END)
        self.macro_running = False

    def start_macro(self):
        if not self.macro_running:
            self.macro_running = True
            self.macro_paused = False
            
            song_name = self.song_selector.get()
            self.macro_display.config(state=tk.NORMAL)
            self.macro_display.delete("1.0", tk.END)
            macro_text = "\n".join(" " + line for line in self.macros[song_name]["macro"].split("\n"))
            self.macro_display.insert(tk.END, macro_text, "center")
            
            self.macro_display.config(state=tk.DISABLED)

            self.macro_thread = threading.Thread(target=self.run_macro_logic, daemon=True)
            self.macro_thread.start()
        else:
            self.macro_paused = False

    def pause_macro(self):
        self.macro_paused = not self.macro_paused

    def stop_macro(self):
        self.macro_running = False
        self.macro_paused = False
        self.progress_bar['value'] = 0
        self.time_label.config(text="00:00 / 00:00")
        self.macro_display.tag_remove("highlight", "1.0", tk.END)

    def update_autoplay_visibility(self):
        if self.autoplay_enabled.get():
            # Force Instrument to Piano and disable other RadioButtons
            if self.instrument_var.get() != "Piano":
                self.instrument_var.set("Piano")
                self.change_instrument()
                
            for inst, rb in self.instrument_radios.items():
                if inst != "Piano":
                    rb.config(state=tk.DISABLED)

            # Repack the Autoplay widgets
            self.macro_display.pack(before=self.piano_wrapper, pady=5)
            self.progress_frame.pack(after=self.piano_wrapper, fill=tk.X, padx=20, pady=(0, 10))
            self.macro_frame.pack(side=tk.BOTTOM, fill=tk.X)
        else:
            # Enable all instrument selections
            for rb in self.instrument_radios.values():
                rb.config(state=tk.NORMAL)

            # Hide the Autoplay widgets
            self.macro_display.pack_forget()
            self.progress_frame.pack_forget()
            self.macro_frame.pack_forget()
            self.stop_macro()

    def change_instrument(self):
        selection = self.instrument_var.get()
        global SAMPLE_BASE_URL
        SAMPLE_BASE_URL = links[selection]
        
        # FIX 1: Dynamically size window based on Layout Choice AND Instrument
        is_expert = self.layout_var.get() == "Expert"
        is_piano = selection == "Piano"
        
        if is_expert and is_piano:
            self.root.geometry("1950x780")
        else:
            self.root.geometry("1150x780")
            
        self.status_label.config(text=f"Loading {selection} interface...")
        self.root.update()

        self.sounds = self.sound_cache.get(selection, {})
        self.create_keys()
        
        self.status_label.config(text=f"{selection} Ready!")

    def play_note(self, note):
        if note in self.sounds:
            self.sounds[note].stop() 
            self.sounds[note].play()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.file_menu = tk.Menu(menubar, tearoff=0)
        
        # Adding Layout Dropdown inside File
        self.layout_menu = tk.Menu(self.file_menu, tearoff=0)
        self.layout_menu.add_radiobutton(label="Basic", variable=self.layout_var, value="Basic", command=self.change_layout)
        self.layout_menu.add_radiobutton(label="Expert", variable=self.layout_var, value="Expert", command=self.change_layout)
        self.file_menu.add_cascade(label="Layout", menu=self.layout_menu)
        
        self.file_menu.add_command(label="Volume Settings", command=self.open_settings)
        self.file_menu.add_checkbutton(label="Autoplay", variable=self.autoplay_enabled, command=self.update_autoplay_visibility)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.destroy)
        
        menubar.add_cascade(label="File", menu=self.file_menu)
        self.root.config(menu=menubar)

    def open_settings(self):
        win = tk.Toplevel(self.root)
        win.title("Volume Settings")
        win.geometry("300x120")
        win.configure(bg='#121212')
        tk.Label(win, text="Master Volume", fg='white', bg='#121212', font=("Arial", 12)).pack(pady=10)
        slider = tk.Scale(win, from_=0, to=100, orient=tk.HORIZONTAL, bg='#121212', fg='white', length=200, command=self.change_volume)
        slider.set(self.master_volume * 100)
        slider.pack()

    def change_volume(self, val):
        self.master_volume = int(val) / 100
        for inst_sounds in self.sound_cache.values():
            for sound in inst_sounds.values():
                sound.set_volume(self.master_volume)

    def set_app_icon(self):
        try:
            response = requests.get(ICON_URL, timeout=5)
            if response.status_code == 200:
                img_data = Image.open(io.BytesIO(response.content))
                self.app_icon = ImageTk.PhotoImage(img_data)
                self.root.iconphoto(False, self.app_icon)
        except: pass

def launch_app():
    main_root = tk.Tk()
    PianoApp(main_root)
    main_root.mainloop()

def launch_splash():
    splash_root = tk.Tk()
    SplashScreen(splash_root, launch_app)
    splash_root.mainloop()

if __name__ == "__main__":
    splash_root = tk.Tk()
    splash = PreLoader(splash_root, launch_splash)
    splash_root.mainloop()