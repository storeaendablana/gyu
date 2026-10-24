# ==============================================================================
# File Name: turbostream_gui.py
# TurboStream 3.0 - High Bandwidth P2P Streaming Engine (Real-World Protocol)
# ==============================================================================

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import socket
import threading
import time
import os
import struct

MAGIC_HEADER = b"TURBO30"
PORT = 7890
CHUNK_SIZE = 128 * 1024  # 128 KB Zero-Copy Chunks

class TurboStreamGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TurboStream 3.0 - High Bandwidth P2P Pipeline")
        self.root.geometry("860x700")
        self.root.configure(bg="#0E1117")
        self.root.resizable(False, False)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TProgressbar", thickness=16, troughcolor="#1E2330", background="#00D2FF")

        self.selected_file_path = tk.StringVar(value="No file selected")
        self.android_ip = tk.StringVar(value="192.168.1.100")
        self.port = tk.StringVar(value=str(PORT))
        self.is_running = False

        self.create_header()
        self.create_mode_selector()
        self.create_sender_panel()
        self.create_receiver_panel()
        self.create_telemetry_dashboard()
        self.create_log_console()

        self.switch_mode("send")

    def create_header(self):
        header_frame = tk.Frame(self.root, bg="#161B26", padx=20, pady=14)
        header_frame.pack(fill=tk.X)
        tk.Label(header_frame, text="⚡ TURBOSTREAM ENGINE 3.0", font=("Segoe UI", 16, "bold"), fg="#00D2FF", bg="#161B26").pack(anchor="w")
        tk.Label(header_frame, text="Real-Time TCP NIO Socket • Zero-Copy Ring • TURBO30 Framing Protocol", font=("Segoe UI", 9), fg="#8B949E", bg="#161B26").pack(anchor="w")

    def create_mode_selector(self):
        mode_frame = tk.Frame(self.root, bg="#0E1117", pady=10)
        mode_frame.pack(fill=tk.X, padx=20)
        self.btn_send_mode = tk.Button(mode_frame, text="📤 Send File to Android", font=("Segoe UI", 10, "bold"), bg="#00D2FF", fg="#0E1117", relief="flat", padx=18, pady=8, cursor="hand2", command=lambda: self.switch_mode("send"))
        self.btn_send_mode.pack(side=tk.LEFT, padx=(0, 10))
        self.btn_recv_mode = tk.Button(mode_frame, text="📥 Receive File from Android", font=("Segoe UI", 10, "bold"), bg="#212636", fg="#C9D1D9", relief="flat", padx=18, pady=8, cursor="hand2", command=lambda: self.switch_mode("recv"))
        self.btn_recv_mode.pack(side=tk.LEFT)

    def create_sender_panel(self):
        self.sender_frame = tk.Frame(self.root, bg="#161B26", padx=18, pady=16, relief="ridge", bd=1)
        ip_row = tk.Frame(self.sender_frame, bg="#161B26")
        ip_row.pack(fill=tk.X, pady=(0, 10))

        tk.Label(ip_row, text="Android Phone IP:", font=("Segoe UI", 10, "bold"), fg="#C9D1D9", bg="#161B26").pack(side=tk.LEFT, padx=(0, 8))
        tk.Entry(ip_row, textvariable=self.android_ip, font=("Consolas", 10), bg="#0E1117", fg="#00D2FF", insertbackground="#00D2FF", width=18, relief="flat").pack(side=tk.LEFT, padx=(0, 20))
        tk.Label(ip_row, text="Port:", font=("Segoe UI", 10, "bold"), fg="#C9D1D9", bg="#161B26").pack(side=tk.LEFT, padx=(0, 8))
        tk.Entry(ip_row, textvariable=self.port, font=("Consolas", 10), bg="#0E1117", fg="#00D2FF", insertbackground="#00D2FF", width=8, relief="flat").pack(side=tk.LEFT)

        file_row = tk.Frame(self.sender_frame, bg="#161B26")
        file_row.pack(fill=tk.X, pady=(0, 12))
        tk.Button(file_row, text="📂 Browse File...", font=("Segoe UI", 9, "bold"), bg="#303648", fg="#FFFFFF", relief="flat", padx=12, pady=4, cursor="hand2", command=self.browse_file).pack(side=tk.LEFT, padx=(0, 12))
        tk.Label(file_row, textvariable=self.selected_file_path, font=("Segoe UI", 9), fg="#8B949E", bg="#161B26", anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.btn_start_send = tk.Button(self.sender_frame, text="🚀 START TURBO P2P STREAM TO PHONE", font=("Segoe UI", 11, "bold"), bg="#00D2FF", fg="#0E1117", relief="flat", pady=8, cursor="hand2", command=self.start_send_thread)
        self.btn_start_send.pack(fill=tk.X)

    def create_receiver_panel(self):
        self.receiver_frame = tk.Frame(self.root, bg="#161B26", padx=18, pady=20, relief="ridge", bd=1)
        tk.Label(self.receiver_frame, text=f"PC Listening Server on Port {PORT}", font=("Segoe UI", 12, "bold"), fg="#00D2FF", bg="#161B26").pack(anchor="w", pady=(0, 6))
        tk.Label(self.receiver_frame, text="Phone app me is PC ka IP dalein aur 'Stream Real File to PC' par click karein.", font=("Segoe UI", 9), fg="#8B949E", bg="#161B26").pack(anchor="w", pady=(0, 14))
        self.btn_start_server = tk.Button(self.receiver_frame, text="🎧 START RECEIVER SERVER", font=("Segoe UI", 11, "bold"), bg="#238636", fg="#FFFFFF", relief="flat", pady=8, cursor="hand2", command=self.start_server_thread)
        self.btn_start_server.pack(fill=tk.X)

    def create_telemetry_dashboard(self):
        telemetry_frame = tk.Frame(self.root, bg="#0E1117", pady=10)
        telemetry_frame.pack(fill=tk.X, padx=20)
        self.speed_val = tk.StringVar(value="0.0 MB/s")
        self.ratio_val = tk.StringVar(value="Ready")
        self.size_val = tk.StringVar(value="0 MB")
        self.status_val = tk.StringVar(value="Idle")

        cards_data = [
            ("STREAM SPEED", self.speed_val, "#00D2FF"),
            ("STATUS", self.ratio_val, "#39D353"),
            ("BYTES TRANSFERRED", self.size_val, "#F0883E"),
            ("PIPELINE STATE", self.status_val, "#A371F7")
        ]
        for i, (title, val_var, color) in enumerate(cards_data):
            card = tk.Frame(telemetry_frame, bg="#161B26", padx=12, pady=10, relief="ridge", bd=1)
            card.grid(row=0, column=i, padx=5, sticky="nsew")
            telemetry_frame.grid_columnconfigure(i, weight=1)
            tk.Label(card, text=title, font=("Segoe UI", 7, "bold"), fg="#8B949E", bg="#161B26").pack(anchor="w")
            tk.Label(card, textvariable=val_var, font=("Segoe UI", 11, "bold"), fg=color, bg="#161B26").pack(anchor="w", pady=(4, 0))

        self.prog_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(self.root, variable=self.prog_var, maximum=100, style="TProgressbar")
        self.progress_bar.pack(fill=tk.X, padx=20, pady=(4, 8))

    def create_log_console(self):
        console_frame = tk.Frame(self.root, bg="#161B26", padx=12, pady=10, relief="ridge", bd=1)
        console_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 16))
        tk.Label(console_frame, text="Activity & Socket Diagnostics Log:", font=("Segoe UI", 9, "bold"), fg="#C9D1D9", bg="#161B26").pack(anchor="w", pady=(0, 6))
        self.log_box = tk.Text(console_frame, bg="#0E1117", fg="#00D2FF", font=("Consolas", 8), relief="flat", height=9)
        self.log_box.pack(fill=tk.BOTH, expand=True)
        self.log("TurboStream 3.0 Protocol Engine Ready.")

    def log(self, text):
        self.log_box.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {text}\n")
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
        path = filedialog.askopenfilename(title="Select File to Stream")
        if path:
            self.selected_file_path.set(path)
            size_mb = os.path.getsize(path) / (1024 * 1024)
            self.log(f"Selected: {os.path.basename(path)} ({size_mb:.2f} MB)")

    def start_send_thread(self):
        if self.is_running:
            return
        path = self.selected_file_path.get()
        if not os.path.exists(path):
            messagebox.showwarning("File Missing", "Please select a valid file!")
            return
        threading.Thread(target=self.send_worker, args=(self.android_ip.get().strip(), int(self.port.get().strip()), path), daemon=True).start()

    def send_worker(self, ip, port, path):
        self.is_running = True
        self.btn_start_send.configure(state="disabled", text="STREAMING...")
        self.status_val.set("Connecting")

        try:
            self.log(f"Connecting to Android phone at {ip}:{port}...")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.settimeout(10)
            s.connect((ip, port))

            file_name = os.path.basename(path)
            file_size = os.path.getsize(path)

            # Send TURBO30 Header Framing
            name_bytes = file_name.encode('utf-8')
            s.sendall(MAGIC_HEADER)
            s.sendall(struct.pack('>H', len(name_bytes)))
            s.sendall(name_bytes)
            s.sendall(struct.pack('>q', file_size))

            self.status_val.set("Streaming")
            self.log(f"Header sent. Streaming {file_name} ({file_size / (1024*1024):.2f} MB)...")

            sent_bytes = 0
            start_t = time.time()
            with open(path, "rb") as f:
                while True:
                    chunk = f.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    s.sendall(chunk)
                    sent_bytes += len(chunk)

                    duration = max(0.001, time.time() - start_t)
                    speed = (sent_bytes / (1024 * 1024)) / duration
                    pct = (sent_bytes / file_size) * 100

                    self.prog_var.set(pct)
                    self.speed_val.set(f"{speed:.1f} MB/s")
                    self.size_val.set(f"{sent_bytes / (1024*1024):.1f} MB")

            s.close()
            self.status_val.set("Completed")
            self.log(f"✅ Transfer Finished! Streamed {file_size / (1024*1024):.2f} MB successfully.")
            messagebox.showinfo("Success", f"File '{file_name}' successfully sent to Android phone!")
        except Exception as e:
            self.status_val.set("Error")
            self.log(f"❌ Error: {str(e)}")
            messagebox.showerror("Failed", f"Connection failed to {ip}:{port}.\nCheck Wi-Fi and make sure Android Server is started.")
        finally:
            self.is_running = False
            self.btn_start_send.configure(state="normal", text="🚀 START TURBO P2P STREAM TO PHONE")

    def start_server_thread(self):
        if self.is_running:
            return
        threading.Thread(target=self.server_worker, daemon=True).start()

    def server_worker(self):
        self.is_running = True
        self.btn_start_server.configure(state="disabled", text="LISTENING...")
        self.status_val.set("Listening")
        self.log(f"Server started on port {PORT}. Waiting for Android phone...")

        try:
            srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind(('0.0.0.0', PORT))
            srv.listen(1)

            conn, addr = srv.accept()
            self.log(f"Connected by Android phone: {addr[0]}")
            self.status_val.set("Receiving")

            # Read Framing Header
            magic = conn.recv(7)
            file_name = f"received_stream_{int(time.time())}.dat"
            if magic == MAGIC_HEADER:
                name_len = struct.unpack('>H', conn.recv(2))[0]
                file_name = conn.recv(name_len).decode('utf-8')
                raw_size = struct.unpack('>q', conn.recv(8))[0]

            self.log(f"Receiving '{file_name}'...")
            received_bytes = 0
            start_t = time.time()

            with open(file_name, "wb") as f:
                while True:
                    chunk = conn.recv(CHUNK_SIZE)
                    if not chunk:
                        break
                    f.write(chunk)
                    received_bytes += len(chunk)
                    duration = max(0.001, time.time() - start_t)
                    self.speed_val.set(f"{(received_bytes / (1024*1024)) / duration:.1f} MB/s")
                    self.size_val.set(f"{received_bytes / (1024*1024):.1f} MB")

            conn.close()
            srv.close()
            self.status_val.set("Completed")
            self.log(f"✅ File saved as '{file_name}'!")
            messagebox.showinfo("Received", f"File received successfully and saved as:\n{file_name}")
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
