#!/usr/bin/env python3
"""
P0-07: Convert a Hugging Face causal LM to GGUF (F16) and quantize to Q8_0 / Q4_K_M
using pinned llama.cpp release b12776. Records exact commands, file sizes, and SHA256.
"""

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PINNED_LLAMACPP_TAG = "b12776"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run_cmd(cmd: list[str]) -> str:
    print(">>", " ".join(cmd))
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr, file=sys.stderr)
        raise RuntimeError(f"Command failed ({proc.returncode}): {' '.join(cmd)}")
    return proc.stdout + proc.stderr


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert HF model to GGUF & quantize (pinned llama.cpp b12776).")
    parser.add_argument("--hf-dir", required=True, help="Local directory containing Hugging Face model files.")
    parser.add_argument("--out-dir", required=True, help="Output directory for GGUF artifacts.")
    parser.add_argument("--model-name", required=True, help="Base prefix for output GGUF filenames.")
    parser.add_argument("--convert-script", required=True, help="Path to pinned llama.cpp convert_hf_to_gguf.py.")
    parser.add_argument("--quantize-bin", required=True, help="Path to llama-quantize executable.")
    parser.add_argument("--outtype", default="f16", choices=["f16", "bf16", "f32"])
    parser.add_argument("--quants", nargs="+", default=["Q8_0", "Q4_K_M"])
    parser.add_argument("--manifest-out", default=None, help="Optional JSON log path.")
    args = parser.parse_args()

    hf_dir = Path(args.hf_dir).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    f16_path = out_dir / f"{args.model_name}-{args.outtype}.gguf"
    conv_cmd = [
        sys.executable,
        str(Path(args.convert_script).resolve()),
        str(hf_dir),
        "--outfile",
        str(f16_path),
        "--outtype",
        args.outtype,
    ]
    conv_log = run_cmd(conv_cmd)

    artifacts = {
        args.outtype.upper(): {
            "path": str(f16_path),
            "bytes": f16_path.stat().st_size,
            "gib": round(f16_path.stat().st_size / (1024 ** 3), 4),
            "sha256": sha256_file(f16_path),
            "command": " ".join(conv_cmd),
        }
    }

    quant_bin = str(Path(args.quantize_bin).resolve())
    for qtype in args.quants:
        q_path = out_dir / f"{args.model_name}-{qtype}.gguf"
        q_cmd = [quant_bin, str(f16_path), str(q_path), qtype]
        run_cmd(q_cmd)
        size_bytes = q_path.stat().st_size
        artifacts[qtype] = {
            "path": str(q_path),
            "bytes": size_bytes,
            "gib": round(size_bytes / (1024 ** 3), 4),
            "sha256": sha256_file(q_path),
            "command": " ".join(q_cmd),
        }

    report = {
        "pinned_llamacpp_tag": PINNED_LLAMACPP_TAG,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "hf_dir": str(hf_dir),
        "artifacts": artifacts,
        "convert_log_tail": conv_log.splitlines()[-15:],
    }

    manifest_path = Path(args.manifest_out) if args.manifest_out else (out_dir / f"{args.model_name}_gguf_manifest.json")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"GGUF conversion complete. Manifest saved -> {manifest_path}")


if __name__ == "__main__":
    main()
