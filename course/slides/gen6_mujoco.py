"""Microduck deck 5 — Duck Adventure (ด่านตะลุย). Usage: gen6.py <deck_root> [ids...]"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from common4 import *  # noqa: F401,F403
from common4 import slides, order

HERE = os.path.dirname(__file__)
BL = json.load(open(os.path.join(HERE, "blobs6.json")))
R = json.load(open(os.path.join(HERE, "results6.json")))
I = lambda k: B(BL[k])
POLS = [("walk", "walk_2000", "Flat"), ("rough", "rough_ft", "Rough 1.5 cm"), ("velstand", "velstand", "ทางการ Pollen"), ("climb", "climb35", "Rough 3.5 cm (ของเรา)")]
LVS = [("adv10", "10 mm"), ("adv20", "20 mm"), ("adv30", "30 mm")]


def vid(still, clip, alt, w, h):
    return f'<img src="{I(still)}" data-video="{I(clip)}" alt="{alt}" style="width:{w}px;height:{h}px;object-fit:cover;border-radius:20px">'


def cell(pol, lv):
    r = R.get(f"{pol}_{lv}")
    if r is None: return "—"
    if r["finish"]: return f'<b style="color:#1F4D06">เข้าเส้น {r["finish"]:.0f} s</b> · ล้ม {r["falls"]}'
    return f'ถึง {r["reached"]} · ล้ม {r["falls"]}'


def stuck(r):
    return f"ติดที่ x = {r['end_x']:.2f} ม."


# ================================================================ cover
put("cover", f'''<section id="cover" data-transition="fade" style="{NAVY};padding:128px 128px 110px;display:flex;flex-direction:column;gap:48px">
<div style="display:flex;flex-direction:column;gap:24px">
<p style="font-size:24px;letter-spacing:3px;text-transform:uppercase;color:#7AC943">Engineering Workshop · ภาคพิเศษของ Module 4</p>
<h1 style="{H};font-size:130px;font-weight:600;line-height:1.02;color:#F4F3EE">Duck Adventure</h1>
<p style="font-size:40px;color:#B8C4D0;line-height:1.4">ด่านตะลุย 5 โซน · checkpoint · จับเวลา · ใครปีนภูเขาได้สูงสุด</p>
</div>
<img src="{I('overview')}" alt="Whole adventure course: cones, lava bridge, stair mountain, rocks, swing doors" style="width:1664px;height:460px;object-fit:cover;border-radius:24px">
</section>''', "Module 4 สร้างด่านเพื่อวัดผล ภาคนี้เอาด่านมาต่อกันเป็นเกม: ผ่าน checkpoint ตามลำดับ ล้มแล้วเกิดใหม่ จับเวลา — และใช้เกมเป็นตัววัดว่า policy ไหนไปได้ไกลแค่ไหน")

# ================================================================ map of zones
zones = [("①", "สลาลอมกรวย", "เลี้ยวซ้ายขวาสลับ · ชนกรวย +2 s", "ทดสอบ: คำสั่งเลี้ยว"),
         ("②", "สะพานข้ามลาวา", "กว้าง 18 ซม. หักมุมกลางสะพาน · ออกนอกสะพาน = เกิดใหม่", "ทดสอบ: เดินตรงแม่น"),
         ("③", "ภูเขาบันได", "3 ขั้น สูงขั้นละ H (10 / 20 / 30 mm) · ลงทางลาด 5°", "ทดสอบ: ยกเท้า"),
         ("④", "ทุ่งหิน", "แผ่น 10 ซม. สูงสุ่ม 1–8 mm", "ทดสอบ: พื้นไม่เรียบ"),
         ("⑤", "ประตูสวิงคู่", "บานละ 22 ซม. มีสปริงดึงปิด ต้องเดินดันเปิด", "ทดสอบ: ถูกผลัก")]
zc = "".join(f'<div style="flex:1;background:#FBFAF6;border:1px solid #DDDBD2;border-radius:24px;padding:28px 26px;display:flex;flex-direction:column;gap:12px">'
             f'<p style="{H};font-size:52px;font-weight:600;color:#B85C00;line-height:1">{n}</p>'
             f'<h3 style="{H};font-size:36px;font-weight:600;color:#0E1621">{t}</h3>{p(d, 26)}<div style="flex:1"></div>{p(k, 26, "#3D7A12", ";font-weight:600")}</div>'
             for n, t, d, k in zones)
put("zones", slide("zones", head("playground/make_adventure.py", "5 โซน แต่ละโซนทดสอบคนละทักษะ"),
    f'<img src="{I("overview")}" alt="Course overview" style="width:1696px;height:330px;object-fit:cover;border-radius:20px">',
    f'<div style="flex:1;display:flex;flex-direction:row;gap:18px">{zc}</div>', at=2),
    "ด่านยาว 7.3–8.0 ม. แล้วแต่ความสูงภูเขา · checkpoint = วงเขียว (CP1 ก่อนสะพาน, CP2 หลังสะพาน, CP3 บนยอดเขา, CP4 หลังทุ่งหิน) · เส้นชัย = วงเหลือง")

# ================================================================ how to play
rules = [["ข้ามเส้นวงเขียวตามลำดับ", "บันทึก checkpoint (กว้าง ±30 ซม.)"], ["เอียงเกิน ~55° นาน 0.5 s", "ล้ม → เกิดใหม่ที่ checkpoint ล่าสุด"],
         ["ตัวออกนอกสะพาน", "ตกลาวา → เกิดใหม่"], ["ชนกรวย", "+2 s ต่อกรวย"], ["เกิน 180 s", "หมดเวลา"]]
put("play", slide("play", head("playground/ctl_adventure.py · sim_play.py --live", "เล่นเอง หรือให้ autopilot เล่น"),
    code(f'{G} python playground/make_adventure.py adv20 H=0.02 soft{SP}{C("# สร้างด่าน + ไฟล์กติกา .json")}<br>'
         f'{G} ADV=…/adv20.json AUTO=0 python playground/sim_play.py <b>--live</b> --ctl playground/ctl_adventure.py \\<br>'
         f'{SP}-- --walking exports/rough_ft.onnx --new-cmd-obs --scene …/scene_adv20.xml<br>'
         f'{C("# ↑ คนบังคับ: กดลูกศร ↑↓←→ ในเทอร์มินัล · ↓ autopilot: ไม่เปิดจอ วิ่งเร็วกว่าเวลาจริง")}<br>'
         f'{G} ADV=… AUTO=1 python playground/sim_play.py --secs 180 --ctl playground/ctl_adventure.py -- …', 26),
    row=[f'<div style="flex:1;display:flex;flex-direction:column">' + table(rules, ["กติกา", "ผล"], size=28) + '</div>',
         card("autopilot ทำอะไร", p("เล็งหัวไปที่ waypoint ถัดไป แล้วสั่ง vx 0.4 (โซนยาก 0.3) กับ ωz ตามมุมที่คลาด", 29)
              + p("ωz ขั้นต่ำ 0.5 rad/s — คำสั่งเลี้ยวเล็ก ๆ policy ไม่ตอบสนองเลย (โซนตาย แบบเดียวกับแอปเตะบอล)", 29)
              + p("ทุกคนได้ autopilot เดียวกัน → เปรียบเทียบ policy ได้ยุติธรรม", 29, "#3D7A12"))],
    at=2), "--live เปิด viewer จริงและอ่านปุ่มจากเทอร์มินัล กติกาเกมทำงานทุก step เหมือนโหมด autopilot; ทดสอบแล้วว่าเปิดได้และเดินถึง CP1 ในหน้าต่างจริง")

# ================================================================ Ex A.1 race
put("exA1", slide("exA1", head("Exercise A.1 · Race", "ด่าน 10 mm: policy ไหนเข้าเส้นชัยได้?", "A.1"),
    code(f'{G} for pol in walk_2000 rough_ft official/velstand; do ADV=…/scene_adv10.json ADV_OUT=$pol.json \\<br>'
         f'{SP}python playground/sim_play.py --secs 180 --ctl playground/ctl_adventure.py -- --walking exports/$pol.onnx --new-cmd-obs --scene …/scene_adv10.xml; done', 25),
    row=[task(["รัน autopilot กับ 3 policy บนด่าน H = 10 mm",
               "จดเวลา จำนวนล้ม และ checkpoint สุดท้าย",
               "ดู x ตอนล้ม (มีใน log) แล้วบอกว่าล้มที่โซนไหน",
               "ทำนายก่อนรัน: policy Flat จะผ่านโซนไหนไม่ได้?"]),
         f'<div style="width:880px;display:flex;flex-direction:column">' + vid("still_rough", "vid_rough", "rough_ft finishing the 10 mm course", 880, 540) + '</div>'],
    at=2), "วิดีโอ: rough_ft บนด่าน 10 mm เร่ง 4 เท่า แถบบนแสดงเวลาในซิม checkpoint ล่าสุด และจำนวนล้ม")

w, r, v = R["walk_adv10"], R["rough_adv10"], R["velstand_adv10"]
put("ansA1", answer("ansA1", "A.1", "ไม่มี policy ไหนชนะทุกโซน",
    [f"<b>rough_ft</b> เข้าเส้น {r['finish']:.0f} s ล้ม {r['falls']} ครั้ง — ล้มที่บันได (x ≈ {', '.join(f'{x:.1f}' for x in r['fall_x'][:2])}) แต่ผ่านประตูได้",
     f"<b>walk_2000</b> (Flat) ข้ามภูเขาได้ ล้มที่ทุ่งหิน {sum(x < 6.2 for x in w['fall_x'])} ครั้ง แล้วล้มหน้าประตูอีก {sum(x >= 6.2 for x in w['fall_x'])} ครั้งจนหมดเวลา — ถูกบานประตูผลักแล้วรับไม่อยู่",
     f"<b>velstand</b> ไม่ล้มเลย แต่<b>หยุดนิ่ง</b>หน้าขั้นที่ 2 ({stuck(v)}) จนหมดเวลา — ตรงกับ Ex 4.1: velstand ผ่านขั้น 20 mm แต่ค้างที่ขั้น 5–15 mm",
     "ทั้ง 3 ตัวผ่านสลาลอมและสะพานได้ ไม่ชนกรวย ไม่ตกลาวา — โซนที่แยก policy ออกจากกันคือภูเขาและประตู"],
    side=table([["walk_2000", cell("walk", "adv10")], ["rough_ft", cell("rough", "adv10")], ["velstand", cell("velstand", "adv10")]], ["policy", "H = 10 mm"], size=32)
         + p("autopilot เดียวกัน · จุดเริ่มเดียวกัน · รัน 1 ครั้งต่อช่อง (ซิม deterministic — รันซ้ำได้ผลเดิม)", 26, "#4A5563"),
    summary="ด่านรวมหลายโซนเห็นจุดอ่อนที่ด่านเดี่ยวไม่เห็น — walk_2000 ผ่านขั้น 10 mm ใน Ex 4.1 แต่แพ้ประตู", side_w=720))

# ================================================================ Ex A.2 mountain
put("exA2", slide("exA2", head("Exercise A.2 · How high?", "ภูเขา 10 → 20 → 30 mm: ใครยังปีนได้?", "A.2"),
    code(f'{G} for h in 0.01 0.02 0.03; do python playground/make_adventure.py adv$h H=$h soft; done{SP}{C("# 3 ด่าน")}', 26),
    row=[task(["รัน 3 policy × 3 ความสูง (9 รอบ)",
               "ใส่ผลในตาราง: เข้าเส้น / checkpoint สุดท้าย / จำนวนล้ม",
               "เป็ดยกเท้าได้ประมาณ 1–2 ซม. — ขั้น 30 mm ควรเป็นไปได้ไหม?",
               "ทำไม velstand ผ่าน 20 mm แต่ไม่ผ่าน 10 mm?"]),
         f'<div style="width:880px;display:flex;flex-direction:column">' + vid("still_velstand", "vid_velstand", "velstand climbing the 20 mm mountain", 880, 540) + '</div>'],
    at=2), "วิดีโอ: velstand บนด่าน 20 mm ล้มบนภูเขาหลายรอบก่อนจะข้ามได้ แล้ววิ่งต่อจนเข้าเส้น")

rows = [[n] + [cell(k, lv) for lv, _ in LVS] for k, n, _ in POLS[:3]]
put("ansA2", answer("ansA2", "A.2", "ขั้น 30 mm ยังไม่มีใครผ่าน",
    [f"ที่ 20 mm มีแค่ <b>velstand</b> เข้าเส้น ({R['velstand_adv20']['finish']:.0f} s, ล้ม {R['velstand_adv20']['falls']}) — walk_2000 กับ rough_ft ล้มที่บันไดซ้ำ {R['walk_adv20']['falls']} และ {R['rough_adv20']['falls']} ครั้ง",
     f"ที่ 30 mm ทุกตัวติดที่ CP2 (ตีนภูเขา) — velstand ล้ม {R['velstand_adv30']['falls']} ครั้งแล้ว{stuck(R['velstand_adv30'])}",
     "velstand ยกเท้าสูงกว่าตัวอื่น (เทรนบนพื้นที่มีขั้น + ท่ายืนนิ่ง) แต่ที่ 10 mm มันหยุดหน้าขั้นเอง ไม่ใช่ล้ม — อาการนี้ยังไม่รู้สาเหตุแน่ชัด",
     "ขั้น 30 mm = 1.5–3 เท่าของความสูงยกเท้า → ต้องเทรนเพิ่ม ไม่ใช่แค่จูนคำสั่ง (Ex A.3)"],
    side=table(rows, ["policy"] + [n for _, n in LVS], size=27) + p("ทุกช่องรัน 180 s · ‘ถึง CPx’ = checkpoint สุดท้ายตอนหมดเวลา · CP2 = ตีนภูเขา", 24, "#4A5563"),
    summary="ความสูงขั้นคือเพดานจริงของ policy เดิน — เส้นชัยวัดได้ชัดกว่าค่า reward", side_w=900))

# ================================================================ bugs while building the game
bugs = [["ทางลาดกลายเป็นหน้าผา", "robot xml ตั้ง <code>compiler angle=\"radian\"</code> — euler=\"0 5 0\" คือ 5 เรเดียน", "ยิง ray วัดความสูงพื้นทุก 3 ซม."],
        ["ผ่านยอดเขาแล้วไม่นับ CP3", "วงรัศมี 12 ซม. — เป็ดเดินเฉ ๆ พลาดวง", "เปลี่ยนเป็น “ข้ามเส้น” กว้าง ±30 ซม."],
        ["เป็ดหมุนตัวอยู่กับที่", "waypoint อยู่ข้างตัว 12 ซม. — หันไปก็เดินไม่ถึง", "นับว่าผ่านเมื่อเลยแนว x"],
        ["ติดหลังประตูทั้งที่ไม่ล้ม", "บานยาวกว่ากำแพง ปลายบานเกี่ยวขา", "ประตูคู่ บานสั้น เปิดแล้วแนบกำแพง"]]
put("bugs", slide("bugs", head("ระหว่างสร้างเกม", "ด่านพังก่อนเป็ดพัง — 4 บั๊กที่เจอจริง"),
    table(bugs, ["อาการ", "สาเหตุ", "วิธีหา / แก้"], size=27),
    think("ทุกบั๊กดูเหมือน “policy แย่” ในตอนแรก — ล้มที่ทางลาด ไม่ถึงเส้นชัย ติดหน้าประตู · ก่อนโทษ policy ให้ตรวจด่านและกติกาก่อน: วัดพื้น ดูวิดีโอ ดู trace ตำแหน่ง"),
    p("ผลข้างเคียง: เวอร์ชันประตูบานเดียว walk_2000 เข้าเส้นได้ใน 43.5 s — พอเปลี่ยนเป็นประตูคู่กลับล้มที่ประตู · ด่านต่างนิดเดียว ผลต่างได้มาก", 27, "#4A5563"),
    at=1), "make_course.py slope= จาก Module 4 มีบั๊กเรเดียนเดียวกัน (แก้แล้ว) — ผลใน Module 4 ไม่ได้ใช้ทางลาดจึงไม่กระทบ")

# ================================================================ Ex A.3 train a climber
ctr = R.get("climb_meta", {})
put("exA3", slide("exA3", head("Exercise A.3 · Train a climber", "เทรนต่อบนบันไดสูงขึ้น แล้วกลับมาปีนภูเขา", "A.3"),
    code(f'{G} MICRODUCK_STAIR_MAX=0.035 uv run train Mjlab-Velocity-Rough-MicroDuck --env.scene.num-envs 1024 \\<br>'
         f'{SP}--agent.max-iterations 1000 --agent.resume True --agent.load-run …rough_ft --agent.load-checkpoint model_2998.pt{SP}{C("# ~40 นาที")}', 25),
    row=[task(["เพิ่ม env var ให้ step_height_range ปรับได้ (ค่าเดิม 1.5 cm)",
               "เทรนต่อจาก rough_ft บนบันไดสูงสุด 3.5 cm อีก 1,000 รอบ",
               "export แล้วรัน Ex A.2 ซ้ำทั้ง 3 ความสูง",
               "ดู Curriculum/terrain_levels ใน log — ระดับขึ้นหรือลง?"]),
         card("อ่าน log ให้ดี", p("terrain_levels ลดจาก 2.4 เหลือ ~0 ทั้งรอบนี้และรอบ rough_ft — กฎเลื่อนขั้นต้องเดินไกล 4 ม. ใน 20 s ซึ่งเป็ดทำไม่ได้", 28)
              + p("แต่ไม่ได้แปลว่าเทรนบนพื้นเรียบ: terrain generator อยู่โหมดสุ่ม ทุกแผ่นสุ่มความยากเอง ไม่ขึ้นกับแถว", 28)
              + p("และพีระมิดบันไดให้เกิดบนยอด — ส่วนใหญ่เป็ดฝึก<b>ลง</b>บันได", 28, "#8A4300"))],
    at=2), "mjlab terrain_levels_vel: move_up = เดินไกลกว่า size/2 (4 ม.), move_down = เดินได้น้อยกว่าครึ่งของ |คำสั่ง|·20 s · TerrainGeneratorCfg.curriculum = False ใน MICRODUCK_ROUGH_TERRAINS_CFG")

crow = [[n] + [cell(k, lv) for lv, _ in LVS] for k, n, _ in POLS if k in ("rough", "velstand", "climb")]
put("ansA3", answer("ansA3", "A.3", R.get("climb_title", "ผลนักปีน"),
    R.get("climb_answers", ["(รอผลเทรน)"]),
    side=table(crow, ["policy"] + [n for _, n in LVS], size=27),
    summary=R.get("climb_summary", ""), side_w=900))

# ================================================================ challenge
chal = [("ออกแบบโซนใหม่", "ไม้กระดก · ทางแคบซิกแซก · ลูกบอลกลิ้งขวาง — เพิ่มใน make_adventure.py แล้วแลกด่านกับทีมอื่น", "โซนที่ดีแยก policy ออกจากกันได้ — ถ้าทุกตัวผ่านหรือทุกตัวตก โซนนั้นไม่ได้วัดอะไร"),
        ("ทำลายสถิติ", "policy เดิม เปลี่ยนได้แค่ ctl: ความเร็ว เส้นทาง จังหวะชะลอก่อนบันได", "autopilot ตอนนี้ใช้ vx 0.4 ทั้งด่าน — ชะลอก่อนขั้นอาจล้มน้อยลง"),
        ("policy ผสม", "velstand บนภูเขา · rough_ft ที่ทุ่งหินและประตู — สลับตาม x ของเป็ด", "obs 61 มิติเหมือนกันทุกตัว จึงสลับ ONNX กลางทางได้ (Module 3) — ยังไม่ได้ลองในด่านนี้")]
put("challenge", slide("challenge", head("Challenge", "แข่งกันทั้งห้อง"),
    f'<div style="flex:1;display:flex;flex-direction:row;gap:28px">' + "".join(card(t, p(d, 30) + '<div style="flex:1"></div>' + p(k, 27, "#3D7A12")) for t, d, k in chal) + '</div>',
    table([["คะแนน", "เวลาในซิม + โทษ (ชนกรวย +2 s) · ไม่เข้าเส้น = นับ checkpoint ก่อน แล้วค่อยเวลา"],
           ["สถิติปัจจุบัน", f"H 10 mm: rough_ft {R['rough_adv10']['finish']:.0f} s · H 20 mm: velstand {R['velstand_adv20']['finish']:.0f} s · H 30 mm: " + (f"{R['climb_adv30']['finish']:.0f} s" if R.get('climb_adv30', {}).get('finish') else "ยังไม่มีใครเข้าเส้น")]],
          ["", ""], size=27),
    at=1))

OUT = sys.argv[1]
only = sys.argv[2:] or order
os.makedirs(f"{OUT}/project/slides", exist_ok=True)
for sid in only:
    open(f"{OUT}/project/slides/{sid}.html", "w").write(slides[sid])
json.dump(order, open(f"{OUT}/order.json", "w"))
print("wrote", len(only), "slides")
