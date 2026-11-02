"""สนามเตะบอล: scene_soccer.xml = scene_ball.xml + ประตู (เสาสองต้น) ที่ x=GX"""
import sys
GX = float(sys.argv[1]) if len(sys.argv) > 1 else 2.0
src = open("src/mjlab_microduck/robot/microduck/scene_ball.xml").read()
posts = "".join(f'<geom name="post{k}" type="cylinder" pos="{GX} {y} 0.1" size="0.015 0.1" rgba="1 1 1 1"/>\n' for k, y in enumerate([-0.25, 0.25]))
posts += f'<geom name="goalline" type="box" pos="{GX} 0 0.0005" size="0.01 0.25 0.0005" rgba="1 1 1 1" contype="0" conaffinity="0"/>\n'
out = src.replace("</worldbody>", posts + "</worldbody>", 1) if "</worldbody>" in src else src.replace("</mujoco>", f"<worldbody>{posts}</worldbody></mujoco>")
open("src/mjlab_microduck/robot/microduck/scene_soccer.xml", "w").write(out); print("ok")
