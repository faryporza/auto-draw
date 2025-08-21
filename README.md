# Auto Drawing with OpenCV + PyDirectInput

โปรแกรมนี้ใช้ในการวิเคราะห์ภาพด้วย OpenCV เพื่อตรวจจับเส้นขอบ (contour) และสั่งเมาส์วาดเส้นลงบนหน้าจอหรือเกมอัตโนมัติผ่าน PyDirectInput โดยสามารถเลือกความเร็วการวาด กำหนดจุดเริ่มต้น และหยุดการทำงานได้ด้วยคีย์บอร์ด

---

## Requirements

* Python 3.8 ขึ้นไป
* ระบบปฏิบัติการ Windows (แนะนำ เนื่องจากใช้ `pydirectinput` และ `keyboard`)
* ไฟล์ภาพ `image.png` ที่ใช้เป็นต้นแบบ

---

## การติดตั้งด้วย Virtual Environment

1. สร้างและเข้าใช้งาน virtual environment

   ```bash
   python -m venv venv
   venv\Scripts\activate       # บน Windows
   source venv/bin/activate    # บน Linux/Mac
   ```

2. ติดตั้ง dependencies

   ```bash
   pip install -r requirements.txt
   ```

   หรือหากไม่มีไฟล์ `requirements.txt` ใช้คำสั่งนี้:

   ```bash
   pip install opencv-python numpy pyautogui pydirectinput keyboard
   ```

---

## โครงสร้างโครงการ

```
.
├── image.png        # ภาพต้นแบบ
├── main.py          # ไฟล์โค้ดหลัก
├── requirements.txt # รายการ dependencies
└── README.md
```

ตัวอย่าง `requirements.txt`

```
opencv-python
numpy
pyautogui
pydirectinput
keyboard
```

---

## วิธีใช้งาน

1. วางไฟล์ `image.png` ในโฟลเดอร์เดียวกับ `main.py`

2. รันโปรแกรม

   ```bash
   python main.py
   ```

3. โปรแกรมจะวิเคราะห์ภาพและแสดงรายละเอียด contours รวมถึงถามให้เลือกความเร็วการวาด

4. กดปุ่ม **Insert (INS)** เพื่อกำหนดตำแหน่งมุมซ้ายบนของพื้นที่ที่จะวาด

5. โปรแกรมจะนับถอยหลังแล้วเริ่มวาดอัตโนมัติ

6. หากต้องการหยุด ให้กดปุ่ม **End**

---

## คำสั่งควบคุม

* Insert (INS): ตั้งตำแหน่งมุมซ้ายบน (origin point)
* End: หยุดการวาดทันที

---

## ระดับความเร็ว

มีทั้งหมด 5 ระดับ

1. Very Slow - ช้ามาก เหมาะสำหรับภาพที่ซับซ้อน
2. Slow - ช้า ใช้ทดสอบการทำงาน
3. Medium - ปานกลาง (ค่าเริ่มต้น)
4. Fast - เร็วขึ้น อาจมีข้อผิดพลาดบ้าง
5. Very Fast - เร็วที่สุด แต่เสี่ยงผิดพลาดสูง




