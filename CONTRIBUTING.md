# Contributing to Perf Tool

Thanks for your interest in contributing! Here's how to get started.

## Development Setup

```bash
git clone https://github.com/artos-n/perf-tool.git
cd perf-tool
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## Project Layout

| File | Purpose |
|------|---------|
| `main.py` | CLI entry point, arg parsing, app bootstrap |
| `monitor.py` | System metrics collection (psutil, pynvml) |
| `overlay.py` | PyQt6 glassmorphism overlay window |
| `widgets.py` | Custom-painted metric cards |
| `config.py` | JSON-based persistent configuration |
| `android/main.py` | Kivy Android app |
| `android/buildozer.spec` | Buildozer APK configuration |

## Running Locally

```bash
python main.py                  # Desktop overlay
cd android && buildozer android debug  # Android APK
```

## Code Style

- Python 3.10+ with type hints
- 120 char line limit
- Docstrings on all public methods
- Run `python -m py_compile main.py` before committing

## Pull Requests

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Test on desktop and/or Android
5. Submit a PR with a clear description

## Issues

Use [GitHub Issues](https://github.com/artos-n/perf-tool/issues) for bugs and feature requests. Include:
- OS / Android version
- Python version
- Steps to reproduce
- Expected vs actual behavior

## License

By contributing, you agree your code will be licensed under the MIT License.
