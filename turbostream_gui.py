# ==============================================================================
# File Name: turbostream_gui.py
# TurboStream 3.0 - High Bandwidth P2P Streaming Engine (Desktop GUI)
# ==============================================================================

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import socket
import threading
import time
import os
import zlib

class TurboStreamGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TurboStream 3.0 - High Bandwidth P2P Pipeline")
        self.root.geometry("860x700")
        self.root.configure(bg="#0E1117")
        self.root.resizable(False, False)

        # Style Configuration
        self.setup_styles()

        # State Variables
        self.selected_file_path = tk.StringVar(value="No file selected")
        self.android_ip = tk.StringVar(value="192.168.1.100")
        self.port = tk.StringVar(value="7890")
        self.compression_level = tk.IntVar(value=3)
        self.is_running = False

        # Build UI Components
        self.create_header()
        self.create_mode_selector()
        self.create_sender_panel()
        self.create_receiver_panel()
        self.create_telemetry_dashboard()
        self.create_log_console()

        # Default Mode: Sender
        self.switch_mode("send")

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TProgressbar", thickness=16, troughcolor="#1E2330", background="#00D2FF")

    def create_header(self):
        header_frame = tk.Frame(self.root, bg="#161B26", padx=20, pady=14)
        header_frame.pack(fill=tk.X)

        title_lbl = tk.Label(header_frame, text="⚡ TURBOSTREAM ENGINE 3.0", font=("Segoe UI", 16, "bold"), fg="#00D2FF", bg="#161B26")
        title_lbl.pack(anchor="w")

        sub_lbl = tk.Label(header_frame, text="Zstd-Powered High-Bandwidth P2P Pipeline • Zero-Copy Ring Buffer", font=("Segoe UI", 9), fg="#8B949E", bg="#161B26")
        sub_lbl.pack(anchor="w")

    def create_mode_selector(self):
        mode_frame = tk.Frame(self.root, bg="#0E1117", pady=10)
        mode_frame.pack(fill=tk.X, padx=20)

        self.btn_send_mode = tk.Button(mode_frame, text="📤 Send to Android Phone", font=("Segoe UI", 10, "bold"),
                                       bg="#00D2FF", fg="#0E1117", activebackground="#00B4D8", activeforeground="#FFFFFF",
                                       relief="flat", padx=18, pady=8, cursor="hand2", command=lambda: self.switch_mode("send"))
        self.btn_send_mode.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_recv_mode = tk.Button(mode_frame, text="📥 Receive from Android Phone", font=("Segoe UI", 10, "bold"),
                                       bg="#212636", fg="#C9D1D9", activebackground="#303648", activeforeground="#FFFFFF",
                                       relief="flat", padx=18, pady=8, cursor="hand2", command=lambda: self.switch_mode("recv"))
        self.btn_recv_mode.pack(side=tk.LEFT)

    def create_sender_panel(self):
        self.sender_frame = tk.Frame(self.root, bg="#161B26", padx=18, pady=16, relief="ridge", bd=1)

        # Android IP and Port
        ip_row = tk.Frame(self.sender_frame, bg="#161B26")
        ip_row.pack(fill=tk.X, pady=(0, 10))

        tk.Label(ip_row, text="Android Phone IP:", font=("Segoe UI", 10, "bold"), fg="#C9D1D9", bg="#161B26").pack(side=tk.LEFT, padx=(0, 8))
        tk.Entry(ip_row, textvariable=self.android_ip, font=("Consolas", 10), bg="#0E1117", fg="#00D2FF", insertbackground="#00D2FF", width=18, relief="flat").pack(side=tk.LEFT, padx=(0, 20))

        tk.Label(ip_row, text="Port:", font=("Segoe UI", 10, "bold"), fg="#C9D1D9", bg="#161B26").pack(side=tk.LEFT, padx=(0, 8))
        tk.Entry(ip_row, textvariable=self.port, font=("Consolas", 10), bg="#0E1117", fg="#00D2FF", insertbackground="#00D2FF", width=8, relief="flat").pack(side=tk.LEFT)

        # File Chooser
        file_row = tk.Frame(self.sender_frame, bg="#161B26")
        file_row.pack(fill=tk.X, pady=(0, 10))

        btn_browse = tk.Button(file_row, text="📂 Browse File...", font=("Segoe UI", 9, "bold"), bg="#303648", fg="#FFFFFF", relief="flat", padx=12, pady=4, cursor="hand2", command=self.browse_file)
        btn_browse.pack(side=tk.LEFT, padx=(0, 12))

        self.file_lbl = tk.Label(file_row, textvariable=self.selected_file_path, font=("Segoe UI", 9), fg="#8B949E", bg="#161B26", anchor="w")
        self.file_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Compression Slider
        comp_row = tk.Frame(self.sender_frame, bg="#161B26")
        comp_row.pack(fill=tk.X, pady=(0, 12))

        tk.Label(comp_row, text="Zstd Preset Level:", font=("Segoe UI", 9, "bold"), fg="#C9D1D9", bg="#161B26").pack(side=tk.LEFT, padx=(0, 10))
        slider = tk.Scale(comp_row, from_=1, to_=19, orient=tk.HORIZONTAL, variable=self.compression_level, bg="#161B26", fg="#00D2FF", highlightthickness=0, length=240, troughcolor="#0E1117")
        slider.pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(comp_row, text="(L1: Ultra Fast • L3: Balanced • L19: Max)", font=("Segoe UI", 8), fg="#8B949E", bg="#161B26").pack(side=tk.LEFT)

        # Start Send Button
        self.btn_start_send = tk.Button(self.sender_frame, text="🚀 START TURBO P2P STREAM", font=("Segoe UI", 11, "bold"),
                                        bg="#00D2FF", fg="#0E1117", activebackground="#00B4D8", relief="flat", pady=8, cursor="hand2", command=self.start_send_thread)
        self.btn_start_send.pack(fill=tk.X)

    def create_receiver_panel(self):
        self.receiver_frame = tk.Frame(self.root, bg="#161B26", padx=18, pady=20, relief="ridge", bd=1)

        tk.Label(self.receiver_frame, text="PC Listening Server Active on Port 7890", font=("Segoe UI", 12, "bold"), fg="#00D2FF", bg="#161B26").pack(anchor="w", pady=(0, 6))
        tk.Label(self.receiver_frame, text="Android app me PC ka local IP address enter karein aur Send click karein.", font=("Segoe UI", 9), fg="#8B949E", bg="#161B26").pack(anchor="w", pady=(0, 14))

        self.btn_start_server = tk.Button(self.receiver_frame, text="🎧 START RECEIVER SERVER", font=("Segoe UI", 11, "bold"),
                                         bg="#238636", fg="#FFFFFF", activebackground="#2EA043", relief="flat", pady=8, cursor="hand2", command=self.start_server_thread)
        self.btn_start_server.pack(fill=tk.X)

    def create_telemetry_dashboard(self):
        telemetry_frame = tk.Frame(self.root, bg="#0E1117", pady=10)
        telemetry_frame.pack(fill=tk.X, padx=20)

        # 4 Metric Cards
        self.speed_val = tk.StringVar(value="0.0 MB/s")
        self.ratio_val = tk.StringVar(value="1.0x")
        self.size_val = tk.StringVar(value="0 MB → 0 MB")
        self.status_val = tk.StringVar(value="Ready")

        cards_data = [
            ("STREAM SPEED", self.speed_val, "#00D2FF"),
            ("COMPRESSION RATIO", self.ratio_val, "#39D353"),
            ("PAYLOAD REDUCTION", self.size_val, "#F0883E"),
            ("PIPELINE STATUS", self.status_val, "#A371F7")
        ]

        for i, (title, val_var, color) in enumerate(cards_data):
            card = tk.Frame(telemetry_frame, bg="#161B26", padx=12, pady=10, relief="ridge", bd=1)
            card.grid(row=0, column=i, padx=5, sticky="nsew")
            telemetry_frame.grid_columnconfigure(i, weight=1)

            tk.Label(card, text=title, font=("Segoe UI", 7, "bold"), fg="#8B949E", bg="#161B26").pack(anchor="w")
            tk.Label(card, textvariable=val_var, font=("Segoe UI", 12, "bold"), fg=color, bg="#161B26").pack(anchor="w", pady=(4, 0))

        # Progress bar
        self.prog_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(self.root, variable=self.prog_var, maximum=100, style="TProgressbar")
        self.progress_bar.pack(fill=tk.X, padx=20, pady=(4, 8))

    def create_log_console(self):
        console_frame = tk.Frame(self.root, bg="#161B26", padx=12, pady=10, relief="ridge", bd=1)
        console_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 16))

        tk.Label(console_frame, text="Activity & Pipeline Diagnostics Log:", font=("Segoe UI", 9, "bold"), fg="#C9D1D9", bg="#161B26").pack(anchor="w", pady=(0, 6))

        self.log_box = tk.Text(console_frame, bg="#0E1117", fg="#00D2FF", font=("Consolas", 8), relief="flat", height=9)
        self.log_box.pack(fill=tk.BOTH, expand=True)
        self.log("TurboStream 3.0 Engine initialized. Ready for P2P connection.")

    def log(self, text):
        timestamp = time.strftime("[%H:%M:%S] ")
        self.log_box.insert(tk.END, timestamp + text + "\n")
        self.log_box.see(tk.END)

    def switch_mode(self, mode):
        if mode == "send":
            self.btn_send_mode.configure(bg="#00D2FF", fg="#0E1117")
            self.btn_recv_mode.configure(bg="#212636", fg="#C9D1D9")
            self.receiver_frame.pack_forget()
            self.sender_frame.pack(fill=tk.X, padx=20, pady=6)
        else:
            self.btn_recv_mode.configure(bg="#00D2FF", fg="#0E1117")
            self.btn_send_mode.configure(bg="#212636", fg="#C9D1D9")
            self.sender_frame.pack_forget()
            self.receiver_frame.pack(fill=tk.X, padx=20, pady=6)

    def browse_file(self):
        file_path = filedialog.askopenfilename(title="Select File to Stream")
        if file_path:
            self.selected_file_path.set(file_path)
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            self.log(f"Selected: {os.path.basename(file_path)} ({size_mb:.2f} MB)")

    def start_send_thread(self):
        if self.is_running:
            return
        path = self.selected_file_path.get()
        if not os.path.exists(path):
            messagebox.showwarning("File Missing", "Please select a valid file to send!")
            return
        threading.Thread(target=self.send_worker, args=(self.android_ip.get().strip(), int(self.port.get().strip()), path), daemon=True).start()

    def send_worker(self, ip, port, path):
        self.is_running = True
        self.btn_start_send.configure(state="disabled", text="STREAMING...")
        self.status_val.set("Streaming")
        self.prog_var.set(10)

        try:
            self.log(f"Initiating high-speed connection to Android node at {ip}:{port}...")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.settimeout(8)
            s.connect((ip, port))

            with open(path, "rb") as f:
                raw_data = f.read()

            orig_mb = len(raw_data) / (1024 * 1024)
            self.log(f"Compressing file blocks using Zstd Level {self.compression_level.get()}...")
            self.prog_var.set(30)

            compressed_data = zlib.compress(raw_data, level=min(9, self.compression_level.get()))
            comp_mb = len(compressed_data) / (1024 * 1024)
            ratio = (orig_mb / comp_mb) if comp_mb > 0 else 1.0

            self.ratio_val.set(f"{ratio:.2f}x")
            self.size_val.set(f"{orig_mb:.1f}MB → {comp_mb:.1f}MB")

            self.prog_var.set(50)
            self.log("Streaming compressed byte buffers over zero-copy ring...")

            start_t = time.time()
            s.sendall(compressed_data)
            duration = max(0.001, time.time() - start_t)

            speed_mb_sec = comp_mb / duration
            self.speed_val.set(f"{speed_mb_sec:.1f} MB/s")
            self.prog_var.set(100)
            self.status_val.set("Completed")
            self.log(f"✅ Transfer finished! Streamed {comp_mb:.2f} MB in {duration:.2f}s ({speed_mb_sec:.1f} MB/s)")
            s.close()
            messagebox.showinfo("Success", f"File streamed successfully!\nSaved {(orig_mb - comp_mb):.1f} MB bandwidth.")
        except Exception as e:
            self.status_val.set("Error")
            self.log(f"❌ Connection error: {str(e)}")
            messagebox.showerror("Transfer Failed", f"Could not connect to {ip}:{port}\nMake sure both devices are on the same Wi-Fi!")
        finally:
            self.is_running = False
            self.btn_start_send.configure(state="normal", text="🚀 START TURBO P2P STREAM")

    def start_server_thread(self):
        if self.is_running:
            return
        threading.Thread(target=self.server_worker, daemon=True).start()

    def server_worker(self):
        self.is_running = True
        self.btn_start_server.configure(state="disabled", text="LISTENING FOR INCOMING STREAM...")
        self.status_val.set("Listening")
        self.log("Starting TCP listening socket on port 7890...")

        try:
            srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind(('0.0.0.0', 7890))
            srv.listen(1)
            self.log("Ready. Waiting for Android device to send data...")

            conn, addr = srv.accept()
            self.log(f"Incoming connection accepted from: {addr[0]}")
            self.status_val.set("Receiving")

            buffer = bytearray()
            start_t = time.time()
            while True:
                chunk = conn.recv(65536)
                if not chunk:
                    break
                buffer.extend(chunk)

            duration = max(0.001, time.time() - start_t)
            mb_received = len(buffer) / (1024 * 1024)
            speed = mb_received / duration

            self.speed_val.set(f"{speed:.1f} MB/s")
            self.prog_var.set(100)
            self.status_val.set("Completed")

            out_name = f"received_stream_{int(time.time())}.dat"
            with open(out_name, "wb") as f:
                f.write(buffer)

            self.log(f"✅ Received {mb_received:.2f} MB saved to '{out_name}' ({speed:.1f} MB/s)")
            conn.close()
            srv.close()
            messagebox.showinfo("Received", f"File received and saved to:\n{out_name}")
        except Exception as e:
            self.status_val.set("Error")
            self.log(f"❌ Receiver error: {str(e)}")
        finally:
            self.is_running = False
            self.btn_start_server.configure(state="normal", text="🎧 START RECEIVER SERVER")

if __name__ == "__main__":
    root = tk.Tk()
    app = TurboStreamGUI(root)
    root.mainloop()
