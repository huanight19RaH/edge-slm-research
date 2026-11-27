#!/usr/bin/env python3
"""
P0-10: RKLLM Toolkit v1.3.1 conversion & quantization script for Rockchip RK3588 / RK3588S.
Requires Linux x86_64 host with rkllm-toolkit==1.3.1 installed.
Enforces verified platform dtype guardrails from Rockchip_RKLLM_SDK_EN_1.3.1.pdf (p. 19).
"""

import argparse
import hashlib
import json
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

PINNED_RKLLM_VERSION = "1.3.1"

PLATFORM_SUPPORTED_DTYPES = {
    "rk3588": ["w8a8", "w8a8_g128", "w8a8_g256", "w8a8_g512"],
    "rk3576": ["w4a16", "w4a16_g32", "w4a16_g64", "w4a16_g128", "w8a8"],
    "rv1126b": ["w4a16", "w4a16_g32", "w4a16_g64", "w4a16_g128", "w8a8"],
    "rk3562": ["w8a8", "w4a16_g32", "w4a16_g64", "w4a16_g128", "w4a8_g32"],
}

PLATFORM_SUPPORTED_CORES = {
    "rk3588": [1, 2, 3],
    "rk3576": [1, 2],
    "rk3562": [1],
    "rv1126b": [1],
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def check_environment() -> dict:
    info = {
        "os": platform.system(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "rkllm_installed": False,
        "rkllm_error": None,
    }
    try:
        import rkllm  # noqa: F401
        from rkllm.api import RKLLM  # noqa: F401
        info["rkllm_installed"] = True
    except Exception as exc:
        info["rkllm_error"] = repr(exc)
    return info


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert HF model to RKLLM (pinned SDK v1.3.1).")
    parser.add_argument("--check-env", action="store_true", help="Only inspect host OS/Python/rkllm availability.")
    parser.add_argument("--model-dir", help="Local Hugging Face model directory.")
    parser.add_argument("--out-dir", default="results/rkllm", help="Output directory for .rkllm artifact.")
    parser.add_argument("--platform", default="rk3588", choices=sorted(PLATFORM_SUPPORTED_DTYPES.keys()))
    parser.add_argument("--dtype", default="w8a8", help="Quantization dtype (e.g. w8a8, w8a8_g128).")
    parser.add_argument("--algorithm", default="normal", help="Quantization algorithm ('normal' or 'grq').")
    parser.add_argument("--optimization-level", type=int, default=0, choices=[0, 1],
                        help="0 = optimized runtime speed (recommended in benchmark.md); 1 = precision opt.")
    parser.add_argument("--num-npu-core", type=int, default=3)
    parser.add_argument("--max-context", type=int, default=4096)
    parser.add_argument("--hybrid-rate", type=float, default=0.0)
    parser.add_argument("--dataset", default=None, help="Calibration JSON path ([{'input': ..., 'target': ...}]).")
    parser.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    parser.add_argument("--load-dtype", default="float32", choices=["float32", "float16", "bfloat16"])
    args = parser.parse_args()

    env_info = check_environment()
    if args.check_env:
        print(json.dumps(env_info, indent=2))
        return 0 if env_info["rkllm_installed"] else 2

    target = args.platform.lower()
    dtype = args.dtype.lower()
    supported = PLATFORM_SUPPORTED_DTYPES[target]
    if dtype not in supported:
        print(
            f"[BLOCKER] quantized_dtype='{dtype}' is NOT supported on target_platform='{target}' "
            f"in RKLLM SDK v{PINNED_RKLLM_VERSION}! Supported dtypes for {target}: {supported}",
            file=sys.stderr,
        )
        return 3

    if args.num_npu_core not in PLATFORM_SUPPORTED_CORES[target]:
        print(
            f"[ERROR] num_npu_core={args.num_npu_core} invalid for {target}. "
            f"Allowed: {PLATFORM_SUPPORTED_CORES[target]}",
            file=sys.stderr,
        )
        return 4

    if not env_info["rkllm_installed"]:
        print(
            f"[HOST-BLOCKED] Cannot import rkllm.api on {env_info['os']} ({env_info['machine']}). "
            f"rkllm-toolkit=={PINNED_RKLLM_VERSION} distributes Linux x86_64 wheels only. "
            f"Run via WSL2 Ubuntu / Linux x86_64 using quantization/setup_wsl_rkllm.sh. "
            f"Error: {env_info['rkllm_error']}",
            file=sys.stderr,
        )
        return 2

    if not args.model_dir:
        print("[ERROR] --model-dir is required unless --check-env is passed.", file=sys.stderr)
        return 1

    from rkllm.api import RKLLM

    model_path = Path(args.model_dir).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{model_path.name}_{dtype}_opt{args.optimization_level}_{target}.rkllm"

    llm = RKLLM()
    ret = llm.load_huggingface(
        model=str(model_path),
        model_lora=None,
        device=args.device,
        dtype=args.load_dtype,
        custom_config=None,
        load_weight=True,
    )
    if ret != 0:
        raise RuntimeError(f"llm.load_huggingface failed with code {ret}")

    ret = llm.build(
        do_quantization=True,
        optimization_level=args.optimization_level,
        quantized_dtype=dtype,
        quantized_algorithm=args.algorithm,
        target_platform=target,
        num_npu_core=args.num_npu_core,
        extra_qparams=None,
        dataset=args.dataset,
        hybrid_rate=args.hybrid_rate,
        max_context=args.max_context,
    )
    if ret != 0:
        raise RuntimeError(f"llm.build failed with code {ret}")

    ret = llm.export_rkllm(str(out_file))
    if ret != 0:
        raise RuntimeError(f"llm.export_rkllm failed with code {ret}")

    meta = {
        "rkllm_version": PINNED_RKLLM_VERSION,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "model_dir": str(model_path),
        "target_platform": target,
        "quantized_dtype": dtype,
        "quantized_algorithm": args.algorithm,
        "optimization_level": args.optimization_level,
        "num_npu_core": args.num_npu_core,
        "max_context": args.max_context,
        "hybrid_rate": args.hybrid_rate,
        "artifact_path": str(out_file),
        "bytes": out_file.stat().st_size,
        "sha256": sha256_file(out_file),
    }
    meta_path = out_dir / f"{out_file.stem}_manifest.json"
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"RKLLM export complete -> {out_file} (manifest: {meta_path})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
