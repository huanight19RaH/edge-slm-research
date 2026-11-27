#!/usr/bin/env python3
"""
P0-04: Download and verify config/tokenizer/license files for the locked base model
at an exact Hugging Face commit revision, computing local SHA256 hashes.
"""

import argparse
import hashlib
import json
from pathlib import Path
from huggingface_hub import hf_hub_download
from transformers import AutoConfig, AutoTokenizer

DEFAULT_REPO = "Qwen/Qwen2.5-3B-Instruct"
DEFAULT_REV = "aa8e72537993ba99e69dfaafa59ed015b17504d1"
FILES_TO_VERIFY = [
    "config.json",
    "generation_config.json",
    "tokenizer.json",
    "tokenizer_config.json",
    "vocab.json",
    "merges.txt",
    "model.safetensors.index.json",
    "LICENSE",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify HF model config & tokenizer at pinned revision.")
    parser.add_argument("--repo-id", default=DEFAULT_REPO)
    parser.add_argument("--revision", default=DEFAULT_REV)
    parser.add_argument("--local-dir", default="results/p0_04_hf_check")
    parser.add_argument("--out-json", default="results/p0_04_tokenizer_check.json")
    args = parser.parse_args()

    local_dir = Path(args.local_dir)
    local_dir.mkdir(parents=True, exist_ok=True)

    file_records = {}
    for fname in FILES_TO_VERIFY:
        downloaded = Path(
            hf_hub_download(
                repo_id=args.repo_id,
                filename=fname,
                revision=args.revision,
                local_dir=str(local_dir),
            )
        )
        file_records[fname] = {
            "bytes": downloaded.stat().st_size,
            "sha256": sha256_file(downloaded),
        }

    cfg = AutoConfig.from_pretrained(str(local_dir))
    tok = AutoTokenizer.from_pretrained(str(local_dir))

    sample_text = "Xin chào Orange Pi 5! Hãy tóm tắt nguyên lý KV Cache trong 1 câu."
    encoded = tok.encode(sample_text)
    decoded = tok.decode(encoded)
    chat_prompt = tok.apply_chat_template(
        [{"role": "user", "content": sample_text}],
        tokenize=False,
        add_generation_prompt=True,
    )

    summary = {
        "repo_id": args.repo_id,
        "revision": args.revision,
        "architectures": getattr(cfg, "architectures", None),
        "model_type": getattr(cfg, "model_type", None),
        "num_hidden_layers": getattr(cfg, "num_hidden_layers", None),
        "num_attention_heads": getattr(cfg, "num_attention_heads", None),
        "num_key_value_heads": getattr(cfg, "num_key_value_heads", None),
        "hidden_size": getattr(cfg, "hidden_size", None),
        "vocab_size": getattr(cfg, "vocab_size", None),
        "max_position_embeddings": getattr(cfg, "max_position_embeddings", None),
        "tokenizer_class": tok.__class__.__name__,
        "eos_token": tok.eos_token,
        "eos_token_id": tok.eos_token_id,
        "pad_token": tok.pad_token,
        "pad_token_id": tok.pad_token_id,
        "smoke_encode_len": len(encoded),
        "smoke_roundtrip_ok": decoded == sample_text,
        "chat_template_preview": chat_prompt[:120],
        "files": file_records,
    }

    out_path = Path(args.out_json)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Verified {args.repo_id}@{args.revision}")
    print(f"Roundtrip OK: {summary['smoke_roundtrip_ok']} | Tokens: {summary['smoke_encode_len']}")
    print(f"Saved report -> {out_path}")


if __name__ == "__main__":
    main()
