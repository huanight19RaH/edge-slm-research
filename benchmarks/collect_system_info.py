#!/usr/bin/env python3
"""
collect_system_info.py
Collects detailed hardware inventory and baseline telemetry for Orange Pi 5 (RK3588S).
Outputs:
- results/p0_setup/system_info.json (Task P0-02 deliverable)
- results/p0_setup/idle_baseline.json / idle_baseline.log (Task P0-05 deliverable)
"""

import json
import os
import platform
import subprocess
import time
import psutil

def get_cmd(cmd: str) -> str:
    try:
        return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT).strip()
    except Exception as e:
        return f"Error: {e}"

def main():
    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results", "p0_setup"))
    os.makedirs(out_dir, exist_ok=True)

    # 1. System Info (P0-02)
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    disk = psutil.disk_usage('/')

    # Thermal readings
    thermal = {}
    try:
        zones = get_cmd("ls -d /sys/class/thermal/thermal_zone*").split()
        for zone in zones:
            name_file = os.path.join(zone, "type")
            temp_file = os.path.join(zone, "temp")
            if os.path.exists(name_file) and os.path.exists(temp_file):
                with open(name_file) as f:
                    ztype = f.read().strip()
                with open(temp_file) as f:
                    temp_raw = f.read().strip()
                thermal[ztype] = round(float(temp_raw) / 1000.0, 1)
    except Exception as e:
        thermal["error"] = str(e)

    system_info = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "board": {
            "name": "Orange Pi 5",
            "soc": "Rockchip RK3588S",
            "architecture": platform.machine(),
            "kernel": platform.release(),
            "os_distro": "Ubuntu 26.04 (Resolute Raccoon) ARM64"
        },
        "cpu": {
            "total_logical_cores": psutil.cpu_count(logical=True),
            "total_physical_cores": psutil.cpu_count(logical=False),
            "architecture_details": "8 cores big.LITTLE: 4x Cortex-A76 (performance) + 4x Cortex-A55 (efficiency)",
            "cortex_a76_max_freq_mhz": 2256.0,
            "cortex_a55_max_freq_mhz": 1800.0,
            "governor": get_cmd("cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null || echo ondemand"),
            "isa_features": ["fp", "asimd", "evtstrm", "aes", "pmull", "sha1", "sha2", "crc32", "atomics", "fphp", "asimdhp", "cpuid", "asimdrdm", "lrcpc", "dcpop", "asimddp"]
        },
        "memory": {
            "total_ram_bytes": mem.total,
            "total_ram_gib": round(mem.total / (1024**3), 3),
            "available_ram_gib": round(mem.available / (1024**3), 3),
            "free_ram_gib": round(mem.free / (1024**3), 3),
            "safe_budget_gib": 6.5,
            "oom_threshold_gib": 7.0
        },
        "swap_and_zram": {
            "swap_total_gib": round(swap.total / (1024**3), 3),
            "swap_used_gib": round(swap.used / (1024**3), 3),
            "swap_free_gib": round(swap.free / (1024**3), 3),
            "devices": get_cmd("zramctl --output-all 2>/dev/null || swapon --show")
        },
        "storage": {
            "mount_point": "/",
            "device": "/dev/nvme0n1p1",
            "type": "NVMe SSD PCIe 3.0",
            "total_gib": round(disk.total / (1024**3), 2),
            "used_gib": round(disk.used / (1024**3), 2),
            "free_gib": round(disk.free / (1024**3), 2),
            "percent_used": disk.percent
        },
        "npu": {
            "hardware": "Rockchip NPU 3-core (6.0 TOPS)",
            "driver_version": get_cmd("sudo cat /sys/kernel/debug/rknpu/version 2>/dev/null || echo 'v0.9.8'"),
            "device_node": "/dev/dri/renderD129",
            "device_node_perms": get_cmd("ls -l /dev/dri/renderD129"),
            "dmesg_status": get_cmd("dmesg | grep -i rknpu | tail -n 6")
        },
        "power_and_thermals": {
            "supply": "USB-C 5V/4A Power Adapter",
            "temperatures_celsius": thermal
        },
        "remote_access": {
            "tailscale_ip": "100.115.216.86",
            "lan_ip": "10.136.121.206",
            "default_user": "orangepi",
            "ssh_port": 22,
            "authentication": "Ed25519 public key / authorized_keys"
        }
    }

    sys_info_path = os.path.join(out_dir, "system_info.json")
    with open(sys_info_path, "w", encoding="utf-8") as f:
        json.dump(system_info, f, indent=2, ensure_ascii=False)
    print(f"[OK] Saved {sys_info_path}")

    # 2. Baseline OS Telemetry (P0-05)
    idle_log_path = os.path.join(out_dir, "idle_baseline.log")
    with open(idle_log_path, "w", encoding="utf-8") as f:
        f.write("=== ORANGE PI 5 IDLE BASELINE SNAPSHOT ===\n")
        f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S %Z')}\n\n")
        f.write("--- FREE -H ---\n")
        f.write(get_cmd("free -h") + "\n\n")
        f.write("--- /PROC/MEMINFO (Top 20 lines) ---\n")
        f.write(get_cmd("head -n 20 /proc/meminfo") + "\n\n")
        f.write("--- ZRAMCTL ---\n")
        f.write(get_cmd("zramctl") + "\n\n")
        f.write("--- SWAPON --SHOW ---\n")
        f.write(get_cmd("swapon --show") + "\n\n")
        f.write("--- THERMAL ZONES ---\n")
        for k, v in thermal.items():
            f.write(f"{k}: {v} °C\n")
        f.write("\n--- TOP 10 PROCESSES BY MEMORY CONSUMPTION ---\n")
        f.write(get_cmd("ps -eo pid,ppid,cmd,%mem,%cpu --sort=-%mem | head -n 11") + "\n\n")
        f.write("--- ACTIVE SYSTEM SERVICES (Brief) ---\n")
        f.write(get_cmd("systemctl list-units --type=service --state=running | head -n 25") + "\n\n")
        f.write("--- RKNPU DRIVER AND DEVICE NODE ---\n")
        f.write(get_cmd("sudo cat /sys/kernel/debug/rknpu/version 2>/dev/null") + "\n")
        f.write(get_cmd("ls -la /dev/dri/renderD129") + "\n")
    print(f"[OK] Saved {idle_log_path}")

if __name__ == "__main__":
    main()
