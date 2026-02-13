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
        self.root.geometry("1250x700") 
        self.root.configure(bg='#121212')
        
        self.set_app_icon()
        self.master_volume = 1.0 
        self.key_buttons = {} 
        
        self.create_menu()

        self.macro_thread = None
        self.macro_running = False
        self.macro_paused = False
        
        self.key_to_note = {
            'q':'C3', 'w':'D3', 'e':'E3', 'r':'F3', 't':'G3', 'y':'A3', 'u':'B3',
            '2':'C#3', '3':'D#3', '5':'F#3', '6':'G#3', '7':'A#3',
            'i':'C4', 'o':'D4', 'p':'E4', 'z':'F4', 'x':'G4', 'c':'A4', 'v':'B4',
            '9':'C#4', '0':'D#4', 's':'F#4', 'd':'G#4', 'f':'A#4',
            'b':'C5', 'n':'D5', 'm':'E5', ',':'F5', '.':'G5', '/':'A5', ']':'B5',
            'h':'C#5', 'j':'D#5', 'l':'F#5', ';':'G#5', "'":'A#5'
        }
        
        self.macros = {
            "River Flows In You": "[YB] [P]] [CB] ] [RB] [I.] [XB] , B M [YB] [P]] [CB] ] [RB] [I.] [XB] , B M [YB] [P]] B C B ] B R B [I.] B X B , B [QN] M [E,] [PB.] M [UVN] O X B V [YB] P C X B N [RM] I X M , [Q.] T P , M [TN] O V [YB] M B [P]] B C B ] B R B [I.] B X B [R,] B [QN] M [T,] [P.] [QM] [TN] [O.] [XB] N N B ] [Y.B] P C B N [RM] [IX] [XB] M , [Q.] [TX] [PM] , M [TN] O [XB] N B ] [YB] B [P.] B [CB] N [YB] ] [RB] B [I.] B [XB] N [TB] ] [QB] N [TM] , [P.] M [QN] B [T]] [ON] [XB] N [TB] ] [YB] B [P.] B [CB] N [YB] ] [RB] B [I.] B [XB] N [RB] ] [QB] N [TM] , [P.] M [QN] B [T]] [ON] [XB] B N [TB] ] [YB] B [P.] B [CB] N [YB] ] [RB] B [I.] B [XB] N [RB] ] [QB] N [TM] , [P.] M [QN] B [T]] [RN] [UB] N [TB] ] [YB] B [P.] B [CB] N [YB] ] [RB] B [I.] B [XB] N [RB] ] [QB] N [TM] , [P.] M [QN] B [T]] [WN] [UV] X B M [YB] [P]] B C B ] B R B [I.] B X B [R,] B [QN] M [T,] [PV.] [QM] [TVN] O X B V [YXB] P X B N [RM] X [XB] N M X [XM] , [Q.] X [TM] , [P.] X [Q,] M [TN] X [O,] M [XN] V [YM] B [P]] B C B [Y]] B R B [I.] B X B [R,] B [QN] M [T,] [P.] [QM] [TN] [O.] [XN] M N [TB] ] [Y.B] P C B N [RM] X [IB] N [XM] X [RM] , [Q.] X [TM] , [P.] X [Q,] M [TN] X [OV] N [UB] N [TB] ] [Y]] B B [P.] B [YB] B N [YB] ] [RB] B [I.] B [XB] B N [RB] ] [QB] N [TM] , [P.] M [QN] B [T]] N [R.] N [UB] B N [TB] ] [Y]] B B [P.] B [YB] B N [YB] ] [RB] B [I.] B [XB] B N [RB] ] [QB] N [TM] , [P.] M [QN] B [T]] N [W.] N [UB] B N [TB] ] [YB] B [P.] B [YB] B N [YB] ] [RB] B [I.] B [XB] B N [RB] ] [QB] N [TM] , [P.] M [QN] B [T]] [WN] [UV] X [YPB] M B ] B ] [YBB] [Z.] [CB] [Y,] [TM] [P,] [B.] M [XVN] B V [YP] X B E X B N [RM] [IX] [XB] M , [Q.] [TX] [PM] , M [TN] O V B M [YB] [P]] [CB] ] [RB] . B [I.] [XB] [R,] [QN] M [T,] [P.] M [T.N] O V B V [YXB] E C B N [RM] [IX] [ZB] M , [Q.] [TX] [PB] , M [TN] W [UX] [YB] [EI] [YP] C B",
            "River Flows In You (Expert)": "[/s];[/h];[/l];[/h];[o/];[c/];[n/]m[c/]n[yh]n[ph]n[m/h]h[np]h[mp]] v m [p/];[/s] h l [/h]] [oh] c n [ch]n[my] p h [np]h[p]] v m| [/s];[/h];[/l];[/h];[o/];[c/];[n/]m[c/]n[yh]n[ph]n[m/h]h[np]m[p]] v m [p/];[/s] h l [/h]] [oh] c n [ch]n[my] p h [np]h[p]]|vmvdpue| opo9[ou5u]| opo9[otwt]| opo9[ow]ywopszxsze[y9ye]| opo9[ou5u]| opo9[otwt]| opo9[ow]ywopszxsze[y9ye]| opo9[ou]| [ou5]po9[ot]| [otw]po9[ow] op[swy]xsze[9y]| [oye]po9[ou] [u5] [ou]p[ou5]9[ot] [tw] [ot]p[otw]9[ow]p[swy]x[cw]v[hwy]n[myye]| [yny]m[yny]h[nu]5[uv]5[nu][m5][un][h5][nt]w[tc]w[nt][mw][tn][hw][nw]y[on][my][lw][.y][ol][my][hy]eye[ny][me][yn][he][nu]5[uv]5[nu][m5][un][h5][nt]w[tc]w[nt][mw][tn][hw][nw]y[on][my][lw][.y][ol][my][hy]eye[ny][ne]m[yn][he][nu]5[uv]5[nu][n5]m[un][h5][nt]w[tc]w[nt][nw]m[tn][hw][nw][my][ol][.y][/w][yl][om][yn][hy]eye[ny][ne]m[yn][he][nu]5[uv]5[nu][n5]m[un][h5][nt]w[tc]w[nt][nw]m[tn][hw][nw][my][ol][.y][/w][yl][om][yn][ly] [me] [yn] [he] [nu]h[n5]h[un]h[n5]h[nt]h[nw]h[tn]v[nw]c[cw]v[hy]n[.w]l[my]n[my] e [yn] [he] [nu]h[n5]h[un]h[n5]h[nt]h[nw]h[tn]v[nw]c[cw]v[hy]n[/w].[ly]m[ly] [me] [yn] [he] [nu]v[n5]v[un]v[n5]v[nt]v[nw]v[tn]c[nw]x[sw]x[sy]x[cw]s[xy]s[py] e y [oe]9[ou] 5 uo[p5]s[xt] w txt[cw]v[hw] [ny] [mw] [ly] [my] e [yn] [he] [nu]v[n5]v[un]v[n5]v[nt]v[nw]v[tn]c[nw]x[sw]x[sy]x[cw]s[xy]c[my] e y [ne]h[nu] 5 un[h5]n[nt] w tn[hw]n[nw] [my] [lw] [.y] [ly] e [yn]mnh [nu]5[vu]w5u[n5]w[vt]uwt[nw][tm][nw][hu][nw]5[cy]w5y[on][yh]n[hy]ey[n9][pm][cn][ph][nu]5[vu]w5u[n5]w[vt]uwt[nw][tm][nw][hu][nw]5[cy]w5y[on][yh]n[hy]ey[n9][pm][cn][ph] [nu][m5][nu][hw][v5]u[n5][mw][nt][hu][vw]t[nw][tm][nw][hu][cw][v5][hy][nw][.5][yl][om][yn][my]ey[n9][pm][cn][ph][nu][m5][nu][hw][v5]u[n5][mw][nt][hu][vw]t[nw][tm][nw][hu][cw][v5][hy][nw][/5][.y][ol][my][ly][me]y[n9]pce [nu][v5][nu][vw][n5][uv][n5][vw][nt][vu][nw][vt][nw][tc][nw][xu][sw][x5][sy][xw][c5][ys][ox][ys][py]ey9pch[nu][v5][nu][vw][n5][uv][n5][vw][nt][vu][nw][vt][nw][tc][nw][xu][sw][x5][sy][xw][c5][ys][ox][cy][cy][v][he][yn][c9][pv][ch][pn][ve][hu][ne][mu][le][;u][/e]2[]ve]| [/e]]/;[/5]9[sl]9[/5][]9][/s][9;][/w]y[om]y[/w][]y][o/][y;][/y]e[/y][]e][hy][ne][yh][]e][;e]upu[/e][u]][p/][u;][/5]9[sl]9[/5][]9][/s][9;][/w]y[om]y[/w][]y][o/][y;][/y]e[/y][]e][hy][ne][yh][]e][;e]upu[/e][u]][p/][u;] [/s]][/h];l [/h]][o/];[cl] [/n]][c/];[my]l[p;]/[nc]h[p]]/[p]] v [/m]][/v];[/s]][/h];l [/h]][o/];[cl] [/n]][c/];[my]l[p;]/[mc]n[ph]][ph] v [/m]][/v]; [/s]l[h;]/[/l]][/h];[o/]l[c;]/[/n]][c/];[/y]m[pl];[nc]h[p]]/[p]] v [/m]][/v];[/s]l[h;]/[/l]l[h;]/[o/]l[c;]/[/n]l[c;]/[/y]m[pl];[c/]m[pl];[/e]][u/]][p/] [um] v [c/ee][]v][c/][d;][c/5] [sl] [55] [c/] [slw]| [c/ww][]v][c/][d;][c/y] [pm] [yy] [c/] [d;e]| [c/ee][]v][c/][d;][c/5] [sl] [55] [c/] [slw]| [c/ww][]v][c/][d;][c/y] [pm] [yy] [c/] [d;e]| [c/ee][]v][c/][d;][c/5] [sl] [;5;5][ll] [c/][slw]| [c/ww][]v][c/][d;][c/y] [pm] [/y/y][;;] [c/][d;e]| [c/ee][]v][c/][d;][c/5] [sl] [;5;5][ll] [c/][slw]| [c/ww][]v][c/][d;][c/y] [pm] [/y/y][;;] [c/][d;e]| [c/ee][]v][c/][d;][/5] [9l] s / [lw] y [o/]]/;[/y] [pm] h / [;e] u [p/]]/;[/5]c[m9]c[/s]]/;[/w]c[my]c[o/]]/;[/y]][ph]n[mh]h]/[;e]| 6 u p d v m ; ] m ; [/s];[/h];[/l];[/h];[o/];[c/];[n/]m[c/]n[yh]n[ph]n[m/h]h[np]h[mp]] v m [p/];[/s] h l [/h]][o/]]h c n [ch]n[yh]nm p h [np]h[np]h] v m| [/s];[/h];[/l];[/h];[o/];[c/];[n/]m[c/]n[yh]n[ph]n[m/h]h[np]h[p]] v m [p/];[/s] h l [/h]][o/]hmc n [ch]n[my]/hp h [np]h[pm];] vmvdpu6e| ]/;/y][yh]/",
            "Fur Elise": "M J M J M V N B [YC] E Y I P C [EV] E 6 P D V [YB] E Y P M J M J M V N B [YC] E Y I P C [EV] E 6 O B V [YC] E Y M J M J M V N B [YC] E Y I P C [EV] E 6 P D V [YB] E Y P M J M J M V N B [YC] E Y I P C [EV] E 6 O B V [YC] E Y V B N [QM] T I X , M [TN] T U Z M N [YB] E Y P N B [EV] E P P M P M M M J M J M J M J M J M V N B [YC] E Y I P C [EV] E 6 P D V [YB] E Y P M J M J M V N B [YC] E Y I P C [EV] E 6 O B V [YC]",
            "Nocturne Op. 9 No. 2": "B [R/] [YZ] [IZC] R [7P.] [9F/] [R.] [YZ] [IZC] [E,] [YZ] [IZCB] [O/] [YS] [SICB] NMN [ON] [YS] [SI/] [TB] [T0] [IPS] [T'] [TO] [7OX/] [I.] [TP] [PF] [9/] [YX] [PXCM] [O,] [YZ] [OZC] [UN] [6Z] [OZD] [IB] [TZM] [FIZN] [IB] ' [TP/] ' [IFN] M [R,] [YZ] [IZC] R [YZ] [IZCB] [R/] [YZ] [IZC] [R.] / [7P.] / . L [9FP.] / [R.] [YZ,] [IZC] [E,] . [YZ,] . , M [IZC,] . [O/] H [YSO] J [SICNO] . [OSL] ' [YS/] M [OSIN] / [TB] [T0] [I0S] [T'] [TO] [7OX/][I.]./././.[TP]./././.[IPF]././[9L/][.'][/]['][YXC/][PXCM][O,] [YZ] [OZC] [UN] [6Z] [OZD] [IB] [TZM] [FIZN] [IB] ' [TP/] ' [IFN]MN [R,] [YZ] [IZC] [R,] [YZM] [IZC,] [I.] [TP] [IPX] [I/] [TP] [IPX.] [U.] [TO] [OX] [UN] [TO] [OX] [7,] [RO,] [O7,] [7,] [9RM] , [79ZG,] , [R,] [YZ] [IZC] [IB] [YZ] [IZC] [5B] [50] [0IC] [5U] [5O] [IO/] [TV.] [TZ] [OZV] [YMB] [YP] [IPC] [OC,] [YZ] [OZC] [TVM] [TZVN] [OZVXM] [IPCB] [UZDH] [7SH] [YSNB] [TOZVNB] [FICM] [RC] B , [Y/] [IZCV] B [RH] B [P7J] M [IP/.] . [R.] [YZ] [IZC,] E . [YZ,] , M [IZC,] . [O/] H [YSO] J [SICNO] . [OSL] ' [YS/] J [OSIN] / [TB] [T0] [I0S] [T'] [TO] [7OX/][I.]./././.[TP]./././.[IPF]././[9L/][.'][/]['] [YXC/] [PXCM] [O,] [YZ] [OZC] [UN] [6Z] [OZD] [IB] [TZM] [IFJN] [IN]H B U [IFM] . P H [IFMB] M / . , [R,] [YZ] [IZC] [R,] [YZM] [IZC,] [I.] [TP] [IPX] [I/] [TP] [IPX.] [U.] [TO] [OX] [UN] [TO] [OX] [7,] , [RO] , [7O,] , [7,] [9RM] , [79ZG,] , [R,] [YZ] [IZC] [IB] [YZ] [IZC] [5B] [50] [0IC] [5U] [5O] [IO/] [TV.] [TZ] [OZV] [YMB] [YP] [IPC] [OC,] [YZ] [OZC] [TVM] [TZVN] [OZVXM] [IPCB] [UZDH] [7SH] [YSNB] [TOZVNB] [FICM] [RC] B , [Y/] [IZCV] B [RH] B [P7J] M [IP/.] . [R.] [YZ] [IZC,] [E,] . [YZ,] M [IZC,] . [O/] H [YSO] J [SICNO] . [OSL] ' [YS/] J [OSIN] / [TY/] B [T0] [I0S] [T'] [TO] [7OX/][I.]./././.[TP]./././.[IPF]././[9L/][.'][/]['] [YXC/] [PXCM] [O,] [YZ] [OZC] [UN] [6Z] [OZD] [IB] M [TZ] J [IZFN] H [IB] U [IFM] I90O[IFJ]M/., [R,] [YZ] [IZC] R [YZ] [IZC] [R,] [79Z] [Z97] [R.] [79Z,] [97Z.] [R/] [YZ] [IZC] R [YZ] [IZC] [R,] [79Z] [Z97] R . [79Z,] . [97Z,] . [R/] [YZI] [IZCM] , . , [RM] [YZM] [IZCN] [RB] [TP] [FICU] [R'] [TPN] [IFM] [R,] [TP.] , . , [IFM] , [U,] / [TZM] , [OZX] , [IBH] [TZB] [IZF'] [HBN]HBN]HBN]HBN]HBN]HBN]HBN]HBN]HBN]HBN]HBN]HBN]HBN]HBN]HBN]HBN]MBN]HBN]HBN]HBN]M/., [RZC] [IB] [I/] [RZC] [IB] [I/] [RZC] [IB] [I/] [RZC] [IB] [I/] [RZC] [ZC/] [RYIZ]"
        }
        tk.Label(self.root, text="KORN-ON! PIANO", font=("Helvetica", 30, "bold"), 
                 bg='#121212', fg='#00ADB5').pack(pady=(20, 10))

        self.control_frame = tk.Frame(self.root, bg='#121212')
        self.control_frame.pack(pady=5)

        self.instrument_var = tk.StringVar(value="Piano")
        rb_style = {'bg': '#121212', 'fg': 'white', 'selectcolor': '#333333', 
                    'activebackground': '#121212', 'activeforeground': '#00ADB5', 'font': ("Arial", 12)}

        for inst in ["Piano", "Guitar", "Poon", "Meowsynth", "Plastic", "Organ"]:
            tk.Radiobutton(self.control_frame, text=inst, variable=self.instrument_var, value=inst, command=self.change_instrument, **rb_style).pack(side=tk.LEFT, padx=10)

        self.status_label = tk.Label(self.root, text="", bg='#121212', fg='#888', font=("Arial", 10))
        self.status_label.pack()

        self.sounds = {}
        self.load_samples()
        
        self.piano_container = tk.Frame(self.root, bg='#121212', height=250)
        self.piano_container.pack(pady=10, fill=tk.X, expand=True)
        self.create_keys()

        # --- Macro Control Bar ---
        self.macro_frame = tk.Frame(self.root, bg='#1c1c1c', pady=10)
        self.macro_frame.pack(side=tk.BOTTOM, fill=tk.X)

        tk.Label(self.macro_frame, text="AUTOPLAY:", fg='#00ADB5', bg='#1c1c1c', font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(20, 10))
        
        self.song_selector = ttk.Combobox(self.macro_frame, values=list(self.macros.keys()), state="readonly", width=25)
        self.song_selector.current(0)
        self.song_selector.pack(side=tk.LEFT, padx=10)

        btn_style = {'font': ("Arial", 12), 'width': 4, 'bg': '#333', 'fg': 'white', 'activebackground': '#444'}
        
        self.play_btn = tk.Button(self.macro_frame, text="▶", command=self.start_macro, **btn_style)
        self.play_btn.pack(side=tk.LEFT, padx=5)

        self.pause_btn = tk.Button(self.macro_frame, text="⏸", command=self.pause_macro, **btn_style)
        self.pause_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = tk.Button(self.macro_frame, text="■", command=self.stop_macro, **btn_style)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        # --- Speed Chooser Section ---
        tk.Label(self.macro_frame, text="SPEED:", fg='#00ADB5', bg='#1c1c1c', font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(20, 5))
        self.speed_selector = ttk.Combobox(self.macro_frame, values=["0.25x", "0.5x", "0.75x", "1.0x", "1.25x", "1.5x", "2.0x"], state="readonly", width=7)
        self.speed_selector.set("1.0x")
        self.speed_selector.pack(side=tk.LEFT, padx=5)

    def visual_press(self, note):
        if note in self.key_buttons:
            btn = self.key_buttons[note]
            orig_bg = btn.cget("bg")
            highlight = "#00FFF2" if orig_bg == "white" else "#008B8B"
            self.root.after(0, lambda: btn.config(bg=highlight))
            self.root.after(150, lambda: btn.config(bg=orig_bg))

    def start_macro(self):
        if not self.macro_running:
            self.macro_running = True
            self.macro_paused = False
            self.macro_thread = threading.Thread(target=self.run_macro_logic, daemon=True)
            self.macro_thread.start()
        else:
            self.macro_paused = False 

    def pause_macro(self):
        self.macro_paused = not self.macro_paused

    def stop_macro(self):
        self.macro_running = False
        self.macro_paused = False

    def run_macro_logic(self):
        song_name = self.song_selector.get()
        macro_text = self.macros.get(song_name, "")
        tokens = re.findall(r'\[.*?\]|[^ \s]', macro_text)
        base_delay = 0.25

        for token in tokens:
            if not self.macro_running: break
            while self.macro_paused:
                if not self.macro_running: break
                time.sleep(0.1)

            # Get dynamic speed multiplier
            try:
                speed_val = self.speed_selector.get().replace('x', '')
                multiplier = float(speed_val)
            except:
                multiplier = 1.0

            if token.startswith('['):
                keys = token[1:-1]
                for k in keys:
                    note = self.key_to_note.get(k.lower())
                    if note: 
                        self.play_note(note)
                        self.visual_press(note)
            else:
                note = self.key_to_note.get(token.lower())
                if note: 
                    self.play_note(note)
                    self.visual_press(note)
            
            time.sleep(base_delay / multiplier)
        
        self.macro_running = False

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
        slider = tk.Scale(win, from_=0, to=100, orient=tk.HORIZONTAL, bg='#121212', fg='white', length=200, command=self.change_volume)
        slider.set(self.master_volume * 100)
        slider.pack()

    def change_volume(self, val):
        self.master_volume = int(val) / 100
        for sound in self.sounds.values():
            sound.set_volume(self.master_volume)

    def set_app_icon(self):
        try:
            response = requests.get(ICON_URL, timeout=5)
            if response.status_code == 200:
                img_data = Image.open(io.BytesIO(response.content))
                self.app_icon = ImageTk.PhotoImage(img_data)
                self.root.iconphoto(False, self.app_icon)
        except: pass

    def change_instrument(self):
        selection = self.instrument_var.get()
        global SAMPLE_BASE_URL
        SAMPLE_BASE_URL = links[selection]
        self.status_label.config(text=f"Loading {selection} sounds...")
        self.root.update()
        self.sounds.clear()
        self.load_samples()
        self.status_label.config(text=f"{selection} Ready!")

    def load_samples(self):
        current_instrument = self.instrument_var.get()
        base_folder = f"samples/{current_instrument}"
        if not os.path.exists(base_folder): os.makedirs(base_folder)
        for note_name, file_name in NOTES_MAPPING.items():
            sample_path = f"{base_folder}/{file_name}.mp3"
            if not os.path.exists(sample_path):
                try:
                    url = f"{links[current_instrument]}{file_name}.mp3"
                    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
                    if r.status_code == 200:
                        with open(sample_path, 'wb') as f: f.write(r.content)
                except: pass
            if os.path.exists(sample_path):
                try:
                    s = pygame.mixer.Sound(sample_path)
                    s.set_volume(self.master_volume) 
                    self.sounds[note_name] = s
                except: pass

    def create_keys(self):
        w_width, w_height = 50, 200
        b_width, b_height = 30, 120
        white_notes_base = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
        black_notes_data = [('C#', 0.7), ('D#', 1.7), ('F#', 3.7), ('G#', 4.7), ('A#', 5.7)]
        key_maps = {
            3: { 'white': ['q', 'w', 'e', 'r', 't', 'y', 'u'], 'black': ['2', '3', '5', '6', '7'] },
            4: { 'white': ['i', 'o', 'p', 'z', 'x', 'c', 'v'], 'black': ['9', '0', 's', 'd', 'f'] },
            5: { 'white': ['b', 'n', 'm', ',', '.', '/', ']'], 'black': ['h', 'j', 'l', ';', "'"] }
        }
        total_offset_x = 50 
        for octave in [3, 4, 5]:
            current_map = key_maps.get(octave)
            for i, note in enumerate(white_notes_base):
                note_name = f"{note}{octave}"
                display_key = current_map['white'][i].upper()
                self.root.bind(display_key.lower(), lambda e, n=note_name: (self.play_note(n), self.visual_press(n)))
                abs_x = total_offset_x + (i * (w_width + 2))
                btn = tk.Button(self.piano_container, text=f"{note}{octave}\n({display_key})", font=("Arial", 8, "bold"),
                                 bg='white', fg='black', anchor=tk.S, pady=10, command=lambda n=note_name: (self.play_note(n), self.visual_press(n)))
                btn.place(x=abs_x, y=0, width=w_width, height=w_height)
                self.key_buttons[note_name] = btn

            for note_char, pos_mult in black_notes_data:
                note_name = f"{note_char}{octave}"
                idx = {'C#':0, 'D#':1, 'F#':2, 'G#':3, 'A#':4}[note_char]
                display_key = current_map['black'][idx].upper()
                self.root.bind(display_key.lower(), lambda e, n=note_name: (self.play_note(n), self.visual_press(n)))
                abs_x = total_offset_x + (pos_mult * (w_width + 2)) - (b_width / 2) + 2
                btn = tk.Button(self.piano_container, text=f"{note_char}\n({display_key})", font=("Arial", 7, "bold"),
                                bg='black', fg='white', anchor=tk.S, pady=5, command=lambda n=note_name: (self.play_note(n), self.visual_press(n)))
                btn.place(x=abs_x, y=0, width=b_width, height=b_height)
                btn.lift()
                self.key_buttons[note_name] = btn

            total_offset_x += (7 * (w_width + 2))

    def play_note(self, note):
        if note in self.sounds:
            self.sounds[note].stop() 
            self.sounds[note].play()

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