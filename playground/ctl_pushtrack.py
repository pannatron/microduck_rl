"""ผลักตามเวลา (PUSHES="3 6 9", ขนาด PUSH_V m/s ทิศสุ่ม) แล้วจับว่า "ล้ม" ระหว่างทางไหม ไม่ใช่ดูแค่ตอนจบ
ล้ม = เอียงเกิน ~57° (upright < 0.55) หรือ trunk ต่ำกว่า 5 ซม. — เกณฑ์เดียวกับ newton_port/newton_qa.py"""
import os, math, random, numpy as np
TIMES = sorted(float(x) for x in os.environ.get("PUSHES", "3 6 9").split()); V = float(os.environ.get("PUSH_V", "1.0"))
random.seed(int(os.environ.get("SEED", "0")))
st = dict(min_up=1.0, min_z=1.0, fell_t=None)
def control(t, pol, m, d):
    while TIMES and TIMES[0] <= t:
        TIMES.pop(0); a = random.uniform(0, 2 * math.pi); d.qvel[0] = V * math.cos(a); d.qvel[1] = V * math.sin(a)
    x, y = d.qpos[4], d.qpos[5]; up = 1 - 2 * (x * x + y * y)
    if t > 1:
        st["min_up"] = min(st["min_up"], up); st["min_z"] = min(st["min_z"], d.qpos[2])
        if (up < 0.55 or d.qpos[2] < 0.05) and st["fell_t"] is None: st["fell_t"] = round(t, 2)
    return []
def report(m, d):
    x, y = d.qpos[4], d.qpos[5]
    print(f"PUSHTRACK fell_t={st['fell_t']} min_up={st['min_up']:.2f} min_z={st['min_z']:.3f} end_up={1 - 2 * (x * x + y * y):.2f} end_z={d.qpos[2]:.3f}")
