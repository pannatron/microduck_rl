"""Microduck deck 4 — Week 9–12: Toward the Real Duck. Usage: gen5.py <deck_root> [ids...]"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from common4 import *  # noqa: F401,F403
from common4 import slides, order

HERO = B("7e875dd79c82ca0af428ba02b5f0b8c7")
SIDE = B("0d8544fd66d36359ca5524d6041ad3e8")
ROLLER = B("ff09a1073778fd49cc39c0f6519e4893")
BENCH = B("9197dc389c36e9d22db3a52c6b22b5dc")
FIT = B("6578c639758810b5157f33d8a6d07ba4")
SENS = B("f972e386d1517dff963a22c5f5a6ccf6")
SID = json.load(open(os.path.join(os.path.dirname(__file__), "sysid.json")))
DRAFT = '<p style="font-size:24px;background:#FBEBDD;color:#8A4300;padding:8px 20px;border-radius:40px;font-weight:600">ร่าง · รอหุ่นจริง</p>'


def draft_head(eyebrow, title):
    return (f'<div style="display:flex;flex-direction:row;justify-content:space-between;align-items:end">'
            f'<div style="display:flex;flex-direction:column;gap:16px">'
            f'<p style="font-size:28px;letter-spacing:4px;text-transform:uppercase;color:#B85C00;font-weight:600">{eyebrow}</p>'
            f'<h2 style="{H};font-size:76px;font-weight:600;line-height:1.1;color:#0E1621">{title}</h2></div>{DRAFT}</div>')


# ================================================================ cover / agenda
put("cover", f'''<section id="cover" data-transition="fade" style="{NAVY};padding:128px;display:flex;flex-direction:row;gap:72px;align-items:center">
<div style="flex:1;display:flex;flex-direction:column;gap:28px">
<p style="font-size:24px;letter-spacing:3px;text-transform:uppercase;color:#7AC943">Engineering Workshop · สัปดาห์ 9–12</p>
<h1 style="{H};font-size:120px;font-weight:600;line-height:1.02;color:#F4F3EE">Toward the Real Duck</h1>
<p style="font-size:40px;color:#B8C4D0;line-height:1.4">มอเตอร์จริง · deploy · sim-to-real gap · final project</p>
<div style="display:flex;flex-direction:row;gap:16px">
<p style="font-size:24px;background:#7AC943;color:#0E1621;padding:10px 22px;border-radius:40px;font-weight:600">สัปดาห์ 9 วัดแล้วในซิม</p>
<p style="font-size:24px;background:#FBEBDD;color:#8A4300;padding:10px 22px;border-radius:40px;font-weight:600">สัปดาห์ 10–12 ร่าง</p>
</div>
<p style="font-size:28px;color:#B8C4D0;line-height:1.5">Pannatorn Bongkotamphon<br>Dr. Sukhum Sattaratnamai</p>
</div>
<img src="{BENCH}" alt="XL330 test bench model: one servo swinging a weighted arm" style="width:720px;height:820px;object-fit:cover;border-radius:24px">
</section>''', "ภาคสุดท้ายของหลักสูตร 12 สัปดาห์ สัปดาห์ 9 ทำในซิมแล้วมีผลวัด สัปดาห์ 10–12 เป็นร่างที่ต้องปรับเมื่อหุ่นจริงมาถึง ทุกหน้าที่เป็นร่างมีป้ายสีส้มมุมขวาบน")

agenda_items = [("09", "System ID · มอเตอร์ตัวเดียวก่อนทั้งหุ่น", "#3D7A12"),
                ("10", "Bring-up · digital twin แล้วค่อยหุ่นจริง", "#B85C00"),
                ("11", "วัด sim-to-real gap · สมมติฐานจาก 9 สัปดาห์", "#B85C00"),
                ("12", "Final project · demo day", "#B85C00"),
                ("→", "แผนที่ทั้งหลักสูตร", "#3D7A12")]
rows = ""
for i, (n, t, c) in enumerate(agenda_items):
    bd = "border-bottom:2px solid #DDDBD2;padding:0px 0px 22px 0px" if i < len(agenda_items) - 1 else ""
    rows += (f'<div style="display:flex;flex-direction:row;gap:36px;align-items:baseline;{bd}">'
             f'<p style="{H};font-size:40px;font-weight:600;color:{c};width:72px">{n}</p>'
             f'<p style="{H};font-size:44px;font-weight:500;color:#0E1621">{t}</p></div>')
put("agenda", f'''<section id="agenda" data-transition="fade" style="{SEC};padding:120px 128px 120px;display:flex;flex-direction:row;gap:96px">
<div style="width:520px;display:flex;flex-direction:column;justify-content:space-between">
<div style="display:flex;flex-direction:column;gap:20px">
<p style="font-size:28px;letter-spacing:4px;text-transform:uppercase;color:#3D7A12;font-weight:600">Week 9–12</p>
<h2 style="{H};font-size:120px;font-weight:600;line-height:1;color:#0E1621">Agenda</h2>
</div>
<img src="{HERO}" alt="Microduck model" style="width:520px;height:480px;object-fit:cover;border-radius:24px">
</div>
<div style="flex:1;display:flex;flex-direction:column;justify-content:space-between">{rows}</div>
</section>''', "สีเขียว = มีผลวัดแล้ว สีส้ม = ร่าง รอหุ่นจริง")

# ================================================================ WEEK 9
put("sec-w9", section("sec-w9", "Week 9 · System ID", "มอเตอร์<br>ตัวเดียว", "ก่อนเชื่อซิมทั้งตัว ให้ซิมของมอเตอร์ตัวเดียวตรงกับของจริงก่อน — ทำได้ตั้งแต่ก่อนหุ่นมาถึง", BENCH, "XL330 test bench"))

put("w9-bench", slide("w9-bench", head("src/mjlab_microduck/robot/xl330_test_bench", "test bench: XL330 หนึ่งตัว แขนหนึ่งข้าง"),
    row=[f'<div style="width:620px;display:flex;flex-direction:column"><img src="{BENCH}" alt="Test bench: XL330 with a weighted pendulum arm" style="width:620px;height:640px;object-fit:cover;border-radius:24px"></div>',
         f'<div style="flex:1;display:flex;flex-direction:column;gap:24px">'
         + table([["scene.xml", "แขนห้อยแบบลูกตุ้ม 0.12 kg — แรงโน้มถ่วงถ่วงตลอด"],
                  ["testbench_sim2real.py", "--mode sim | real · --compare · --to-bam"],
                  ["validate_bam_testbench.py", "เทียบ BAM กับข้อมูลจริง (ต้องมี repo Rhoban bam)"],
                  ["testbench_env_cfg.py", "task RL ข้อต่อเดียว — <b>ยังเป็น API mjlab รุ่นเก่า</b>"]], ["ไฟล์", "ใช้ทำอะไร"], size=26)
         + think("testbench_env_cfg.py import ของที่ mjlab 1.3.0 ไม่มีแล้ว (RslRlPpoActorCriticCfg, TerrainImporterCfg) — task นี้จึงเทรนไม่ได้ตอนนี้ เราเลยใช้แค่ฉากกับ BAM") + '</div>'],
    at=1), "ลองแล้ว: shim RslRlPpoActorCriticCfg ผ่าน แต่ไปติด TerrainImporterCfg ต่อ ต้อง port ทั้งไฟล์ ไม่คุ้มสำหรับคาบนี้")

bamt = [["kt", "0.366 N·m/A", "ค่าคงที่แรงบิด"], ["R", "2.81 Ω", "ความต้านทานขดลวด"], ["vin", "7.4 V", "แรงดัน (เทรนสุ่ม 6.5–8.2 V)"],
        ["kp firmware", "200", "P-loop ในตัวมอเตอร์"], ["แรงบิดสูงสุด", "vin·kt/R = 0.96 N·m", "ลดลงเมื่อแบตอ่อน"],
        ["voltage sag", "gain 0.1 (เทรน 0–0.2)", "แรงดันตกตามโหลด"], ["delay", "3–6 physics step", "15–30 ms"]]
put("w9-bam", slide("w9-bam", head("Rhoban BAM · model m6", "BAM จำลองมอเตอร์ไฟฟ้า ไม่ใช่สปริง"),
    row=[f'<div style="flex:1;display:flex;flex-direction:column">' + table(bamt, ["พารามิเตอร์", "ค่า", "หมายเหตุ"], size=27) + '</div>',
         card("ต่างจาก PD ตรงไหน", p("PD: แรงบิด = kp·(เป้า − มุม) − kd·ความเร็ว จบแค่นั้น", 29)
              + p("BAM: firmware P-loop สั่ง<b>แรงดัน</b> → กระแส (หัก back-EMF) → แรงบิด และแรงเสียดทานขึ้นกับโหลด", 29)
              + p("ผล: <b>แบตอ่อน = มอเตอร์อ่อน</b> — PD ที่ kp คงที่ไม่มีทางรู้", 29))],
    at=1), "ค่าจาก log ของ infer_policy.py (BAM m6 actuators: kt=0.3660 R=2.8114 vin=7.40V kp_fw=200) และ microduck_constants.py (vin_range 6.5–8.2, vin_drop_gain_range 0–0.2, delay 3–6)")

f = SID["fit"]; pr = SID["pd_ref"]
put("ex91", slide("ex91", head("Exercise 9.1 · Fit a PD to the motor", "PD ธรรมดาเลียนแบบมอเตอร์ได้ใกล้แค่ไหน?", "9.1"),
    code(f'{G} python playground/sysid_testbench.py sysid.json{SP}{C("# BAM = “มอเตอร์จริง” ชั่วคราว")}<br>'
         f'res = least_squares(lambda x: run_pd(*x) - q_bam, x0=[0.55, 0.05, 0.96]){SP}{C("# kp, kd, torque limit")}', 26),
    row=[task(["สั่งมุม 0 → 57° → −29° บน test bench (BAM m6, 7.4 V)",
               "ฟิต kp, kd, torque limit ของ PD ให้ตรงด้วย least squares",
               "เทียบกับ PD ที่เราใช้เทรนและทดสอบในสัปดาห์ 6",
               "PD แบบไหนทำให้ policy เห็นมอเตอร์ “แรงเกินจริง”?"]),
         f'<div style="width:880px;display:flex;flex-direction:column"><img src="{FIT}" alt="Step response: BAM, fitted PD with RMSE 1.2 degrees, MJCF PD 2.8 degrees, Newton runner PD 6.9 degrees" style="width:880px;height:512px;object-fit:contain;border-radius:20px"></div>'],
    at=2))

put("ans91", answer("ans91", "9.1", "PD ฟิตได้ใกล้ แต่ค่าที่ได้ไม่ใช่ค่าใน MJCF",
    [f"PD ที่ฟิตได้: kp <b>{f['kp']}</b>, kd <b>{f['kd']}</b>, แรงบิดสูงสุด <b>{f['torque_limit']} N·m</b> → คลาดจาก BAM <b>{f['rmse_deg']}°</b> (RMSE)",
     f"PD ตาม MJCF ของเป็ด (kp 0.55, damping 0.053, 0.96 N·m) คลาด {pr['mjcf_duck']['rmse_vs_bam_deg']}° — <b>แกว่งเกิน</b>ตอนถอยกลับ ทั้งที่ BAM ไม่แกว่ง",
     f"PD ใน Newton runner ของเรา (damping 0.053 + D-gain 0.053) คลาด <b>{pr['newton_isaaclab']['rmse_vs_bam_deg']}°</b> — ช้ากว่ามอเตอร์จริง",
     "มอเตอร์จริงอยู่ระหว่างสองค่านี้ → ความต่าง kd ที่ทำให้เป็ดเดินช้าลง 35% ในสัปดาห์ 6 ไม่ใช่เรื่องบังเอิญ: เป็น gap ที่ <b>วัดได้</b> ตั้งแต่ระดับมอเตอร์ตัวเดียว"],
    side=table([["PD ที่ฟิต", f"{f['kp']}", f"{f['kd']}", f"{f['rmse_deg']}°"], ["MJCF เป็ด", "0.55", "0.053", f"{pr['mjcf_duck']['rmse_vs_bam_deg']}°"],
                ["Newton runner", "0.55", "0.106", f"{pr['newton_isaaclab']['rmse_vs_bam_deg']}°"], ["MJCF test bench", "0.386", "0.041", f"{pr['mjcf_testbench']['rmse_vs_bam_deg']}°"]],
               ["PD", "kp", "kd รวม", "RMSE"], size=26) + p("kd รวม = joint damping + D-gain · RMSE เทียบ BAM ทั้ง 2 วินาที", 24, "#4A5563"),
    summary="ก่อนเทรน ให้ฟิตโมเดลมอเตอร์กับมอเตอร์จริงก่อน — ค่าใน MJCF เป็นจุดเริ่ม ไม่ใช่ความจริง", side_w=820),
    "MJCF ของ test bench ใช้ actuator class เก่า (kp 0.386, ±0.67 N·m) ไม่ตรงกับ MJCF ของเป็ด (0.55, ±0.96) — อีกตัวอย่างว่าค่าในไฟล์แต่ละไฟล์ไม่จำเป็นต้องสอดคล้องกัน")

b = SID["bam"]
put("ex92", slide("ex92", head("Exercise 9.2 · Battery & payload", "แบตอ่อนหรือแขนหนัก มอเตอร์ทำได้เท่าเดิมไหม?", "9.2"),
    code(f'{G} run_bam(vin=6.5){SP}{G} run_bam(vin=8.2){SP}{C("# ช่วงที่ Pollen สุ่มตอนเทรน")}<br>{G} run_bam(mass=0.05){SP}{G} run_bam(mass=0.25){SP}{C("# แขนเบา / หนัก")}', 26),
    row=[task(["สั่งมุมเดิม เปลี่ยนแรงดัน 6.5 / 7.4 / 8.2 V",
               "เปลี่ยนน้ำหนักแขน 0.05 / 0.12 / 0.25 kg",
               "วัดมุมที่ค้างห่างเป้าหลัง 1 s",
               "PD ที่ฟิตใน 9.1 (ที่ 7.4 V) จะผิดแค่ไหนตอนแบตเหลือ 6.5 V?"]),
         f'<div style="width:880px;display:flex;flex-direction:column"><img src="{SENS}" alt="BAM step responses: low battery and heavy arm both stop further from the target" style="width:880px;height:512px;object-fit:contain;border-radius:20px"></div>'],
    at=2))

put("ans92", answer("ans92", "9.2", "มอเตอร์เดียวกัน ทำงานไม่เท่ากันทุกวัน",
    [f"มุมค้างห่างเป้า: 8.2 V = {b['vin_8.2']['final_err_deg']}°, 7.4 V = {b['nominal']['final_err_deg']}°, <b>6.5 V = {b['vin_6.5']['final_err_deg']}°</b> — แบตอ่อนลง มอเตอร์อ่อนตาม",
     f"แขน 0.05 kg = {b['mass_0.05']['final_err_deg']}°, 0.12 kg = {b['nominal']['final_err_deg']}°, <b>0.25 kg = {b['mass_0.25']['final_err_deg']}°</b> — firmware เป็น P-loop ล้วน ไม่มี I จึงค้างตามโหลด",
     "PD ที่ฟิตไว้ที่ 7.4 V เป็นค่าคงที่ — แบตหมดกลางคาบ policy จะเจอมอเตอร์ที่ไม่เคยเห็น",
     "นี่คือเหตุผลที่ Pollen เทรนด้วย BAM <b>และ</b>สุ่มแรงดัน 6.5–8.2 V กับ voltage sag 0–0.2 แทนการใช้ PD"],
    side=table([["8.2 V", f"{b['vin_8.2']['final_err_deg']}°"], ["7.4 V (ปกติ)", f"{b['nominal']['final_err_deg']}°"], ["6.5 V", f"{b['vin_6.5']['final_err_deg']}°"],
                ["แขน 0.05 kg", f"{b['mass_0.05']['final_err_deg']}°"], ["แขน 0.25 kg", f"{b['mass_0.25']['final_err_deg']}°"]], ["สภาพ", "ค้างห่างเป้า (1 s)"], size=28),
    summary="ทดสอบหุ่นจริงทั้งตอนแบตเต็มและแบตใกล้หมด — ถ้าผลต่างกัน ให้สงสัยแรงดันก่อนสงสัย policy", side_w=620),
    "เป้า 57° ทุกกรณี แขนห้อยแบบลูกตุ้มบน test bench; BAM m6 ใน MuJoCo CPU dt 0.005 s")

steps9 = [("ต่อมอเตอร์", "XL330 + ตัวแปลง USB-serial ของ Dynamixel · port /dev/ttyUSB0 · baud 1M"),
          ("บันทึกซิม", "testbench_sim2real.py --mode sim --onnx &lt;policy&gt; --out sim.npz"),
          ("บันทึกจริง", "--mode real --port /dev/ttyUSB0 --motor-id 1 --out real.npz"),
          ("เทียบ", "--compare sim.npz real.npz → กราฟซ้อน"),
          ("ฟิต", "--to-bam real.npz log.json แปลงเป็นข้อมูลแบบ BAM แล้วฟิต (หรือแทน BAM ใน sysid_testbench.py)")]
cards9 = "".join(f'<div style="flex:1;background:#FBFAF6;border:1px solid #DDDBD2;border-radius:24px;padding:28px 26px;display:flex;flex-direction:column;gap:12px">'
                 f'<p style="{H};font-size:52px;font-weight:600;color:#B85C00;line-height:1">{i + 1}</p>'
                 f'<h3 style="{H};font-size:34px;font-weight:600;color:#0E1621">{t}</h3><p style="{M};font-size:24px;color:#1B2430;line-height:1.45">{d}</p></div>'
                 for i, (t, d) in enumerate(steps9))
put("w9-real", slide("w9-real", draft_head("Week 9 · เมื่อมีมอเตอร์จริง", "ทำซ้ำ 9.1 กับมอเตอร์ตัวจริง"),
    f'<div style="flex:1;display:flex;flex-direction:row;gap:18px">{cards9}</div>',
    think("ต้องมี policy ของ test bench ก่อน (testbench_env_cfg.py ต้อง port เป็น mjlab 1.3.0) — หรือเขียนลำดับมุมเป้าหมายเองแทน policy เพื่อเก็บ step response อย่างเดียว"),
    at=1), "คำสั่งและตัวเลือกทั้งหมดอ่านจาก argparse/docstring ของ scripts/testbench_sim2real.py; ยังไม่ได้รันกับมอเตอร์จริง")

# ================================================================ WEEK 10
put("sec-w10", section("sec-w10", "Week 10 · Bring-up (ร่าง)", "หุ่นจริง<br>วันแรก", "ซ้อมกับ digital twin ที่ใช้ daemon ตัวจริง แล้วค่อยเปิดหุ่น", SIDE, "Microduck side view"))

twin = [["scripts/duck-sim", "duck-body (MuJoCo + BAM) + robotd --sim + tofd --sim"],
        ["scripts/duck-sim drive", "เดินหน้า 8 s (vx 0.15)"],
        ["scripts/duck-sim ctl health", "robotctl ตัวจริง ชี้ไปที่เป็ดจำลอง"],
        ["scripts/duck-sim monitor", "ข้อต่อ, IMU, ToF แบบสด"],
        ["DUCK_SIM_VIEWER=0", "รันแบบไม่มีจอ"]]
put("w10-twin", slide("w10-twin", draft_head("pollen-robotics/microduck · docs/robot/simulation.md", "digital twin: daemon จริง ตัวหุ่นในซิม"),
    row=[f'<div style="flex:1;display:flex;flex-direction:column;gap:20px">' + table(twin, ["คำสั่ง", "ทำอะไร"], size=26) + '</div>',
         card("ซ้อมอะไรได้ · อะไรไม่ได้", p("<b>ได้:</b> loop 50 Hz, policy, safety, fall detection, odometry, IPC, robotctl — โค้ดชุดเดียวกับบนหุ่น", 28)
              + p("<b>ไม่ได้:</b> driver ทั้งหมด — บัส Dynamixel, BLE, กล้อง, NPU (“absent, not modelled”)", 28)
              + p("<b>สถานะ:</b> ยังไม่ได้รันบนเครื่องนี้ ต้อง build daemon ภาษา Rust จาก repo microduck ก่อน", 28, "#8A4300"))],
    at=1), "อ่านจาก docs/robot/simulation.md ของ repo microduck (clone แล้วที่ ~/repos/microduck) และ docstring ของ duck-body (src/mjlab_microduck/sim/body_server.py)")

flow = ""
for i, (t, d) in enumerate([("export", "ONNX + normalizer ฝังใน"), ("publish", "uv run publish → manifest schema-2 + ตรวจ shape/smoke"),
                            ("HF Hub", "repo &lt;user&gt;/microduck-&lt;name&gt;"), ("robotctl", "policy add บนหุ่น"), ("robotd", "สลับ policy ได้ใน runtime")]):
    flow += (f'<div style="flex:1;background:{"#1F4D06" if i == 4 else "#FBFAF6"};border:1px solid #DDDBD2;border-radius:24px;padding:28px 24px;display:flex;flex-direction:column;gap:12px">'
             f'<p style="{M};font-size:30px;font-weight:600;color:{"#B8E68F" if i == 4 else "#B85C00"}">{t}</p>'
             f'<p style="font-size:27px;color:{"#F4F3EE" if i == 4 else "#1B2430"};line-height:1.4">{d}</p></div>')
    if i < 4:
        flow += '<x-shape kind="arrow-right" style="width:48px;height:28px;background:#B9B7AE;align-self:center"></x-shape>'
checks = [("ก่อนเปิด", "นับมอเตอร์ 15 ตัว · ทิศข้อต่อตรงกับซิม (robotctl monitor) · แบตเต็ม"),
          ("policy แรก", "velstand ทางการก่อน แล้วค่อย policy ของเรา"),
          ("ลำดับทดสอบ", "แขวน → วางยืน → เดินช้า → เดินตรง 1 m · มีคนคอยจับทุกครั้ง"),
          ("บันทึก", "วิดีโอ + log obs/action ทุกครั้ง ไว้ใช้สัปดาห์ 11")]
put("w10-deploy", slide("w10-deploy", draft_head("AGENTS.md · Commands", "จาก checkpoint ถึงหุ่นจริง"),
    f'<div style="display:flex;flex-direction:row;gap:12px">{flow}</div>',
    table([[a, b2] for a, b2 in checks], ["ขั้น", "เช็กลิสต์ bring-up (ร่าง)"], size=28),
    at=1), "ห้ามแปลง checkpoint เป็น ONNX เอง ต้องใช้ scripts/export.py (AGENTS.md: normalizer ต้องฝังใน ONNX); policy ที่เราเทรนบน Newton ใช้ ckpt2onnx.py ของเราซึ่งฝัง normalizer แบบเดียวกัน แต่ยังไม่ได้ผ่าน publish gate ของ Pollen")

# ================================================================ WEEK 11
put("sec-w11", section("sec-w11", "Week 11 · Sim-to-real gap (ร่าง)", "ซิมบอก<br>อะไรผิด", "9 สัปดาห์ที่ผ่านมาทิ้งสมมติฐานไว้หลายข้อ — สัปดาห์นี้ให้หุ่นจริงตัดสิน", ROLLER, "Our roller policy"))

hyp = [["สั่ง ≤ 0.2 m/s แล้วยืนนิ่ง", "1, 6", "เกิดทุกซิม → น่าจะเกิดบนหุ่นด้วย"],
       ["policy จาก Newton เดินเร็วเกินคำสั่ง", "6", "MuJoCo 0.3 → 0.40–0.45"],
       ["PD ไม่ตรงมอเตอร์จริง", "6, 9", "kd ทำความเร็วต่างได้ 35%"],
       ["latency DR จำเป็นแค่ไหน", "6", "ตัวไม่มี DR ล้ม 684/1,024 ที่หน่วงเต็ม"],
       ["แรงเสียดทานล้อจริง 0.003 หรือไม่", "7", "ถ้าใช่ roller.onnx ไถได้แค่ 0.13"],
       ["ช่อง command ที่ไม่เคยใช้", "8", "ป้อนแล้วล้ม 768/768 ในซิม"]]
put("w11-hyp", slide("w11-hyp", draft_head("Week 11 · เอาสมมติฐานไปทดสอบ", "6 คำถามที่ซิมตอบไม่ได้"),
    table(hyp, ["สมมติฐาน", "จากสัปดาห์", "ซิมบอกว่า"], size=28),
    think("วิธีวัดเหมือนในซิมทุกข้อ: คำสั่งเดียวกัน หลายรอบ รายงานเป็นช่วง — ถ้าหุ่นจริงไม่ตรงกับซิม ให้กลับไปดูว่าพารามิเตอร์ไหนในซิมอยู่นอกช่วงของจริง"),
    at=1))

knobs = [["แรงดันแบต", "6.5–8.2 V", "ความเร็วต่างตามระดับแบต"], ["voltage sag", "0–0.2", "อ่อนลงตอนเดินเร็ว"],
         ["actuator delay", "3–6 step (15–30 ms)", "สั่นหรือล้มเมื่อเร็ว"], ["IMU delay", "0–1 step", "เอียงแล้วแก้ช้า"],
         ["joint vel delay", "1 step ตายตัว", "—"], ["backlash", "add_backlash.py --backlash-deg 2.0", "ข้อต่อหลวม เดินสะดุด"],
         ["แรงเสียดทานล้อ", "0 → 0.0015 (curriculum)", "ไถช้า (เวอร์ชันล้อ)"]]
put("w11-dr", slide("w11-dr", draft_head("microduck_constants.py · velocity cfg", "ปุ่ม DR ที่ Pollen ใช้ และอาการที่ชี้ไปหามัน"),
    table(knobs, ["ปุ่ม DR", "ช่วงที่เทรน", "อาการบนหุ่นจริงที่ควรสงสัยปุ่มนี้"], size=28),
    p("ช่วงในตารางอ่านจากโค้ด · คอลัมน์อาการเป็นร่างจากการทดลองในซิม ต้องยืนยันบนหุ่น", 26, "#4A5563"),
    at=1))

# ================================================================ WEEK 12
put("sec-w12", section("sec-w12", "Week 12 · Final project (ร่าง)", "Demo<br>day", "เอาแอปหรือท่าที่ทำในซิมลงหุ่นจริง แล้วรายงานว่าอะไรต่างจากซิม", HERO, "Microduck"))

proj = [("แอปบนหุ่นจริง", "เตะบอล · เดินลาดตระเวน · ท่าเต้น จากสัปดาห์ 5"), ("ท่าใหม่ของตัวเอง", "จากสัปดาห์ 8 — เทรนบน Newton แล้ว deploy"),
        ("เวอร์ชันล้อ", "ไถตรง 3 m แล้วเบรกหยุดในเส้น")]
cards12 = "".join(card(t, p(d, 30)) for t, d in proj)
deliver = [["วิดีโอบนหุ่นจริง", "ทำงานครบ 1 รอบ ไม่มีคนช่วย"], ["ตัวเลขซิม vs จริง", "อย่างน้อย 3 ตัวแปร หลายรอบ รายงานเป็นช่วง"],
           ["รายงานความต่าง", "อะไรต่าง · สงสัยพารามิเตอร์ไหน · แก้ด้วยอะไร"], ["ไฟล์", "ONNX + controller (ctl_*.py) ที่คนอื่นรันซ้ำได้"]]
put("w12-project", slide("w12-project", draft_head("Week 12 · Final project", "เลือกหนึ่งโจทย์ ส่งของ 4 อย่าง"),
    f'<div style="display:flex;flex-direction:row;gap:28px">{cards12}</div>',
    table(deliver, ["สิ่งที่ส่ง", "รายละเอียด"], size=28),
    at=1))

# ================================================================ course map
weeks = [["1–2", "Microduck · PPO · reward", "Module 1–2", "มีผลวัด"], ["3–6", "Skill Zoo · ด่าน · แอป · Newton", "Module 3–6 Sim Playground", "มีผลวัด"],
         ["7–8", "เวอร์ชันล้อ · ออกแบบท่าใหม่", "Week 7–8 Roller &amp; New Skills", "มีผลวัด"],
         ["9", "System ID มอเตอร์", "เด็คนี้", "มีผลวัดในซิม"], ["10–12", "Bring-up · gap · final project", "เด็คนี้", "ร่าง รอหุ่นจริง"]]
put("map", slide("map", head("ทั้งหลักสูตร", "12 สัปดาห์ · 4 เด็ค"),
    table(weeks, ["สัปดาห์", "เนื้อหา", "เด็ค", "สถานะ"], size=30),
    f'<div style="flex:1;display:flex;flex-direction:row;gap:28px">'
    + card("ซิมไม่ตรงกันเอง", p("MuJoCo CPU, MuJoCo Warp, Newton ให้ความเร็วต่างกันได้ 37% กับ policy เดียวกัน", 29))
    + card("พารามิเตอร์นอกช่วง", p("แรงเสียดทานล้อ, kd ของ PD, แรงดันแบต — ค่าเดียวที่ผิดเปลี่ยนผลทั้งหมด", 29))
    + card("ตัวเลขไม่พอ", p("เป็ดล้อไถเร็วแต่ท่าผิด — เห็นได้จากวิดีโอเท่านั้น", 29)) + '</div>',
    at=1), "สิ่งที่ซ้ำทุกสัปดาห์: วัดก่อนเชื่อ — ตัวเลขจากซิมหลายตัวในหลักสูตรนี้ถูกแก้หลังวัดซ้ำ และนั่นคือทักษะที่ต้องใช้มากที่สุดเมื่อหุ่นจริงมาถึง · ลิงก์เด็ค: Module 1–2 https://claude.ai/artifact/Aocjt2p64YPCmjzUnwmmFo · Module 3–6 https://claude.ai/artifact/N16x3JaWE9Y9J6wwMYKMc2 · Week 7–8 https://claude.ai/artifact/YELPvtyg9biUhwQfbhZoMn · แผนหลักสูตร https://claude.ai/artifact/NE3WHzHXwDYGhbhXkzweuq")

OUT = sys.argv[1]
only = sys.argv[2:] or order
os.makedirs(f"{OUT}/project/slides", exist_ok=True)
for sid in only:
    open(f"{OUT}/project/slides/{sid}.html", "w").write(slides[sid])
json.dump(order, open(f"{OUT}/order.json", "w"))
print("wrote", len(only), "slides")
