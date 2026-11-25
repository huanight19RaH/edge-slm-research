# edge-slm-research

**Triển khai và Lượng tử hóa Mô hình Ngôn ngữ Nhỏ (SLM) Ngoại tuyến trên Thiết bị Biên Giới hạn Bộ nhớ**

Repository nghiên cứu khoa học và kỹ thuật triển khai các mô hình ngôn ngữ nhỏ (Small Language Models - SLM) chạy hoàn toàn ngoại tuyến (offline) trên nền tảng phần cứng nhúng **Orange Pi 5 (RK3588S, 8GB RAM)**, so sánh định lượng giữa thực thi trên CPU (`llama.cpp` / GGUF) và tăng tốc NPU (`RKLLM` / W8A8, W4A16).

---

## 1. Phần cứng mục tiêu và Mô hình nghiên cứu

### Phần cứng mục tiêu
- **Bo mạch:** Orange Pi 5
- **SoC:** Rockchip RK3588S
- **CPU:** 8 nhân ARM (4x Cortex-A76 + 4x Cortex-A55)
- **NPU:** Rockchip NPU 6 TOPS
- **Bộ nhớ:** 8 GB LPDDR4X RAM (ngưỡng an toàn Memory Budget: **<= 6.5 GiB**, kết hợp ZRAM 4 GB)
- **Hệ điều hành:** Linux ARM64 (Ubuntu / Armbian / Debian for RK3588)

### Mô hình nghiên cứu
1. `Qwen2.5-3B-Instruct`
2. `Llama-3.2-3B-Instruct`

### Định dạng lượng tử hóa đối chứng
- **CPU Baseline (`llama.cpp`):** GGUF `Q8_0`, `Q4_K_M`
- **NPU Acceleration (`RKLLM`):** `W8A8`, `W4A16`

### Tham số khảo sát
- **Context Length (KV Cache):** `512`, `1024`, `2048`, `4096` tokens
- **Chỉ số hiệu năng hệ thống:** Peak RAM (RSS / MemAvailable), TTFT (Time To First Token), Decode throughput (Tokens/s), ổn định qua stress-test 15 lượt hội thoại liên tục
- **Chất lượng đầu ra:** Bộ 60 câu hỏi kiểm thử phân tầng và tập hiệu chuẩn (Calibration set)

---

## 2. Cấu trúc thư mục và Phân công nhóm (05 thành viên)

```text
edge-slm-research/
├── configs/          # Cấu hình thí nghiệm (YAML/JSON cho từng model & quantization)
├── docs/             # Setup và tài liệu nghiên cứu (Đề cương, Milestone 1a-1b)
├── quantization/     # Model conversion — TV1 (Script convert GGUF & RKLLM)
├── runtime/          # CPU/NPU runtime — TV2 (Wrapper gọi RKLLM & llama.cpp)
├── benchmarks/       # Benchmark runner — TV3 (Đo Peak RAM, TTFT, Tokens/s)
├── datasets/         # Calibration và evaluation (Tập calibration & 60 câu hỏi test)
├── experiments/      # Kịch bản chạy thí nghiệm (Shell scripts tự động hóa)
├── results/          # Raw logs và số liệu (CSV/JSON kết quả đo)
├── app/              # Offline chatbot (Giao diện tương tác cục bộ)
├── tests/            # Smoke test và integration test
├── README.md
├── .gitignore
└── requirements.txt
```

### Phân công trách nhiệm thành viên

| Thành viên | Vai trò | Thư mục phụ trách | Nhiệm vụ chính |
| :--- | :--- | :--- | :--- |
| **TV1** | Model & Quantization Formats Engineer | `quantization/` | Chuyển đổi model sang RKLLM (`W8A8`, `W4A16`) và GGUF (`Q4_K_M`, `Q8_0`) |
| **TV2** | NPU Runtime Engineer | `runtime/` | Triển khai RKLLM Runtime, quản lý context length và driver NPU |
| **TV3** | CPU Baseline & Memory Profiler | `benchmarks/` | Đối chứng CPU qua `llama.cpp`, cấu hình ZRAM, giám sát Peak RAM chống OOM dưới 6.5 GiB |
| **TV4** | Evaluation Dataset & Quality Lead | `datasets/` | Xây dựng tập hiệu chuẩn (Calibration) và bộ 60 câu hỏi kiểm thử phân tầng |
| **TV5** | Latency Benchmark & Demo Lead | `app/`, `experiments/` | Đo TTFT, Tokens/s, xây dựng giao diện Chatbot ngoại tuyến và tổng hợp báo cáo |

---

## 3. Lộ trình nghiên cứu (Milestones 1–4)

- **Milestone 1 — Memory Budget, ZRAM & CPU Baseline:**
  Tính toán phân bổ bộ nhớ dưới ngưỡng an toàn 6.5 GiB, cấu hình ZRAM 4 GB trên Orange Pi 5, chạy mốc chuẩn CPU với `llama.cpp` (`Q8_0` và `Q4_K_M`). Xem chi tiết tại [docs/milestone_1_setup.md](docs/milestone_1_setup.md).
- **Milestone 2 — Biên dịch & Chạy thử nghiệm NPU RKLLM:**
  Biên dịch và hiệu chuẩn mô hình trên máy Host x86 sang định dạng RKLLM (`W8A8`, `W4A16`), triển khai và chạy xác minh trên NPU RK3588S.
- **Milestone 3 — Khảo sát KV Cache & Đánh giá chất lượng:**
  Đo đạc tác động của ngữ cảnh (`512`, `1024`, `2048`, `4096` tokens) lên Peak RAM và độ trễ; chấm điểm chất lượng mô hình trên bộ 60 câu hỏi phân tầng.
- **Milestone 4 — Tối ưu hóa Prefill/Decode & Đóng gói Demo:**
  Tối ưu pha Prefill vs Decode, thực hiện stress-test 15 lượt hội thoại liên tục không tràn bộ nhớ, đóng gói ứng dụng Chatbot ngoại tuyến tại `app/`.

---

## 4. Thiết lập môi trường nhanh

```bash
# Tạo môi trường ảo Python
python3 -m venv .venv
source .venv/bin/activate  # Linux/ARM64
# .venv\Scripts\activate   # Windows

# Cài đặt thư viện phụ trợ
pip install -r requirements.txt
```

### Quy ước quản lý mã nguồn và dữ liệu lớn
- **Không commit trọng số mô hình** (`.gguf`, `.rkllm`, `.safetensors`, `.bin`, `.pt`) lên Git. Lưu trữ trọng số tại thư mục cục bộ được cấu hình trong `.gitignore`.
- Mỗi thành viên làm việc trên nhánh riêng theo quy ước `feat/tv<so>-<ten-tinh-nang>` (ví dụ: `feat/tv1-rkllm-w4a16`, `feat/tv3-zram-profiler`) và tạo Pull Request vào `main`.
- Mọi kết quả đo đạc tổng hợp lưu dưới dạng `.csv` hoặc `.json` có cấu trúc rõ ràng trong `results/` kèm metadata phần cứng và cấu hình chạy từ `configs/`.
