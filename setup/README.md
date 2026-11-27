# Phase 0 — Setup Deliverables (Phúc)

Thư mục này chứa toàn bộ kết quả và script thực hiện các task giai đoạn **Setup (`P0 · Setup`)** của **Phúc** (`P0-01`, `P0-04`, `P0-07`, `P0-10`, `P0-13`).

## Cấu trúc thư mục

```text
setup/
├── README.md
├── docs/
│   ├── p0_01_compatibility_matrix.md     # P0-01: So sánh Qwen2.5-3B vs Llama-3.2-3B & tương thích RKLLM
│   ├── p0_10_rkllm_support_matrix.md     # P0-10: Ma trận dtype RKLLM v1.3.1 cho RK3588 & trạng thái host
│   └── p0_13_reproducibility_guide.md    # P0-13: Hướng dẫn tái lập & ghi nhận giới hạn kỹ thuật
├── quantization/
│   ├── environment.yml                   # P0-04: Môi trường Conda Linux x86_64 (RKLLM 1.3.1 + GGUF)
│   ├── requirements-gguf.txt             # P0-04: Dependencies nhẹ cho verify HF & GGUF
│   ├── verify_hf_tokenizer.py            # P0-04: Script tải & kiểm chứng config/tokenizer theo revision
│   ├── convert_gguf.py                   # P0-07: Script convert HF -> F16 GGUF -> Q8_0 / Q4_K_M (llama.cpp b12776)
│   ├── run_gguf_smoke.py                 # P0-07: Smoke test tự động GGUF + llama-cli
│   ├── convert_rkllm.py                  # P0-10: Script convert RKLLM v1.3.1 kèm guardrail RK3588
│   ├── setup_wsl_rkllm.sh                # P0-10: Script cài đặt & smoke test RKLLM trên Linux x86_64 / WSL2
│   └── model_manifest.json               # P0-13: Khóa model/revision, SHA256, toolchain & hạn chế nghiên cứu
└── results/
    ├── p0_04_tokenizer_check.json        # Bằng chứng kiểm tra tokenizer/config Qwen2.5-3B-Instruct
    ├── p0_07_gguf_smoke_log.json         # Bằng chứng smoke test GGUF F16 -> Q8_0 / Q4_K_M + llama-cli
    ├── p0_10_env_check.json              # Kết quả kiểm tra môi trường Windows host đối với rkllm-toolkit
    └── p0_10_w4a16_guardrail.txt         # Bằng chứng guardrail chặn w4a16 trên RK3588
```

## Tóm tắt trạng thái các Task của Phúc
- **`P0-01` (Hoàn thành):** Chốt `Qwen/Qwen2.5-3B-Instruct` (`aa8e72537993ba99e69dfaafa59ed015b17504d1`), KV Cache `36 KiB/token` (nhỏ hơn `3.11×` so với `Llama-3.2-3B-Instruct`).
- **`P0-04` (Hoàn thành):** Đã tạo `environment.yml`, `.venv` Python `3.12` và verify roundtrip tokenizer thành công.
- **`P0-07` (Hoàn thành):** Pin `llama.cpp b12776`, pass smoke test convert `F16` → `Q8_0` & `Q4_K_M` + chạy `llama-cli`.
- **`P0-10` (Đang làm — chờ Linux x86_64/WSL2):** Đã hoàn thiện script, support matrix & guardrail; phát hiện RKLLM SDK v1.3.1 **không hỗ trợ `w4a16` trên `rk3588`** (chỉ hỗ trợ `w8a8`, `w8a8_g128`, `w8a8_g256`, `w8a8_g512`). Chờ chạy `bash setup/quantization/setup_wsl_rkllm.sh` trên WSL2 Ubuntu / Linux x86_64 để sinh artifact `.rkllm` smoke test.
- **`P0-13` (Hoàn thành):** Đã khóa `model_manifest.json` kèm SHA256 thật và tài liệu tái lập.
