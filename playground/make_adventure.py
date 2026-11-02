"""Duck Adventure — ด่านตะลุย 5 โซน + checkpoint (เขียน MJCF + ไฟล์กติกา .json คู่กัน)

usage: python playground/make_adventure.py <ชื่อ> [H=0.02] [soft]
  H = ความสูงบันไดต่อขั้นในโซนภูเขา (ม.) — 0.01 ง่าย · 0.02 ปกติ · 0.03 บอส
ได้ src/mjlab_microduck/robot/microduck/scene_<ชื่อ>.xml และ .json (checkpoint, ลาวา, waypoint ของ autopilot)

  START → ① สลาลอมกรวย → CP1 → ② สะพานข้ามลาวา → CP2 → ③ ภูเขาบันได 3 ขั้น (CP3 บนยอด) → ทางลาดลง
        → ④ ทุ่งหินขรุขระ → CP4 → ⑤ ประตูสวิงคู่ (ต้องดันเปิด) → FINISH
"""
import sys, math, re, json, random
name = sys.argv[1]
H = next((float(a[2:]) for a in sys.argv[2:] if a.startswith("H=")), 0.02)
SOFT = "soft" in sys.argv[2:]
base = open("src/mjlab_microduck/robot/microduck/scene.xml").read()
SOFTATTR = ' solref="0.04 1" solimp="0.85 0.95 0.001 0.5 2"' if SOFT else ""


def box(n, x, y, z, sx, sy, sz, rgba, euler=None, solid=True):
    e = f' euler="{euler}"' if euler else ""
    c = f'{SOFTATTR} friction="1.0 0.005 0.0001"' if solid else ' contype="0" conaffinity="0"'
    return f'<geom name="{n}" type="box" pos="{x:.4f} {y:.4f} {z:.4f}" size="{sx:.4f} {sy:.4f} {sz:.4f}" rgba="{rgba}"{e}{c}/>\n'


def marker(n, x, y, z, rgba, r=0.07):          # วงแหวน checkpoint (มองเห็นได้ ไม่ชน)
    return f'<geom name="{n}" type="cylinder" pos="{x} {y} {z + 0.0015}" size="{r} 0.0015" rgba="{rgba}" contype="0" conaffinity="0"/>\n'


g = ""
# ① สลาลอม: กรวย 3 อัน สลับซ้ายขวา — ชนกรวย = +2 วินาที
CONES = [(0.7, 0.10), (1.2, -0.10), (1.7, 0.10)]
for i, (x, y) in enumerate(CONES):
    g += f'<geom name="cone{i}" type="cylinder" pos="{x} {y} 0.06" size="0.025 0.06" rgba="1 0.45 0.1 1"/>\n'

# ② สะพานข้ามลาวา: ลาวาเป็นแค่สีบนพื้น (กติกาเกม) — ตัวเป็ดออกนอกสะพาน = ตกลาวา กลับไป CP ล่าสุด
LAVA = [2.4, 3.6, -0.5, 0.5]
BRIDGE = [(2.4, 0.0), (2.9, 0.0), (3.2, 0.15), (3.6, 0.15)]
BRIDGE_HALF = 0.09
g += box("lava", (LAVA[0] + LAVA[1]) / 2, 0, 0.0005, (LAVA[1] - LAVA[0]) / 2, LAVA[3], 0.0005, "0.95 0.25 0.05 1", solid=False)
for i, ((x0, y0), (x1, y1)) in enumerate(zip(BRIDGE, BRIDGE[1:])):
    L = math.hypot(x1 - x0, y1 - y0); a = math.degrees(math.atan2(y1 - y0, x1 - x0))
    g += box(f"bridge{i}", (x0 + x1) / 2, (y0 + y1) / 2, 0.0011 + 0.0003 * i, L / 2 + BRIDGE_HALF, BRIDGE_HALF, 0.0006, "0.55 0.38 0.2 1", euler=f"0 0 {math.radians(a):.4f}", solid=False)

# ③ ภูเขา: บันได 3 ขั้น (ลึกขั้นละ 25 ซม.) → ยอด 40 ซม. → ทางลาดลง 5° (ใกล้ความชันที่เทรนมา)
X0, TREAD, TOP = 4.0, 0.25, 0.4
XTOP_END = X0 + 2 * TREAD + TOP
for k in range(3):
    xs = X0 + TREAD * k; h = H * (k + 1)
    g += box(f"stair{k}", (xs + XTOP_END) / 2, 0, h / 2, (XTOP_END - xs) / 2, 0.5, h / 2, ["0.95 0.75 0.4 1", "0.9 0.6 0.25 1", "0.8 0.45 0.1 1"][k])
deg = 5.0; a = math.radians(deg); L = 3 * H / math.tan(a); t = 0.01
mx, mz = XTOP_END + L / 2, 1.5 * H
g += box("ramp", mx - t * math.sin(a), 0, mz - t * math.cos(a), L / (2 * math.cos(a)) + 0.01, 0.5, t, "0.8 0.45 0.1 1", euler=f"0 {a:.4f} 0")   # robot xml ตั้ง compiler angle="radian" → euler/range ต้องเป็นเรเดียน
XR_END = XTOP_END + L

# ④ ทุ่งหิน: แผ่น 10×10 ซม. สูงสุ่ม 0–8 มม.
random.seed(7); XC0 = XR_END + 0.1
for i in range(8):
    for j in range(6):
        hh = random.uniform(0.001, 0.008)
        g += box(f"rock{i}_{j}", XC0 + 0.1 * i + 0.05, -0.3 + 0.1 * j + 0.05, hh / 2, 0.05, 0.05, hh / 2, "0.5 0.6 0.7 1")
XC_END = XC0 + 0.8

# ⑤ ประตูสวิงคู่: บานพับที่กำแพงสองข้าง สปริงดึงปิด — ต้องเดินดันให้เปิด (กำแพงกันเดินอ้อม)
XG = XC_END + 0.5
for s in (-1, 1):                               # กำแพงยาวเลยปลายประตูตอนเปิด (ไม่งั้นเท้าไปติดปลายบาน)
    g += box(f"wall{'LR'[s > 0]}", XG + 0.1, s * 0.25, 0.04, 0.4, 0.01, 0.04, "0.4 0.4 0.45 1")
for s, side in ((-1, "R"), (1, "L")):         # ประตูสวิงคู่ (แบบบาร์คาวบอย) บานละ 22 ซม. — เปิดแล้วแนบกำแพงพอดี
    g += (f'<body name="gate{side}" pos="{XG} {s * 0.245} 0.0">\n'
          f'  <joint name="gate_hinge{side}" type="hinge" axis="0 0 1" range="{"-1.5 0" if s < 0 else "0 1.5"}" stiffness="0.004" damping="0.002" armature="0.0005"/>\n'
          f'  <geom name="gate_door{side}" type="box" pos="0 {-s * 0.115} 0.045" size="0.004 0.11 0.035" mass="0.006" rgba="0.3 0.7 0.95 1"/>\n'
          f'</body>\n')
XF = XG + 0.7

CPS = [dict(name="START", x=0.0, y=0.0, z=0.0), dict(name="CP1", x=2.2, y=0.0, z=0.0), dict(name="CP2", x=3.85, y=0.0, z=0.0),
       dict(name="CP3", x=round(X0 + 2 * TREAD + TOP / 2, 3), y=0.0, z=3 * H), dict(name="CP4", x=round(XC_END + 0.1, 3), y=0.0, z=0.0),
       dict(name="FINISH", x=round(XF, 3), y=0.0, z=0.0)]
for c in CPS[1:]:
    g += marker(c["name"], c["x"], c["y"], c["z"], "0.2 0.85 0.3 0.9" if c["name"] != "FINISH" else "1 0.85 0.1 1", 0.08 if c["name"] == "FINISH" else 0.07)
g += f'<geom name="flag_pole" type="cylinder" pos="{XF} 0.3 0.12" size="0.006 0.12" rgba="0.9 0.9 0.9 1" contype="0" conaffinity="0"/>\n'
g += f'<geom name="flag" type="box" pos="{XF + 0.05} 0.3 0.21" size="0.05 0.002 0.03" rgba="1 0.85 0.1 1" contype="0" conaffinity="0"/>\n'

WAYPOINTS = [(0.4, 0.0), (0.7, -0.13), (1.2, 0.13), (1.7, -0.13), (2.2, 0.0), (2.45, 0.0), (2.9, 0.0), (3.2, 0.15), (3.6, 0.15), (3.85, 0.0),
             (CPS[3]["x"], 0.0), (XR_END, 0.0), (XC_END + 0.1, 0.0), (XG + 0.3, 0.0), (XF, 0.0)]
SLOW = [[0.55, 1.95], [2.35, 3.7], [X0 - 0.15, X0 + 2 * TREAD + 0.1]]          # ช่วงที่ autopilot เดินช้าลง

out = base.replace("</worldbody>", g + "</worldbody>", 1)
out = re.sub(r'qpos="([^"]*)"', lambda mm: f'qpos="{mm.group(1).rstrip()} 0 0"', out)   # keyframe ต้องมีค่าของบานพับประตู 2 บานด้วย
path = f"src/mjlab_microduck/robot/microduck/scene_{name}.xml"
open(path, "w").write(out)
json.dump(dict(H=H, cps=CPS, lava=LAVA, bridge=BRIDGE, bridge_half=BRIDGE_HALF, cones=CONES, waypoints=WAYPOINTS, slow=SLOW,
               stairs=[X0, XTOP_END], ramp_end=XR_END, gate_x=XG), open(path[:-4] + ".json", "w"), indent=1)
print(path, f"H={H*1000:.0f}mm ยาว {XF:.1f} ม.")
