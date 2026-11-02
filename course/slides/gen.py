"""Microduck RL deck — Module 1–2 content slides (W1–3 design system)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from lib import H, M, SEC, head, code, task, result, think, table, slide, divider

OUT = sys.argv[1]
HERO = "/_blob/3cfc6bf6ce44cdca778ccea5503a45bb"
SIDE = "/_blob/420f44741f72e5eccf694b34398aec0d"
FRONT = "/_blob/c6ccef2541839e88a07110a3a6676154"
NAVY = "background:#0E1621;color:#F4F3EE;font-family:'IBM Plex Sans Thai', Arial, sans-serif"
G = '<span style="color:#7AC943">$</span>'
C = lambda t: f'<span style="color:#7A8492">{t}</span>'
SP = "&#160;" * 4

slides = {}


def put(sid, html, notes=None):
    if notes:
        html = html.rstrip()
        assert html.endswith("</section>")
        html = html[: -len("</section>")] + f"<aside>{notes}</aside></section>\n"
    slides[sid] = html


def p(t, size=33, color="#1B2430", extra=""):
    return f'<p style="font-size:{size}px;color:{color};line-height:1.45{extra}">{t}</p>'


def card(title, body, bg="#FBFAF6", border="1px solid #DDDBD2", tcolor="#0E1621"):
    return (f'<div style="flex:1;background:{bg};border:{border};border-radius:24px;padding:40px 44px;display:flex;flex-direction:column;gap:22px">'
            f'<h3 style="{H};font-size:44px;font-weight:600;color:{tcolor};line-height:1.15">{title}</h3>{body}</div>')


def section(sid, eyebrow, title, sub, img, alt):
    return (f'<section id="{sid}" data-transition="fade" style="{NAVY};padding:128px;display:flex;flex-direction:row;gap:64px;align-items:center">'
            f'<div style="flex:1;display:flex;flex-direction:column;gap:28px">'
            f'<p style="font-size:24px;letter-spacing:3px;text-transform:uppercase;color:#7AC943;font-weight:600">{eyebrow}</p>'
            f'<h1 style="{H};font-size:110px;font-weight:600;line-height:1.05;color:#F4F3EE">{title}</h1>'
            f'<p style="font-size:36px;color:#B8C4D0;line-height:1.4">{sub}</p></div>'
            f'<img src="{img}" alt="{alt}" style="width:620px;height:760px;object-fit:cover;border-radius:24px"></section>\n')


# ---------------------------------------------------------------- cover / agenda
put("cover", f'''<section id="cover" data-transition="fade" style="{NAVY};padding:128px;display:flex;flex-direction:row;gap:72px;align-items:center">
<div style="flex:1;display:flex;flex-direction:column;gap:28px">
<p style="font-size:24px;letter-spacing:3px;text-transform:uppercase;color:#7AC943">Engineering Workshop · mjlab + MuJoCo Warp</p>
<h1 style="{H};font-size:120px;font-weight:600;line-height:1.02;color:#F4F3EE">Microduck RL</h1>
<p style="font-size:40px;color:#B8C4D0;line-height:1.4">Module 1–2 — จากซิมสู่ reward ที่เป็ดเข้าใจ</p>
<div style="display:flex;flex-direction:row;gap:16px">
<p style="font-size:24px;background:#7AC943;color:#0E1621;padding:10px 22px;border-radius:40px;font-weight:600">RL → Sim-to-Real</p>
<p style="font-size:24px;border:2px solid #3A4A5C;color:#B8C4D0;padding:8px 22px;border-radius:40px">2026 edition</p>
</div>
<p style="font-size:28px;color:#B8C4D0;line-height:1.5">Pannatorn Bongkotamphon<br>Dr. Sukhum Sattaratnamai</p>
</div>
<img src="{HERO}" alt="Microduck robot model rendered in MuJoCo" style="width:720px;height:820px;object-fit:cover;border-radius:24px">
</section>''', "หลักสูตร Microduck: Module 1 ตั้งค่าซิมและเทรนเดินได้ภายในคาบ, Module 2 เปิดฝากระโปรงดู PPO และ reward ทุกตัว ทุกตัวเลขในเด็คนี้วัดจริงบน RTX 3060 Laptop 6 GB")

agenda_items = [
    ("01", "Meet Microduck · ทำไมต้องเป็ด", "#3D7A12"),
    ("02", "Module 1 · ติดตั้ง เทรน export ONNX", "#3D7A12"),
    ("03", "Module 2 · PPO, observation 61 มิติ, reward", "#3D7A12"),
    ("04", "กฎ reward ที่ทีม Pollen เรียนมาแบบเจ็บตัว", "#3D7A12"),
    ("05", "Exercises 4 ข้อ + เฉลย", "#B85C00"),
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
<p style="font-size:28px;letter-spacing:4px;text-transform:uppercase;color:#3D7A12;font-weight:600">Module 1–2</p>
<h2 style="{H};font-size:120px;font-weight:600;line-height:1;color:#0E1621">Agenda</h2>
</div>
<img src="{FRONT}" alt="Microduck front view" style="width:520px;height:480px;object-fit:cover;border-radius:24px">
</div>
<div style="flex:1;display:flex;flex-direction:column;justify-content:space-between">{rows}</div>
</section>''')

# ---------------------------------------------------------------- meet
lineage = "".join(
    f'<div style="flex:1;background:{bg};border-radius:24px;padding:36px 36px;display:flex;flex-direction:column;gap:14px">'
    f'<p style="{H};font-size:56px;font-weight:600;color:{yc};line-height:1">{y}</p>'
    f'<h3 style="{H};font-size:40px;font-weight:600;color:{tc};line-height:1.15">{t}</h3>'
    f'<p style="font-size:28px;color:{bc};line-height:1.45">{b}</p></div>'
    for y, t, b, bg, yc, tc, bc in [
        ("2023", "Disney BDX", "หุ่นสองขาตัวละครจาก Disney Research เดินด้วย RL + ท่าที่แอนิเมเตอร์ออกแบบ — ปิดซอร์ส", "#FBFAF6", "#7A8492", "#0E1621", "#4A5563"),
        ("2024–25", "Open Duck Mini v2", "โปรเจกต์ชุมชน สูง ~42 cm ปริ้นท์ 3D เอง BOM &lt; $400 · ใช้ BAM แล้วย้ายไป MuJoCo Playground", "#FBFAF6", "#7A8492", "#0E1621", "#4A5563"),
        ("2026", "Microduck", "Pollen Robotics + Hugging Face · 25 cm · $399 · ซอฟต์แวร์ Apache-2.0 ทั้งสแตก", "#0E1621", "#7AC943", "#F4F3EE", "#B8C4D0"),
    ])
put("lineage", slide("lineage", head("Why a duck", "สายพันธุ์เป็ด: จากดิสนีย์ถึงโต๊ะเรา"),
                     f'<div style="flex:1;display:flex;flex-direction:row;gap:32px">{lineage}</div>',
                     think("เป็ดเล็ก = ล้มไม่พัง เทรนเร็ว (14 ข้อต่อ) และเปิดหมดตั้งแต่ reward ถึง runtime — ครบที่สุดสำหรับสอน sim-to-real"), at=1),
    "เล่าสั้นๆ ว่า BDX เป็นแรงบันดาลใจ, Open Duck Mini คือเวอร์ชันชุมชนที่ฮาร์ดแวร์เปิด, Microduck คือเวอร์ชันสำเร็จรูปที่ซอฟต์แวร์เปิดแต่ไฟล์ฮาร์ดแวร์ไม่เปิด")

spec_rows = [
    ["ขนาด / น้ำหนัก", "25 × 14 cm · ไม่ถึง 800 g (โมเดลซิม 0.737 kg)"],
    ["มอเตอร์", "15 ตัว · Dynamixel XL330 · RL คุม 14 ข้อต่อ"],
    ["คอมพิวเตอร์", "Rockchip RK3566 + AI accelerator · RAM 1 GB"],
    ["เซนเซอร์", "IMU ×2 · กล้องหน้า · ToF 8×8 · ไมค์ ลำโพง NFC"],
    ["แบตเตอรี่", "NP-F550 2600 mAh · ~1 ชม. (ตัวเลขผู้ผลิต)"],
    ["ราคา / ส่ง", "$399 · ล็อตแรกก่อนคริสต์มาส 2026 · NA/EU/UK"],
]
put("specs", slide("specs", head("Hardware", "Microduck ในตัวเลข"),
                   row=[table(spec_rows, ["หัวข้อ", "สเปก"], size=30),
                        f'<div style="width:560px;display:flex;flex-direction:column"><img src="{SIDE}" alt="Microduck side view" style="width:560px;height:100%;object-fit:cover;border-radius:24px"></div>'],
                   at=1),
    "สเปกจาก press kit ของ Pollen (ดึงข้อมูล 2 พ.ย. 2026) — กล้อง LiDAR และวิทยุบางตัวยังเขียนว่าไม่ final; ประเทศไทยยังไม่อยู่ในพื้นที่จัดส่ง")

# pipeline diagram
def box(x, y, w, h, title, sub, bg="#FBFAF6", tc="#0E1621", sc="#4A5563", border="2px solid #DDDBD2"):
    return (f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{bg};border:{border};border-radius:20px;padding:24px 28px;display:flex;flex-direction:column;gap:8px">'
            f'<h3 style="{H};font-size:38px;font-weight:600;color:{tc};line-height:1.1">{title}</h3>'
            f'<p style="font-size:26px;color:{sc};line-height:1.4">{sub}</p></div>')
pipe = (box(112, 380, 380, 300, "Train", "mjlab · MuJoCo Warp<br>rsl_rl PPO · 4096 envs<br>GPU ของเรา / HF Jobs", "#E6F2DA", "#1F4D06", "#1B2430", "2px solid #7AC943")
        + box(552, 380, 380, 300, "Export", "scripts/export.py<br>ONNX [1,61]→[1,14]<br>normalizer ฝังในไฟล์")
        + box(992, 380, 380, 300, "Publish", "uv run publish<br>HF Hub repo<br>policy.onnx + manifest")
        + box(1432, 380, 376, 300, "Robot", "robotd (Rust) 50 Hz<br>RK3566<br>robotctl policy add", "#0E1621", "#F4F3EE", "#B8C4D0", "2px solid #0E1621")
        + "".join(f'<x-connector x1="{a}" y1="530" x2="{a+60}" y2="530" head="end" style="color:#B85C00;border-width:5px"></x-connector>' for a in (492, 932, 1372))
        + f'<div style="position:absolute;left:112px;top:740px;width:1696px;background:#FBEBDD;border-left:8px solid #B85C00;border-radius:16px;padding:24px 36px"><p style="font-size:30px;color:#1B2430"><b style="color:#B85C00">ซ้อมก่อนลงหุ่น:</b> scripts/infer_policy.py รัน ONNX ตัวเดียวกันใน MuJoCo บน CPU พร้อมโมเดลมอเตอร์ BAM — Module 1 จบที่ขั้นนี้</p></div>')
put("pipeline", f'''<section id="pipeline" data-transition="fade" style="{SEC};padding:100px 112px 90px;display:flex;flex-direction:column;gap:32px">
{head("The stack", "จาก GPU ถึงขาเป็ด: 4 ขั้น")}
{pipe}
</section>''', "ทั้งสแตกเปิดซอร์ส: microduck_rl (เทรน) และ microduck (runtime Rust) — policy ทุกตัวใช้สัญญาข้อมูล 61→14 เดียวกันจึงสลับกันได้")

# ---------------------------------------------------------------- Module 1
put("sec-m1", section("sec-m1", "Module 1", "ซิมก่อนจับหุ่น", "ติดตั้ง mjlab, เทรนให้เป็ดเดินบน GPU 6 GB, export เป็น ONNX แล้วซ้อมบน CPU", HERO, "Microduck in MuJoCo"))

put("install", slide("install", head("Setup · 1 คำสั่ง", "ติดตั้ง microduck_rl"),
    code(f'{G} git clone https://github.com/pollen-robotics/microduck_rl.git<br>{G} cd microduck_rl &amp;&amp; uv sync<br>{G} uv run list-envs {C("# 45 tasks: MicroDuck + Cartpole, G1, Go1, Yam")}'),
    think("mjlab = Isaac Lab-style API บน MuJoCo Warp — คนที่ผ่าน W1–3 จะเจอ ManagerBasedRlEnvCfg, RewardTermCfg หน้าตาคุ้นเคย"),
    row=[result(p("Python 3.12 · mjlab 1.3.0 · warp-lang 1.12.0 · torch 2.9.1 — ล็อกเวอร์ชันใน uv.lock") +
                p("ต้องมี GPU CUDA (MuJoCo Warp) · ไม่มี GPU → เติม <b>--hf-jobs</b> ไปเทรนบน Hugging Face Jobs")),
         card("ไม่ต้องติดตั้ง", p("Isaac Sim, ROS, conda — ไม่ต้องเลย") + p("ไม่ต้องล็อกอิน wandb ถ้าใช้ <b>--agent.logger tensorboard</b>"))],
    at=2), "ทดสอบบนเครื่องจริง 2 พ.ย. 2026: uv sync ผ่านรวดเดียว ไม่ต้องติดตั้งอะไรเพิ่ม")

joints = [["0–4", "ขาซ้าย", "hip_yaw · hip_roll · hip_pitch · knee · ankle"],
          ["5–8", "คอ / หัว", "neck_pitch · head_pitch · head_yaw · head_roll"],
          ["9–13", "ขาขวา", "hip_yaw · hip_roll · hip_pitch · knee · ankle"]]
put("robot", slide("robot", head("Robot model", "14 ข้อต่อที่ policy คุม"),
    row=[f'<div style="flex:1;display:flex;flex-direction:column;gap:28px">{table(joints, ["index", "ส่วน", "ข้อต่อ"], size=28)}'
         + p("MJCF export จาก Onshape ด้วย onshape-to-robot · ซิมรุ่น walk ให้ชนพื้นแค่เท้า (เร็ว)") +
         think("ทำไมหัว 4 ข้อต่อถึงอยู่ใน policy เดิน? หัวหนัก ~38% ของตัว — ขยับหัวเปลี่ยนสมดุลทั้งตัว") + '</div>',
         f'<div style="width:520px;display:flex;flex-direction:column"><img src="{FRONT}" alt="Microduck front view" style="width:520px;height:100%;object-fit:cover;border-radius:24px"></div>'],
    at=1), "เลข index สำคัญมาก เพราะ ONNX ส่ง action 14 ตัวตามลำดับนี้ AGENTS.md ระบุว่าหัวหนัก 38% ของมวล")

put("smoke", slide("smoke", head("Rule #1", "Smoke test ก่อนเทรนยาวเสมอ"),
    code(f'{G} uv run train Mjlab-Velocity-Flat-MicroDuck \\<br>{SP}--env.scene.num-envs 64 --agent.max-iterations 5 --agent.logger tensorboard'),
    think("เทรนยาว 2 ชม. แล้วพังที่ export = เสียทั้งคาบ · smoke test ใช้ไม่ถึง 1 นาที"),
    row=[card("ทำไม", p("“5 iterations ที่ 64 envs จับ config error ได้ ~95% ในราคาไม่กี่สตางค์” — AGENTS.md") + p("เช็ก: build ได้ · ไม่มี NaN · obs = 61 มิติ · reward ทุกตัวคำนวณได้ · export ONNX ได้")),
         card("ข้อความแรกที่จะเห็น", f'<p style="{M};font-size:24px;color:#1B2430;line-height:1.6">[mdp] Patches 1-2 active: NaN-safe reward/advantage<br>[mdp] Patch 4 active: ONNX export filters passive_* joints<br>[mdp] Patch 5 active: MICRODUCK_WARM_START=1 ...</p>' + p("ปกติ — เป็น patch ของ repo ไม่ใช่ error", 26, "#4A5563"))],
    at=2))

put("train", slide("train", head("Train", "เทรนท่าเดิน 4096 ตัวพร้อมกัน"),
    code(f'{G} uv run train Mjlab-Velocity-Flat-MicroDuck \\<br>{SP}--env.scene.num-envs 4096 --agent.max-iterations 2000 \\<br>{SP}--agent.save-interval 250 --agent.logger tensorboard'),
    row=[result(f'<div style="display:flex;flex-direction:row;gap:48px"><div><p style="{H};font-size:72px;font-weight:600;color:#1F4D06;line-height:1">4.99 GB</p>{p("VRAM สูงสุด จาก 6 GB", 26)}</div><div><p style="{H};font-size:72px;font-weight:600;color:#1F4D06;line-height:1">~3.0 s</p>{p("ต่อ iteration · GPU 92%", 26)}</div></div>'
                + p("1 iteration = 4096 envs × 24 steps = 98,304 transitions")),
         card("อ่าน flag", p("<b>num-envs</b> หุ่นที่จำลองพร้อมกัน") + p("<b>max-iterations</b> รอบอัปเดต PPO") + p("<b>save-interval</b> เซฟ model_N.pt ทุก N รอบ") + p("log อยู่ที่ logs/rsl_rl/velocity/&lt;วันเวลา&gt;/", 26, "#4A5563"))],
    at=2), "ค่าเริ่มต้นของ task คือ 50,000 iterations — ต้องตั้ง max-iterations เอง AGENTS.md บอกว่าท่าเดินจริงจังใช้ 4000–6000")

log_rows = [["Mean reward", "ผลรวม reward ต่อ episode", "ควรขึ้น"],
            ["Episode_Termination/fell_over", "จำนวน episode ที่จบเพราะล้ม (ต่อรอบ log)", "ควรลงเกือบ 0"],
            ["Episode_Termination/time_out", "อยู่รอดครบ 20 s", "ควรขึ้น"],
            ["Metrics/twist/error_vel_xy", "ความเร็วจริงพลาดจากคำสั่ง (m/s)", "ควรลง"],
            ["Episode_Reward/&lt;penalty&gt;", "ค่า penalty ถ่วงน้ำหนักแล้ว", "ต้อง ≤ 0 เสมอ"],
            ["Curriculum/*", "ความยากที่ปรับตามรอบ", "ขึ้นเป็นขั้น"]]
put("log", slide("log", head("Read the log", "ดู 6 บรรทัดนี้ก่อน"),
    table(log_rows, ["บรรทัดใน log", "หมายถึง", "ทิศที่ดี"], size=28),
    think("Mean reward ขึ้นอย่างเดียวไม่พอ — reward รวมอาจขึ้นจาก regularizer ทั้งที่เป็ดยังไม่เดิน ให้ดู term หลักด้วย"), at=1))

put("export", slide("export", head("Export", "Checkpoint → ONNX ทางเดียวที่ปลอดภัย"),
    code(f'{G} uv run scripts/export.py Mjlab-Velocity-Flat-MicroDuck \\<br>{SP}--checkpoint-file logs/rsl_rl/velocity/&lt;run&gt;/model_1999.pt'),
    think("ใน play เดินสวย ≠ ONNX ถูก — ตรวจด้วย infer_policy เสมอ (หน้าถัดไป)"),
    row=[card("ทำไมห้ามแปลงเอง", p("observation ถูก normalize ตอนเทรน — export.py <b>ฝัง normalizer ลงใน ONNX</b>") + p("ใน play จะไม่เห็นบั๊กนี้ เพราะ play ใช้ normalizer ให้อยู่แล้ว แต่หุ่นจริงจะเดินมั่ว")),
         card("สัญญาข้อมูล", f'<p style="{M};font-size:30px;color:#0E1621">input&#160;&#160;[1, 61]<br>output [1, 14]</p>' + p("metadata ใน ONNX: run_path, task_id, checkpoint, sha256 — สืบย้อนได้ว่ามาจากรอบไหน"))],
    at=2), "--checkpoint-file ใช้ได้กับไฟล์ในเครื่อง ไม่ต้องใช้ wandb")

put("infer", slide("infer", head("Rehearse", "ซ้อมบน CPU ด้วย ONNX ตัวจริง"),
    code(f'{G} uv run scripts/infer_policy.py --walking policy.onnx<br>{C("# MuJoCo บน CPU + โมเดลมอเตอร์ BAM เหมือนตอนเทรน · --no-bam = PD ธรรมดา")}'),
    think("เดินได้ใน Warp แต่ล้มใน MuJoCo CPU = สัญญาณเตือน อย่าเพิ่งเอาไปลงหุ่นจริง"),
    row=[card("ทำไมต้องซ้อม", p("เป็น <b>sim-to-sim</b>: ต่างตัวจำลอง (Warp → CPU) แต่ ONNX ตัวเดียวกับที่จะลงหุ่น") + p("พิมพ์ความเร็วเฉลี่ยจริงเทียบคำสั่งทุก 1 s")),
         card("คุมด้วยคีย์บอร์ด", p("พิมพ์ใน <b>terminal</b> ไม่ใช่หน้าต่าง viewer") + p("ตั้งความเร็วตรงๆ: --lin-vel-x 0.2 --ang-vel-z 0.5") + p("ทดสอบความหน่วง: --delay", 28, "#4A5563"))],
    at=2))

lab = "".join(
    f'<div style="background:#172231;border-left:8px solid {c};border-radius:16px;padding:30px 36px;display:flex;flex-direction:column;gap:8px">'
    f'<h3 style="{H};font-size:44px;font-weight:600;color:#F4F3EE">{t}</h3><p style="font-size:30px;color:#B8C4D0">{b}</p></div>'
    for t, b, c in [("1.1 · ติดตั้งผ่าน", "uv sync ผ่าน และ list-envs เห็น Mjlab-Velocity-Flat-MicroDuck", "#7AC943"),
                    ("1.2 · เทรนเดินได้", "fell_over ลงเกือบ 0 และมี model_*.pt ในโฟลเดอร์ log", "#7AC943"),
                    ("1.3 · ONNX เดินบน CPU", "export ได้ แล้ว infer_policy เดินตามคำสั่ง — ต่อด้วย Exercises", "#F2A65A")])
put("lab1", f'''<section id="lab1" data-transition="fade" style="{NAVY};padding:110px 112px 100px;display:flex;flex-direction:row;gap:64px">
<div style="flex:1;display:flex;flex-direction:column;justify-content:space-between">
<div style="display:flex;flex-direction:column;gap:16px">
<p style="font-size:28px;letter-spacing:4px;text-transform:uppercase;color:#7AC943;font-weight:600">Checkpoint · ก่อนไปต่อ</p>
<h2 style="{H};font-size:110px;font-weight:600;line-height:1.05;color:#F4F3EE">Lab 1 ผ่านไหม?</h2>
</div>{lab}</div>
<img src="{SIDE}" alt="Microduck side view" style="width:560px;height:870px;object-fit:cover;border-radius:28px">
</section>''')

# ---------------------------------------------------------------- Module 2
put("sec-m2", section("sec-m2", "Module 2", "PPO กับ reward ที่เป็ดเข้าใจ", "เปิดดู observation, action, PPO และ reward ทุกตัวใน microduck_velocity_env_cfg.py", SIDE, "Microduck side view"))

obs_seg = [("3", "ang_vel", "IMU gyro"), ("3", "gravity", "projected"), ("14", "joint_pos", "+ encoder bias"),
           ("14", "joint_vel", ""), ("14", "last_action", ""), ("13", "command", "twist · head · body")]
bar = "".join(
    f'<div style="flex:{int(n)};background:{"#0E1621" if k == "command" else "#1F4D06"};border-radius:12px;padding:20px 14px;display:flex;flex-direction:column;gap:6px;min-width:150px">'
    f'<p style="{H};font-size:44px;font-weight:600;color:{"#F2A65A" if k == "command" else "#B8E68F"};line-height:1">{n}</p>'
    f'<p style="{M};font-size:24px;color:#F4F3EE">{k}</p><p style="font-size:24px;color:#B8C4D0">{s}</p></div>'
    for n, k, s in obs_seg)
put("obs", slide("obs", head("Observation", "เป็ดเห็นอะไร: 48 + 13 = 61 มิติ"),
    f'<div style="display:flex;flex-direction:row;gap:12px">{bar}</div>',
    think("ไม่มี base_lin_vel ใน actor — หุ่นจริงวัดความเร็วลำตัวตรงๆ ไม่ได้ policy ต้องอนุมานเองจาก IMU + ขา"),
    row=[card("48 proprioception", p("ทุกอย่างวัดได้จากตัวหุ่นเอง: IMU + encoder + action ที่แล้ว") + p("ไม่มีกล้อง ไม่มีตำแหน่งในโลก — หุ่นจริงก็ไม่มี")),
         card("13 command", p("twist (vx, vy, ωz) · head_pose 4 · body_pose 6") + p("ทุก policy ในครอบครัวใช้ layout เดียวกัน ช่องที่ไม่ใช้ → <b>เติมศูนย์</b> ห้ามลบ"))],
    at=2), "ใน infer_policy.py มีบรรทัดตรวจ: 3 + 3 + 14×3 + 13 = 61 ถ้าไม่ตรงจะเตือน")

put("action", slide("action", head("Action", "เป็ดสั่งอะไร: มุมเป้าหมาย 14 ข้อต่อ"),
    code(f'target_q = HOME_pose + 1.0 × action{SP}{C("# scale = 1.0 rad, use_default_offset = True")}'),
    think("action = 0 แปลว่า “ยืนท่า HOME” → policy เรียนแค่ส่วนต่างจากท่ายืน จึงเริ่มต้นได้ไม่ล้มทันที"),
    row=[result(f'<div style="display:flex;flex-direction:row;gap:48px"><div><p style="{H};font-size:72px;font-weight:600;color:#1F4D06;line-height:1">50 Hz</p>{p("policy (0.005 s × decimation 4)", 26)}</div><div><p style="{H};font-size:72px;font-weight:600;color:#1F4D06;line-height:1">20 s</p>{p("ต่อ episode", 26)}</div></div>'
                + p("อ่านจาก logs/.../params/env.yaml ของรอบที่เทรนจริง"), "ค่าจริงจาก config"),
         card("ไม่มี filter", p("policy <b>ไม่</b> low-pass action ตอนเทรน") + p("ห้ามเติม EMA ตอน deploy ถ้าไม่ได้เทรนแบบนั้น — ต่างกันนิดเดียวก็ transfer พัง"))],
    at=2), "มอเตอร์ XL330 รับคำสั่งตำแหน่ง แต่ในซิมไม่ใช่ PD ธรรมดา — เป็น BAM ที่จำลองแรงดัน back-EMF และแรงเสียดทาน (Module 3)")

ppo_rows = [["clip_param", "0.2", "จำกัดการเปลี่ยน policy ต่อรอบ"],
            ["learning_rate", "1e-3 (adaptive, desired_kl 0.01)", "ปรับเองตาม KL"],
            ["gamma / lam", "0.99 / 0.95", "discount / GAE"],
            ["epochs × mini-batches", "5 × 4", "ใช้ข้อมูลแต่ละรอบซ้ำ"],
            ["entropy_coef", "0.01", "กันสำรวจหยุดเร็ว"],
            ["actor / critic", "MLP 512-256-128", "ทั้งสองตัว"]]
put("ppo", slide("ppo", head("PPO", "ค่าจริงใน RslRlOnPolicyRunnerCfg"),
    table(ppo_rows, ["พารามิเตอร์", "ค่า", "หน้าที่"], size=30),
    think("ค่าพวกนี้แทบไม่ต้องแตะ — ทีม Pollen ปรับ reward, curriculum และ randomization มากกว่า PPO"), at=1))

put("asym", slide("asym", head("Asymmetric actor-critic", "Critic โกงได้ Actor โกงไม่ได้"),
    think("กฎง่ายๆ: ข้อมูลไหนหุ่นจริงไม่มี → ใส่ได้เฉพาะ critic"),
    row=[card("Actor (ไปลงหุ่น)", p("เห็น 61 มิติแบบที่หุ่นจริงเห็น") + p("joint_pos <b>มี encoder bias</b> ±0.86°") + p("IMU <b>เอียงสุ่ม</b> ได้ถึง 6°"), "#FBFAF6"),
         card("Critic (ใช้แค่ตอนเทรน)", p("เห็น <b>base_lin_vel</b> — ความเร็วจริงของลำตัว ซึ่งหุ่นจริงวัดตรงๆ ไม่ได้") + p("joint_pos <b>ไม่มี</b> bias") + p("ไม่ถูก export จึงใช้ข้อมูลพิเศษได้เต็มที่"), "#E6F2DA", "none", "#1F4D06")],
    at=1, ), "นี่คือ privileged critic — ประเมินค่าได้แม่นขึ้นแต่ไม่ทำให้ policy พึ่งข้อมูลที่หุ่นจริงไม่มี")

rew_rows = [["track_linear_velocity", "+2.0", "เดินตามความเร็ว (Gaussian)"],
            ["track_angular_velocity", "+2.0", "หมุนตามคำสั่ง"],
            ["head_pose_tracking", "+2.0", "หัวไปตามคำสั่ง"],
            ["upright", "+2.0", "ลำตัวตั้งตรง"],
            ["air_time", "+3.0", "ก้าวเท้าค้าง 0.125–0.3 s"],
            ["pose", "+1.0", "ใกล้ท่ายืน HOME"],
            ["action_rate_l2", "−0.1 → −1.0", "สั่งกระตุก (มี curriculum)"],
            ["foot_slip · body_ang_vel · angular_momentum", "−0.1 · −0.05 · −0.02", "เท้าไถล / ตัวส่าย"],
            ["self_collisions", "−1.0", "ขาชนกันเอง"]]
put("rewards", slide("rewards", head("Reward stack", "Reward ของท่าเดิน (ย่อ)"),
    table(rew_rows, ["term", "weight", "ให้รางวัล / ลงโทษ"], size=26), at=1),
    "ยังมี foot_clearance, foot_swing_height (เป้า 2 cm), dof_pos_limits, head_pose_bias, body_pose_tracking (weight 0 เพื่อเลี้ยงช่อง obs ไว้) ดูได้ใน log ทุกบรรทัด Episode_Reward/")

put("gauss", slide("gauss", head("Tracking reward", "Gaussian: std คือ error ที่เรายังแคร์"),
    code(f'r = exp(−‖v_cmd − v‖² / std²){SP}{C("# track_linear_velocity: std² = 0.1")}', 32),
    row=[card("std กว้างไป", p("ไม่มี gradient ตอน error เล็ก → เดินพอประมาณก็ได้คะแนนเกือบเต็ม")),
         card("std แคบไป", p("ตัวอย่างจริงจาก repo: บีบ head tracking ให้แคบ (std 0.1) → policy <b>หยุดเดิน</b> ภายใน iteration 300") + p("หัวที่หนัก 38% ต้องแกว่งตอนเดิน — แคบไปเท่ากับลงโทษการเดิน", 28, "#4A5563")),
         card("upright แรงขึ้น", p("weight 1.0 / std² 0.1: เอียง 4° เสีย ~0.05/step = ฟรี") + p("weight 2.0 / std² 0.05: เสีย ~0.19/step = พอให้ตั้งตัว"))],
    at=2), "ตัวอย่างทั้งหมดมาจาก comment ใน microduck_velocity_env_cfg.py และ AGENTS.md")

cur_rows = [["0", "−0.1", "2%"], ["500", "−0.2", "5%"], ["750", "−0.4", "…"], ["1000", "−0.6", "…"], ["1250", "−0.8", "…"], ["1500", "−1.0", "…"]]
put("curriculum", slide("curriculum", head("Curriculum", "ภาษีความนุ่มนวล: เก็บทีหลัง"),
    row=[f'<div style="flex:1;display:flex;flex-direction:column;gap:24px">{table(cur_rows, ["iteration", "action_rate weight", "standing envs"], size=30)}</div>',
         card("หลักคิด", p("ช่วงแรกเป็ดยังเดินไม่เป็น ถ้าลงโทษความกระตุกหนัก “ยืนเฉยๆ” จะชนะ") + p("พอเดินได้แล้วค่อยขึ้นภาษี — ทำเป็น<b>ขั้น</b> ไม่ใช่เส้นตรง") + p("head_pose ก็ขยายช่วงทุก 500 iterations ถึง 2000") + think("ถ้ากราฟตกตรงขอบขั้น curriculum พอดี = เร่งเร็วไป"))],
    at=1), "1 iteration = 24 env steps ใน config จึงเขียน step = iteration × 24")

cmd_rows = [["lin_vel_x", "±0.4 m/s"], ["lin_vel_y", "±0.3 m/s"], ["ang_vel_z", "±1.0 rad/s"],
            ["หมุนกับที่", "15% ของ envs"], ["ยืนนิ่ง (คำสั่ง 0)", "2% → เพิ่มตาม curriculum"]]
put("commands", slide("commands", head("Commands", "ข้อมูลที่ไม่เคยเห็น = ทำไม่เป็น"),
    think("ถ้าอยากให้เป็ดทำอะไรตอน deploy ต้องแน่ใจว่ามันเห็นสถานการณ์นั้นพอตอนเทรน"),
    row=[table(cmd_rows, ["คำสั่ง", "ช่วง"], size=30),
         card("บทเรียนจากการ audit", p("สุ่ม vx, vy, ωz แยกกัน → หมุนกับที่มีแค่ ~2% ของข้อมูล → <b>ไม่เคยเทรน</b>") + p("สุ่มแบบ uniform แทบไม่มีวันได้คำสั่ง 0 พอดี ซึ่งคือสถานะตอนหุ่นจริงยืนรอ") + p("แก้ด้วยการแบ่ง bucket ชัดเจน", 28, "#4A5563"))],
    at=1), "ช่วงคำสั่งคงที่ ไม่มี curriculum ขยายช่วง เพราะเคยลองแล้วขยายเร็วกว่าที่หุ่นทำได้")

rules = [("Sign convention", "penalty บางตัวคืนค่าลบเองอยู่แล้ว ใส่ weight ลบซ้ำ = ให้รางวัลกับความผิด → ทุก Episode_Reward/&lt;penalty&gt; ต้อง ≤ 0"),
         ("RL ทำตามตัวอักษร", "อะไรที่ไม่ได้ระบุจะถูกโกง — กำหนดท่าด้วยเงื่อนไขสถานะ ไม่ใช่ penalty เล็กๆ"),
         ("ห้ามแจ็กพอต", "รางวัล “ถึงเป้า” ที่จ่ายทุก step = ซื้อความรุนแรง ให้ใช้เป้าที่เลื่อนช้าๆ"),
         ("อย่าจ่ายในสถานะแย่", "ให้รางวัลตอนล้ม/ต่ำ → policy นอนเก็บแต้ม ใช้ potential shaping จ่าย Δprogress")]
rule_html = "".join(
    f'<div style="display:flex;flex-direction:row;gap:28px;align-items:start;border-bottom:1px solid #DDDBD2;padding:0px 0px 18px 0px">'
    f'<p style="{H};font-size:40px;font-weight:600;color:#B85C00;width:60px;line-height:1.2">{i+1}</p>'
    f'<div style="flex:1;display:flex;flex-direction:column;gap:6px"><h3 style="{H};font-size:38px;font-weight:600;color:#0E1621">{t}</h3>{p(b, 28)}</div></div>'
    for i, (t, b) in enumerate(rules))
put("rules", slide("rules", head("Lessons · AGENTS.md", "กฎ reward ที่ทีม Pollen เรียนแบบเจ็บตัว"),
    f'<div style="flex:1;display:flex;flex-direction:column;justify-content:space-between">{rule_html}</div>', at=1),
    "ทุกข้อมีเหตุการณ์จริงใน repo: sign ผิดทำให้เป็ด 'butt-hop', ท่าม้วนกลายเป็นเหวี่ยง, ท่าลุกกลายเป็นใช้หัวค้ำ — Exercise 2.1 จะลองทำ sign ผิดเอง")

put("reading", slide("reading", head("Measure before theorizing", "เทรนพัง? วัดก่อนแก้"),
    row=[card("ทุก iteration ดู", p("reward รวมขึ้น <b>และ</b> episode length ไปตามที่งานต้องการ") + p("penalty ทุกตัว ≤ 0") + p("term หลักโตจริง ไม่ใช่โตแค่ regularizer")),
         card("ก่อนเปลี่ยน reward", p("รัน eval checkpoint จริงแบบ headless ก่อน") + p("หลายครั้งที่ “พัง” คือแค่ดู checkpoint ต้นเกินไป") + p("ดูวิดีโอด้วย — ตัวเลขผ่านแต่ตาคนไม่ผ่านก็มี")),
         card("รายงานแบบวิศวกร", p("“ม้วนได้แต่หน้าทิ่ม 1 ใน 3”") + p("ไม่ใช่ “ใช้ได้แล้ว!”", 30, "#B85C00") + p("ใครจะตัดสินว่าดีพอ = คนใช้งาน ไม่ใช่คนเทรน", 28, "#4A5563"))],
    at=1))

# ---------------------------------------------------------------- write
os.makedirs(f"{OUT}/project/slides", exist_ok=True)
for sid, html in slides.items():
    open(f"{OUT}/project/slides/{sid}.html", "w").write(html)
print("wrote", len(slides), sorted(slides))
