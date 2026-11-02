"""Microduck deck 5 — Duck Adventure บน Newton (ด่านตะลุย). Usage: gen6.py <deck_root> [ids...]"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from common4 import *  # noqa: F401,F403
from common4 import slides, order

HERE = os.path.dirname(__file__)
BL = json.load(open(os.path.join(HERE, "blobs6.json")))
N = json.load(open(os.path.join(HERE, "results6n.json")))     # Newton (หลักของเด็คนี้)
M = json.load(open(os.path.join(HERE, "results6.json")))      # MuJoCo CPU + BAM (ตรวจไขว้)
I = lambda k: B(BL[k])
POLS = [("walk_2000", "walk_2000", "Flat · mjlab"), ("rough_ft", "rough_ft", "Rough 1.5 cm · mjlab"), ("velstand", "velstand", "ทางการ Pollen"),
        ("climb35", "climb35", "Rough 3.5 cm · ของเรา"), ("newton_walk_2000", "newton_walk", "Flat · เทรนบน Newton")]
MKEY = {"walk_2000": "walk", "rough_ft": "rough", "velstand": "velstand", "climb35": "climb"}
LVS = [("adv10", "10 mm"), ("adv20", "20 mm"), ("adv30", "30 mm")]
CPN = ["START", "CP1", "CP2", "CP3", "CP4", "FINISH"]


def vid(still, clip, alt, w, h):
    return f'<img src="{I(still)}" data-video="{I(clip)}" alt="{alt}" style="width:{w}px;height:{h}px;object-fit:cover;border-radius:20px">'


def ncell(pol, lv):
    r = N[f"{pol}_{lv}"]
    if r["finished"]:
        t = r["times"]; rng = f"{t[0]:.0f}" if len(t) == 1 else f"{t[0]:.0f}–{t[-1]:.0f}"
        return f'<b style="color:#1F4D06">เข้าเส้น {r["finished"]}/{r["n"]}</b> · {rng} s'
    return f'{CPN[r["best_cp"]]} · ล้ม {r["falls"][0]}–{r["falls"][-1]}'


def mcell(pol, lv):
    r = M.get(f"{MKEY.get(pol, '')}_{lv}")
    if r is None: return "—"
    if r["finish"]: return f'<b style="color:#1F4D06">เข้าเส้น {r["finish"]:.0f} s</b> · ล้ม {r["falls"]}'
    return f'ถึง {r["reached"]} · ล้ม {r["falls"]}'


meta = N["meta"]
NEWTON_BADGE = '<p style="font-size:24px;background:#7AC943;color:#0E1621;padding:10px 22px;border-radius:40px;font-weight:600">Newton 1.17 · SolverMuJoCo (MuJoCo-Warp) · ViewerGL</p>'

# ================================================================ cover
put("cover", f'''<section id="cover" data-transition="fade" style="{NAVY};padding:128px;display:flex;flex-direction:row;gap:64px;align-items:center">
<div style="width:800px;display:flex;flex-direction:column;gap:28px">
<p style="font-size:24px;letter-spacing:3px;text-transform:uppercase;color:#7AC943">Workshop · ภาคพิเศษ Module 4</p>
<h1 style="{H};font-size:124px;font-weight:600;line-height:1.02;color:#F4F3EE">Duck Adventure</h1>
<p style="font-size:38px;color:#B8C4D0;line-height:1.4">ด่านตะลุย 5 โซน · 10 เป็ดแข่งพร้อมกันบน GPU · ใครปีนภูเขาได้สูงสุด</p>
<div style="display:flex;flex-direction:row">{NEWTON_BADGE}</div>
</div>
<img src="{I('nover')}" alt="Ten Microducks lined up on ten copies of the adventure course in Newton" style="flex:1;height:820px;object-fit:cover;border-radius:24px">
</section>''', "ภาคนี้รันบน Newton ทั้งฟิสิกส์และภาพ: แต่ละเลนคือ world แยกกันบน GPU ด่านเดียวกัน เป็ดคนละ policy · ฝั่ง MuJoCo CPU + BAM ใช้ตรวจไขว้และให้คนบังคับเองด้วยคีย์บอร์ด")

# ================================================================ map of zones
zones = [("①", "สลาลอมกรวย", "เลี้ยวซ้ายขวาสลับ 3 กรวย", "ทดสอบ: คำสั่งเลี้ยว"),
         ("②", "สะพานข้ามลาวา", "กว้าง 18 ซม. หักมุมกลางสะพาน · ออกนอกสะพาน = เกิดใหม่", "ทดสอบ: เดินตรงแม่น"),
         ("③", "ภูเขาบันได", "3 ขั้น สูงขั้นละ H (10 / 20 / 30 mm) · ลงทางลาด 5°", "ทดสอบ: ยกเท้า"),
         ("④", "ทุ่งหิน", "แผ่น 10 ซม. สูงสุ่ม 1–8 mm", "ทดสอบ: พื้นไม่เรียบ"),
         ("⑤", "ประตูสวิงคู่", "บานพับจริงในฟิสิกส์ มีสปริงดึงปิด ต้องเดินดันเปิด", "ทดสอบ: ถูกผลัก")]
zc = "".join(f'<div style="flex:1;background:#FBFAF6;border:1px solid #DDDBD2;border-radius:24px;padding:28px 26px;display:flex;flex-direction:column;gap:12px">'
             f'<p style="{H};font-size:52px;font-weight:600;color:#B85C00;line-height:1">{n}</p>'
             f'<h3 style="{H};font-size:36px;font-weight:600;color:#0E1621">{t}</h3>{p(d, 26)}<div style="flex:1"></div>{p(k, 26, "#3D7A12", ";font-weight:600")}</div>'
             for n, t, d, k in zones)
put("zones", slide("zones", head("make_adventure.py → newton_adventure.py", "5 โซน แต่ละโซนทดสอบคนละทักษะ"),
    f'<img src="{I("nzone")}" alt="One adventure course rendered in Newton: cones, lava bridge, stair mountain, rocks, swing doors, flag" style="width:1696px;height:330px;object-fit:cover;border-radius:20px">',
    f'<div style="flex:1;display:flex;flex-direction:row;gap:18px">{zc}</div>', at=2),
    "make_adventure.py เขียนด่านเป็น MJCF + ไฟล์กติกา .json · newton_adventure.py อ่าน geom ทุกชิ้นจาก MJCF (68 ชิ้นคงที่ + ประตู 2 บานพร้อมบานพับ) แล้วสร้างใหม่ใน Newton ModelBuilder · checkpoint = วงเขียว เส้นชัย = วงเหลือง")

# ================================================================ Newton: many lanes
put("newton", slide("newton", head("newton_port/newton_adventure.py", f"{meta['N']} เลนบน GPU เดียว — ทุกเลนคือ world แยกกัน"),
    code(f'{G} .venv/bin/python …/newton_adventure.py --level adv10 --per 2 \\<br>'
         f'{SP}--policies walk_2000,rough_ft,velstand,climb35,newton_walk_2000 \\<br>'
         f'{SP}--video frames/ --cam overview{SP}{C("# รันจาก ~/IsaacLab · กล้องตามเป็ด: --cam follow:4")}', 26),
    row=[f'<div style="width:960px;display:flex;flex-direction:column">' + vid("nstill_race", "nvid_race", "Ten ducks racing the 10 mm course side by side in Newton", 960, 540) + '</div>',
         f'<div style="flex:1;display:flex;flex-direction:column;gap:24px">'
         + bigrow(big(f"{meta['N']}", "เป็ด · 5 policy × 2"), big("56 s", "เวลาจริงของซิม 180 s ทั้ง 10 เลน"))
         + card("ทำงานยังไง", p("ด่าน 1 ชุดต่อ world · <b>scene.replicate()</b> ก๊อปเป็ด + ด่านไป 10 world", 27)
                + p("กติกาเกม + autopilot เป็น tensor บน GPU — เช็ก checkpoint, ล้ม, ลาวา ทุกเลนพร้อมกัน", 27)
                + p("มอเตอร์เป็น PD (kd 0.053 ตามสัปดาห์ 6) ไม่ใช่ BAM", 27, "#8A4300")) + '</div>'],
    at=2), "56 s คือรันไม่อัดวิดีโอ (อัดวิดีโอ 1280×720 ทุก 0.1 s ใช้ 148 s) · ต้องปิด world offsets ของ ViewerGL (set_world_offsets((0,0,0))) ไม่งั้น viewer เลื่อนเลนไปวางเป็นตารางเอง ภาพไม่ตรงตำแหน่งในฟิสิกส์")

# ================================================================ how to play
rules = [["ข้ามเส้นวงเขียวตามลำดับ", "บันทึก checkpoint (กว้าง ±30 ซม.)"], ["เอียงเกิน ~55° นาน 0.5 s", "ล้ม → เกิดใหม่ที่ checkpoint ล่าสุด"],
         ["ตัวออกนอกสะพาน", "ตกลาวา → เกิดใหม่"], ["เกิน 180 s", "หมดเวลา"]]
put("play", slide("play", head("autopilot · เล่นเองด้วยคีย์บอร์ด", "ใครบังคับเป็ด?"),
    row=[f'<div style="flex:1;display:flex;flex-direction:column;gap:24px">' + table(rules, ["กติกา", "ผล"], size=28)
         + card("autopilot (ทั้งสองซิม)", p("เล็งหัวไปที่ waypoint ถัดไป สั่ง vx 0.4 (โซนยาก 0.3) กับ ωz ตามมุมที่คลาด", 28)
                + p("ωz ขั้นต่ำ 0.5 rad/s — คำสั่งเลี้ยวเล็ก ๆ policy ไม่ตอบสนองเลย (โซนตาย แบบแอปเตะบอล)", 28)
                + p("ทุกเลนได้ autopilot เดียวกัน → เทียบ policy ได้ยุติธรรม", 28, "#3D7A12")) + '</div>',
         f'<div style="flex:1;display:flex;flex-direction:column;gap:24px">'
         + card("เล่นเอง (MuJoCo viewer)", p("Newton ViewerGL ยังไม่มีช่องรับคีย์บอร์ดในสคริปต์เรา — โหมดคนเล่นจึงใช้ infer_policy เดิม", 28)
                + code(f'{G} ADV=…/adv20.json AUTO=0 python playground/sim_play.py \\<br>{SP}<b>--live</b> --ctl playground/ctl_adventure.py -- \\<br>{SP}--walking exports/velstand.onnx --new-cmd-obs \\<br>{SP}--scene …/scene_adv20.xml', 24)
                + p("กดลูกศร ↑↓←→ ในเทอร์มินัล · ซิมนี้ใช้มอเตอร์ BAM", 28, "#4A5563")) + '</div>'],
    at=1), "--live เปิด viewer จริงและอ่านปุ่มจากเทอร์มินัล กติกาเกมทำงานทุก step; ทดสอบแล้วว่าเปิดได้และ autopilot เดินถึง CP1 ในหน้าต่างจริง")

# ================================================================ Ex A.1 race
put("exA1", slide("exA1", head("Exercise A.1 · Race", "ด่าน 10 mm: policy ไหนเข้าเส้นชัยได้?", "A.1"),
    code(f'{G} .venv/bin/python …/newton_adventure.py --level adv10 --policies walk_2000,rough_ft,velstand,climb35,newton_walk_2000 \\<br>{SP}--per 2 --secs 180 --out adv10.json{SP}{C("# รัน 2 รอบ = 4 เลนต่อ policy")}', 25),
    row=[task(["รัน 5 policy × 2 เลน บนด่าน 10 mm สองรอบ",
               "จด: เข้าเส้นกี่เลน เวลา จำนวนล้ม checkpoint ไกลสุด",
               "ดู end_x ของเลนที่ไม่ถึง แล้วบอกว่าติดโซนไหน",
               "ทำนายก่อนรัน: policy ที่เทรนบน Newton จะได้เปรียบไหม?"]),
         f'<div style="width:900px;display:flex;flex-direction:column">' + vid("nstill_follow", "nvid_follow", "Follow camera on walk_2000 finishing the 10 mm course in Newton", 900, 506) + '</div>'],
    at=2), "วิดีโอ: เลน walk_2000 บนด่าน 10 mm กล้องตาม เร่ง 4 เท่า — เข้าเส้นใน 130 s · แถบบนแสดงเวลาในซิม checkpoint และจำนวนล้มของเลนนี้")

nv, nr, nw, nc, nn = (N[f"{k}_adv10"] for k in ("velstand", "rough_ft", "walk_2000", "climb35", "newton_walk_2000"))
put("ansA1", answer("ansA1", "A.1", "เข้าเส้น 3 policy — แต่ไม่มีตัวไหนครบทุกเลน",
    [f"<b>walk_2000 · rough_ft · climb35</b> เข้าเส้นตัวละ 2/4 เลน — walk_2000 เร็วสุด ({nw['times'][0]:.0f}–{nw['times'][-1]:.0f} s) · เลนที่ไม่ถึงติดที่ทุ่งหินหรือประตู (CP4)",
     f"<b>velstand</b> หยุดนิ่งหน้าขั้นแรกทุกเลน (x = {nv['end_x'][0]:.2f} ม.) ไม่ล้มเลย — เหมือนบน MuJoCo · คำสั่ง 0.3 m/s ไม่พอให้มันขึ้นบันได (ดู A.4)",
     f"<b>newton_walk</b> (เทรนบน Newton) ถึง CP4 แต่ล้ม {nn['falls'][0]}–{nn['falls'][-1]} ครั้ง — เทรนบนซิมเดียวกันไม่ช่วย ถ้าไม่เคยเจอพื้นขรุขระหรือแรงผลัก",
     "<b>แก้ตัว:</b> หน้านี้รุ่นแรกบอกว่า velstand ชนะคนเดียว — วัดตอนที่ damping ซ้อนสองชั้น (ดูหน้าบั๊ก) ตั้งให้ตรงกับตอนเทรนแล้วผลเปลี่ยน"],
    side=table([[n, ncell(k, "adv10")] for k, n, _ in POLS], ["policy", "Newton · 10 mm (4 เลน)"], size=30)
         + p("ช่วงเวลา = เลนที่เร็วสุด–ช้าสุด · CPx = checkpoint ไกลสุด · ‘ล้ม a–b’ = น้อยสุด–มากสุด", 24, "#4A5563"),
    summary="ผลต่างกันทุกเลน ต้องรายงานเป็นช่วง — และตั้งค่าซิมให้ตรงกับตอนเทรนก่อนสรุปอะไร", side_w=820),
    "ทุกเลนใช้ autopilot เดียวกัน ต่างกันที่ท่าเริ่มสุ่ม ±0.03 rad และความไม่แน่นอนของ GPU solver · D-gain: policy จาก mjlab = 0, จาก Newton = 0.053 (Newton นำเข้า damping 0.053 จาก MJCF อยู่แล้ว)")

# ================================================================ MuJoCo vs Newton
put("gap", slide("gap", head("sim-to-sim อีกรอบ", "ตั้งค่าให้ตรงกับตอนเทรน สองซิมก็ตรงกันขึ้น"),
    table([[n, mcell(k, "adv10"), ncell(k, "adv10")] for k, n, _ in POLS[:4]],
          ["policy (ด่าน 10 mm)", "MuJoCo CPU + BAM (1 รอบ)", "Newton + PD (4 เลน)"], size=29),
    f'<div style="flex:1;display:flex;flex-direction:row;gap:28px">'
    + card("ตรงกันแล้ว", p("velstand หยุดหน้าบันไดทั้งสองซิม ไม่ล้ม · rough_ft และ climb35 เข้าเส้นได้ทั้งสองซิม", 28))
    + card("ยังต่าง", p("walk_2000: MuJoCo ล้มที่ประตู 43 ครั้ง · Newton เข้าเส้น 2/4 — ประตู/กรวยและมอเตอร์ (BAM vs PD) ยังจำลองคนละแบบ", 28))
    + card("บทเรียน", p("รุ่นแรกของหน้านี้ผลกลับข้างทั้งหมด — ต้นเหตุคือ damping ซ้อนในซิมฝั่งเรา ไม่ใช่ตัวซิม", 28, "#8A4300")) + '</div>',
    at=1), "MuJoCo CPU ใช้ infer_policy.py (BAM m6) · Newton ใช้ SolverMuJoCo + PD kp 0.55, damping MJCF 0.053 + D-gain ตามที่เทรน · ด่านจาก MJCF ไฟล์เดียวกันและ autopilot ตรรกะเดียวกัน")

# ================================================================ Ex A.2 mountain
put("exA2", slide("exA2", head("Exercise A.2 · How high?", "ภูเขา 10 → 20 → 30 mm: ใครยังปีนได้?", "A.2"),
    code(f'{G} for h in 0.01 0.02 0.03; do python playground/make_adventure.py adv$h H=$h soft; done{SP}{C("# 3 ด่าน")}', 26),
    row=[task(["รัน 5 policy × 3 ความสูงบน Newton",
               "ใส่ผลในตาราง: เข้าเส้น / checkpoint ไกลสุด / จำนวนล้ม",
               "เป็ดยกเท้าได้ประมาณ 1–2 ซม. — ขั้น 30 mm ควรเป็นไปได้ไหม?",
               "ล้มตรงไหนบนภูเขา: ขาขึ้นหรือขาลง?"]),
         f'<div style="width:900px;display:flex;flex-direction:column">' + vid("nstill_climb", "nvid_climb", "climb35 trying the 20 mm stairs in Newton and falling", 900, 506) + '</div>'],
    at=2), "วิดีโอ: climb35 บนด่าน 20 mm กล้องตาม เร่ง 3 เท่า — ล้มที่ขั้นแรกซ้ำแล้วซ้ำอีก")

put("ansA2", answer("ansA2", "A.2", "ขั้น 20 mm ไม่มีใครผ่านบน Newton",
    ["ที่ 20 และ 30 mm ทุก policy ติดที่ CP2 (ตีนภูเขา) ทุกเลน — ล้มตั้งแต่ขั้นแรก x ≈ 3.9–4.1 ม. เป็นขาขึ้นล้วน",
     f"velstand ล้มน้อยสุด ({N['velstand_adv20']['falls'][0]}–{N['velstand_adv20']['falls'][-1]} ครั้งที่ 20 mm) newton_walk ล้มมากสุด ({N['newton_walk_2000_adv20']['falls'][0]}+) — ล้มน้อยไม่ได้แปลว่าผ่าน",
     f"บน MuJoCo + BAM มีแค่ velstand ที่ข้าม 20 mm ได้ ({M['velstand_adv20']['finish']:.0f} s) · บน Newton velstand ข้ามได้เมื่อ “วิ่งใส่” บันได (A.4)",
     "ขั้น 20 mm ≈ 2 เท่าของที่เป็ดยกเท้าตอนเดิน (~1 ซม. ดู Ex A.3) → จูนคำสั่งอย่างเดียวไม่พอ"],
    side=table([[n] + [ncell(k, lv) for lv, _ in LVS] for k, n, _ in POLS], ["Newton", "10 mm", "20 mm", "30 mm"], size=27)
         + p("10 mm = 4 เลน · 20/30 mm = 2 เลน · ทุกเลน 180 s", 24, "#4A5563"),
    summary="ความสูงขั้นคือเพดานจริงของ policy เดิน — เส้นชัยวัดได้ชัดกว่าค่า reward", side_w=1000))

# ================================================================ bugs while building the game
bugs = [["ทางลาดกลายเป็นหน้าผา", "robot xml ตั้ง <code>angle=\"radian\"</code> — euler 5 = 5 เรเดียน", "ยิง ray วัดพื้นทุก 3 ซม."],
        ["ผ่านยอดเขาแล้วไม่นับ CP3", "วงรัศมี 12 ซม. เป็ดเดินเฉพลาดวง", "นับเป็น “ข้ามเส้น” ±30 ซม."],
        ["เป็ดหมุนอยู่กับที่", "waypoint อยู่ข้างตัว เดินไม่ถึง", "นับผ่านเมื่อเลยแนว x"],
        ["ติดหลังประตูทั้งที่ไม่ล้ม", "บานยาวกว่ากำแพง ปลายบานเกี่ยวขา", "ประตูคู่ บานสั้น"],
        ["Newton: ประตูสร้างไม่ได้", "add_body() แถม free joint ซ้อนกับบานพับ", "ใช้ add_link()"],
        ["Newton: กล้องหาเป็ดไม่เจอ", "ViewerGL เลื่อน world ไปวางเป็นตารางเอง", "set_world_offsets((0,0,0))"],
        ["พัสดุ 300 g เวลาเท่าเดิมเป๊ะ", "MJCF ล็อก inertia — shape ใหม่ไม่เพิ่มมวล", "ใส่มวล/CoM/inertia ให้ trunk เอง"],
        ["ส่งของไม่ถึงทั้งที่ไม่ล้ม", "เส้นทางเฉียดโต๊ะ console 2 ซม.", "ย้ายเส้นทางไปกลางทางเดิน"],
        ["<b>ผลกลับข้างไปมาระหว่างซิม</b>", "Newton นำเข้า damping 0.053 จาก MJCF แล้วเราใส่ D-gain ซ้ำอีก 0.053", "D-gain ตามที่เทรน: mjlab 0 · Newton 0.053"],
        ["<b>ToF ไม่เคยเห็นหลุม</b>", "SensorTiledCamera คืน depth 0 เมื่อรังสีไม่ชนอะไร — โค้ดอ่านเป็น “กำแพงที่ 0 ม.”", "depth ≤ 0 → inf · ตรวจด้วย --probe หน้าหลุม"]]
put("bugs", slide("bugs", head("ระหว่างสร้างเกม", "ด่านพังก่อนเป็ดพัง — 10 บั๊กที่เจอจริง"),
    table(bugs, ["อาการ", "สาเหตุ", "แก้"], size=22),
    think("ทุกบั๊กดูเหมือน “policy แย่” ในตอนแรก — ล้มที่ทางลาด ไม่ถึงเส้นชัย ติดหน้าประตู · ก่อนโทษ policy ให้ตรวจด่านและกติกาก่อน: วัดพื้น ดูวิดีโอ ดูตำแหน่ง"),
    at=1), "ผลข้างเคียงของบั๊กประตู: เวอร์ชันประตูบานเดียว walk_2000 เข้าเส้นใน MuJoCo ได้ 43.5 s — พอเปลี่ยนเป็นประตูคู่กลับล้มที่ประตู · make_course.py slope= จาก Module 4 มีบั๊กเรเดียนเดียวกัน (แก้แล้ว ผลใน Module 4 ไม่ได้ใช้ทางลาด)")

# ================================================================ Ex A.3 train a climber
put("exA3", slide("exA3", head("Exercise A.3 · Train a climber", "เทรนต่อบนบันไดสูงขึ้น แล้วกลับมาปีนภูเขา", "A.3"),
    code(f'{G} MICRODUCK_STAIR_MAX=0.035 uv run train Mjlab-Velocity-Rough-MicroDuck --env.scene.num-envs 1024 \\<br>'
         f'{SP}--agent.max-iterations 1000 --agent.resume True --agent.load-run …rough_ft --agent.load-checkpoint model_2998.pt{SP}{C("# ~42 นาที")}', 25),
    row=[task(["เพิ่ม env var ให้ step_height_range ปรับได้ (ค่าเดิม 1.5 cm)",
               "เทรนต่อจาก rough_ft บนบันไดสูงสุด 3.5 cm อีก 1,000 รอบ",
               "export แล้วรัน Ex A.1–A.2 ซ้ำทั้งสองซิม",
               "ดู Curriculum/terrain_levels และ Metrics/peak_height_mean ใน log"]),
         card("อ่าน log ให้ดี", p("terrain_levels ลดจาก 2.4 เหลือ 0 ทั้งรอบนี้และรอบ rough_ft — กฎเลื่อนขั้นต้องเดินไกล 4 ม. ใน 20 s ซึ่งเป็ดทำไม่ได้", 27)
              + p("แต่ไม่ได้แปลว่าเทรนบนพื้นเรียบ: terrain generator อยู่โหมดสุ่ม ทุกแผ่นสุ่มความยากเอง ไม่ขึ้นกับแถว", 27)
              + p("พีระมิดบันไดให้เกิดบนยอด — ส่วนใหญ่เป็ดฝึก<b>ลง</b>บันได", 27, "#8A4300"))],
    at=2), "mjlab terrain_levels_vel: move_up = เดินไกลกว่า size/2 (4 ม.), move_down = เดินได้น้อยกว่าครึ่งของ |คำสั่ง|·20 s · TerrainGeneratorCfg.curriculum = False ใน MICRODUCK_ROUGH_TERRAINS_CFG")

put("ansA3", answer("ansA3", "A.3", "เทรนนานขึ้นไม่ได้ทำให้ยกเท้าสูงขึ้น",
    [f"Newton: climb35 เข้าเส้น 10 mm {N['climb35_adv10']['finished']}/{N['climb35_adv10']['n']} เลน ({N['climb35_adv10']['times'][0]:.0f}–{N['climb35_adv10']['times'][-1]:.0f} s) พอ ๆ กับ rough_ft ต้นทาง · 20/30 mm ติดตีนภูเขาเหมือนตัวอื่น",
     f"MuJoCo + BAM: เข้าเส้น 10 mm ใน {M['climb_adv10']['finish']:.0f} s (ล้ม {M['climb_adv10']['falls']}) ใกล้ rough_ft ({M['rough_adv10']['finish']:.0f} s) · 20 mm ล้ม {M['climb_adv20']['falls']} ครั้ง ไม่ผ่าน",
     "ต้นเหตุใน log: <b>peak_height_mean ≈ 1.06 cm ตลอด 1,000 รอบ</b> (rough_ft ปลายรอบ 1.17 cm) — reward ตั้งเป้ายกเท้า 2 cm แต่เป็ดไม่เคยไปถึง จึงขึ้นขั้น 2 cm ไม่ได้",
     "สิ่งที่น่าลองต่อ: บันไดแบบขาขึ้น (เกิดในหลุม) · เพิ่มน้ำหนัก foot_swing_height · กฎเลื่อนขั้นที่ใช้ระยะสั้นลง"],
    side=table([[n, ncell(k, "adv10"), mcell(k, "adv10"), mcell(k, "adv20")] for k, n, _ in POLS if k in ("rough_ft", "velstand", "climb35")],
               ["policy", "Newton 10 mm", "MuJoCo 10 mm", "MuJoCo 20 mm"], size=25),
    summary="ก่อนเทรนท่ายาก ให้วัดก่อนว่าร่างกายทำได้ไหม — ยกเท้า 1 ซม. ปีนขั้น 2 ซม. ไม่ได้ ไม่ว่าเทรนกี่รอบ", side_w=1000),
    "ข้อเสนอ 'บันไดขาขึ้น': mjlab มี BoxInvertedPyramidStairsTerrainCfg แต่ cfg ของ Pollen เอาออกเพราะ env_origin_z ติดลบทำให้เกิดใต้พื้น (ดูคอมเมนต์ใน microduck_velocity_env_cfg.py) — ต้องแก้จุดเกิดก่อน")

exec(open(os.path.join(HERE, "gen6_applied.py")).read())
exec(open(os.path.join(HERE, "gen6_applied2.py")).read())

# ================================================================ challenge
chal = [("ออกแบบโซนใหม่", "ไม้กระดก · ทางแคบซิกแซก · ลูกบอลกลิ้งขวาง — เพิ่มใน make_adventure.py แล้วแลกด่านกับทีมอื่น", "Newton อ่านด่านจาก MJCF เองอัตโนมัติ — กล่อง ทรงกระบอก บานพับ"),
        ("ทำลายสถิติ", "policy เดิม เปลี่ยนได้แค่ autopilot: ความเร็วแต่ละโซน เส้นทาง การสลับ policy", "A.4 ได้ 81% ที่ 20 mm — ใครทำ 64/64 ได้?"),
        ("ToF ไม่ตกหลุม", "แก้ tof_cliff ให้ไม่ตกช่องบันไดจากด้านข้าง แล้วไปให้ครบ 6 ห้อง", "ใบ้: ตรวจพื้นทุกคอลัมน์ · เท้าอยู่นอกภาพ ToF — ต้องจำ"),
        ]
best = N["walk_2000_adv10"]["times"][0]
put("challenge", slide("challenge", head("Challenge", "แข่งกันทั้งห้อง บน Newton"),
    f'<div style="flex:1;display:flex;flex-direction:row;gap:28px">' + "".join(card(t, p(d, 30) + '<div style="flex:1"></div>' + p(k, 27, "#3D7A12")) for t, d, k in chal) + '</div>',
    table([["คะแนน", "เวลาในซิม · ไม่เข้าเส้น = เทียบ checkpoint ก่อน แล้วค่อยจำนวนล้ม · รายงานทุกเลน ไม่ใช่เลนที่ดีที่สุด"],
           ["สถิติปัจจุบัน", f"10 mm: walk_2000 {best:.0f} s (velstand + วิ่งบันได มัธยฐาน {X['adv10_0.6']['t_med']:.0f} s) · 20 mm: velstand + วิ่ง {X['sprint_0.6']['t_min']:.0f} s · 30 mm: ยังไม่มีใคร"]],
          ["", ""], size=27),
    at=1))

TT = X["tof"]
tsum = lambda c, k: TT['living_' + c][k] + TT['corridor_' + c][k]
put("ansChal", answer("ansChal", "A.6 · Challenge ToF", "ไม่ตกหลุมเลย 64 เลน — เหลือแต่ชนเฟอร์นิเจอร์",
    [f"<b>tof_cliff2</b>: ตรวจพื้น<b>ทุกคอลัมน์</b> แถว 5–7 · ความสูงจุดที่รังสีชน = หัวสูง − d·sin(มุมก้ม) จากท่าหัวจริง ต่ำกว่าพื้น 4 ซม. = หลุม · หลุมข้าง → เดินช้าแล้วเบี่ยงหนี · หลุมหน้า → หมุนหนีฝั่งตรงข้าม → ตกหลุม <b>{tsum('tof_cliff2', 'hole')}/32</b>",
     f"<b>tof_mem</b>: ToF เห็นแค่ 0.4–0.9 ม. ข้างหน้า เท้าอยู่นอกภาพ — จำจุดหลุมในแผนที่ของตัวเอง (gyro + คำสั่ง แบบ A.7) แล้วไม่เดินเข้าใกล้ → ตกหลุม <b>{tsum('tof_mem', 'hole')}/32</b> ล้มรวมน้อยสุด ({tsum('tof_mem', 'fell')}/32)",
     "ก่อนเชื่อเซนเซอร์ให้ <b>probe</b>: ยืนหน้าหลุมแล้วพิมพ์ภาพ 8×8 — เจอว่า Newton คืน 0 เมื่อไม่ชนอะไร ทุกรุ่นก่อนแก้จึงไม่เคยเห็นหลุม",
     f"ที่ยังล้ม ({tsum('tof_cliff2', 'fell')} และ {tsum('tof_mem', 'fell')} ครั้ง) <b>เกิดนอกหลุมทั้งหมด</b> — มุมตู้ข้างโต๊ะทำงาน มุมตู้เสื้อผ้า ขาโต๊ะ ปลายกำแพง · ไปได้เฉลี่ย ~2 จาก 6 ห้อง: เดินสุ่มยังสำรวจไม่ทั่ว"],
    side=vid("tstill_mem", "tvid_mem", "Duck with tof_mem starting at the stairwell edge, turning away and avoiding it again later, ToF inset", 700, 394)
         + table([[n, f"{tsum(c, 'hole')}/32", f"{tsum(c, 'fell')}/32", f"{tsum(c, 'rooms') / 2:.1f}", f"{tsum(c, 'dist') / 2:.0f} ม."]
                  for c, n in (("tof_cliff", "tof_cliff"), ("tof_cliff2", "tof_cliff2"), ("tof_mem", "tof_mem"))],
                 ["ตัวคุม", "ตกหลุม", "ล้มรวม", "ห้อง", "ระยะ"], size=24),
    summary="โจทย์ถัดไป: ชนเฟอร์นิเจอร์ (ToF จำลองยิง 1 รังสีต่อโซน — ขาโต๊ะ 4 ซม. หลุดระหว่างรังสีได้) และสำรวจให้ครบ 6 ห้อง", side_w=760),
    "16 เลนต่อตัวคุมต่อจุดเริ่ม (นั่งเล่น + ทางเดิน) · 180 s · วิดีโอเริ่มห่างหลุม 35 ซม. หันเข้าหลุม · ตำแหน่งล้มดูจาก fall_xy ใน JSON แล้วเทียบ geom ใน scene_apartment.xml · "
    "ข้อสังเกตเรื่องขาโต๊ะเป็นสมมติฐาน ยังไม่ได้ทดสอบ — ToF ตัวจริงเฉลี่ยทั้งโซน ไม่ใช่รังสีเดียว · env: GEO=1 (ใช้ท่าหัว) DROP=0.04")

OUT = sys.argv[1]
only = sys.argv[2:] or order
os.makedirs(f"{OUT}/project/slides", exist_ok=True)
for sid in only:
    open(f"{OUT}/project/slides/{sid}.html", "w").write(slides[sid])
json.dump(order, open(f"{OUT}/order.json", "w"))
print("wrote", len(only), "slides")
