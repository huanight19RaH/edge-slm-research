# Ma trận Phiên bản & Tương thích NPU RKLLM (Orange Pi 5)
**Dự án:** NCKH SLM Offline – Team B (Phúc – Nhật – Hưng)
**Deliverable Task P0-11:** `NPU smoke log + version matrix`

## 1. Bảng Khóa Phiên bản Hệ thống (Version Lock Matrix)

| Thành phần | Phiên bản khóa | Ghi chú & Trạng thái |
| :--- | :--- | :--- |
| **Phần cứng mục tiêu** | Orange Pi 5 (RK3588S) | 8 Cores CPU + 3 Cores NPU (6.0 TOPS) |
| **Hệ điều hành / Kernel** | Ubuntu 26.04 ARM64 / `6.1.115-vendor-rk35xx` | Nhân Linux Rockchip vendor hỗ trợ NPU |
| **RKNPU Driver** | `v0.9.8` | DRM minor 1 (`/dev/dri/renderD129`) |
| **RKLLM Runtime** | `v1.3.1` | `librkllmrt.so` (C/C++ runtime trên bo mạch) |
| **RKLLM Toolkit** | `v1.3.1` | Dùng trên máy Host x86_64 để convert model |
| **Lượng tử hóa NPU hỗ trợ** | `W8A8`, `W4A16` | INT8/INT4 chuyên dụng cho NPU RK3588 |
| **Môi trường Python** | Python 3.11 (`teamb_slm`) | Conda môi trường độc lập trên bo mạch |

## 2. Kết quả Smoke Test trên NPU

- **Mô hình kiểm chứng:** `qwen3-0.6b_w8a8_rk3588.rkllm` (W8A8 quantized)
- **Trạng thái khởi tạo NPU:** `rkllm init success` (Khởi tạo thành công trên phần cứng NPU)
- **Thời gian chạy:** 4.28 s
- **Bằng chứng log chi tiết:** `results/p0_setup/npu_smoke.log`
