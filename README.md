# Perf Tool

<div align="center">

![Perf Tool Banner](https://img.shields.io/badge/Perf_Tool-🎮_Performance_Monitoring-blue?style=for-the-badge)
![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Android](https://img.shields.io/badge/Android-8.0%2B-3DDC84?logo=android&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**A real-time performance overlay for gamers.**

Glassmorphism UI. CPU, GPU, RAM, FPS, network — everything at a glance.

[Features](#features) · [Installation](#installation) · [Android](#android) · [Configuration](#configuration) · [Contributing](#contributing)

</div>

---

## Features

| Module | Desktop | Android |
|--------|:-------:|:-------:|
| **FPS Counter** — real-time frame rate with color-coded badges | ✅ | ✅ |
| **CPU Monitor** — usage, per-core, frequency, temperature | ✅ | ✅ |
| **GPU Monitor** — NVIDIA usage, VRAM, temp, fan speed | ✅ | ⬜ |
| **RAM Monitor** — usage, used/total breakdown | ✅ | ✅ |
| **Network** — download/upload speeds in Mbps | ✅ | ✅ |
| **Glassmorphism UI** — frosted glass, always-on-top overlay | ✅ | ✅ |
| **Draggable & Resizable** — position anywhere on screen | ✅ | — |
| **Keyboard Shortcuts** — quick toggle and opacity control | ✅ | — |

## Screenshot

```
 ┌──────────────────────────────────┐
 │  PERFORMANCE MONITOR    144 FPS  │
 │                                  │
 │  ⚡  CPU                         │
 │  45%  ▓▓▓▓▓▓▓▓░░░░░░░░░░        │
 │       3.8 GHz │ 62°C             │
 │                                  │
 │  🎮  GPU                         │
 │  62%  ▓▓▓▓▓▓▓▓▓▓░░░░░░░░        │
 │       2.1/8.0 GB │ 71°C         │
 │                                  │
 │  🧠  RAM                         │
 │  38%  ▓▓▓▓▓▓▓░░░░░░░░░░░        │
 │       6.1/16.0 GB               │
 │                                  │
 │  ⬇ 12.3 Mbps    ⬆ 2.1 Mbps     │
 └──────────────────────────────────┘
```

## Installation

### Desktop (Windows / Linux / macOS)

```bash
git clone https://github.com/artos-n/perf-tool.git
cd perf-tool
pip install -r requirements.txt
python main.py
```

### Android

Download the latest APK from [Releases](https://github.com/artos-n/perf-tool/releases) and sideload to your device.

**Requires:** Android 8.0+ (API 26)

## Usage

```bash
# Default — all modules enabled
python main.py

# Custom position
python main.py --x 100 --y 200

# Compact mode (CPU + FPS only)
python main.py --compact

# Custom refresh rate
python main.py --refresh 500

# Adjust opacity
python main.py --opacity 0.9

# Disable specific modules
python main.py --no-gpu --no-network
```

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `F9` | Toggle visibility |
| `F10` | Cycle opacity (50% → 100%) |
| `F11` | Toggle compact mode |
| `Ctrl+Q` | Quit |
| `Ctrl+R` | Reset position to default |
| `Double-click` | Toggle compact mode |
| `Right-click` | Context menu |

## Configuration

Settings persist to `~/.perf-tool/config.json` across sessions.

```json
{
  "x": 20,
  "y": 20,
  "width": 320,
  "height": 380,
  "opacity": 0.82,
  "refresh_ms": 1000,
  "show_cpu": true,
  "show_gpu": true,
  "show_ram": true,
  "show_network": true
}
```

## Project Structure

```
perf-tool/
├── main.py                 # Entry point & CLI
├── monitor.py              # System metrics engine
├── overlay.py              # Glassmorphism overlay window
├── widgets.py              # Metric card widgets
├── config.py               # Configuration management
├── android/
│   ├── main.py             # Kivy Android app
│   ├── buildozer.spec      # Android build config
│   └── assets/             # App icons & splash screen
├── .github/
│   └── workflows/
│       └── build-apk.yml   # Automated APK builds
├── requirements.txt
├── LICENSE
└── README.md
```

## Building the APK

The project includes a GitHub Actions workflow that automatically builds the Android APK on every push to `main`.

To build locally:

```bash
cd android
pip install buildozer
buildozer android debug
```

## Tech Stack

- **Desktop:** Python 3.10+, PyQt6, psutil, pynvml
- **Android:** Kivy, Buildozer, psutil
- **CI/CD:** GitHub Actions

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

[MIT](LICENSE) © 2026 artos
