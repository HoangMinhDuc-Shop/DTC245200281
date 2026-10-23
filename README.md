# CINEMASTER - HỆ THỐNG ĐẶT VÉ XEM PHIM & GIÁM SÁT DEVOPS TOÀN DIỆN

Hệ thống ứng dụng web đặt vé xem phim trực tuyến hiện đại, tích hợp cơ sở dữ liệu MySQL, giao diện quản trị phpMyAdmin và hệ thống giám sát toàn diện chuẩn DevOps sử dụng Prometheus & Grafana trên nền tảng Docker & Ubuntu.

---

## 🏛 1. Kiến Trúc Hệ Thống (System Architecture)

```
                                      [ NGƯỜI DÙNG & QUẢN TRỊ ]
                                                  │
                                         Port 80  ▼
                           ┌──────────────────────────────────────────────┐
                           │            Nginx (Reverse Proxy)             │
                           └──────────────────────┬───────────────────────┘
                                                  │
                  ┌───────────────────────────────┼───────────────────────────────┐
           Port 80│                        Port 8080│                        Port 3000│
                  ▼                               ▼                               ▼
       ┌─────────────────────┐         ┌─────────────────────┐         ┌─────────────────────┐
       │   NodeJS Web App    │         │     phpMyAdmin      │         │  Grafana Dashboard  │
       │ (Auth, Booking, EJS)│         │(Quản lý CSDL Web UI)│         │(Trực quan hóa số liệu)
       └──────────┬──────────┘         └──────────┬──────────┘         └──────────▲──────────┘
                  │                               │                               │ Query
                  └───────────────┬───────────────┘                               │
                                  ▼ Port 3306                                     │
                       ┌─────────────────────┐                         ┌──────────┴──────────┐
                       │   MySQL Database    │◄── mysqld_exporter ─────┤     Prometheus      │
                       │(Users, Orders, Seats)│       (Port 9104)      │  (Thu thập Metrics) │
                       └─────────────────────┘                         └──────────▲──────────┘
                                                                                  │
                               Ubuntu Host OS ─────── node_exporter ──────────────┘
                                                      (Port 9100)
```

---

## 🚀 2. Bảng Danh Sách Dịch Vụ & Cổng Truy Cập (Port Mapping)

| Dịch vụ | Cổng (Port) | Chức năng | Tài khoản mặc định |
| :--- | :--- | :--- | :--- |
| **Web Ứng Dụng** | `80` (hoặc `3001`) | Giao diện đặt vé phim, chọn ghế, xuất vé QR | `khachhang` / `123456` |
| **Admin Portal** | `80/admin` | Quản trị doanh thu, danh sách đơn hàng | `admin` / `admin123` |
| **Cổng Soát Vé** | `80/checkin` | Soát vé QR tại cổng rạp phim | Không cần đăng nhập |
| **phpMyAdmin** | `8080` | Giao diện quản lý CSDL MySQL trực quan | `root` / `rootpassword` |
| **Grafana** | `3000` | Dashboard giám sát CPU, RAM, MySQL, Doanh thu | `admin` / `admin` |
| **Prometheus** | `9090` | Thu thập và lưu trữ time-series metrics | Không cần đăng nhập |
| **MySQL Server** | `3306` | Hệ quản trị cơ sở dữ liệu quan hệ | `root` / `rootpassword` |

---

## 🛠 3. Hướng Dẫn Cài Đặt & Khởi Chạy (Quick Start)

### Yêu cầu tiên quyết:
* Hệ điều hành: Ubuntu 20.04/22.04 LTS (hoặc máy ảo VMware/WSL2).
* Đã cài đặt **Docker** và **Docker Compose**.

### Các bước thực hiện:

#### Bước 1: Sao chép mã nguồn và vào thư mục dự án
```bash
git clone <URL_REPOSITORY_CUA_BAN>
cd movie-system
```

#### Bước 2: Cấu hình biến môi trường
Tạo file `.env` từ file mẫu `.env.example`:
```bash
cp .env.example .env
```
*(Tùy chọn: Có thể điền `TMDB_API_KEY` nếu muốn tự động đồng bộ thêm phim từ The Movie Database).*

#### Bước 3: Khởi động toàn bộ cụm hệ thống bằng Docker Compose
```bash
sudo docker compose up -d --build
```

#### Bước 4: Kiểm tra trạng thái hoạt động
```bash
sudo docker compose ps
```
Khi thấy tất cả các container (`movie_nginx`, `movie_web`, `mysql_db`, `movie_phpmyadmin`, `prometheus`, `grafana`, `node_exporter`, `mysql_exporter`) đều ở trạng thái **`Up`** là hệ thống đã sẵn sàng 100%!

---

## ✨ 4. Các Chức Năng Nổi Bật Của Dự Án

### 🎬 A. Phía Khách Hàng (Client Portal)
* **Xem phim & Chi tiết:** Hiển thị Poster HD, điểm đánh giá, thể loại và tóm tắt phim chuẩn rạp.
* **Sơ đồ chọn ghế tương tác thời gian thực:** Phân loại Ghế Thường, Ghế VIP, tự động tính tổng tiền.
* **Chống đặt trùng ghế (Race Condition Protection):** Ghế đã được mua sẽ lập tức bị khóa đỏ (`Occupied`) và lưu vào CSDL, người khác không thể đặt đè.
* **Vé điện tử (E-Ticket):** Xuất vé điện tử có mã đặt vé và mã QR Check-in chuẩn rạp phim.

### 🔑 B. Phân Quyền & Bảo Mật (Authentication)
* Đăng ký, đăng nhập và đăng xuất phiên làm việc an toàn.
* Mật khẩu được mã hóa an toàn bằng thuật toán `scrypt` kèm salt 16-byte ngẫu nhiên.
* Cookie phiên được ký chống giả mạo bằng chữ ký điện tử `HMAC-SHA256`.

### 🛡 C. Phía Quản Trị & Soát Vé
* **Cổng Soát Vé (`/checkin`):** Nhập mã vé hoặc quét QR để kiểm tra tính hợp lệ của vé, ngăn chặn tình trạng dùng lại vé cũ (`USED`).
* **Trang Admin (`/admin`):** Thống kê tổng doanh thu thực tế và quản lý toàn bộ danh sách vé đã bán ra.

### 🗄 D. Quản Trị CSDL Với phpMyAdmin (`Port 8080`)
* Truy cập `http://<IP>:8080` để xem và thao tác trực tiếp trên các bảng:
  - `movies`: Danh sách phim chiếu rạp.
  - `users`: Tài khoản khách hàng và quản trị viên.
  - `orders`: Lịch sử đơn đặt vé.
  - `booked_seats`: Dữ liệu ghế đã đặt theo từng suất chiếu.

### 📊 E. Hệ Thống Giám Sát DevOps (Prometheus & Grafana)
* **Giám sát hạ tầng Ubuntu OS:** Đo tải CPU, bộ nhớ RAM, dung lượng Disk I/O, Network Traffic qua `node_exporter`.
* **Giám sát hiệu năng Database:** Đo số lượng kết nối, truy vấn mỗi giây (QPS), buffer pool qua `mysqld_exporter`.
* **Đo lường chỉ số kinh doanh (Business Metrics):**
  - `movie_tickets_booked_total`: Đếm số vé bán ra theo phim và loại ghế.
  - `movie_revenue_vnd_total`: Đo tổng doanh thu theo thời gian thực (VND).
  - `active_sessions_total`: Đo số lượng phiên người dùng đang hoạt động.

---

## 📁 5. Cấu Trúc Thư Mục Dự Án

```text
movie-system/
├── docker-compose.yml          # File điều phối toàn bộ các container Docker
├── .env.example                # File mẫu cấu hình biến môi trường
├── .my.cnf                     # Cấu hình chứng thực cho mysqld_exporter
├── README.md                   # Tài liệu hướng dẫn sử dụng và triển khai
├── nginx/
│   └── nginx.conf              # Cấu hình Nginx Reverse Proxy cổng 80
├── monitoring/
│   └── prometheus.yml          # Cấu hình các target thu thập dữ liệu Prometheus
└── web/
    ├── Dockerfile              # Dockerfile đóng gói ứng dụng NodeJS
    ├── package.json            # Khai báo thư viện và phụ thuộc NodeJS
    ├── index.js                # Toàn bộ mã nguồn Backend, APIs & Metrics
    └── views/                  # Giao diện EJS (HTML/CSS Glassmorphism)
        ├── _head.ejs           # Header & CSS Dark Mode chung
        ├── index.ejs           # Trang chủ & Sơ đồ chọn ghế Realtime
        ├── login.ejs           # Trang đăng nhập
        ├── register.ejs        # Trang đăng ký tài khoản
        ├── success.ejs         # Tấm vé điện tử E-Ticket QR
        ├── checkin.ejs         # Cổng soát vé tại rạp
        └── admin.ejs           # Bảng điều khiển quản trị viên
```
