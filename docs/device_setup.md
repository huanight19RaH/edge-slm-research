# Báo cáo Thiết lập OS và Baseline Hệ thống Orange Pi 5
**Dự án:** NCKH SLM Offline – Team B (Phúc – Nhật – Hưng)  
**Deliverable Task P0-05:** `device_setup.md + idle baseline log`

---

## 1. Tổng quan Phần cứng và Hệ điều hành (Baseline)

| Thông số | Chi tiết đo lường thực tế | Ghi chú kỹ thuật |
| :--- | :--- | :--- |
| **Bo mạch** | Orange Pi 5 (8GB) | SoC Rockchip RK3588S (8nm LP) |
| **Kiến trúc CPU** | 8 Cores ARMv8.2-A big.LITTLE | 4x Cortex-A76 (@ 2.256 GHz) + 4x Cortex-A55 (@ 1.800 GHz) |
| **Tập lệnh ISA mở rộng** | `fp asimd aes pmull sha1 sha2 crc32 atomics fphp asimdhp asimdrdm asimddp` | Hỗ trợ ARM NEON Dot Product (`asimddp`) & FP16 |
| **NPU** | 3 Cores NPU tích hợp (6.0 TOPS INT8/INT4/FP16) | Driver kernel `v0.9.8`, device node `/dev/dri/renderD129` |
| **Tổng RAM vật lý** | **7.744 GiB** (~8,119,864 kB) | LPDDR4X |
| **RAM khả dụng ở trạng thái tĩnh (Idle)** | **~6.3 – 7.0 GiB** | Đủ tiêu chuẩn chạy mô hình 3B với trần an toàn 6.5 GiB |
| **ZRAM / Swap** | **3.9 GiB** (`/dev/zram0`, comp algorithm: `lzo-rle`) | Bộ đệm chống crash kernel khi chạm đỉnh bộ nhớ |
| **Ổ cứng lưu trữ** | 512 GB NVMe SSD (`/dev/nvme0n1p1`) | 465 GiB khả dụng, còn trống **388 GiB** (tốc độ đọc tuần tự >2 GB/s) |
| **Hệ điều hành** | Ubuntu 26.04 (Resolute Raccoon) ARM64 | Kernel `6.1.115-vendor-rk35xx` |
| **Nhiệt độ nghỉ (Idle Temp)** | **40.5 °C – 43.5 °C** | Tản nhiệt chủ động (quạt làm mát + khối nhôm tiếp xúc) |

---

## 2. Phân bổ Ngưỡng Bộ nhớ An toàn (Memory Budget)

Theo quy ước nghiên cứu của nhóm:
- **Trần an toàn tuyệt đối (Safe Ceiling):** `<= 6.5 GiB`.
- **Dự phòng cho Hệ điều hành & Dịch vụ nền:** `1.5 GiB` (kernel, network, tailscale, zram scratch).
- **Ngưỡng kích hoạt cảnh báo nguy cơ OOM (Out Of Memory):** `>= 6.0 GiB`.

### Bảng dự toán phân bổ bộ nhớ cho mô hình 3B:
| Thành phần | GGUF Q4_K_M (CPU) | GGUF Q8_0 (CPU) | RKLLM W4A16 (NPU) | RKLLM W8A8 (NPU) |
| :--- | :--- | :--- | :--- | :--- |
| **Trọng số mô hình (Weights)** | ~1.9 GiB | ~3.4 GiB | ~1.8 GiB | ~3.2 GiB |
| **KV Cache (2048 tokens)** | ~0.5 GiB | ~0.5 GiB | ~0.4 GiB | ~0.4 GiB |
| **Runtime Buffers & Scratchpad** | ~0.3 GiB | ~0.4 GiB | ~0.3 GiB | ~0.3 GiB |
| **Dịch vụ OS nền** | ~1.2 GiB | ~1.2 GiB | ~1.2 GiB | ~1.2 GiB |
| **Tổng Peak RAM dự kiến** | **~3.9 GiB** | **~5.5 GiB** | **~3.7 GiB** | **~5.1 GiB** |
| **Độ an toàn (< 6.5 GiB)** | **An toàn** | **An toàn** | **An toàn** | **An toàn** |

---

## 3. Cấu hình Dịch vụ Nền & Giảm tải tài nguyên

Nhật đã kiểm tra các dịch vụ nền đang chạy trên hệ thống:
1. `tailscaled.service`: Giữ kết nối VPN an toàn cho cả nhóm (~0.6% RAM, ~45MB).
2. `ssh.service`: Phục vụ truy cập terminal từ xa.
3. Không chạy giao diện đồ họa nặng (X11 desktop / GNOME display manager) trong quá trình đo benchmark để giải phóng tối đa RAM và CPU cores cho `llama.cpp` và `rkllm`.

Log chi tiết lưu tại file: `results/p0_setup/idle_baseline.log`.
