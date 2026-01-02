# 📹 EZVIZ Camera Monitoring and Controlling

Modern GUI application untuk monitoring dan controlling kamera EZVIZ dengan live RTSP streaming dan full control capabilities.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20linux%20%7C%20macos-lightgrey.svg)

## 📖 Overview

EZVIZ Camera Monitoring and Controlling adalah aplikasi desktop berbasis Python dengan GUI modern untuk:
- 📡 Monitor multiple EZVIZ cameras
- 🎥 Live RTSP video streaming  
- ⚙️ Full camera control (alarm, audio, IR LED, privacy mode, PTZ)
- 📷 Snapshot capture
- 🔒 Secure login (no hardcoded credentials)

Built with `pyezvizapi`, `customtkinter`, and `opencv-python`.

## ✨ Features

### 🔐 Security First
- ✅ **Pop-up Login Dialog** - No hardcoded credentials in code
- ✅ **Session-based Auth** - Credentials only stored in memory
- ✅ **Manual RTSP Input** - User inputs camera password each session
- ✅ **GitHub Safe** - All sensitive data excluded via `.gitignore`

### 📹 Video Streaming
- ✅ **Live RTSP Stream** - Real-time video from camera
- ✅ **Multiple Stream Paths** - Support main/sub streams
- ✅ **4K Support** - Handle high-resolution streams
- ✅ **Snapshot Capture** - Save images from live stream

### 🎛️ Camera Controls
- ✅ **Alarm Notification** - Enable/disable motion alerts
- ✅ **Audio Control** - Toggle camera microphone
- ✅ **IR LED** - Night vision control
- ✅ **Privacy Mode** - Lens cover on/off
- ✅ **PTZ Controls** - Pan/Tilt for supported cameras
- ✅ **Reboot Camera** - Remote restart

### 🖥️ User Interface
- ✅ **Modern Dark Theme** - CustomTkinter based UI
- ✅ **Multi-camera Support** - Manage multiple cameras
- ✅ **Real-time Status** - Live camera info display
- ✅ **Responsive Layout** - Adaptive window sizing

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- EZVIZ account with registered cameras
- Camera and PC on the same local network (for RTSP streaming)

### Installation

1. **Clone repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/ezviz-camera-monitoring.git
   cd ezviz-camera-monitoring
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements_gui.txt
   ```

3. **Run application:**
   ```bash
   python ezviz_gui.py
   ```

## 📱 Usage Guide

### 1. Login

When you start the application, a login dialog will appear:

```
🔐 Login ke EZVIZ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📧 Email: your-email@example.com
🔑 Password: ••••••••••
🌍 Region: Singapore/Asia
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        [Cancel]  [Login]
```

**Supported Regions:**
- Singapore/Asia: `apiisgp.ezvizlife.com`
- Europe: `apiieu.ezvizlife.com`
- United States: `apiius.ezvizlife.com`

### 2. Select Camera

After successful login:
1. Camera list will appear on the left panel
2. Online cameras show 🟢, offline show 🔴
3. Click on a camera to view details

### 3. Start RTSP Stream

To view live video:

1. Click **▶ Start Stream** button
2. RTSP settings dialog will appear:
   ```
   📹 RTSP Stream
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   🎥 Camera Name
   📍 192.168.100.200:554
   
   👤 Username: admin
   🔑 Password: ••••••••••
   📂 Path: /stream1
   
   🔗 Preview:
   rtsp://admin:****@192.168.100.200:554/stream1
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           [Cancel]  [Connect]
   ```

3. Enter your camera's RTSP password
4. Click **Connect**

**Common RTSP Paths:**
- `/stream1` - Main stream (high quality)
- `/stream2` - Sub stream (lower quality, more stable)
- `/h264/ch1/main/av_stream` - H264 format main
- `/Streaming/Channels/101` - Hikvision compatible

### 4. Control Camera

Available controls in the right panel:

| Control | Function |
|---------|----------|
| 🔔 Alarm Notify | Enable/disable motion alerts |
| 🔊 Audio | Toggle camera microphone |
| 🌙 IR LED | Night vision on/off |
| 🔒 Privacy Mode | Physical lens cover |
| ⬆️⬇️⬅️➡️ PTZ | Move camera (if supported) |
| 📷 Snapshot | Capture current frame |
| 🔄 Refresh | Update camera status |
| 🔃 Reboot | Restart camera |

### 5. Snapshot

While streaming:
1. Click **📷 Snapshot** button
2. Image saved as `snapshot_[SERIAL]_[TIMESTAMP].jpg`

## 🔧 Configuration

### Optional Config File

You can create `ezviz_config.json` for CLI testing (NOT required for GUI):

```json
{
  "ezviz": {
    "username": "your-email@example.com",
    "password": "your-password",
    "region": "apiisgp.ezvizlife.com"
  }
}
```

⚠️ **WARNING:** Never commit this file! Already excluded in `.gitignore`.

## 🌐 Remote Access

By default, RTSP streaming requires camera and PC on the same network.

### Option 1: VPN (Recommended)

Use VPN to access your home network remotely:

**Tailscale** (Easiest):
```bash
# Install on both home PC and remote device
# Login once, automatic P2P connection
# No port forwarding needed
```

**WireGuard**:
- Full control over VPN configuration
- Requires port forwarding on router

### Option 2: Port Forwarding

Forward RTSP port on your router:
```
Service: RTSP
External Port: 8554
Internal IP: [Camera IP]
Internal Port: 554
Protocol: TCP
```

⚠️ **Security Risk:** Camera exposed to internet. Use strong password!

## 🐛 Troubleshooting

### Login Failed

**Symptoms:** Cannot login to EZVIZ account

**Solutions:**
1. ✅ Verify email and password are correct
2. ✅ Check internet connection
3. ✅ Try different region server
4. ✅ Ensure account is active on EZVIZ mobile app

### RTSP Stream Failed (401 Unauthorized)

**Symptoms:** Cannot connect to camera stream

**Solutions:**
1. ✅ Verify RTSP password (NOT your EZVIZ account password)
2. ✅ Try different stream paths (`/stream1`, `/stream2`)
3. ✅ Check camera's Video Encryption settings in EZVIZ app
4. ✅ Disable Video Encryption if enabled
5. ✅ Ensure PC and camera on same network

### No Cameras Found

**Symptoms:** Camera list is empty after login

**Solutions:**
1. ✅ Check cameras are online in EZVIZ mobile app
2. ✅ Verify cameras registered to your account
3. ✅ Try refreshing camera list
4. ✅ Re-login to EZVIZ account

### Stream Timeout

**Symptoms:** Video loading but no frames appear

**Solutions:**
1. ✅ Check network connection stability
2. ✅ Try sub-stream instead of main stream
3. ✅ Verify firewall not blocking port 554
4. ✅ Restart camera from EZVIZ app

### PTZ Not Working

**Symptoms:** PTZ buttons don't move camera

**Solutions:**
1. ✅ Verify camera model supports PTZ
2. ✅ Check camera permissions in EZVIZ app
3. ✅ Try refreshing camera status
4. ✅ Some models have limited PTZ API support

## 📂 Project Structure

```
ezviz-camera-monitoring/
├── ezviz_gui.py              # Main GUI application
├── ezviz_test.py             # CLI testing script
├── requirements_gui.txt      # Python dependencies
├── README.md                 # This file
├── .gitignore                # Git ignore rules
└── LICENSE                   # MIT license
```

## 🔒 Security & Privacy

### What's Safe to Share

✅ All Python code files  
✅ README documentation  
✅ Requirements file  
✅ .gitignore file

### What to Keep Private

❌ `ezviz_config.json` - Contains credentials  
❌ Any test files with passwords  
❌ Snapshot images  
❌ VPN configuration files

### Security Features

- **No Hardcoded Credentials** - All sensitive data input via dialogs
- **Session-Only Storage** - Credentials not written to disk
- **HTTPS API** - Communication with EZVIZ cloud uses HTTPS
- **Local RTSP** - Video streams stay on local network

## 🛠️ Development

### Requirements

```python
pyezvizapi>=0.2.2    # EZVIZ cloud API wrapper
customtkinter>=5.2.0  # Modern GUI framework
pillow>=10.0.0        # Image processing
opencv-python>=4.8.0  # Video streaming
```

### API Limitations

**pyEzvizApi Library:**
- ✅ Full control API (switches, PTZ, settings)
- ❌ No cloud streaming API
- ❌ No P2P video connection
- ❌ No direct snapshot API

For video streaming, RTSP protocol is used (requires local network).

### Testing

CLI testing script:
```bash
python ezviz_test.py
```

Features tested:
- ✅ EZVIZ account login
- ✅ Camera discovery
- ✅ Control switches (alarm, audio, IR)
- ✅ Camera status retrieval

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

**Guidelines:**
- ✅ Never commit credentials or config files
- ✅ Follow existing code style
- ✅ Update documentation for new features
- ✅ Test on clean install

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **pyEzvizApi** - EZVIZ API reverse engineering
- **CustomTkinter** - Modern tkinter UI library
- **OpenCV** - Computer vision and video streaming
- **EZVIZ** - Camera hardware and cloud services

## 📧 Support

For issues and questions:

1. Check [Troubleshooting](#-troubleshooting) section
2. Review closed issues on GitHub
3. Open new issue with:
   - OS and Python version
   - Error messages
   - Steps to reproduce

## 🗺️ Roadmap

- [ ] Multi-camera grid view
- [ ] Motion detection alerts
- [ ] Video recording capability
- [ ] Cloud storage integration
- [ ] Mobile app version
- [ ] Docker support
- [ ] Web interface

---

Made with ❤️ for EZVIZ camera users

**Star ⭐ this repo if you find it helpful!**
