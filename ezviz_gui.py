"""
GUI untuk EZVIZ Camera Controller
Requirements:
    pip install pyezvizapi customtkinter pillow opencv-python
"""

import sys
import io
import customtkinter as ctk
from tkinter import messagebox, ttk
import threading
import json
from datetime import datetime
from PIL import Image, ImageTk
import cv2

# Fix encoding untuk Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from pyezviz.client import EzvizClient
from pyezviz.camera import EzvizCamera


class LoginDialog:
    """Dialog untuk login EZVIZ"""
    def __init__(self, parent, default_region='apiisgp.ezvizlife.com'):
        self.username = None
        self.password = None
        self.region = default_region
        
        # Create dialog window
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("EZVIZ Login")
        self.dialog.geometry("450x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"450x400+{x}+{y}")
        
        # Title
        title = ctk.CTkLabel(self.dialog, text="🔐 Login ke EZVIZ", 
                            font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=20)
        
        # Form frame
        form_frame = ctk.CTkFrame(self.dialog)
        form_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        # Email
        ctk.CTkLabel(form_frame, text="📧 Email:", 
                    font=ctk.CTkFont(size=14)).pack(anchor="w", padx=20, pady=(20, 5))
        self.email_entry = ctk.CTkEntry(form_frame, width=350, placeholder_text="email@example.com")
        self.email_entry.pack(padx=20, pady=(0, 15))
        self.email_entry.focus()
        
        # Password
        ctk.CTkLabel(form_frame, text="🔑 Password:", 
                    font=ctk.CTkFont(size=14)).pack(anchor="w", padx=20, pady=(0, 5))
        self.password_entry = ctk.CTkEntry(form_frame, width=350, show="*", 
                                          placeholder_text="Password EZVIZ Anda")
        self.password_entry.pack(padx=20, pady=(0, 15))
        
        # Region
        ctk.CTkLabel(form_frame, text="🌍 Region Server:", 
                    font=ctk.CTkFont(size=14)).pack(anchor="w", padx=20, pady=(0, 5))
        
        self.region_var = ctk.StringVar(value=default_region)
        region_options = [
            "apiisgp.ezvizlife.com (Singapore/Asia)",
            "apiieu.ezvizlife.com (Europe)",
            "apiius.ezvizlife.com (United States)"
        ]
        self.region_menu = ctk.CTkOptionMenu(
            form_frame, 
            values=region_options,
            variable=self.region_var,
            width=350
        )
        self.region_menu.pack(padx=20, pady=(0, 20))
        
        # Buttons
        btn_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=20)
        
        cancel_btn = ctk.CTkButton(btn_frame, text="❌ Batal", 
                                   command=self.cancel, width=150,
                                   fg_color="gray")
        cancel_btn.pack(side="left", padx=5)
        
        login_btn = ctk.CTkButton(btn_frame, text="✓ Login", 
                                 command=self.submit, width=150)
        login_btn.pack(side="right", padx=5)
        
        # Bind Enter key
        self.email_entry.bind('<Return>', lambda e: self.password_entry.focus())
        self.password_entry.bind('<Return>', lambda e: self.submit())
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def submit(self):
        """Submit login"""
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not email or not password:
            messagebox.showwarning("Error", "Email dan password harus diisi!")
            return
        
        self.username = email
        self.password = password
        
        # Parse region from selection
        region_text = self.region_var.get()
        if "Singapore" in region_text or "Asia" in region_text:
            self.region = "apiisgp.ezvizlife.com"
        elif "Europe" in region_text:
            self.region = "apiieu.ezvizlife.com"
        elif "United States" in region_text:
            self.region = "apiius.ezvizlife.com"
        else:
            self.region = region_text.split()[0]
        
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel login"""
        self.username = None
        self.password = None
        self.dialog.destroy()


class RTSPInputDialog:
    """Dialog untuk input RTSP credentials"""
    def __init__(self, parent, camera_ip, port, camera_name):
        self.rtsp_url = None
        
        # Create dialog window
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("RTSP Stream Settings")
        self.dialog.geometry("500x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"500x500+{x}+{y}")
        
        # Title
        title = ctk.CTkLabel(self.dialog, text="📹 RTSP Stream", 
                            font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=20)
        
        # Camera info
        info_frame = ctk.CTkFrame(self.dialog, fg_color="gray25")
        info_frame.pack(fill="x", padx=30, pady=(0, 20))
        
        ctk.CTkLabel(info_frame, text=f"🎥 {camera_name}", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
        ctk.CTkLabel(info_frame, text=f"📍 {camera_ip}:{port}", 
                    font=ctk.CTkFont(size=12)).pack(pady=5)
        
        # Form frame
        form_frame = ctk.CTkFrame(self.dialog)
        form_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        # Username
        ctk.CTkLabel(form_frame, text="👤 Username:", 
                    font=ctk.CTkFont(size=14)).pack(anchor="w", padx=20, pady=(20, 5))
        self.username_entry = ctk.CTkEntry(form_frame, width=400, placeholder_text="admin")
        self.username_entry.insert(0, "admin")
        self.username_entry.pack(padx=20, pady=(0, 15))
        
        # Password
        ctk.CTkLabel(form_frame, text="🔑 Password:", 
                    font=ctk.CTkFont(size=14)).pack(anchor="w", padx=20, pady=(0, 5))
        self.password_entry = ctk.CTkEntry(form_frame, width=400, show="*",
                                          placeholder_text="Password RTSP")
        self.password_entry.pack(padx=20, pady=(0, 15))
        self.password_entry.focus()
        
        # Path
        ctk.CTkLabel(form_frame, text="📂 Stream Path:", 
                    font=ctk.CTkFont(size=14)).pack(anchor="w", padx=20, pady=(0, 5))
        self.path_entry = ctk.CTkEntry(form_frame, width=400, placeholder_text="/stream1")
        self.path_entry.insert(0, "/stream1")
        self.path_entry.pack(padx=20, pady=(0, 10))
        
        # Help text
        help_text = ctk.CTkLabel(
            form_frame,
            text="💡 Contoh path lain:\n"
                 "  /stream2 (sub stream)\n"
                 "  /h264/ch1/main/av_stream\n"
                 "  /Streaming/Channels/101",
            font=ctk.CTkFont(size=11),
            text_color="gray70",
            justify="left"
        )
        help_text.pack(anchor="w", padx=20, pady=(0, 15))
        
        # Preview
        ctk.CTkLabel(form_frame, text="🔗 URL Preview:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=20, pady=(10, 5))
        
        self.preview_label = ctk.CTkLabel(
            form_frame,
            text=f"rtsp://admin:****@{camera_ip}:{port}/stream1",
            font=ctk.CTkFont(size=11),
            text_color="cyan",
            wraplength=400
        )
        self.preview_label.pack(anchor="w", padx=20, pady=(0, 15))
        
        # Update preview on input change
        self.username_entry.bind('<KeyRelease>', lambda e: self.update_preview(camera_ip, port))
        self.password_entry.bind('<KeyRelease>', lambda e: self.update_preview(camera_ip, port))
        self.path_entry.bind('<KeyRelease>', lambda e: self.update_preview(camera_ip, port))
        
        # Buttons
        btn_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=20)
        
        cancel_btn = ctk.CTkButton(btn_frame, text="❌ Batal", 
                                   command=self.cancel, width=150,
                                   fg_color="gray")
        cancel_btn.pack(side="left", padx=5)
        
        connect_btn = ctk.CTkButton(btn_frame, text="▶ Connect", 
                                    command=lambda: self.submit(camera_ip, port), 
                                    width=150)
        connect_btn.pack(side="right", padx=5)
        
        # Bind Enter
        self.password_entry.bind('<Return>', lambda e: self.submit(camera_ip, port))
        self.path_entry.bind('<Return>', lambda e: self.submit(camera_ip, port))
        
        # Wait for dialog
        self.dialog.wait_window()
    
    def update_preview(self, camera_ip, port):
        """Update URL preview"""
        username = self.username_entry.get().strip() or "admin"
        password = self.password_entry.get().strip()
        path = self.path_entry.get().strip() or "/stream1"
        
        if password:
            preview = f"rtsp://{username}:****@{camera_ip}:{port}{path}"
        else:
            preview = f"rtsp://{username}:(empty)@{camera_ip}:{port}{path}"
        
        self.preview_label.configure(text=preview)
    
    def submit(self, camera_ip, port):
        """Submit and build RTSP URL"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        path = self.path_entry.get().strip()
        
        if not username:
            username = "admin"
        if not path:
            path = "/stream1"
        
        if not password:
            messagebox.showwarning("Error", "Password RTSP harus diisi!")
            return
        
        # Build RTSP URL
        self.rtsp_url = f"rtsp://{username}:{password}@{camera_ip}:{port}{path}"
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel"""
        self.rtsp_url = None
        self.dialog.destroy()


class EzvizGUI:
    def __init__(self):
        # Set appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Main window
        self.root = ctk.CTk()
        self.root.title("EZVIZ Camera Controller")
        self.root.geometry("1200x800")
        
        # Variables
        self.client = None
        self.cameras = {}
        self.selected_camera = None
        self.stream_thread = None
        self.stream_running = False
        self.current_frame = None
        
        # Load config
        self.config = self.load_config()
        
        # Create UI
        self.create_ui()
        
    def load_config(self):
        """Load konfigurasi dari file (optional)"""
        try:
            with open('ezviz_config.json', 'r') as f:
                return json.load(f)
        except:
            # Config file optional - bisa login manual
            return {'ezviz': {'region': 'apiisgp.ezvizlife.com'}}
    
    def create_ui(self):
        """Buat user interface"""
        # Header
        header = ctk.CTkFrame(self.root)
        header.pack(fill="x", padx=10, pady=10)
        
        title = ctk.CTkLabel(header, text="🎥 EZVIZ Camera Controller", 
                            font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(side="left", padx=10)
        
        self.status_label = ctk.CTkLabel(header, text="⚪ Disconnected", 
                                         font=ctk.CTkFont(size=14))
        self.status_label.pack(side="right", padx=10)
        
        # Login button
        self.login_btn = ctk.CTkButton(header, text="🔐 Login", 
                                       command=self.login_thread, width=100)
        self.login_btn.pack(side="right", padx=5)
        
        # Main content area (split)
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Left panel - Camera list
        left_panel = ctk.CTkFrame(main_frame, width=250)
        left_panel.pack(side="left", fill="y", padx=(0, 5))
        left_panel.pack_propagate(False)
        
        ctk.CTkLabel(left_panel, text="📹 Cameras", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        # Camera list scrollable frame
        self.camera_list_frame = ctk.CTkScrollableFrame(left_panel)
        self.camera_list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Center panel - Video view
        center_panel = ctk.CTkFrame(main_frame)
        center_panel.pack(side="left", fill="both", expand=True, padx=5)
        
        # Video display
        self.video_frame = ctk.CTkFrame(center_panel, fg_color="black")
        self.video_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.video_label = ctk.CTkLabel(self.video_frame, text="📹\nNo Camera Selected", 
                                       font=ctk.CTkFont(size=20))
        self.video_label.pack(expand=True)
        
        # Video controls
        video_controls = ctk.CTkFrame(center_panel)
        video_controls.pack(fill="x", padx=5, pady=5)
        
        self.stream_btn = ctk.CTkButton(video_controls, text="▶ Start Stream", 
                                        command=self.toggle_stream, state="disabled")
        self.stream_btn.pack(side="left", padx=5)
        
        self.snapshot_btn = ctk.CTkButton(video_controls, text="📷 Snapshot", 
                                         command=self.take_snapshot, state="disabled")
        self.snapshot_btn.pack(side="left", padx=5)
        
        # PTZ Controls
        ptz_frame = ctk.CTkFrame(center_panel)
        ptz_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(ptz_frame, text="PTZ Controls:", 
                    font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=5)
        
        # PTZ buttons
        ptz_grid = ctk.CTkFrame(ptz_frame)
        ptz_grid.pack(side="left", padx=10)
        
        self.btn_up = ctk.CTkButton(ptz_grid, text="▲", width=50, 
                                    command=lambda: self.move_camera("up"), state="disabled")
        self.btn_up.grid(row=0, column=1, padx=2, pady=2)
        
        self.btn_left = ctk.CTkButton(ptz_grid, text="◄", width=50, 
                                      command=lambda: self.move_camera("left"), state="disabled")
        self.btn_left.grid(row=1, column=0, padx=2, pady=2)
        
        self.btn_center = ctk.CTkButton(ptz_grid, text="●", width=50, state="disabled")
        self.btn_center.grid(row=1, column=1, padx=2, pady=2)
        
        self.btn_right = ctk.CTkButton(ptz_grid, text="►", width=50, 
                                       command=lambda: self.move_camera("right"), state="disabled")
        self.btn_right.grid(row=1, column=2, padx=2, pady=2)
        
        self.btn_down = ctk.CTkButton(ptz_grid, text="▼", width=50, 
                                      command=lambda: self.move_camera("down"), state="disabled")
        self.btn_down.grid(row=2, column=1, padx=2, pady=2)
        
        # Right panel - Controls & Info
        right_panel = ctk.CTkFrame(main_frame, width=300)
        right_panel.pack(side="left", fill="y", padx=(5, 0))
        right_panel.pack_propagate(False)
        
        # Camera info
        info_label = ctk.CTkLabel(right_panel, text="ℹ Camera Info", 
                                 font=ctk.CTkFont(size=16, weight="bold"))
        info_label.pack(pady=10)
        
        self.info_text = ctk.CTkTextbox(right_panel, height=200)
        self.info_text.pack(fill="x", padx=5, pady=5)
        self.info_text.insert("1.0", "Select a camera to view info")
        self.info_text.configure(state="disabled")
        
        # Controls
        controls_label = ctk.CTkLabel(right_panel, text="⚙ Controls", 
                                     font=ctk.CTkFont(size=16, weight="bold"))
        controls_label.pack(pady=10)
        
        controls_frame = ctk.CTkFrame(right_panel)
        controls_frame.pack(fill="x", padx=5, pady=5)
        
        # Alarm switch
        self.alarm_var = ctk.BooleanVar(value=False)
        self.alarm_switch = ctk.CTkSwitch(controls_frame, text="🔔 Alarm Notify", 
                                         variable=self.alarm_var, 
                                         command=self.toggle_alarm, state="disabled")
        self.alarm_switch.pack(anchor="w", padx=10, pady=5)
        
        # Audio switch
        self.audio_var = ctk.BooleanVar(value=False)
        self.audio_switch = ctk.CTkSwitch(controls_frame, text="🔊 Audio", 
                                         variable=self.audio_var, 
                                         command=self.toggle_audio, state="disabled")
        self.audio_switch.pack(anchor="w", padx=10, pady=5)
        
        # IR LED switch
        self.ir_var = ctk.BooleanVar(value=False)
        self.ir_switch = ctk.CTkSwitch(controls_frame, text="🌙 IR LED", 
                                      variable=self.ir_var, 
                                      command=self.toggle_ir, state="disabled")
        self.ir_switch.pack(anchor="w", padx=10, pady=5)
        
        # Privacy mode switch
        self.privacy_var = ctk.BooleanVar(value=False)
        self.privacy_switch = ctk.CTkSwitch(controls_frame, text="🔒 Privacy Mode", 
                                           variable=self.privacy_var, 
                                           command=self.toggle_privacy, state="disabled")
        self.privacy_switch.pack(anchor="w", padx=10, pady=5)
        
        # Action buttons
        actions_frame = ctk.CTkFrame(right_panel)
        actions_frame.pack(fill="x", padx=5, pady=10)
        
        self.refresh_btn = ctk.CTkButton(actions_frame, text="🔄 Refresh Status", 
                                        command=self.refresh_status, state="disabled")
        self.refresh_btn.pack(fill="x", padx=5, pady=5)
        
        self.reboot_btn = ctk.CTkButton(actions_frame, text="🔃 Reboot Camera", 
                                       command=self.reboot_camera, 
                                       fg_color="orange", state="disabled")
        self.reboot_btn.pack(fill="x", padx=5, pady=5)
        
    def login_thread(self):
        """Login dalam thread terpisah"""
        # Show login dialog
        login_dialog = LoginDialog(self.root, self.config.get('ezviz', {}).get('region', 'apiisgp.ezvizlife.com'))
        
        if not login_dialog.username or not login_dialog.password:
            messagebox.showwarning("Cancelled", "Login dibatalkan.")
            return
        
        self.login_btn.configure(state="disabled", text="Logging in...")
        
        # Store credentials for this session
        self.session_username = login_dialog.username
        self.session_password = login_dialog.password
        self.session_region = login_dialog.region
        
        threading.Thread(target=self.login, daemon=True).start()
        
    def login(self):
        """Login ke EZVIZ"""
        try:
            username = self.session_username
            password = self.session_password
            region = self.session_region
            
            self.client = EzvizClient(username, password, region)
            self.client.login()
            
            # Get cameras
            self.cameras = self.client.get_device_infos()
            
            # Update UI in main thread
            self.root.after(0, self.on_login_success)
            
        except Exception as e:
            self.root.after(0, lambda: self.on_login_error(str(e)))
    
    def on_login_success(self):
        """Callback ketika login berhasil"""
        self.status_label.configure(text=f"🟢 Connected ({len(self.cameras)} cameras)")
        self.login_btn.configure(text="✓ Logged In", state="disabled")
        
        # Populate camera list
        for widget in self.camera_list_frame.winfo_children():
            widget.destroy()
            
        for serial, camera_data in self.cameras.items():
            name = camera_data.get('name', serial)
            status = camera_data.get('status', 0)
            status_icon = "🟢" if status == 1 else "🔴"
            
            btn = ctk.CTkButton(self.camera_list_frame, 
                               text=f"{status_icon} {name}", 
                               command=lambda s=serial: self.select_camera(s),
                               anchor="w")
            btn.pack(fill="x", pady=2)
            
        messagebox.showinfo("Success", f"Login berhasil!\n{len(self.cameras)} kamera ditemukan.")
    
    def on_login_error(self, error):
        """Callback ketika login gagal"""
        self.status_label.configure(text="🔴 Login Failed")
        self.login_btn.configure(text="🔐 Retry Login", state="normal")
        messagebox.showerror("Login Error", f"Login gagal:\n{error}")
    
    def select_camera(self, serial):
        """Pilih kamera"""
        self.selected_camera = serial
        camera = EzvizCamera(self.client, serial)
        status = camera.status()
        
        # Update info
        self.info_text.configure(state="normal")
        self.info_text.delete("1.0", "end")
        info = f"""
Name: {status.get('name', 'N/A')}
Serial: {serial}
Model: {status.get('device_sub_category', 'N/A')}
Status: {'🟢 Online' if status.get('status') == 1 else '🔴 Offline'}
IP: {status.get('local_ip', 'N/A')}
Signal: {status.get('wifiInfos', {}).get('signal', 'N/A')}%
Version: {status.get('version', 'N/A')}
"""
        self.info_text.insert("1.0", info)
        self.info_text.configure(state="disabled")
        
        # Update switches based on current status
        self.alarm_var.set(status.get('alarm_notify', False))
        switches = status.get('switches', {})
        self.audio_var.set(switches.get('22', False))  # Audio switch ID
        self.ir_var.set(switches.get('10', False))     # IR LED switch ID
        self.privacy_var.set(switches.get('2', False)) # Privacy switch ID
        
        # Enable controls
        self.stream_btn.configure(state="normal")
        self.snapshot_btn.configure(state="normal")
        self.alarm_switch.configure(state="normal")
        self.audio_switch.configure(state="normal")
        self.ir_switch.configure(state="normal")
        self.privacy_switch.configure(state="normal")
        self.refresh_btn.configure(state="normal")
        self.reboot_btn.configure(state="normal")
        
        # Enable PTZ if supported
        self.btn_up.configure(state="normal")
        self.btn_down.configure(state="normal")
        self.btn_left.configure(state="normal")
        self.btn_right.configure(state="normal")
        
    def toggle_stream(self):
        """Toggle video stream"""
        if self.stream_running:
            self.stop_stream()
        else:
            self.start_stream()
    
    def start_stream(self):
        """Start RTSP stream"""
        if not self.selected_camera:
            return
            
        try:
            camera = EzvizCamera(self.client, self.selected_camera)
            status = camera.status()
            
            # Get camera IP
            local_ip = status.get('local_ip', '')
            if not local_ip or local_ip == '0.0.0.0':
                messagebox.showerror("Error", "IP kamera tidak valid!\nPastikan kamera dalam jaringan yang sama.")
                return
                
            port = status.get('local_rtsp_port', '554')
            camera_name = status.get('name', 'N/A')
            
            # Show RTSP input dialog
            rtsp_dialog = RTSPInputDialog(self.root, local_ip, port, camera_name)
            
            if not rtsp_dialog.rtsp_url:
                messagebox.showwarning("Cancelled", "Stream dibatalkan.")
                return
            
            rtsp_urls = [rtsp_dialog.rtsp_url]
            
            self.stream_running = True
            self.stream_btn.configure(text="⏸ Stop Stream")
            self.stream_thread = threading.Thread(target=self.stream_worker, 
                                                  args=(rtsp_urls,), daemon=True)
            self.stream_thread.start()
            
        except Exception as e:
            messagebox.showerror("Stream Error", 
                f"Error starting stream:\n{str(e)}\n\n"
                "Solusi:\n"
                "1. Pastikan kamera online\n"
                "2. Restart kamera\n"
                "3. Pastikan password/verification code benar")
    
    def stream_worker(self, rtsp_urls):
        """Worker thread untuk streaming video"""
        cap = None
        connected = False
        last_error = ""
        
        # Coba setiap URL sampai ada yang berhasil
        for idx, rtsp_url in enumerate(rtsp_urls, 1):
            if not self.stream_running:
                break
            
            # Extract info for logging
            try:
                parts = rtsp_url.split('@')
                auth_part = parts[0].split('://')[-1]
                username = auth_part.split(':')[0]
                stream_path = parts[1].split('/', 1)[-1] if len(parts) > 1 else ""
                
                print(f"\n[{idx}/{len(rtsp_urls)}] Trying:")
                print(f"  Username: {username if username else '(empty)'}")
                print(f"  Path: {stream_path}")
            except:
                print(f"\n[{idx}/{len(rtsp_urls)}] Trying connection...")
            
            cap = cv2.VideoCapture(rtsp_url)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Test baca 1 frame untuk cek koneksi (dengan timeout manual)
            import time
            start_time = time.time()
            ret = False
            test_frame = None
            
            # Coba baca frame dengan timeout
            attempt = 0
            while (time.time() - start_time) < 8:  # 8 second timeout
                ret, test_frame = cap.read()
                attempt += 1
                if ret:
                    print(f"  ✓ SUCCESS after {attempt} attempts!")
                    break
                time.sleep(0.1)  # Small delay between attempts
                    
            if ret:
                connected = True
                success_msg = f"Stream terhubung!\n\nFormat: {stream_path}\nUsername: {username if username else '(empty)'}"
                self.root.after(0, lambda msg=success_msg: messagebox.showinfo("Success", msg))
                break
            else:
                cap.release()
                print(f"  ✗ Failed (tried {attempt} times)")
                last_error = f"Format {idx}: {stream_path}"
        
        if not connected:
            error_detail = (
                "Semua format RTSP gagal connect (401 Unauthorized).\n\n"
                "🔧 Solusi yang bisa dicoba:\n\n"
                "1. DISABLE Video Encryption:\n"
                "   • Buka EZVIZ App → Camera Settings\n"
                "   • Device Settings → Video Encryption\n"
                "   • Set ke OFF/Disabled\n\n"
                "2. Enable RTSP:\n"
                "   • Device Settings → Platform Access\n"
                "   • Enable RTSP/ONVIF\n\n"
                "3. Cek di Router:\n"
                "   • Port Forward 554 ke IP kamera\n"
                "   • Atau PC dan kamera di network yang sama\n\n"
                "4. Restart kamera setelah perubahan setting\n\n"
                f"Tested: {len(rtsp_urls)} kombinasi username/path"
            )
            
            self.root.after(0, lambda msg=error_detail: messagebox.showerror(
                "Connection Failed", msg
            ))
            self.root.after(0, self.stop_stream)
            return
        
        # Main streaming loop
        retry_count = 0
        max_retries = 5
        frame_count = 0
        
        while self.stream_running:
            ret, frame = cap.read()
            
            if ret:
                retry_count = 0
                frame_count += 1
                
                # Resize frame
                frame = cv2.resize(frame, (640, 480))
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Convert to PIL Image
                img = Image.fromarray(frame_rgb)
                # Store for snapshot
                self.current_frame = frame_rgb
                # Convert to CTk compatible
                imgtk = ImageTk.PhotoImage(image=img)
                
                # Update label in main thread (every frame)
                if frame_count % 2 == 0:  # Skip frames untuk performance
                    self.root.after(0, lambda img=imgtk: self.update_video_label(img))
            else:
                retry_count += 1
                if retry_count >= max_retries:
                    self.root.after(0, lambda: messagebox.showwarning(
                        "Connection Lost", 
                        "Koneksi ke kamera terputus!"
                    ))
                    self.root.after(0, self.stop_stream)
                    break
        
        if cap:
            cap.release()
        print("Stream stopped")
    
    def update_video_label(self, imgtk):
        """Update video label dengan frame baru"""
        self.video_label.configure(image=imgtk, text="")
        self.video_label.image = imgtk
    
    def stop_stream(self):
        """Stop video stream"""
        self.stream_running = False
        self.stream_btn.configure(text="▶ Start Stream")
        self.video_label.configure(image=None, text="📹\nStream Stopped")
    
    def take_snapshot(self):
        """Ambil snapshot dari stream"""
        if self.current_frame is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"snapshot_{self.selected_camera}_{timestamp}.jpg"
            img = Image.fromarray(self.current_frame)
            img.save(filename)
            messagebox.showinfo("Snapshot", f"Snapshot saved:\n{filename}")
        else:
            messagebox.showwarning("Warning", "No video stream active!")
    
    def move_camera(self, direction):
        """Gerakkan kamera PTZ"""
        if not self.selected_camera:
            return
        try:
            camera = EzvizCamera(self.client, self.selected_camera)
            camera.move(direction, speed=5)
        except Exception as e:
            messagebox.showerror("PTZ Error", f"Error moving camera:\n{str(e)}")
    
    def toggle_alarm(self):
        """Toggle alarm notification"""
        if not self.selected_camera:
            return
        try:
            camera = EzvizCamera(self.client, self.selected_camera)
            camera.alarm_notify(1 if self.alarm_var.get() else 0)
        except Exception as e:
            messagebox.showerror("Error", f"Error toggling alarm:\n{str(e)}")
            self.alarm_var.set(not self.alarm_var.get())
    
    def toggle_audio(self):
        """Toggle audio"""
        if not self.selected_camera:
            return
        try:
            camera = EzvizCamera(self.client, self.selected_camera)
            camera.switch_device_audio(1 if self.audio_var.get() else 0)
        except Exception as e:
            messagebox.showerror("Error", f"Error toggling audio:\n{str(e)}")
            self.audio_var.set(not self.audio_var.get())
    
    def toggle_ir(self):
        """Toggle IR LED"""
        if not self.selected_camera:
            return
        try:
            camera = EzvizCamera(self.client, self.selected_camera)
            camera.switch_device_ir_led(1 if self.ir_var.get() else 0)
        except Exception as e:
            messagebox.showerror("Error", f"Error toggling IR:\n{str(e)}")
            self.ir_var.set(not self.ir_var.get())
    
    def toggle_privacy(self):
        """Toggle privacy mode"""
        if not self.selected_camera:
            return
        try:
            camera = EzvizCamera(self.client, self.selected_camera)
            camera.switch_privacy_mode(1 if self.privacy_var.get() else 0)
        except Exception as e:
            messagebox.showerror("Error", f"Error toggling privacy:\n{str(e)}")
            self.privacy_var.set(not self.privacy_var.get())
    
    def refresh_status(self):
        """Refresh camera status"""
        if self.selected_camera:
            self.select_camera(self.selected_camera)
            messagebox.showinfo("Refresh", "Status updated!")
    
    def reboot_camera(self):
        """Reboot kamera"""
        if not self.selected_camera:
            return
        
        if messagebox.askyesno("Confirm", "Reboot kamera?\nKamera akan offline sementara."):
            try:
                self.client.device_operation(self.selected_camera, "reboot")
                messagebox.showinfo("Reboot", "Reboot command sent!\nKamera akan restart dalam beberapa detik.")
            except Exception as e:
                messagebox.showerror("Error", f"Error rebooting camera:\n{str(e)}")
    
    def run(self):
        """Jalankan aplikasi"""
        self.root.mainloop()


if __name__ == "__main__":
    app = EzvizGUI()
    app.run()
