# CINEMASTER - HỆ THỐNG ĐẶT VÉ PHIM & GIÁM SÁT DEVOPS TOÀN DIỆN

Hệ thống ứng dụng web đặt vé xem phim trực tuyến hiện đại, tích hợp cơ sở dữ liệu MySQL, giao diện quản trị phpMyAdmin, hệ thống giám sát Prometheus/Grafana, hệ thống ghi log tập trung Loki/Promtail và áp dụng các tiêu chuẩn Hardening bảo mật nâng cao.

---

## 🏛 1. Kiến Trúc Hệ Thống (System Architecture)

```
                                      [ NGƯỜI DÙNG & QUẢN TRỊ ]
                                                  │
                                         Port 80  ▼
                           ┌──────────────────────────────────────────────┐
                           │       Nginx (Reverse Proxy + Hardening)      │
                           └──────────────────────┬───────────────────────┘
                                                  │
                  ┌───────────────────────────────┼───────────────────────────────┐
           Port 80│                        Port 8080│                        Port 3000│
                  ▼                               ▼                               ▼
       ┌─────────────────────┐         ┌─────────────────────┐         ┌─────────────────────┐
       │   NodeJS Web App    │         │     phpMyAdmin      │         │  Grafana Dashboard  │
       │ (Auth, Booking, EJS)│         │(Quản lý CSDL Web UI)│         │ (Giám sát & Logs)   │
       └──────────┬──────────┘         └──────────┬──────────┘         └──────────▲──────────┘
                  │                               │                               │ Query PromQL/LogQL
                  └───────────────┬───────────────┘                               │
                                  ▼ Port 3306                         ┌───────────┴───────────┐
                       ┌─────────────────────┐                        │ Prometheus  │  Loki   │
                       │   MySQL Database    │                        │  (Metrics)  │ (Logs)  │
                       │(Users, Orders, Seats)│                        └─────▲───────┴────▲────┘
                       └─────────────────────┘                              │            │
                                  ▲                                         │            │
                                  ├────── mysqld_exporter (9104) ───────────┤            │
                                  ├────── node_exporter   (9100) ───────────┤            │
                                  ├────── cadvisor        (8080) ───────────┘            │
                                  └────── promtail (/var/run/docker.sock) ───────────────┘
```

---

## 📋 2. Bảng Danh Sách Dịch Vụ & Cổng Truy Cập (Port Mapping)

| Dịch vụ | Cổng (Port) | Chức năng | Tài khoản mặc định |
| :--- | :--- | :--- | :--- |
| **Web Ứng Dụng** | `80` (hoặc `3001`) | Đặt vé xem phim, chọn ghế, xuất vé QR | `khachhang` / `123456` |
| **Admin Portal** | `80/admin` | Quản trị doanh thu, danh sách đơn hàng | `admin` / `admin123` |
| **Cổng Soát Vé** | `80/checkin` | Soát vé QR tại cổng rạp phim | Không cần đăng nhập |
| **phpMyAdmin** | `8080` | Giao diện quản lý CSDL MySQL trực quan | `root` / `rootpassword` |
| **Grafana** | `3000` | Dashboard giám sát Metrics & Logs | `admin` / `admin` |
| **Loki** | `3100` | Máy chủ lưu trữ và xử lý Log tập trung | Không cần đăng nhập |
| **Prometheus** | `9090` | Thu thập và lưu trữ time-series metrics | Không cần đăng nhập |
| **MySQL Server** | `3306` | Hệ quản trị cơ sở dữ liệu quan hệ | `root` / `rootpassword` |

---

## 🛡 3. Báo Cáo Hardening Bảo Mật (Tiêu Chí 6)

Dự án áp dụng đầy đủ **4 biện pháp bảo mật nâng cao**:

1. **Network Isolation (Phân tách mạng nội bộ Docker):**
   - Tạo 2 mạng độc lập: `frontend_net` và `backend_net`.
   - Cơ sở dữ liệu `mysql_db` chỉ kết nối vào `backend_net`, hoàn toàn không mở cổng thô ra ngoài Internet, ngăn chặn tối đa nguy cơ tấn công brute-force cổng DB từ bên ngoài.
2. **Nginx Security Headers (Tiêu chí 3 & 6):**
   - `X-Frame-Options: SAMEORIGIN`: Chống tấn công Clickjacking.
   - `X-Content-Type-Options: nosniff`: Chống tấn công MIME-sniffing.
   - `X-XSS-Protection: 1; mode=block`: Bật bộ lọc chống Cross-Site Scripting (XSS).
   - `Referrer-Policy: strict-origin-when-cross-origin`: Bảo vệ rò rỉ URL nhạy cảm.
   - `server_tokens off`: Ẩn thông tin phiên bản web server để tránh bị khai thác lỗ hổng đã biết.
3. **Mã Hóa Mật Khẩu Nâng Cao (Password Hashing):**
   - Sử dụng thuật toán `scrypt` kết hợp với chuỗi `salt` ngẫu nhiên 16-byte cho mỗi tài khoản, chống lại tấn công Rainbow Table và Brute-force tốc độ cao.
4. **Bảo Vệ Phiên Làm Việc (Session Security):**
   - Cookie phiên được ký điện tử bằng `HMAC-SHA256` với khóa bí mật `SESSION_SECRET`.
   - Xác thực chữ ký bằng hàm `crypto.timingSafeEqual` để loại trừ hoàn toàn nguy cơ tấn công Timing Attack.

---

## 🪵 4. Hệ Thống Log Tập Trung Loki + Promtail (Tiêu Chí 5)

Hệ thống sử dụng **Promtail** tự động bắt các dòng log từ Docker Socket (`/var/run/docker.sock`) và gửi về **Loki**. 

### Các câu truy vấn LogQL cơ bản trên Grafana (Explore > Data source: Loki):
1. **Xem toàn bộ log của ứng dụng Web đặt vé:**
   ```logql
   {container_name="movie_web"}
   ```
2. **Lọc các thao tác Đặt vé thành công (POST /book):**
   ```logql
   {container_name="movie_web"} |= "POST /book"
   ```
3. **Lọc log cảnh báo hoặc lỗi hệ thống:**
   ```logql
   {container_name="movie_web"} |~ "(?i)(error|lỗi|fail|warn)"
   ```
4. **Xem log truy cập từ Nginx Reverse Proxy:**
   ```logql
   {container_name="movie_nginx"}
   ```

---

## 📊 5. Hệ Thống Giám Sát Prometheus & Grafana (Tiêu Chí 4)

Thu thập và hiển thị toàn diện trên 3 tầng:
1. **Tầng Hệ điều hành (Host):** `node_exporter` đo CPU Usage, RAM, Disk I/O, Network Traffic.
2. **Tầng Container:** `cadvisor` đo lượng tài nguyên tiêu thụ chi tiết của từng container Docker.
3. **Tầng Cơ sở dữ liệu:** `mysql_exporter` đo số lượng kết nối (threads), QPS, buffer pool.
4. **Tầng Nghiệp vụ Web (Business Metrics):**
   - Tổng doanh thu bán vé (VND): `sum(movie_revenue_vnd_total)`
   - Tỷ lệ vé bán theo phim: `sum by (movie_title) (movie_tickets_booked_total)`
   - Số phiên người dùng online: `active_sessions_total`

---

## 🚀 6. Hướng Dẫn Cài Đặt & Triển Khai (Quick Start)

```bash
# 1. Clone repository
git clone https://github.com/HoangMinhDuc-Shop/DTC245200281.git
cd DTC245200281

# 2. Khởi tạo file môi trường
cp .env.example .env

# 3. Khởi chạy toàn bộ hệ thống
sudo docker compose up -d --build
```
