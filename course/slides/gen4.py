"""Microduck deck 3 — Week 7–8: Roller & New Skills. Usage: gen4.py <deck_root> [ids...]"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from common4 import *  # noqa: F401,F403  (helpers ชุดเดียวกับ gen3: put, slides, order, p, card, big, bigrow, section, strip ...)
from common4 import slides, order

HERO = B("a74406d950ae2549f45d2341664c51f0")
SIDE = B("c3f4c86e129adefcc495be73043d5ec9")
SECR = B("53a1fc1df244e6f99abaad812bea6e8d")
RSTRIP = B("a84b147e75279dcdccbd7b0b67b5e76d")
RFRIC = B("bac058af773fe06fa7e2c56433b54607")
RBRAKE = B("5799e29a2f40b71afe4e51c0232dd188")
RES = json.load(open(os.path.join(os.path.dirname(__file__), "results4.json")))
VID = {"roller": ("8b9c4c023e904cc05826b1798dcfc240", "e7052773fa4dbf76d58068fd0f24d6e0")}
VID.update({k: tuple(v) for k, v in RES.get("videos", {}).items()})


def video(name, alt, w, h):
    still, clip = VID[name]
    return f'<img src="{B(still)}" data-video="{B(clip)}" alt="{alt}" style="width:{w}px;height:{h}px;object-fit:cover;border-radius:20px">'


# ================================================================ cover / agenda
put("cover", f'''<section id="cover" data-transition="fade" style="{NAVY};padding:128px;display:flex;flex-direction:row;gap:72px;align-items:center">
<div style="flex:1;display:flex;flex-direction:column;gap:28px">
<p style="font-size:24px;letter-spacing:3px;text-transform:uppercase;color:#7AC943">Engineering Workshop · สัปดาห์ 7–8</p>
<h1 style="{H};font-size:120px;font-weight:600;line-height:1.02;color:#F4F3EE">Roller &amp; New Skills</h1>
<p style="font-size:40px;color:#B8C4D0;line-height:1.4">เป็ดใส่สเก็ต และการออกแบบท่าใหม่ด้วยตัวเอง</p>
<div style="display:flex;flex-direction:row;gap:16px">
<p style="font-size:24px;background:#7AC943;color:#0E1621;padding:10px 22px;border-radius:40px;font-weight:600">ยังไม่ต้องมีหุ่น</p>
<p style="font-size:24px;border:2px solid #3A4A5C;color:#B8C4D0;padding:8px 22px;border-radius:40px">Microduck RL · ภาค 3</p>
</div>
<p style="font-size:28px;color:#B8C4D0;line-height:1.5">Pannatorn Bongkotamphon<br>Dr. Sukhum Sattaratnamai</p>
</div>
<img src="{SECR}" alt="Microduck on roller skates" style="width:720px;height:820px;object-fit:cover;border-radius:24px">
</section>''', "ต่อจาก Module 3–6 สัปดาห์ 7 ใช้เป็ดเวอร์ชันล้อของ Pollen สัปดาห์ 8 สร้างท่าใหม่เองตั้งแต่ reward ไปจนเทรนเสร็จ ทุกตัวเลขวัดจริงบน RTX 3060 Laptop 6 GB")

agenda_items = [("07", "Roller · เป็ดใส่สเก็ต ไถ เบรก", "#3D7A12"),
                ("07", "ซิมนอกช่วงที่เทรน: แรงเสียดทานล้อ", "#3D7A12"),
                ("08", "ออกแบบท่าใหม่ตาม workflow ของ Pollen", "#3D7A12"),
                ("08", "หันหัวมองเป้าขณะเดิน · reward ที่ขัดกัน", "#3D7A12"),
                ("Ex", "Exercises 4 ข้อ + เฉลย", "#B85C00")]
rows = ""
for i, (n, t, c) in enumerate(agenda_items):
    bd = "border-bottom:2px solid #DDDBD2;padding:0px 0px 22px 0px" if i < len(agenda_items) - 1 else ""
    rows += (f'<div style="display:flex;flex-direction:row;gap:36px;align-items:baseline;{bd}">'
             f'<p style="{H};font-size:40px;font-weight:600;color:{c};width:72px">{n}</p>'
             f'<p style="{H};font-size:44px;font-weight:500;color:#0E1621">{t}</p></div>')
put("agenda", f'''<section id="agenda" data-transition="fade" style="{SEC};padding:120px 128px 120px;display:flex;flex-direction:row;gap:96px">
<div style="width:520px;display:flex;flex-direction:column;justify-content:space-between">
<div style="display:flex;flex-direction:column;gap:20px">
<p style="font-size:28px;letter-spacing:4px;text-transform:uppercase;color:#3D7A12;font-weight:600">Week 7–8</p>
<h2 style="{H};font-size:120px;font-weight:600;line-height:1;color:#0E1621">Agenda</h2>
</div>
<img src="{HERO}" alt="Microduck model" style="width:520px;height:480px;object-fit:cover;border-radius:24px">
</div>
<div style="flex:1;display:flex;flex-direction:column;justify-content:space-between">{rows}</div>
</section>''')

# ================================================================ WEEK 7 · ROLLER
put("sec-w7", section("sec-w7", "Week 7 · Roller", "เป็ด<br>ใส่สเก็ต", "ใบมีดสเก็ตกับล้อ passive 4 ล้อ — เป็ดไม่ได้เดิน แต่ถีบแล้วไถ", SECR, "Microduck on roller skates"))

cmdt = [["vx > 0", "ถีบเร่ง", "ยิ่งมากยิ่งถีบแรง ไม่ใช่ความเร็วเป้าหมาย"],
        ["vx = 0", "ไถต่อ (coast)", "หุบขา ปล่อยให้ล้อหมุน"],
        ["vx < 0", "เบรก", "ให้รางวัลเมื่อหยุด"],
        ["ช่อง 3", "heading error", "ปิดอยู่ในเวอร์ชันปัจจุบัน (ไถตรง)"]]
put("r-what", slide("r-what", head("Mjlab-Velocity-Flat-MicroDuck-Rollers", "ตัวเดิม แต่ความหมายของ command เปลี่ยน"),
    row=[f'<div style="flex:1;display:flex;flex-direction:column;gap:24px">' + table(cmdt, ["คำสั่ง", "แปลว่า", "หมายเหตุ"], size=28)
         + p("obs 61 มิติเหมือนเดิมทุกช่อง — สลับกับ policy เดินได้ใน runtime เดียวกัน", 28, "#4A5563") + '</div>',
         card("ต่างจากตัวเดิมตรงไหน", p("ล้อ passive <b>4 ล้อ</b> ใบละ 2 ล้อ ชื่อ <b>passive_*wheel</b> แทรกอยู่ในลำดับข้อต่อหลังข้อเท้า", 30)
              + p("ตัวสูงขึ้น 13.5 mm · action scale <b>0.8</b> (เดินใช้ 1.0)", 30)
              + p("กฎของ Pollen: <b>ห้าม hardcode index ข้อต่อ</b> ให้หาตามชื่อเสมอ", 30))],
    at=1), "ทั้งหมดอ่านจาก docstring ของ microduck_velocity_rollers_env_cfg.py และ manifest.json (roller.onnx: mode roller, action_scale 0.8)")

rew = [["wheel_speed", "+10.0", "cmd_x × tanh(ความเร็วล้อ / 0.3) — reward บวกตัวเดียวของงาน"],
       ["glide", "+4.0", "ไถบนใบเดียว ขานิ่ง — ให้ถีบทีละจังหวะ ไม่ตะกุยถี่"],
       ["skating_air_time", "+1.5", "ยกเท้าคืน 0.15–0.45 s เฉพาะตอนตัวเคลื่อนแล้ว"],
       ["braking", "+1.0", "สั่งเบรกแล้วความเร็วไปข้างหน้าเป็นศูนย์"],
       ["hip_roll_neutral", "−2.0", "ดึงขาไม่ให้กางพักบนลิมิต"]]
put("r-reward", slide("r-reward", head("reward ของเป็ดล้อ", "รางวัลจ่ายให้ “ล้อหมุน” ไม่ใช่ “ตัวเคลื่อน”"),
    table(rew, ["เทอม", "weight", "จ่ายเมื่อ"], size=28),
    think("คอมเมนต์ในโค้ดเล่าบทเรียนจากหุ่นจริง: ช่วงยกเท้า [0.40, 1.00] s เคย “บังคับให้เตะยาวแรง จน<b>หุ่นจริงล้ม</b>” จึงลดเหลือ 0.15–0.45 s — reward ดี ๆ หลายตัวมาจากการเห็นหุ่นจริงพัง"),
    at=1), "reward เต็มชุดมีมากกว่านี้ ตารางนี้คัดเฉพาะตัวที่กำหนดท่าไถ ค่าอ่านจาก cfg ปัจจุบันใน repo")

put("r-video", slide("r-video", head("roller.onnx · MuJoCo CPU + BAM", "ไถด้วยคำสั่ง +0.6 แล้วเบรกด้วย −0.5"),
    row=[video("roller", "Microduck on roller skates pushing forward, then braking", 820, 620),
         card("ดูอะไรในวิดีโอ", p("ถีบสลับข้าง แล้ว<b>ไถบนใบเดียว</b>ระหว่างจังหวะ — นี่คือสิ่งที่ reward <b>glide</b> จ่ายให้", 30)
              + p("หัวตั้ง ขาหุบ — ผลของ hip_roll_neutral", 30)
              + p("ที่ t = 6 s คำสั่งเปลี่ยนเป็นเบรก (ป้ายมุมซ้ายบน) — สังเกตทิศที่เป็ดไหลต่อ", 30)
              + p("วิดีโอเล่นตอน Present หรือคลิกที่ภาพ", 26, "#4A5563"))],
    at=1))

put("ex71", slide("ex71", head("Exercise 7.1 · Push strength", "ทำไมสั่ง 0.2 แล้วเป็ดไม่ยอมถีบ?", "7.1"),
    code(f'{G} CMDS="0:0.2" python playground/sim_play.py --ctl playground/ctl_roller.py --secs 10 -- \\<br>'
         f'{SP}--roller --walking roller.onnx --action-scale 0.8 --new-cmd-obs<br>'
         f'{G} CMDS="0:0.6 4:0.2" ...{SP}{C("# ไถมาก่อนแล้วค่อยลด")}{SP}{G} WHEEL_FRIC=0.0015 ...{SP}{C("# แรงเสียดทานล้อ")}', 26),
    row=[task(["กวาดคำสั่ง 0.1–0.6 วัดความเร็วไถ",
               "สมมติฐาน A: เริ่มจากหยุดนิ่งแล้วไม่คุ้มถีบ → ลองไถมาก่อนแล้วลดเป็น 0.2",
               "อ่าน <b>infer_policy.py</b> ว่าตั้งแรงเสียดทานลูกปืนล้อเท่าไร เทียบกับ curriculum ตอนเทรน",
               "ลองแรงเสียดทาน 0, 0.0015, 0.003"]),
         f'<div style="width:880px;display:flex;flex-direction:column"><img src="{RFRIC}" alt="Speed after 9 s by wheel friction: friction 0 gives 0.53 and 0.76, 0.0015 gives 0.06 and 0.42, 0.003 gives 0 and 0.13 for commands 0.2 and 0.4" style="width:880px;height:512px;object-fit:contain;border-radius:20px"></div>'],
    at=2))

put("ans71", answer("ans71", "7.1", "ซิมที่ใช้ซ้อม ตั้งค่านอกช่วงที่ policy เคยเห็น",
    ["สมมติฐาน A <b>ผิด</b>: ไถมาที่ 0.17 m/s แล้วลดคำสั่งเป็น 0.2 เป็ดก็หยุดถีบภายใน 2 s เหมือนเริ่มจากนิ่ง",
     "<b>infer_policy.py</b> ตั้งแรงเสียดทานลูกปืนล้อ <b>0.003</b> แต่ curriculum ตอนเทรนเริ่มที่ 0 และขึ้นไปแค่ <b>0.0015</b> ที่ iteration 5,000 — แรงหน่วงเป็น 2 เท่าของที่เคยเห็น",
     "ที่ 0.0015 สั่ง 0.2 ถีบเป็นพัก ๆ (0.03–0.14), สั่ง 0.4 ไถได้ <b>0.42</b> — มากกว่าค่าเดิม 3 เท่า",
     "ที่ 0 (ช่วงต้นการเทรน) เป็ดเร่งไม่หยุด — cmd_x คือ “แรงถีบ” ไม่ใช่ความเร็ว ไม่มีอะไรบอกให้หยุดเร่ง"],
    side=table([["0.1", "0", "—", "—"], ["0.2", "0", "0.06", "0.53 ↑"], ["0.3", "0.08", "—", "—"], ["0.4", "0.13", "0.42", "0.76"],
                ["0.5", "0.16", "—", "—"], ["0.6", "0.17", "—", "—"]], ["cmd", "fric 0.003", "fric 0.0015", "fric 0"], size=26)
         + p("m/s หลังไถ 9 s · ↑ = ยังเร่งอยู่ · — = ไม่ได้วัด", 24, "#4A5563"),
    summary="ก่อนสรุปว่า policy แย่ ให้เช็กว่าซิมที่ใช้ทดสอบอยู่ในช่วงพารามิเตอร์ที่เทรนมาหรือเปล่า", side_w=760),
    "แรงเสียดทาน 0.003 ใน infer_policy มีคอมเมนต์ว่า “realistic wheel bearing friction” — ถ้าค่านี้ตรงกับของจริง หุ่นจริงจะไถได้ช้าแบบ 0.003 และ policy ควรเทรนให้ถึงค่านี้; ยังไม่มีหุ่นให้ยืนยัน")

put("ex72", slide("ex72", head("Exercise 7.2 · Brake", "สั่งเบรกแล้วเป็ดทำอะไร?", "7.2"),
    code(f'{K("def")} braking_reward(env, command_name, vel_std=0.3):{SP}{C("# mdp.py")}<br>'
         f'{SP}brake = clamp(-cmd_x, min=0)<br>'
         f'{SP}stopped = exp(-(fwd_vel<b>.clamp(min=0)</b> ** 2) / vel_std ** 2)<br>'
         f'{SP}{K("return")} brake * stopped', 27),
    row=[task(["ไถด้วย +0.6 สี่วินาที แล้วสั่ง −0.5",
               "อ่าน reward เบรก: ถ้าเป็ด<b>ถอยหลัง</b> จะได้รางวัลเท่าไร?",
               "รันซ้ำที่แรงเสียดทาน 0, 0.0015, 0.003",
               "ช่องโหว่ใน reward = policy ใช้ช่องโหว่เสมอไหม?"]),
         f'<div style="width:880px;display:flex;flex-direction:column"><img src="{RBRAKE}" alt="Speed over time after brake command for three friction values: 0 and 0.0015 stop near zero, 0.003 rolls backward to minus 0.14" style="width:880px;height:512px;object-fit:contain;border-radius:20px"></div>'],
    at=2))

put("ans72", answer("ans72", "7.2", "ช่องโหว่ใน reward ไม่ได้ถูกใช้เสมอ — จนกว่าโลกจะเปลี่ยน",
    ["<b>.clamp(min=0)</b> ทำให้ความเร็วติดลบนับเป็น “หยุด” → <b>ถอยหลังได้รางวัลเต็ม</b> เท่ากับหยุดนิ่ง",
     "ที่แรงเสียดทานในช่วงที่เทรน (0, 0.0015) เป็ด<b>หยุดจริง</b> ภายใน ~1.5 s ไม่ถอย",
     "ที่ 0.003 (นอกช่วง) เป็ด<b>ถอยหลังต่อเนื่อง</b> ถึง −0.14 m/s — พฤติกรรมแฝงที่ reward อนุญาต โผล่เมื่อซิมออกนอกช่วง",
     "แก้: ใช้ exp(−fwd_vel² / std²) ไม่ clamp ให้ถอยหลังเสียคะแนนเท่ากับไปหน้า (ยังไม่ได้เทรนทดสอบ)"],
    side=video("roller", "Roller pushing then braking", 760, 430) + p("roller.onnx ไม่ระบุว่าเทรนจาก cfg รุ่นไหน — คำอธิบายนี้อิง reward ใน repo ปัจจุบัน", 24, "#4A5563"),
    summary="ทดสอบนอกช่วงที่เทรนเป็นวิธีขุดหาพฤติกรรมที่ reward แอบอนุญาตไว้", side_w=760))

rt = RES["roller_train"]
put("ex73", slide("ex73", head("Exercise 7.3 · Train it yourself", "เทรนเป็ดล้อเองบน 6 GB", "7.3"),
    code(f'{G} uv run train Mjlab-Velocity-Flat-MicroDuck-Rollers --env.scene.num-envs 4096 \\<br>{SP}--agent.max-iterations 1000 --agent.logger tensorboard', 26),
    row=[task(["วัด VRAM และเวลาต่อ iteration ที่ 4,096 envs",
               "ดู Episode_Reward/wheel_speed กับ fell_over ทุก 100 iterations",
               "export แล้วสั่ง 0.4 ที่แรงเสียดทาน 0 — ไถได้ไหม?",
               "curriculum ของ Pollen ยาวถึง iteration 5,000 — เราอยู่ตรงไหน?"]),
         result(bigrow(big(rt["vram"], "VRAM ที่ 4,096 envs"), big(rt["time"], rt["time_label"])) + p(rt["headline"], 28))],
    at=2))

put("ans73", answer("ans73", "7.3", rt["title"], rt["answers"],
    side=(f'<img src="{B(rt["curve_blob"])}" alt="{rt["curve_alt"]}" style="width:860px;height:520px;object-fit:contain;border-radius:16px">' if rt.get("curve_blob") else ""),
    summary=rt["summary"], side_w=860), rt.get("notes"))

put("r-ours", slide("r-ours", head("roller_1000.onnx · ของเราเอง", "ดูวิดีโอแล้วจะเห็นสิ่งที่ตัวเลขไม่บอก"),
    row=[video("roller_ours", "Our roller policy skating with head bowed and legs splayed, then falling when told to coast", 820, 620),
         card("เทียบกับตัวทางการ", p("<b>ก้มหัวต่ำ</b> ใช้หัวเป็นตัวถ่วง", 30)
              + p("<b>กางขา ตะกุยทั้งสองใบ</b> ไม่เคยไถบนใบเดียว (glide = 0)", 30)
              + p("ที่ t = 6 s สั่ง coast (0) → <b>ล้มภายใน 1 วินาที</b>", 30)
              + p("แรงเสียดทานล้อ 0.0015 · คำสั่ง +0.4 ไถได้ 0.32 m/s", 26, "#4A5563"))],
    at=1))

# ================================================================ WEEK 8 · NEW SKILL
put("sec-w8", section("sec-w8", "Week 8 · New skill", "ออกแบบ<br>ท่าใหม่", "จากไอเดีย → reward → ตรวจฟิสิกส์ → smoke test → เทรน — ทำครบวงจรบน Newton ใน 1 คาบ", SIDE, "Microduck side view"))

steps = ""
for n, (t, d) in enumerate([("เลือก template", "ท่าเดิน → velocity · จบที่ท่า → standup · สองสถานะ → sitstand · ท่าเร็ว → roulade"),
                            ("ตรวจฟิสิกส์ก่อนเทรน", "ท่าเป้าหมายต้องเป็นจุดสมดุลจริง — ท่ายืน kp 0.55 ไม่ใช่ (ล้มเองทุกครั้ง)"),
                            ("เขียน cfg test", "เครื่องหมาย weight · index ข้อต่อ · obs 61 มิติ"),
                            ("smoke test", "64 envs × 5 iterations จับ config ผิดได้ ~95%"),
                            ("เทรนแล้วอ่าน log", "คาดไว้เลยว่าต้องไล่ reward hacking 2–5 รอบ")]):
    steps += (f'<div style="flex:1;background:#FBFAF6;border:1px solid #DDDBD2;border-radius:24px;padding:32px 28px;display:flex;flex-direction:column;gap:14px">'
              f'<p style="{H};font-size:56px;font-weight:600;color:#B85C00;line-height:1">{n + 1}</p>'
              f'<h3 style="{H};font-size:34px;font-weight:600;color:#0E1621;line-height:1.15">{t}</h3>'
              f'<p style="font-size:27px;color:#1B2430;line-height:1.4">{d}</p></div>')
put("s-workflow", slide("s-workflow", head("AGENTS.md ของ Pollen · Building a new env", "5 ขั้นก่อนเทรนท่าใหม่"),
    f'<div style="flex:1;display:flex;flex-direction:row;gap:20px">{steps}</div>',
    think("ข้อ 2 ช่วยประหยัดเวลามากที่สุดตาม AGENTS.md: “ความสูงเป้าหมายผิด 5 mm เคยทำให้งานเป็นไปไม่ได้อยู่หลายวัน”"),
    at=1))

put("s-design", slide("s-design", head("ท่าใหม่: หันหัวมองเป้าขณะเดิน", "ใช้ช่อง obs ที่มีอยู่แล้ว ไม่ต้องเปลี่ยน 61 มิติ"),
    code(f'{K("class")} HeadTargetObs(ManagerTermBase):{SP}{C("# ช่อง head_pose 4 ช่อง (เดิมเป็นศูนย์)")}<br>'
         f'{SP}pitch ~ U(±0.4), yaw ~ U(±0.8) rad · สุ่มใหม่ทุก 2–4 s · <b>20% = มองตรง</b><br><br>'
         f'{K("def")} head_tracking(env, std=0.15):{SP}{C("# weight +1.5")}<br>'
         f'{SP}{K("return")} exp(-‖q_head − (default + target)‖² / std²)', 27),
    row=[card("ทำไม 20% มองตรง", p("AGENTS.md: “พฤติกรรมตอนคำสั่งเป็นศูนย์ต้องฝึกตรง ๆ” — สุ่มแบบ uniform แทบไม่เคยได้ศูนย์พอดี ซึ่งคือสถานะที่ใช้บ่อยที่สุดตอนใช้งานจริง", 29)),
         card("ทำไมไม่ใช้ช่องใหม่", p("ทุก policy ของ Pollen ใช้ obs 61 มิติชุดเดียว → สลับกันได้ใน runtime ช่องที่ไม่ใช้ <b>ใส่ศูนย์ ห้ามลบ</b>", 29))],
    at=2), "โค้ดอยู่ใน newton_port/isaaclab_task/microduck_tasks.py (task Microduck-HeadTrack-Flat-Newton) · HEAD_V=1 เก็บ penalty head_still ไว้, HEAD_V=2 ลบออก")

ht = RES["head"]
put("ex81", slide("ex81", head("Exercise 8.1 · Conflicting rewards", "เพิ่ม reward ใหม่ แต่ลืมลบ penalty เก่า — พังไหม?", "8.1"),
    code(f'{G} cd ~/IsaacLab && HEAD_V=1 uv run python .../train.py --task Microduck-HeadTrack-Flat-Newton \\<br>{SP}--num_envs 4096 physics=newton_mjwarp agent.max_iterations=1000{SP}{C("# v1: head_still −0.5 ยังอยู่")}<br>'
         f'{G} HEAD_V=2 ...{SP}{C("# v2: ลบ head_still ออก")}', 25),
    row=[task(["v1: เพิ่ม head_tracking (+1.5) แต่ <b>head_still (−0.5)</b> ที่ลงโทษการขยับหัวยังอยู่",
               "v2: ลบ head_still ออก",
               "เทรนอย่างละ 1,000 iterations แล้ววัดว่าหัวคลาดกี่องศา — policy เลือกทางไหน?",
               "ป้อนเป้าหัวให้ policy เดิมที่ไม่เคยเห็นช่องนี้ — เกิดอะไรขึ้น?"]),
         result(bigrow(big(ht["v1_err"], "v1 คลาดเฉลี่ย (yaw)", "#B85C00"), big(ht["v2_err"], "v2 คลาดเฉลี่ย (yaw)")) + p(ht["headline"], 28))],
    at=2))

put("ans81", answer("ans81", "8.1", ht["title"], ht["answers"],
    side=table(ht["table"], ["", "v1 (มี head_still)", "v2 (ลบแล้ว)"], size=26),
    summary=ht["summary"], side_w=860), ht.get("notes"))

if "head" in VID:
    put("s-video", slide("s-video", head("Newton · ท่าใหม่หลังเทรน 1,000 iterations", "เดินไปพร้อมหันหัวตามเป้า", ),
        video("head", "Ducks walking while turning their heads toward random targets", 1696, 600),
        p(ht["video_caption"], 30, "#4A5563"), at=1))

put("next", f'''<section id="next" data-transition="fade" style="{NAVY};padding:128px;display:flex;flex-direction:row;gap:64px;align-items:center">
<div style="flex:1;display:flex;flex-direction:column;gap:32px">
<p style="font-size:24px;letter-spacing:3px;text-transform:uppercase;color:#7AC943;font-weight:600">Next · Week 9</p>
<h1 style="{H};font-size:100px;font-weight:600;line-height:1.05;color:#F4F3EE">มอเตอร์ตัวเดียว ก่อนทั้งหุ่น</h1>
<p style="font-size:36px;color:#B8C4D0;line-height:1.45">test bench XL330 ใน repo: เทรน task ข้อต่อเดียว แล้วเทียบซิมกับมอเตอร์จริงผ่าน USB — ทำได้ก่อนหุ่นมาถึง</p>
<div style="display:flex;flex-direction:row;gap:16px">
<p style="font-size:26px;background:#7AC943;color:#0E1621;padding:10px 22px;border-radius:40px;font-weight:600">testbench_sim2real.py</p>
<p style="font-size:26px;border:2px solid #3A4A5C;color:#B8C4D0;padding:8px 22px;border-radius:40px">BAM m6</p>
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
