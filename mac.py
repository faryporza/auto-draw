import cv2
import time
import threading
from pynput import keyboard  # ✅ ใช้บน macOS
import pyautogui
import numpy as np

# ปิดความปลอดภัย (failsafe) เพื่อให้เมาส์ไม่หยุดฉุกเฉิน
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.001

# โหลดภาพและหาเส้นขอบ
img = cv2.imread("image.png", 0)
if img is None:
    print("❌ ไม่พบไฟล์ image.png หรือไฟล์เสียหาย")
    exit()

edges = cv2.Canny(img, 50, 150)
contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

print(f"🔍 พบ contours จำนวน: {len(contours)}")

# ตัวแปรควบคุม
origin_x, origin_y = 0, 0
origin_set = False
should_stop = False
drawing_speed = "medium"

# ความเร็วสำหรับการวาด
SPEED_SETTINGS = {
    "very_slow": {"move_duration": 0.05, "draw_duration": 0.03, "line_delay": 0.5},
    "slow": {"move_duration": 0.03, "draw_duration": 0.02, "line_delay": 0.3},
    "medium": {"move_duration": 0.02, "draw_duration": 0.01, "line_delay": 0.12},
    "fast": {"move_duration": 0.01, "draw_duration": 0.005, "line_delay": 0.05},
    "very_fast": {"move_duration": 0.005, "draw_duration": 0.001, "line_delay": 0.01},
}

def show_preview():
    global drawing_speed

    print("🖼️  กำลังสร้าง preview...")
    preview_img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    valid_contours = 0
    total_points = 0

    for cnt in contours:
        arc_length = cv2.arcLength(cnt, False)
        color = (0, 255, 0) if arc_length >= 20 else (0, 0, 255)
        cv2.drawContours(preview_img, [cnt], -1, color, 1)

        if arc_length >= 20:
            valid_contours += 1
            total_points += len(cnt)

    print(f"✅ วิเคราะห์ภาพเสร็จแล้ว")
    print(f"🖼️ ขนาดภาพ: {img.shape[1]} x {img.shape[0]} pixels")
    print(f"   - Contours ทั้งหมด: {len(contours)}")
    print(f"   - Contours ที่จะวาด: {valid_contours}")
    print(f"   - จำนวนจุดทั้งหมด: {total_points}")

    cv2.imwrite("preview.png", preview_img)
    print("✅ บันทึก preview เป็นไฟล์: preview.png")

    print("\n⚡ เลือกความเร็วการวาด:")
    print("1. Very Slow")
    print("2. Slow")
    print("3. Medium ✅ (Default)")
    print("4. Fast")
    print("5. Very Fast")

    choice = input("เลือก (1-5) หรือ Enter เพื่อใช้ค่าเริ่มต้น: ")

    drawing_speed = {
        "1": "very_slow",
        "2": "slow",
        "3": "medium",
        "4": "fast",
        "5": "very_fast"
    }.get(choice, "medium")

    speed_config = SPEED_SETTINGS[drawing_speed]
    estimated_time = total_points * speed_config["draw_duration"] + valid_contours * speed_config["line_delay"]

    print(f"\n✅ เลือกความเร็ว: {drawing_speed}")
    print(f"⌛ ประมาณเวลาการวาด: {estimated_time:.1f} วินาที")

    input("\nกด Enter เพื่อเริ่มทำงาน...")
    return True


def on_press(key):
    global origin_x, origin_y, origin_set, should_stop

    try:
        if key == keyboard.Key.f6:
            origin_x, origin_y = pyautogui.position()
            origin_set = True
            print(f"✅ Origin ถูกตั้งไว้ที่: ({origin_x}, {origin_y})")

        elif key == keyboard.Key.esc:
            should_stop = True
            print("⛔ หยุดการวาดแล้ว")

    except:
        pass

def wait_keypress():
    print("\n⌨️  กด F6 เพื่อตั้งตำแหน่งเริ่มต้น และ ESC เพื่อหยุดวาด")
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


def sort_contours(contours):
    filtered = [cnt for cnt in contours if cv2.arcLength(cnt, False) >= 20]
    if not filtered:
        return []

    sorted_list = []
    last_point = np.array([0, 0])
    remaining = filtered[:]

    while remaining:
        next_index = min(range(len(remaining)), key=lambda i: np.linalg.norm(remaining[i][0][0] - last_point))
        next_cnt = remaining.pop(next_index)
        sorted_list.append(next_cnt)
        last_point = next_cnt[-1][0]

    return sorted_list


def draw():
    global should_stop
    sorted_contours = sort_contours(contours)
    speed = SPEED_SETTINGS[drawing_speed]

    print("\n🎨 เริ่มวาด... (กด ESC เพื่อหยุดได้ตลอดเวลา)")
    for i, cnt in enumerate(sorted_contours):
        if should_stop:
            break

        points = cnt.squeeze()

        start_x = origin_x + points[0][0]
        start_y = origin_y + points[0][1]
        pyautogui.moveTo(start_x, start_y, duration=speed["move_duration"])
        pyautogui.mouseDown()

        for pt in points[1:]:
            if should_stop:
                break
            pyautogui.moveTo(origin_x + pt[0], origin_y + pt[1], duration=speed["draw_duration"])

        pyautogui.mouseUp()
        time.sleep(speed["line_delay"])

    print("\n✅ วาดเสร็จแล้ว")


# MAIN PROGRAM (macOS)
if __name__ == "__main__":
    print("🍎 macOS Mode Loaded")

    if not show_preview():
        exit()

    threading.Thread(target=wait_keypress, daemon=True).start()
    print("\n⌛ รอให้กด F6 เพื่อกำหนดตำแหน่ง origin...")

    while not origin_set:
        time.sleep(0.1)

    time.sleep(1)  # เวลารอเตรียมหน้าจอ
    draw()
