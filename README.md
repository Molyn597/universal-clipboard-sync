# 📋 Universal Clipboard (Windows ⇄ macOS)

[![Latest release](https://img.shields.io/github/v/release/Molyn597/universal-clipboard-sync)](https://github.com/Molyn597/universal-clipboard-sync/releases/latest)
[![Cross-Platform](https://img.shields.io/badge/Platform-Windows%20%E2%87%84%20macOS-informational.svg)]()
[![P2P Network](https://img.shields.io/badge/Architecture-P2P%20Local%20Wi--Fi-success.svg)]()
[![Encrypted](https://img.shields.io/badge/Traffic-Encrypted-blueviolet.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Private peer-to-peer clipboard sync between Windows and macOS.** Copy text, links, code, screenshots, files or whole folders on one computer and paste them on the other – over your local Wi-Fi, encrypted, without any cloud service or account.

---

## ⬇️ Download & install

Get the latest version from **[Releases](https://github.com/Molyn597/universal-clipboard-sync/releases/latest)**.

### 🪟 Windows 10 / 11

1. Download `Universal-Clipboard-Setup-<version>.exe` and run it (no admin rights needed).
2. Optionally tick *Start automatically after sign-in* and *Create a desktop shortcut*.

> The app is not code-signed. If Windows shows *“Windows protected your PC”*, click **More info → Run anyway** (only the first time).

### 🍎 macOS (Apple Silicon)

Open Terminal and run:

```bash
curl -fsSL https://raw.githubusercontent.com/Molyn597/universal-clipboard-sync/main/install_mac.sh | bash
```

It downloads the latest `.dmg`, installs the app into *Applications* and starts it – without a Gatekeeper warning.

> If you download the `.dmg` manually in a browser, macOS blocks the unsigned app. After dragging it into *Applications*, run
> `xattr -dr com.apple.quarantine "/Applications/Universal Clipboard.app"` or allow it in *System Settings → Privacy & Security → Open Anyway*.

### 🔑 Pair your devices

Both devices must be on the same Wi-Fi and share the same pairing code:

1. On the first device open **Zařízení** (Devices) and click **Kopírovat** (Copy) next to *Kód tohoto zařízení*.
2. On the second device paste it into **Kód z druhého zařízení** and click **Spárovat** (Pair).

Within a few seconds the bridge at the top of the **Schránka** (Clipboard) view shows *Tento PC — propojeno — MacBook*. The app UI is in Czech.

---

## ✨ Features

| Capability | What it does |
| :--- | :--- |
| **⚡ Automatic sync** | `Ctrl + C` on Windows ➔ `Cmd + V` on the Mac and back. Text, links, code, screenshots and images. |
| **📁 Files & folders** | Copied files and folders (up to 25 MB) arrive as real files – paste them in Explorer/Finder. Received files are saved to *Downloads/Universal Clipboard* or a folder you choose. |
| **💬 Conversation timeline** | Received items on the left, sent items on the right, oldest at the top, newest at the bottom – each with the device name and time. Filter by received / sent / pinned and search. |
| **🖼 Rich previews** | Thumbnails for screenshots and images, first page of PDFs, snippets of text files, formatted links and code, typed tiles for other files. |
| **🔍 In-app viewer** | Open images, every page of a PDF, text and code, audio, video or folder contents right in the app; open in the default app or reveal in the folder. |
| **🗂 Files page** | Browse all received and sent files with thumbnails; copy, resend, reveal or open them. |
| **📤 Drag & drop and composer** | Drop files anywhere into the window or type a text message and send it to all devices. |
| **🔄 Automatic updates** | The app checks GitHub Releases on start and every 6 hours and installs a new version with one click (download is verified with SHA-256). |
| **⏸ Pause & notifications** | Pause syncing with one click (sidebar or tray), get system notifications for incoming items. |
| **🌗 Look & feel** | Rounded frameless window, dark and light theme, Windows tray icon, closing the window keeps syncing in the background. |

---

## 🔄 Updating

The app updates itself: when a new version is available a green **Aktualizovat** (Update) button appears in the title bar, or use *Nastavení → Zkontrolovat* (Settings → Check). One click downloads, verifies and installs it, then restarts the app.

On macOS you can always reinstall the latest version with the `install_mac.sh` command above. Pairing, history and settings are kept.

---

## 🏗 How it works

```
   ┌─────────────────────────────────────────────────────────────┐
   │                     Local Wi-Fi network                     │
   └─────────────────────────────────────────────────────────────┘
          ▲  encrypted UDP beacons (discovery)  ▲
          ▼                                     ▼
 ┌─────────────────────────┐   encrypted   ┌─────────────────────────┐
 │      Windows 10/11      │   HTTP sync   │          macOS          │
 │─────────────────────────│ ◄───────────► │─────────────────────────│
 │ Win32 clipboard API     │               │ NSPasteboard (PyObjC)   │
 │ aiohttp server + WS     │               │ aiohttp server + WS     │
 │ pywebview window + tray │               │ pywebview window + Dock │
 └─────────────────────────┘               └─────────────────────────┘
```

- **Discovery:** every device broadcasts a sealed beacon every 2 s; only devices with the same pairing code can read it.
- **Loop prevention:** the OS clipboard change counter (Windows sequence number / `NSPasteboard.changeCount`) tells the app which changes it made itself, so received items are never echoed back. Content hashes (pixels for images, normalised line endings for text, file contents for files) are a second safety net.
- **Files:** contents are packed (folders as zip), encrypted and sent; the receiver unpacks them into the receive folder and puts them on the clipboard as real files.

---

## 🛡️ Privacy & security

- **Local only:** data never leaves your local network; there is no server or account.
- **Encrypted & authenticated:** beacons and clipboard payloads are sealed with Fernet (AES-128-CBC + HMAC-SHA256) derived from the pairing code. Devices without the code can't read, inject or even see your clipboard; messages older than 120 s are rejected.
- **Localhost-only UI:** the dashboard API only answers `127.0.0.1`, rejects cross-origin requests and foreign `Host` headers (DNS rebinding). The file viewer can only open the receive/sent folders and files from your history.
- **Pairing code** is never synced or written to history. Treat it like a password.
- **Stored data:** history (up to 50 unpinned items plus pinned ones), settings and the pairing code are kept on your computer – clear history any time in *Nastavení* (Settings).

| What | Windows | macOS |
| :--- | :--- | :--- |
| Settings, history, pairing code, log | `%APPDATA%\Universal Clipboard` | `~/Library/Application Support/Universal Clipboard` |
| Received files (default) | `Downloads\Universal Clipboard` | `~/Downloads/Universal Clipboard` |
| App | `%LOCALAPPDATA%\Programs\Universal Clipboard` | `/Applications/Universal Clipboard.app` |

---

## 🛠 Development

Requires Python 3.11+.

```bash
git clone https://github.com/Molyn597/universal-clipboard-sync.git
cd universal-clipboard-sync

# Run from source (creates a venv and installs requirements)
run.bat            # Windows
./run_mac.sh       # macOS

# Clipboard round-trip tests (use the real OS clipboard)
python -m pytest tests

# Build the app locally
pyinstaller --noconfirm universal_clipboard.spec
```

- Set `UNIVERSAL_CLIPBOARD_DATA_DIR` to keep a development instance's history and settings apart from the installed app; `CLIPBOARD_SYNC_KEY` overrides the pairing code.
- `stop_windows.bat` / `stop_mac.sh` stop a running instance.
- **Releasing:** bump `__version__` in `version.py`, commit, then push a tag `vX.Y.Z`. GitHub Actions runs the macOS clipboard tests, builds the Windows installer (Inno Setup) and the macOS `.dmg`, and publishes the release with `checksums.txt` – installed apps pick it up automatically.

---

## 📄 License

MIT License – see [LICENSE](LICENSE) for details. Built by [Molyn597](https://github.com/Molyn597).
