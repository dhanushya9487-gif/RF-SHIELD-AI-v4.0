import tkinter as tk
import math
import serial
import serial.tools.list_ports
import threading
import time
from datetime import datetime

# =========================================================
# OPTIONAL SOUND
# =========================================================
try:
    import pygame
    pygame.mixer.init()
    SOUND_AVAILABLE = True
except Exception:
    SOUND_AVAILABLE = False

# =========================================================
# SETTINGS
# =========================================================
BAUD = 9600
PORT = "COM5"

SAFE_MAX = 60
SUSPICIOUS_MAX = 120

GRAPH_POINTS = 40

# =========================================================
# RF SHIELD AI
# =========================================================
class RF_SHIELD_FINAL:

    def __init__(self, root):

        self.root = root
        self.root.title("RF SHIELD AI v4.0 - REAL TIME RF MONITOR")
        self.root.geometry("1180x820")
        self.root.configure(bg="#0a0e14")

        # -------------------------------------------------
        # DATA
        # -------------------------------------------------
        self.real_rf_value = 0
        self.serial_connected = False

        self.history = []
        self.angle = 0
        self.blink_state = False
        self.last_beep = 0

        # =================================================
        # HEADER
        # =================================================
        header = tk.Frame(
            root,
            bg="#10151f",
            height=70
        )
        header.pack(fill="x")

        tk.Label(
            header,
            text="RF SHIELD AI v4.0",
            fg="#00ff9d",
            bg="#10151f",
            font=("Consolas", 22, "bold")
        ).place(x=20, y=10)

        tk.Label(
            header,
            text="REAL LCD + LIVE GRAPH + RADAR + LED + SOUND + AI SIGNAL ANALYSIS",
            fg="#5a6a7a",
            bg="#10151f",
            font=("Consolas", 9)
        ).place(x=22, y=45)

        self.conn_label = tk.Label(
            header,
            text="CONNECTING...",
            fg="#ffcc00",
            bg="#10151f",
            font=("Consolas", 10, "bold")
        )
        self.conn_label.place(x=820, y=25)

        # =================================================
        # MAIN
        # =================================================
        main = tk.Frame(
            root,
            bg="#0a0e14"
        )
        main.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        # =================================================
        # LEFT SIDE
        # =================================================
        left = tk.Frame(
            main,
            bg="#111821",
            highlightbackground="#1e2a3a",
            highlightthickness=1
        )

        left.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 10)
        )

        tk.Label(
            left,
            text="RF ACTIVITY MONITOR + LIVE ALERTS",
            fg="white",
            bg="#111821",
            font=("Consolas", 12, "bold")
        ).pack(pady=10)

        # -------------------------------------------------
        # RADAR
        # -------------------------------------------------
        self.canvas = tk.Canvas(
            left,
            width=400,
            height=400,
            bg="#0d121b",
            highlightthickness=0
        )
        self.canvas.pack()

        # =================================================
        # VIRTUAL LED + SOUND
        # =================================================
        v_hard = tk.Frame(
            left,
            bg="#0a0e14",
            highlightbackground="#00ff9d",
            highlightthickness=1
        )

        v_hard.pack(
            fill="x",
            padx=10,
            pady=10,
            ipady=10
        )

        tk.Label(
            v_hard,
            text="VIRTUAL ALERT SYSTEM [LED + SOUND]",
            fg="#00ff9d",
            bg="#0a0e14",
            font=("Consolas", 11, "bold")
        ).pack(
            anchor="w",
            padx=10
        )

        led_frame = tk.Frame(
            v_hard,
            bg="#0a0e14"
        )

        led_frame.pack(
            fill="x",
            padx=10,
            pady=8
        )

        self.led_canvas = tk.Canvas(
            led_frame,
            width=350,
            height=55,
            bg="#0a0e14",
            highlightthickness=0
        )

        self.led_canvas.pack(side="left")

        # GREEN LED
        self.led_green = self.led_canvas.create_oval(
            10, 5, 45, 40,
            fill="#0f2810",
            outline="#00ff9d",
            width=2
        )

        self.led_canvas.create_text(
            27, 50,
            text="SAFE",
            fill="white",
            font=("Consolas", 8, "bold")
        )

        # YELLOW LED
        self.led_yellow = self.led_canvas.create_oval(
            70, 5, 105, 40,
            fill="#28220f",
            outline="#ffcc00",
            width=2
        )

        self.led_canvas.create_text(
            87, 50,
            text="SUSPICIOUS",
            fill="white",
            font=("Consolas", 7, "bold")
        )

        # RED LED
        self.led_red = self.led_canvas.create_oval(
            130, 5, 165, 40,
            fill="#281010",
            outline="#ff3b3b",
            width=2
        )

        self.led_canvas.create_text(
            147, 50,
            text="ALERT",
            fill="white",
            font=("Consolas", 8, "bold")
        )

        # -------------------------------------------------
        # SOUND STATUS
        # -------------------------------------------------
        self.buzzer_frame = tk.Frame(
            led_frame,
            bg="#0a0e14"
        )

        self.buzzer_frame.pack(
            side="left",
            padx=20
        )

        self.buzzer_lbl = tk.Label(
            self.buzzer_frame,
            text="SYSTEM SAFE",
            fg="#00ff9d",
            bg="#0a0e14",
            font=("Consolas", 12, "bold")
        )

        self.buzzer_lbl.pack()

        self.sound_lbl = tk.Label(
            self.buzzer_frame,
            text="Sound: OFF",
            fg="#5a6a7a",
            bg="#0a0e14",
            font=("Consolas", 8)
        )

        self.sound_lbl.pack()

        # =================================================
        # EVENT LOG
        # =================================================
        tk.Label(
            left,
            text="EVENT LOG",
            fg="#7a8a9a",
            bg="#111821",
            font=("Consolas", 8, "bold")
        ).pack(
            anchor="w",
            padx=10
        )

        self.log_box = tk.Listbox(
            left,
            bg="#0d121b",
            fg="#00ff9d",
            font=("Consolas", 8),
            height=7,
            bd=0
        )

        self.log_box.pack(
            fill="x",
            padx=10,
            pady=5
        )

        # =================================================
        # RIGHT SIDE
        # =================================================
        right = tk.Frame(
            main,
            bg="#0a0e14"
        )

        right.pack(
            side="right",
            fill="both",
            expand=True
        )

        # =================================================
        # STATUS CARD
        # =================================================
        self.status_card = tk.Frame(
            right,
            bg="#111821",
            highlightbackground="#1e2a3a",
            highlightthickness=1,
            height=150
        )

        self.status_card.pack(
            fill="x",
            pady=(0, 10)
        )

        self.status_card.pack_propagate(False)

        tk.Label(
            self.status_card,
            text="THREAT STATUS [3 MODES]",
            fg="#7a8a9a",
            bg="#111821",
            font=("Consolas", 10)
        ).pack(
            anchor="w",
            padx=20,
            pady=(10, 0)
        )

        self.status_label = tk.Label(
            self.status_card,
            text="WAITING",
            fg="#5a6a7a",
            bg="#111821",
            font=("Consolas", 24, "bold")
        )

        self.status_label.pack(pady=5)

        self.sub_label = tk.Label(
            self.status_card,
            text="Connecting...",
            fg="#7a8a9a",
            bg="#111821",
            font=("Consolas", 9)
        )

        self.sub_label.pack()

        # =================================================
        # STAT BOXES
        # =================================================
        grid = tk.Frame(
            right,
            bg="#0a0e14"
        )

        grid.pack(
            fill="x",
            pady=5
        )

        def make_stat(title, value):

            f = tk.Frame(
                grid,
                bg="#111821",
                highlightbackground="#1e2a3a",
                highlightthickness=1,
                width=170,
                height=80
            )

            f.pack(
                side="left",
                padx=5,
                expand=True,
                fill="both"
            )

            f.pack_propagate(False)

            tk.Label(
                f,
                text=title,
                fg="#7a8a9a",
                bg="#111821",
                font=("Consolas", 9)
            ).pack(pady=(10, 5))

            lbl = tk.Label(
                f,
                text=value,
                fg="white",
                bg="#111821",
                font=("Consolas", 16, "bold")
            )

            lbl.pack()

            return lbl

        self.rf_lbl = make_stat(
            "RF SIGNAL",
            "--"
        )

        self.freq_lbl = make_stat(
            "FREQUENCY",
            "2.4 GHz"
        )

        self.threat_lbl = make_stat(
            "THREAT LEVEL",
            "--"
        )

        # =================================================
        # SIGNAL BAR
        # =================================================
        bar_frame = tk.Frame(
            right,
            bg="#111821",
            highlightbackground="#1e2a3a",
            highlightthickness=1
        )

        bar_frame.pack(
            fill="x",
            pady=8,
            ipady=5
        )

        tk.Label(
            bar_frame,
            text="SIGNAL STRENGTH (A0 0-1023) - LIVE",
            fg="#7a8a9a",
            bg="#111821",
            font=("Consolas", 10)
        ).pack(
            anchor="w",
            padx=15
        )

        self.bar_canvas = tk.Canvas(
            bar_frame,
            height=18,
            bg="#0d121b",
            highlightthickness=0
        )

        self.bar_canvas.pack(
            fill="x",
            padx=15,
            pady=8
        )

        # =================================================
        # NEW LIVE GRAPH
        # =================================================
        graph_frame = tk.Frame(
            right,
            bg="#111821",
            highlightbackground="#00ff9d",
            highlightthickness=1
        )

        graph_frame.pack(
            fill="x",
            pady=6
        )

        tk.Label(
            graph_frame,
            text="LIVE RF SIGNAL GRAPH",
            fg="#00ff9d",
            bg="#111821",
            font=("Consolas", 10, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=(6, 2)
        )

        self.graph_canvas = tk.Canvas(
            graph_frame,
            height=145,
            bg="#0d121b",
            highlightthickness=0
        )

        self.graph_canvas.pack(
            fill="x",
            padx=15,
            pady=(2, 8)
        )

        # =================================================
        # SIGNAL PATTERN ANALYSIS
        # =================================================
        analysis_frame = tk.Frame(
            right,
            bg="#111821",
            highlightbackground="#00ff9d",
            highlightthickness=1
        )

        analysis_frame.pack(
            fill="x",
            pady=8,
            ipady=5
        )

        tk.Label(
            analysis_frame,
            text="RF SIGNAL PATTERN ANALYSIS",
            fg="#00ff9d",
            bg="#111821",
            font=("Consolas", 10, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=(8, 2)
        )

        self.pattern_lbl = tk.Label(
            analysis_frame,
            text="Signal Pattern : --",
            fg="#c0c0c0",
            bg="#111821",
            font=("Consolas", 9)
        )

        self.pattern_lbl.pack(
            anchor="w",
            padx=15
        )

        self.var_lbl = tk.Label(
            analysis_frame,
            text="Signal Variation : -- | Activity : --",
            fg="#c0c0c0",
            bg="#111821",
            font=("Consolas", 9)
        )

        self.var_lbl.pack(
            anchor="w",
            padx=15
        )

        self.anomaly_lbl = tk.Label(
            analysis_frame,
            text="Anomaly Score : --% | Threat : --",
            fg="white",
            bg="#111821",
            font=("Consolas", 11, "bold")
        )

        self.anomaly_lbl.pack(
            anchor="w",
            padx=15,
            pady=2
        )

        self.final_lbl = tk.Label(
            analysis_frame,
            text="FINAL STATUS : WAITING",
            fg="#ffcc00",
            bg="#111821",
            font=("Consolas", 10, "bold")
        )

        self.final_lbl.pack(
            anchor="w",
            padx=15,
            pady=(2, 8)
        )

        # =================================================
        # AI ENGINE
        # =================================================
        ai_frame = tk.Frame(
            right,
            bg="#0d121b",
            highlightbackground="#1e2a3a",
            highlightthickness=1
        )

        ai_frame.pack(
            fill="x",
            pady=5,
            ipady=5
        )

        tk.Label(
            ai_frame,
            text="AI SIGNAL ANALYSIS ENGINE",
            fg="#7a8a9a",
            bg="#0d121b",
            font=("Consolas", 9, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=(5, 2)
        )

        tk.Label(
            ai_frame,
            text="Strength + Variation + Temporal Pattern + Noise Filtering + Anomaly Score",
            fg="#5a6a7a",
            bg="#0d121b",
            font=("Consolas", 7)
        ).pack(
            anchor="w",
            padx=15
        )

        self.ai_decision_lbl = tk.Label(
            ai_frame,
            text="AI DECISION -> WAITING FOR DATA",
            fg="#00ff9d",
            bg="#0d121b",
            font=("Consolas", 10, "bold")
        )

        self.ai_decision_lbl.pack(
            anchor="w",
            padx=15,
            pady=5
        )

        # =================================================
        # START
        # =================================================
        self.signal = 0

        self.start_serial_thread()

        self.update_system()

    # =====================================================
    # FIND ARDUINO
    # =====================================================
    def find_arduino_port(self):

        ports = list(
            serial.tools.list_ports.comports()
        )

        for p in ports:

            description = str(p.description)

            if (
                "Arduino" in description
                or "CH340" in description
                or "USB" in description
            ):
                return p.device

        return PORT

    # =====================================================
    # SERIAL READING
    # =====================================================
    def start_serial_thread(self):

        def read_serial():

            try:

                auto_port = self.find_arduino_port()

                ser = serial.Serial(
                    auto_port,
                    BAUD,
                    timeout=1
                )

                time.sleep(2)

                self.serial_connected = True

                # UI update through main thread
                self.root.after(
                    0,
                    lambda: self.conn_label.config(
                        text=f"CONNECTED {auto_port} | SOUND ON",
                        fg="#00ff9d"
                    )
                )

                buf = []

                while True:

                    if ser.in_waiting:

                        line = (
                            ser.readline()
                            .decode(
                                errors="ignore"
                            )
                            .strip()
                        )

                        if line.isdigit():

                            value = int(line)

                            # Limit invalid values
                            value = max(
                                0,
                                min(
                                    1023,
                                    value
                                )
                            )

                            buf.append(value)

                            if len(buf) > 3:
                                buf.pop(0)

                            self.real_rf_value = (
                                sum(buf) // len(buf)
                            )

            except Exception as e:

                self.serial_connected = False

                err_msg = str(e)[:35]

                self.root.after(
                    0,
                    lambda msg=err_msg: self.conn_label.config(
                        text=f"COM ERROR: {msg}",
                        fg="#ff3b3b"
                    )
                )

        threading.Thread(
            target=read_serial,
            daemon=True
        ).start()

    # =====================================================
    # RADAR
    # =====================================================
    def draw_radar(self):

        self.canvas.delete("all")

        cx = 200
        cy = 200

        # Radar circles
        for r in [60, 120, 180]:

            self.canvas.create_oval(
                cx-r,
                cy-r,
                cx+r,
                cy+r,
                outline="#1e2a3a"
            )

        # Radar lines
        for a in range(
            0,
            360,
            45
        ):

            x = (
                cx
                + 180
                * math.cos(
                    math.radians(a)
                )
            )

            y = (
                cy
                + 180
                * math.sin(
                    math.radians(a)
                )
            )

            self.canvas.create_line(
                cx,
                cy,
                x,
                y,
                fill="#1e2a3a"
            )

        # Sweep
        self.angle = (
            self.angle + 4
        ) % 360

        ex = (
            cx
            + 180
            * math.cos(
                math.radians(
                    self.angle
                )
            )
        )

        ey = (
            cy
            + 180
            * math.sin(
                math.radians(
                    self.angle
                )
            )
        )

        self.canvas.create_line(
            cx,
            cy,
            ex,
            ey,
            fill="#00ff9d",
            width=2
        )

        # Detection point
        if self.signal > SAFE_MAX:

            distance = min(
                170,
                max(
                    30,
                    self.signal * 1.2
                )
            )

            bx = (
                cx
                + distance
                * math.cos(
                    math.radians(
                        self.angle
                    )
                )
            )

            by = (
                cy
                + distance
                * math.sin(
                    math.radians(
                        self.angle
                    )
                )
            )

            point_color = (
                "#ff3b3b"
                if self.signal > SUSPICIOUS_MAX
                else "#ffcc00"
            )

            self.canvas.create_oval(
                bx-7,
                by-7,
                bx+7,
                by+7,
                fill=point_color,
                outline=""
            )

    # =====================================================
    # AI BRAIN
    # =====================================================
    def ai_brain(self, history):

        if len(history) < 5:

            return (
                0,
                0,
                "NORMAL"
            )

        avg = (
            sum(history)
            / len(history)
        )

        variance = (
            sum(
                (x - avg) ** 2
                for x in history
            )
            / len(history)
        )

        # Pattern classification
        if variance > 400:

            pattern = "ANOMALOUS"

        elif variance > 120:

            pattern = "SUSPICIOUS"

        else:

            pattern = "NORMAL"

        return (
            avg,
            variance,
            pattern
        )

    # =====================================================
    # LIVE GRAPH
    # =====================================================
    def draw_signal_graph(self):

        self.graph_canvas.delete("all")

        width = self.graph_canvas.winfo_width()

        if width < 100:
            width = 450

        height = 145

        # -------------------------------------------------
        # GRID
        # -------------------------------------------------
        for value in [
            0,
            256,
            512,
            768,
            1023
        ]:

            y = (
                height
                - (
                    value
                    / 1023
                )
                * height
            )

            self.graph_canvas.create_line(
                35,
                y,
                width,
                y,
                fill="#1e2a3a"
            )

            self.graph_canvas.create_text(
                18,
                y,
                text=str(value),
                fill="#5a6a7a",
                font=("Consolas", 7)
            )

        # -------------------------------------------------
        # SAFE LINE
        # -------------------------------------------------
        safe_y = (
            height
            - (
                SAFE_MAX
                / 1023
            )
            * height
        )

        self.graph_canvas.create_line(
            35,
            safe_y,
            width,
            safe_y,
            fill="#244c39",
            dash=(4, 4)
        )

        # -------------------------------------------------
        # SUSPICIOUS LINE
        # -------------------------------------------------
        suspicious_y = (
            height
            - (
                SUSPICIOUS_MAX
                / 1023
            )
            * height
        )

        self.graph_canvas.create_line(
            35,
            suspicious_y,
            width,
            suspicious_y,
            fill="#594c1c",
            dash=(4, 4)
        )

        # -------------------------------------------------
        # NO DATA
        # -------------------------------------------------
        if len(self.history) < 2:
            return

        # -------------------------------------------------
        # GRAPH POINTS
        # -------------------------------------------------
        left = 38
        right = width - 5

        usable_width = (
            right - left
        )

        points = []

        for i, value in enumerate(
            self.history
        ):

            x = (
                left
                + i
                * usable_width
                / (
                    len(self.history) - 1
                )
            )

            y = (
                height
                - (
                    value
                    / 1023
                )
                * height
            )

            points.extend(
                [x, y]
            )

        # -------------------------------------------------
        # GRAPH COLOR
        # -------------------------------------------------
        if self.signal > SUSPICIOUS_MAX:

            graph_color = "#ff3b3b"

        elif self.signal > SAFE_MAX:

            graph_color = "#ffcc00"

        else:

            graph_color = "#00ff9d"

        # -------------------------------------------------
        # DRAW GRAPH
        # -------------------------------------------------
        self.graph_canvas.create_line(
            *points,
            fill=graph_color,
            width=3,
            smooth=True
        )

        # -------------------------------------------------
        # CURRENT POINT
        # -------------------------------------------------
        x = points[-2]
        y = points[-1]

        self.graph_canvas.create_oval(
            x-5,
            y-5,
            x+5,
            y+5,
            fill=graph_color,
            outline=""
        )

        # -------------------------------------------------
        # CURRENT VALUE
        # -------------------------------------------------
        self.graph_canvas.create_text(
            width - 60,
            12,
            text=f"NOW: {self.signal}",
            fill=graph_color,
            font=("Consolas", 8, "bold")
        )

    # =====================================================
    # SOUND - OLD PYGAME MODEL SAME
    # =====================================================
    def play_alert_sound(self, mode):

        if not SOUND_AVAILABLE:
            return

        if (
            time.time()
            - self.last_beep
            < 1.0
        ):
            return

        self.last_beep = time.time()

        def sound_thread():

            try:

                sound_file = (
                    "C:\\Windows\\Media\\chimes.wav"
                )

                if mode == "ALERT":

                    for _ in range(2):

                        pygame.mixer.music.load(
                            sound_file
                        )

                        pygame.mixer.music.play()

                        time.sleep(0.6)

                elif mode == "SUSPICIOUS":

                    pygame.mixer.music.load(
                        sound_file
                    )

                    pygame.mixer.music.play()

            except Exception:
                pass

        threading.Thread(
            target=sound_thread,
            daemon=True
        ).start()

    # =====================================================
    # LED + SOUND STATUS
    # =====================================================
    def update_virtual_led_sound(
        self,
        mode
    ):

        # Reset LEDs
        self.led_canvas.itemconfig(
            self.led_green,
            fill="#0f2810"
        )

        self.led_canvas.itemconfig(
            self.led_yellow,
            fill="#28220f"
        )

        self.led_canvas.itemconfig(
            self.led_red,
            fill="#281010"
        )

        self.buzzer_lbl.config(
            text="SYSTEM SAFE",
            fg="#00ff9d"
        )

        self.sound_lbl.config(
            text="Sound: OFF",
            fg="#5a6a7a"
        )

        # -------------------------------------------------
        # SAFE
        # -------------------------------------------------
        if mode == "SAFE":

            self.led_canvas.itemconfig(
                self.led_green,
                fill="#00ff00"
            )

            self.buzzer_lbl.config(
                text="SYSTEM SAFE",
                fg="#00ff9d"
            )

        # -------------------------------------------------
        # SUSPICIOUS
        # -------------------------------------------------
        elif mode == "SUSPICIOUS":

            color = (
                "#ffff00"
                if self.blink_state
                else "#28220f"
            )

            self.led_canvas.itemconfig(
                self.led_yellow,
                fill=color
            )

            self.buzzer_lbl.config(
                text="WARNING BEEP",
                fg="#ffcc00"
            )

            self.sound_lbl.config(
                text="Sound: WARNING",
                fg="#ffcc00"
            )

            self.play_alert_sound(
                "SUSPICIOUS"
            )

        # -------------------------------------------------
        # ALERT
        # -------------------------------------------------
        elif mode == "ALERT":

            color = (
                "#ff0000"
                if self.blink_state
                else "#281010"
            )

            self.led_canvas.itemconfig(
                self.led_red,
                fill=color
            )

            self.buzzer_lbl.config(
                text="ALERT SOUND!",
                fg="#ff3b3b"
            )

            self.sound_lbl.config(
                text="Sound: ALERT!!!",
                fg="#ff3b3b"
            )

            self.play_alert_sound(
                "ALERT"
            )

    # =====================================================
    # EVENT LOG
    # =====================================================
    def add_log(self, text):

        self.log_box.insert(
            0,
            text
        )

        # Keep only latest 8 logs
        if self.log_box.size() > 8:

            self.log_box.delete(
                8,
                tk.END
            )

    # =====================================================
    # MAIN UPDATE
    # =====================================================
    def update_system(self):

        # Radar
        self.draw_radar()

        # Blink
        self.blink_state = (
            not self.blink_state
        )

        # =================================================
        # NO SERIAL DATA
        # =================================================
        if not self.serial_connected:

            self.rf_lbl.config(
                text="--"
            )

            self.threat_lbl.config(
                text="--"
            )

            self.status_label.config(
                text="NO DATA",
                fg="#ff3b3b",
                font=(
                    "Consolas",
                    24,
                    "bold"
                )
            )

            self.sub_label.config(
                text="Waiting for Arduino..."
            )

            self.bar_canvas.delete(
                "all"
            )

            self.graph_canvas.delete(
                "all"
            )

            self.update_virtual_led_sound(
                "SAFE"
            )

        # =================================================
        # SERIAL CONNECTED
        # =================================================
        else:

            self.signal = (
                self.real_rf_value
            )

            # -------------------------------------------------
            # RF VALUE
            # -------------------------------------------------
            self.rf_lbl.config(
                text=str(
                    self.signal
                )
            )

            # -------------------------------------------------
            # SIGNAL BAR
            # -------------------------------------------------
            self.bar_canvas.delete(
                "all"
            )

            bar_width = (
                self.signal
                / 1023
                * max(
                    300,
                    self.bar_canvas.winfo_width()
                )
            )

            if (
                self.signal
                <= SAFE_MAX
            ):

                bar_color = "#00ff9d"

            elif (
                self.signal
                <= SUSPICIOUS_MAX
            ):

                bar_color = "#ffcc00"

            else:

                bar_color = "#ff3b3b"

            self.bar_canvas.create_rectangle(
                0,
                0,
                bar_width,
                18,
                fill=bar_color,
                outline=bar_color
            )

            # -------------------------------------------------
            # HISTORY
            # -------------------------------------------------
            self.history.append(
                self.signal
            )

            if len(
                self.history
            ) > GRAPH_POINTS:

                self.history.pop(0)

            # -------------------------------------------------
            # AI ANALYSIS
            # -------------------------------------------------
            avg, variance, pattern = (
                self.ai_brain(
                    self.history
                )
            )

            if variance > 400:

                var_status = "HIGH"

            elif variance > 120:

                var_status = "MEDIUM"

            else:

                var_status = "LOW"

            activity = (
                "ACTIVE"
                if self.signal > 40
                else "IDLE"
            )

            # -------------------------------------------------
            # ANOMALY SCORE
            # -------------------------------------------------
            anomaly_score = int(
                min(
                    95,
                    (
                        self.signal
                        * 0.5
                    )
                    + (
                        variance
                        / 40
                    )
                )
            )

            if anomaly_score > 70:

                threat_text = "HIGH"

                anomaly_color = "#ff3b3b"

            elif anomaly_score > 40:

                threat_text = "MEDIUM"

                anomaly_color = "#ffcc00"

            else:

                threat_text = "LOW"

                anomaly_color = "#00ff9d"

            self.anomaly_lbl.config(
                text=(
                    f"Anomaly Score : {anomaly_score}% "
                    f"| Threat : {threat_text}"
                ),
                fg=anomaly_color
            )

            # -------------------------------------------------
            # UPDATE GRAPH
            # -------------------------------------------------
            self.draw_signal_graph()

            # -------------------------------------------------
            # ANALYSIS LABELS
            # -------------------------------------------------
            self.pattern_lbl.config(
                text=(
                    f"Signal Pattern : "
                    f"{pattern}"
                )
            )

            self.var_lbl.config(
                text=(
                    f"Signal Variation : "
                    f"{var_status} "
                    f"({int(variance)})"
                    f" | Activity : "
                    f"{activity}"
                    f" | Avg: "
                    f"{int(avg)}"
                )
            )

            # =================================================
            # ALERT
            # =================================================
            if (
                self.signal
                > SUSPICIOUS_MAX
            ):

                self.status_label.config(
                    text=(
                        "POTENTIAL DRONE\n"
                        "SIGNAL DETECTED"
                    ),
                    fg="#ff3b3b",
                    font=(
                        "Consolas",
                        22,
                        "bold"
                    )
                )

                self.threat_lbl.config(
                    text="HIGH"
                )

                self.final_lbl.config(
                    text=(
                        f"FINAL STATUS : "
                        f"POTENTIAL DRONE "
                        f"[{anomaly_score}%]"
                    ),
                    fg="#ff3b3b"
                )

                self.ai_decision_lbl.config(
                    text=(
                        f"AI DECISION -> "
                        f"{pattern} "
                        f"PATTERN DETECTED - "
                        f"ALERT"
                    ),
                    fg="#ff3b3b"
                )

                self.sub_label.config(
                    text=(
                        f"REAL LCD SYNCED | "
                        f"RF:{self.signal} | "
                        f"Pattern:{pattern} | "
                        f"SOUND ON"
                    )
                )

                self.update_virtual_led_sound(
                    "ALERT"
                )

                # Add log only when value changes
                current_log = (
                    f"ALERT: {self.signal}"
                )

                if (
                    self.log_box.size() == 0
                    or current_log
                    not in str(
                        self.log_box.get(
                            0
                        )
                    )
                ):

                    self.add_log(
                        f"[{datetime.now().strftime('%H:%M:%S')}] "
                        f"ALERT: RF={self.signal} "
                        f"Pattern={pattern} "
                        f"Anomaly={anomaly_score}%"
                    )

            # =================================================
            # SUSPICIOUS
            # =================================================
            elif (
                self.signal
                > SAFE_MAX
            ):

                self.status_label.config(
                    text=(
                        "SUSPICIOUS\n"
                        "RF ACTIVITY"
                    ),
                    fg="#ffcc00",
                    font=(
                        "Consolas",
                        20,
                        "bold"
                    )
                )

                self.threat_lbl.config(
                    text="MEDIUM"
                )

                self.final_lbl.config(
                    text=(
                        f"FINAL STATUS : "
                        f"SUSPICIOUS "
                        f"[{anomaly_score}%]"
                    ),
                    fg="#ffcc00"
                )

                self.ai_decision_lbl.config(
                    text=(
                        f"AI DECISION -> "
                        f"{pattern} - "
                        f"WARNING"
                    ),
                    fg="#ffcc00"
                )

                self.sub_label.config(
                    text=(
                        f"Monitoring | "
                        f"RF:{self.signal} | "
                        f"Pattern:{pattern} | "
                        f"Warning Beep"
                    )
                )

                self.update_virtual_led_sound(
                    "SUSPICIOUS"
                )

            # =================================================
            # SAFE
            # =================================================
            else:

                self.status_label.config(
                    text="SKY SAFE",
                    fg="#00ff9d",
                    font=(
                        "Consolas",
                        28,
                        "bold"
                    )
                )

                self.threat_lbl.config(
                    text="LOW"
                )

                self.final_lbl.config(
                    text=(
                        f"FINAL STATUS : "
                        f"SKY SAFE "
                        f"[{anomaly_score}%]"
                    ),
                    fg="#00ff9d"
                )

                self.ai_decision_lbl.config(
                    text=(
                        f"AI DECISION -> "
                        f"{pattern} - SAFE"
                    ),
                    fg="#00ff9d"
                )

                self.sub_label.config(
                    text=(
                        f"Scanning | "
                        f"RF:{self.signal} | "
                        f"{pattern} | "
                        f"No Sound"
                    )
                )

                self.update_virtual_led_sound(
                    "SAFE"
                )

        # =================================================
        # UPDATE EVERY 150 ms
        # =================================================
        self.root.after(
            150,
            self.update_system
        )

# =========================================================
# START APPLICATION
# =========================================================
if __name__ == "__main__":

    root = tk.Tk()

    app = RF_SHIELD_FINAL(
        root
    )

    root.mainloop()
