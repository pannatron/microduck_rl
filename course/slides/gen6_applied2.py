# ================================================================ ภาคประยุกต์ ต่อ: A.7 ไม่มี GPS · A.8 QA · บทเรียนพื้น (exec ใน gen6.py)
O = X["odom"]; Q3, Q1 = O["sq3"], O["sq1"]

put("exA7", slide("exA7", head("Exercise A.7 · No GPS", "เดินสี่เหลี่ยมกลับจุดเดิม โดยนับก้าวเอา", "A.7"),
    row=[f'<div style="flex:1;display:flex;flex-direction:column;gap:24px">' + task(["เป็ด 32 ตัวเริ่มจุดเดียวกัน เดินสี่เหลี่ยม 1.5 ม. 3 รอบ (18 ม.)",
               "เลี้ยวตาม “ตำแหน่งที่คิดว่าอยู่” — ตำแหน่งจริงใช้แค่ให้คะแนน",
               "เทียบ: คำสั่งอย่างเดียว · + gyro (bias ±0.3°/s) · + วัดความเร็ว · + หา bias ตอนยืนนิ่ง",
               "ความคลาดแบบไหนแก้ได้ แบบไหนแก้ไม่ได้?"])
         + code(f'{G} …/newton_odom.py --calib{SP}{C("# k = เดินจริง/คำสั่ง")}<br>{G} …/newton_odom.py --est cmd,gyro,gyro_cal,gyro_still --per 32 --loops 3', 24) + '</div>',
         f'<div style="width:700px;display:flex;flex-direction:column;gap:16px">'
         + vid("ostill_cmd", "ovid_cmd", "32 ducks steering by commanded motion only end together at the wrong spot", 700, 340)
         + vid("ostill_gyro", "ovid_gyro", "32 ducks steering by gyro spread along a line near the start", 700, 340) + '</div>'],
    at=1), "วิดีโอบน: คำสั่งอย่างเดียว — ทั้ง 32 ตัวไปจบที่จุดผิดเดียวกัน · ล่าง: + gyro — แต่ละตัวจบคนละที่เพราะ bias ของ gyro แต่ละตัวต่างกัน · เส้นเหลือง = เส้นทางที่ตั้งใจ วงเขียว = จุดเริ่ม/จุดจบ")

put("ansA7", answer("ansA7", "A.7", "ความคลาด 2 แบบ: แบบหนึ่งแก้ได้ อีกแบบต้องมีตา",
    [f"<b>คำสั่งอย่างเดียว</b>: จบห่างจุดเริ่ม {Q1['cmd']['home_err_med']:.2f} ม. หลังเดิน 6 ม. และ {Q3['cmd']['home_err_med']:.2f} ม. หลัง 18 ม. — ทุกตัวผิด<b>ไปทางเดียวกัน</b> (แบบเป็นระบบ วัดแล้วแก้ได้)",
     f"<b>+ gyro</b>: เหลือ {Q1['gyro']['home_err_med']:.2f} และ {Q3['gyro']['home_err_med']:.2f} ม. แต่<b>กระจาย</b>ตาม bias ของแต่ละตัว (แย่สุด {Q3['gyro']['home_err_max']:.2f} ม.)",
     f"หา bias ตอนยืนนิ่ง 1 s <b>กลับแย่ลง</b> ({O['still1']['groups']['gyro_still']['home_err_med']:.2f} ม.) — เป็ดยังโยกตัวอยู่ ({O['still1']['true_gyro_while_still_deg_s']:.2f}°/s มากกว่า bias เอง) · ยืน 3 s ดีขึ้นเป็น {O['still3']['groups']['gyro_still']['home_err_med']:.2f} ม.",
     f"gyro สมบูรณ์ไม่มี bias ยังคลาด {O['perfect']['gyro']['home_err_med']:.2f} ม. — เป็ดเคลื่อนที่ตอน “หมุนอยู่กับที่” และไถลข้าง ซึ่งการนับก้าวมองไม่เห็น",
     f"วัดความเร็วจริงไม่ช่วย: k = {O['k']} (Newton เดินตรงคำสั่งเกือบเป๊ะ)"],
    side=f'<img src="{I("odom_scatter")}" alt="Scatter of where ducks actually ended: commands-only cluster far off, gyro spread along a line, perfect gyro near start" style="width:780px;height:607px;object-fit:contain;border-radius:16px">',
    summary="ประตูห้องกว้าง 80 ซม. — คลาด 0.4 ม. ก็ชนวงกบแล้ว: ส่งของจริงต้องมีตาช่วย (ToF จาก A.6, กล้อง, ป้าย)", side_w=780),
    "error ทั้งหมดเป็นมัธยฐานของ 32 ตัว วัดเป็นระยะจากจุดจบจริงถึงจุดเริ่ม (ที่เป็ด “คิดว่า” กลับมาถึง) · bias gyro สุ่มต่อตัว ±0.3°/s + noise 0.02 rad/s ต่อ sample")

# ---------------------------------------------------------------- A.8 QA
QA = X["qa"]; QC = QA["cells"]
def qa(p, t): c = QC[f"{p}|{t}"]; return c["pass_"], c["n"], c["fell"]
put("exA8", slide("exA8", head("Exercise A.8 · QA before release", "ทดสอบ 1,008 ตัว ก่อนปล่อย policy", "A.8"),
    code(f'{G} …/newton_qa.py --reps 21 --ice-mu 0.15 --weak 0.7{SP}{C("# 6 policy × 8 การทดสอบ × 21 ตัว · 7.6 s")}', 25),
    row=[task(["8 การทดสอบ: ปกติ · พื้นกล่อง · ผลัก 0.5 / 1.0 m/s · พื้นลื่น μ 0.15 · มอเตอร์ ×0.7 · แบก 200 g · IMU noise",
               "ผ่าน = ไม่ล้ม และเดินได้ ≥ 1.5 ม. ใน 20 s",
               "ตั้งค่าแยกต่อ world ก่อนสร้าง solver (μ, แรงบิด, มวล, ตำแหน่งพื้น)",
               "ตัดสิน: policy ไหนพร้อมลงหุ่นจริง?"]),
         f'<div style="width:900px;display:flex;flex-direction:column">' + vid("qstill", "qvid", "Grid of 1,008 Microducks under different QA conditions in Newton; some fall", 900, 506) + '</div>'],
    at=2), "μ 0.3 และมอเตอร์ ×0.85 ไม่ทำให้ใครล้มเลย จึงใช้ค่าที่หนักขึ้น · ตรวจแล้วว่าการตั้งค่าต่อ world มีผลจริง: μ 0.02 และ ×0.2 ทำให้ล้มทุกตัว")

nw, rf, vs = "newton_walk_2000", "rough_ft", "velstand"
QU = lambda p, t: QC[f"{p}|{t}"]["up_end"]
put("ansA8", answer("ansA8", "A.8", "ไม่มี policy ไหนผ่านครบ — ตารางนี้คือรายงานก่อนปล่อย",
    [f"<b>rough_ft</b> ผ่านมากสุด (21/21 ทุกข้อ ยกเว้นผลัก) · <b>climb35</b> ใกล้เคียง · <b>walk_2000</b> พลาดที่พื้นลื่น ({qa('walk_2000', 'ice')[0]}/21)",
     f"<b>newton_walk</b> แบก 200 g ล้ม {qa(nw, 'heavy')[2]}/21 · <b>newton_latency</b> ผลัก 0.5 ล้ม {qa('newton_latency_2000', 'push05')[2]}/21 — ตัวที่เทรนบน Newton ทนแรงรบกวนน้อยกว่า",
     f"ผลัก 1.0 m/s ล้มเกือบทุกตัว แต่ <b>velstand ลุกกลับมายืนได้ทุกตัว</b> ({QU(vs, 'push10')}/21) ตัวอื่นแทบไม่ลุก · บน MuJoCo CPU velstand ก็ล้มแล้วลุก 6/6",
     f"velstand ไม่ล้มแต่ <b>ช้ากว่าเกณฑ์</b> บนพื้นกล่องและตอนแบกของ ({qa(vs, 'box')[0]}/21, {qa(vs, 'heavy')[0]}/21)"],
    side=f'<img src="{I("qa_matrix")}" alt="Pass-rate heatmap of six policies across eight QA tests" style="width:1000px;height:467px;object-fit:contain;border-radius:16px">',
    summary="QA ที่ดีแยก “ล้ม” “ช้า” และ “ล้มแล้วลุกได้” ออกจากกัน — ผ่าน/ไม่ผ่านอย่างเดียวซ่อนความต่างไว้", side_w=1000),
    "1,008 world · 20 s ต่อตัว · 7.6 s บน RTX 3060 Laptop · D-gain ตามที่เทรนต่อ world · ผลักแบบตั้งความเร็วแนวนอนของลำตัวทับ ที่ 5, 10, 15 s ทิศสุ่ม · รุ่นแรกของหน้านี้ (damping ซ้อน) เคยพบว่าทุกตัวล้มที่ผลัก 0.5 และคิดว่า Newton ต่างจาก MuJoCo — ต้นเหตุจริงคือ damping ซ้อน + เกณฑ์ “ล้ม” ที่ไม่เท่ากัน")

FL = X["floor"]
def fc(d, k): c = d[k]; return f"{c['pass_']}/{c['n']}" + (f" · ล้ม {c['fell']}" if c["fell"] else "") + (f" · {c['dist_med']} ม." if c.get("dist_med") else "")
put("floor", slide("floor", head("บทเรียนจาก QA", "พื้น plane กับพื้นกล่อง: เรียบเท่ากัน แต่ผลไม่เท่ากัน"),
    row=[f'<div style="flex:1;display:flex;flex-direction:column;gap:20px">'
         + table([["newton_walk · แบก 200 g", fc(FL["plane"], "newton_walk_2000|heavy"), fc(FL["box"], "newton_walk_2000|heavy")],
                  ["velstand · ปกติ", fc(FL["plane"], "velstand|nominal"), fc(FL["box"], "velstand|nominal")],
                  ["velstand · แบก 200 g", fc(FL["plane"], "velstand|heavy"), fc(FL["box"], "velstand|heavy")],
                  ["rough_ft · แบก 200 g", fc(FL["plane"], "rough_ft|heavy"), fc(FL["box"], "rough_ft|heavy")],
                  ["walk_2000 · ปกติ", fc(FL["plane"], "walk_2000|nominal"), fc(FL["box"], "walk_2000|nominal")]],
                 ["16 ตัวต่อช่อง", "พื้น plane", "พื้นกล่อง"], size=28)
         + p("ผ่าน · ล้ม · ระยะมัธยฐานใน 20 s (ผ่าน = ไม่ล้ม + ≥ 1.5 ม.)", 24, "#4A5563") + '</div>',
         f'<div style="width:620px;display:flex;flex-direction:column;gap:18px">'
         + card("สมมติฐาน", p("เท้าเป็ดเป็น mesh — ชน plane ด้วยสูตร mesh-plane แต่ชนกล่องด้วย CCD (Newton โหลด kernel CCD เฉพาะตอนมีกล่อง) · Rough ของ mjlab เป็นกล่องทั้งหมด Flat ใช้ plane", 25))
         + card("แก้ตัว", p("รุ่นแรกบอกว่า walk_2000 ล้มบนกล่องทุกตัว — นั่นมาจาก damping ซ้อน หลังแก้ walk_2000 ผ่านทั้งสองพื้น · ความต่างที่เหลือคือความเร็ว และ newton_walk ตอนแบกของ", 25, "#8A4300")) + '</div>'],
    at=1), "A.5–A.6 วัดบนพื้นกล่อง (อพาร์ตเมนต์) และบันได/หินใน Duck Adventure เป็นกล่อง — ผลจริงสำหรับพื้นแบบนั้น · MuJoCo CPU ให้ 1 จุดสัมผัสต่อเท้าทั้งบน plane และกล่อง (ตอนยืน)")
