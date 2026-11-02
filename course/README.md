# Microduck RL — 12-week workshop (course branch)

งานของหลักสูตรวางอยู่บน `microduck_rl` ของ Pollen (branch `develop`, commit `bae39f5`) — โค้ดของ Pollen ไม่ได้แก้ ยกเว้นบรรทัดเดียว:
`MICRODUCK_STAIR_MAX` ใน `src/mjlab_microduck/tasks/microduck_velocity_env_cfg.py` (ความสูงบันไดสูงสุดตอนเทรน Rough, ค่าเดิม 0.015)

อัปเดตจาก Pollen: `git fetch origin && git merge origin/develop`

## โฟลเดอร์

| ที่ | อะไร |
|---|---|
| `playground/` | รันบน MuJoCo CPU ผ่าน `scripts/infer_policy.py`: `sim_play.py` (director/`--live`), `ctl_*.py` (แอป), `make_course.py`, `make_soccer.py`, `make_adventure.py` + `ctl_adventure.py` (Duck Adventure), `sysid_testbench.py` |
| `newton_port/` | Newton 1.17 (รันจาก venv ของ `~/IsaacLab`): `newton_duck.py`, `newton_adventure.py`, `onnx2npz.py`, `ckpt2onnx.py`, `isaaclab_task/` (เทรนบน Newton ผ่าน Isaac Lab) |
| `course/slides/` | ตัวสร้างสไลด์ (`gen3.py` Module 3–6, `gen4.py` W7–8, `gen5.py` W9–12, `gen6.py` Duck Adventure) + ผลวัด `results*.json` |
| `src/.../scene_adv*.xml/.json` | ด่าน Duck Adventure H = 10/20/30 mm (สร้างใหม่ได้ด้วย `make_adventure.py`) |

## ไฟล์ที่ไม่อยู่ใน git

- `exports/*.onnx` และ `newton_port/*.npz` — policy ทางการโหลดจาก HF `pollen-robotics/microduck-policies` (ดู `exports/official/README.md`);
  ของเราสร้างใหม่จาก checkpoint ด้วย `scripts/export.py` หรือ `newton_port/ckpt2onnx.py` แล้ว `newton_port/onnx2npz.py`
- `newton_port/isaaclab_task/generated/` — USD ที่ Isaac Lab แปลงจาก MJCF ให้เองตอนรันครั้งแรก
- `logs/`, วิดีโอ, ภาพ — สำรองไว้นอก repo

## เด็ค (claude.ai, private)

Module 1–2 · Module 3–6 Sim Playground · Week 7–8 Roller · Week 9–12 Toward the Real Duck · Duck Adventure — ลิงก์อยู่ในเอกสารแผนหลักสูตร
