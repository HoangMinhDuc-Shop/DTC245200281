# -*- coding: utf-8 -*-
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
import os
import shutil

def create_qa_document(output_path):
    doc = docx.Document()

    # Set page margins (0.8 - 0.9 inch)
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.85)
        section.right_margin = Inches(0.85)

    # Helper styling functions
    def set_cell_background(cell, hex_color):
        shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
        cell._tc.get_or_add_tcPr().append(shading)

    def set_cell_margins(cell, top=120, bottom=120, left=150, right=150):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = OxmlElement('w:tcMar')
        for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
            node = OxmlElement(f'w:{m}')
            node.set(qn('w:w'), str(val))
            node.set(qn('w:type'), 'dxa')
            tcMar.append(node)
        tcPr.append(tcMar)

    # Document Header Title
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(4)
    run_sub = title_p.add_run("TRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN & TRUYỀN THÔNG (ICTU)\nKHOA CÔNG NGHỆ THÔNG TIN\n")
    run_sub.font.name = 'Times New Roman'
    run_sub.font.size = Pt(11)
    run_sub.font.bold = True
    run_sub.font.color.rgb = RGBColor(70, 80, 95)

    title_main = title_p.add_run("TÀI LIỆU VẤN ĐÁP & HƯỚNG DẪN BẢO VỆ ĐỒ ÁN\n")
    title_main.font.name = 'Times New Roman'
    title_main.font.size = Pt(18)
    title_main.font.bold = True
    title_main.font.color.rgb = RGBColor(14, 116, 144) # Teal

    title_topic = title_p.add_run("ĐỀ TÀI: TRIỂN KHAI HỆ THỐNG ĐẶT VÉ XEM PHIM TRÊN DOCKER\nKÈM NGINX REVERSE PROXY, GIÁM SÁT PROMETHEUS/GRAFANA & LOG LOKI")
    title_topic.font.name = 'Times New Roman'
    title_topic.font.size = Pt(13)
    title_topic.font.bold = True
    title_topic.font.color.rgb = RGBColor(30, 41, 59)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # Metadata Card
    info_table = doc.add_table(rows=4, cols=2)
    info_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    info_data = [
        ("Sinh viên thực hiện:", "Hoàng Minh Đức (MSV: DTC245200281)"),
        ("Môi trường triển khai:", "Ubuntu 22.04 LTS (VMware Workstation) - IP: 192.168.241.128"),
        ("Mã nguồn GitHub:", "https://github.com/HoangMinhDuc-Shop/DTC245200281.git"),
        ("Mục tiêu đánh giá:", "Đạt điểm tối đa 10/10 theo 7 tiêu chí chuẩn")
    ]
    for row_idx, (label, val) in enumerate(info_data):
        row = info_table.rows[row_idx]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(2.2)
        c1.width = Inches(4.5)
        set_cell_background(c0, "F1F5F9")
        set_cell_background(c1, "F8FAFC")
        set_cell_margins(c0, 60, 60, 100, 100)
        set_cell_margins(c1, 60, 60, 100, 100)

        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(label)
        r0.font.name = 'Times New Roman'
        r0.font.size = Pt(10)
        r0.font.bold = True
        r0.font.color.rgb = RGBColor(51, 65, 85)

        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_after = Pt(0)
        r1 = p1.add_run(val)
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(10)
        r1.font.color.rgb = RGBColor(15, 23, 42)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # Heading 1 Generator
    def add_section_header(text, icon=""):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(f"{icon} {text}")
        r.font.name = 'Times New Roman'
        r.font.size = Pt(14)
        r.font.bold = True
        r.font.color.rgb = RGBColor(14, 116, 144)
        return p

    def add_question(q_num, q_text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(f"Câu {q_num}: {q_text}")
        r.font.name = 'Times New Roman'
        r.font.size = Pt(11.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(185, 28, 28) # Red-brick
        return p

    def add_answer(ans_text, tip=None):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        r_label = p.add_run("👉 Trả lời: ")
        r_label.font.name = 'Times New Roman'
        r_label.font.size = Pt(11)
        r_label.font.bold = True
        r_label.font.color.rgb = RGBColor(16, 185, 129) # Emerald Green

        r_ans = p.add_run(ans_text)
        r_ans.font.name = 'Times New Roman'
        r_ans.font.size = Pt(10.5)
        r_ans.font.color.rgb = RGBColor(30, 41, 59)

        if tip:
            box = doc.add_table(rows=1, cols=1)
            box.alignment = WD_TABLE_ALIGNMENT.CENTER
            cell = box.rows[0].cells[0]
            cell.width = Inches(6.7)
            set_cell_background(cell, "EFF6FF") # Soft Blue
            set_cell_margins(cell, 80, 80, 120, 120)
            bp = cell.paragraphs[0]
            bp.paragraph_format.space_after = Pt(0)
            br1 = bp.add_run("💡 Điểm nhấn ăn trọn điểm: ")
            br1.font.name = 'Times New Roman'
            br1.font.size = Pt(10)
            br1.font.bold = True
            br1.font.color.rgb = RGBColor(29, 78, 216)
            br2 = bp.add_run(tip)
            br2.font.name = 'Times New Roman'
            br2.font.size = Pt(9.5)
            br2.font.italic = True
            br2.font.color.rgb = RGBColor(30, 58, 138)
            doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # ==========================================
    # PHẦN 1: BẢNG TIÊU CHÍ VÀ THÔNG SỐ DEMO
    # ==========================================
    add_section_header("PHẦN 1: BẢNG TỔNG HỢP CÁC CỔNG DỊCH VỤ & TIÊU CHÍ ĐÁNH GIÁ (10/10 ĐIỂM)", "📌")
    
    t_criteria = doc.add_table(rows=8, cols=4)
    t_criteria.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Tiêu chí", "Điểm", "Thành phần kỹ thuật", "Địa chỉ / Đường link demo"]
    hdr_row = t_criteria.rows[0]
    for i, h in enumerate(headers):
        cell = hdr_row.cells[i]
        set_cell_background(cell, "0E7490")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    data_rows = [
        ("1. Git & GitHub", "1.5đ", "Repo công khai, >= 3 commits có ý nghĩa, README.md", "github.com/HoangMinhDuc-Shop/DTC245200281"),
        ("2. Web + DB + phpMyAdmin", "1.5đ", "Node.js 3001, MySQL 3306, phpMyAdmin 8080", "http://192.168.241.128:8080 (root / rootpassword)"),
        ("3. Nginx Reverse Proxy", "1.5đ", "Proxy port 80/443, HTTPS tự ký, 5 Security Headers", "https://192.168.241.128 (Tự redirect 80 -> 443)"),
        ("4. Giám sát Monitoring", "1.5đ", "Prometheus 9090, 4 Exporters, Grafana 3000", "http://192.168.241.128:3000 (admin / admin)"),
        ("5. Log tập trung", "1.5đ", "Loki 3100, Promtail (thu thập docker.sock), LogQL", "Grafana Explore -> chọn Loki -> query LogQL"),
        ("6. Hardening hệ thống", "1.5đ", "2 mạng cô lập, hash scrypt, HMAC-SHA256, HSTS", "docker network inspect frontend_net / backend_net"),
        ("7. Trình bày & Vấn đáp", "1.0đ", "Kịch bản demo liền mạch, giải thích tự tin", "Xem chi tiết kịch bản 5 phút ở Phần 2")
    ]
    t_criteria.columns[0].width = Inches(1.8)
    t_criteria.columns[1].width = Inches(0.6)
    t_criteria.columns[2].width = Inches(2.3)
    t_criteria.columns[3].width = Inches(2.3)

    for r_idx, row_data in enumerate(data_rows, start=1):
        row = t_criteria.rows[r_idx]
        bg = "FFFFFF" if r_idx % 2 != 0 else "F8FAFC"
        for c_idx, val in enumerate(row_data):
            cell = row.cells[c_idx]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 60, 60, 80, 80)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(9.5)
            if c_idx == 1:
                r.font.bold = True
                r.font.color.rgb = RGBColor(185, 28, 28)

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # ==========================================
    # PHẦN 2: KỊCH BẢN DEMO 5 PHÚT TỰ TIN LẤY ĐIỂM
    # ==========================================
    add_section_header("PHẦN 2: KỊCH BẢN DEMO THỰC TẾ 5 PHÚT TRƯỚC HỘI ĐỒNG", "🎬")
    
    steps = [
        ("Bước 1: Giới thiệu kiến trúc tổng thể (1 phút)",
         "Mở file README trên GitHub repo hoặc slide: 'Kính thưa Thầy/Cô, hệ thống của em gồm 8 container Docker hoạt động phối hợp, được phân tách làm 2 mạng: frontend_net cho người dùng và backend_net cho cơ sở dữ liệu và hệ thống giám sát nhằm đảm bảo bảo mật tối đa'."),
        ("Bước 2: Demo Ứng dụng & Nginx HTTPS (1.5 phút)",
         "Gõ 'http://192.168.241.128' trên trình duyệt để Thầy/Cô thấy Nginx tự động redirect 301 sang 'https://192.168.241.128'. Bấm vào ổ khóa bảo mật xem chứng chỉ SSL tự ký có tên tổ chức 'ICTU'. Tiến hành đăng nhập tài khoản 'minhduc', chọn phim thật từ TMDB và đặt 2 ghế A1, A2. Sau đó vào phpMyAdmin (:8080) chỉ cho Thầy/Cô thấy dòng dữ liệu vé vừa được chèn vào bảng orders và booked_seats."),
        ("Bước 3: Demo Giám sát Prometheus & Grafana (1.5 phút)",
         "Mở Prometheus ':9090/targets' chứng minh 5/5 Exporter đều UP màu xanh (Node, Web, MySQL, cAdvisor, Prometheus). Sau đó mở Grafana ':3000', mở dashboard 'Ban Ve' chỉ cho Thầy/Cô thấy biểu đồ Doanh thu (movie_revenue_vnd_total) và Số vé (movie_tickets_booked_total) vừa nhảy số ngay sau lượt đặt vé ở Bước 2."),
        ("Bước 4: Demo Log tập trung với Loki & LogQL (1 phút)",
         "Vào Grafana Explore, chọn Data source là 'loki'. Gõ câu lệnh LogQL: {container_name=\"movie_web\"} để hiển thị log web thời gian thực. Sau đó biểu diễn câu lệnh lọc log: {container_name=\"movie_web\"} |= \"error\" hoặc xem log Nginx {container_name=\"movie_nginx\"}."),
        ("Bước 5: Kết luận & Mời Thầy/Cô đặt câu hỏi (30 giây)",
         "'Em đã hoàn thành trọn vẹn 7 tiêu chí triển khai hệ thống an toàn, có tính sẵn sàng cao và giám sát toàn diện. Em xin kính mời Thầy/Cô đóng góp ý kiến và đặt câu hỏi ạ!'")
    ]
    for title, desc in steps:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(2)
        r1 = p.add_run(f"✔ {title}\n")
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(11)
        r1.font.bold = True
        r1.font.color.rgb = RGBColor(14, 116, 144)
        r2 = p.add_run(f"    {desc}")
        r2.font.name = 'Times New Roman'
        r2.font.size = Pt(10)
        r2.font.color.rgb = RGBColor(51, 65, 85)

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # ==========================================
    # PHẦN 3: BỘ CÂU HỎI VẤN ĐÁP THEO 7 TIÊU CHÍ
    # ==========================================
    add_section_header("PHẦN 3: BỘ 27 CÂU HỎI VẤN ĐÁP CHUYÊN SÂU & CÂU TRẢ LỜI MẪU", "❓")

    # --- NHÓM 1: GIT & GITHUB ---
    p_group = doc.add_paragraph()
    p_group.paragraph_format.space_before = Pt(8)
    p_group.paragraph_format.space_after = Pt(2)
    rg1 = p_group.add_run("I. TIÊU CHÍ 1: QUẢN LÝ MÃ NGUỒN TRÊN GIT & GITHUB (1.5 ĐIỂM)")
    rg1.font.name = 'Times New Roman'
    rg1.font.size = Pt(12)
    rg1.font.bold = True
    rg1.font.color.rgb = RGBColor(30, 41, 59)

    add_question(1, "Quy trình quản lý mã nguồn của em như thế nào? Các commit có tuân theo tiêu chuẩn gì không?")
    add_answer(
        "Dạ thưa Thầy/Cô, mã nguồn dự án được quản lý tập trung trên GitHub tại repository công khai DTC245200281. Em tuân thủ quy chuẩn Conventional Commits trong từng lần commit với tiền tố rõ ràng như: 'feat:' khi thêm tính năng hạ tầng, 'fix:' khi sửa lỗi, 'docs:' khi hoàn thiện tài liệu hướng dẫn và 'refactor:' khi tối ưu cấu hình. Lịch sử Git có hơn 6 commit phân tách rõ ràng qua từng giai đoạn phát triển.",
        "Mở tab commit trên GitHub chỉ cho thầy cô thấy các commit: feat(infra), feat(app), docs(readme), feat(monitoring-loki), fix(loki-permissions), feat(nginx-https)."
    )

    add_question(2, "File .gitignore trong dự án của em dùng để làm gì? Tại sao phải cấu hình cẩn thận?")
    add_answer(
        "File .gitignore dùng để chỉ định các file hoặc thư mục mà Git không được theo dõi và không đưa lên kho lưu trữ từ xa. Trong dự án của em, .gitignore loại trừ: thư mục node_modules/ (chứa thư viện phụ thuộc quá lớn, có thể cài lại bằng npm install), các file biến môi trường .env và các khóa bí mật tư nhân (*.key) để tránh rò rỉ dữ liệu nhạy cảm ra ngoài.",
        "Nhấn mạnh vào bảo mật: Tuyệt đối không bao giờ commit private key và secret password lên GitHub công khai."
    )

    # --- NHÓM 2: ỨNG DỤNG WEB & DATABASE & PHPMYADMIN ---
    p_group = doc.add_paragraph()
    p_group.paragraph_format.space_before = Pt(8)
    p_group.paragraph_format.space_after = Pt(2)
    rg2 = p_group.add_run("II. TIÊU CHÍ 2: TRIỂN KHAI WEB, CƠ SỞ DỮ LIỆU & PHPMYADMIN (1.5 ĐIỂM)")
    rg2.font.name = 'Times New Roman'
    rg2.font.size = Pt(12)
    rg2.font.bold = True
    rg2.font.color.rgb = RGBColor(30, 41, 59)

    add_question(3, "Ứng dụng web đặt vé xem phim của em được xây dựng bằng công nghệ gì và cơ sở dữ liệu gồm những bảng nào?")
    add_answer(
        "Dạ thưa Thầy/Cô, ứng dụng được xây dựng theo mô hình Full-stack bằng Node.js và framework Express, kết hợp công nghệ Server-side Rendering với EJS template engine. Cơ sở dữ liệu sử dụng MySQL 8.0 gồm 4 bảng chính:\n"
        "1. movies: Lưu danh sách 8 bộ phim rạp thực tế (lấy từ TMDB API), thông tin giá vé, thời lượng, poster HD.\n"
        "2. users: Lưu thông tin tài khoản người dùng, vai trò (admin/user), mật khẩu đã băm.\n"
        "3. orders: Lưu lịch sử đặt vé gồm mã đơn CINE-xxxxxx, suất chiếu, danh sách ghế, tổng tiền.\n"
        "4. booked_seats: Lưu thông tin chi tiết từng ghế đã bị chiếm theo suất chiếu để khóa ghế chống đặt trùng.",
        "Dữ liệu phim không phải là mock text giả lập mà là 8 phim thật với ảnh poster HD được cache trực tiếp từ TMDB CDN."
    )

    add_question(4, "Em giải quyết bài toán chống đặt trùng ghế (Double Booking) như thế nào?")
    add_answer(
        "Hệ thống giải quyết bài toán này ở 2 tầng:\n"
        "- Tầng ứng dụng (Application Level): Trước khi lưu đơn, hệ thống thực hiện truy vấn 'SELECT seat_code FROM booked_seats WHERE movie_title = ? AND showtime = ? AND seat_code IN (?)'. Nếu phát hiện ghế đã bị người khác đặt trước trong suất chiếu đó, hệ thống lập tức rollback và cảnh báo người dùng chọn ghế khác.\n"
        "- Tầng cơ sở dữ liệu (Database Level): Bảng booked_seats lưu từng ghế tương ứng với suất chiếu, có thể kết hợp ràng buộc khóa duy nhất UNIQUE(movie_title, showtime, seat_code) để đảm bảo toàn vẹn dữ liệu ở cấp độ Transaction ACID.",
        "Đây là câu hỏi Thầy/Cô rất hay hỏi về tính logic nghiệp vụ của hệ thống đặt vé!"
    )

    add_question(5, "Tại sao em lại tách phpMyAdmin ra một container riêng trên cổng 8080?")
    add_answer(
        "phpMyAdmin là công cụ quản trị giao diện web cho MySQL. Việc tách ra một container riêng giúp phân tách mối quan tâm (Separation of Concerns). phpMyAdmin chạy trên cổng 8080 độc lập với cổng ứng dụng web (80/443), giúp người quản trị dễ dàng thao tác trực quan mà không ảnh hưởng tới người dùng cuối, đồng thời dễ dàng chặn cổng này qua tường lửa UFW khi đưa lên môi trường Production thực tế.",
        "Mở tab phpMyAdmin http://192.168.241.128:8080 chỉ các bảng dữ liệu để lấy điểm trực quan."
    )

    # --- NHÓM 3: NGINX REVERSE PROXY & HTTPS ---
    p_group = doc.add_paragraph()
    p_group.paragraph_format.space_before = Pt(8)
    p_group.paragraph_format.space_after = Pt(2)
    rg3 = p_group.add_run("III. TIÊU CHÍ 3: NGINX REVERSE PROXY & BẢO MẬT HTTPS (1.5 ĐIỂM)")
    rg3.font.name = 'Times New Roman'
    rg3.font.size = Pt(12)
    rg3.font.bold = True
    rg3.font.color.rgb = RGBColor(30, 41, 59)

    add_question(6, "Reverse Proxy là gì? Tại sao không cho người dùng truy cập trực tiếp vào Node.js (cổng 3001) mà phải đi qua Nginx?")
    add_answer(
        "Reverse Proxy là một máy chủ trung gian đứng trước các máy chủ backend (Node.js), tiếp nhận mọi yêu cầu từ client và điều phối tới backend phù hợp. Không cho người dùng truy cập trực tiếp cổng 3001 vì 5 lý do cốt lõi:\n"
        "1. Ẩn giấu cấu trúc nội bộ: Client chỉ biết cổng 80/443 của Nginx, không biết backend viết bằng gì hay chạy ở port nào.\n"
        "2. SSL Termination (Giải mã SSL): Nginx đảm nhiệm tính toán mã hóa HTTPS nặng nề, giải phóng CPU cho Node.js tập trung xử lý nghiệp vụ.\n"
        "3. Tự động chuyển hướng: Nginx tự động chuyển hướng HTTP (80) sang HTTPS (443) bằng mã phản hồi 301 Moved Permanently.\n"
        "4. Gắn Security Headers: Nginx tự động chèn các tiêu đề an ninh bảo vệ ứng dụng.\n"
        "5. Cân bằng tải (Load Balancing): Dễ dàng mở rộng thêm nhiều container web phía sau mà không đổi IP của client.",
        "Nhớ từ khóa: 'SSL Termination' và 'Giảm tải cho Backend' - Thầy cô chuyên về mạng rất thích 2 từ này!"
    )

    add_question(7, "Chứng chỉ SSL/TLS trong dự án này được tạo ra như thế nào? Tại sao trình duyệt lại hiện cảnh báo bảo mật?")
    add_answer(
        "Chứng chỉ SSL được tạo trực tiếp bằng công cụ OpenSSL trên máy ảo Ubuntu bằng lệnh: openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx.key -out nginx.crt. Trong đó, em cấu hình tên miền Common Name là IP máy ảo 192.168.241.128 và Tổ chức phát hành là ICTU.\n"
        "Trình duyệt hiện cảnh báo bảo mật vì đây là chứng chỉ Tự Ký (Self-Signed Certificate), không được ký bởi các nhà cấp phát chứng chỉ công khai (CA uy tín như DigiCert hay Let's Encrypt - vốn yêu cầu phải có tên miền Internet thực sự). Trong môi trường phát triển và phòng Lab, việc dùng chứng chỉ tự ký là quy chuẩn kỹ thuật tiêu chuẩn để kiểm thử mã hóa TLS.",
        "Chỉ cho thầy cô thấy thông tin chứng chỉ: Organization: ICTU, Locality: Thai Nguyen."
    )

    add_question(8, "Em hãy giải thích ý nghĩa của 5 Security Headers mà em đã cấu hình trong Nginx?")
    add_answer(
        "Trong file nginx.conf, em đã cấu hình 5 header an ninh chuẩn OWASP:\n"
        "1. X-Frame-Options 'SAMEORIGIN': Ngăn chặn tấn công Clickjacking (không cho trang web khác nhúng web của mình vào <iframe> độc hại).\n"
        "2. X-Content-Type-Options 'nosniff': Ngăn chặn trình duyệt đoán định sai kiểu file (MIME-sniffing), chống thực thi script ẩn trong file ảnh/text.\n"
        "3. X-XSS-Protection '1; mode=block': Kích hoạt bộ lọc chống tấn công Cross-Site Scripting (XSS) trên trình duyệt.\n"
        "4. Referrer-Policy 'strict-origin-when-cross-origin': Bảo vệ quyền riêng tư người dùng, chỉ gửi thông tin nguồn gốc URL qua kết nối HTTPS an toàn.\n"
        "5. Strict-Transport-Security (HSTS): Ép buộc trình duyệt chỉ được phép giao tiếp qua giao thức mã hóa HTTPS trong thời gian 1 năm.",
        "Chứng minh: Có thể mở F12 trên trình duyệt -> tab Network -> bấm vào request -> xem mục Response Headers sẽ thấy đủ 5 headers này!"
    )

    # --- NHÓM 4: HỆ THỐNG GIÁM SÁT PROMETHEUS & GRAFANA ---
    p_group = doc.add_paragraph()
    p_group.paragraph_format.space_before = Pt(8)
    p_group.paragraph_format.space_after = Pt(2)
    rg4 = p_group.add_run("IV. TIÊU CHÍ 4: HỆ THỐNG GIÁM SÁT PROMETHEUS & GRAFANA (1.5 ĐIỂM)")
    rg4.font.name = 'Times New Roman'
    rg4.font.size = Pt(12)
    rg4.font.bold = True
    rg4.font.color.rgb = RGBColor(30, 41, 59)

    add_question(9, "Prometheus là gì? Tác dụng, khái niệm và cơ chế hoạt động của Prometheus trong hệ thống?")
    add_answer(
        "Dạ thưa Thầy/Cô, về Prometheus:\n\n"
        "1. KHÁI NIỆM:\n"
        "Prometheus là một hệ thống giám sát (Monitoring System) và cảnh báo mã nguồn mở, ban đầu được phát triển bởi SoundCloud và hiện là dự án tốt nghiệp thứ hai (sau Kubernetes) của tổ chức Cloud Native Computing Foundation (CNCF). Prometheus được thiết kế chuyên biệt để theo dõi độ tin cậy và hiệu năng của các hệ thống vi dịch vụ (Microservices) và Docker Containers.\n\n"
        "2. TÁC DỤNG TRONG HỆ THỐNG:\n"
        "- Thu thập số liệu hiệu năng (Metrics) theo thời gian thực từ phần cứng, hệ điều hành đến ứng dụng.\n"
        "- Lưu trữ dữ liệu dạng chuỗi thời gian (Time-Series Database - TSDB) với tốc độ nén và truy xuất cực cao.\n"
        "- Cung cấp ngôn ngữ truy vấn mạnh mẽ PromQL (Prometheus Query Language) để tính toán tỉ lệ tải (rate), giá trị trung bình, phần trăm (percentile), cộng dồn (sum).\n"
        "- Hỗ trợ phát hiện lỗi và gửi cảnh báo (Alerting) khi hệ thống gặp sự cố (quá tải CPU, hết RAM, service bị sập).\n\n"
        "3. CƠ CHẾ HOẠT ĐỘNG:\n"
        "- Khám phá mục tiêu (Target Discovery): Prometheus đọc file cấu hình prometheus.yml để xác định danh sách các điểm cuối cần giám sát (Targets: web:3001, node_exporter:9100, cadvisor:8080, mysql_exporter:9104).\n"
        "- Kéo dữ liệu định kỳ (PULL Mechanism): Cứ sau mỗi chu kỳ scrape_interval (10 giây), Prometheus chủ động gửi yêu cầu HTTP GET tới endpoint /metrics của từng Target để lấy dữ liệu.\n"
        "- Xử lý & Lưu trữ: Dữ liệu nhận về được gắn nhãn (Labels: job, instance) và lưu trữ trực tiếp vào cơ sở dữ liệu chuỗi thời gian TSDB trên ổ cứng bền vững (Volume prom_data).\n"
        "- Cung cấp API cho Grafana: Prometheus mở cổng 9090 để Grafana truy vấn dữ liệu bằng PromQL và vẽ biểu đồ trực quan.",
        "Nhớ từ khóa: 'CNCF Project', 'Time-Series Database (TSDB)', 'PULL mechanism qua HTTP /metrics', 'Ngôn ngữ PromQL'."
    )

    add_question(10, "Grafana là gì? Tác dụng, khái niệm và cơ chế hoạt động của Grafana trong hệ thống?")
    add_answer(
        "Dạ thưa Thầy/Cô, về Grafana:\n\n"
        "1. KHÁI NIỆM:\n"
        "Grafana là nền tảng mã nguồn mở hàng đầu thế giới về Trực quan hóa dữ liệu (Data Visualization), Phân tích số liệu và Giám sát giao diện người dùng, được phát triển bởi Grafana Labs. Grafana biến các chuỗi số liệu thô phức tạp thành các bảng điều khiển (Dashboards) trực quan, sinh động và dễ hiểu đối với con người.\n\n"
        "2. TÁC DỤNG TRONG HỆ THỐNG:\n"
        "- Trực quan hóa đa dạng: Cung cấp hàng chục loại biểu đồ: Time Series (biểu đồ đường theo thời gian), Gauge (đồng hồ đo tốc độ/phần trăm), Stat (thẻ hiển thị số liệu lớn), Bar Chart, Heatmap, Bảng dữ liệu.\n"
        "- Hợp nhất một màn hình duy nhất (Single Pane of Glass): Cho phép người quản trị vừa theo dõi chỉ số hiệu năng (Metrics từ Prometheus) vừa theo dõi nhật ký hoạt động (Logs từ Loki) trên cùng một giao diện duy nhất.\n"
        "- Đa nguồn dữ liệu (Multi-DataSource): Grafana không tự lưu trữ dữ liệu mà kết nối linh hoạt tới nhiều Data Sources: Prometheus, Loki, MySQL, InfluxDB, Elasticsearch, CloudWatch...\n"
        "- Tùy biến và Tương tác cao: Hỗ trợ lọc khoảng thời gian (now-5m, now-1h, now-24h), tự động làm mới (Auto-refresh 5s, 10s), phóng to thu nhỏ (Zoom-in/Zoom-out) các điểm bất thường trên đồ thị.\n\n"
        "3. CƠ CHẾ HOẠT ĐỘNG:\n"
        "- Kết nối Data Source: Người quản trị cấu hình nguồn cấp dữ liệu trong Grafana (Data Source Prometheus qua URL http://prometheus:9090 và Loki qua http://loki:3100).\n"
        "- Gửi câu truy vấn: Khi người dùng mở Dashboard, mỗi Panel trong Grafana sẽ tự động gửi câu truy vấn tương ứng (PromQL tới Prometheus hoặc LogQL tới Loki) thông qua HTTP REST API nội bộ.\n"
        "- Nhận dữ liệu & Render đồ họa: Máy chủ Prometheus/Loki xử lý tính toán và trả về kết quả JSON. Grafana tiếp nhận dữ liệu và vẽ biểu đồ dạng vector trên trình duyệt web của người dùng.\n"
        "- Cập nhật chu kỳ: Nếu bật tính năng Auto-refresh, Grafana sẽ lặp lại quá trình truy vấn trên theo chu kỳ để biểu đồ dịch chuyển và nhảy số theo thời gian thực.",
        "Nhớ từ khóa: 'Visualization Layer', 'Single Pane of Glass (hợp nhất Metrics và Logs)', 'Data Source agnostic (không tự lưu dữ liệu mà truy vấn từ nguồn)'."
    )

    add_question(11, "Prometheus hoạt động theo mô hình Pull hay Push? So sánh ưu điểm của mô hình Pull?")
    add_answer(
        "Prometheus hoạt động theo mô hình PULL (máy chủ chủ động kéo dữ liệu). Ưu điểm vượt trội của mô hình PULL so với PUSH:\n"
        "1. Kiểm soát tải của Server: Prometheus tự quyết định thời điểm và tần suất cào dữ liệu (scrape_interval), không bao giờ bị nghẽn mạng do hàng nghìn client đồng loạt 'bắn' dữ liệu về máy chủ.\n"
        "2. Dễ dàng phát hiện sự cố: Khi một ứng dụng hoặc Exporter bị sập (DOWN), Prometheus gửi request cào dữ liệu không thành công sẽ lập tức phát hiện và đánh dấu mục tiêu đó là DOWN ngay trên bảng điều khiển.\n"
        "3. Kiến trúc đơn giản: Phía ứng dụng chỉ cần mở một cổng HTTP GET /metrics đơn giản, không cần cấu hình địa chỉ IP máy chủ giám sát phức tạp.",
        "Nếu thầy cô hỏi 'Có trường hợp nào Prometheus dùng Push không?' -> Trả lời: Có, khi giám sát các tiến trình ngắn hạn (Batch jobs, Cron jobs), Prometheus sẽ dùng một thành phần phụ trợ gọi là Pushgateway."
    )

    add_question(12, "Hệ thống của em đang giám sát những tầng nào và sử dụng những Exporter nào?")
    add_answer(
        "Hệ thống giám sát toàn diện 4 tầng (Full-stack Observability):\n"
        "1. Tầng Máy chủ Host: Sử dụng node_exporter (cổng 9100) để đo CPU, RAM, Disk I/O, Network của hệ điều hành Ubuntu.\n"
        "2. Tầng Container: Sử dụng google/cadvisor để đo mức tiêu thụ CPU, RAM, giới hạn tài nguyên của từng container Docker riêng biệt.\n"
        "3. Tầng Cơ sở dữ liệu: Sử dụng mysqld_exporter (cổng 9104) kết nối với MySQL để đo số lượng truy vấn (QPS), Threads connected, Buffer pool.\n"
        "4. Tầng Ứng dụng Web: Sử dụng thư viện prom-client nhúng trực tiếp trong Node.js để xuất endpoint /metrics, đo cả hiệu năng hệ thống (Node.js Heap memory, CPU) lẫn metric nghiệp vụ riêng.",
        "Mở trang http://192.168.241.128:9090/targets để khoe 5/5 targets đều màu xanh (UP)."
    )

    add_question(13, "Em đã tự định nghĩa những Custom Metric (chỉ số nghiệp vụ) nào trong mã nguồn Node.js?")
    add_answer(
        "Trong web/index.js, em đã tự định nghĩa 3 custom metric quan trọng bằng thư viện prom-client:\n"
        "1. movie_tickets_booked_total (kiểu Counter): Đo tổng số vé đã bán, phân loại theo nhãn tên phim (movie_title) và loại ghế (seat_type).\n"
        "2. movie_revenue_vnd_total (kiểu Counter): Đo tổng doanh thu bán vé bằng tiền VND, tự động tăng theo giá trị mỗi đơn hàng.\n"
        "3. active_sessions_total (kiểu Gauge): Đo số lượng phiên làm việc của người dùng đang hoạt động trong hệ thống.\n"
        "Mỗi khi người dùng đặt vé thành công, mã nguồn sẽ gọi lệnh: totalTicketsBooked.inc(...) và totalRevenue.inc(...) để cập nhật số liệu ngay lập tức.",
        "Đây là điểm cộng xuất sắc vì đa số sinh viên chỉ lấy metric mặc định, còn bạn tự viết metric nghiệp vụ bán vé!"
    )

    add_question(14, "Sự khác biệt giữa Counter và Gauge trong Prometheus là gì?")
    add_answer(
        "Dạ thưa Thầy/Cô:\n"
        "- Counter: Là chỉ số chỉ có thể tăng lên hoặc reset về 0 khi tiến trình khởi động lại (không bao giờ giảm). Phù hợp để đo lường các đại lượng tích lũy như: tổng số vé đã bán, tổng số lượt request, tổng doanh thu.\n"
        "- Gauge: Là chỉ số có thể tăng lên hoặc giảm xuống tùy ý tại bất kỳ thời điểm nào. Phù hợp để đo lường trạng thái tức thời như: dung lượng RAM sử dụng, nhiệt độ CPU, số người dùng đang online đồng thời.",
        "Đây là câu hỏi kinh điển về lý thuyết giám sát hệ thống!"
    )

    # --- NHÓM 5: HỆ THỐNG LOG TẬP TRUNG LOKI & PROMTAIL ---
    p_group = doc.add_paragraph()
    p_group.paragraph_format.space_before = Pt(8)
    p_group.paragraph_format.space_after = Pt(2)
    rg5 = p_group.add_run("V. TIÊU CHÍ 5: HỆ THỐNG QUẢN LÝ LOG TẬP TRUNG LOKI & PROMTAIL (1.5 ĐIỂM)")
    rg5.font.name = 'Times New Roman'
    rg5.font.size = Pt(12)
    rg5.font.bold = True
    rg5.font.color.rgb = RGBColor(30, 41, 59)

    add_question(15, "Tại sao em chọn Loki thay vì giải pháp ELK (Elasticsearch, Logstash, Kibana)?")
    add_answer(
        "Em lựa chọn Loki (kiến trúc PLG: Promtail - Loki - Grafana) vì 3 ưu điểm vượt trội so với ELK:\n"
        "1. Tiết kiệm tài nguyên vượt bậc: Elasticsearch đánh chỉ mục toàn văn bản (full-text index), ngốn rất nhiều RAM (tối thiểu 4GB-8GB). Loki chỉ đánh chỉ mục cho các Nhãn (Labels: container_name, service), còn nội dung log được nén lại thành các khối nhỏ (chunks). Nhờ đó Loki chỉ tốn vài trăm MB RAM, chạy cực êm trên máy ảo sinh viên.\n"
        "2. Đồng nhất hệ sinh thái: Loki sử dụng chung giao diện Grafana với Prometheus. Quản trị viên có thể vừa xem biểu đồ CPU vừa xem log trên cùng một màn hình.\n"
        "3. Ngôn ngữ truy vấn LogQL: LogQL có cú pháp tương tự như PromQL, rất dễ học và dễ viết truy vấn kết hợp.",
        "Nhấn mạnh từ khóa: 'Loki does not index the text, it only indexes metadata labels' (Loki không index văn bản mà chỉ index nhãn)."
    )

    add_question(16, "Promtail thu thập log từ Docker như thế nào?")
    add_answer(
        "Promtail được cấu hình mount volume trực tiếp vào Docker socket của máy chủ host tại đường dẫn /var/run/docker.sock. Nhờ cơ chế Docker SD (Service Discovery), Promtail tự động phát hiện tất cả container đang chạy, tự động lắng nghe luồng stdout và stderr của container, gắn nhãn metadata (như tên container, image, id), sau đó đóng gói và đẩy (Push) qua HTTP về máy chủ Loki ở cổng 3100.",
        "Chỉ file cấu hình monitoring/promtail-config.yml có khối docker_sd_configs."
    )

    add_question(17, "Em hãy viết và giải thích 3 câu truy vấn LogQL để kiểm tra log hệ thống?")
    add_answer(
        "Dạ thưa Thầy/Cô, 3 câu lệnh LogQL em sử dụng để vận hành hệ thống là:\n"
        "1. {container_name=\"movie_web\"}: Truy vấn toàn bộ log của ứng dụng web đặt vé Node.js theo thời gian thực.\n"
        "2. {container_name=\"movie_web\"} |= \"error\" or {container_name=\"movie_web\"} |= \"500\": Lọc ra các dòng log chứa thông báo lỗi hoặc mã lỗi HTTP 500 để khắc phục sự cố khẩn cấp.\n"
        "3. {container_name=\"movie_nginx\"} |= \"POST\": Lọc ra các lượt người dùng gửi dữ liệu đăng nhập hoặc đặt vé thông qua Nginx Reverse Proxy.",
        "Mở Grafana Explore -> dán câu lệnh {container_name=\"movie_web\"} -> bấm Run query cho thầy cô xem."
    )

    # --- NHÓM 6: HARDENING HỆ THỐNG ---
    p_group = doc.add_paragraph()
    p_group.paragraph_format.space_before = Pt(8)
    p_group.paragraph_format.space_after = Pt(2)
    rg6 = p_group.add_run("VI. TIÊU CHÍ 6: HARDENING HỆ THỐNG & BẢO MẬT ĐA TẦNG (1.5 ĐIỂM)")
    rg6.font.name = 'Times New Roman'
    rg6.font.size = Pt(12)
    rg6.font.bold = True
    rg6.font.color.rgb = RGBColor(30, 41, 59)

    add_question(18, "Hardening là gì? Em đã áp dụng những biện pháp Hardening cụ thể nào vào hệ thống này?")
    add_answer(
        "Hardening (Gia cố an ninh) là quá trình bảo vệ hệ thống bằng cách giảm thiểu bề mặt tấn công (attack surface) và loại bỏ các điểm yếu tiềm tàng. Em đã triển khai 4 biện pháp Hardening toàn diện:\n"
        "1. Cô lập mạng đa tầng (Network Segmentation): Tách hệ thống làm 2 mạng riêng biệt frontend_net và backend_net. MySQL hoàn toàn không mở cổng ra ngoài host.\n"
        "2. Mã hóa mật khẩu chuẩn cao cấp với thuật toán scrypt: Kèm Salt ngẫu nhiên 16 bytes chống tấn công Rainbow table và phần cứng ASIC.\n"
        "3. Session Cookie bảo mật ký số HMAC-SHA256: Có gắn cờ HttpOnly, SameSite=Lax và kiểm tra bằng hàm timingSafeEqual chống tấn công Timing Attack.\n"
        "4. Cấu hình Nginx Security Headers và server_tokens off: Ẩn thông tin phiên bản máy chủ và chặn Clickjacking, MIME-sniffing, XSS.",
        "Đây là nội dung ghi trọn 1.5 điểm của Tiêu chí 6."
    )

    add_question(19, "Tại sao em chia làm 2 mạng frontend_net và backend_net? Lợi ích bảo mật là gì?")
    add_answer(
        "Trong docker-compose.yml:\n"
        "- frontend_net: Chỉ chứa container Nginx và Web.\n"
        "- backend_net: Chứa container Web, MySQL, và các hệ thống giám sát (Prometheus, Loki, Exporters).\n"
        "Lợi ích bảo mật: Áp dụng nguyên tắc 'Đặc quyền tối thiểu' (Least Privilege). Nginx chỉ được phép giao tiếp với Web, không thể giao tiếp trực tiếp với Database. Ngay cả khi kẻ tấn công xâm nhập thành công vào Nginx từ Internet, chúng cũng bị chặn lại bởi tường lửa mạng ảo Docker và không thể gửi truy vấn trực tiếp vào cơ sở dữ liệu MySQL.",
        "Có thể chạy lệnh 'sudo docker network inspect backend_net' để chứng minh Nginx không nằm trong mạng này!"
    )

    add_question(20, "Tại sao em chọn thuật toán băm scrypt để lưu mật khẩu thay vì MD5 hay SHA-256 thông thường?")
    add_answer(
        "MD5 và SHA-256 là các thuật toán hàm băm thông điệp nhanh (Fast Hashes), được thiết kế để tính toán cực nhanh. Điều này khiến chúng trở nên cực kỳ nguy hiểm khi dùng lưu mật khẩu, vì hacker có thể dùng card đồ họa GPU hoặc máy đào ASIC để thử hàng tỷ mật khẩu mỗi giây (Brute-force).\n"
        "Ngược lại, scrypt là thuật toán Key Derivation Function có tính chất 'Memory-Hard' (đòi hỏi tiêu tốn nhiều bộ nhớ RAM khi tính toán). Kẻ tấn công không thể tận dụng sức mạnh tính toán song song của GPU để bẻ khóa hàng loạt. Kết hợp với Salt ngẫu nhiên 16 bytes, mỗi mật khẩu sinh ra một chuỗi băm độc nhất, vô hiệu hóa hoàn toàn phương pháp tấn công bằng Bảng Cầu Vồng (Rainbow Table).",
        "Thầy cô dạy môn An toàn thông tin nghe câu này sẽ cho điểm tuyệt đối!"
    )

    add_question(21, "Tại sao phải ký số HMAC-SHA256 cho Cookie phiên làm việc (Session Cookie)?")
    add_answer(
        "Nếu cookie lưu thông tin người dùng ở dạng thông thường (như {username: 'admin'}), kẻ tấn công có thể dễ dàng sửa giá trị cookie trên trình duyệt của họ để mạo danh tài khoản Quản trị viên (Privilege Escalation).\n"
        "Bằng việc sử dụng HMAC-SHA256 với một khóa bí mật (SESSION_SECRET) chỉ có máy chủ biết, mỗi khi client gửi cookie lên, máy chủ sẽ băm lại dữ liệu và so sánh với chữ ký đính kèm. Nếu kẻ tấn công tự ý sửa dù chỉ 1 ký tự, chữ ký sẽ không khớp và phiên đăng nhập bị hủy ngay lập tức.",
        "Chỉ hàm verify(cookie) trong web/index.js để minh họa."
    )

    # --- NHÓM 7: VẬN HÀNH & XỬ LÝ SỰ CỐ SRE ---
    p_group = doc.add_paragraph()
    p_group.paragraph_format.space_before = Pt(8)
    p_group.paragraph_format.space_after = Pt(2)
    rg7 = p_group.add_run("VII. TIÊU CHÍ 7: QUY TRÌNH VẬN HÀNH & KHẮC PHỤC SỰ CỐ SRE (1.0 ĐIỂM)")
    rg7.font.name = 'Times New Roman'
    rg7.font.size = Pt(12)
    rg7.font.bold = True
    rg7.font.color.rgb = RGBColor(30, 41, 59)

    add_question(22, "Nếu trang web bất ngờ bị chậm hoặc sập, em sẽ dùng các công cụ đã cài đặt để điều tra và xử lý theo các bước nào?")
    add_answer(
        "Em áp dụng quy trình 3 bước chuẩn SRE (Site Reliability Engineering):\n"
        "- Bước 1 (Triệu chứng - Metrics): Mở Grafana xem biểu đồ CPU/RAM của Host và Containers. Xem CPU có bị 100% không? MySQL có bị nghẽn số lượng kết nối (Threads Connected) không? Metric nào đang tăng đột biến?\n"
        "- Bước 2 (Nguyên nhân gốc rễ - Logs): Vào Grafana Explore dùng LogQL truy vấn {container_name=\"movie_web\"} |= \"error\" để xem chi tiết Stack Trace lỗi, hoặc kiểm tra log Nginx xem có bị tấn công DDoS / brute-force không.\n"
        "- Bước 3 (Khắc phục - Action): Nếu thiếu tài nguyên, mở rộng scale thêm container web: docker compose up -d --scale web=3. Nếu do nghẽn cơ sở dữ liệu, vào phpMyAdmin để tối ưu lại câu lệnh và đánh chỉ mục (Index) cho bảng.",
        "Câu trả lời này thể hiện tư duy kỹ sư vận hành hệ thống chuyên nghiệp."
    )

    add_question(23, "Dữ liệu của MySQL, Prometheus, Grafana có bị mất khi khởi động lại máy ảo hoặc tắt container không? Tại sao?")
    add_answer(
        "Dạ không bị mất. Vì toàn bộ dữ liệu quan trọng đều được gắn kết qua Docker Named Volumes có tính năng lưu trữ bền vững (Persistent Storage). Trong docker-compose.yml em đã cấu hình:\n"
        "- mysql_data: Lưu trữ toàn bộ database MySQL tại /var/lib/mysql.\n"
        "- prom_data: Lưu trữ cơ sở dữ liệu chuỗi thời gian TSDB của Prometheus.\n"
        "- grafana_data: Lưu cấu hình dashboards và tài khoản người dùng của Grafana.\n"
        "- loki_data: Lưu trữ các khối log nén của Loki.\n"
        "Ngay cả khi chạy lệnh docker compose down rồi bật lại bằng docker compose up -d, toàn bộ dữ liệu phim, tài khoản và lịch sử đặt vé vẫn còn nguyên vẹn 100%.",
        "Có thể chạy 'docker volume ls' để chỉ ra các volume này."
    )

    add_question(24, "Khi cập nhật mã nguồn mới từ Git trên máy ảo Ubuntu, em thực hiện những lệnh nào?")
    add_answer(
        "Quy trình cập nhật mã nguồn gồm 3 bước chuẩn:\n"
        "1. git pull origin main: Kéo các thay đổi mã nguồn mới nhất từ GitHub về thư mục dự án.\n"
        "2. sudo docker compose build web: Đóng gói lại Docker image của container web với mã nguồn mới.\n"
        "3. sudo docker compose up -d: Khởi động lại container với thời gian gián đoạn (downtime) gần như bằng 0 (Zero-downtime update).",
        "Ghi nhớ 3 lệnh này nếu thầy cô bảo kéo code mới hoặc sửa code trực tiếp tại chỗ."
    )

    add_question(25, "Làm thế nào để sao lưu (Backup) cơ sở dữ liệu MySQL định kỳ trong môi trường Docker?")
    add_answer(
        "Có thể sử dụng công cụ mysqldump chạy trực tiếp thông qua Docker Exec:\n"
        "sudo docker exec movie_mysql mysqldump -u root -prootpassword moviedb > backup_$(date +%F).sql\n"
        "Để tự động hóa định kỳ hàng ngày, ta có thể tạo một cronjob trên hệ điều hành Ubuntu để định kỳ 2h sáng tự động chạy lệnh này và đẩy file nén backup lên Google Drive hoặc máy chủ lưu trữ từ xa.",
        "Thầy cô chấm điểm rất thích những ý tưởng tự động hóa sao lưu dự phòng (Disaster Recovery)."
    )

    add_question(26, "Tại sao khi truy cập trang web bằng IP máy ảo, các ảnh poster phim HD vẫn tải về bình thường mà không bị lỗi?")
    add_answer(
        "Vì hệ thống lưu trữ đường dẫn ảnh trực tiếp từ CDN toàn cầu của TMDB (image.tmdb.org) với độ phân giải chuẩn w500. Trình duyệt của máy client khi render HTML sẽ tải trực tiếp poster từ CDN này. Riêng phần dữ liệu text phim đã được hệ thống seed sẵn vào MySQL ngay khi container web khởi chạy lần đầu tiên, đảm bảo trang web hoạt động độc lập và ổn định tuyệt đối ngay cả khi mạng quốc tế có độ trễ.",
        "Chứng minh: 8 bộ phim rạp thật với đầy đủ poster HD sắc nét trên trang chủ."
    )

    add_question(27, "Theo em, nếu hệ thống này được triển khai lên Production thực tế cho hàng triệu người dùng, em sẽ nâng cấp thêm những gì?")
    add_answer(
        "Em sẽ thực hiện 4 nâng cấp quan trọng:\n"
        "1. Chuyển sang Kubernetes (K8s): Thay thế Docker Compose bằng cụm K8s với Horizontal Pod Autoscaler (HPA) để tự động co giãn số lượng Pod theo lưu lượng người dùng.\n"
        "2. Caching với Redis: Đặt Redis trước MySQL để lưu đệm danh sách phim và khóa ghế thời gian thực (Distributed Lock với Redlock).\n"
        "3. Cổng thanh toán trực tuyến: Tích hợp cổng VNPAY/Momo qua cơ chế Webhook và chữ ký số an toàn.\n"
        "4. Đăng ký Domain thật và SSL Let's Encrypt: Mua tên miền công khai và dùng Certbot để cấp chứng chỉ SSL miễn phí tự động gia hạn.",
        "Câu trả lời kết thúc đồ án hoàn hảo, thể hiện tầm nhìn mở rộng (Scalability) của sinh viên!"
    )

    # Save to path
    doc.save(output_path)
    print(f"Document successfully created at: {output_path}")

if __name__ == '__main__':
    project_dir = r"C:\Users\tqpxc\Downloads\movie-system-v4\movie-system"
    target_path = os.path.join(project_dir, "TAI_LIEU_VAN_DAP_DO_AN.docx")
    downloads_path = r"C:\Users\tqpxc\Downloads\TAI_LIEU_VAN_DAP_DO_AN.docx"

    create_qa_document(target_path)
    try:
        shutil.copyfile(target_path, downloads_path)
        print(f"Copied to Downloads at: {downloads_path}")
    except Exception as e:
        print(f"Could not copy to Downloads: {e}")
