"""Microduck deck — measured slides: curve, exercises, answers, bridge. Usage: gen2.py <deck_root> [ids...]"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from lib import H, M, SEC, head, code, task, result, think, table, slide, divider, answer
from gen import put, slides, p, card, NAVY, G, C, SP, HERO, SIDE  # noqa: re-uses helpers (gen.py also writes its slides)

CURVE = "/_blob/c8fcd83ccdd9e54fc45d5a1531b04b25"
STRIP = "/_blob/c380d9836726264e4806a7b53de14433"
TRAJ = "/_blob/b788334c2ee2896f2cf8ca61ff6ee7e6"
RES = json.load(open(os.path.join(os.path.dirname(__file__), "results.json")))
new = {}


def put2(sid, html, notes=None):
    put(sid, html, notes)
    new[sid] = slides[sid]


def big(v, label, color="#1F4D06"):
    return f'<div><p style="{H};font-size:68px;font-weight:600;color:{color};line-height:1">{v}</p>{p(label, 26)}</div>'


def bigrow(*items):
    return f'<div style="display:flex;flex-direction:row;gap:44px">{"".join(items)}</div>'


# ---------------------------------------------------------------- curve
put2("curve", slide("curve", head("Our run · 2,000 iterations", "กราฟจริง: 1 ชม. 38 นาที บน 6 GB"),
    f'<img src="{CURVE}" alt="Training curves: mean reward rises to 120, episode length to 959 of 1000, falls drop to 0.2" style="width:1696px;height:509px;object-fit:contain;border-radius:20px">',
    think("reward <b>ตก</b> ตรง iteration 1000 และ 1500 พอดี — คือขั้นที่ action_rate weight ขึ้นเป็น −0.6 และ −1.0 (เส้นประส้ม) ไม่ใช่ policy แย่ลง แต่ภาษีแพงขึ้น"),
    at=1), "fell_over ใน log เป็นจำนวน episode ที่จบเพราะล้มในรอบ log ไม่ใช่สัดส่วน เริ่มที่ ~150 ลงเหลือ 0.2 ภายใน ~100 iterations")

# ---------------------------------------------------------------- exercises divider + bridge
put2("sec-ex", divider("sec-ex", "Exercises · Module 1–2", "ลองเอง วัดเอง", "4 ข้อ ทุกข้อมีผลวัดจริงบน RTX 3060 Laptop 6 GB และเฉลยสีเขียวตามหลัง"))

# ---------------------------------------------------------------- Ex 1.1
e = RES.get("ex11")
if e:
    rows = [[f'{r["n"]:,}', r["vram"], r["it"], r["tput"], r["note"]] for r in e["rows"]]
    put2("ex11", slide("ex11", head("Exercise 1.1 · Scaling", "เพิ่ม envs ได้ถึงเท่าไรก่อน 6 GB เต็ม?", "1.1"),
        code(f'{G} for n in 1024 2048 4096 8192; do<br>{SP}uv run train Mjlab-Velocity-Flat-MicroDuck --env.scene.num-envs $n \\<br>{SP}{SP}--agent.max-iterations 20 --agent.logger tensorboard; done'),
        think("เพิ่ม envs 2 เท่า เวลา/iteration เพิ่มเท่าไร? ถ้าเพิ่มไม่ถึง 2 เท่า = ยังมีงานต่อวินาทีเหลือให้ใช้"),
        row=[task(["รันทีละค่า เปิด <b>nvidia-smi -l 1</b> อีกหน้าต่าง จด VRAM สูงสุด",
                   "อ่าน <b>Iteration time</b> ใน log (ไม่นับ 3 รอบแรก)",
                   "คำนวณ throughput = envs × 24 / เวลาต่อ iteration",
                   "ค่าไหนคุ้มที่สุดสำหรับเครื่องนี้?"]),
             result(bigrow(big(e["best_tput"], "steps/s สูงสุด"), big(e["max_vram"], "VRAM สูงสุดที่วัดได้")) + p(e["headline"], 28))],
        at=2), e.get("notes"))
    put2("ans11", answer("ans11", "1.1", "ตาราง scaling บนเครื่องทดสอบ", e["answers"],
        side=table(rows, ["envs", "VRAM", "s/iter", "steps/s", "หมายเหตุ"], size=26), summary=e["summary"], side_w=980))

# ---------------------------------------------------------------- Ex 1.2
put2("ex12", slide("ex12", head("Exercise 1.2 · Command tracking", "สั่ง 0.3 m/s แล้วเป็ดเดินได้จริงเท่าไร?", "1.2"),
    code(f'{G} uv run scripts/export.py Mjlab-Velocity-Flat-MicroDuck --checkpoint-file &lt;run&gt;/model_1999.pt<br>{G} uv run scripts/infer_policy.py --walking output.onnx <b>--new-cmd-obs</b> --lin-vel-x 0.3'),
    row=[task(["export checkpoint สุดท้ายเป็น ONNX แล้วรันที่ vx = 0.2, 0.3, 0.4",
               "อ่านบรรทัด <b>[vel 1s avg] achieved/cmd</b> เฉลี่ย 10 วินาทีสุดท้าย",
               "โหลด <b>alpha_walking.onnx</b> จาก HF repo pollen-robotics/microduck-policies มาเทียบ",
               "รันซ้ำด้วย <b>--no-bam</b> — ความเร็วเปลี่ยนไหม?"]),
         result(bigrow(big("0.15 m/s", "ได้จริงเมื่อสั่ง 0.30"), big("+0.24 rad/s", "หมุนซ้ายเองทั้งที่สั่ง 0", "#B85C00"))
                + f'<img src="{STRIP}" alt="Six frames of the trained Microduck walking at 0.1 s intervals" style="width:100%;height:270px;object-fit:cover;border-radius:12px">')],
    at=2), "ลืม --new-cmd-obs = สคริปต์สร้าง obs 51 มิติแบบเก่า แล้ว onnxruntime ขึ้น INVALID_ARGUMENT invalid dimensions")

t12 = [["0.20", "0.00 (ยืนนิ่ง)", "0.00 (ยืนนิ่ง)", "0.00", "—"],
       ["0.25", "0.10", "0.09", "—", "—"],
       ["0.30", "0.15 · ωz +0.24", "0.11", "0.21", "0.13"],
       ["0.40", "0.23", "0.16", "0.28", "0.18"]]
put2("ans12", answer("ans12", "1.2", "ซิมเดินได้ ≠ ทำตามคำสั่งได้",
    ["ต้องใส่ <b>--new-cmd-obs</b> ไม่งั้นสคริปต์สร้าง obs 51 มิติ แล้ว ONNX ขึ้น INVALID_ARGUMENT",
     "ได้ความเร็วจริงแค่ <b>40–60%</b> ของคำสั่ง และที่ ≤ 0.2 m/s เป็ด<b>ยืนนิ่ง</b>จากท่าเริ่ม — เป็นทั้งของเราและของ Pollen (ยังไม่ได้พิสูจน์สาเหตุ)",
     "ของเรา<b>เดินวนซ้าย</b> ~3/4 รอบใน 20 s ของ Pollen โค้งขวาน้อยกว่า — policy คุมความเร็ว ไม่ได้คุมทิศ",
     "<b>--no-bam</b> เร็วขึ้น 20–40% → แรงเสียดทานและแรงดันในโมเดลมอเตอร์กินความเร็วจริง"],
    side=f'<img src="{TRAJ}" alt="Top-view paths: ours circles left, Pollen curves right" style="width:900px;height:330px;object-fit:contain;border-radius:16px">'
         + table(t12, ["cmd", "ของเรา", "Pollen", "เรา no-BAM", "Pollen no-BAM"], size=24),
    summary="เทรนครบ 2,000 iterations แล้วยังต้องวัดก่อนลงหุ่น · AGENTS.md บอกว่าท่าเดินจริงใช้ 4,000–6,000", side_w=900),
    "ค่าเฉลี่ย 10 วินาทีสุดท้ายของ [vel 1s avg] จาก infer_policy.py บน CPU ทดสอบ 2 พ.ย. 2026; alpha_walking.onnx เป็นไฟล์ใน HF repo ทางการ ณ วันนั้น")

# ---------------------------------------------------------------- Ex 2.1
e = RES.get("ex21")
if e:
    put2("ex21", slide("ex21", head("Exercise 2.1 · Sign bug", "พลิกเครื่องหมายเดียว เป็ดจะโกงไหม?", "2.1"),
        code(f'{G} uv run train Mjlab-Velocity-Flat-MicroDuck --env.scene.num-envs 4096 \\<br>{SP}--agent.max-iterations 300 --agent.logger tensorboard \\<br>{SP}<b>--env.rewards.foot-slip.weight 0.1</b>{SP}{C("# ค่าจริง −0.1")}'),
        row=[task(["รัน 300 iterations ด้วย weight +0.1 แล้วรันซ้ำที่ <b>+1.0</b>",
                   "ดู <b>Episode_Reward/foot_slip</b> — บวกหรือลบ?",
                   "เทียบ <b>Metrics/slip_velocity_mean</b> กับรอบปกติที่ iteration เดียวกัน",
                   "ถ้าไม่รู้ว่า weight ผิด จะจับได้จากบรรทัดไหน?"]),
             result(bigrow(big(e["b1"], e["l1"], "#B85C00"), big(e["b2"], e["l2"], "#B85C00")) + p(e["headline"], 28))],
        at=2), e.get("notes"))
    put2("ans21", answer("ans21", "2.1", "penalty ที่เป็นบวก = เป็ดได้เงินจากความผิด", e["answers"],
        side=table(e["table"], ["iteration 300", "ปกติ −0.1", "+0.1", "+1.0"], size=26), summary=e["summary"], side_w=900))

# ---------------------------------------------------------------- Ex 2.2
e = RES.get("ex22")
if e:
    put2("ex22", slide("ex22", head("Exercise 2.2 · Ablation", "ตัด air_time ออก เป็ดยังก้าวไหม?", "2.2"),
        code(f'{G} uv run train Mjlab-Velocity-Flat-MicroDuck --env.scene.num-envs 4096 \\<br>{SP}--agent.max-iterations 500 --agent.logger tensorboard \\<br>{SP}<b>--env.rewards.air-time.weight 0.0</b>{SP}{C("# ค่าจริง +3.0")}'),
        row=[task(["รัน 500 iterations โดยไม่มีรางวัลการยกเท้า",
                   "เทียบกับรอบปกติที่ iteration 500: <b>peak_height_mean</b>, <b>fell_over</b>, <b>error_vel_xy</b> (air_time_mean หายจาก log เมื่อ weight = 0)",
                   "Mean reward ของสองรอบเทียบกันตรงๆ ได้ไหม? ทำไม",
                   "export แล้วรัน infer_policy — เป็ดก้าวไหม?"]),
             result(bigrow(big(e["b1"], e["l1"], "#B85C00"), big(e["b2"], e["l2"], "#B85C00")) + p(e["headline"], 28))],
        at=2), e.get("notes"))
    put2("ans22", answer("ans22", "2.2", e["title"], e["answers"],
        side=table(e["table"], ["iteration 500", "ปกติ", "ไม่มี air_time"], size=26), summary=e["summary"], side_w=900))

# ---------------------------------------------------------------- bridge
put2("next", f'''<section id="next" data-transition="fade" style="{NAVY};padding:128px;display:flex;flex-direction:row;gap:64px;align-items:center">
<div style="flex:1;display:flex;flex-direction:column;gap:32px">
<p style="font-size:24px;letter-spacing:3px;text-transform:uppercase;color:#7AC943;font-weight:600">Next · Module 3–5 Sim Playground</p>
<h1 style="{H};font-size:100px;font-weight:600;line-height:1.05;color:#F4F3EE">ยังไม่มีหุ่น ก็เล่นต่อได้</h1>
<p style="font-size:36px;color:#B8C4D0;line-height:1.45">เรียก 9 ท่าทางการของ Pollen ในซิม สร้างด่านเอง แล้วเขียนแอปเตะบอล — ส่วนโมเดลมอเตอร์ BAM ย้ายไป Module 6 ตอนหุ่นมาถึง</p>
<div style="display:flex;flex-direction:row;gap:16px">
<p style="font-size:26px;background:#7AC943;color:#0E1621;padding:10px 22px;border-radius:40px;font-weight:600">Skill Zoo</p>
<p style="font-size:26px;border:2px solid #3A4A5C;color:#B8C4D0;padding:8px 22px;border-radius:40px">Level Design</p>
<p style="font-size:26px;border:2px solid #3A4A5C;color:#B8C4D0;padding:8px 22px;border-radius:40px">Applications</p>
</div></div>
<img src="{SIDE}" alt="Microduck side view" style="width:560px;height:760px;object-fit:cover;border-radius:24px">
</section>''')

OUT = sys.argv[1]
only = sys.argv[2:] or list(new)
for sid in only:
    open(f"{OUT}/project/slides/{sid}.html", "w").write(new[sid])
print("wrote", only)
