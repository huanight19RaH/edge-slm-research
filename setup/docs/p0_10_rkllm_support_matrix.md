# P0-10: RKLLM Toolkit v1.3.1 Support Matrix & Host Status

- **Phụ trách:** Phúc (`P0-10`)
- **Phối hợp:** Nhật
- **Toolkit pinned:** `airockchip/rknn-llm` tag `release-v1.3.1` (`rkllm-toolkit==1.3.1`, Python `3.10` / `3.11` / `3.12`, Linux `x86_64` wheel).
- **Target Board:** Orange Pi 5 — SoC **RK3588S** (`target_platform="rk3588"`, `num_npu_core` in `[1, 2, 3]`, `max_context <= 16384`).

---

## 1. Ma trận `quantized_dtype` chính thức (RKLLM SDK v1.3.1, trang 19)

| `quantized_dtype` | Mô tả kỹ thuật | RK3588 / RK3588S | RK3576 / RV1126B | RK3562 |
| :--- | :--- | :---: | :---: | :---: |
| `w8a8` | 8-bit weight + 8-bit activation | **Hỗ trợ** | Hỗ trợ | Hỗ trợ |
| `w8a8_g128` | 8-bit grouped (group size = 128) | **Hỗ trợ** | — | — |
| `w8a8_g256` | 8-bit grouped (group size = 256) | **Hỗ trợ** | — | — |
| `w8a8_g512` | 8-bit grouped (group size = 512) | **Hỗ trợ** | — | — |
| `w4a16` | 4-bit weight + 16-bit activation | **KHÔNG HỖ TRỢ** | Hỗ trợ | — |
| `w4a16_g32/g64/g128` | 4-bit grouped + 16-bit activation | **KHÔNG HỖ TRỢ** | Hỗ trợ | Hỗ trợ |
| `w4a8_g32` | 4-bit grouped + 8-bit activation | **KHÔNG HỖ TRỢ** | — | Hỗ trợ |

### Ghi chú thuật toán & tham số (`Rockchip_RKLLM_SDK_EN_1.3.1.pdf`, tr. 19–20 & `benchmark.md`):
- `quantized_algorithm`: `"normal"` hỗ trợ mọi dtype; `"grq"` chỉ hỗ trợ `w4a16` / `w4a16_g*` (không dùng được cho `rk3588`).
- `optimization_level`: `0` tối ưu tốc độ suy luận (được khuyến nghị trong `benchmark.md`), `1` ưu tiên độ chính xác lượng tử hóa (có thể giảm tốc độ).
- `hybrid_rate`: ∈ `[0, 1)` dùng để trộn giữa `w8a8` và `w8a8_g*` trên RK3588.
- **Lưu ý group size:** `group_size` (128 / 256 / 512) phải chia hết chiều đầu ra của lớp Linear.

---

## 2. Trạng thái Smoke Test trên máy hiện tại (Windows Host)

- **Kiểm tra môi trường:** `rkllm_toolkit-1.3.1-cp312-cp312-linux_x86_64.whl` chỉ phân phối cho **Linux `x86_64`** (sử dụng thư viện native `.so` và `torch==2.6.0`, `transformers==5.8.0`).
- **Trạng thái máy trạm hiện tại:** Windows host (`wsl -l -v` chưa cài distro Linux nào).
- **Hành động đã hoàn tất:**
  1. Đã viết sẵn script [`convert_rkllm.py`](../quantization/convert_rkllm.py) cài guardrail chặn `w4a16` trên `rk3588` và xuất manifest SHA256.
  2. Đã viết sẵn script [`setup_wsl_rkllm.sh`](../quantization/setup_wsl_rkllm.sh) để cài đặt và chạy smoke test `Qwen/Qwen2.5-0.5B-Instruct` (`w8a8`) ngay khi bật WSL2 Ubuntu (`wsl --install -d Ubuntu`) hoặc trên máy Linux `x86_64`.
- **Blocker cần mở trước khi đóng `P0-10`:** Chạy `bash quantization/setup_wsl_rkllm.sh` trong WSL2 Ubuntu / Linux `x86_64` để sinh tệp `.rkllm` mẫu và log thực tế (`results/p0_10_rkllm_smoke/smoke_convert.log`) bàn giao cho Nhật test `P0-11`.
