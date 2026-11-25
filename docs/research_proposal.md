# Đề cương Nghiên cứu: Triển khai và Lượng tử hóa SLM Ngoại tuyến trên Thiết bị Biên

## 1. Bài toán và Mục tiêu
Triển khai các mô hình ngôn ngữ nhỏ (3B tham số) hoàn toàn ngoại tuyến trên thiết bị biên giới hạn bộ nhớ **Orange Pi 5 (8GB LPDDR4X RAM, Rockchip RK3588S)** mà vẫn đảm bảo:
- Không xảy ra lỗi tràn bộ nhớ (OOM) dưới ngưỡng an toàn **6.5 GiB** (bao gồm OS, runtime, model weights và KV Cache).
- Độ trễ phản hồi (TTFT) và tốc độ sinh token (Tokens/s) đáp ứng nhu cầu tương tác thời gian thực.
- Duy trì chất lượng suy luận trên tập đánh giá phân tầng 60 câu hỏi.

## 2. Phạm vi mô hình và Ma trận thực nghiệm
- **Mô hình:** `Qwen2.5-3B-Instruct`, `Llama-3.2-3B-Instruct`.
- **Đối chứng CPU (`llama.cpp`):** GGUF `Q8_0`, `Q4_K_M`.
- **Tăng tốc NPU (`RKLLM`):** `W8A8`, `W4A16`.
- **Các mức Context Length khảo sát KV Cache:** `512`, `1024`, `2048`, `4096` tokens.

## 3. Biến đo lường và Tiêu chí đánh giá
1. **Bộ nhớ (Memory Footprint):** Peak RSS / System Memory Used (MiB/GiB), mức sử dụng ZRAM, khoảng an toàn so với ngưỡng 6.5 GiB.
2. **Độ trễ và Thông lượng:**
   - **TTFT (Time To First Token):** Thời gian pha Prefill từ khi nhận prompt đến token đầu tiên.
   - **Decode Speed (Tokens/s):** Tốc độ sinh chuỗi ở pha Decode.
3. **Độ ổn định dài hạn:** Stress-test **15 lượt hội thoại liên tục** (multi-turn context accumulation).
4. **Chất lượng mô hình:** Đánh giá có hệ thống trên **60 câu hỏi kiểm thử phân tầng** (TV4 phụ trách).

## 4. Lộ trình 4 Milestones
- **Milestone 1:** Memory Budget (<= 6.5 GiB), thiết lập ZRAM 4GB, chạy CPU baseline (`llama.cpp` GGUF `Q8_0` & `Q4_K_M`).
- **Milestone 2:** Biên dịch & hiệu chuẩn mô hình trên Host x86 sang RKLLM (`W8A8`, `W4A16`), chạy thử nghiệm trên NPU RK3588S.
- **Milestone 3:** Khảo sát KV Cache (`512`, `1024`, `2048`, `4096`) và chấm điểm chất lượng trên bộ 60 câu hỏi.
- **Milestone 4:** Tối ưu pha Prefill vs Decode, stress-test 15 lượt hội thoại liên tục và đóng gói ứng dụng Chatbot ngoại tuyến.
