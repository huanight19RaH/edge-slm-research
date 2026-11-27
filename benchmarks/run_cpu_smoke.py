#!/usr/bin/env python3
"""
run_cpu_smoke.py
Executes CPU inference smoke test using llama.cpp on Orange Pi 5.
Measures:
- TTFT (Time To First Token) / Prefill latency
- Decode speed (tokens/sec)
- Peak RSS memory of llama-cli
- System memory before and after
- Temperature before and after
Outputs:
- results/p0_setup/cpu_smoke.log
- results/p0_setup/runtime_manifest.json
"""

import json
import os
import subprocess
import time
import psutil

def get_thermal():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return round(float(f.read().strip()) / 1000.0, 1)
    except:
        return 0.0

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    out_dir = os.path.join(base_dir, "results", "p0_setup")
    os.makedirs(out_dir, exist_ok=True)

    llama_bin = os.path.join(base_dir, "runtime", "llama.cpp", "build", "bin", "llama-cli")
    model_path = os.path.join(base_dir, "models", "qwen2.5-0.5b-instruct-q4_k_m.gguf")

    if not os.path.exists(llama_bin):
        print(f"[ERROR] llama-cli not found at {llama_bin}")
        return
    if not os.path.exists(model_path):
        print(f"[ERROR] Model not found at {model_path}")
        return

    prompt = "<|im_start|>system\nBạn là trợ lý AI hữu ích.<|im_end|>\n<|im_start|>user\nGiải thích ngắn gọn lợi ích của Edge AI trên Orange Pi 5 trong 3 gạch đầu dòng.<|im_end|>\n<|im_start|>assistant\n"
    
    cmd = [
        llama_bin,
        "-m", model_path,
        "-p", prompt,
        "-n", "128",
        "-t", "4",
        "-c", "512",
        "--temp", "0.7",
        "--repeat-penalty", "1.1",
        "--single-turn",
        "--simple-io"
    ]

    print(f"Executing: {' '.join(cmd)}")
    temp_before = get_thermal()
    mem_before = psutil.virtual_memory()

    start_time = time.time()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    peak_rss_bytes = 0
    while proc.poll() is None:
        try:
            p = psutil.Process(proc.pid)
            rss = p.memory_info().rss
            if rss > peak_rss_bytes:
                peak_rss_bytes = rss
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        time.sleep(0.05)

    stdout, stderr = proc.communicate()
    end_time = time.time()
    elapsed = end_time - start_time

    temp_after = get_thermal()
    mem_after = psutil.virtual_memory()

    # Save cpu_smoke.log
    smoke_log_path = os.path.join(out_dir, "cpu_smoke.log")
    with open(smoke_log_path, "w", encoding="utf-8") as f:
        f.write("=== LLAMA.CPP CPU SMOKE TEST EXECUTION LOG ===\n")
        f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S %Z')}\n")
        f.write(f"Command: {' '.join(cmd)}\n")
        f.write(f"Return Code: {proc.returncode}\n")
        f.write(f"Elapsed Time: {elapsed:.2f} seconds\n")
        f.write(f"Peak Process RSS: {peak_rss_bytes / (1024**2):.2f} MiB ({peak_rss_bytes / (1024**3):.3f} GiB)\n")
        f.write(f"Available RAM Before: {mem_before.available / (1024**3):.2f} GiB -> After: {mem_after.available / (1024**3):.2f} GiB\n")
        f.write(f"Temperature Before: {temp_before} °C -> After: {temp_after} °C\n\n")
        f.write("--- STDOUT (Model Generation) ---\n")
        f.write(stdout + "\n\n")
        f.write("--- STDERR (llama.cpp Telemetry & Timings) ---\n")
        f.write(stderr + "\n")

    print(f"[OK] Saved {smoke_log_path}")

    # Build runtime_manifest.json
    manifest = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "runtime": {
            "name": "llama.cpp",
            "version": "1.1.0-dev (commit e0b9fd7)",
            "binary": llama_bin,
            "architecture": "aarch64",
            "compiler": "GNU 15.2.0 (Ubuntu)",
            "acceleration": "ARM NEON Dot Product (+dotprod) + FP16 vector arithmetic",
            "threads_used": 4
        },
        "model": {
            "name": "Qwen2.5-0.5B-Instruct-GGUF",
            "format": "GGUF",
            "quantization": "Q4_K_M",
            "size_bytes": os.path.getsize(model_path),
            "size_mib": round(os.path.getsize(model_path) / (1024**2), 2),
            "context_window": 512
        },
        "performance": {
            "peak_rss_mib": round(peak_rss_bytes / (1024**2), 2),
            "total_elapsed_sec": round(elapsed, 2),
            "temp_start_c": temp_before,
            "temp_end_c": temp_after,
            "exit_code": proc.returncode
        }
    }

    manifest_path = os.path.join(out_dir, "runtime_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"[OK] Saved {manifest_path}")

if __name__ == "__main__":
    main()
