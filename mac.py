import cv2
import time
import threading
import pyautogui
import numpy as np
from collections import deque
import math

# แก้ปัญหา keyboard listener บน macOS Sequoia
import sys
import select

# ปรับปรุงประสิทธิภาพ pyautogui
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.0001  # ลดให้ต่ำสุด

# โหลดภาพและประมวลผลอย่างมีประสิทธิภาพ
def load_and_process_image(image_path, target_width=None, target_height=None):
    print("🔄 กำลังโหลดและประมวลผลภาพ...")
    
    # โหลดภาพเป็น grayscale โดยตรง
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"❌ ไม่พบไฟล์ {image_path}")
    
    h, w = img.shape
    print(f"📐 ขนาดภาพต้นฉบับ: {w} x {h} pixels")
    
    # ถ้ามีการระบุขนาดเป้าหมาย
    if target_width or target_height:
        if target_width and target_height:
            new_w, new_h = target_width, target_height
        elif target_width:
            scale = target_width / w
            new_w, new_h = target_width, int(h * scale)
        else:  # target_height
            scale = target_height / h
            new_w, new_h = int(w * scale), target_height
        
        img = cv2.resize(img, (new_w, new_h))
        print(f"✅ ปรับขนาดเป็น: {new_w} x {new_h} pixels")
    
    # ประมวลผลขอบแบบเร็ว
    blurred = cv2.GaussianBlur(img, (3, 3), 0)
    edges = cv2.Canny(blurred, 60, 150)
    
    # หา contours แบบเร็ว
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)
    
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
        self.key_pressed = None
        
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
        
        # แสดงข้อมูลหน้าจอ
        screen_width, screen_height = pyautogui.size()
        print(f"🖥️  ขนาดหน้าจอ: {screen_width} x {screen_height} pixels")
        print(f"📊 เปรียบเทียบ: ภาพคือ {(img.shape[1]/screen_width)*100:.1f}% ของความกว้างหน้าจอ")
        
        # สร้าง preview ขนาดเท่าจริงที่จะวาด (overlay บนพื้นหลัง)
        screen_preview = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)
        screen_preview[:, :] = (40, 40, 40)  # พื้นหลังสีเทาเข้ม
        
        # วาง preview ที่มุมซ้ายบน (0, 0)
        h, w = preview_img.shape[:2]
        if h <= screen_height and w <= screen_width:
            screen_preview[0:h, 0:w] = preview_img
            # วาดกรอบสีแดงรอบภาพ
            cv2.rectangle(screen_preview, (0, 0), (w-1, h-1), (0, 0, 255), 2)
            cv2.putText(screen_preview, f"Drawing Area: {w}x{h}px", (10, h+30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # บันทึก preview ทั้งสอง
        cv2.imwrite("preview_drawing.png", preview_img)
        cv2.imwrite("preview_fullscreen.png", screen_preview)
        print("✅ บันทึก preview:")
        print("   - preview_drawing.png (ขนาดภาพที่จะวาด)")
        print("   - preview_fullscreen.png (เทียบกับหน้าจอจริง)")
        
        # แสดง preview บนหน้าจอ
        try:
            cv2.namedWindow('Preview - Full Screen Comparison', cv2.WINDOW_NORMAL)
            cv2.setWindowProperty('Preview - Full Screen Comparison', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            cv2.imshow('Preview - Full Screen Comparison', screen_preview)
            print("\n👁️  กำลังแสดง preview เต็มจอ...")
            print("   - พื้นที่สีเทา = หน้าจอของคุณ")
            print("   - กรอบสี���ดง = พื้นที่ที่จะวาด")
            print("   - กด 'q' เพื่อปิด preview")
            
            while True:
                key = cv2.waitKey(100) & 0xFF
                if key == ord('q') or cv2.getWindowProperty('Preview - Full Screen Comparison', cv2.WND_PROP_VISIBLE) < 1:
                    break
            cv2.destroyAllWindows()
        except:
            print("⚠️ ไม่สามารถแสดง preview บนหน้าจอได้ กรุณาเปิดไฟล์ preview_fullscreen.png")
        
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
    
    def check_keyboard_simple(self):
        """ตรวจสอบคีย์บอร์ดแบบง่าย ๆ โดยไม่ใช้ pynput (แก้ปัญหา macOS Sequoia)"""
        print("\n⌨️ คำแนะนำการใช้งาน:")
        print("   1. กด F6 = ตั้งตำแหน่ง Origin (จุดเริ่มต้นวาด)")
        print("   2. กด ESC หรือ Ctrl+C = หยุดการวาด")
        print("   3. ใช้ Accessibility Keyboard หรือ Better Touch Tool สำหรับ hotkey")
        print("\n💡 เนื่องจาก macOS Sequoia มีข้อจำกัดด้าน Security:")
        print("   - โปรแกรมจะใช้ระบบตรวจจับตำแหน่ง Mouse แทน")
        print("   - ให้เลื่อน Mouse ไปตำแหน่งที่ต้องการ แล้วรอ 2 วินาที = ตั้ง Origin")
        
    def wait_for_origin_by_mouse(self):
        """รอให้ผู้ใช้เลื่อน mouse ไปตำแหน่งที่ต้องการและหยุดไว้ 2 วินาที"""
        print("\n⏱️  เลื่อน Mouse ไปที่ตำแหน่งเริ่มต้น และอย่าขยับ Mouse เป็นเวลา 2 วินาที...")
        print("   (หรือกด Ctrl+C เพื่อยกเลิก)")
        
        last_pos = None
        still_count = 0
        required_still_count = 20  # 2 วินาที (0.1 x 20)
        
        while not self.should_stop:
            try:
                current_pos = pyautogui.position()
                
                if last_pos == current_pos:
                    still_count += 1
                    if still_count >= required_still_count:
                        self.origin_x, self.origin_y = current_pos
                        self.origin_set = True
                        print(f"\n✅ ตั้ง Origin ที่: ({self.origin_x}, {self.origin_y})")
                        return True
                    elif still_count % 5 == 0:
                        print(f"   รอ... {still_count // 5}/{required_still_count // 5}")
                else:
                    still_count = 0
                    last_pos = current_pos
                
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                self.should_stop = True
                print("\n❌ ยกเลิกโดยผู้ใช้")
                return False
        
        return False


    
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
        
        print(f"\n📊 จำนวน contours ที่จะวาด: {len(optimized_contours)}")
        
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
        # ถามขนาดภาพที่ต้องการ
        print("\n📐 ต้องการปรับขนาดภาพไหม?")
        print("1. ใช้ขนาดต้นฉบับ")
        print("2. กำหนดความกว้าง (Width)")
        print("3. กำหนดความสูง (Height)")
        print("4. กำหนดทั้ง Width และ Height")
        
        choice = input("เลือก (1-4): ").strip()
        
        target_w, target_h = None, None
        
        if choice == "2":
            target_w = int(input("ความกว้างที่ต้องการ (pixels): "))
        elif choice == "3":
            target_h = int(input("ความสูงที่ต้องการ (pixels): "))
        elif choice == "4":
            target_w = int(input("ความกว้างที่ต้องการ (pixels): "))
            target_h = int(input("ความสูงที่ต้องการ (pixels): "))
        
        # โหลดและประมวลผลภาพ
        img, contours = load_and_process_image("image.png", target_w, target_h)
        
        # สร้าง optimizer
        optimizer = DrawingOptimizer()
        
        # แสดง preview และรับ contours ที่กรองแล้ว
        valid_contours = optimizer.show_preview(img, contours)
        
        if not valid_contours:
            print("❌ ไม่มี contours ที่สามารถวาดได้")
            return
        
        # แสดงคำแนะนำและรอตั้ง origin ด้วย mouse
        optimizer.check_keyboard_simple()
        
        if not optimizer.wait_for_origin_by_mouse():
            print("❌ ไม่ได้ตั้ง origin - ยกเลิกการทำงาน")
            return
        
        if optimizer.should_stop:
            print("❌ ผู้ใช้ยกเลิกการทำงาน")
            return
        
        # รอเตรียมตัวก่อนวาด
        print("\n⏳ เริ่มวาดใน 3 วินาที... (กด Ctrl+C เพื่อยกเลิก)")
        try:
            for i in range(3, 0, -1):
                if optimizer.should_stop:
                    print("❌ ผู้ใช้ยกเลิกการทำงาน")
                    return
                print(f"   {i}...")
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n❌ ยกเลิกโดยผู้ใช้")
            return
        
        # เริ่มวาด
        print("\n🎨 เริ่มวาด! (กด Ctrl+C เพื่อหยุดฉุกเฉิน)")
        try:
            optimizer.draw(valid_contours)
        except KeyboardInterrupt:
            print("\n⛔ หยุดการวาดโดยผู้ใช้")
        
        print("\n✅ โปรแกรมเสร็จสิ้น")
        
    except KeyboardInterrupt:
        print("\n❌ ผู้ใช้กด Ctrl+C - ยกเลิกการทำงาน")
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()