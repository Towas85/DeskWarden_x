# 🛡️ DeskWarden — Application Locker for Windows

[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/13500/badge)](https://www.bestpractices.dev/projects/13500)

![DeskWarden Logo](https://github.com/user-attachments/assets/db1db07c-080c-440a-acd7-feea60f4e218)

> Copyright © 2026 Tahasinur Rahman Muntasir. Licensed under the [MIT License](LICENSE).

> **Your PC. Your rules.**
> Lock any app or software with a password — just like your phone, but for Windows.

DeskWarden is a lightweight Windows security software that runs silently in the background and intercepts any app you choose the moment it opens — before it even has a chance to load.

No subscriptions. No account. No cloud. Just install and it works.



## 🎨 UI & Experience

Crafted with a modern Premium interface — every screen, every 
interaction feels deliberate. The Control Panel is clean and 
structured. The lock screen is bold and immersive. 
This is what security software should look like.


---


## 📸 Interface Preview

### Control Panel
![Control Panel](https://github.com/user-attachments/assets/573296fe-c752-4c7e-8792-a75e9f39b6ef)

### Password Protection
![Lock Screen](https://github.com/user-attachments/assets/01bc5722-cb09-4983-afde-c92c4b550150)

### Access Denied
![Block Notice](https://github.com/user-attachments/assets/1637648d-4125-461b-a36d-5c1648c2a03d)


---

## 💡 Why DeskWarden?

Ever wished you could lock Chrome, a game, or any application on your PC — the same way you lock apps on your phone?

Windows doesn't have this built-in. Most solutions are either paid, require technical setup, or just hide the window instead of truly blocking the software.

**DeskWarden actually freezes the process** at the kernel level. The app cannot open, cannot run, and cannot be bypassed — until the correct password is entered.

- ✅ Free and open source
- ✅ No technical knowledge needed — one double-click to install
- ✅ Works on any software or `.exe` — browsers, games, tools, anything
- ✅ Lightweight — no Electron, no heavy runtime, no background bloat

---

## ✨ What It Can Do

- 🔒 **Lock any app with a password** — the app freezes instantly on launch
- 🖥️ **Fullscreen lock screen** — clean, unbypassable, appears in under a second
- 🔁 **Four lock modes** per app — full flexibility:
  - **Ask Always** — password required every single time
  - **Session Once** — ask once, remember until PC restart
  - **Always Block** — permanently blocked, no password option
  - **None** — tracked but unrestricted, switch modes anytime
- 🚫 **Wrong password = app killed** — no way around it
- 🔑 **Multi-Factor Password Recovery** — reset forgotten passwords using an Emergency Recovery Key or Email OTP
- 🔍 **Live App Search Bar** — quickly find and filter through your protected applications
- 🔐 **SHA-256 password hashing** — your password is never stored in plain text
- ⏱️ **Brute-force protection** — locked out after 3 wrong attempts
- 💾 **Encrypted Backup & Restore** — export and import your entire setup with AES-256-GCM `.deskwarden` containers
- 🔄 **Auto-update** — checks for new versions with in-app release notes & direct download
- 📋 **Security Log** — full history of every unlock and failed attempt
- 🚀 **Starts with Windows** — always running, always protecting

---

## 📦 Installation

> No Python knowledge required. The installer handles everything.

1. Go to the [Releases](https://github.com/muntasir018/DeskWarden/releases) page and download the latest version
2. Extract the zip file anywhere
3. Right-click `install_deskwarden.bat` → **Run as administrator**
4. Done — DeskWarden installs itself, creates shortcuts, and starts automatically

**What the installer does behind the scenes:**
- Detects and installs Python automatically if not found
- Downloads and installs all required packages with a real-time progress bar
- Copies everything to `C:\Program Files\DeskWarden`
- Creates Desktop and Start Menu shortcuts
- Registers itself to start on Windows login
- Launches DeskWarden immediately

---

## 🚀 Getting Started

1. After installation, find the **DeskWarden icon in your system tray** (bottom-right corner)
2. Double-click the desktop shortcut or right-click the tray icon → **Control Panel**
3. Set your master password and emergency recovery options on the first run setup wizard

---

## 🔒 How to Lock an Application

Locking any software, browser, tool, or game on your PC takes just a few clicks:

1. **Open Control Panel** — Launch DeskWarden from your Desktop shortcut or right-click the system tray icon → **Control Panel**.
2. **Add Your Application** — Click **`＋ Add App`** and use either of the 2 easy methods:
   - **Method 1 (Direct Browse):** Click **`＋ Add App`** → Browse and select any `.exe` file or Desktop shortcut (`.lnk`).
   - **Method 2 (Windows Search / Copy Path):** Search the app in Windows Start Menu → Right-click → **Open file location** → Right-click the shortcut/exe → Click **Copy as path** → Click **`＋ Add App`** in DeskWarden, paste (**Ctrl+V**) into the File name box, and click **Open**.
3. **Choose Lock Mode** — Select your preferred protection level:
   - **Ask Always** *(Recommended)*: Requires your master password every single time the app is opened.
   - **Session Once**: Requires password once per Windows login session.
   - **Always Block**: Keeps the app completely blocked from opening.
4. **Done!** — From now on, whenever that application is launched, DeskWarden instantly intercepts it and presents the secure lock screen.

---

## 🗑️ Uninstallation

1. Right-click `uninstall_deskwarden.bat` → **Run as administrator**
2. Follow the steps — optionally keep or delete your settings

---

## ⚠️ Known Limitations

- Games with **kernel-level anti-cheat** (EAC, BattlEye) may resist process suspension
- Some **UWP / Microsoft Store** apps have non-standard process structures and may not work correctly

---

## 📁 File Locations

| File | Location |
|------|----------|
| Settings | `%APPDATA%\DeskWarden\config.json` |
| Security Log | `%APPDATA%\DeskWarden\security_log.json` |
| Diagnostic Log | `%APPDATA%\DeskWarden\diagnostic_log.txt` |
| Crash Log | `%APPDATA%\DeskWarden\crash_log.txt` |

---

## 🔧 Requirements

- Windows 10 or 11 (64-bit)
- Python 3.10+ *(installer handles this automatically)*

---

## 📄 License

This project is licensed under the MIT License.
You are free to use, modify, and distribute this software.
Attribution to the original author must be preserved in all copies.

> Built with ❤️ by [Tahasinur Rahman Muntasir](https://github.com/muntasir018)
