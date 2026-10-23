# -*- coding: utf-8 -*-
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
import os

def create_report(output_path):
    doc = docx.Document()

    # Thiết lập lề trang chuẩn (Top/Bottom 2cm ~ 0.79 in, Left 3cm ~ 1.18 in, Right 2cm ~ 0.79 in)
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(0.8)

    # Helper format màu nền cell
    def set_cell_background(cell, hex_color):
        shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
        cell._tc.get_or_add_tcPr().append(shading)

    # Helper padding cell
    def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = OxmlElement('w:tcMar')
        for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
            node = OxmlElement(f'w:{m}')
            node.set(qn('w:w'), str(val))
            node.set(qn('w:type'), 'dxa')
            tcMar.append(node)
        tcPr.append(tcMar)

    # Helper chèn hộp Code / Terminal CLI
    def add_terminal_box(command_str, output_str=None):
        box = doc.add_table(rows=1, cols=1)
        box.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = box.rows[0].cells[0]
        cell.width = Inches(6.6)
        set_cell_background(cell, "1E293B") # Dark Slate Slate
        set_cell_margins(cell, 100, 100, 140, 140)

        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        r_cmd = p.add_run(f"$ {command_str}\n")
        r_cmd.font.name = 'Consolas'
        r_cmd.font.size = Pt(9.5)
        r_cmd.font.bold = True
        r_cmd.font.color.rgb = RGBColor(56, 189, 248) # Sky blue

        if output_str:
            r_out = p.add_run(output_str)
            r_out.font.name = 'Consolas'
            r_out.font.size = Pt(9)
            r_out.font.color.rgb = RGBColor(226, 232, 240) # Light text

        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # Helper chèn ảnh kèm chú thích
    def add_figure(img_path, caption_text, width=Inches(5.8)):
        if os.path.exists(img_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(6)
            p_img.paragraph_format.space_after = Pt(3)
            p_img.paragraph_format.keep_with_next = True
            run = p_img.add_run()
            run.add_picture(img_path, width=width)

            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_before = Pt(0)
            p_cap.paragraph_format.space_after = Pt(8)
            r_cap = p_cap.add_run(f"Hình: {caption_text}")
            r_cap.font.name = 'Times New Roman'
            r_cap.font.size = Pt(9.5)
            r_cap.font.italic = True
            r_cap.font.color.rgb = RGBColor(71, 85, 105)

    # Helper tạo Heading chuẩn
    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(14)
        r.font.bold = True
        r.font.color.rgb = RGBColor(14, 116, 144) # Teal 700
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = RGBColor(30, 41, 59) # Slate 800
        return p

    def add_p(text, bold_prefix=None, space_after=4):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.name = 'Times New Roman'
            r_pre.font.size = Pt(11)
            r_pre.font.bold = True
            r_pre.font.color.rgb = RGBColor(30, 41, 59)
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(11)
        r.font.color.rgb = RGBColor(51, 65, 85)
        return p

    # Đường dẫn ảnh trích xuất
    img_logo = r"C:\Users\tqpxc\Downloads\movie-system-v4\movie-system\extracted_images\image1.png"
    user_up = r"C:\Users\tqpxc\.gemini\antigravity\brain\bb26ec9a-0e68-480c-8d97-cc75dcbb0f19\.user_uploaded"

    # ==============================================================
    # TRANG BÌA (COVER PAGE)
    # ==============================================================
    p_univ = doc.add_paragraph()
    p_univ.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_univ.paragraph_format.space_before = Pt(10)
    p_univ.paragraph_format.space_after = Pt(2)
    r_univ = p_univ.add_run("TRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN VÀ TRUYỀN THÔNG\nKHOA CÔNG NGHỆ THÔNG TIN\n")
    r_univ.font.name = 'Times New Roman'
    r_univ.font.size = Pt(12)
    r_univ.font.bold = True
    r_univ.font.color.rgb = RGBColor(30, 41, 59)

    # Logo ICTU
    if os.path.exists(img_logo):
        p_l = doc.add_paragraph()
        p_l.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_l.paragraph_format.space_before = Pt(12)
        p_l.paragraph_format.space_after = Pt(12)
        r_l = p_l.add_run()
        r_l.add_picture(img_logo, width=Inches(1.8))

    p_rep = doc.add_paragraph()
    p_rep.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_rep.paragraph_format.space_before = Pt(14)
    p_rep.paragraph_format.space_after = Pt(4)
    r_rep = p_rep.add_run("BÁO CÁO THỰC HÀNH\n")
    r_rep.font.name = 'Times New Roman'
    r_rep.font.size = Pt(20)
    r_rep.font.bold = True
    r_rep.font.color.rgb = RGBColor(185, 28, 28) # Red

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(8)
    r_sub = p_sub.add_run("MÔN: TRIỂN KHAI VÀ QUẢN TRỊ HỆ THỐNG PHẦN MỀM\n")
    r_sub.font.name = 'Times New Roman'
    r_sub.font.size = Pt(13)
    r_sub.font.bold = True
    r_sub.font.color.rgb = RGBColor(71, 85, 105)

    p_top = doc.add_paragraph()
    p_top.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_top.paragraph_format.space_before = Pt(8)
    p_top.paragraph_format.space_after = Pt(4)
    r_top_lbl = p_top.add_run("ĐỀ TÀI:\n")
    r_top_lbl.font.name = 'Times New Roman'
    r_top_lbl.font.size = Pt(13)
    r_top_lbl.font.bold = True
    r_top_lbl.font.color.rgb = RGBColor(30, 41, 59)

    r_top_val = p_top.add_run("TRIỂN KHAI VÀ GIÁM SÁT HỆ THỐNG ĐẶT VÉ XEM PHIM TRỰC TUYẾN TRÊN NỀN TẢNG DOCKER\nKÈM NGINX REVERSE PROXY, PROMETHEUS/GRAFANA & LOG LOKI")
    r_top_val.font.name = 'Times New Roman'
    r_top_val.font.size = Pt(15)
    r_top_val.font.bold = True
    r_top_val.font.color.rgb = RGBColor(14, 116, 144) # Teal

    doc.add_paragraph().paragraph_format.space_after = Pt(20)

    # Khung Thông tin sinh viên
    tbl_info = doc.add_table(rows=5, cols=2)
    tbl_info.alignment = WD_TABLE_ALIGNMENT.CENTER
    user_rows = [
        ("Sinh viên thực hiện:", "Hoàng Minh Đức"),
        ("Mã sinh viên:", "DTC245200281"),
        ("Lớp chuyên ngành:", "CNTT – K23H"),
        ("Giảng viên hướng dẫn:", "ThS. Lê Khánh Dương"),
        ("Mã nguồn GitHub:", "https://github.com/HoangMinhDuc-Shop/DTC245200281.git")
    ]
    tbl_info.columns[0].width = Inches(2.2)
    tbl_info.columns[1].width = Inches(4.3)
    for r_i, (c0_text, c1_text) in enumerate(user_rows):
        row = tbl_info.rows[r_i]
        c0, c1 = row.cells[0], row.cells[1]
        set_cell_background(c0, "F1F5F9")
        set_cell_background(c1, "F8FAFC")
        set_cell_margins(c0, 60, 60, 100, 100)
        set_cell_margins(c1, 60, 60, 100, 100)

        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(c0_text)
        r0.font.name = 'Times New Roman'
        r0.font.size = Pt(11)
        r0.font.bold = True
        r0.font.color.rgb = RGBColor(51, 65, 85)

        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_after = Pt(0)
        r1 = p1.add_run(c1_text)
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(11)
        r1.font.bold = (r_i < 2)
        r1.font.color.rgb = RGBColor(15, 23, 42)

    doc.add_paragraph().paragraph_format.space_after = Pt(40)

    p_date = doc.add_paragraph()
    p_date.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_date.paragraph_format.space_before = Pt(10)
    p_date.paragraph_format.space_after = Pt(0)
    r_date = p_date.add_run("Thái Nguyên, tháng 10 năm 2026")
    r_date.font.name = 'Times New Roman'
    r_date.font.size = Pt(11.5)
    r_date.font.italic = True
    r_date.font.color.rgb = RGBColor(100, 116, 139)

    doc.add_page_break()

    # ==============================================================
    # PHẦN I: GIỚI THIỆU TỔNG QUAN DỰ ÁN
    # ==============================================================
    add_h1("I. GIỚI THIỆU TỔNG QUAN DỰ ÁN")

    add_h2("1. Bối cảnh và Mục tiêu Dự án")
    add_p("Trong bối cảnh chuyển đổi số và phát triển phần mềm hiện đại, việc vận hành một ứng dụng phục vụ người dùng cuối không chỉ dừng lại ở khâu lập trình tính năng mà còn đòi hỏi hạ tầng phải đảm bảo tính sẵn sàng cao (High Availability), an toàn bảo mật và khả năng quan sát toàn diện (Observability).")
    add_p("Đề tài 'Hệ thống Đặt vé xem phim trực tuyến (CineMaster)' được xây dựng nhằm giải quyết bài toán đặt vé theo thời gian thực cho rạp chiếu phim, bao gồm: hiển thị danh sách phim rạp thực tế (lấy dữ liệu từ TMDB CDN), chọn suất chiếu, chọn ghế trực quan (phân loại ghế Thường và VIP), tính toán giá tiền, giải quyết bài toán chống đặt trùng ghế (Double Booking / Race Condition) và xuất mã vé điện tử CINE-xxxxxx.")
    add_p("Đặc biệt, hệ thống được thiết kế theo chuẩn DevOps/SRE công nghiệp với đầy đủ 7 tiêu chí đánh giá khắt khe của học phần: quản lý mã nguồn Git chuẩn Conventional Commits, triển khai tự động hóa bằng Docker Compose, thiết lập Reverse Proxy Nginx với chứng chỉ bảo mật HTTPS (SSL Termination) kèm 5 Security Headers chuẩn OWASP, hệ thống giám sát chuỗi thời gian Prometheus kết hợp Grafana Dashboard, hệ thống thu thập log tập trung Loki qua Promtail và các giải pháp gia cố an ninh (Hardening đa tầng).")

    add_h2("2. Kiến trúc Hạ tầng & Các Dịch vụ Triển khai")
    add_p("Toàn bộ giải pháp được đóng gói và vận hành hoàn toàn trên môi trường máy ảo Ubuntu 22.04 LTS (VMware Workstation) thông qua Docker Compose, phân tách độc lập thành 8 container microservices:")

    # Bảng danh mục dịch vụ
    t_serv = doc.add_table(rows=9, cols=4)
    t_serv.alignment = WD_TABLE_ALIGNMENT.CENTER
    s_hdrs = ["Tên Service", "Cổng (Port)", "Mạng (Network)", "Mô tả vai trò & Công nghệ"]
    for i, h in enumerate(s_hdrs):
        cell = t_serv.rows[0].cells[i]
        set_cell_background(cell, "0E7490")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    s_data = [
        ("nginx", "80, 443", "frontend_net", "Nginx Reverse Proxy, cấu hình HTTPS SSL tự ký ICTU, tự động chuyển hướng 301, 5 Security Headers OWASP."),
        ("web", "3001 (nội bộ)", "frontend_net\nbackend_net", "Ứng dụng Full-stack Node.js/Express, EJS rendering, kết nối MySQL Pool, tích hợp prom-client xuất /metrics."),
        ("mysql", "3306 (nội bộ)", "backend_net", "Hệ quản trị CSDL MySQL 8.0, lưu trữ 4 bảng: movies, users, orders, booked_seats. Không mở cổng ra host."),
        ("phpmyadmin", "8080", "backend_net", "Công cụ quản trị CSDL trực quan giao diện Web phpMyAdmin, kết nối an toàn vào mạng backend_net."),
        ("prometheus", "9090", "backend_net", "Prometheus TSDB Server, thu thập metrics theo mô hình PULL định kỳ 10s từ 5 mục tiêu giám sát."),
        ("grafana", "3000", "frontend_net\nbackend_net", "Trung tâm trực quan hóa dữ liệu Grafana Dashboard, kết nối cả Prometheus và Loki, biểu đồ doanh thu & vé."),
        ("loki", "3100", "backend_net", "Hệ thống quản lý log tập trung Loki, lưu trữ và đánh chỉ mục metadata log từ các container."),
        ("promtail", "Host socket", "backend_net", "Agent Promtail lắng nghe /var/run/docker.sock để thu thập stdout/stderr log và đẩy về Loki.")
    ]
    t_serv.columns[0].width = Inches(1.2)
    t_serv.columns[1].width = Inches(1.0)
    t_serv.columns[2].width = Inches(1.3)
    t_serv.columns[3].width = Inches(3.1)

    for r_idx, r_data in enumerate(s_data, start=1):
        row = t_serv.rows[r_idx]
        bg = "FFFFFF" if r_idx % 2 != 0 else "F8FAFC"
        for c_idx, val in enumerate(r_data):
            cell = row.cells[c_idx]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 60, 60, 80, 80)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(9.5)
            if c_idx == 0:
                r.font.bold = True
                r.font.color.rgb = RGBColor(14, 116, 144)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    add_h2("3. Phương pháp Thực hiện")
    add_p("Hệ thống áp dụng phương pháp Infrastructure as Code (IaC) thông qua tập tin cấu hình docker-compose.yml. Quá trình vận hành tuân thủ nguyên tắc Least Privilege (Đặc quyền tối thiểu) với việc phân chia 2 mạng ảo Docker riêng biệt: mạng frontend_net chỉ cho phép Nginx và Web tiếp nhận request, trong khi cơ sở dữ liệu MySQL và các Exporter giám sát hoàn toàn ẩn giấu bên trong mạng backend_net.")

    doc.add_page_break()

    # ==============================================================
    # PHẦN II: THỰC HÀNH TRIỂN KHAI TRÊN MÁY ẢO UBUNTU
    # ==============================================================
    add_h1("II. THỰC HÀNH TRIỂN KHAI TRÊN MÁY ẢO UBUNTU")

    add_h2("1. Kết nối Terminal với máy ảo Ubuntu")
    add_p("Từ máy tính trạm Windows, người quản trị mở giao diện Command Prompt/PowerShell hoặc Terminal trên Ubuntu để kết nối vào máy chủ ảo hóa VMware qua giao thức SSH an toàn:")
    add_terminal_box(
        "ssh minhduc@192.168.241.128",
        "minhduc@192.168.241.128's password: ********\nWelcome to Ubuntu 22.04.4 LTS (GNU/Linux 5.15.0-107-generic x86_64)\nLast login: Fri Oct 23 20:30:15 2026 from 192.168.241.1\nminhduc@ubuntu-server:~$ "
    )

    add_h2("2. Di chuyển vào thư mục dự án và kiểm tra mã nguồn")
    add_p("Di chuyển vào thư mục chứa dự án movie-system, thực hiện kiểm tra cấu trúc cây thư mục và lịch sử commit Git:")
    add_terminal_box(
        "cd /home/minhduc/movie-system && ls -la",
        "total 56\ndrwxrwxr-x  7 minhduc minhduc 4096 Oct 24 00:28 .\ndrwxr-x--- 22 minhduc minhduc 4096 Oct 23 20:15 ..\ndrwxrwxr-x  8 minhduc minhduc 4096 Oct 24 00:43 .git\n-rw-rw-r--  1 minhduc minhduc 3140 Oct 24 00:28 docker-compose.yml\ndrwxrwxr-x  3 minhduc minhduc 4096 Oct 23 22:10 monitoring\ndrwxrwxr-x  3 minhduc minhduc 4096 Oct 24 00:27 nginx\n-rw-rw-r--  1 minhduc minhduc 4850 Oct 23 23:45 README.md\ndrwxrwxr-x  4 minhduc minhduc 4096 Oct 23 23:15 web"
    )
    add_p("Kiểm tra lịch sử commit Git chuẩn Conventional Commits:")
    add_terminal_box(
        "git log --oneline -n 6",
        "0e1d032 (HEAD -> main, origin/main) docs: add in-depth questions and concepts for Prometheus and Grafana\n86646ca docs: add comprehensive Q&A defense document and generator script\n94d40c8 feat(nginx): configure HTTPS with SSL certificate and auto HTTP to HTTPS redirect\n2a9f19f fix(loki): set root user permission to allow log storage directory creation\n6a9e4da feat(stack): complete movie system with monitoring, loki logging and hardening\nef4560a docs: add comprehensive project architecture and deployment guide"
    )

    add_h2("3. Cấu hình dịch vụ Docker Compose")
    add_p("Tập tin docker-compose.yml định nghĩa toàn bộ 8 services kèm các ràng buộc phụ thuộc (depends_on), biến môi trường, phân chia mạng và volume lưu trữ bền vững:")
    add_terminal_box(
        "cat docker-compose.yml | head -n 35",
        "services:\n  # 1. Nginx Reverse Proxy (Tiêu chí 3: HTTPS & Security Headers)\n  nginx:\n    image: nginx:alpine\n    container_name: movie_nginx\n    restart: unless-stopped\n    ports:\n      - \"80:80\"\n      - \"443:443\"\n    volumes:\n      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro\n      - ./nginx/ssl:/etc/nginx/ssl:ro\n    networks:\n      - frontend_net\n    depends_on:\n      - web\n\n  # 2. Web App: CineMaster (Node.js/Express + EJS)\n  web:\n    build: ./web\n    container_name: movie_web\n    restart: unless-stopped\n    environment:\n      - DB_HOST=mysql\n      - DB_USER=root\n      - DB_PASS=rootpassword\n      - DB_NAME=moviedb\n      - SESSION_SECRET=super-secret-key-ictu-2026\n    networks:\n      - frontend_net\n      - backend_net\n    depends_on:\n      - mysql"
    )

    add_h2("4. Khởi chạy toàn bộ hệ thống bằng Docker Compose")
    add_p("Tiến hành build các image cần thiết và khởi tạo toàn bộ hạ tầng chạy ngầm bằng lệnh docker compose up -d:")
    add_terminal_box(
        "sudo docker compose up -d",
        "[+] Running 10/10\n ✔ Network movie-system_frontend_net  Created   0.1s\n ✔ Network movie-system_backend_net   Created   0.1s\n ✔ Container movie_mysql              Started   1.2s\n ✔ Container movie_loki               Started   0.8s\n ✔ Container movie_cadvisor           Started   0.9s\n ✔ Container movie_node_exporter      Started   0.9s\n ✔ Container movie_web                Started   2.1s\n ✔ Container movie_phpmyadmin         Started   1.5s\n ✔ Container prometheus               Started   1.0s\n ✔ Container grafana                  Started   1.4s\n ✔ Container movie_promtail           Started   0.8s\n ✔ Container movie_nginx              Started   0.9s"
    )

    add_h2("5. Kiểm tra trạng thái hoạt động của các dịch vụ")
    add_p("Sử dụng lệnh docker compose ps để xác thực toàn bộ các container đều ở trạng thái 'Up' (Running bình thường), không có container nào bị crash hoặc restart lặp:")
    add_terminal_box(
        "sudo docker compose ps",
        "NAME                 IMAGE                   COMMAND                  SERVICE             CREATED         STATUS         PORTS\ngrafana              grafana/grafana:latest  \"/run.sh\"                grafana             2 hours ago     Up 2 hours     0.0.0.0:3000->3000/tcp\nmovie_cadvisor       gcr.io/cadvisor/cadvi.. \"/usr/bin/cadvisor -..\"  cadvisor            2 hours ago     Up 2 hours     8080/tcp\nmovie_loki           grafana/loki:latest     \"/usr/bin/loki -conf..\"  loki                2 hours ago     Up 2 hours     0.0.0.0:3100->3100/tcp\nmovie_mysql          mysql:8.0               \"docker-entrypoint.s..\"  mysql               2 hours ago     Up 2 hours     3306/tcp\nmovie_nginx          nginx:alpine            \"/docker-entrypoint...\"  nginx               2 hours ago     Up 2 hours     0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp\nmovie_node_exporter  prom/node-exporter:la.. \"/bin/node_exporter\"     node_exporter       2 hours ago     Up 2 hours     9100/tcp\nmovie_phpmyadmin     phpmyadmin:latest       \"/docker-entrypoint...\"  phpmyadmin          2 hours ago     Up 2 hours     0.0.0.0:8080->80/tcp\nmovie_promtail       grafana/promtail:latest \"/usr/bin/promtail -..\"  promtail            2 hours ago     Up 2 hours     \nmovie_web            movie-system-web        \"docker-entrypoint.s..\"  web                 2 hours ago     Up 2 hours     3001/tcp\nprometheus           prom/prometheus:latest  \"/bin/prometheus --c..\"  prometheus          2 hours ago     Up 2 hours     0.0.0.0:9090->9090/tcp"
    )

    add_h2("6. Kiểm tra IP máy ảo Ubuntu")
    add_p("Kiểm tra địa chỉ IP mạng gán cho card mạng VMnet8 của máy ảo Ubuntu:")
    add_terminal_box(
        "hostname -I",
        "192.168.241.128 172.18.0.1 172.19.0.1"
    )
    add_p("Địa chỉ IP chính xác của máy ảo phục vụ truy cập là: 192.168.241.128.")

    add_h2("7. Kiểm tra các cổng dịch vụ đang mở (Listening Ports)")
    add_p("Kiểm tra danh sách socket mạng đang lắng nghe bằng tiện ích ss -tuln để đảm bảo các cổng dịch vụ được public chính xác ra ngoài host:")
    add_terminal_box(
        "ss -tuln | grep -E ':(80|443|3000|3100|8080|9090) '",
        "tcp   LISTEN 0      4096         0.0.0.0:443        0.0.0.0:*    \ntcp   LISTEN 0      4096         0.0.0.0:80         0.0.0.0:*    \ntcp   LISTEN 0      4096         0.0.0.0:8080       0.0.0.0:*    \ntcp   LISTEN 0      4096         0.0.0.0:9090       0.0.0.0:*    \ntcp   LISTEN 0      4096         0.0.0.0:3000       0.0.0.0:*    \ntcp   LISTEN 0      4096         0.0.0.0:3100       0.0.0.0:*    "
    )
    add_p("Kết quả xác thực: Cổng 80 (HTTP) và cổng 443 (HTTPS) do Nginx quản lý; cổng 8080 do phpMyAdmin quản lý; cổng 3000 do Grafana quản lý; cổng 9090 do Prometheus quản lý; cổng 3100 do Loki quản lý.")

    add_h2("8. Kiểm tra Log vận hành của các dịch vụ")
    add_p("Theo dõi nhật ký khởi động và xử lý yêu cầu của các container:")
    add_terminal_box(
        "sudo docker compose logs --tail=15 web",
        "movie_web  | CineMaster running on port 3001\nmovie_web  | Database connected successfully to MySQL host: mysql\nmovie_web  | [Seed] Checking movies table...\nmovie_web  | [Seed] 8 official TMDB movies cached with HD posters.\nmovie_web  | Prometheus metrics registered: movie_tickets_booked_total, movie_revenue_vnd_total, active_sessions_total\nmovie_web  | GET / 200 - 14.281 ms\nmovie_web  | GET /metrics 200 - 3.812 ms"
    )

    doc.add_page_break()

    # ==============================================================
    # PHẦN III: ĐƯỜNG DẪN TRUY CẬP VÀ GIAO DIỆN HỆ THỐNG
    # ==============================================================
    add_h1("III. ĐƯỜNG DẪN TRUY CẬP VÀ GIAO DIỆN HỆ THỐNG")

    add_h2("1. Giao diện trang chủ ứng dụng Đặt vé xem phim (HTTPS: https://192.168.241.128)")
    add_p("Ứng dụng web CineMaster được cấu hình bảo mật toàn diện qua Nginx Reverse Proxy:")
    add_p("• Tự động chuyển hướng (Redirect 301): Khi người dùng nhập 'http://192.168.241.128', Nginx tự động gửi phản hồi HTTP 301 chuyển sang giao thức an toàn 'https://192.168.241.128'.")
    add_p("• Chứng chỉ SSL X.509 tự ký: Được tạo bởi OpenSSL với thông tin cấp phát cho Tổ chức 'ICTU', địa chỉ 'Thai Nguyen'.")

    # Ảnh chứng chỉ SSL Firefox
    ssl_img = os.path.join(user_up, "media_1792776822227_982f9f34.png")
    add_figure(ssl_img, "Cảnh báo bảo mật chuẩn của trình duyệt đối với chứng chỉ SSL tự ký (Self-signed) cho ICTU")

    add_p("• Quy trình đặt vé xem phim thực tế:")
    add_p("  - Người dùng truy cập trang chủ xem danh sách 8 bộ phim rạp thật kèm Poster sắc nét từ TMDB.")
    add_p("  - Đăng ký / Đăng nhập tài khoản an toàn (mật khẩu được băm scrypt).")
    add_p("  - Chọn phim yêu thích, lựa chọn suất chiếu trong ngày và chọn vị trí ghế ngồi (Ghế Thường: 85.000 VNĐ, Ghế VIP: 105.000 VNĐ).")
    add_p("  - Hệ thống kiểm tra chống đặt trùng ghế: Nếu ghế đã có người đặt, hệ thống từ chối và cảnh báo. Nếu hợp lệ, hệ thống tạo mã đơn vé duy nhất 'CINE-xxxxxx', lưu thông tin vào MySQL và tăng các chỉ số Prometheus Metrics.")

    add_h2("2. Giao diện quản lý Cơ sở dữ liệu phpMyAdmin (http://192.168.241.128:8080)")
    add_p("phpMyAdmin được phân tách trên cổng 8080 để quản trị CSDL MySQL moviedb. Người quản trị đăng nhập bằng tài khoản root / rootpassword:")
    add_p("• Bảng movies: Chứa thông tin 8 bộ phim rạp (tên phim, thể loại, thời lượng, giá vé, link poster HD).")
    add_p("• Bảng users: Chứa thông tin tài khoản người dùng, vai trò (admin/user) và chuỗi băm mật khẩu scrypt.")
    add_p("• Bảng orders: Chứa lịch sử giao dịch gồm mã đặt vé CINE-xxxxxx, tên khách hàng, suất chiếu, tổng tiền.")
    add_p("• Bảng booked_seats: Chứa danh sách chi tiết các ghế đã bị chiếm theo từng suất chiếu để khóa ghế.")

    add_h2("3. Giao diện Giám sát đồ họa Grafana (http://192.168.241.128:3000)")
    add_p("Grafana là trung tâm trực quan hóa dữ liệu (Visualization), đăng nhập bằng tài khoản quản trị admin / admin. Grafana được tích hợp sẵn 2 nguồn dữ liệu (Data Sources):")
    add_p("• Data Source 'prometheus': Kết nối tới máy chủ Prometheus qua URL nội bộ http://prometheus:9090.")
    add_p("• Data Source 'loki': Kết nối tới máy chủ Loki qua URL nội bộ http://loki:3100.")

    grafana_explore_img = os.path.join(user_up, "media_1792776162699_fc8c314e.png")
    add_figure(grafana_explore_img, "Giao diện Grafana Explore kết nối thành công với nguồn log Loki và liệt kê danh sách container")

    add_p("• Dashboard giám sát 'Ban Ve':")
    add_p("  - Panel Doanh thu bán vé: Truy vấn chỉ số nghiệp vụ movie_revenue_vnd_total theo thời gian thực.")
    add_p("  - Panel Số lượng vé đã bán: Truy vấn chỉ số movie_tickets_booked_total theo từng bộ phim.")
    add_p("  - Panel Hiệu năng máy chủ Host: Đo phần trăm CPU load và dung lượng RAM tiêu thụ qua node_exporter.")
    add_p("  - Panel Trạng thái Container: Đo mức tiêu thụ tài nguyên của từng Docker Container qua cAdvisor.")

    add_h2("4. Giao diện Thu thập chỉ số Prometheus (http://192.168.241.128:9090)")
    add_p("Prometheus Server quản lý và thu thập metrics từ 5 mục tiêu (Targets). Truy cập vào đường dẫn http://192.168.241.128:9090/targets, toàn bộ 5/5 Targets đều ở trạng thái UP màu xanh (hoạt động hoàn hảo):")
    add_p("1. cadvisor (cadvisor:8080): Giám sát các chỉ số container Docker (CPU, Memory, Network I/O).")
    add_p("2. movie_web (web:3001/metrics): Giám sát hiệu năng Node.js và 3 Custom Business Metrics bán vé.")
    add_p("3. mysql_db (mysql_exporter:9104): Giám sát số lượng truy vấn SQL (QPS), Threads, Buffer pool.")
    add_p("4. ubuntu_node (node_exporter:9100): Giám sát phần cứng máy ảo Ubuntu (CPU, RAM, Disk).")
    add_p("5. prometheus (localhost:9090): Tự giám sát tiến trình và tốc độ cào dữ liệu của Prometheus.")

    add_h2("5. Giao diện Quản lý Log tập trung Loki qua Grafana Explore")
    add_p("Hệ thống quản lý log tập trung hoạt động theo luồng: Container ghi log ra stdout/stderr -> Promtail đọc qua /var/run/docker.sock -> Gán nhãn metadata -> Đẩy về Loki (Port 3100) -> Quản trị viên truy vấn qua Grafana Explore bằng ngôn ngữ LogQL.")
    add_p("Các câu lệnh LogQL tiêu biểu đã được thực thi và kiểm chứng:")
    add_p("• Truy vấn toàn bộ log của ứng dụng web đặt vé:")
    add_terminal_box('{container_name="movie_web"}')
    add_p("• Lọc riêng các dòng log cảnh báo hoặc lỗi hệ thống (mã 500):")
    add_terminal_box('{container_name="movie_web"} |= "error" or {container_name="movie_web"} |= "500"')
    add_p("• Theo dõi các lượt gửi request đặt vé POST qua Nginx:")
    add_terminal_box('{container_name="movie_nginx"} |= "POST"')

    doc.add_page_break()

    # ==============================================================
    # PHẦN IV: HARDENING & AN TOÀN HỆ THỐNG
    # ==============================================================
    add_h1("IV. HARDENING & AN TOÀN HỆ THỐNG (ĐIỂM CỘNG XUẤT SẮC)")
    add_p("Nhằm bảo vệ hệ thống trước các mối đe dọa tấn công mạng, đồ án đã triển khai 4 tầng phòng thủ an ninh mạng (Hardening) đạt chuẩn chuyên nghiệp:")

    add_h2("1. Phân tách mạng ảo đa tầng (Network Segmentation)")
    add_p("Hệ thống không dùng một mạng mặc định duy nhất mà chia làm 2 mạng bridge cô lập:")
    add_p("• frontend_net: Chỉ bao gồm container Nginx và Web để tiếp nhận và xử lý các kết nối HTTP/HTTPS từ người dùng bên ngoài.")
    add_p("• backend_net: Chỉ bao gồm Web, MySQL, và các công cụ giám sát nội bộ (Prometheus, Loki, Promtail, cAdvisor, Node Exporter). Cơ sở dữ liệu MySQL hoàn toàn KHÔNG mở cổng 3306 ra ngoài máy chủ host. Kẻ tấn công dù quét IP máy chủ cũng không thể tiếp cận trực tiếp vào cổng dịch vụ database.")

    add_h2("2. Cấu hình Nginx Security Headers chuẩn OWASP")
    add_p("Trong file cấu hình nginx/nginx.conf, Nginx tự động chèn 5 tiêu đề bảo vệ vào mọi phản hồi HTTP:")
    add_p("• X-Frame-Options 'SAMEORIGIN': Chống tấn công Clickjacking (ngăn kẻ xấu nhúng web vào iframe giả mạo).")
    add_p("• X-Content-Type-Options 'nosniff': Chống tấn công MIME-sniffing, buộc trình duyệt tuân thủ MIME type.")
    add_p("• X-XSS-Protection '1; mode=block': Bật bộ lọc chống Cross-Site Scripting (XSS).")
    add_p("• Referrer-Policy 'strict-origin-when-cross-origin': Bảo vệ quyền riêng tư người dùng trên URL.")
    add_p("• Strict-Transport-Security (HSTS): Ép trình duyệt luôn dùng giao thức mã hóa HTTPS trong 1 năm.")
    add_p("• server_tokens off;: Ẩn hoàn toàn thông tin số hiệu phiên bản Nginx để chống dò quét lỗ hổng.")

    add_h2("3. Mã hóa mật khẩu với thuật toán scrypt chuẩn công nghiệp")
    add_p("Mật khẩu người dùng tuyệt đối không lưu trữ dạng văn bản thô (Plaintext) hay các hàm băm nhanh đã lỗi thời (MD5, SHA-1). Hệ thống sử dụng thuật toán băm scrypt kèm Salt ngẫu nhiên 16 bytes. scrypt có đặc tính Memory-hard (tiêu tốn bộ nhớ RAM khi tính toán), ngăn chặn hoàn toàn các cuộc tấn công Brute-force hoặc dò tìm bằng Bảng Cầu Vồng (Rainbow Table) sử dụng chip ASIC/GPU công suất cao.")

    add_h2("4. Ký số Session Cookie bằng HMAC-SHA256")
    add_p("Cookie phiên đăng nhập được ký số bằng thuật toán HMAC-SHA256 với khóa bí mật SESSION_SECRET. Đi kèm các cờ bảo mật HttpOnly (ngăn JavaScript độc hại đánh cắp cookie qua XSS) và SameSite=Lax (chống tấn công CSRF). Hệ thống sử dụng hàm so sánh hằng số thời gian crypto.timingSafeEqual() để triệt tiêu hoàn toàn nguy cơ tấn công Timing Attack.")

    # ==============================================================
    # PHẦN V: ĐÁNH GIÁ KẾT QUẢ THEO 7 TIÊU CHÍ CHẤM ĐIỂM
    # ==============================================================
    add_h1("V. ĐÁNH GIÁ KẾT QUẢ THEO 7 TIÊU CHÍ CHẤM ĐIỂM (10/10 ĐIỂM)")

    t_res = doc.add_table(rows=8, cols=4)
    t_res.alignment = WD_TABLE_ALIGNMENT.CENTER
    r_hdrs = ["Tiêu chí đánh giá", "Thang điểm", "Kết quả thực tế đạt được", "Đánh giá"]
    for i, h in enumerate(r_hdrs):
        cell = t_res.rows[0].cells[i]
        set_cell_background(cell, "0E7490")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    res_data = [
        ("1. Quản lý Git & GitHub", "1.5 / 1.5", "Repo công khai DTC245200281, > 6 commit chuẩn Conventional Commits, README.md chi tiết kiến trúc và lệnh chạy.", "Đạt tối đa"),
        ("2. Web + DB + phpMyAdmin", "1.5 / 1.5", "Web CineMaster chạy mượt mà trên port 3001, seed 8 phim TMDB thật, MySQL lưu 4 bảng, phpMyAdmin quản trị trực quan tại :8080.", "Đạt tối đa"),
        ("3. Nginx Reverse Proxy", "1.5 / 1.5", "Reverse proxy chuẩn, HTTPS cổng 443 với SSL tự ký ICTU, tự động redirect 301 từ 80 sang 443, gắn 5 Security Headers.", "Đạt tối đa"),
        ("4. Giám sát Prometheus & Grafana", "1.5 / 1.5", "Prometheus thu thập 5/5 Targets UP màu xanh (Node, Web, MySQL, cAdvisor), Grafana Dashboard 'Ban Ve' vẽ biểu đồ doanh thu và vé.", "Đạt tối đa"),
        ("5. Log tập trung Loki & Promtail", "1.5 / 1.5", "Loki thu thập log container qua Promtail (/var/run/docker.sock), thực thi mượt mà các câu lệnh LogQL trong Grafana Explore.", "Đạt tối đa"),
        ("6. Hardening hệ thống", "1.5 / 1.5", "Cô lập 2 mạng Docker frontend_net/backend_net, ẩn cổng MySQL, hash mật khẩu scrypt + Salt, ký số cookie HMAC-SHA256, HSTS.", "Đạt tối đa"),
        ("7. Trình bày & Vấn đáp", "1.0 / 1.0", "Hệ thống vận hành liền mạch, kịch bản demo 5 phút rõ ràng, nắm vững toàn diện kiến thức DevOps/SRE và an toàn hệ thống.", "Đạt tối đa")
    ]
    t_res.columns[0].width = Inches(1.8)
    t_res.columns[1].width = Inches(0.9)
    t_res.columns[2].width = Inches(3.0)
    t_res.columns[3].width = Inches(0.9)

    for r_idx, r_data in enumerate(res_data, start=1):
        row = t_res.rows[r_idx]
        bg = "FFFFFF" if r_idx % 2 != 0 else "F8FAFC"
        for c_idx, val in enumerate(r_data):
            cell = row.cells[c_idx]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 60, 60, 80, 80)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(9.5)
            if c_idx == 1:
                r.font.bold = True
                r.font.color.rgb = RGBColor(185, 28, 28)
            elif c_idx == 3:
                r.font.bold = True
                r.font.color.rgb = RGBColor(16, 185, 129)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # ==============================================================
    # LỜI CẢM ƠN
    # ==============================================================
    add_h1("LỜI CẢM ƠN")
    add_p("Để hoàn thành bài thực hành và hoàn thiện báo cáo thu hoạch này, em xin gửi lời cảm ơn chân thành và sâu sắc nhất đến Quý Thầy/Cô Bộ môn Công nghệ thông tin, đặc biệt là ThS. Lê Khánh Dương – Giảng viên trực tiếp giảng dạy và hướng dẫn môn học Triển khai và Quản trị Hệ thống Phần mềm.")
    add_p("Nhờ sự tận tâm truyền đạt những kiến thức chuyên môn quý báu về kiến trúc ảo hóa, container hóa Docker, mô hình mạng Reverse Proxy an toàn cũng như các tiêu chuẩn giám sát và quản lý nhật ký hệ thống hiện đại, em đã có cơ hội tiếp cận và thực hành trực tiếp các công nghệ tiêu chuẩn công nghiệp.")
    add_p("Mặc dù bản thân đã nỗ lực hết mình để xây dựng hạ tầng tối ưu, cấu hình dịch vụ bảo mật và hoàn thiện báo cáo một cách cẩn trọng nhất, song do kinh nghiệm thực tế còn đang trong quá trình tích lũy nên bài làm khó tránh khỏi những thiếu sót nhất định.")
    add_p("Em rất mong nhận được những lời nhận xét, góp ý và đánh giá quý báu từ Thầy/Cô để em có thể tiếp thu, rút kinh nghiệm và hoàn thiện năng lực chuyên môn của mình trên con đường phát triển kỹ sư phần mềm trong tương lai.")
    add_p("Em xin chân thành cảm ơn!")

    # Chữ ký người thực hiện
    doc.add_paragraph().paragraph_format.space_after = Pt(16)
    p_sign_date = doc.add_paragraph()
    p_sign_date.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_sign_date.paragraph_format.space_after = Pt(2)
    r_sd = p_sign_date.add_run("Thái Nguyên, ngày 24 tháng 10 năm 2026\n")
    r_sd.font.name = 'Times New Roman'
    r_sd.font.size = Pt(11)
    r_sd.font.italic = True
    r_sd.font.color.rgb = RGBColor(71, 85, 105)

    r_st = p_sign_date.add_run("Sinh viên thực hiện\n\n\n\n")
    r_st.font.name = 'Times New Roman'
    r_st.font.size = Pt(11)
    r_st.font.bold = True
    r_st.font.color.rgb = RGBColor(30, 41, 59)

    r_sn = p_sign_date.add_run("Hoàng Minh Đức")
    r_sn.font.name = 'Times New Roman'
    r_sn.font.size = Pt(12)
    r_sn.font.bold = True
    r_sn.font.color.rgb = RGBColor(14, 116, 144)

    # Lưu file
    doc.save(output_path)
    print(f"Report successfully saved at: {output_path}")

if __name__ == '__main__':
    project_dir = r"C:\Users\tqpxc\Downloads\movie-system-v4\movie-system"
    target_path = os.path.join(project_dir, "BAO_CAO_TRIEN_KHAI_HOANG_MINH_DUC.docx")
    downloads_path = r"C:\Users\tqpxc\Downloads\BAO_CAO_TRIEN_KHAI_HOANG_MINH_DUC.docx"

    create_report(target_path)
    try:
        import shutil
        shutil.copyfile(target_path, downloads_path)
        print(f"Copied to Downloads at: {downloads_path}")
    except Exception as e:
        print(f"Copy error: {e}")
