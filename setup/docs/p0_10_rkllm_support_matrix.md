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

## 2. Trạng thái Smoke Test trên Linux `x86_64`

- **Kiểm tra môi trường ([`p0_10_env_check.json`](../results/p0_10_env_check.json)):** Linux `x86_64`, Python `3.12.3`, đã cài thành công `rkllm_toolkit-1.3.1-cp312-cp312-linux_x86_64.whl` trong `.venv_rkllm` (`rkllm_installed: true`).
- **Hành động đã hoàn tất:**
  1. Cài đặt guardrail trong [`convert_rkllm.py`](../quantization/convert_rkllm.py) chặn `w4a16` trên `rk3588` (exit code `3`, đã ghi log tại [`p0_10_w4a16_guardrail.txt`](../results/p0_10_w4a16_guardrail.txt)).
  2. Tải model smoke test `Qwen/Qwen2.5-0.5B-Instruct` (`sha: 7ae557604adf67be50417f59c2c2f167def9a775`) và chuyển đổi thành công sang `.rkllm` (`dtype=w8a8`, `optimization_level=0`, `num_npu_core=3`, `max_context=2048`, `target_platform=rk3588`).
  3. **Artifact bàn giao cho `P0-11` (Nhật):**
     - Model: `Qwen2.5-0.5B-Instruct_w8a8_opt0_rk3588.rkllm` (`792,129,860` bytes / ~`756 MiB`, SHA256: `79cf529516b1c163c71b0178f7efbaaa66ce51c8f3e87a16397287a63011f727` — file nhị phân `.rkllm` được loại trừ khỏi Git theo `.gitignore`).
     - Manifest & log: [`Qwen2.5-0.5B-Instruct_w8a8_opt0_rk3588_manifest.json`](../results/p0_10_rkllm_smoke/Qwen2.5-0.5B-Instruct_w8a8_opt0_rk3588_manifest.json) và [`smoke_convert.txt`](../results/p0_10_rkllm_smoke/smoke_convert.txt).
