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
    ├── p0_10_env_check.json              # Kết quả kiểm tra môi trường Linux x86_64 đối với rkllm-toolkit
    ├── p0_10_w4a16_guardrail.txt         # Bằng chứng guardrail chặn w4a16 trên RK3588
    └── p0_10_rkllm_smoke/
        ├── Qwen2.5-0.5B-Instruct_w8a8_opt0_rk3588_manifest.json  # Manifest & SHA256 artifact .rkllm smoke test
        └── smoke_convert.txt             # Log convert RKLLM w8a8 thành công trên Linux x86_64
```

## Tóm tắt trạng thái các Task của Phúc
- **`P0-01` (Hoàn thành):** Chốt `Qwen/Qwen2.5-3B-Instruct` (`aa8e72537993ba99e69dfaafa59ed015b17504d1`), KV Cache `36 KiB/token` (nhỏ hơn `3.11×` so với `Llama-3.2-3B-Instruct`).
- **`P0-04` (Hoàn thành):** Đã tạo `environment.yml`, `.venv` Python `3.12` và verify roundtrip tokenizer thành công.
- **`P0-07` (Hoàn thành):** Pin `llama.cpp b12776`, pass smoke test convert `F16` → `Q8_0` & `Q4_K_M` + chạy `llama-cli`.
- **`P0-10` (Hoàn thành):** Đã cài `rkllm-toolkit==1.3.1` trên Linux `x86_64`, kiểm chứng guardrail chặn `w4a16` trên `rk3588` (RKLLM SDK v1.3.1 chỉ hỗ trợ `w8a8`, `w8a8_g128`, `w8a8_g256`, `w8a8_g512`), và hoàn tất smoke test convert `Qwen/Qwen2.5-0.5B-Instruct` (`w8a8`, `opt0`, `rk3588`) ra `.rkllm` (`792,129,860` bytes, SHA256 `79cf529516b1c163c71b0178f7efbaaa66ce51c8f3e87a16397287a63011f727`) sẵn sàng bàn giao cho `P0-11`.
- **`P0-13` (Hoàn thành):** Đã khóa `model_manifest.json` kèm SHA256 thật và tài liệu tái lập.
