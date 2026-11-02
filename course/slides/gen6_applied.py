# ================================================================ ภาคประยุกต์ (exec ภายใน gen6.py — ใช้ตัวแปรของ gen6)
X = json.load(open(os.path.join(HERE, "results6x.json")))
PROBE = [[0.73, 0.73, 0.70, 0.69, 0.71, 0.71, 0.72, 0.77], [0.71, 0.68, 0.68, 0.69, 0.68, 0.69, 0.71, 0.72], [0.70, 0.68, 0.66, 0.66, 0.67, 0.68, 0.69, 0.72],
         [0.70, 0.69, 0.69, 0.67, 0.67, 0.68, 0.69, 0.73], [0.70, 0.68, 0.67, 0.65, 0.67, 0.68, 0.70, 0.73], [0.71, 0.70, 0.68, 0.67, 0.69, 0.69, 0.71, 0.74],
         [0.71, 0.70, 0.70, 0.70, 0.69, 0.70, 0.72, 0.74], [0.67, 0.64, 0.63, 0.62, 0.62, 0.62, 0.63, 0.63]]   # newton_tof.py --probe
S3, S6 = X["sprint_0.3"], X["sprint_0.6"]
put("sec-app", section("sec-app", "Applied · ภาคประยุกต์", "จากเกม<br>สู่งานจริง", "แก้ด่านที่ไม่มีใครผ่าน · ส่งพัสดุในอพาร์ตเมนต์ · เดินด้วยตาของเป็ดเอง (ToF) — ทั้งหมดบน Newton", I("apt_top"), "Pollen apartment rendered in Newton, top view"))

# ---------------------------------------------------------------- A.4 sprint
put("exA4", slide("exA4", head("Exercise A.4 · Fix it", "ข้ามบันได 20 mm ให้ได้ โดยไม่เทรนใหม่", "A.4"),
    code(f'{G} …/newton_adventure.py --level adv20 --per 16 --policies velstand --vstairs 0.6{SP}{C("# หรือ rough_ft+velstand@mountain")}', 25),
    row=[task(["ลองสลับ policy ตามโซน หรือเปลี่ยนความเร็วเฉพาะบันได",
               "ช้าลง (0.1, 0.2) หรือเร็วขึ้น (0.45–0.9)? เดาก่อน",
               "16 เลนต่อค่า × 4 รอบ — รอบเดียวหลอกได้",
               "เทรนมาแค่ ±0.4 m/s — สั่ง 0.6 ได้ไหม?"]),
         f'<div style="width:900px;display:flex;flex-direction:column">' + vid("nstill_sprint", "nvid_sprint", "Eight velstand ducks sprinting at the 20 mm stairs in Newton", 900, 506) + '</div>'],
    at=2), "วิดีโอ: velstand 8 เลน สั่ง 0.6 m/s เฉพาะช่วงบันได ด่าน 20 mm — รอบนี้เข้าเส้น 6/8")

spd = [["0.3 (เดิม)", f"{S3['fin']}/{S3['n']} เข้าเส้น"], ["0.45", f"{X['sprint_0.45']['fin']}/16"], ["0.6", f'<b style="color:#1F4D06">{S6["fin"]}/{S6["n"]}</b> เข้าเส้น'],
       ["0.75", f"{X['sprint_0.75']['fin']}/16"], ["0.9", f"{X['sprint_0.9']['fin']}/16"]]
put("ansA4", answer("ansA4", "A.4", "วิ่งใส่บันได ไม่ใช่ค่อย ๆ ก้าว",
    [f"<b>0.6 m/s เฉพาะช่วงบันได</b>: เข้าเส้นด่าน 20 mm {S6['fin']}/{S6['n']} เลน ({S6['fin']*100//S6['n']}%) จาก {S3['fin']}/{S3['n']} ({S3['fin']*100//S3['n']}%) ที่ความเร็วเดิม · ล้มน้อยลงด้วย (มัธยฐาน {S3['falls_med']} → {S6['falls_med']})",
     f"เร็วขึ้นอีกยังดี: 0.75 → {X['sprint_0.75']['fin']}/16 · 0.9 → {X['sprint_0.9']['fin']}/16 — ทั้งที่ velstand เทรนคำสั่งเดินหน้าแค่ ±0.4 m/s",
     f"ด่าน 10 mm: ความเร็วเดิมหยุดหน้าบันไดทุกเลน (0/16) · วิ่งใส่ 0.6 → <b>{X['adv10_0.6']['fin']}/16</b> เข้าเส้น มัธยฐาน {X['adv10_0.6']['t_med']:.0f} s",
     f"ผลต่อรอบ 16 เลนที่ 0.6: {', '.join(map(str, S6['per_run']))} · ที่ 0.3: {', '.join(map(str, S3['per_run']))} — รอบเดียวพอบอกทิศทาง แต่ตัวเลขต้องใช้หลายรอบ",
     "<b>แก้ตัว:</b> รุ่นแรกได้ 22/64 vs 6/64 — วัดตอน damping ซ้อน (หน้าบั๊ก) ข้อสรุป “วิ่งใส่ดีกว่า” ยังอยู่ แต่ตัวเลขเปลี่ยนมาก"],
    side=table(spd, ["vstairs (m/s)", "velstand ด่าน 20 mm"], size=28) + p("0.3 และ 0.6 = 64 เลน (4 รอบ × 16) · ค่าอื่น 16 เลน · 240 s ต่อเลน", 24, "#4A5563"),
    summary="ก่อนเทรนใหม่ ลองแก้ที่ “วิธีใช้” ก่อน — ความเร็วตอนเข้าบันไดเปลี่ยนผลจาก 39% เป็น 81% โดยไม่แตะ policy", side_w=720),
    "สมมติฐาน: velstand ต้องมีแรงส่งพอให้เท้าข้ามขอบ ที่ 0.3 m/s มันเข้าโหมดยืน/ก้าวสั้นแล้วหยุดหน้าขั้น · สลับ policy ตามโซน (rough_ft + velstand บนภูเขา) วัดแค่ 4 เลนตอนยังมีบั๊ก damping จึงไม่ได้ใส่ไว้")

# ---------------------------------------------------------------- A.5 delivery
R = X["routes"]
put("deliv", slide("deliv", head("newton_port/newton_delivery.py · apartment.xml ของ Pollen", "ส่งพัสดุในอพาร์ตเมนต์ 6 ห้อง"),
    row=[f'<div style="width:960px;display:flex;flex-direction:column">' + vid("apt_top_still", "dvid_top", "Top view of the apartment in Newton with a duck carrying a parcel from kitchen to office", 960, 540) + '</div>',
         f'<div style="flex:1;display:flex;flex-direction:column;gap:22px">'
         + table([["ครัว → ห้องนอน", f"{R['kitchen_bedroom']} ม."], ["ครัว → ห้องทำงาน", f"{R['kitchen_office']} ม."], ["นั่งเล่น → ห้องน้ำ", f"{R['living_bath']} ม."]], ["เส้นทาง", "ระยะ"], size=28)
         + card("วัดอะไร", p("พัสดุบนหลัง 0–400 g (เป็ดหนัก 0.74 kg) · ล้ม = ส่งไม่สำเร็จ ไม่มีเกิดใหม่", 27)
                + p("เวลา และงานกลต่อเมตร Σ|τ·q̇| — ตัวบอกว่าแบตหมดเร็วแค่ไหน", 27)
                + p("เดินตาม waypoint ที่ผ่านกลางประตู — ยังรู้ตำแหน่งตัวเองอยู่ (A.6 จะเอาออก)", 27, "#8A4300")) + '</div>'],
    at=1), "ฉาก apartment.xml ของ Pollen (ใช้ทดสอบ SLAM/MCL ของเป็ดจริง) ถูกอ่านเป็นกล่อง/ทรงกระบอกใน Newton — สีพื้นแต่ละห้องเอาจากสี texture เพราะ Newton ไม่อ่าน texture ของ MuJoCo")

put("exA5", slide("exA5", head("Exercise A.5 · Delivery", "พัสดุหนักแค่ไหนถึงยังส่งได้ — ใช้ policy ไหนดี?", "A.5"),
    row=[f'<div style="flex:1;display:flex;flex-direction:column;gap:24px">' + task(["3 เส้นทาง × 3 policy × 5 น้ำหนัก × 4 เลน",
               "ตารางส่งสำเร็จ / 12 และเวลามัธยฐาน",
               "หา “น้ำหนักสูงสุด” ของแต่ละ policy",
               "เขียนกฎเลือก policy ตามน้ำหนักพัสดุ"])
         + code(f'{G} …/newton_delivery.py --mission kitchen_office \\<br>{SP}--policies rough_ft,velstand,newton_walk_2000 \\<br>{SP}--payloads 0,100,200,300,400 --per 4<br>{C("# 60 เลนพร้อมกัน · 27 s")}', 24) + '</div>',
         f'<div style="width:700px;display:flex;flex-direction:column;gap:16px">'
         + vid("dstill_rough300", "dvid_rough300", "rough_ft delivering a 300 g parcel", 700, 340) + vid("dstill_nw300", "dvid_nw300", "newton_walk falling with a 300 g parcel", 700, 340) + '</div>'],
    at=1), "วิดีโอบน: rough_ft แบก 300 g ส่งถึงห้องทำงาน · ล่าง: newton_walk แบก 300 g ล้มที่ทางเดิน (พัสดุตก)")

D_ = X["delivery"]
def dcell(pol, g):
    r = D_[f"{pol}@{g}"]
    s = f"{r['ok']}/12" + (f" · {r['t_med']:.0f} s" if r["t_med"] else "")
    return f'<b style="color:#1F4D06">{s}</b>' if r["ok"] == 12 else s
put("ansA5", answer("ansA5", "A.5", "ไม่มี policy เดียวที่ดีที่สุด — เลือกตามน้ำหนัก",
    [f"<b>≤ 200 g → newton_walk</b>: ส่งครบ 12/12 เร็วสุด ({D_['newton_walk_2000@0']['t_med']:.0f}–{D_['newton_walk_2000@200']['t_med']:.0f} s) แต่ 300 g ส่งได้แค่ {D_['newton_walk_2000@300']['ok']}/12",
     f"<b>300–400 g → rough_ft</b>: ส่งครบ 12/12 ทุกน้ำหนัก ({D_['rough_ft@0']['t_med']:.0f}–{D_['rough_ft@400']['t_med']:.0f} s) ช้ากว่า newton_walk ราว 2 เท่า",
     f"velstand ส่งครบถึง 300 g แต่ช้าสุด ({D_['velstand@200']['t_med']:.0f}–{D_['velstand@300']['t_med']:.0f} s) และ 400 g ไม่ถึงเลย",
     f"งานกลต่อเมตรใกล้กัน: newton_walk ~{D_['newton_walk_2000@200']['J_m']:.0f} · rough_ft ~{D_['rough_ft@200']['J_m']:.0f} · velstand ~{D_['velstand@200']['J_m']:.0f} J/m",
     "<b>ระวัง</b>: พื้นอพาร์ตเมนต์เป็นกล่อง — บนพื้น plane newton_walk แบก 200 g ล้ม 9/16 (A.8) · กฎนี้ใช้กับพื้นแบบนี้"],
    side=table([[f"{g} g", dcell("newton_walk_2000", g), dcell("rough_ft", g), dcell("velstand", g)] for g in (0, 100, 200, 300, 400)],
               ["พัสดุ", "newton_walk", "rough_ft", "velstand"], size=26) + p("ส่งสำเร็จ / 12 (3 เส้นทาง × 4 เลน) · เวลามัธยฐานของเลนที่ส่งถึง", 24, "#4A5563"),
    summary="ระบบจริงเลือก policy ตามงาน: พัสดุเบาใช้ตัวเร็ว พัสดุหนักใช้ตัวที่ทน — ตารางนี้คือ spec ของเป็ด", side_w=900),
    "งานกล = Σ|τ·q̇|·dt จาก PD ที่สั่งจริง ไม่ใช่พลังงานไฟฟ้า · รุ่นแรกของหน้านี้ (damping ซ้อน) เคยพบว่า rough_ft/velstand ไม่แบกของกลับล้มบ่อยกว่า — หายไปหลังแก้ damping จึงตัดออก")

# ---------------------------------------------------------------- A.6 ToF
put("tof", slide("tof", head("newton.sensors.SensorTiledCamera · sim/tof.py ของ Pollen", "ToF ของเป็ดจริง บน Newton"),
    row=[f'<div style="flex:1;display:flex;flex-direction:column;gap:22px">'
         + table([["รุ่น", "VL53L5CX (ติดบนหัวเป็ดจริง)"], ["ภาพ", "8 × 8 โซน · มุม 45° · ไกลสุด 4 ม."], ["ความถี่", "15 Hz (เราใช้ 16.7 Hz)"],
                  ["noise", "σ = 3 mm + 2 cm × d / 4 m"], ["ตำแหน่ง", "site <code>tof</code> ใน MJCF (บน jaw_soft)"]], ["ToF", "ค่า"], size=27)
         + card("บน Newton ทำยังไง", p("กล้อง pinhole 8×8 ของ <b>SensorTiledCamera</b> วางที่ site ToF แล้วอ่านช่อง <b>depth</b> — เรนเดอร์ทุก world ในครั้งเดียวบน GPU", 27)
                + p("ไม่เจออะไรใน 4 ม. = “ไม่มีเป้า” เหมือนสถานะ 255 ของตัวจริง", 27, "#4A5563")) + '</div>',
         f'<div style="width:760px;display:flex;flex-direction:column;gap:16px">'
         + p("ตรวจก่อนใช้: ยืนหันหน้าเข้ากำแพง ห่าง 0.67 ม.", 28, "#1B2430", ";font-weight:600")
         + table([[f"{v:.2f}" for v in row] for row in PROBE], [f"c{j}" for j in range(8)], size=24)
         + p("กลางภาพ 0.65–0.69 ม. ✓ · มุมไกลขึ้น ✓ · แถวล่างเริ่มเห็นพื้น 0.62 ม. (ยิงก้ม 20°) ✓", 25, "#3D7A12") + '</div>'],
    at=1), "ค่าในตารางคือภาพ ToF จริงจาก newton_tof.py --probe: เป็ดยืนที่ x = −3.2 หันไปทางกำแพงตะวันตก (ผิวกำแพง x = −3.94) หัวสูง 0.225 ม.")

put("exA6", slide("exA6", head("Exercise A.6 · See with ToF", "ลาดตระเวนทั้งบ้าน โดยไม่รู้ตำแหน่งตัวเอง", "A.6"),
    code(f'{G} .venv/bin/python …/newton_tof.py --ctl blind,tof,tof_cliff --per 8 --spawn corridor{SP}{C("# 24 เลน 180 s · 42 s")}', 25),
    row=[task(["ตัวคุมเห็นแค่ ToF 8×8 — ไม่มี waypoint ไม่มีตำแหน่ง",
               "<b>blind</b>: เดินตรง เลี้ยวสุ่ม · <b>tof</b>: ข้างหน้าใกล้กว่า 35 ซม. → หมุนไปฝั่งที่โล่ง",
               "ทางเดินมี <b>ช่องบันไดลง</b> 40×70 ซม. — tof มองเห็นไหม?",
               "เขียน <b>tof_cliff</b>: แถวล่างควรเห็นพื้นที่ ~0.66 ม. ถ้าไกลกว่านั้นคือหลุม"]),
         f'<div style="width:900px;display:flex;flex-direction:column">' + vid("tstill_tof", "tvid_tof", "Duck with obstacle-only ToF walking into the stairwell hole, ToF image inset", 900, 506) + '</div>'],
    at=2), "วิดีโอ: ตัวคุม tof (ดูแค่สิ่งกีดขวาง) เดินตกช่องบันไดที่ 30 s — มุมขวาบนคือภาพ ToF 8×8 ที่เป็ดเห็น สีดำ = ไม่มีเป้าใน 4 ม.")

TT = X["tof"]
tofrows = [[n, f"{TT['living_' + c]['fell']}/8", f"{TT['corridor_' + c]['fell']}/8", f"{TT['living_' + c]['hole'] + TT['corridor_' + c]['hole']}", f"{(TT['living_' + c]['dist'] + TT['corridor_' + c]['dist']) / 2:.0f} ม."]
           for c, n in (("blind", "blind"), ("tof", "tof"), ("tof_cliff", "tof_cliff"))]
put("ansA6", answer("ansA6", "A.6", "เซนเซอร์ที่ดีต้องคู่กับคำถามที่ถูก",
    [f"<b>blind</b> ล้มเกือบทุกเลน ({TT['living_blind']['fell'] + TT['corridor_blind']['fell']}/16) — เดินชนกำแพงแล้วล้ม เดินได้แค่ ~{(TT['living_blind']['dist'] + TT['corridor_blind']['dist']) / 2:.0f} ม.",
     f"<b>tof</b> เดินได้ไกลขึ้น 4 เท่า แต่<b>ตกช่องบันได {TT['living_tof']['hole'] + TT['corridor_tof']['hole']} ครั้ง</b> — หลุมไม่ใช่ “สิ่งกีดขวางข้างหน้า” จึงไม่เคยถูกถาม",
     f"<b>tof_cliff</b> เริ่มจากทางเดินหันเข้าหลุม: ล้ม {TT['corridor_tof_cliff']['fell']}/8 (จาก {TT['corridor_tof']['fell']}/8) และไปถึงเฉลี่ย {TT['corridor_tof_cliff']['rooms']} ห้อง",
     f"ยังตกหลุมจากด้านข้าง {TT['living_tof_cliff']['hole']}/8 เมื่อเริ่มที่ห้องนั่งเล่น — ตรวจแค่คอลัมน์กลาง 4 ช่อง เดินเฉียงเข้าขอบจึงไม่เห็น"],
    side=vid("tstill_cliff", "tvid_cliff", "Duck with cliff check turning away from the stairwell, ToF inset", 700, 394)
         + table(tofrows, ["ตัวคุม", "ล้ม·นั่งเล่น", "ล้ม·ทางเดิน", "ตกหลุม", "ระยะเฉลี่ย"], size=24),
    summary="ToF ตัวเดิม ถามเพิ่มข้อเดียว (“พื้นยังอยู่ไหม?”) ล้มลดจาก 7/8 เหลือ 1/8", side_w=760),
    "ตำแหน่งจริงใช้แค่ให้คะแนน (ห้องที่ไปถึง, ตกหลุม) ตัวคุมไม่เห็น · ‘ติด’ = สั่งเดินแต่ขยับไม่ถึง 2 ซม. ใน 0.5 s — ยังสูงทุกตัวคุม (5–11 ครั้ง) — ยังไม่ได้ตรวจว่าติดอะไร")
