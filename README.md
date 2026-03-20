# Gaming Performance Monitor

A real-time gaming performance overlay with **glassmorphism** UI, inspired by iOS's frosted glass aesthetic.

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-green.svg)

## Features

- 🎮 **FPS Counter** — Real-time frame rate monitoring
- 📊 **CPU Monitor** — Usage per core, frequency, temperature
- 🎮 **GPU Monitor** — Usage, VRAM, temperature (NVIDIA/AMD)
- 🧠 **RAM Monitor** — Memory usage with breakdown
- 🌐 **Network** — Upload/download speeds, ping
- 🌡️ **Temperature** — System thermal monitoring
- 🪟 **Glassmorphism UI** — Frosted glass overlay (iOS-style)
- 🖱️ **Draggable & Resizable** — Position anywhere on screen
- ⚡ **Low Overhead** — Minimal impact on gaming performance

## Screenshot

```
┌─────────────────────────────────┐
│ ╭─────────────────────────────╮ │
│ │  🎮  144 FPS               │ │
│ │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░ 87%   │ │
│ ├─────────────────────────────┤ │
│ │  CPU  ▓▓▓▓▓▓▓░░░░░░  45%  │ │
│ │  GPU  ▓▓▓▓▓▓▓▓▓░░░░  62%  │ │
│ │  RAM  ▓▓▓▓▓▓░░░░░░░  38%  │ │
│ │  NET  ↓ 12.3  ↑ 2.1 Mbps  │ │
│ ╰─────────────────────────────╯ │
└─────────────────────────────────┘
```

## Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/gaming-monitor.git
cd gaming-monitor

# Install dependencies
pip install -r requirements.txt

# Run the overlay
python main.py
```

## Requirements

- Python 3.10+
- Windows 10/11 (primary), Linux (partial), macOS (partial)
- For GPU monitoring: NVIDIA drivers (nvml) or AMD drivers

## Usage

```bash
# Run with default settings
python main.py

# Run with custom position
python main.py --x 100 --y 100

# Run in compact mode
python main.py --compact

# Run with custom refresh rate (ms)
python main.py --refresh 500

# Toggle modules
python main.py --no-gpu --no-network
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `F9` | Toggle visibility |
| `F10` | Cycle opacity |
| `F11` | Toggle compact mode |
| `Ctrl+Q` | Quit |
| `Ctrl+R` | Reset position |

## Architecture

```
gaming-monitor/
├── main.py              # Entry point & CLI
├── monitor.py           # System metrics collection
├── overlay.py           # Glassmorphism overlay window
├── widgets.py           # Individual metric widgets
├── config.py            # Configuration & settings
├── requirements.txt     # Dependencies
└── README.md            # This file
```

## Configuration

Settings are saved to `~/.gaming-monitor/config.json` and persist across sessions.

## Contributing

Contributions welcome! Please open an issue first to discuss what you'd like to change.

## License

MIT
