"""สร้างด่านเป็น MJCF: python playground/make_course.py <ชื่อ> step=0.01 | slope=5 | course  [soft]
ไฟล์จะถูกเขียนไว้ที่ src/mjlab_microduck/robot/microduck/scene_<ชื่อ>.xml (ต้องอยู่ข้าง robot xml เพราะ include/meshdir เป็น path สัมพัทธ์)"""
import sys, math, re
name, kind = sys.argv[1], sys.argv[2]
SOFT = "soft" in sys.argv[3:]            # ใส่ soft = ขอบนิ่มเหมือนพื้นตอนเทรน rough
base = open("src/mjlab_microduck/robot/microduck/scene.xml").read()

def box(n, x, y, z, sx, sy, sz, rgba="0.85 0.55 0.2 1", euler=None):
    e = f' euler="{euler}"' if euler else ""
    if SOFT: e += ' solref="0.04 1" solimp="0.85 0.95 0.001 0.5 2"'   # แบบเดียวกับ _soften_terrain_contacts ตอนเทรน
    return f'<geom name="{n}" type="box" pos="{x} {y} {z}" size="{sx} {sy} {sz}" rgba="{rgba}"{e} friction="1.0 0.005 0.0001"/>\n'

g = ""
if kind.startswith("step="):                      # ขั้นเดียว สูง h เริ่มที่ x=0.35
    h = float(kind.split("=")[1]); g += box("step", 1.35, 0, h / 2, 1.0, 1.0, h / 2)
elif kind.startswith("slope="):                   # ทางลาดขึ้น deg องศา ยาว 1 ม.
    deg = float(kind.split("=")[1]); a = math.radians(deg); L = 1.0
    g += box("ramp", 0.35 + L / 2 * math.cos(a), 0, L / 2 * math.sin(a) - 0.01 * math.cos(a), L / 2, 1.0, 0.01, euler=f"0 {-a:.4f} 0")   # compiler angle="radian" ใน robot xml
elif kind == "course":                            # ด่านรวม: ขั้นบันได → พื้นขรุขระ → ทางลาด → เป้าหมาย
    for k, h in enumerate([0.005, 0.010, 0.015]):  # บันได 3 ขั้น ขั้นละ 0.3 ม.
        g += box(f"stair{k}", 0.5 + 0.3 * k + 0.15 + (0.6 - 0.3 * k) / 2 - 0.15, 0, h / 2, 0.15 + (0.6 - 0.3 * k) / 2, 0.5, h / 2, ["0.95 0.75 0.4 1", "0.9 0.6 0.25 1", "0.8 0.45 0.1 1"][k])
    import random; random.seed(0)
    for i in range(6):                            # แผ่นขรุขระ 6×4 แผ่น สูงสุ่ม 0–8 มม. ต่อจากชั้นบน (z=15 มม.)
        for j in range(4):
            hh = 0.015 + random.uniform(0, 0.008)
            g += box(f"rough{i}_{j}", 1.1 + 0.12 * i + 0.06, -0.24 + 0.12 * j + 0.06, hh / 2, 0.06, 0.06, hh / 2, "0.5 0.6 0.7 1")
    g += box("land", 1.82 + 0.5, 0, 0.0075, 0.5, 0.5, 0.0075, "0.85 0.55 0.2 1")
    g += '<geom name="goal" type="cylinder" pos="2.6 0 0.016" size="0.08 0.001" rgba="0.2 0.8 0.3 1" contype="0" conaffinity="0"/>\n'
else:
    sys.exit("unknown kind")
out = base.replace("</worldbody>", g + "</worldbody>", 1)
path = f"src/mjlab_microduck/robot/microduck/scene_{name}.xml"
open(path, "w").write(out); print(path)
