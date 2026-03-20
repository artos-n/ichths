"""
Perf Tool — System Metrics Collection Engine
"""
import time
import threading
import psutil
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CPUMetrics:
    usage_percent: float = 0.0
    per_core: list = field(default_factory=list)
    frequency_mhz: float = 0.0
    temperature_c: Optional[float] = None
    core_count: int = 0
    thread_count: int = 0


@dataclass
class GPUMetrics:
    available: bool = False
    name: str = ""
    usage_percent: float = 0.0
    memory_used_mb: float = 0.0
    memory_total_mb: float = 0.0
    memory_percent: float = 0.0
    temperature_c: Optional[float] = None
    fan_percent: Optional[float] = None
    power_w: Optional[float] = None


@dataclass
class RAMMetrics:
    usage_percent: float = 0.0
    used_gb: float = 0.0
    total_gb: float = 0.0
    available_gb: float = 0.0


@dataclass
class NetworkMetrics:
    download_mbps: float = 0.0
    upload_mbps: float = 0.0
    bytes_recv: int = 0
    bytes_sent: int = 0
    ping_ms: Optional[float] = None


@dataclass
class FPSMetrics:
    fps: int = 0
    frame_time_ms: float = 0.0
    avg_fps: int = 0
    min_fps: int = 0
    max_fps: int = 0


@dataclass
class TempMetrics:
    cpu_c: Optional[float] = None
    gpu_c: Optional[float] = None
    max_cpu_c: Optional[float] = None
    max_gpu_c: Optional[float] = None


@dataclass
class SystemSnapshot:
    """Complete snapshot of all system metrics at a point in time."""
    cpu: CPUMetrics = field(default_factory=CPUMetrics)
    gpu: GPUMetrics = field(default_factory=GPUMetrics)
    ram: RAMMetrics = field(default_factory=RAMMetrics)
    network: NetworkMetrics = field(default_factory=NetworkMetrics)
    fps: FPSMetrics = field(default_factory=FPSMetrics)
    temps: TempMetrics = field(default_factory=TempMetrics)
    timestamp: float = 0.0


class SystemMonitor:
    """
    Collects system metrics in a background thread.
    Uses psutil for CPU/RAM/network and tries GPUtil + nvidia-ml-py for GPU.
    """

    def __init__(self, refresh_interval: float = 1.0):
        self.refresh_interval = refresh_interval
        self.snapshot = SystemSnapshot()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._gpu_available = False
        self._gpu_handle = None
        self._prev_net = None
        self._prev_time = None
        self._fps_history: list[int] = []
        self._max_cpu_temp: Optional[float] = None
        self._max_gpu_temp: Optional[float] = None

        # Initialize CPU baseline (first call returns 0)
        psutil.cpu_percent(percpu=True)
        psutil.cpu_percent()
        time.sleep(0.05)

        # Try GPU init
        self._init_gpu()

    def _init_gpu(self):
        """Try to initialize NVIDIA GPU monitoring via pynvml."""
        try:
            import pynvml
            pynvml.nvmlInit()
            self._gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            self._gpu_available = True
            self._pynvml = pynvml
        except Exception:
            self._gpu_available = False

    def _collect_cpu(self) -> CPUMetrics:
        per_core = psutil.cpu_percent(percpu=True)
        overall = psutil.cpu_percent()
        freq = psutil.cpu_freq()

        temp = None
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for name, entries in temps.items():
                    if "core" in name.lower() or "cpu" in name.lower() or "tctl" in name.lower():
                        temp = entries[0].current
                        break
                if temp is None:
                    # Fallback: take the first available
                    for entries in temps.values():
                        if entries:
                            temp = entries[0].current
                            break
        except Exception:
            pass

        if temp is not None:
            if self._max_cpu_temp is None or temp > self._max_cpu_temp:
                self._max_cpu_temp = temp

        return CPUMetrics(
            usage_percent=overall,
            per_core=per_core,
            frequency_mhz=freq.current if freq else 0,
            temperature_c=temp,
            core_count=psutil.cpu_count(logical=False) or 0,
            thread_count=psutil.cpu_count(logical=True) or 0,
        )

    def _collect_gpu(self) -> GPUMetrics:
        if not self._gpu_available:
            return GPUMetrics()

        try:
            pynvml = self._pynvml
            handle = self._gpu_handle

            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
            name = pynvml.nvmlDeviceGetName(handle)
            if isinstance(name, bytes):
                name = name.decode()

            temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)

            fan = None
            try:
                fan = pynvml.nvmlDeviceGetFanSpeed(handle)
            except Exception:
                pass

            power = None
            try:
                power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0  # mW to W
            except Exception:
                pass

            if self._max_gpu_temp is None or temp > self._max_gpu_temp:
                self._max_gpu_temp = temp

            return GPUMetrics(
                available=True,
                name=name,
                usage_percent=util.gpu,
                memory_used_mb=mem.used / (1024 ** 2),
                memory_total_mb=mem.total / (1024 ** 2),
                memory_percent=(mem.used / mem.total) * 100 if mem.total > 0 else 0,
                temperature_c=temp,
                fan_percent=fan,
                power_w=power,
            )
        except Exception:
            return GPUMetrics()

    def _collect_ram(self) -> RAMMetrics:
        mem = psutil.virtual_memory()
        return RAMMetrics(
            usage_percent=mem.percent,
            used_gb=mem.used / (1024 ** 3),
            total_gb=mem.total / (1024 ** 3),
            available_gb=mem.available / (1024 ** 3),
        )

    def _collect_network(self) -> NetworkMetrics:
        counters = psutil.net_io_counters()
        now = time.time()

        dl = 0.0
        ul = 0.0
        if self._prev_net and self._prev_time:
            dt = now - self._prev_time
            if dt > 0:
                dl = (counters.bytes_recv - self._prev_net.bytes_recv) / dt / (1024 ** 2) * 8  # Mbps
                ul = (counters.bytes_sent - self._prev_net.bytes_sent) / dt / (1024 ** 2) * 8

        self._prev_net = counters
        self._prev_time = now

        return NetworkMetrics(
            download_mbps=max(0, dl),
            upload_mbps=max(0, ul),
            bytes_recv=counters.bytes_recv,
            bytes_sent=counters.bytes_sent,
        )

    def _collect_temps(self) -> TempMetrics:
        return TempMetrics(
            cpu_c=self._collect_cpu().temperature_c if self.snapshot.cpu.temperature_c is None else self.snapshot.cpu.temperature_c,
            gpu_c=self._collect_gpu().temperature_c if not self._gpu_available else None,
            max_cpu_c=self._max_cpu_temp,
            max_gpu_c=self._max_gpu_temp,
        )

    def _collect_loop(self):
        while self._running:
            cpu = self._collect_cpu()
            gpu = self._collect_gpu()
            ram = self._collect_ram()
            net = self._collect_network()
            temps = TempMetrics(
                cpu_c=cpu.temperature_c,
                gpu_c=gpu.temperature_c if gpu.available else None,
                max_cpu_c=self._max_cpu_temp,
                max_gpu_c=self._max_gpu_temp,
            )

            with self._lock:
                self.snapshot = SystemSnapshot(
                    cpu=cpu,
                    gpu=gpu,
                    ram=ram,
                    network=net,
                    fps=self.snapshot.fps,  # FPS updated externally
                    temps=temps,
                    timestamp=time.time(),
                )

            time.sleep(self.refresh_interval)

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._collect_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=3)

    def get_snapshot(self) -> SystemSnapshot:
        with self._lock:
            return self.snapshot

    def report_fps(self, fps: int):
        """External FPS injection (e.g., from a game hook or manual counter)."""
        with self._lock:
            self._fps_history.append(fps)
            if len(self._fps_history) > 120:
                self._fps_history = self._fps_history[-120:]

            avg = sum(self._fps_history) / len(self._fps_history) if self._fps_history else 0
            self.snapshot.fps = FPSMetrics(
                fps=fps,
                frame_time_ms=1000.0 / fps if fps > 0 else 0,
                avg_fps=int(avg),
                min_fps=min(self._fps_history) if self._fps_history else 0,
                max_fps=max(self._fps_history) if self._fps_history else 0,
            )
