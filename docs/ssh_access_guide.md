# Hướng dẫn Truy cập Từ xa Orange Pi 5 (SSH & Tailscale)
**Dự án:** NCKH SLM Offline – Team B (Phúc – Nhật – Hưng)  
**Deliverable Task P0-02:** `system_info.json + hướng dẫn SSH`

---

## 1. Thông số Mạng & Địa chỉ Truy cập

| Kênh kết nối | Địa chỉ IP / Hostname | Cổng | Tài khoản | Ghi chú |
| :--- | :--- | :--- | :--- | :--- |
| **Tailscale (Khuyên dùng)** | `100.115.216.86` hoặc `orangepi5` | `22` | `orangepi` | Truy cập an toàn từ mọi mạng (4G, Wi-Fi trường, ở nhà) |
| **Mạng Nội bộ (LAN FPTU)** | `10.136.121.206` | `22` | `orangepi` | Chỉ khả dụng khi cùng dải subnet mạng nội bộ |

---

## 2. Thiết lập SSH Client cho Thành viên (Phúc, Nhật, Hưng)

### Bước 1: Tạo SSH Key cá nhân (nếu chưa có)
Trên máy Host (Windows PowerShell / macOS / Linux terminal của mỗi thành viên):
```bash
ssh-keygen -t ed25519 -C "ten_thanh_vien@edge-slm-research"
```
*(Lưu ý: Không đặt mật khẩu rỗng nếu máy có người khác sử dụng).*

### Bước 2: Cấp quyền truy cập trên Orange Pi 5
Gửi chuỗi khóa công khai (`~/.ssh/id_ed25519.pub`) cho Nhật để thêm vào file:
```bash
/home/orangepi/.ssh/authorized_keys
```

### Bước 3: Cấu hình `~/.ssh/config` trên máy cá nhân
Thêm khối cấu hình sau vào file `~/.ssh/config` (hoặc `C:\Users\<user>\.ssh\config` trên Windows):

```ssh-config
Host orangepi5
    HostName 100.115.216.86
    User orangepi
    Port 22
    IdentityFile ~/.ssh/id_ed25519
    ServerAliveInterval 60
    ServerAliveCountMax 3

Host orangepi5-lan
    HostName 10.136.121.206
    User orangepi
    Port 22
    IdentityFile ~/.ssh/id_ed25519
```

### Bước 4: Kiểm tra kết nối
```bash
ssh orangepi5
```
Khi đăng nhập thành công, terminal sẽ hiển thị:
```text
orangepi@orangepi5:~$
```

---

## 3. Đường dẫn Dự án và Môi trường Python trên Bo mạch

- **Thư mục dự án chính:** `/home/orangepi/TeamB_SLM`
- **Môi trường Conda chuẩn:** `/home/orangepi/miniconda3/envs/teamb_slm`
- **Kích hoạt môi trường:**
  ```bash
  conda activate teamb_slm
  cd /home/orangepi/TeamB_SLM
  ```

---

## 4. Quy tắc An toàn khi làm việc từ xa
1. **Không tắt nguồn đột ngột:** Orange Pi 5 chạy hệ điều hành trên NVMe SSD, tắt nguồn đột ngột có thể gây lỗi filesystem. Luôn dùng lệnh `sudo poweroff` hoặc thông báo cho người quản lý bo mạch.
2. **Không commit khóa bảo mật / mật khẩu** lên GitHub repository.
3. **Chỉ một người chạy benchmark nặng tại một thời điểm** để đảm bảo đo lường bộ nhớ (Peak RAM) và độ trễ (TTFT/Tokens/s) chính xác, không bị nhiễu do tranh chấp tài nguyên CPU/NPU.
