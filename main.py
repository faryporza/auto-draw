import cv2
import time
import threading
import keyboard  # ต้องติดตั้งด้วย pip install keyboard
import pydirectinput  # ต้องติดตั้งด้วย pip install pydirectinput
import pyautogui
import numpy as np # เพิ่มเข้ามา

# โหลดภาพและหาเส้นขอบ
img = cv2.imread("image.png", 0)
if img is None:
    print("❌ ไม่พบไฟล์ image.png หรือไฟล์เสียหาย")
    exit()

edges = cv2.Canny(img, 50, 150)
contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

print(f"🔍 พบ contours จำนวน: {len(contours)}")

# ค่าตัวแปรควบคุม
origin_x, origin_y = 0, 0
origin_set = False
should_stop = False
drawing_speed = "medium"  # เพิ่มตัวแปรความเร็ว

# การตั้งค่าความเร็ว
SPEED_SETTINGS = {
    "very_slow": {
        "move_duration": 0.05,
        "draw_duration": 0.03,
        "line_delay": 0.5,
        "mouse_delay": 0.2
    },
    "slow": {
        "move_duration": 0.03,
        "draw_duration": 0.02,
        "line_delay": 0.3,
        "mouse_delay": 0.15
    },
    "medium": {
        "move_duration": 0.02,
        "draw_duration": 0.01,
        "line_delay": 0.1,
        "mouse_delay": 0.1
    },
    "fast": {
        "move_duration": 0.01,
        "draw_duration": 0.005,
        "line_delay": 0.05,
        "mouse_delay": 0.05
    },
    "very_fast": {
        "move_duration": 0.005,
        "draw_duration": 0.001,
        "line_delay": 0.01,
        "mouse_delay": 0.02
    }
}

def show_preview():
    """สร้างและบันทึกภาพ preview แล้วแสดงข้อมูล"""
    global drawing_speed
    
    print("🖼️  กำลังสร้าง preview...")
    
    # สร้างภาพสี 3 ช่องสำหรับ preview
    preview_img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    
    # สร้างภาพว่างสำหรับแสดง contours
    contours_img = np.zeros_like(preview_img)
    
    # วาด contours ทั้งหมดด้วยสีต่างๆ
    for i, cnt in enumerate(contours):
        arc_length = cv2.arcLength(cnt, False)
        if arc_length >= 20:  # เฉพาะเส้นที่จะวาดจริง
            color = (0, 255, 0)  # เขียวสำหรับเส้นที่จะวาด
        else:
            color = (0, 0, 255)  # แดงสำหรับเส้นที่จะข้าม
        
        cv2.drawContours(contours_img, [cnt], -1, color, 2)
        cv2.drawContours(preview_img, [cnt], -1, color, 1)
    
    print("✅ วิเคราะห์ภาพเสร็จแล้ว")
    
    # แสดงข้อมูลภาพ
    print("\n🖼️  ข้อมูลภาพ:")
    print(f"   - ขนาดภาพ: {img.shape[1]} x {img.shape[0]} pixels")
    print(f"   - จำนวน contours ทั้งหมด: {len(contours)}")
    
    # นับ contours ที่มีขนาดเหมาะสม
    valid_contours = 0
    total_points = 0
    for cnt in contours:
        arc_length = cv2.arcLength(cnt, False)
        if arc_length >= 20:
            valid_contours += 1
            total_points += len(cnt)
    
    print(f"   - จำนวน contours ที่จะวาด: {valid_contours}")
    print(f"   - จำนวนจุดทั้งหมด: {total_points}")
    print(f"   - ค่า Canny edges: 50-150")
    
    # แสดงข้อมูลแต่ละ contour
    print("\n📋 รายละเอียด contours:")
    for i, cnt in enumerate(contours):
        arc_length = cv2.arcLength(cnt, False)
        area = cv2.contourArea(cnt)
        points_count = len(cnt)
        status = "✅ จะวาด" if arc_length >= 20 else "❌ ข้าม"
        print(f"   - Contour {i+1}: ความยาว={arc_length:.1f}, พื้นที่={area:.1f}, จุด={points_count} {status}")
    
    # คำนวณเวลาตามความเร็วที่เลือก
    speed_config = SPEED_SETTINGS[drawing_speed]
    estimated_time = total_points * speed_config["draw_duration"] + valid_contours * speed_config["line_delay"]
    
    print(f"\n🎨 การวาดจะใช้เวลาประมาณ: {estimated_time:.1f} วินาที")
    
    # เลือกความเร็ว
    print("\n⚡ เลือกความเร็วการวาด:")
    print("1. Very Slow (ช้ามาก - เหมาะสำหรับภาพซับซ้อน)")
    print("2. Slow (ช้า - เหมาะสำหรับการทดสอบ)")
    print("3. Medium (ปานกลาง - แนะนำ) [ค่าเริ่มต้น]")
    print("4. Fast (เร็ว - เสี่ยงข้อผิดพลาด)")
    print("5. Very Fast (เร็วมาก - เสี่ยงมาก)")
    
    while True:
        choice = input("กรุณาเลือกความเร็ว (1-5) หรือกด Enter เพื่อใช้ค่าเริ่มต้น: ").strip()
        
        if choice == "" or choice == "3":
            drawing_speed = "medium"
            break
        elif choice == "1":
            drawing_speed = "very_slow"
            break
        elif choice == "2":
            drawing_speed = "slow"
            break
        elif choice == "4":
            drawing_speed = "fast"
            break
        elif choice == "5":
            drawing_speed = "very_fast"
            break
        else:
            print("❌ กรุณาเลือกตัวเลข 1-5 เท่านั้น")
    
    speed_names = {
        "very_slow": "ช้ามาก",
        "slow": "ช้า", 
        "medium": "ปานกลาง",
        "fast": "เร็ว",
        "very_fast": "เร็วมาก"
    }
    
    # คำนวณเวลาใหม่ตามความเร็วที่เลือก
    speed_config = SPEED_SETTINGS[drawing_speed]
    estimated_time = total_points * speed_config["draw_duration"] + valid_contours * speed_config["line_delay"]
    
    print(f"✅ เลือกความเร็ว: {speed_names[drawing_speed]}")
    print(f"🕐 เวลาการวาดประมาณ: {estimated_time:.1f} วินาที")
    print("\n📝 กด Enter เพื่อดำเนินการต่อ หรือ Ctrl+C เพื่อออกจากโปรแกรม")
    input("กดปุ่ม Enter...")
    
    return True

def wait_for_insert_key():
    global origin_x, origin_y, origin_set
    print("⌨️ กรุณากดปุ่ม Insert (INS) เพื่อกำหนดตำแหน่งมุมซ้ายบน...")
    keyboard.wait("insert")
    origin_x, origin_y = pyautogui.position()
    origin_set = True
    print(f"✅ ตำแหน่งเริ่มต้นถูกตั้งไว้ที่: ({origin_x}, {origin_y})")

def watch_for_end_key():
    global should_stop
    keyboard.wait("end")
    should_stop = True
    print("⛔ หยุดการวาดแล้ว (กด End)")

def sort_contours(contours, start_point=(0, 0)):
    """จัดเรียง contours ตามระยะทางที่ใกล้ที่สุด"""
    if not contours:
        return []

    # กรองเฉพาะ contours ที่มีขนาดเหมาะสม
    filtered_contours = []
    for cnt in contours:
        arc_length = cv2.arcLength(cnt, False)
        if arc_length >= 20:  # เอาเฉพาะเส้นที่ยาวพอ
            filtered_contours.append(cnt)
    
    print(f"🔄 กรอง contours: {len(contours)} -> {len(filtered_contours)}")
    
    if not filtered_contours:
        print("⚠️ ไม่มีเส้นที่เหมาะสมสำหรับการวาด")
        return []

    sorted_contours = []
    remaining_contours = list(filtered_contours)
    
    # หา contour แรกที่ใกล้กับ start_point ที่สุด
    def get_distance_to_point(cnt, point):
        # หาจุดที่ใกล้ที่สุดใน contour กับ point ที่กำหนด
        points = cnt.squeeze(axis=1)
        if len(points.shape) == 1:  # ถ้าเป็น 1D array
            points = points.reshape(1, -1)
        distances = np.sqrt(np.sum((points - point)**2, axis=1))
        return np.min(distances)

    # หา contour แรก
    first_cnt_index = np.argmin([get_distance_to_point(cnt, start_point) for cnt in remaining_contours])
    current_contour = remaining_contours.pop(first_cnt_index)
    sorted_contours.append(current_contour)
    
    # จุดสุดท้ายของ contour ปัจจุบัน
    last_point = current_contour.squeeze(axis=1)[-1]

    while remaining_contours:
        # หา contour ที่เหลือที่ใกล้กับ last_point ที่สุด
        next_cnt_index = np.argmin([get_distance_to_point(cnt, last_point) for cnt in remaining_contours])
        current_contour = remaining_contours.pop(next_cnt_index)
        sorted_contours.append(current_contour)
        last_point = current_contour.squeeze(axis=1)[-1]
        
    return sorted_contours

def draw():
    global should_stop
    print("🎨 เริ่มวาด...")
    print(f"⚡ ความเร็ว: {drawing_speed}")
    
    speed_config = SPEED_SETTINGS[drawing_speed]
    
    # โฟกัสเกมเร็วขึ้น
    pydirectinput.click(origin_x, origin_y)
    time.sleep(0.2)  # ลดจาก 0.5
    
    sorted_contours = sort_contours(contours)
    
    if not sorted_contours:
        print("❌ ไม่มีเส้นที่สามารถวาดได้")
        return
    
    print(f"📝 จำนวนเส้นที่จะวาด: {len(sorted_contours)}")

    for i, cnt in enumerate(sorted_contours, 1):
        if should_stop:
            break

        points = cnt.squeeze()

        if len(points.shape) != 2 or len(points) < 2:
            continue

        print(f"🖌️  กำลังวาดเส้นที่ {i}/{len(sorted_contours)}")

        try:
            pydirectinput.mouseUp()
            time.sleep(speed_config["mouse_delay"] * 0.5)  # ลดลงครึ่งหนึ่ง
            
            start_x = origin_x + points[0][0]
            start_y = origin_y + points[0][1]
            pydirectinput.moveTo(start_x, start_y, duration=speed_config["move_duration"])
            time.sleep(speed_config["mouse_delay"] * 0.3)  # ลดลง
            
            pydirectinput.mouseDown()
            time.sleep(speed_config["mouse_delay"] * 0.3)  # ลดลง

            for pt in points[1:]:
                if should_stop:
                    break
                x, y = origin_x + pt[0], origin_y + pt[1]
                pydirectinput.moveTo(x, y, duration=speed_config["draw_duration"])

        except Exception as e:
            print(f"⚠️ เกิดข้อผิดพลาดระหว่างวาดเส้นที่ {i}: {e}")

        finally:
            pydirectinput.mouseUp()
            time.sleep(speed_config["mouse_delay"] * 0.5)  # ลดลง

        time.sleep(speed_config["line_delay"] * 0.8)  # ลดลงเล็กน้อย

    print("✅ วาดเสร็จแล้วหรือหยุดกลางทาง")

# แก้ไขในส่วน __main__
if __name__ == "__main__":
    if not show_preview():
        exit()
    
    # เอาค่า PAUSE ออกหรือตั้งให้ต่ำมาก
    pydirectinput.FAILSAFE = False
    pydirectinput.PAUSE = 0.001  # ลดจาก 0.01 เป็น 0.001
    
    threading.Thread(target=watch_for_end_key, daemon=True).start()
    wait_for_insert_key()
    
    print("⌛ เตรียมโปรแกรมให้พร้อมใน 1 วินาที...")  # ลดเวลาเตรียมตัว
    time.sleep(1)
    
    draw()