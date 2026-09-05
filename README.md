# 📋 Universal Clipboard Sync (Windows ⇄ macOS)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Cross-Platform](https://img.shields.io/badge/Platform-Windows%20%E2%87%84%20macOS-informational.svg)]()
[![P2P Network](https://img.shields.io/badge/Architecture-P2P%20Local%20Wi--Fi-success.svg)]()
[![Zero Config](https://img.shields.io/badge/Discovery-UDP%20Broadcast-orange.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Blazing fast, private peer-to-peer clipboard synchronization between Windows and macOS.** Seamlessly shares text, code snippets, URLs, screenshots, and image files over your local Wi-Fi network without third-party cloud servers or account sign-ups.

---

| Capability | What's Covered |
| :--- | :--- |
| **⚡ Zero-Click Sync** | `Ctrl + C` on Windows (text or Snipping Tool screenshot) ➔ instantly `Cmd + V` on macOS. `Cmd + C` on Mac ➔ instantly `Ctrl + V` on Windows. |
| **📡 Zero-Configuration Autodiscovery** | Devices discover each other within one second via local UDP network beacons. No static IP addresses or router port forwarding required. |
| **🔄 Loop Prevention Engine** | Cryptographic SHA-256 state hashing and timestamp tracking prevents infinite clipboard ping-pong and reflection loops. |
| **🖼 Image & Binary Support** | Synchronizes raw clipboard images (PNG, JPEG, bitmap) as well as multiline formatting and code blocks without distortion. |
| **🌐 Glassmorphic Web Dashboard** | Local web control center (`http://localhost:7890`) with drag-and-drop file upload, clipboard history, text sender, and live node status. |
| **🪟 Background Daemons & Tray** | Native background execution via Windows VBScript/Tray icon and macOS LaunchAgents. |

---

## 🏗 System Architecture

```
   ┌─────────────────────────────────────────────────────────────┐
   │                     Local Wi-Fi Network                     │
   └─────────────────────────────────────────────────────────────┘
                  ▲                               ▲
     UDP Beacon   │                               │   UDP Beacon
    Autodiscovery │                               │  Autodiscovery
                  ▼                               ▼
      ┌───────────────────────┐       ┌───────────────────────┐
      │     Windows 10/11     │       │      macOS Node       │
      │───────────────────────│       │───────────────────────│
      │ • Win32 Clipboard API │  P2P  │ • NSPasteboard / App  │
      │ • SHA-256 Dedup Ring  │ ◄───► │ • SHA-256 Dedup Ring  │
      │ • Local FastAPI / WS  │ HTTP  │ • Local FastAPI / WS  │
      │ • System Tray Icon    │       │ • Menu Bar / Daemon   │
      └───────────────────────┘       └───────────────────────┘
```

---

## ⚡ Quick Start

### 🪟 Windows 10 / 11

```bash
# 1. Clone repository
git clone https://github.com/Molyn597/universal-clipboard-sync.git
cd universal-clipboard-sync

# 2. Launch (creates virtual environment and installs packages automatically)
run.bat

# Or run silently in the background
# Double-click "Universal Clipboard.vbs"
```

### 🍎 macOS

```bash
# 1. Clone repository
git clone https://github.com/Molyn597/universal-clipboard-sync.git
cd universal-clipboard-sync

# 2. Make scripts executable and run setup
chmod +x *.sh
./mac_setup.sh

# 3. Start background sync
./run_mac.sh
```

Once running on both devices connected to the same Wi-Fi, clipboard sync activates automatically. Open `http://localhost:7890` in your browser to inspect connected peers and clipboard history.

---

## 🕹 Service Management

| Platform | Action | Command / Script |
| :--- | :--- | :--- |
| **Windows** | Start with terminal | `run.bat` |
| **Windows** | Start silently | Double-click `Universal Clipboard.vbs` |
| **Windows** | Stop background service | `stop_windows.bat` |
| **macOS** | Start service | `./run_mac.sh` |
| **macOS** | Stop service | `./stop_mac.sh` |
| **macOS** | Build standalone app | `./build_mac_app.sh` |

---

## 🛡️ Privacy & Security

- **Direct Peer-to-Peer**: Data never touches the public internet. All traffic stays strictly within your private local subnet.
- **In-Memory Buffer**: Clipboard contents are cached in temporary volatile memory and discarded upon service shutdown.

---

## 📄 License
MIT License — see [LICENSE](LICENSE) for details. Built by [Molyn597](https://github.com/Molyn597).
