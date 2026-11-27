# Báo cáo Tổng kết Các Task Giai đoạn Setup (`Phase 0`) — Phụ trách: Phúc

- **Đề tài:** Triển khai và Lượng tử hóa Mô hình Ngôn ngữ Nhỏ (SLM) Ngoại tuyến trên Thiết bị Biên Giới hạn Bộ nhớ (Orange Pi 5 / RK3588S, RAM 8GB)
- **Phụ trách:** Phúc (`P0-01`, `P0-04`, `P0-07`, `P0-10`, `P0-13`)
- **Phối hợp:** Nhật, Hưng
- **Trạng thái chung:** Đã hoàn thành toàn bộ các task Setup (`5/5` đầu việc) và sẵn sàng cho Setup Gate (`P0-15`) & bàn giao sang `P0-11` / Phase 1.

---

## 1. Tổng quan tiến độ các Task

| Mã Task | Nội dung chính | Trạng thái | Sản phẩm / Bằng chứng chính |
| :--- | :--- | :---: | :--- |
| **`P0-01`** | So sánh ứng viên SLM 3B, chốt model chính & ma trận tương thích phần cứng | **Hoàn thành** | [`p0_01_compatibility_matrix.md`](./p0_01_compatibility_matrix.md) |
| **`P0-04`** | Khóa môi trường thực nghiệm & kiểm chứng config, license, tokenizer | **Hoàn thành** | [`environment.yml`](../quantization/environment.yml), [`verify_hf_tokenizer.py`](../quantization/verify_hf_tokenizer.py), [`p0_04_tokenizer_check.json`](../results/p0_04_tokenizer_check.json) |
| **`P0-07`** | Pin `llama.cpp` & chạy smoke test convert + lượng tử hóa GGUF (`F16` → `Q8_0`, `Q4_K_M`) | **Hoàn thành** | [`convert_gguf.py`](../quantization/convert_gguf.py), [`run_gguf_smoke.py`](../quantization/run_gguf_smoke.py), [`p0_07_gguf_smoke_log.json`](../results/p0_07_gguf_smoke_log.json) |
| **`P0-10`** | Thiết lập `rkllm-toolkit` v1.3.1, kiểm chứng giới hạn RK3588 & chạy smoke test `.rkllm` | **Hoàn thành** | [`convert_rkllm.py`](../quantization/convert_rkllm.py), [`setup_wsl_rkllm.sh`](../quantization/setup_wsl_rkllm.sh), [`p0_10_rkllm_support_matrix.md`](./p0_10_rkllm_support_matrix.md), [`smoke_convert.txt`](../results/p0_10_rkllm_smoke/smoke_convert.txt) |
| **`P0-13`** | Khóa manifest SHA256, tổng hợp hướng dẫn tái lập & hạn chế kỹ thuật | **Hoàn thành** | [`model_manifest.json`](../quantization/model_manifest.json), [`p0_13_reproducibility_guide.md`](./p0_13_reproducibility_guide.md) |

---

## 2. Chi tiết kết quả từng Task

### `P0-01`: Lựa chọn Mô hình & Ma trận Tương thích (`Orange Pi 5 / RK3588S`)
- Đối chiếu trực tiếp hai mô hình ứng viên 3B: `Qwen/Qwen2.5-3B-Instruct` và `meta-llama/Llama-3.2-3B-Instruct`.
- **Quyết định chọn model chính:** `Qwen/Qwen2.5-3B-Instruct` (revision `aa8e72537993ba99e69dfaafa59ed015b17504d1`):
  - **KV Cache (FP16):** Chỉ **`36 KiB/token`** (`72 MiB` @ `2048` tokens; `144 MiB` @ `4096` tokens) — **nhẹ hơn `3.11×`** so với `Llama-3.2-3B-Instruct` (`112 KiB/token`, `224 MiB` @ `2048`, `448 MiB` @ `4096`), giúp giữ mức dùng RAM dưới trần an toàn `6.5 GiB` trên bo mạch 8GB.
  - **Giấy phép & truy cập:** `qwen-research`, không bị gated trên Hugging Face (dễ tái lập hơn `llama3.2` vốn yêu cầu duyệt thủ công và `HF_TOKEN`).
  - **Hỗ trợ tiếng Việt:** Tốt trên các tác vụ đánh giá mục tiêu.
- **Quyết định chọn model smoke test (0.5B):** `Qwen/Qwen2.5-0.5B-Instruct` (revision `7ae557604adf67be50417f59c2c2f167def9a775`), dùng chung kiến trúc `Qwen2ForCausalLM` và `Qwen2Tokenizer` để kiểm chứng pipeline nhanh trước khi chạy model 3B.

### `P0-04`: Thiết lập Môi trường & Kiểm chứng Tokenizer / Config
- Đóng gói đặc tả môi trường:
  - [`environment.yml`](../quantization/environment.yml): Môi trường Conda cô lập cho Linux `x86_64` (Python `3.12.7`, `torch==2.6.0`, `transformers==5.8.0`, `gguf>=0.14.0`, khớp với `rkllm-toolkit==1.3.1`).
  - [`requirements-gguf.txt`](../quantization/requirements-gguf.txt): Bộ phụ thuộc nhẹ để verify HF và convert GGUF.
- Thực thi [`verify_hf_tokenizer.py`](../quantization/verify_hf_tokenizer.py) trên `Qwen/Qwen2.5-3B-Instruct@aa8e72537993ba99e69dfaafa59ed015b17504d1`:
  - Tải và tính SHA256 cho `8` tệp cấu hình, tokenizer và license (`config.json`, `generation_config.json`, `tokenizer.json`, `tokenizer_config.json`, `vocab.json`, `merges.txt`, `model.safetensors.index.json`, `LICENSE`).
  - Xác nhận cấu hình `Qwen2ForCausalLM` (`36` layers, `16` Q heads, `2` KV heads, `hidden_size=2048`, `vocab_size=151936`, `max_position_embeddings=32768`).
  - Kiểm tra roundtrip encode/decode tiếng Việt (`"Xin chào Orange Pi 5! Hãy tóm tắt nguyên lý KV Cache trong 1 câu."`) → `smoke_encode_len: 21`, `smoke_roundtrip_ok: true` ([`p0_04_tokenizer_check.json`](../results/p0_04_tokenizer_check.json)).

### `P0-07`: Pipeline Chuyển đổi & Smoke Test GGUF (`llama.cpp b12776`)
- Khóa công cụ CPU ở `ggml-org/llama.cpp` release **`b12776`** (commit `e38ea719bd29defbd8e5d11b5e1d799572cea45a`).
- Xây dựng script [`convert_gguf.py`](../quantization/convert_gguf.py) (convert HF → `F16`, lượng tử hóa sang `Q8_0` / `Q4_K_M`, tự động ghi kích thước và SHA256) và [`run_gguf_smoke.py`](../quantization/run_gguf_smoke.py).
- **Kết quả smoke test** với mô hình tiny 2-layer `Qwen2ForCausalLM` dùng tokenizer thật của `Qwen2.5` ([`p0_07_gguf_smoke_log.json`](../results/p0_07_gguf_smoke_log.json)):
  - `F16`: `45,422,688` bytes (`0.0423 GiB`), SHA256 `0612394cf0147c320bd988fd539895a888b7786983b88fb92dc2c8e15ad4e729`.
  - `Q8_0`: `26,913,888` bytes (`0.0251 GiB`), SHA256 `c816882ce9d8a715f28ca324886071aafa0c95640238330ab5bcbbf9fbf173b5` — chạy `llama-cli` thành công (`returncode: 0`).
  - `Q4_K_M`: `26,806,624` bytes (`0.025 GiB`), SHA256 `094202e377e546d20c0ebd66bf08585ea4b6ec3392809764c3e973b6b1428fa9` — chạy `llama-cli` thành công (`returncode: 0`).

### `P0-10`: Toolchain RKLLM v1.3.1, Guardrail RK3588 & Smoke Test `.rkllm`
- Khóa toolkit tại `airockchip/rknn-llm` tag **`release-v1.3.1`** (`rkllm-toolkit==1.3.1`, Python `3.12`, wheel Linux `x86_64`).
- **Phát hiện giới hạn phần cứng quan trọng (theo `Rockchip_RKLLM_SDK_EN_1.3.1.pdf`, trang 19):**
  - `target_platform="rk3588"` (Orange Pi 5 / RK3588S) **chỉ hỗ trợ** `w8a8`, `w8a8_g128`, `w8a8_g256`, `w8a8_g512`.
  - **Không hỗ trợ `w4a16`** hay `w4a16_g*` (các kiểu 4-bit này chỉ hỗ trợ trên RK3576 / RV1126B / RK3562).
- Cài đặt guardrail trong [`convert_rkllm.py`](../quantization/convert_rkllm.py) chặn sớm các `quantized_dtype` không tương thích với `rk3588` (trả về exit code `3`, log xác minh tại [`p0_10_w4a16_guardrail.txt`](../results/p0_10_w4a16_guardrail.txt)).
- Thiết lập môi trường `.venv_rkllm` trên **Linux `x86_64`** (Python `3.12.3`, `"rkllm_installed": true` trong [`p0_10_env_check.json`](../results/p0_10_env_check.json)) và chạy smoke test chuyển đổi `Qwen/Qwen2.5-0.5B-Instruct`:
  - Tham số: `platform=rk3588`, `dtype=w8a8`, `algorithm=normal`, `optimization_level=0`, `num_npu_core=3`, `max_context=2048`, `device=cpu`.
  - Quá trình chạy hoàn tất `Building model` (`319/319`), `Optimizing model` (`24/24`), `Converting model` (`291/291`), `Exporting` (`513/513` — `100%`) tại [`smoke_convert.txt`](../results/p0_10_rkllm_smoke/smoke_convert.txt).
  - **Artifact bàn giao cho `P0-11` (Nhật):** `Qwen2.5-0.5B-Instruct_w8a8_opt0_rk3588.rkllm` (`792,129,860` bytes / ~`755.4 MiB`, SHA256 `79cf529516b1c163c71b0178f7efbaaa66ce51c8f3e87a16397287a63011f727`, manifest tại [`Qwen2.5-0.5B-Instruct_w8a8_opt0_rk3588_manifest.json`](../results/p0_10_rkllm_smoke/Qwen2.5-0.5B-Instruct_w8a8_opt0_rk3588_manifest.json)).

### `P0-13`: Khóa Baseline (`model_manifest.json`) & Tài liệu Tái lập
- Khóa toàn bộ thông số kiến trúc, SHA256 các tệp Hugging Face (kể cả 2 shard `model-00001-of-00002.safetensors` và `model-00002-of-00002.safetensors`), phiên bản toolchain và trạng thái smoke test trong [`model_manifest.json`](../quantization/model_manifest.json).
- Viết hướng dẫn tái lập từng bước cho kiểm chứng HF, convert GGUF và convert RKLLM trong [`p0_13_reproducibility_guide.md`](./p0_13_reproducibility_guide.md).

---

## 3. Các điểm cần báo cáo tại Setup Gate (`P0-15`) & Bước tiếp theo

1. **Điều chỉnh phương án lượng tử hóa NPU cho Phase 2 (`P2-03`):**
   - Do RKLLM SDK v1.3.1 không hỗ trợ `w4a16` trên RK3588S, cần đề xuất nhóm chuyển phương án đối chứng trên NPU sang **`w8a8`** và **`w8a8_g128`** (hoặc điều chỉnh `hybrid_rate` ∈ `[0, 1)`), đồng thời ghi nhận giới hạn phần cứng đối với `w4a16` trong báo cáo khoa học.
2. **Bàn giao sang `P0-11`:**
   - Chép tệp `Qwen2.5-0.5B-Instruct_w8a8_opt0_rk3588.rkllm` sang Orange Pi 5 để kiểm chứng load và suy luận thực tế trên NPU RK3588S (`librkllmrt.so`).
3. **Chuẩn bị Phase 1 (`P1-01`):**
   - Tải đầy đủ trọng số `Qwen/Qwen2.5-3B-Instruct` (`aa8e72537993ba99e69dfaafa59ed015b17504d1`) và chạy `convert_gguf.py` để tạo các bản `Q8_0` và `Q4_K_M` phục vụ benchmark CPU baseline trên Orange Pi 5.
