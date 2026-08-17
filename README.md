# ⛳ DNS Golf Outlet - Facebook Post Assistant

ระบบช่วยงาน Social Media Officer สำหรับดึงข้อมูลสินค้าพร้อมขาย และสินค้ามาใหม่ล่าสุด (New Clubs) จากเว็บ DNS Golf Outlet 62

## 📁 โฟลเดอร์ที่เก็บไฟล์ทั้งหมดบนเครื่องของคุณ (Folder Location)
`/Users/Nathee/.gemini/antigravity/scratch/dns-golf-facebook-helper`

## 📄 รายชื่อไฟล์ในโฟลเดอร์ (Files Included):
- `app.py` : เซิร์ฟเวอร์ Web App (Flask Backend & ZIP Exporter)
- `scraper.py` : ตัวสแกนเว็บ DNS Golf Outlet (รองรับสินค้ามาใหม่ และกรอง SOLD OUT)
- `cli.py` : โปรแกรมใช้งานผ่าน Command Line
- `start_app.sh` : สคริปต์คลิกเริ่มทำงานอัตโนมัติ
- `requirements.txt` : รายการไลบรารี Python ที่ใช้
- `static/index.html` : หน้าต่าง UI แดชบอร์ด
- `static/style.css` : สไตล์การตกแต่งหน้าเว็บ Modern Glassmorphic Dark UI
- `static/app.js` : ระบบควบคุมหน้าเว็บและพรีวิว Facebook

## 🚀 วิธีเปิดใช้งาน (How to Run)

### วิธีที่ 1: เปิดใช้งานหน้าเว็บ
1. เปิดเบราว์เซอร์แล้วไปที่: **`http://localhost:5050`**
2. หรือรันคำสั่งใน Terminal:
   ```bash
   bash /Users/Nathee/.gemini/antigravity/scratch/dns-golf-facebook-helper/start_app.sh
   ```

### วิธีที่ 2: ดึงข้อมูลผ่าน Terminal (CLI)
```bash
# ดึงสินค้ามาใหม่ล่าสุดในหมวด Iron Set
python3 /Users/Nathee/.gemini/antigravity/scratch/dns-golf-facebook-helper/cli.py iron-set --new-only

# ดึงสินค้าพร้อมขายทั้งหมดในหมวด Driver
python3 /Users/Nathee/.gemini/antigravity/scratch/dns-golf-facebook-helper/cli.py driver
```
