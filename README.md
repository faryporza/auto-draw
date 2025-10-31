# 🎨 Auto Draw - Automatic Drawing Tool

โปรแกรมวาดรูปอัตโนมัติที่รองรับทั้ง Windows และ macOS

## 🖥️ Platform Support

| Platform | File | Keyboard Shortcuts |
|----------|------|-------------------|
| **Windows** | `main.py` | Insert (set origin), End (stop) |
| **macOS** | `mac.py` | F6 (set origin), ESC (stop) |

---

## 📦 Installation

### วิธีที่ 1: ใช้ Virtual Environment (แนะนำ) ✅

#### สำหรับ macOS:
```bash
# สร้าง virtual environment ด้วย Python 3.9
python3.9 -m venv .venv

# เปิดใช้งาน virtual environment
source env/bin/activate

# ติดตั้ง dependencies
pip install -r requirements-mac.txt
```

#### สำหรับ Windows:
```bash
# สร้าง virtual environment ด้วย Python 3.9
python -m venv .venv

# เปิดใช้งาน virtual environment
.venv\Scripts\activate

# ติดตั้ง dependencies
pip install -r requirements-windows.txt
```

### วิธีที่ 2: ใช้ Docker (ไม่แนะนำสำหรับ GUI automation) ⚠️

**หมายเหตุ:** Docker ไม่สามารถควบคุม mouse/keyboard ของ host ได้โดยตรง แนะนำให้ใช้ Virtual Environment แทน

```bash
# สำหรับ macOS
docker-compose --profile mac build
docker-compose --profile mac up

# สำหรับ Windows
docker-compose --profile windows build
docker-compose --profile windows up
```

---

## 🚀 Usage

### macOS:
```bash
# เปิดใช้งาน virtual environment
source env/bin/activate

# รันโปรแกรม
python mac.py
```

**⚠️ macOS Permissions:**
ไปที่ **System Settings → Privacy & Security → Accessibility** และเพิ่ม:
- Terminal หรือ VSCode
- Python.app

### Windows:
```bash
# เปิดใช้งาน virtual environment
.venv\Scripts\activate

# รันโปรแกรม
python main.py
```

---

## 🎮 How to Use

1. **เตรียมรูปภาพ:** วางไฟล์ `image.png` ในโฟลเดอร์เดียวกับโปรแกรม
2. **รันโปรแกรม:** ดูข้อมูล preview และเลือกความเร็วการวาด
3. **กดปุ่มเพื่อเริ่ม:**
   - **macOS:** กด `F6` เพื่อกำหนดตำแหน่งเริ่มต้น
   - **Windows:** กด `Insert` เพื่อกำหนดตำแหน่งเริ่มต้น
4. **หยุดการวาด:**
   - **macOS:** กด `ESC`
   - **Windows:** กด `End`

---

## ⚡ Speed Settings

| Speed | Description | Use Case |
|-------|-------------|----------|
| **Very Slow** | ช้ามาก | ภาพซับซ้อนมาก |
| **Slow** | ช้า | การทดสอบ |
| **Medium** | ปานกลาง (แนะนำ) | ใช้งานทั่วไป |
| **Fast** | เร็ว | ภาพง่าย (เสี่ยงข้อผิดพลาด) |
| **Very Fast** | เร็วมาก | ทดสอบเท่านั้น (เสี่ยงมาก) |

---

## 📋 Requirements

- Python 3.9+
- opencv-python
- numpy
- pyautogui
- pydirectinput
- **Windows:** keyboard
- **macOS:** pynput

---

## 🔧 Technical Details

### Windows Version (`main.py`)
- ใช้ `keyboard` module สำหรับจับ global hotkeys
- รองรับปุ่ม Insert และ End

### macOS Version (`mac.py`)
- ใช้ `pynput` แทน `keyboard` (เพราะ keyboard ไม่รองรับ macOS)
- เปลี่ยนปุ่ม Insert → F6
- เปลี่ยนปุ่ม End → ESC
- ต้องการสิทธิ์ Accessibility

---

## 🐛 Troubleshooting

### macOS: "Operation not permitted"
ตรวจสอบว่าได้เพิ่ม Terminal/VSCode/Python ใน **Accessibility** แล้ว

### Windows: "keyboard module not found"
```bash
pip install keyboard
```

### ภาพไม่โหลด
ตรวจสอบว่ามีไฟล์ `image.png` ในโฟลเดอร์เดียวกับโปรแกรม

---

## 📝 License

MIT License

---

## 👨‍💻 Author

Created for automatic drawing automation on both Windows and macOS platforms




