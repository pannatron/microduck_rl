"""Microduck deck 2 — Module 3–5 Sim Playground. Usage: gen3.py <deck_root> [ids...]"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from lib import H, M, SEC, head, code, task, result, think, table, slide, divider, answer

NAVY = "background:#0E1621;color:#F4F3EE;font-family:'IBM Plex Sans Thai', Arial, sans-serif"
G = '<span style="color:#7AC943">$</span>'
C = lambda t: f'<span style="color:#7A8492">{t}</span>'
K = lambda t: f'<span style="color:#FFB86B">{t}</span>'
SP = "&#160;" * 4
B = lambda i: f"/_blob/{i}"
HERO = B("a88555969a0a11f36f88f09a35699164")
COURSE = B("af096553fce887f045e1b7dad0e6813f")
DANCE = B("5f1fca8d5fca82bdf6c5acaeab8ef162")
KICK = B("68e938064ccfbb7cbade2a5735f4c78f")
PICK = B("28af7f59731772ede3e9d50e9652204e")
ROLL = B("f3fbfd120612e09b263e2ea53075d7d6")
SIT = B("3bf5c34ac09ad6680496afa9b0d0265a")
SOCBAR = B("3fd000bcbe363d7eb47b52d195efe9c6")
SIDE = B("68a5aff00f1d9accdf8e762e9b9b90bd")
SECROLL = B("905e876607921c021b318cd593cec247")
SECKICK = B("52d3a9e60469ef7d01adbaa9f928788c")
SOCFR = B("4fcb54f50d3a1a68fc5a54a9c20d9776")
RES = json.load(open(os.path.join(os.path.dirname(__file__), "results3.json")))
STEPS = B(RES["steps_blob"]) if RES.get("steps_blob") else None

slides, order = {}, []


def put(sid, html, notes=None):
    if notes:
        html = html.rstrip()
        html = html[: -len("</section>")] + f"<aside>{notes}</aside></section>\n"
    slides[sid] = html
    order.append(sid)


def p(t, size=33, color="#1B2430", extra=""):
    return f'<p style="font-size:{size}px;color:{color};line-height:1.45{extra}">{t}</p>'


def card(title, body, bg="#FBFAF6", border="1px solid #DDDBD2", tcolor="#0E1621"):
    return (f'<div style="flex:1;background:{bg};border:{border};border-radius:24px;padding:40px 44px;display:flex;flex-direction:column;gap:22px">'
            f'<h3 style="{H};font-size:44px;font-weight:600;color:{tcolor};line-height:1.15">{title}</h3>{body}</div>')


def big(v, label, color="#1F4D06"):
    return f'<div><p style="{H};font-size:68px;font-weight:600;color:{color};line-height:1">{v}</p>{p(label, 26)}</div>'


def bigrow(*items):
    return f'<div style="display:flex;flex-direction:row;gap:44px">{"".join(items)}</div>'


def section(sid, eyebrow, title, sub, img, alt):
    return (f'<section id="{sid}" data-transition="fade" style="{NAVY};padding:128px;display:flex;flex-direction:row;gap:64px;align-items:center">'
            f'<div style="flex:1;display:flex;flex-direction:column;gap:28px">'
            f'<p style="font-size:24px;letter-spacing:3px;text-transform:uppercase;color:#7AC943;font-weight:600">{eyebrow}</p>'
            f'<h1 style="{H};font-size:110px;font-weight:600;line-height:1.05;color:#F4F3EE">{title}</h1>'
            f'<p style="font-size:36px;color:#B8C4D0;line-height:1.4">{sub}</p></div>'
            f'<img src="{img}" alt="{alt}" style="width:620px;height:760px;object-fit:cover;border-radius:24px"></section>\n')


def strip(src, alt, h=300):
    return f'<img src="{src}" alt="{alt}" style="width:1696px;height:{h}px;object-fit:cover;border-radius:20px">'


# ================================================================ cover / agenda
put("cover", f'''<section id="cover" data-transition="fade" style="{NAVY};padding:128px;display:flex;flex-direction:row;gap:72px;align-items:center">
<div style="flex:1;display:flex;flex-direction:column;gap:28px">
<p style="font-size:24px;letter-spacing:3px;text-transform:uppercase;color:#7AC943">Engineering Workshop · mjlab + MuJoCo</p>
<h1 style="{H};font-size:120px;font-weight:600;line-height:1.02;color:#F4F3EE">Sim Playground</h1>
<p style="font-size:40px;color:#B8C4D0;line-height:1.4">Module 3–6 — ท่าทาง ด่าน แอป และ Newton ก่อนหุ่นจริงจะมาถึง</p>
<div style="display:flex;flex-direction:row;gap:16px">
<p style="font-size:24px;background:#7AC943;color:#0E1621;padding:10px 22px;border-radius:40px;font-weight:600">ไม่ต้องมีหุ่น</p>
<p style="font-size:24px;border:2px solid #3A4A5C;color:#B8C4D0;padding:8px 22px;border-radius:40px">Microduck RL · ภาค 2</p>
</div>
<p style="font-size:28px;color:#B8C4D0;line-height:1.5">Pannatorn Bongkotamphon<br>Dr. Sukhum Sattaratnamai</p>
</div>
<img src="{HERO}" alt="Microduck robot model rendered in MuJoCo" style="width:720px;height:820px;object-fit:cover;border-radius:24px">
</section>''', "ภาคต่อจาก Module 1–2 ทั้งภาคนี้รันบนซิมล้วน: ใช้ policy ทางการของ Pollen 9 ตัว สร้างด่านเอง และเขียนแอปควบคุมเป็ด ทุกตัวเลขวัดจริงบนเครื่องทดสอบ RTX 3060 Laptop 6 GB")

agenda_items = [
    ("03", "Skill Zoo · เรียก 9 ท่าของ Pollen ในซิม", "#3D7A12"),
    ("04", "Level Design · สร้างด่าน แล้วดูว่าเป็ดตกตรงไหน", "#3D7A12"),
    ("05", "Applications · เต้น เตะบอล เขียน state machine", "#3D7A12"),
    ("06", "Newton · sim-to-sim และเทรนขนานหลายหมื่นตัว", "#3D7A12"),
    ("Ex", "Exercises 8 ข้อ + เฉลย", "#B85C00"),
]
rows = ""
for i, (n, t, c) in enumerate(agenda_items):
    bd = "border-bottom:2px solid #DDDBD2;padding:0px 0px 22px 0px" if i < len(agenda_items) - 1 else ""
    rows += (f'<div style="display:flex;flex-direction:row;gap:36px;align-items:baseline;{bd}">'
             f'<p style="{H};font-size:40px;font-weight:600;color:{c};width:72px">{n}</p>'
             f'<p style="{H};font-size:44px;font-weight:500;color:#0E1621">{t}</p></div>')
put("agenda", f'''<section id="agenda" data-transition="fade" style="{SEC};padding:120px 128px 120px;display:flex;flex-direction:row;gap:96px">
<div style="width:520px;display:flex;flex-direction:column;justify-content:space-between">
<div style="display:flex;flex-direction:column;gap:20px">
<p style="font-size:28px;letter-spacing:4px;text-transform:uppercase;color:#3D7A12;font-weight:600">Module 3–6</p>
<h2 style="{H};font-size:120px;font-weight:600;line-height:1;color:#0E1621">Agenda</h2>
</div>
<img src="{COURSE}" alt="Microduck at the start of a custom obstacle course" style="width:520px;height:480px;object-fit:cover;border-radius:24px">
</div>
<div style="flex:1;display:flex;flex-direction:column;justify-content:space-between">{rows}</div>
</section>''')

put("why", slide("why", head("ทำไมเริ่มที่ซิม", "ยังไม่มีหุ่น ก็ฝึกครบ 3 ชั้นได้"),
    think("ทุกโจทย์ในภาคนี้รันบน <b>CPU</b> ได้เร็วกว่า real-time ราว 15–20 เท่า ยกเว้น Ex 4.2 ที่ต้องใช้ GPU เทรน"),
    row=[card("ชั้น Skill", p("policy ONNX แต่ละตัว = หนึ่งท่า (เดิน นั่ง เตะ ม้วน) เรียนจากของจริงที่ Pollen ส่งมากับหุ่น") + p("ฝึก: เรียก ร้อย และสลับท่า", 30, "#4A5563") + '<div style="flex:1"></div>' + p("<b>Module 3</b>", 30, "#3D7A12")),
         card("ชั้นโลก", p("พื้น บันได ทางลาด ลูกบอล — ทุกอย่างคือ MJCF ที่เราแก้เองได้ แล้ววัดว่า policy พังตรงไหน") + p("ฝึก: สร้างด่าน วัดเป็น x/5 เทรนต่อบนพื้นขรุขระ", 30, "#4A5563") + '<div style="flex:1"></div>' + p("<b>Module 4</b>", 30, "#3D7A12")),
         card("ชั้นแอป", p("โค้ด Python ที่ตัดสินใจว่าจะสั่งท่าไหนเมื่อไร — ตัวเดียวกันนี้ย้ายไปรันบนหุ่นจริงได้") + p("ฝึก: ท่าเต้น state machine เตะบอล calibrate", 30, "#4A5563") + '<div style="flex:1"></div>' + p("<b>Module 5</b>", 30, "#3D7A12"))],
    at=1, ),
    "ชั้นแอปคือส่วนที่วิศวกรส่วนใหญ่ต้องเขียนจริงในงาน และไม่ต้องรอฮาร์ดแวร์")

# ================================================================ MODULE 3
put("sec-m3", section("sec-m3", "Module 3 · Skill Zoo", "9 ท่า<br>พร้อมใช้", "Pollen ปล่อย policy ทุกท่าที่หุ่นจริงใช้ไว้ใน HF repo เดียว — โหลดมาเล่นในซิมได้ทันที", SECROLL, "Microduck mid forward roll"))

zoo = [["velstand", "perpetual", "เดิน + ยืนนิ่ง (ค่าเริ่มต้น)", "twist 3 + body roll/pitch"],
       ["alpha_sitstand", "scripted", "นั่ง ↔ ลุก", "twist.vx = 1 นั่ง / 0 ยืน"],
       ["alpha_ground_pick", "episodic 2.8 s", "ก้มเก็บของ", "phase ผ่าน twist.vx, vy"],
       ["ball_kick_left / right", "episodic 0.5 s", "เตะบอล", "command ศูนย์ทั้ง 13 ช่อง"],
       ["roulade", "episodic 1.0 s", "ม้วนหน้า", "command ศูนย์"],
       ["roller / roller_crouch", "perpetual / 3.5 s", "ไถรองเท้าสเก็ต", "ใช้ robot XML คนละตัว"]]
put("zoo", slide("zoo", head("exports/official/manifest.json", "ท่าทั้งหมด อ่านจาก manifest"),
    table(zoo, ["ไฟล์", "ชนิด", "ทำอะไร", "สั่งผ่าน command อย่างไร"], size=30),
    code(f'{G} uv run python -c "from huggingface_hub import snapshot_download as s; s(\'pollen-robotics/microduck-policies\', local_dir=\'exports/official\')"', 26),
    at=1), "ทุกตัวรับ obs 61 มิติเหมือนกัน ต่างกันแค่ความหมายของ 13 ช่อง command — นี่คือเหตุผลที่สลับ policy กลางอากาศได้")

put("switch", slide("switch", head("กลไกสลับท่า", "สลับท่า = สลับ ONNX session"),
    think("ทำไมท่าแบบ episodic ถึงต้องป้อน command เป็นศูนย์ทั้ง 13 ช่อง? — เพราะตอนเทรนมันเห็นแค่ศูนย์ ค่าอื่นคือ <b>out-of-distribution</b>"),
    row=[card("perpetual", p("รันตลอด จนกว่าจะสั่งเปลี่ยน — <b>velstand</b> คือ “บ้าน” ที่ทุกท่ากลับมา") + p("ตัวอย่าง: velstand, roller", 28, "#4A5563")),
         card("episodic", p("รันตามเวลาที่กำหนด แล้ว infer_policy คืนให้ velstand เอง — ต้อง<b>เริ่มจากท่ายืน</b> ถึงจะสั่งได้") + p("ตัวอย่าง: kick 0.5 s, roulade 1.0 s, ground_pick 2.8 s", 28, "#4A5563")),
         card("scripted", p("policy เดียวทำสองทิศ — sitstand อ่าน flag ในช่อง twist.vx: 1 = นั่ง, 0 = ลุก") + p("ตัวอย่าง: alpha_sitstand (ramp 2 s)", 28, "#4A5563"))],
    at=1))

put("harness", slide("harness", head("playground/sim_play.py", "ไม่มีคีย์บอร์ด ก็ให้ “ผู้กำกับ” กดแทน"),
    code(f'{C("# ctl_keys.py — กดปุ่มตามเวลา")}<br>'
         f'{K("def")} control(t, pol, m, d):{SP}{C("# เรียกทุก control step (50 Hz)")}<br>'
         f'{SP}... {K("return")} [{K(chr(34)+"k"+chr(34))}]{SP}{C("# = กด K (เตะซ้าย)")}<br><br>'
         f'{G} KEYS=<b>"2:y 6:y 10:k 15:r"</b> python playground/sim_play.py --ctl playground/ctl_keys.py \\<br>'
         f'{SP}--secs 20 -- --walking velstand.onnx --sitstand alpha_sitstand.onnx \\<br>'
         f'{SP}--kick-left ball_kick_left.onnx --roulade roulade.onnx --new-cmd-obs', 28),
    row=[card("แทนที่ 3 อย่าง", p("TerminalInput → Director · viewer → offscreen renderer · <b>time.time() → เวลาในซิม</b>", 30)),
         card("ทำไมต้องเวลาซิม", p("infer_policy นับเวลาท่า episodic ด้วยนาฬิกาจริง — บน CPU ที่เร็วกว่า real-time ท่าจะ<b>ถูกตัดก่อนจบ</b>", 30))],
    at=2), "sim_play.py exec ตัว infer_policy.py เดิมทั้งไฟล์ แค่แทนชื่อ TerminalInput ด้วย Director จึงได้ BAM, การสลับท่า และ obs แบบเดียวกับที่ใช้จริงทุกบรรทัด เร็วกว่า real-time ประมาณ 15–20 เท่าบน CPU")

put("kick", slide("kick", head("ball_kick_left.onnx · 0.1 s ต่อเฟรม", "เตะ: 0.5 วินาที บอลไป 2.6 เมตร"),
    strip(KICK, "Six frames 0.1 s apart: the duck swings its left foot and the ball leaves the frame", 330),
    row=[result(bigrow(big("2.55 m", "บอลไปไกลสุดใน 4 s"), big("1.00", "upright หลังเตะ (1 = ตั้งตรง)")), "ผลบนเครื่องทดสอบ · CPU MuJoCo + BAM"),
         card("ข้อควรรู้", p("infer_policy <b>วาร์ปบอล</b>ไปไว้หน้าเท้าทุกครั้งที่กด K (ตรงกับตอนเทรน) — Module 5 เราจะปิดมัน แล้วให้เป็ดเดินไปหาบอลเอง", 30))],
    at=2))

put("roll", slide("roll", head("roulade.onnx · scene_allcollisions.xml", "ม้วนหน้า แล้วลุกยืนเอง"),
    strip(ROLL, "Six frames: standing, tucking, rolling over the head, landing, standing again", 330),
    row=[result(bigrow(big("0.58 m", "ไถลไปข้างหน้า"), big("1.0 s", "ตัวท่า + 1 s ให้ velstand รับช่วง")), "ผลบนเครื่องทดสอบ · CPU MuJoCo + BAM"),
         card("ใช้ scene ไหน", p("ตอนถ่ายใช้ <b>scene_allcollisions.xml</b> ให้ลำตัวและหัวชนพื้นได้จริง — ฉากปกติมี collision แค่ที่เท้า", 30))],
    at=2))

put("picksit", slide("picksit", head("alpha_ground_pick · alpha_sitstand", "ก้มเก็บของ และนั่ง–ลุก"),
    strip(PICK, "Ground pick: the duck crouches and lowers its head to the floor, then stands", 270),
    strip(SIT, "Sit and stand: the duck folds its legs to sit, then stands back up", 270),
    think("ground_pick ไม่ได้รับ “เป้าหมาย” — command คือ <b>phase</b> ของนาฬิกา 4 s ใส่ในช่อง vx, vy เป็ดจึงก้มที่เดิมทุกครั้ง ถ้าอยากหยิบของตรงไหน ต้องเดินไปให้ถึงก่อน"),
    at=1))

put("ex31", slide("ex31", head("Exercise 3.1 · Skill chain", "ร้อยท่าเป็นโชว์ 20 วินาที", "3.1"),
    code(f'{G} KEYS="2:y 4:k 6:y 10:k 15:r" python playground/sim_play.py --ctl playground/ctl_keys.py --secs 20 -- \\<br>'
         f'{SP}--walking velstand.onnx --sitstand alpha_sitstand.onnx --kick-left ball_kick_left.onnx --roulade roulade.onnx --new-cmd-obs', 26),
    row=[task(["นั่ง (Y) → ลอง<b>เตะตอนนั่ง</b> (K) → ลุก → เตะ → ม้วนหน้า",
               "อ่าน log: คำสั่งไหนถูกปฏิเสธ เพราะอะไร?",
               "จดตำแหน่งบอลและ upright ตอนจบ",
               "ลองตั้ง <b>--roulade-duration 0.5</b> — เกิดอะไรขึ้น? (ทำเอง ไม่มีเฉลยตัวเลข)"]),
         result(bigrow(big("1 คำสั่ง", "ถูกปฏิเสธ: เตะตอนนั่ง", "#B85C00"), big("5.5 m", "บอลไปหลังเตะครั้งที่ 2")) + p("จบที่ upright 1.00 — ทุกท่ากลับบ้านที่ velstand ได้", 28))],
    at=2))

put("ans31", answer("ans31", "3.1", "ตัวสลับท่าคือ state machine ตัวแรกของเรา",
    ["log ขึ้น <b>Cannot start kick_left while sitting</b> — infer_policy มี guard: ท่า episodic เริ่มได้จากท่ายืนเท่านั้น",
     "เตะหลังลุกได้ปกติ บอลไป 5.5 m (สุ่มต่างจาก 2.55 m เพราะท่ายืนก่อนเตะต่างกัน)",
     "ทุกท่าจบแล้วคืนให้ velstand — upright 1.00 ตอน t = 20 s",
     "guard แบบนี้คือสิ่งที่ต้องเขียนเองในแอปจริง: <b>ท่าไหนต่อจากท่าไหนได้</b>"],
    side=code(f'{C("# จาก log จริง")}<br>Sit: ON<br><span style="color:#FF8A80">Cannot start kick_left while sitting</span><br>Sit: OFF → standing up<br>kick_left: started<br>kick_left: done → back to walking<br>roulade: started<br>roulade: done → back to walking', 26),
    summary="ท่าแต่ละตัวเก่งเฉพาะจุดเริ่มที่มันถูกเทรน — การร้อยท่าคือการพาเป็ดไปถึงจุดเริ่มนั้นก่อน", side_w=820))

# ================================================================ MODULE 4
put("sec-m4", section("sec-m4", "Module 4 · Level Design", "สร้างด่าน", "พื้นในซิมคือ MJCF ไม่กี่บรรทัด — สร้างบันได ทางลาด พื้นขรุขระ แล้ววัดว่า policy ไปได้ถึงไหน", COURSE, "Custom obstacle course with stairs, rough tiles and a landing"))

terr = [["flat", "25%", "พื้นเรียบ"],
        ["pyramid_stairs", "25%", "ขั้นสูง 0–<b>1.5 cm</b> (ค่า default ของ mjlab คือ 10 cm)"],
        ["random_grid", "30%", "แผ่น 45 cm สูงสุ่ม 0–1 cm"],
        ["pyramid_slope", "20%", "ลาด 1.7°–5.7°"]]
put("terrain", slide("terrain", head("Mjlab-Velocity-Rough-MicroDuck", "ด่านตอนเทรน: เล็กมาก เพราะเป็ดยกเท้าได้ 1–2 cm"),
    table(terr, ["sub-terrain", "สัดส่วน", "รายละเอียด"], size=30),
    row=[card("terrain curriculum", p("10 ระดับความยาก — ผ่านด่านได้ไกล = เลื่อนขึ้นระดับ ล้มบ่อย = ลดลง ดูได้ใน <b>Curriculum/terrain_levels</b>", 30)),
         card("ขอบนิ่มกว่าปกติ", p("ทุกก้อนตั้ง <b>solref 0.04</b> (นิ่มกว่าค่าปกติ 2 เท่า) กันขอบกล่องทำ solver ระเบิดเป็น NaN", 30))],
    at=2), "ค่าทั้งหมดอ่านจาก MICRODUCK_ROUGH_TERRAINS_CFG ใน microduck_velocity_env_cfg.py; โค้ดคอมเมนต์ไว้เองว่าหุ่นยกเท้าได้ราว 1–2 cm")

put("mjcf", slide("mjcf", head("playground/make_course.py", "ด่านหนึ่งด่าน = กล่องไม่กี่ก้อน"),
    code(f'{K("def")} box(name, x, y, z, sx, sy, sz, rgba):{SP}{C("# sx,sy,sz = ครึ่งความกว้าง")}<br>'
         f'{SP}{K("return")} f\'&lt;geom type="box" pos="{{x}} {{y}} {{z}}" size="{{sx}} {{sy}} {{sz}}"<br>'
         f'{SP}{SP}{SP}{SP}solref="0.04 1"/&gt;\'{SP}{C("# ขอบนิ่มแบบเดียวกับตอนเทรน")}<br><br>'
         f'xml = open({K(chr(39)+"scene.xml"+chr(39))}).read().replace({K(chr(39)+"&lt;/worldbody&gt;"+chr(39))}, geoms + {K(chr(39)+"&lt;/worldbody&gt;"+chr(39))})<br><br>'
         f'{G} python playground/make_course.py step10 step=0.010 soft{SP}{C("# ขั้นเดียว 10 mm")}<br>'
         f'{G} python playground/make_course.py course course soft{SP}{SP}{C("# ด่านรวม")}', 28),
    row=[card("ต้องวางไฟล์ข้าง robot XML", p("include และ meshdir เป็น path สัมพัทธ์ — scene ใหม่ต้องอยู่ใน robot/microduck/", 30)),
         card("ctl_straight.py", p("P-controller บนมุม yaw ให้เดินตรง — ไม่งั้นเป็ดเราเดินวนซ้ายจนพลาดด่าน (Ex 1.2)", 30))],
    at=2))

put("course", slide("course", head("scene_course.xml", "ด่านรวม: บันได 3 ขั้น → แผ่นขรุขระ → ลงจอด"),
    f'<img src="{COURSE}" alt="Course: three stairs of 5, 10 and 15 mm, a strip of rough tiles 15–23 mm high, then a landing at 15 mm" style="width:1696px;height:640px;object-fit:cover;border-radius:20px">',
    p("บันได 5 → 10 → 15 mm · แผ่น 12 cm สูงสุ่ม 15–23 mm กว้าง 48 cm · ลงสู่พื้น 15 mm · เป้าหมายที่ x = 2.6 m", 30, "#4A5563"),
    at=1))

st = RES["steps"]
put("ex41", slide("ex41", head("Exercise 4.1 · Step ladder", "ขั้นสูงเท่าไรที่เป็ดยังข้ามได้?", "4.1"),
    code(f'{G} for h in 0.005 0.010 0.015 0.020 0.025; do python playground/make_course.py s$h step=$h soft; done<br>'
         f'{G} X0=-0.06 VX=0.3 python playground/sim_play.py --ctl playground/ctl_straight.py --secs 20 -- \\<br>{SP}--walking &lt;policy&gt;.onnx --new-cmd-obs --scene .../scene_s0.010.xml', 26),
    row=[task(["รันทุกความสูง × <b>5 จุดเริ่ม</b> (X0 = 0, −3, −6, −9, −12 cm)",
               "ผ่าน = x &gt; 0.6 m และ upright &gt; 0.8",
               "เทียบ <b>velstand</b> (Pollen, เทรนบน Rough) กับ <b>walk_2000</b> (ของเรา, Flat)",
               "ทำไมต้องรันหลายจุดเริ่ม?"]),
         result(bigrow(big(st["ours_max"], "ของเราข้ามได้สูงสุด"), big(st["vs_low"], "velstand ที่ 5 mm", "#B85C00")) + p(st["headline"], 28))],
    at=2))

put("ans41", answer("ans41", "4.1", "ซิมไม่ได้ตอบว่า “ข้ามได้ไหม” แต่ตอบว่า “กี่ครั้งในกี่ครั้ง”", st["answers"],
    side=f'<img src="{STEPS}" alt="Pass rate by step height for each policy" style="width:880px;height:520px;object-fit:contain;border-radius:16px">' if STEPS else "",
    summary=st["summary"], side_w=880), st.get("notes"))

rf = RES["rough"]
put("ex42", slide("ex42", head("Exercise 4.2 · Train for the level", "เทรนต่อบนพื้นขรุขระ แล้วกลับมาลองด่าน", "4.2"),
    code(f'{G} uv run train Mjlab-Velocity-Rough-MicroDuck --env.scene.num-envs 1024 \\<br>'
         f'{SP}--agent.resume True --agent.load-run &lt;flat run&gt; --agent.load-checkpoint model_1999.pt \\<br>{SP}--agent.max-iterations 1000', 26),
    row=[task(["ลอง num-envs 4096 ก่อน แล้วค่อยลดลง — Rough ใช้ VRAM ต่อ env มากกว่า Flat แค่ไหน?",
               "เทรนต่อจาก checkpoint Flat อีก 1,000 iterations",
               "ดู <b>Curriculum/terrain_levels/mean</b> ระหว่างเทรน",
               "export แล้วรัน Ex 4.1 + ด่านรวมซ้ำ"]),
         result(bigrow(big(rf["envs"], "envs ที่รันได้บน 6 GB", "#B85C00"), big(rf["time"], "1,000 iterations")) + p(rf["headline"], 28))],
    at=2))

put("ans42", answer("ans42", "4.2", rf["title"], rf["answers"],
    side=table(rf["table"], ["ด่าน", "walk_2000 (Flat)", "rough_ft (ของเรา)", "velstand"], size=26),
    summary=rf["summary"], side_w=900), rf.get("notes"))

# ================================================================ MODULE 5
put("sec-m5", section("sec-m5", "Module 5 · Applications", "เขียนแอป<br>บนเป็ด", "policy คือกล้ามเนื้อ แอปคือสมอง — เขียนแค่ 13 ตัวเลขต่อ step ก็สั่งเป็ดได้ทุกอย่าง", SECKICK, "Duck swinging its left foot at a ball"))

layers = [["0–2", "twist", "vx, vy, ωz", "เดิน เลี้ยว ยืนนิ่ง (ศูนย์)"],
          ["3–6", "head_pose", "neck pitch, head pitch / yaw / roll", "หันหัว ก้ม เงย"],
          ["7–12", "body_pose", "x, y, z, roll, pitch, yaw", "ย่อตัว เอียงตัว"]]
put("layers", slide("layers", head("API ของเป็ด", "แอปเขียนแค่ command 13 ช่อง"),
    table(layers, ["ช่อง", "กลุ่ม", "ค่า", "ใช้ทำ"], size=30),
    code(f'pol.vel_cmd = np.array([vx, vy, wz]){SP}{C("# twist")}<br>'
         f'pol.head_offset[:] = [0, pitch, yaw, 0]{SP}{C("# head_pose (rad)")}<br>'
         f'pol.body_cmd[:] = [0, 0, 0, roll, pitch, 0]{SP}{C("# body_pose")}<br>'
         f'pol._update_policy_session(); pol._update_command()', 28),
    think("ท่าแบบ episodic (เตะ ม้วน ก้ม) ไม่ได้อยู่ใน 13 ช่องนี้ — แอปสั่งด้วยการ “กดปุ่ม” ผ่าน <b>return [\"k\"]</b> เหมือนเดิม"),
    at=1), "อย่าใช้ pol.set_vel_cmd() ใน loop 50 Hz เพราะมัน print ทุกครั้ง; ตั้ง field ตรงแล้วเรียก _update_command แทน")

put("dance", slide("dance", head("playground/ctl_dance.py", "ท่าเต้น = keyframe + interpolation"),
    row=[f'<div style="flex:1;display:flex;flex-direction:column;gap:24px">'
         + code(f'KF = [{C("# t, head_yaw, head_pitch, roll, pitch, vx, wz")}<br>'
                f'{SP}(2.5, D(45), 0, 0, 0, 0, 0),{SP}{C("# หันซ้าย")}<br>'
                f'{SP}(4.5, 0, D(-25), 0, 0, 0, 0),{SP}{C("# ก้มหัว")}<br>'
                f'{SP}(6.5, 0, 0, D(8), 0, 0, 0),{SP}{C("# เอียงตัว")}<br>'
                f'{SP}(11.0, D(30), 0, 0, 0, 0, 1.0),{SP}{C("# หมุนตัว")}<br>]<br>'
                f'u = 0.5 - 0.5*cos(pi*u){SP}{C("# เร่ง-ผ่อนนุ่ม ๆ")}', 26)
         + result(bigrow(big("1.04", "rad/s ที่หมุนได้ (สั่ง 1.0)"), big("1.6°", "RMS error ของ roll")), "ผลบนเครื่องทดสอบ · velstand") + '</div>',
         f'<img src="{DANCE}" alt="Commanded vs achieved trunk roll at 1x and 3x command scale" style="width:820px;height:600px;object-fit:contain;border-radius:20px">'],
    at=1))

put("ex51", slide("ex51", head("Exercise 5.1 · Push the envelope", "สั่งเอียงเกินช่วงที่เทรน เป็ดทำตามไหม?", "5.1"),
    code(f'{G} for s in 1 2 3; do SCALE=$s python playground/sim_play.py --ctl playground/ctl_dance.py --secs 17 -- \\<br>{SP}--walking velstand.onnx --new-cmd-obs; done', 26),
    row=[task(["รันท่าเต้นเดิมโดยคูณมุม body ด้วย 1, 2, 3 (สูงสุด 8°, 16°, 24°)",
               "วัดมุม roll ที่ทำได้จริงเทียบกับที่สั่ง",
               "manifest บอกว่า velstand เอียงได้ราว <b>±10°</b> — ผลตรงไหม?",
               "เป็ดล้มไหม?"]),
         result(table([["×1 (8°)", "6.3°", "1.6°", "ไม่ล้ม"], ["×2 (16°)", "13.1°", "2.1°", "ไม่ล้ม"], ["×3 (24°)", "17.5°", "2.8°", "ไม่ล้ม"]],
                      ["สั่ง", "roll สูงสุดจริง", "RMS error", ""], size=28))],
    at=2))

put("ans51", answer("ans51", "5.1", "policy ที่ดี “ไม่ทำตาม” อย่างปลอดภัย",
    ["roll <b>อิ่มตัวที่ราว 17°</b> แม้สั่ง 24° — policy ไม่ยอมเอียงจนล้ม เพราะ reward ตั้งตรงมี weight สูงกว่า",
     "ตั้งแต่ ×1 ก็ได้แค่ราว 80% ของคำสั่ง (6.3° จาก 8°) — มี lag ราว 0.2 s ตามกราฟ",
     "ไม่ล้มเลยทั้ง 3 ระดับ แต่ <b>error โตขึ้น</b> 1.6° → 2.8° — ใช้ error เป็นสัญญาณว่าออกนอกช่วงแล้ว",
     "ในแอปจริง: clip คำสั่งให้อยู่ในช่วงที่เทรน (±10°) ดีกว่าหวังว่า policy จะรับมือเอง"],
    side=f'<img src="{DANCE}" alt="Roll tracking at 1x and 3x" style="width:820px;height:480px;object-fit:contain;border-radius:16px">',
    summary="ออกนอกช่วงที่เทรนไม่ได้แปลว่าพังทันที แต่ไม่มีใครรับประกัน — ช่วงที่เทรนคือสเปกของ API", side_w=820))

fsm = ""
for i, (n, d) in enumerate([("APPROACH", "หันหาจุดหลังบอล<br>แล้วเดิน 0.3 m/s"), ("ALIGN", "ปรับ x, y, yaw<br>ด้วย P-controller"),
                             ("SETTLE", "หยุด 1 s<br>เช็กว่ายังตรง"), ("KICK", "กด K<br>รอ 3.5 s")]):
    fsm += (f'<div style="flex:1;background:{"#1F4D06" if n == "KICK" else "#FBFAF6"};border:1px solid #DDDBD2;border-radius:24px;padding:32px 28px;display:flex;flex-direction:column;gap:14px">'
            f'<p style="{M};font-size:30px;font-weight:600;color:{"#B8E68F" if n == "KICK" else "#B85C00"}">{n}</p>'
            f'<p style="font-size:28px;color:{"#F4F3EE" if n == "KICK" else "#1B2430"};line-height:1.4">{d}</p></div>')
    if i < 3:
        fsm += '<x-shape kind="arrow-right" style="width:56px;height:32px;background:#B9B7AE;align-self:center"></x-shape>'
put("soccer", slide("soccer", head("playground/ctl_soccer.py", "แอปเตะบอล: state machine 4 สถานะ"),
    f'<div style="display:flex;flex-direction:row;gap:16px">{fsm}</div>',
    f'<img src="{SOCFR}" alt="Top view: duck walks around the ball, lines up behind it, kicks it toward the goal posts" style="width:1696px;height:340px;object-fit:cover;border-radius:20px">',
    p("ปิดการวาร์ปบอลก่อน: <b>pol._place_ball = lambda name: None</b> — ต้องเดินไปให้บอลอยู่ที่ (9, 4.2) cm หน้าเท้าซ้ายเอง เหมือนตอนเทรน", 30),
    at=1), "SETTLE กลับไป ALIGN ได้ถ้ายังคลาด และ ALIGN มี timeout 12 s กันค้าง")

put("ex52", slide("ex52", head("Exercise 5.2 · Calibrate", "จาก 4 ใน 12 ลูก ให้ได้ 8 ใน 12", "5.2"),
    code(f'{G} BALL=0.6,-0.3 TOL=0.015 VMIN=0.2 AIM=14 python playground/sim_play.py --ctl playground/ctl_soccer.py --secs 60 -- \\<br>'
         f'{SP}--walking velstand.onnx --kick-left ball_kick_left.onnx --new-cmd-obs --scene .../scene_soccer.xml', 26),
    row=[task(["รัน 12 ตำแหน่งบอล ประตูกว้าง 50 cm ที่ x = 2 m",
               "ลด TOL จาก 30 → 15 mm อย่างเดียว ผลเป็นอย่างไร?",
               "ดู <b>align_err</b> ใน log — ทำไมเป็ดหยุดก่อนถึงเป้าเสมอ?",
               "ดู <b>kick_dir_vs_body</b> — เตะออกตรงไหม?"]),
         f'<div style="width:880px;display:flex;flex-direction:column"><img src="{SOCBAR}" alt="Goals out of 12: base 4 to 6, tight tolerance 0, plus minimum command 5, plus aim offset 8" style="width:880px;height:500px;object-fit:contain;border-radius:20px"></div>'],
    at=2), "base รันสองรอบได้ 4 และ 6 ลูก (onnxruntime บน CPU หลายเธรดทำให้ผลไม่ deterministic 100%); +AIM 14° รันสองรอบได้ 8 ทั้งสองรอบ")

put("ans52", answer("ans52", "5.2", "ปัญหาของแอป ส่วนใหญ่คือนิสัยของ policy",
    ["TOL 15 mm อย่างเดียว = <b>0/12</b> — เป็ดหยุดห่างเป้า ~2 cm ทุกครั้ง เพราะคำสั่งเล็ก ๆ ทำให้ velstand <b>ยืนนิ่ง</b> (โซนตายเดียวกับ Ex 1.2)",
     "<b>VMIN 0.2</b>: ถ้ายังคลาด สั่งอย่างน้อย 0.2 m/s ดันผ่านโซนตาย → จัดท่าได้ใน 1 cm, ได้ 5/12",
     "พอจัดท่าแม่นแล้ว ทิศเตะ<b>คงที่</b>: เบี่ยงซ้าย +14° ถึง +19° เกือบทุกลูก — พลาดเสาแค่ 5–12 cm",
     "<b>AIM 14°</b>: หันตัวชดเชยไปทางขวาก่อนเตะ → 8/12 ทั้งสองรอบ ลูกที่ยังพลาดคือเตะเฉียด (เบี่ยง > 40°)"],
    side=f'<img src="{SOCBAR}" alt="Goals out of 12 by configuration" style="width:820px;height:480px;object-fit:contain;border-radius:16px">',
    summary="ต้องจัดท่าให้แม่นก่อน bias ของการเตะถึงจะคงที่พอให้ชดเชยได้ — calibrate ทีละชั้น", side_w=820))

# ================================================================ MODULE 6 · NEWTON
NSCALE = B("5073eca3b7217e042622884779ba2b96")
VID = {"crowd": ("d4d9fdd00bd723f367dbe8f9b73f9ffd", "fcce5321ae4c7996cb22301f88c70328"),
       "progress": ("2c19d3e4661011733f5ab050118f6724", "70081c6101799c39ee81926d064444d9"),
       "latency": ("2696a15c7fb0e6333140d2ec685e91a2", "be463594a1dd0cc2bbe3b0462bda7a9d"),
       "follow": ("802545af424bd9aee868ac5ec8519371", "3d28cdbc2f16ed7accbb50be10021f57")}


def video(name, alt, w, h):
    still, clip = VID[name]
    return f'<img src="{B(still)}" data-video="{B(clip)}" alt="{alt}" style="width:{w}px;height:{h}px;object-fit:cover;border-radius:20px">'


def vslide(sid, eyebrow, title, name, alt, caption, h=600, notes=None):
    put(sid, slide(sid, head(eyebrow, title), video(name, alt, 1696, h), p(caption, 30, "#4A5563"), at=1), notes)

put("sec-m6", section("sec-m6", "Module 6 · Sim-to-Sim on Newton", "เป็ดตัวเดียว<br>สามซิม", "ย้าย policy ไป Newton แล้ววัดเทียบ — จากนั้นเทรนบน Newton เองพร้อมกันหลายหมื่นตัว", HERO, "Microduck model"))

sims = [["MuJoCo CPU + BAM", "scripts/infer_policy.py", "ซ้อมก่อนลงหุ่น (ของ Pollen)"],
        ["MuJoCo Warp (mjlab)", "uv run train", "ที่ policy ถูกเทรน"],
        ["Newton · SolverMuJoCo", "newton_port/newton_duck.py", "ซิมที่สาม: GPU, หลายพันตัวพร้อมกัน"]]
put("n-why", slide("n-why", head("ทำไมต้อง sim-to-sim", "ถ้าเดินได้แค่ในซิมที่เทรน = ยังไม่ผ่าน"),
    table(sims, ["ซิม", "รันด้วย", "บทบาท"], size=30),
    think("Newton ไม่ใช่ MuJoCo ตัวใหม่ — เป็น engine จาก NVIDIA/Disney/DeepMind บน Warp ที่มี solver หลายตัว: <b>MuJoCo, Featherstone, XPBD, VBD, Kamino</b> เราลองทุกตัวที่เกี่ยวกับหุ่นแข็ง"),
    row=[card("ผ่าน", p("<b>SolverMuJoCo</b> รันเป็ด 1,024 ตัวพร้อมกัน ~4,000× real-time ไม่ล้มเลย", 30)),
         card("ไม่ผ่าน (ยัง)", p("Featherstone / semi-implicit / XPBD → <b>NaN</b> ภายใน 1 s ต้องจูน contact และ PD ใหม่ทั้งชุดสำหรับหุ่น 0.7 kg", 30))],
    at=2), "Featherstone: เป็ดถูกดีดขึ้นสูง 0.72 m ใน 0.25 s เพราะ contact kd เริ่มต้น 100 แข็งเกินสำหรับหุ่นเล็ก ลด kd เหลือ 10 แล้วไม่ระเบิดแต่ทรุดลงพื้น และช้า 0.2× real-time; semi/XPBD ต้องเรียก eval_ik เองเพราะไม่อัปเดต joint_q")

put("n-port", slide("n-port", head("newton_port/newton_duck.py", "พอร์ต: ONNX → torch, เป็ดหลายพันตัวใน GPU เดียว"),
    code(f'duck = newton.ModelBuilder(); duck.add_mjcf(<b>"robot_groundcontact.xml"</b>, floating=True)<br>'
         f'scene.replicate(duck, N); scene.add_ground_plane(){SP}{C("# N โลกแยกกัน ไม่ชนกัน")}<br>'
         f'solver = newton.solvers.SolverMuJoCo(model, iterations=10)<br><br>'
         f'x = (obs - mean) / std{SP}{C("# normalizer ที่ฝังใน ONNX")}<br>'
         f'{K("for")} w, b {K("in")} layers: x = elu(x @ w.T + b){SP}{C("# MLP 512-256-128 → 14")}<br>'
         f'tgt[:, -14:] = default + x;{SP}wp.capture_launch(graph){SP}{C("# 4 substep ใน CUDA graph")}', 27),
    row=[result(bigrow(big("4,000×", "real-time · 1,024 ตัว"), big("0 / 1,024", "ล้ม (Pollen ทั้ง 4 policy)")), "ผลบนเครื่องทดสอบ · RTX 3060 Laptop 6 GB"),
         card("ไม่ต้องลง onnxruntime", p("ONNX ของเป็ดคือ Sub → Div → (Gemm, Elu)×4 อ่านน้ำหนักด้วย <b>onnx2npz.py</b> แล้วคูณเมทริกซ์เองใน torch", 30))],
    at=2))

vslide("n-crowd", "Newton ViewerGL · headless", "เป็ด 1,024 ตัว เดินพร้อมกันบน GPU เดียว", "crowd",
       "Top view of 1,024 Microducks walking in a grid on Newton",
       "policy ที่เทรนบน Newton (latency DR) · 4 กลุ่มความเร็ว 0.1–0.4 m/s กลุ่มละ 256 ตัว · ฟิสิกส์ 100× real-time รวมเวลาเรนเดอร์", 620,
       "เรนเดอร์จาก newton.viewer.ViewerGL(headless=True) โดยตรง: newton_duck.py --video <dir> แล้วรวมเป็น mp4 ด้วย make_video.py")

put("n-bug", slide("n-bug", head("ไล่หาความต่างทีละ step", "เป็ดเดินช้าลง 37% บน Newton — เพราะอะไร?"),
    think("ซิมที่ Pollen ใช้ซ้อมก่อนลงหุ่น (MuJoCo CPU) <b>ไม่ได้ตรงกับซิมที่ใช้เทรน</b> ด้วยซ้ำ — sim-to-sim gap มีอยู่แล้วก่อนเราแตะ Newton"),
    row=[card("1 · gyro เร็วกว่า 25%", p("step 0 obs ตรงกันเป๊ะ แต่ step 1 gyro ของ Newton สูงกว่า 1.25 เท่า: <b>mj_step คำนวณ sensor ก่อน integrate</b> → gyro/xquat ของ MuJoCo ช้าไป 1 substep (5 ms) และ policy ถูกเทรนกับค่าที่ช้านั้น", 29)),
         card("2 · จำนวนจุดสัมผัส", p("แก้ข้อ 1 แล้ว step 1–2 ตรงกัน 0.00000 แต่ step 3 (เท้าแตะพื้น) แยกทาง: ยืนนิ่ง MuJoCo CPU ให้ <b>4 จุด/เท้า</b>, MuJoCo Warp (ที่ใช้เทรน) <b>10 จุด/เท้า</b>", 29)),
         card("3 · สิ่งที่ไม่ใช่", p("ตัด integrator, solver iterations, self-collision ทิ้งแล้ว — ผลไม่เปลี่ยน model ที่ Newton แปลงมีค่า kp, damping, armature, friction, solref <b>ตรงกันทุกตัว</b>", 29))],
    at=1), "เครื่องมือ: native_dump.py (obs 50 step แรกจาก MuJoCo), newton_duck.py --dump, substep_cmp.py, mjwarp_contacts.py ทั้งหมดอยู่ใน newton_port/")

put("ex61", slide("ex61", head("Exercise 6.1 · Three sims", "policy เดิม 4 ตัว ใน 3 ซิม ได้ความเร็วเท่ากันไหม?", "6.1"),
    code(f'{G} cd ~/IsaacLab && .venv/bin/python ~/repos/microduck_rl/newton_port/newton_duck.py --policy walk_2000 \\<br>{SP}--cmds 0.2,0.25,0.3,0.4 --per-cmd 256 --secs 20{SP}{C("# 1,024 ตัว ~5 วินาที")}<br>'
         f'{G} bash newton_port/native_batch.sh{SP}{C("# MuJoCo CPU ± BAM")}', 26),
    row=[task(["รัน walk_2000, alpha_walking, velstand, rough_ft บน Newton",
               "รันชุดเดียวกันบน MuJoCo CPU ทั้ง BAM และ --no-bam",
               "ความเร็วที่ cmd 0.3 ต่างกันกี่ % ระหว่างซิม?",
               "อาการ “สั่ง 0.2 แล้วยืนนิ่ง” (Ex 1.2) เป็นนิสัยของ policy หรือของซิม?"]),
         result(table([["walk_2000", "0.133", "0.150", "0.210"], ["alpha_walking", "0.142", "0.110", "0.131"],
                       ["velstand", "0.129", "0.088", "0.109"], ["rough_ft", "0.146", "0.109", "0.139"]],
                      ["cmd 0.3 m/s", "Newton", "CPU+BAM", "CPU no-BAM"], size=26), "ผลวัด · m/s เฉลี่ย 10 s สุดท้าย")],
    at=2))

put("ans61", answer("ans61", "6.1", "ความเร็วต่างกันได้ถึง 37% แต่ “นิสัย” ของ policy ตามไปทุกซิม",
    ["ความเร็วที่ cmd 0.3 แกว่ง <b>0.09–0.21 m/s</b> ตามซิม — ไม่มีซิมไหนเร็วกว่าเสมอ (walk_2000 เร็วสุดใน CPU no-BAM, ที่เหลือเร็วสุดใน Newton)",
     "สั่ง 0.2 แล้ว<b>ยืนนิ่งทั้ง 3 ซิม</b> สำหรับ walk_2000, alpha_walking, rough_ft → เป็นนิสัยของ policy ไม่ใช่บั๊กซิม (ตอบสมมติฐานค้างจาก Ex 1.2)",
     "velstand เดินที่ 0.2 ได้ทุกซิม (0.06–0.09) — เพราะถูกเทรนให้รวมยืน+เดินในตัวเดียว",
     "บน Newton ไม่มีเป็ดล้มเลยใน 1,024 ตัว × 4 policy — ความเสถียรข้ามซิมได้ แต่ <b>ความเร็วไม่ข้าม</b>"],
    side=table([["0.2", "0 / 0 / 0", "0.09 / 0.06 / 0.08"], ["0.25", "0.12 / 0.11 / 0.11", "0.11 / 0.07 / 0.09"],
                ["0.3", "0.13 / 0.15 / 0.21", "0.13 / 0.09 / 0.11"], ["0.4", "0.26 / 0.23 / 0.28", "0.16 / 0.13 / 0.15"]],
               ["cmd", "walk_2000", "velstand"], size=26) + p("ค่าในช่อง = Newton / CPU+BAM / CPU no-BAM (m/s)", 26, "#4A5563"),
    summary="ก่อนลงหุ่น ให้รายงานความเร็วเป็นช่วงจากหลายซิม ไม่ใช่ตัวเลขเดียว", side_w=820))

scale = [["mjlab (MuJoCo Warp)", "4,096", "3.02", "5.0 GB", "33k"], ["Newton", "1,024", "0.39", "0.6 GB", "63k"],
         ["Newton", "4,096", "0.74", "1.4 GB", "133k"], ["Newton", "8,192", "1.25", "2.5 GB", "158k"],
         ["Newton", "16,384", "2.23", "4.7 GB", "176k"], ["Newton", "32,768", "—", "OOM", "—"]]
put("n-train", slide("n-train", head("Isaac Lab + Newton · Microduck-Walk-Flat-Newton", "เทรนบน Newton: เป็ด 16,384 ตัวในการ์ด 6 GB"),
    think("<b>ไม่ใช่การเทียบแบบยุติธรรม 100%</b>: mjlab ของ Pollen มีโมเดลมอเตอร์ BAM, DR หลายชั้น และ reward ชุดใหญ่กว่า — ของเราเป็น PD ธรรมดา + reward สูตร G1 13 เทอม ส่วนต่างความเร็วจึงมาจากทั้ง engine และงานที่น้อยกว่า"),
    row=[f'<div style="flex:1;display:flex;flex-direction:column;gap:24px">' + table(scale, ["ซิม", "envs", "s/iter", "VRAM", "steps/s"], size=27, hi=2)
         + p("obs 61 มิติลำดับเดียวกับ Pollen · action = default + 1.0×a · PD kp 0.55 ±0.96 Nm · MuJoCo contacts · 50 Hz", 27, "#4A5563") + '</div>',
         f'<img src="{NSCALE}" alt="Env steps per second: mjlab 33k at 4096 envs; Newton 63k, 133k, 158k, 176k at 1k to 16k envs" style="width:800px;height:470px;object-fit:contain;border-radius:20px">'],
    at=1), "2,000 iterations ที่ 4,096 envs ใช้ 25 นาที (mjlab 1 ชม. 38 นาที) ไฟล์ task: newton_port/isaaclab_task/microduck_tasks.py รันจาก ~/IsaacLab ด้วย train.py ... physics=newton_mjwarp")

vslide("n-progress", "Training replay · checkpoints", "ระหว่างเทรน: จากล้มทั้งหมด สู่เดินพร้อมกัน", "progress",
       "Three panels of 25 ducks each: iteration 0 all fall, iteration 250 wobbly walk, iteration 2000 steady walk",
       "รัน checkpoint ของ run เดียวกันที่ iteration 0 · 250 · 2,000 อย่างละ 25 ตัว สั่ง 0.3 m/s — ที่ iteration 0 (policy สุ่ม) ล้มทุกตัวภายในวินาทีแรก", 560,
       "ภาพนี้คือการ replay checkpoint บน Newton ไม่ใช่ภาพสดระหว่างเทรน (Isaac Lab ตอนเทรนรันแบบ headless ไม่มี viewer)")

put("ex62", slide("ex62", head("Exercise 6.2 · Train on Newton, test on MuJoCo", "เทรนบน Newton แล้วเอาไปเดินใน MuJoCo", "6.2"),
    code(f'{G} cd ~/IsaacLab && LATENCY_DR=0 uv run python ~/repos/microduck_rl/newton_port/isaaclab_task/train.py \\<br>{SP}--task Microduck-Walk-Flat-Newton --num_envs 4096 physics=newton_mjwarp agent.max_iterations=2000<br>'
         f'{G} .venv/bin/python newton_port/ckpt2onnx.py &lt;run&gt;/model_1999.pt exports/newton_walk_2000.onnx<br>'
         f'{G} uv run scripts/infer_policy.py --walking exports/newton_walk_2000.onnx --new-cmd-obs --lin-vel-x 0.3', 25),
    row=[task(["เทรน 2,000 iterations (25 นาที) — ดู error_vel_xy ระหว่างเทรน",
               "รันใน Newton ด้วย PD แบบเดียวกับตอนเทรน (<b>--pd-kd 0.053</b>) และแบบ MJCF (kd = 0)",
               "รันใน MuJoCo CPU ทั้ง BAM และ --no-bam (มันไม่เคยเห็น BAM)",
               "สั่ง 0.1 ได้ไหม? สั่ง 0.4 ล้มไหม?"]),
         result(bigrow(big("0.40", "m/s ที่ cmd 0.4 · Newton motor ตรง"), big("0.26", "m/s ถ้า kd = 0", "#B85C00")) + p("motor model ต่างกันแค่ D-gain 0.053 ความเร็วสูงสุดหายไป 35% และเริ่มล้ม", 28))],
    at=2))

put("ans62", answer("ans62", "6.2", "ก่อนโทษ latency ให้เช็กโมเดลมอเตอร์ก่อน",
    ["ใน Newton ที่ตั้ง PD ให้ตรงกับตอนเทรน (kp 0.55, <b>kd 0.053</b>) เดินตามคำสั่งเป๊ะ: 0.1→0.10, 0.2→0.20, 0.3→0.31, 0.4→0.40 — ตรงกับ error 0.03 ตอนเทรน",
     "รอบแรกผมวัดได้แค่ ~0.26 และล้มเกือบครึ่งที่ 0.4 แล้วสรุปว่าเป็นเพราะ gyro ช้า 5 ms — <b>ผิด</b>: ตัวการคือ runner ใช้ position actuator ของ MJCF ที่ไม่มี D-term (kv = 0)",
     "MuJoCo CPU ก็ใช้ actuator kv = 0 เหมือนกัน: cmd 0.1–0.3 เดินได้ทั้ง BAM / no-BAM (0.13–0.28) แต่ cmd 0.4 แบบ no-BAM ล้มหลัง 4 s",
     "ความต่างที่ดูเล็กที่สุดใน config (kd 0.053 Nm·s/rad) ให้ผลใหญ่กว่า latency ทั้งหมด — ต้อง<b>ไล่ actuator ให้ตรงก่อน</b>ทุกครั้ง"],
    side=table([["0.1", "0.10", "0.13", "0.13", "0.15"], ["0.2", "0.20", "0.23", "0.26", "0.25"], ["0.3", "0.31", "0.25", "0.28", "0.26"],
                ["0.4", "0.40", "0.23 · ล้ม 47%", "0.30", "ล้ม"]], ["cmd", "Newton kd .053", "Newton kd 0", "CPU+BAM", "CPU no-BAM"], size=24)
         + p("Newton ทั้งสองคอลัมน์ใช้ gyro ช้า 1 substep แบบ MuJoCo", 24, "#4A5563"),
    summary="ผมแก้ข้อสรุปนี้หลังวัดซ้ำ — ตัวเลขชุดแรกถูก แต่คำอธิบายผิด เพราะยังไม่ได้เทียบ actuator", side_w=900),
    "Newton kd .053 ที่ cmd 0.1 แบบ gyro ไม่ช้ามีเป็ดล้ม 36/256 ตัว (แบบ gyro ช้า 0 ตัว) ยังไม่ได้หาสาเหตุ")

put("ex63", slide("ex63", head("Exercise 6.3 · Latency DR", "ใส่ความหน่วงแบบหุ่นจริง แล้วเทรนใหม่", "6.3"),
    code(f'{C("# microduck_tasks.py (LATENCY_DR=1) — ค่าเดียวกับ mjlab ของ Pollen")}<br>'
         f'servos = DelayedPDActuatorCfg(stiffness=0.55, damping=0.053, min_delay=<b>3</b>, max_delay=<b>6</b>){SP}{C("# 15–30 ms")}<br>'
         f'base_ang_vel = delayed(mdp.base_ang_vel, <b>0, 1</b>, update_period=64){SP}{C("# IMU 0–20 ms")}<br>'
         f'joint_vel{SP}= delayed(mdp.joint_vel_rel, <b>1, 1</b>, update_period=0){SP}{SP}{C("# firmware Dynamixel")}', 25),
    row=[task(["เพิ่ม 3 ความหน่วง แล้วยืนยันว่าทำงาน (<b>latency_check.py</b>)",
               "เทรนใหม่ 2,000 iterations (27 นาที)",
               "ทดสอบ 4 เงื่อนไข × 4 ความเร็ว × 256 ตัว เทียบกับตัวเดิม",
               "แลกอะไรไปบ้าง?"]),
         result(bigrow(big("684", "ตัวเดิมล้ม / 1,024 (หน่วงเต็ม)", "#B85C00"), big("0", "ตัวใหม่ล้ม / 1,024")) + p("หน่วงเต็ม = มอเตอร์ 30 ms + gyro ช้า + joint vel ช้า 1 step", 28))],
    at=2), "latency_check.py: joint vel ใน obs = ค่า step ก่อน 98% (อีก 2% คือ env ที่เพิ่ง reset), gyro = ปัจจุบัน/ก่อนหน้า ~50/50, actuator delay สุ่ม 3–6")

lat = [["ไม่มีหน่วง", "36", "0.31", "0", "0.38"], ["gyro ช้า 5 ms", "0", "0.31", "0", "0.31"],
       ["มอเตอร์ 15 ms", "0", "0.28", "0", "0.31"], ["มอเตอร์ 30 ms + IMU + joint vel", "684", "0.22*", "0", "0.29"]]
put("ans63", answer("ans63", "6.3", "ความทนทานต้องใส่เข้าไปตอนเทรน",
    ["ตัวเดิมรอดเมื่อหน่วงน้อย (gyro 5 ms, มอเตอร์ 15 ms — ล้ม 0) แต่พอหน่วงเต็มแบบที่ Pollen ใช้ <b>ล้ม 684 / 1,024</b> — ที่ cmd 0.4 ล้มหมด",
     "ตัวใหม่<b>ไม่ล้มเลย</b>ทุกเงื่อนไข ทุกความเร็ว (4 × 1,024 ตัว)",
     "ราคาที่จ่าย: error ตอนเทรน 0.033 → 0.042 และที่ cmd 0.1 เดินช้ากว่าคำสั่ง (0.06–0.10)",
     "ใน MuJoCo CPU ตัวใหม่ไม่ล้ม แต่<b>เดินเร็วเกินคำสั่ง</b> (สั่ง 0.3 ได้ 0.40 กับ BAM, 0.45 no-BAM) — ยังไม่ได้หาสาเหตุ"],
    side=video("latency", "Left: ducks without latency DR fall under full delay; right: ducks with latency DR keep walking", 820, 300)
         + table(lat, ["เงื่อนไข (Newton)", "ล้ม เดิม", "cmd .3 เดิม", "ล้ม ใหม่", "cmd .3 ใหม่"], size=24)
         + p("ล้ม = รวม 4 ความเร็ว จาก 1,024 ตัว · 36 ตัวของ “ไม่มีหน่วง” ล้มที่ cmd 0.1 · * เฉลี่ยจากตัวที่ยังไม่ล้ม", 24, "#4A5563"),
    summary="latency DR ไม่ได้ทำให้เดินดีขึ้นในซิมที่สะอาด — มันทำให้ <b>ไม่พัง</b> เมื่อโลกไม่ตรงกับซิม", side_w=900))

vslide("n-play", "Newton · follow cam", "policy สุดท้าย: Newton-trained + latency DR", "follow",
       "Side view following one Microduck walking at 0.3 m/s",
       "exports/newton_latency_2000.onnx · cmd 0.3 m/s ได้จริง 0.31 · ไฟล์เดียวกันนี้รันใน infer_policy.py ของ Pollen ได้ทันที (obs 61 มิติ)", 640)

ideas = [("เป็ดลาดตระเวน", "เดินตาม waypoint ใน <b>scene_apartment.xml</b> 6 ห้อง หลบเฟอร์นิเจอร์ แล้วกลับแท่นชาร์จ"),
         ("แข่งวิ่งด่าน", "ทีมละด่าน แลกกันวิ่ง นับเวลา + จำนวนล้ม ใน 5 จุดเริ่ม — ด่านที่ policy ทุกตัวผ่านได้แต่ช้าที่สุดชนะ"),
         ("ท่าเต้นตามเพลง", "แปลง beat ของเพลงเป็น keyframe — ให้คะแนนจาก RMS error และไม่ล้ม"),
         ("ฟุตบอล 1 ต่อ 0", "บอลกลิ้งอยู่ ต้องดักก่อนเตะ — ต่อยอด ctl_soccer.py ด้วยการทำนายตำแหน่งบอลล่วงหน้า")]
cards = "".join(card(t, p(d, 34)) for t, d in ideas[:2])
cards2 = "".join(card(t, p(d, 34)) for t, d in ideas[2:])
put("projects", slide("projects", head("ปลายภาค · ทำในซิมล้วน", "ไอเดียโปรเจกต์ที่ไม่ต้องมีหุ่น"),
    f'<div style="flex:1;display:flex;flex-direction:row;gap:32px">{cards}</div>',
    f'<div style="flex:1;display:flex;flex-direction:row;gap:32px">{cards2}</div>',
    at=1), "ทุกข้อใช้ sim_play.py + controller ไฟล์เดียว ส่งงานเป็นไฟล์ ctl_*.py ให้ผู้สอนรันซ้ำได้")

put("next", f'''<section id="next" data-transition="fade" style="{NAVY};padding:128px;display:flex;flex-direction:row;gap:64px;align-items:center">
<div style="flex:1;display:flex;flex-direction:column;gap:32px">
<p style="font-size:24px;letter-spacing:3px;text-transform:uppercase;color:#7AC943;font-weight:600">Next · Module 7</p>
<h1 style="{H};font-size:100px;font-weight:600;line-height:1.05;color:#F4F3EE">เมื่อหุ่นจริงมาถึง</h1>
<p style="font-size:36px;color:#B8C4D0;line-height:1.45">Module 7 เปิดโมเดลมอเตอร์ BAM: วัด XL330 บน test bench แล้ว fit แรงเสียดทานและแรงดันเอง — ต่อด้วย deploy ผ่าน robotd</p>
<div style="display:flex;flex-direction:row;gap:16px">
<p style="font-size:26px;background:#7AC943;color:#0E1621;padding:10px 22px;border-radius:40px;font-weight:600">xl330_test_bench</p>
<p style="font-size:26px;border:2px solid #3A4A5C;color:#B8C4D0;padding:8px 22px;border-radius:40px">Rhoban BAM</p>
<p style="font-size:26px;border:2px solid #3A4A5C;color:#B8C4D0;padding:8px 22px;border-radius:40px">robotctl policy add</p>
</div></div>
<img src="{SIDE}" alt="Microduck side view" style="width:560px;height:760px;object-fit:cover;border-radius:24px">
</section>''')

OUT = sys.argv[1]
only = sys.argv[2:] or order
os.makedirs(f"{OUT}/project/slides", exist_ok=True)
for sid in only:
    open(f"{OUT}/project/slides/{sid}.html", "w").write(slides[sid])
json.dump(order, open(f"{OUT}/order.json", "w"))
print("wrote", len(only), "slides")
