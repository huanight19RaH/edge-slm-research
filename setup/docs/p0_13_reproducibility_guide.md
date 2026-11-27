# P0-13: Hướng dẫn Tái lập & Quyết định Kỹ thuật từ Phase 0 (Setup)

- **Phụ trách:** Phúc (`P0-13`)
- **Phối hợp:** Nhật, Hưng
- **Tệp khóa cấu hình:** [`quantization/model_manifest.json`](../quantization/model_manifest.json)

---

## 1. Cấu hình đã khóa (Locked Baseline)

| Hạng mục | Giá trị đã khóa |
| :--- | :--- |
| **Model chính (3B)** | `Qwen/Qwen2.5-3B-Instruct` |
| **Revision (Commit SHA)** | `aa8e72537993ba99e69dfaafa59ed015b17504d1` |
| **Model Smoke Test (0.5B)** | `Qwen/Qwen2.5-0.5B-Instruct` (`sha: 7ae557604adf67be50417f59c2c2f167def9a775`) |
| **Kiến trúc / Tokenizer** | `Qwen2ForCausalLM` (`36L`, `2 KV heads`, `head_dim=128`) · `Qwen2Tokenizer` (`vocab=151936`) |
| **Giấy phép** | `qwen-research` (không gated) |
| **GGUF Toolchain (CPU)** | `ggml-org/llama.cpp` release **`b12776`** (`Q8_0`, `Q4_K_M`) |
| **RKLLM Toolchain (NPU)** | `airockchip/rknn-llm` release **`release-v1.3.1`** (`rkllm-toolkit==1.3.1`, Python 3.12, Linux x86_64) |

---

## 2. Hạn chế kỹ thuật cần báo cáo ở Setup Gate (`P0-15`)

1. **RK3588S không hỗ trợ `W4A16` trong RKLLM SDK v1.3.1:**
   - Theo `Rockchip_RKLLM_SDK_EN_1.3.1.pdf` (trang 19), `target_platform="rk3588"` chỉ hỗ trợ 4 kiểu lượng tử hóa: `w8a8`, `w8a8_g128`, `w8a8_g256`, `w8a8_g512`.
   - `w4a16` và `w4a16_g*` chỉ hỗ trợ trên RK3576 / RV1126B / RK3562.
   - **Đề xuất phương án nghiên cứu cho Phase 2:** Chạy NPU đối chứng giữa `w8a8` và `w8a8_g128` (hoặc `hybrid_rate`), đồng thời ghi nhận rõ giới hạn phần cứng NPU RK3588S đối với `w4a16` trong báo cáo khoa học.
2. **Môi trường Convert RKLLM yêu cầu Linux `x86_64`:**
   - Wheel `rkllm_toolkit-1.3.1-cp312-cp312-linux_x86_64.whl` không chạy trực tiếp trên Windows host. Cần chạy `bash quantization/setup_wsl_rkllm.sh` trong WSL2 Ubuntu hoặc máy trạm Linux x86_64 để hoàn tất smoke test `.rkllm`.
3. **Dung lượng & Ngưỡng RAM 8GB:**
   - `Qwen2.5-3B-Instruct` có KV Cache chỉ `36 KiB/token` (`72 MiB` @ 2048, `144 MiB` @ 4096), giúp giữ `Q4_K_M` (~1.93 GB) và `Q8_0` (~3.29 GB) dưới ngưỡng an toàn `6.5 GB` trên Orange Pi 5.

---

## 3. Quy trình tái lập nhanh

### A. Kiểm chứng Model Config & Tokenizer (`P0-04`)
```powershell
uv venv .venv --python 3.12
uv pip install --python .venv\Scripts\python.exe -r quantization\requirements-gguf.txt
.venv\Scripts\python.exe quantization\verify_hf_tokenizer.py
```

### B. Chuyển đổi & Lượng tử hóa GGUF (`P0-07` / `P1-01`)
```powershell
# Smoke test với model tiny (đã kiểm chứng trên llama.cpp b12776):
.venv\Scripts\python.exe quantization\run_gguf_smoke.py

# Khi chạy model 3B chính thức ở Phase 1 (P1-01):
.venv\Scripts\python.exe quantization\convert_gguf.py `
  --hf-dir models\Qwen2.5-3B-Instruct `
  --out-dir models\gguf `
  --model-name qwen2.5-3b-instruct `
  --convert-script tools\llama_cpp_b12776\convert_hf_to_gguf.py `
  --quantize-bin tools\llama_cpp_b12776\bin\llama-quantize.exe
```

### C. Chuyển đổi RKLLM trên Linux x86_64 / WSL2 (`P0-10` / `P2-03`)
```bash
bash quantization/setup_wsl_rkllm.sh
```
