# Milestone 1: Memory Budget, ZRAM 4GB và CPU Baseline

## Milestone 1a: Tính toán Memory Budget & Thiết lập ZRAM 4GB trên Orange Pi 5

### 1. Phân bổ ngưỡng bộ nhớ an toàn (Safe Budget: 6.5 GiB / 8.0 GiB)
- **Tổng RAM vật lý:** ~7.7–8.0 GiB khả dụng trên Linux ARM64.
- **Ngưỡng trần an toàn cho tiến trình nghiên cứu:** **6.5 GiB** (chừa ~1.5 GiB cho kernel, hệ điều hành, dịch vụ hệ thống và bộ đệm I/O để tránh OOM killer).
- Thành phần tiêu thụ chính khi chạy SLM:
  1. Trọng số mô hình (Model weights: ~1.8–3.4 GB tùy `Q4_K_M` / `Q8_0` / `W4A16` / `W8A8`).
  2. Bộ đệm ngữ cảnh (KV Cache theo `512` -> `4096` tokens).
  3. Scratchpad / Compute buffers của runtime (`llama.cpp` hoặc `librkllmrt.so`).

### 2. Hướng dẫn kiểm tra và cấu hình ZRAM 4GB (LZ4)
Thực hiện trên Orange Pi 5 (TV3 phụ trách xác minh):

```bash
# Kiểm tra trạng thái RAM và swap hiện tại
free -h
zramctl

# Nạp module zram nếu chưa kích hoạt
sudo modprobe zram

# Cấu hình zram0 dung lượng 4GB với thuật toán nén lz4
sudo swapoff /dev/zram0 2>/dev/null || true
echo lz4 | sudo tee /sys/block/zram0/comp_algorithm
echo 4G | sudo tee /sys/block/zram0/disksize
sudo mkswap /dev/zram0
sudo swapon -p 100 /dev/zram0

# Xác nhận lại cấu hình
zramctl
swapon --show
```

---

## Milestone 1b: CPU Baseline với `llama.cpp` (GGUF Q8_0 & Q4_K_M)

### Mục tiêu
Thiết lập đường cơ sở (baseline) trên CPU 8 nhân ARM Cortex-A76/A55 trước khi chuyển sang NPU RK3588S:
- Mô hình: `Qwen2.5-3B-Instruct` và `Llama-3.2-3B-Instruct`.
- Định dạng: GGUF `Q8_0` và `Q4_K_M`.
- Ghi nhận: Peak RAM, TTFT (ms), Decode (Tokens/s) và trạng thái ổn định dưới ngưỡng 6.5 GiB.
- Lưu toàn bộ log và bảng tổng hợp vào thư mục `results/`.
