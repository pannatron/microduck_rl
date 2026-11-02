"""sim_play.py — รัน infer_policy.py แบบไม่มีจอ/คีย์บอร์ด แล้วให้ "ผู้กำกับ" (controller) สั่งแทน

usage: python playground/sim_play.py --ctl playground/ctl_xxx.py --secs 20 [--film out_prefix] -- <infer_policy args>
       python playground/sim_play.py --live --ctl ... -- <infer_policy args>   # เปิดหน้าต่าง viewer จริง + คีย์บอร์ดจากเทอร์มินัล (controller ทำงานคู่กัน)

controller file ต้องมี  control(t, pol, m, d) -> list[str]  (คืนปุ่มที่จะ "กด" ใน step นี้ เช่น ["k"])
และจะเปลี่ยนคำสั่ง pol.vel_cmd / pol.set_vel_cmd(...) ตรง ๆ ก็ได้
"""
import sys, os, time, runpy, argparse, importlib.util, json
import numpy as np, mujoco, mujoco.viewer

ap = argparse.ArgumentParser()
ap.add_argument("--ctl", default=None); ap.add_argument("--secs", type=float, default=10)
ap.add_argument("--film", default=None); ap.add_argument("--every", type=int, default=25)
ap.add_argument("--cam", default="follow")  # follow | follow:dist,az,el | x,y,z,dist,az,el
ap.add_argument("--size", type=int, default=640)
ap.add_argument("--live", action="store_true")
i = sys.argv.index("--"); a = ap.parse_args(sys.argv[1:i]); infer_args = sys.argv[i+1:]

ctl = None
if a.ctl:
    spec = importlib.util.spec_from_file_location("ctl", a.ctl); ctl = importlib.util.module_from_spec(spec); spec.loader.exec_module(ctl)

S = {"m": None, "d": None, "pol": None, "frames": [], "log": [], "viewer": None}
if ctl is not None: ctl.S = S
if not a.live:
    _real_time = time.time
    time.time = lambda: (S["d"].time if S["d"] is not None else 0.0) + 1000.0   # นาฬิกา = เวลาในซิม
    time.sleep = lambda s: None

class FakeViewer:
    def __init__(self, m, d, **kw):
        S["m"], S["d"] = m, d; self.m, self.d = m, d; self.n = 0; self.user_scn = mujoco.MjvScene(m, 50)
        if a.film:
            m.vis.global_.offwidth = max(m.vis.global_.offwidth, a.size); m.vis.global_.offheight = max(m.vis.global_.offheight, a.size)
            self.r = mujoco.Renderer(m, a.size, a.size)
    def __enter__(self): return self
    def __exit__(self, *x): pass
    def is_running(self): return self.d.time < a.secs
    def sync(self):
        self.n += 1; d = self.d
        S["log"].append([d.time, *d.qpos[:7]])
        if a.film and self.n % a.every == 0:
            cam = mujoco.MjvCamera()
            if a.cam.startswith("follow"):            # follow หรือ follow:dist,az,el
                dist, az, el = map(float, a.cam.split(":")[1].split(",")) if ":" in a.cam else (0.7, 120, -15)
                cam.lookat[:] = [d.qpos[0], d.qpos[1], d.qpos[2] - 0.02]; cam.distance = dist; cam.azimuth = az; cam.elevation = el
            else:
                x, y, z, dist, az, el = map(float, a.cam.split(",")); cam.lookat[:] = [x, y, z]; cam.distance = dist; cam.azimuth = az; cam.elevation = el
            self.r.update_scene(d, cam); S["frames"].append(self.r.render().copy())
_real_launch = mujoco.viewer.launch_passive
def _live_launch(m, d, **kw):
    S["m"], S["d"] = m, d; S["viewer"] = _real_launch(m, d, **kw); return S["viewer"]
mujoco.viewer.launch_passive = _live_launch if a.live else (lambda m, d, **kw: FakeViewer(m, d, **kw))

class Director:                      # แทน TerminalInput: "กดปุ่ม" ตาม controller
    enabled = True
    def __enter__(self): return self
    def __exit__(self, *x): pass
    def get_keys(self):
        if ctl is None or S["pol"] is None: return []
        return list(ctl.control(S["d"].time, S["pol"], S["m"], S["d"]) or [])

class LiveDirector:                  # --live: ปุ่มจริงจากเทอร์มินัล + ให้ controller (กติกาเกม) ทำงานทุก step
    def __init__(self, ti): self.ti = ti; self.enabled = getattr(ti, "enabled", True)
    def __enter__(self): self.ti.__enter__(); self.enabled = getattr(self.ti, "enabled", True); return self
    def __exit__(self, *x): return self.ti.__exit__(*x)
    def get_keys(self):
        keys = list(self.ti.get_keys() or [])
        if ctl is not None and S["pol"] is not None and S["d"] is not None: keys += list(ctl.control(S["d"].time, S["pol"], S["m"], S["d"]) or [])
        return keys

os.chdir(os.path.expanduser("~/repos/microduck_rl"))
src = open("scripts/infer_policy.py").read().replace("with TerminalInput() as term", "with LiveDirector(TerminalInput()) as term" if a.live else "with Director() as term")
ns = {"__name__": "infer_policy", "__file__": "scripts/infer_policy.py", "Director": Director, "LiveDirector": LiveDirector}
exec(compile(src, "scripts/infer_policy.py", "exec"), ns)
_init = ns["PolicyInference"].__init__
def _wrap(self, *x, **k):
    _init(self, *x, **k); S["pol"] = self
ns["PolicyInference"].__init__ = _wrap
if ctl is not None and hasattr(ctl, "setup"): ns["_ctl_setup"] = ctl.setup
sys.argv = ["infer_policy.py"] + infer_args
try: ns["main"]()
except SystemExit: pass
if ctl is not None and hasattr(ctl, "report"): ctl.report(S["m"], S["d"])
if a.film:
    from PIL import Image
    os.makedirs(os.path.dirname(a.film) or ".", exist_ok=True)
    for k, f in enumerate(S["frames"]): Image.fromarray(f).save(f"{a.film}_{k:03d}.png")
    np.save(a.film + "_log.npy", np.array(S["log"]))
    print("frames", len(S["frames"]))
