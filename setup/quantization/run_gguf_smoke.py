#!/usr/bin/env python3
"""
P0-07 Smoke Test Runner:
1. Downloads pinned llama.cpp b12776 Windows CPU x64 binaries + convert_hf_to_gguf.py.
2. Builds a tiny 2-layer Qwen2ForCausalLM smoke model with the real Qwen2.5 tokenizer.
3. Converts to F16 GGUF, quantizes to Q8_0 and Q4_K_M, verifies SHA256, and runs llama-cli inference.
"""

import json
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path
import torch
from transformers import Qwen2Config, Qwen2ForCausalLM

TAG = "b12776"
WIN_ZIP_URL = f"https://github.com/ggml-org/llama.cpp/releases/download/{TAG}/llama-{TAG}-bin-win-cpu-x64.zip"
LLAMACPP_REPO = "https://github.com/ggml-org/llama.cpp.git"


def download_file(url: str, dest: Path) -> None:
    if dest.exists() and dest.stat().st_size > 0:
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {url} -> {dest}")
    urllib.request.urlretrieve(url, dest)


def ensure_convert_repo(repo_dir: Path) -> Path:
    convert_py = repo_dir / "convert_hf_to_gguf.py"
    if not (repo_dir / "conversion").exists() or not convert_py.exists():
        if repo_dir.exists():
            shutil.rmtree(repo_dir)
        subprocess.run(
            ["git", "clone", "--depth", "1", "--branch", TAG, "--filter=blob:none", "--sparse", LLAMACPP_REPO, str(repo_dir)],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(repo_dir), "sparse-checkout", "set", "conversion", "gguf-py"],
            check=True,
        )
    return convert_py


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    tools_dir = root / "tools" / f"llama_cpp_{TAG}"
    bin_dir = tools_dir / "bin"
    zip_path = tools_dir / f"llama-{TAG}-bin-win-cpu-x64.zip"
    repo_dir = tools_dir / "repo"

    convert_py = ensure_convert_repo(repo_dir)
    download_file(WIN_ZIP_URL, zip_path)

    if not (bin_dir / "llama-quantize.exe").exists():
        bin_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(bin_dir)

    quant_exe = next(bin_dir.rglob("llama-quantize.exe"))
    cli_exe = next(bin_dir.rglob("llama-cli.exe"))

    # Create tiny 2-layer Qwen2 model using real Qwen2.5 tokenizer checked in P0-04
    tok_src = root / "results" / "p0_04_hf_check"
    smoke_hf = root / "results" / "p0_07_smoke_hf"
    smoke_hf.mkdir(parents=True, exist_ok=True)
    for fname in ["tokenizer.json", "tokenizer_config.json", "vocab.json", "merges.txt"]:
        shutil.copy2(tok_src / fname, smoke_hf / fname)

    cfg = Qwen2Config(
        vocab_size=151936,
        hidden_size=128,
        intermediate_size=256,
        num_hidden_layers=2,
        num_attention_heads=4,
        num_key_value_heads=2,
        max_position_embeddings=2048,
        tie_word_embeddings=True,
        torch_dtype=torch.float16,
    )
    torch.manual_seed(42)
    model = Qwen2ForCausalLM(cfg).to(torch.float16)
    model.save_pretrained(smoke_hf, safe_serialization=True)

    smoke_out = root / "results" / "p0_07_gguf_smoke"
    manifest_json = root / "results" / "p0_07_gguf_smoke_log.json"
    conv_cmd = [
        sys.executable,
        str(root / "quantization" / "convert_gguf.py"),
        "--hf-dir", str(smoke_hf),
        "--out-dir", str(smoke_out),
        "--model-name", "qwen25-tiny-smoke",
        "--convert-script", str(convert_py),
        "--quantize-bin", str(quant_exe),
        "--outtype", "f16",
        "--quants", "Q8_0", "Q4_K_M",
        "--manifest-out", str(manifest_json),
    ]
    subprocess.run(conv_cmd, check=True)

    # Run inference smoke check on Q8_0 and Q4_K_M
    data = json.loads(manifest_json.read_text(encoding="utf-8"))
    data["inference_smoke"] = {}
    for q in ["Q8_0", "Q4_K_M"]:
        q_path = data["artifacts"][q]["path"]
        cmd = [str(cli_exe), "-m", q_path, "-p", "Hello", "-n", "8", "-c", "128", "--no-display-prompt", "-st"]
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        data["inference_smoke"][q] = {
            "returncode": proc.returncode,
            "stdout_preview": proc.stdout.strip()[:200],
            "stderr_tail": proc.stderr.strip().splitlines()[-6:],
        }
        if proc.returncode != 0:
            raise RuntimeError(f"llama-cli failed for {q}: {proc.stderr}")

    manifest_json.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"P0-07 GGUF smoke test PASSED -> {manifest_json}")


if __name__ == "__main__":
    main()
