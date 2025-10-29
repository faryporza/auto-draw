import cv2
import time
import threading
from pynput import keyboard
import pyautogui
import numpy as np
from collections import deque
import math

# ปรับปรุงประสิทธิภาพ pyautogui
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.0001  # ลดให้ต่ำสุด

# โหลดภาพและประมวลผลอย่างมีประสิทธิภาพ
def load_and_process_image(image_path):
    print("🔄 กำลังโหลดและประมวลผลภาพ...")
    
    # โหลดภาพเป็น grayscale โดยตรง
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"❌ ไม่พบไฟล์ {image_path}")
    
    # ปรับขนาดภาพถ้าใหญ่เกินไป (เพิ่มประสิทธิภาพ)
    h, w = img.shape
    max_dimension = 2000
    if max(h, w) > max_dimension:
        scale = max_dimension / max(h, w)
        new_w, new_h = int(w * scale), int(h * scale)
        img = cv2.resize(img, (new_w, new_h))
        print(f"📐 ปรับขนาดภาพจาก {w}x{h} เป็น {new_w}x{new_h}")
    
    # ประมวลผลขอบแบบเร็ว
    blurred = cv2.GaussianBlur(img, (3, 3), 0)
    edges = cv2.Canny(blurred, 60, 150)
    
    # หา contours แบบเร็ว
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)  # ใช้ algorithm ที่เร็วขึ้น
    
    print(f"🔍 พบ contours จำนวน: {len(contours)}")
    return img, contours

# ตั้งค่าความเร็วที่เร็วขึ้น
SPEED_SETTINGS = {
    "very_slow": {"move_duration": 0.02, "draw_duration": 0.01, "line_delay": 0.1},
    "slow": {"move_duration": 0.01, "draw_duration": 0.005, "line_delay": 0.05},
    "medium": {"move_duration": 0.005, "draw_duration": 0.002, "line_delay": 0.02},
    "fast": {"move_duration": 0.002, "draw_duration": 0.001, "line_delay": 0.01},
    "very_fast": {"move_duration": 0.001, "draw_duration": 0.0005, "line_delay": 0.005},
    "ultra_fast": {"move_duration": 0.0005, "draw_duration": 0.0002, "line_delay": 0.002},  # เพิ่มความเร็วสุด
}

class DrawingOptimizer:
    def __init__(self):
        self.origin_x, self.origin_y = 0, 0
        self.origin_set = False
        self.should_stop = False
        self.drawing_speed = "fast"  # เปลี่ยนเป็น fast เพื่อความแม่นยำ
        
    def show_preview(self, img, contours):
        print("🖼️ กำลังสร้าง preview...")
        
        # สร้าง preview แบบเร็ว
        preview_img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        
        valid_contours = []
        total_points = 0
        
        # กรอง contours ที่มีขนาดพอเหมาะ
        min_contour_length = 15
        for cnt in contours:
            if len(cnt) >= min_contour_length:
                valid_contours.append(cnt)
                total_points += len(cnt)
                cv2.drawContours(preview_img, [cnt], -1, (0, 255, 0), 1)
        
        print(f"✅ วิเคราะห์ภาพเสร็จแล้ว")
        print(f"🖼️ ขนาดภาพ: {img.shape[1]} x {img.shape[0]} pixels")
        print(f"   - Contours ทั้งหมด: {len(contours)}")
        print(f"   - Contours ที่จะวาด: {len(valid_contours)}")
        print(f"   - จำนวนจุดทั้งหมด: {total_points}")
        
        # บันทึก preview
        cv2.imwrite("preview_optimized.png", preview_img)
        print("✅ บันทึก preview เป็นไฟล์: preview_optimized.png")
        
        # เลือกความเร็ว
        print("\n⚡ เลือกความเร็วการวาด (แนะนำ: fast สำหรับความแม่นยำ):")
        speeds = list(SPEED_SETTINGS.keys())
        for i, speed in enumerate(speeds, 1):
            print(f"{i}. {speed} {'✅ แนะนำ' if speed == 'fast' else ''}")
        
        choice = input(f"เลือก (1-{len(speeds)}) หรือ Enter เพื่อใช้ค่าเริ่มต้น: ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(speeds):
            self.drawing_speed = speeds[int(choice) - 1]
        else:
            self.drawing_speed = "fast"
        
        # คำนวณเวลา
        speed_config = SPEED_SETTINGS[self.drawing_speed]
        estimated_time = (total_points * speed_config["draw_duration"] + 
                         len(valid_contours) * speed_config["line_delay"])
        
        print(f"\n✅ เลือกความเร็ว: {self.drawing_speed}")
        print(f"⌛ ประมาณเวลาการวาด: {estimated_time:.1f} วินาที")
        print(f"✏️ โหมด: วาดทุกจุดตามลำดับ (ไม่ข้าม)")
        
        input("\nกด Enter เพื่อเริ่มทำงาน...")
        return valid_contours
    
    def on_press(self, key):
        try:
            if key == keyboard.Key.f6:
                self.origin_x, self.origin_y = pyautogui.position()
                self.origin_set = True
                print(f"✅ Origin ถูกตั้งไว้ที่: ({self.origin_x}, {self.origin_y})")
                
            elif key == keyboard.Key.esc:
                self.should_stop = True
                print("⛔ หยุดการวาดแล้ว")
                
        except Exception as e:
            print(f"⚠️ ข้อผิดพลาดในการรับคีย์: {e}")
    
    def wait_keypress(self):
        print("\n⌨️ กด F6 เพื่อตั้ง origin / กด ESC เพื่อหยุดการวาด")

        def key_listener(key):
            self.on_press(key)

        listener = keyboard.Listener(on_press=key_listener)
        listener.daemon = True
        listener.start()


    
    def optimize_contour_order(self, contours):
        """เรียงลำดับ contours ให้วาดต่อเนื่องกันเพื่อลดการเคลื่อนไหวที่ไม่จำเป็น"""
        if not contours:
            return []
        
        # กรอง contours ที่สั้นเกินไป
        filtered = [cnt for cnt in contours if len(cnt) >= 10]
        if not filtered:
            return []
        
        # เรียงลำดับโดยใช้ KD-tree แบบง่าย (Nearest Neighbor)
        sorted_contours = []
        remaining = filtered.copy()
        
        # เริ่มจาก contour ที่ใกล้ origin มากที่สุด
        current_point = np.array([0, 0])
        
        while remaining and not self.should_stop:
            # หา contour ที่ใกล้ที่สุด
            min_dist = float('inf')
            best_idx = 0
            
            for i, cnt in enumerate(remaining):
                start_point = cnt[0][0]
                dist = np.linalg.norm(start_point - current_point)
                
                if dist < min_dist:
                    min_dist = dist
                    best_idx = i
            
            # เลือก contour นั้น
            next_contour = remaining.pop(best_idx)
            sorted_contours.append(next_contour)
            current_point = next_contour[-1][0]  # จุดสิ้นสุดของ contour
        
        return sorted_contours
    
    def draw_contour_smooth(self, points, speed_config):
        """วาด contour แบบเชื่อมต่อทุกจุด ไม่ข้าม"""
        if len(points) < 2:
            return
        
        # วาดทุกจุดตามลำดับ ไม่ข้าม
        for i, pt in enumerate(points):
            if self.should_stop:
                break
            
            x = self.origin_x + int(pt[0])
            y = self.origin_y + int(pt[1])
            
            # ใช้ duration ที่เร็วมากเพื่อวาดให้ต่อเนื่อง
            pyautogui.moveTo(x, y, duration=speed_config["draw_duration"])
    
    def draw(self, contours):
        """ฟังก์ชันวาดหลักที่ปรับปรุงให้เร็วขึ้น"""
        self.should_stop = False
        optimized_contours = self.optimize_contour_order(contours)
        speed_config = SPEED_SETTINGS[self.drawing_speed]
        
        print(f"\n🎨 เริ่มวาด... (กด ESC เพื่อหยุดได้ตลอดเวลา)")
        print(f"📊 จำนวน contours ที่จะวาด: {len(optimized_contours)}")
        
        start_time = time.time()
        contours_drawn = 0
        points_drawn = 0
        
        for i, cnt in enumerate(optimized_contours):
            if self.should_stop:
                break
            
            points = cnt.squeeze()
            if points.ndim == 1:
                points = points.reshape(1, -1)
            
            # เริ่มวาด contour นี้
            start_x = self.origin_x + int(points[0][0])
            start_y = self.origin_y + int(points[0][1])
            
            # เคลื่อนที่ไปยังจุดเริ่มต้น (ยกปากกาขึ้น)
            pyautogui.mouseUp()
            pyautogui.moveTo(start_x, start_y, duration=speed_config["move_duration"])
            time.sleep(0.001)
            
            # เริ่มวาด (กดปากกาลง)
            pyautogui.mouseDown()
            time.sleep(0.001)
            
            # วาดทุกจุดตามลำดับ ไม่ข้าม
            self.draw_contour_smooth(points[1:], speed_config)
            
            # จบ contour นี้ (ยกปากกาขึ้น)
            pyautogui.mouseUp()
            time.sleep(0.001)
            
            # พักเบาๆ ระหว่าง contours
            if speed_config["line_delay"] > 0:
                time.sleep(speed_config["line_delay"])
            
            contours_drawn += 1
            points_drawn += len(points)
            
            # แสดงความคืบหน้า
            if (i + 1) % 10 == 0:
                progress = (i + 1) / len(optimized_contours) * 100
                print(f"📈 ความคืบหน้า: {progress:.1f}% ({i + 1}/{len(optimized_contours)})")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"\n✅ วาดเสร็จแล้ว!")
        print(f"📊 สถิติ:")
        print(f"   - Contours ที่วาด: {contours_drawn}")
        print(f"   - จุดทั้งหมด: {points_drawn}")
        print(f"   - เวลาที่ใช้: {total_time:.2f} วินาที")
        print(f"   - ความเร็วเฉลี่ย: {points_drawn/total_time:.1f} จุด/วินาที")

# MAIN PROGRAM
def main():
    print("🚀 macOS Drawing Bot (Optimized Version)")
    print("=" * 50)
    
    try:
        # โหลดและประมวลผลภาพ
        img, contours = load_and_process_image("image.png")
        
        # สร้าง optimizer
        optimizer = DrawingOptimizer()
        
        # แสดง preview และรับ contours ที่กรองแล้ว
        valid_contours = optimizer.show_preview(img, contours)
        
        if not valid_contours:
            print("❌ ไม่มี contours ที่สามารถวาดได้")
            return
        
        # รอการกดปุ่มใน thread แยก
        key_thread = threading.Thread(target=optimizer.wait_keypress, daemon=True)
        key_thread.start()
        
        print("\n⌛ รอให้กด F6 เพื่อกำหนดตำแหน่ง origin...")
        while not optimizer.origin_set and not optimizer.should_stop:
            time.sleep(0.01)
        
        if optimizer.should_stop:
            print("❌ ผู้ใช้ยกเลิกการทำงาน")
            return
        
        # รอเตรียมตัวก่อนวาด
        print("⏳ เริ่มวาดใน 2 วินาที...")
        time.sleep(2)
        
        # เริ่มวาด
        optimizer.draw(valid_contours)
        
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()