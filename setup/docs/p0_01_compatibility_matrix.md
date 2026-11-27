# P0-01: Model Manifest & Compatibility Matrix (Orange Pi 5 / RK3588S)

- **Phụ trách:** Phúc (`P0-01`)
- **Phối hợp:** Nhật, Hưng
- **Trạng thái:** Hoàn thành kiểm chứng cấu hình, license, tokenizer và khả năng hỗ trợ từ Rockchip RKLLM SDK `release-v1.3.1`.

---

## 1. So sánh hai mô hình ứng viên SLM 3B

| Tiêu chí | `Qwen/Qwen2.5-3B-Instruct` **(ĐỀ XUẤT CHỌN)** | `meta-llama/Llama-3.2-3B-Instruct` |
| :--- | :--- | :--- |
| **Revision khóa (Commit SHA)** | `aa8e72537993ba99e69dfaafa59ed015b17504d1` | `0cb88a4f764b7a12671c53f0838cd831a0843b95` |
| **Kiến trúc (`architectures`)** | `Qwen2ForCausalLM` (`model_type: qwen2`) | `LlamaForCausalLM` (`model_type: llama`) |
| **Số lớp (`num_hidden_layers`)** | `36` | `28` |
| **Query / KV Heads (GQA)** | `16` Q / `2` KV | `24` Q / `8` KV |
| **Hidden Size / Head Dim** | `2048` / `128` | `3072` / `128` |
| **Intermediate Size** | `11008` | `8192` |
| **Vocab Size** | `151936` | `128256` |
| **Max Position Embeddings** | `32768` | `131072` |
| **Tied Embeddings** | `true` | `true` |
| **Tokenizer Class** | `Qwen2Tokenizer` (`<|im_end|>`, no BOS) | `PreTrainedTokenizerFast` (Tiktoken BPE) |
| **KV Cache (FP16 / token)** | **`36 KiB/token`** (`72 MiB` @ 2048; `144 MiB` @ 4096) | **`112 KiB/token`** (`224 MiB` @ 2048; `448 MiB` @ 4096) — **nặng gấp 3.11×** |
| **Dung lượng BF16/FP16 gốc** | `6,171,926,992` bytes (~`5.75 GiB`) | ~`6.43 GB` |
| **Giấy phép & Truy cập HF** | `qwen-research` · **Không gated** (`gated: false`) | `llama3.2` · **Gated manual** (cần duyệt & `HF_TOKEN`) |
| **Hỗ trợ `llama.cpp` (CPU ARM)** | Đầy đủ (`Q8_0`, `Q4_K_M`, v.v.) | Đầy đủ (`Q8_0`, `Q4_K_M`, v.v.) |
| **Hỗ trợ `rkllm-toolkit` v1.3.1** | Liệt kê chính thức (`Qwen2/Qwen2.5`) | Liệt kê chính thức (`LLAMA models`) |

---

## 2. Phát hiện tương thích quan trọng cho RK3588 / RK3588S (Orange Pi 5)

Theo tài liệu chính thức **Rockchip RKLLM SDK v1.3.1** (`doc/Rockchip_RKLLM_SDK_EN_1.3.1.pdf`, mục `3.1.3` trang 19) và `benchmark.md` của `airockchip/rknn-llm`:

| Nền tảng NPU | Các `quantized_dtype` được hỗ trợ | Hỗ trợ `w4a16`? |
| :--- | :--- | :---: |
| **RK3588 / RK3588S (Orange Pi 5)** | `w8a8`, `w8a8_g128`, `w8a8_g256`, `w8a8_g512` | **KHÔNG** (`w4a16` báo lỗi không hỗ trợ trên `rk3588`) |
| RK3576 / RV1126B | `w4a16`, `w4a16_g32`, `w4a16_g64`, `w4a16_g128`, `w8a8` | Có |
| RK3562 | `w8a8`, `w4a16_g32`, `w4a16_g64`, `w4a16_g128`, `w4a8_g32` | Có (grouped) |

**Hệ quả nghiên cứu cần báo cáo trong P0-13 & P0-15 (Setup Gate):**
1. Đề cương ban đầu dự kiến chạy hai cấu hình NPU `W8A8` và `W4A16` trên Orange Pi 5 (`RK3588S`). Thực tế SDK RKLLM v1.3.1 **không hỗ trợ `w4a16` trên phần cứng RK3588**, chỉ hỗ trợ `w8a8` và nhóm `w8a8_g128` / `w8a8_g256` / `w8a8_g512` (cùng `hybrid_rate` ∈ `[0, 1)`).
2. Khi chuyển sang Phase 2 (`P2-03`), nhóm cần đối chứng trên NPU giữa `w8a8` và `w8a8_g128` (hoặc ghi nhận blocker phần cứng đối với `w4a16` theo đúng nguyên tắc của `P2-03`).

---

## 3. Quyết định chọn Model chính & Model Smoke Test

- **Model chính (Main 3B):** `Qwen/Qwen2.5-3B-Instruct` (`sha: aa8e72537993ba99e69dfaafa59ed015b17504d1`)
  - **Lý do kỹ thuật:** KV Cache nhỏ hơn `3.11×` so với `Llama-3.2-3B-Instruct`, giúp tối ưu ngân sách RAM 8GB khi khảo sát context `2048–4096` tokens ở Milestone 3; hỗ trợ tiếng Việt tốt; không bị gated trên Hugging Face nên dễ tái lập.
- **Model Smoke Test (0.5B cho P0-07 / P0-10 / P0-11):** `Qwen/Qwen2.5-0.5B-Instruct` (`sha: 7ae557604adf67be50417f59c2c2f167def9a775`) — cùng họ kiến trúc `Qwen2ForCausalLM` và cùng `Qwen2Tokenizer`, tải nhanh và chạy nhẹ để kiểm chứng pipeline CPU + NPU trước khi chạy model 3B.
