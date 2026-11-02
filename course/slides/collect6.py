"""collect adventure runs → results6.json"""
import json, os
SP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = {}
for pol in ["walk", "rough", "velstand", "climb"]:
    for lv in ["adv10", "adv20", "adv30"]:
        f = f"{SP}/adv/{pol}_{lv}.json"
        if not os.path.exists(f): continue
        r = json.load(open(f))
        out[f"{pol}_{lv}"] = dict(reached=r["reached"], cps=r["cps"], finish=r["finish"], falls=r["falls"], lava=r["lava"], cones=r["cone_hits"],
                                  end_x=r["trace"][-1][1], fall_x=[round(float(e[1].split("x=")[1].split(",")[0]), 2) for e in r["events"] if "x=" in e[1]])
json.dump(out, open(f"{SP}/mgen/results6.json", "w"), indent=1, ensure_ascii=False)
for k, v in out.items(): print(k, v["reached"], v["finish"], v["falls"], v["end_x"])
