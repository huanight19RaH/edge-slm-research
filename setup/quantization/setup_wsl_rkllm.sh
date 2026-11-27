#!/usr/bin/env bash
# P0-10: Setup RKLLM Toolkit v1.3.1 on Linux x86_64 (or WSL2 Ubuntu) and run smoke test.
set -euo pipefail

PY_VER="${PY_VER:-3.12}"
RKLLM_TAG="release-v1.3.1"
WHL_URL="https://github.com/airockchip/rknn-llm/raw/${RKLLM_TAG}/rkllm-toolkit/packages/rkllm_toolkit-1.3.1-cp312-cp312-linux_x86_64.whl"
REQ_URL="https://raw.githubusercontent.com/airockchip/rknn-llm/${RKLLM_TAG}/rkllm-toolkit/packages/requirements.txt"

mkdir -p tools/rkllm_sdk results/p0_10_rkllm_smoke

echo "[1/4] Downloading pinned RKLLM v1.3.1 wheel and requirements..."
curl -fL -o tools/rkllm_sdk/requirements.txt "${REQ_URL}"
curl -fL -o tools/rkllm_sdk/rkllm_toolkit-1.3.1-cp312-cp312-linux_x86_64.whl "${WHL_URL}"

echo "[2/4] Creating isolated uv venv (Python ${PY_VER})..."
uv venv .venv_rkllm --python "${PY_VER}"
uv pip install --python .venv_rkllm/bin/python -r tools/rkllm_sdk/requirements.txt
uv pip install --python .venv_rkllm/bin/python tools/rkllm_sdk/rkllm_toolkit-1.3.1-cp312-cp312-linux_x86_64.whl

echo "[3/4] Downloading smoke model Qwen/Qwen2.5-0.5B-Instruct (pinned SHA)..."
.venv_rkllm/bin/python -c "
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='Qwen/Qwen2.5-0.5B-Instruct',
    revision='7ae557604adf67be50417f59c2c2f167def9a775',
    local_dir='models/Qwen2.5-0.5B-Instruct'
)
"

echo "[4/4] Running RKLLM smoke conversion (w8a8 on rk3588)..."
.venv_rkllm/bin/python quantization/convert_rkllm.py \
  --model-dir models/Qwen2.5-0.5B-Instruct \
  --out-dir results/p0_10_rkllm_smoke \
  --platform rk3588 \
  --dtype w8a8 \
  --optimization-level 0 \
  --max-context 2048 \
  --device cpu \
  2>&1 | tee results/p0_10_rkllm_smoke/smoke_convert.log
