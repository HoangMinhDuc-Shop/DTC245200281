const express = require('express');
const mysql = require('mysql2');
const client = require('prom-client');
const path = require('path');
const crypto = require('crypto');

const SECRET = process.env.SESSION_SECRET || 'dev-secret-change-me';
const sign = o => { const b = Buffer.from(JSON.stringify(o)).toString('base64url'); return b + '.' + crypto.createHmac('sha256', SECRET).update(b).digest('base64url'); };
const verify = t => { const [b, sig] = (t || '').split('.'); if (!b || !sig) return null;
    const ok = crypto.createHmac('sha256', SECRET).update(b).digest('base64url');
    if (sig.length !== ok.length || !crypto.timingSafeEqual(Buffer.from(sig), Buffer.from(ok))) return null;
    try { return JSON.parse(Buffer.from(b, 'base64url').toString()); } catch (e) { return null; } };

const hashPw = (p, salt = crypto.randomBytes(16).toString('hex')) => 'scrypt$' + salt + '$' + crypto.scryptSync(p, salt, 32).toString('hex');
const checkPw = (p, st) => { if (st.startsWith('scrypt$')) { const a = Buffer.from(hashPw(p, st.split('$')[1])), b = Buffer.from(st); return a.length === b.length && crypto.timingSafeEqual(a, b); }
    return crypto.createHash('sha256').update(p).digest('hex') === st; };

const app = express();
const port = 3001;

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));
app.use(express.urlencoded({ extended: true }));
app.use(express.json());

// Helper parse cookies an toàn (giải mã tiếng Việt UTF-8)
app.use((req, res, next) => {
    const list = {};
    const rc = req.headers.cookie;
    if (rc) {
        rc.split(';').forEach(cookie => {
            const parts = cookie.split('=');
            const key = parts.shift().trim();
            const val = parts.join('=');
            try {
                list[key] = decodeURIComponent(val);
            } catch(e) {
                list[key] = val;
            }
        });
    }
    req.cookies = list;
    next();
});

// Prometheus Metrics
const register = new client.Registry();
client.collectDefaultMetrics({ register });

// 1. HTTP Requests Total chuẩn Prometheus
const httpRequestsTotal = new client.Counter({
    name: 'http_requests_total',
    help: 'Tong so luot HTTP request den he thong',
    labelNames: ['method', 'handler', 'status']
});
register.registerMetric(httpRequestsTotal);

// 2. Custom Business Metrics: Vé đã đặt
const totalTicketsBooked = new client.Counter({
    name: 'movie_tickets_booked_total',
    help: 'Tong so luong ve da dat',
    labelNames: ['movie_title', 'seat_type']
});
register.registerMetric(totalTicketsBooked);

// 3. Custom Business Metrics: Doanh thu bán vé (VND)
const totalRevenue = new client.Counter({
    name: 'movie_revenue_vnd_total',
    help: 'Tong doanh thu ban ve (VND)',
    labelNames: ['movie_title']
});
register.registerMetric(totalRevenue);

// 4. Custom Business Metrics: Phiên hoạt động
const activeUsersGauge = new client.Gauge({
    name: 'active_sessions_total',
    help: 'So luong phien nguoi dung dang hoat dong'
});
register.registerMetric(activeUsersGauge);

// 5. Custom Business Metrics: Tổng số phim
const totalMoviesGauge = new client.Gauge({
    name: 'movie_catalog_total',
    help: 'Tong so phim trong danh muc'
});
register.registerMetric(totalMoviesGauge);

// Middleware tự động đếm mọi HTTP request vào Prometheus
app.use((req, res, next) => {
    res.on('finish', () => {
        const handler = req.route ? req.route.path : req.path;
        httpRequestsTotal.inc({
            method: req.method,
            handler: handler || req.path,
            status: `${res.statusCode}`
        });
    });
    next();
});

// Kết nối MySQL Pool
const db = mysql.createPool({
    host: 'mysql',
    user: 'root',
    password: 'rootpassword',
    database: 'moviedb',
    waitForConnections: true,
    connectionLimit: 10
});

const GENRES = {28:'Hành động',12:'Phiêu lưu',16:'Hoạt hình',35:'Hài',80:'Hình sự',18:'Chính kịch',10751:'Gia đình',14:'Giả tưởng',27:'Kinh dị',9648:'Bí ẩn',10749:'Lãng mạn',878:'Khoa học viễn tưởng',53:'Giật gân',10752:'Chiến tranh'};

const REAL_TMDB_FALLBACK = [
    [1058424, 'Hope: Vùng Tử Địa', 'Hành động / Bí ẩn', 110000, '120 phút', '★ 6.9', 'https://image.tmdb.org/t/p/w500/yY5GFSFM4eQknenk2oCoC19EeF5.jpg', 'https://image.tmdb.org/t/p/w1280/qqHFLg90IUSoTmSMpKOOW5RyqN3.jpg', 'Tại Hope Harbor, cảnh sát trưởng Bum-seok nhận được tin báo khẩn cấp về sự xuất hiện của một con hổ, hé lộ sự thật ngoài sức tưởng tượng.'],
    [1153576, 'Chiến Binh Đường Phố (Street Fighter)', 'Hành động / Giả tưởng', 105000, '115 phút', '★ 6.3', 'https://image.tmdb.org/t/p/w500/lnaGK9y2Dw1cwRz8e7X5plvYVdI.jpg', 'https://image.tmdb.org/t/p/w1280/qRN8eqYwG6HPSy0i3fKzuLrUOhp.jpg', 'Lấy bối cảnh năm 1993, Ryu và Ken bị kéo trở lại giải Chiến Binh Thế Giới khốc liệt để đối đầu âm mưu chết chóc.'],
    [1148365, 'Matchbox Phim Điện Ảnh', 'Hành động / Hài', 95000, '105 phút', '★ 7.8', 'https://image.tmdb.org/t/p/w500/l6Pp3m0L3kOaSyjkjUgl93C0IJg.jpg', 'https://image.tmdb.org/t/p/w1280/jdJsnhHfkIi3J7jwfiCFT4gXNx5.jpg', 'Cuộc hội ngộ của một nhóm bạn thuở nhỏ bỗng rẽ vào bước ngoặt bất ngờ khi cả bọn rơi vào âm mưu quốc tế nguy hiểm.'],
    [1101412, 'Cú Rơi Tử Thần 2: Điểm Chết', 'Giật gân / Phiêu lưu', 100000, '110 phút', '★ 7.3', 'https://image.tmdb.org/t/p/w500/fgSm5ylwiXbIHn8UbUXDjk9RRu4.jpg', 'https://image.tmdb.org/t/p/w1280/nGau0KBOaRILSK5MqFcuTfv7GMl.jpg', 'Jax và Luce thử thách cung đường ván treo khét tiếng trên núi Kwan ở Thái Lan, nhưng một vụ sạt lở khiến Jax mắc kẹt ở độ cao 3,000 feet.'],
    [1255833, 'Cá Voi Nuốt Chửng (Whalefall)', 'Giật gân / Tâm lý', 90000, '100 phút', '★ 7.1', 'https://image.tmdb.org/t/p/w500/jlP8XDjZN89GrpM3je5Uf8Grqx8.jpg', 'https://image.tmdb.org/t/p/w1280/shW2jHkQLZVv4Fko2rJDqTGU0gx.jpg', 'Một thợ lặn biển bị cá nhà táng nặng 60 tấn nuốt chửng, chỉ còn 1 giờ để thoát ra trước khi cạn bình oxy.'],
    [1400837, 'Người Mẹ Khác (Other Mommy)', 'Kinh dị / Giật gân', 85000, '95 phút', '★ 5.8', 'https://image.tmdb.org/t/p/w500/nZYi7HeXJVfJmZ0kprb1cJBHN2g.jpg', 'https://image.tmdb.org/t/p/w1280/ncm7djsVTHQQMX2HEbEVxMUFchG.jpg', 'Một cô bé cùng gia đình bị ám bởi một thực thể tà ác, kẻ quyết tâm chiếm lấy thân xác cô để trú ngụ vĩnh viễn.'],
    [1423191, 'Vùng Đất Quỷ Dữ (Resident Evil)', 'Kinh dị / Hành động', 110000, '125 phút', '★ 7.3', 'https://image.tmdb.org/t/p/w500/jlFMvLuzjwt7aI1QVtiNVnFHNBe.jpg', 'https://image.tmdb.org/t/p/w1280/3icyRAqgakNcQn6aDVz9libFmBA.jpg', 'Cơn ác mộng sinh học bùng nổ khi thành phố chìm trong đại dịch thây ma, buộc những người sống sót phải chiến đấu sinh tồn.'],
    [1302904, 'Bùa Yêu: Bí Mật Gia Tộc', 'Phép thuật / Hài', 90000, '110 phút', '★ 7.1', 'https://image.tmdb.org/t/p/w500/fNyixhNFs5iWZ3QXhdT8t8D6lsk.jpg', 'https://image.tmdb.org/t/p/w1280/oIglj0Jy9duG4LnrRUpH8n001Pk.jpg', 'Hai chị em nhà Owens đối mặt với lời nguyền cổ xưa dưới ánh trăng huyền bí để bảo vệ hạnh phúc gia đình.']
];

function seedFallbackMovies() {
    REAL_TMDB_FALLBACK.forEach(m => {
        db.query(`INSERT INTO movies (tmdb_id,title,genre,price,duration,rating,poster,backdrop,overview) VALUES (?,?,?,?,?,?,?,?,?)
            ON DUPLICATE KEY UPDATE title=VALUES(title),genre=VALUES(genre),price=VALUES(price),rating=VALUES(rating),poster=VALUES(poster),backdrop=VALUES(backdrop),overview=VALUES(overview)`,
            m);
    });
    console.log('TMDB: đã đồng bộ 8 phim chiếu rạp thật (TMDB HD)');
}

// Lấy phim đang chiếu thật (poster + backdrop) từ TMDB
async function syncTMDB() {
    const key = process.env.TMDB_API_KEY;
    try {
        const r = await fetch(`https://api.themoviedb.org/3/movie/now_playing?api_key=${key}&language=vi-VN&region=VN&page=1`);
        const { results = [] } = await r.json();
        if (!results || results.length === 0) throw new Error('Không có dữ liệu trả về');
        const img = (p, s) => p ? `https://image.tmdb.org/t/p/${s}${p}` : null;
        results.filter(m => m.poster_path).slice(0, 8).forEach(m => {
            db.query(`INSERT INTO movies (tmdb_id,title,genre,price,duration,rating,poster,backdrop,overview) VALUES (?,?,?,?,?,?,?,?,?)
                ON DUPLICATE KEY UPDATE title=VALUES(title),rating=VALUES(rating),poster=VALUES(poster),backdrop=VALUES(backdrop),overview=VALUES(overview)`,
                [m.id, m.title, m.genre_ids.map(g => GENRES[g]).filter(Boolean).slice(0, 2).join(' / ') || 'Phim', 95000, '—',
                 '★ ' + m.vote_average.toFixed(1), img(m.poster_path, 'w500'), img(m.backdrop_path, 'w1280'), m.overview]);
        });
        console.log('TMDB: đã đồng bộ', Math.min(results.length, 8), 'phim');
    } catch (e) {
        console.log('TMDB API bị mạng chặn, tự động kích hoạt chế độ nạp 8 phim rạp thật!');
        seedFallbackMovies();
    }
}
function seedOrSync() {
    if (process.env.TMDB_API_KEY) return syncTMDB();
    seedFallbackMovies();
}

// Khởi tạo Database
function initDB() {
    db.query(`
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            fullname VARCHAR(100),
            role VARCHAR(20) DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    `, () => {
        const hashAdmin = hashPw('admin123');
        const hashUser = hashPw('123456');
        db.query(`INSERT IGNORE INTO users (username, password, fullname, role) VALUES 
            ('admin', '${hashAdmin}', 'Quản Trị Viên', 'admin'),
            ('khachhang', '${hashUser}', 'Nguyễn Văn Khách', 'user')
        `);
    });

    db.query(`
        CREATE TABLE IF NOT EXISTS movies (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255), genre VARCHAR(100), price INT,
            duration VARCHAR(50), rating VARCHAR(10), poster VARCHAR(500)
        )
    `, () => {
        const alters = [
            "ALTER TABLE movies ADD COLUMN backdrop VARCHAR(500)",
            "ALTER TABLE movies ADD COLUMN overview TEXT",
            "ALTER TABLE movies ADD COLUMN tmdb_id INT UNIQUE",
            "DELETE FROM movies WHERE poster LIKE '%unsplash%'"
        ];
        let i = 0;
        const next = () => i < alters.length ? db.query(alters[i++], next) : seedOrSync();
        next();
    });

    db.query(`
        CREATE TABLE IF NOT EXISTS orders (
            id INT AUTO_INCREMENT PRIMARY KEY,
            booking_code VARCHAR(50) UNIQUE,
            username VARCHAR(50),
            movie_title VARCHAR(255),
            showtime VARCHAR(100),
            seats VARCHAR(255),
            total_price INT,
            status VARCHAR(20) DEFAULT 'PAID',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    `);

    db.query(`
        CREATE TABLE IF NOT EXISTS booked_seats (
            id INT AUTO_INCREMENT PRIMARY KEY,
            movie_title VARCHAR(255),
            showtime VARCHAR(100),
            seat_code VARCHAR(20),
            order_id INT,
            UNIQUE KEY unique_seat (movie_title, showtime, seat_code)
        )
    `, () => {
        // Đồng bộ số liệu từ Database MySQL vào Prometheus Metrics ngay khi khởi động
        setTimeout(() => {
            db.query("SELECT COUNT(*) AS total FROM movies", (err, r) => {
                if (!err && r && r[0]) totalMoviesGauge.set(r[0].total);
            });
            db.query("SELECT movie_title, seats, total_price FROM orders", (err, rows) => {
                if (!err && rows && rows.length > 0) {
                    rows.forEach(row => {
                        const seatList = (row.seats || '').split(',').map(s => s.trim()).filter(Boolean);
                        const count = seatList.length || 1;
                        const hasVip = seatList.some(s => s.includes('VIP'));
                        totalTicketsBooked.inc({ movie_title: row.movie_title, seat_type: hasVip ? 'VIP' : 'Standard' }, count);
                        totalRevenue.inc({ movie_title: row.movie_title }, Number(row.total_price) || 0);
                    });
                    console.log(`[Prometheus] Synced ${rows.length} existing orders into metrics.`);
                }
            });
        }, 1500);
    });
}
setTimeout(initDB, 3000);

// Middleware xác thực phiên
function authMiddleware(req, res, next) {
    req.user = verify(req.cookies.user_auth);
    next();
}
app.use(authMiddleware);

// Route Trang chủ
app.get('/', (req, res) => {
    db.query("SELECT * FROM movies", (err, movies) => {
        res.render('index', { user: req.user, movies: movies || [] });
    });
});

// API lấy ghế đã bán
app.get('/api/occupied-seats', (req, res) => {
    const { movie, showtime } = req.query;
    db.query("SELECT seat_code FROM booked_seats WHERE movie_title = ? AND showtime = ?", 
        [movie, showtime], (err, rows) => {
            if (err) return res.json({ occupied: [] });
            res.json({ occupied: rows.map(r => r.seat_code) });
        }
    );
});

// Auth Routes
app.get('/login', (req, res) => res.render('login', { user: req.user, error: null }));
app.get('/register', (req, res) => res.render('register', { user: req.user, error: null }));

app.post('/login', (req, res) => {
    const { username, password } = req.body;
    db.query("SELECT * FROM users WHERE username = ?", [username], (err, users) => {
        const u = users && users[0];
        if (!u || !checkPw(password || '', u.password)) return res.render('login', { user: null, error: 'Sai tài khoản hoặc mật khẩu!' });
        if (!u.password.startsWith('scrypt$')) db.query("UPDATE users SET password = ? WHERE id = ?", [hashPw(password), u.id]);
        const userObj = { id: u.id, username: u.username, fullname: u.fullname, role: u.role };
        
        // MÃ HÓA COOKIE ĐÚNG CHUẨN (tránh lỗi 502 với tiếng Việt)
        const encodedCookie = sign(userObj);
        res.setHeader('Set-Cookie', `user_auth=${encodedCookie}; Path=/; HttpOnly; SameSite=Lax`);
        
        activeUsersGauge.inc();
        res.redirect('/');
    });
});

app.post('/register', (req, res) => {
    const { username, password, fullname } = req.body;
    const hash = hashPw(password || '');
    db.query("INSERT INTO users (username, password, fullname) VALUES (?, ?, ?)", [username, hash, fullname], (err) => {
        if (err) return res.render('register', { user: null, error: 'Tên đăng nhập đã tồn tại!' });
        res.redirect('/login');
    });
});

app.get('/logout', (req, res) => {
    res.setHeader('Set-Cookie', 'user_auth=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT');
    activeUsersGauge.dec();
    res.redirect('/');
});

// Giá vé luôn tính lại ở server
app.post('/book', (req, res, next) => {
    db.query("SELECT price FROM movies WHERE title = ?", [req.body.movie_title], (e, r) => {
        if (!r || !r[0]) return res.redirect('/');
        const seats = String(req.body.seats || '').split(',').map(x => x.trim()).filter(Boolean);
        req.body.total_price = seats.reduce((a, x) => a + r[0].price + (x.includes('VIP') ? 20000 : 0), 0);
        next();
    });
});

// Route Đặt vé
app.post('/book', (req, res) => {
    if (!req.user) return res.redirect('/login');

    const { movie_title, seats, showtime, total_price } = req.body;
    const seatList = seats ? seats.split(',').map(s => s.trim()) : [];
    if (seatList.length === 0) return res.redirect('/');

    const bookingCode = 'CINE-' + Math.floor(100000 + Math.random() * 900000);
    const finalPrice = parseInt(total_price) || 0;

    db.query("SELECT seat_code FROM booked_seats WHERE movie_title = ? AND showtime = ? AND seat_code IN (?)",
        [movie_title, showtime, seatList], (err, occupied) => {
            if (occupied && occupied.length > 0) {
                return res.send(`<script>alert('Ghế ${occupied.map(o => o.seat_code).join(', ')} vừa bị người khác đặt!'); window.location.href='/';</script>`);
            }

            db.query("INSERT INTO orders (booking_code, username, movie_title, showtime, seats, total_price) VALUES (?, ?, ?, ?, ?, ?)",
                [bookingCode, req.user.username, movie_title, showtime, seatList.join(', '), finalPrice], (err, result) => {
                    if (err) return res.redirect('/');
                    const orderId = result.insertId;

                    const seatValues = seatList.map(s => [movie_title, showtime, s, orderId]);
                    db.query("INSERT INTO booked_seats (movie_title, showtime, seat_code, order_id) VALUES ?", [seatValues], () => {
                        totalTicketsBooked.inc({ movie_title, seat_type: seatList.some(s => s.includes('VIP')) ? 'VIP' : 'Standard' }, seatList.length);
                        totalRevenue.inc({ movie_title }, finalPrice);

                        res.render('success', {
                            user: req.user,
                            bookingCode,
                            movie_title,
                            seats: seatList.join(', '),
                            showtime,
                            total_price: finalPrice.toLocaleString('vi-VN') + ' đ'
                        });
                    });
                }
            );
        }
    );
});

// Route Soát vé
app.get('/checkin', (req, res) => res.render('checkin', { user: req.user }));
app.post('/checkin', (req, res) => {
    if (!req.user || req.user.role !== 'admin') return res.status(403).json({ ok: false, message: 'Chỉ nhân viên rạp mới được soát vé' });
    const m = String(req.body.code || '').toUpperCase().match(/CINE-\d{6}/);
    if (!m) return res.json({ ok: false, message: 'Mã vé không hợp lệ' });
    db.query("SELECT * FROM orders WHERE booking_code = ?", [m[0]], (e, o) => {
        if (!o || !o[0]) return res.json({ ok: false, message: 'Vé không tồn tại' });
        db.query("UPDATE orders SET status='USED' WHERE id = ? AND status <> 'USED'", [o[0].id], (e2, r) => {
            const ok = r && r.affectedRows === 1;
            res.json({ ok, message: ok ? 'SOÁT VÉ THÀNH CÔNG – mời vào phòng chiếu' : 'VÉ ĐÃ ĐƯỢC SỬ DỤNG trước đó', order: o[0] });
        });
    });
});

// Route Admin
app.get('/admin', (req, res) => {
    if (!req.user || req.user.role !== 'admin') return res.status(403).send("Bạn không có quyền truy cập trang quản trị!");
    const q = sql => new Promise(r => db.query(sql, (e, x) => r(x || [])));
    Promise.all([
        q("SELECT * FROM orders ORDER BY id DESC LIMIT 200"),
        q("SELECT COALESCE(SUM(total_price),0) rev, COUNT(*) n, COALESCE(SUM(status='USED'),0) used FROM orders"),
        q("SELECT DATE_FORMAT(created_at,'%d/%m') d, SUM(total_price) rev FROM orders WHERE created_at >= NOW() - INTERVAL 7 DAY GROUP BY d ORDER BY MIN(created_at)"),
        q("SELECT movie_title t, SUM(total_price) rev FROM orders GROUP BY movie_title ORDER BY rev DESC LIMIT 6")
    ]).then(([orders, [s], byDay, byMovie]) => res.render('admin', { user: req.user, orders, s, byDay, byMovie }));
});

// Prometheus Endpoint
app.get('/metrics', async (req, res) => {
    res.setHeader('Content-Type', register.contentType);
    res.send(await register.metrics());
});

app.listen(port, () => console.log(`CineMaster running on port ${port}`));
