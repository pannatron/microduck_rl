# ================================================================ MODULE 6 · NEWTON
NSCALE = B("5073eca3b7217e042622884779ba2b96")
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

put("n-bug", slide("n-bug", head("ไล่หาความต่างทีละ step", "เป็ดเดินช้าลง 35% บน Newton — เพราะอะไร?"),
    row=[card("1 · gyro เร็วกว่า 25%", p("step 0 obs ตรงกันเป๊ะ แต่ step 1 gyro ของ Newton สูงกว่า 1.25 เท่า: <b>mj_step คำนวณ sensor ก่อน integrate</b> → gyro/xquat ของ MuJoCo ช้าไป 1 substep (5 ms) และ policy ถูกเทรนกับค่าที่ช้านั้น", 29)),
         card("2 · จำนวนจุดสัมผัส", p("แก้ข้อ 1 แล้ว step 1–2 ตรงกัน 0.00000 แต่ step 3 (เท้าแตะพื้น) แยกทาง: ยืนนิ่ง MuJoCo CPU ให้ <b>4 จุด/เท้า</b>, MuJoCo Warp (ที่ใช้เทรน) <b>10 จุด/เท้า</b>", 29)),
         card("3 · สิ่งที่ไม่ใช่", p("ตัด integrator, solver iterations, self-collision ทิ้งแล้ว — ผลไม่เปลี่ยน model ที่ Newton แปลงมีค่า kp, damping, armature, friction, solref <b>ตรงกันทุกตัว</b>", 29))],
    think("ซิมที่ Pollen ใช้ซ้อมก่อนลงหุ่น (MuJoCo CPU) <b>ไม่ได้ตรงกับซิมที่ใช้เทรน</b> ด้วยซ้ำ — sim-to-sim gap มีอยู่แล้วก่อนเราแตะ Newton"),
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

put("ans61", answer("ans61", "6.1", "ซิมต่างกันได้ ±35% แต่ “นิสัย” ของ policy ตามไปทุกซิม",
    ["ความเร็วที่ cmd 0.3 แกว่ง <b>0.09–0.21 m/s</b> ตามซิม — ไม่มีซิมไหนเร็วกว่าเสมอ (walk_2000 เร็วสุดใน CPU no-BAM, ที่เหลือเร็วสุดใน Newton)",
     "สั่ง 0.2 แล้ว<b>ยืนนิ่งทั้ง 3 ซิม</b> สำหรับ walk_2000, alpha_walking, rough_ft → เป็นนิสัยของ policy ไม่ใช่บั๊กซิม (ตอบสมมติฐานค้างจาก Ex 1.2)",
     "velstand เดินที่ 0.2 ได้ทุกซิม (0.06–0.09) — เพราะถูกเทรนให้รวมยืน+เดินในตัวเดียว",
     "บน Newton ไม่มีเป็ดล้มเลยใน 4,096 ตัว × 4 policy — ความเสถียรข้ามซิมได้ แต่ <b>ความเร็วไม่ข้าม</b>"],
    side=table([["0.2", "0 / 0 / 0", "0.09 / 0.06 / 0.08"], ["0.25", "0.12 / 0.11 / 0.11", "0.11 / 0.07 / 0.09"],
                ["0.3", "0.13 / 0.15 / 0.21", "0.13 / 0.09 / 0.11"], ["0.4", "0.26 / 0.23 / 0.28", "0.16 / 0.13 / 0.15"]],
               ["cmd", "walk_2000", "velstand"], size=26) + p("ค่าในช่อง = Newton / CPU+BAM / CPU no-BAM (m/s)", 26, "#4A5563"),
    summary="ก่อนลงหุ่น ให้รายงานความเร็วเป็นช่วงจากหลายซิม ไม่ใช่ตัวเลขเดียว", side_w=820))

scale = [["mjlab (MuJoCo Warp)", "4,096", "3.02", "5.0 GB", "33k"], ["Newton", "1,024", "0.39", "0.6 GB", "63k"],
         ["Newton", "4,096", "0.74", "1.4 GB", "133k"], ["Newton", "8,192", "1.25", "2.5 GB", "158k"],
         ["Newton", "16,384", "2.23", "4.7 GB", "176k"], ["Newton", "32,768", "—", "OOM", "—"]]
put("n-train", slide("n-train", head("Isaac Lab + Newton · Microduck-Walk-Flat-Newton", "เทรนบน Newton: เป็ด 16,384 ตัวในการ์ด 6 GB"),
    row=[f'<div style="flex:1;display:flex;flex-direction:column;gap:24px">' + table(scale, ["ซิม", "envs", "s/iter", "VRAM", "steps/s"], size=27, hi=2)
         + p("obs 61 มิติลำดับเดียวกับ Pollen · action = default + 1.0×a · PD kp 0.55 ±0.96 Nm · MuJoCo contacts · 50 Hz", 27, "#4A5563") + '</div>',
         f'<img src="{NSCALE}" alt="Env steps per second: mjlab 33k at 4096 envs; Newton 63k, 133k, 158k, 176k at 1k to 16k envs" style="width:800px;height:470px;object-fit:contain;border-radius:20px">'],
    think("<b>ไม่ใช่การเทียบแบบยุติธรรม 100%</b>: mjlab ของ Pollen มีโมเดลมอเตอร์ BAM, DR หลายชั้น, reward ~20 เทอม — ของเราเป็น PD ธรรมดา + reward สูตร G1 13 เทอม ส่วนต่างความเร็วจึงมาจากทั้ง engine และงานที่น้อยกว่า"),
    at=1), "2,000 iterations ที่ 4,096 envs ใช้ 25 นาที (mjlab 1 ชม. 38 นาที) ไฟล์ task: newton_port/isaaclab_task/microduck_tasks.py รันจาก ~/IsaacLab ด้วย train.py ... physics=newton_mjwarp")

put("ex62", slide("ex62", head("Exercise 6.2 · Train on Newton, test on MuJoCo", "เทรนบน Newton แล้วเอาไปเดินใน MuJoCo", "6.2"),
    code(f'{G} cd ~/IsaacLab && uv run python ~/repos/microduck_rl/newton_port/isaaclab_task/train.py \\<br>{SP}--task Microduck-Walk-Flat-Newton --num_envs 4096 physics=newton_mjwarp agent.max_iterations=2000<br>'
         f'{G} .venv/bin/python newton_port/ckpt2onnx.py &lt;run&gt;/model_1999.pt exports/newton_walk_2000.onnx<br>'
         f'{G} uv run scripts/infer_policy.py --walking exports/newton_walk_2000.onnx --new-cmd-obs --lin-vel-x 0.3', 25),
    row=[task(["เทรน 2,000 iterations (25 นาที) — ดู error_vel_xy ระหว่างเทรน",
               "รันใน Newton ทั้งแบบ gyro ปกติ และแบบช้า 1 substep (<b>--sensor-lag</b>)",
               "รันใน MuJoCo CPU ทั้ง BAM และ --no-bam (มันไม่เคยเห็น BAM)",
               "สั่ง 0.1 ได้ไหม? สั่ง 0.4 ล้มไหม?"]),
         result(bigrow(big("0.03", "error_vel_xy ตอนเทรน (m/s)"), big("0.25–0.28", "ที่ cmd 0.3 ทุกซิม")) + p("สั่ง 0.1 แล้วเดินได้ (0.13–0.15) — ไม่มีโซนตายแบบ policy ของ Pollen", 28))],
    at=2))

put("ans62", answer("ans62", "6.2", "ข้ามซิมได้ แต่ 5 ms ของ sensor ทำให้ล้ม",
    ["ข้ามจาก Newton ไป MuJoCo CPU ได้ทั้ง BAM และ no-BAM ที่ cmd 0.1–0.3 — แม้ไม่เคยเห็นโมเดลมอเตอร์ BAM เลย",
     "ที่ cmd 0.4: บน Newton แบบเดียวกับตอนเทรนไม่ล้มเลย แต่พอให้ gyro <b>ช้าไป 1 substep</b> แบบ MuJoCo → <b>ล้ม 115 / 256</b> และใน MuJoCo no-BAM ล้มหลัง 4 s",
     "ความเร็วอิ่มตัวที่ ~0.26–0.29 m/s ทุกซิม ทั้งที่สั่ง 0.4 — ต่ำกว่า error 0.03 ตอนเทรนบอก (เฉลี่ยรวมคำสั่งช้า ๆ ซึ่งเยอะกว่า)",
     "บทเรียน: ใส่ <b>delay/latency DR</b> ตอนเทรน (mjlab ของ Pollen มี) — ไม่งั้น timing ต่างกันแค่ 5 ms ก็พอให้ล้ม"],
    side=table([["0.1", "0.13", "0.13", "0.15"], ["0.2", "0.23", "0.26", "0.25"], ["0.3", "0.25", "0.28", "0.26"],
                ["0.4", "0.23 · ล้ม 45%", "0.29", "ล้ม"]], ["cmd", "Newton (lag)", "CPU+BAM", "CPU no-BAM"], size=26),
    summary="เทรนเร็วขึ้น 4 เท่าได้จริง — แต่ความทนทานต้องใส่ลงไปเอง ไม่ได้มากับ engine", side_w=820))

