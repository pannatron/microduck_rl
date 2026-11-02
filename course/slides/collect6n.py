"""Newton adventure runs → results6n.json (เฉพาะรันเต็ม 180 s)"""
import json, os, sys
SP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = sys.argv[1] if len(sys.argv) > 1 else f"{SP}/nadv"
RUNS = {"adv10": ["adv10", "race10"], "adv20": ["adv20"], "adv30": ["adv30"]}
out = {}
for lv, fs in RUNS.items():
    lanes = sum((json.load(open(f"{D}/{f}.json"))["lanes"] for f in fs), [])
    for pol in sorted({l["policy"] for l in lanes}):
        L = [l for l in lanes if l["policy"] == pol]; fin = sorted(l["finish"] for l in L if l["finish"])
        out[f"{pol}_{lv}"] = dict(n=len(L), finished=len(fin), times=fin, falls=sorted(l["falls"] for l in L), best_cp=max(l["cps"] for l in L),
                                  reached=[l["reached"] for l in L], end_x=[l["end_x"] for l in L])
w = json.load(open(f"{SP}/nadv/race10.json")); out["meta"] = dict(N=w["N"], wall_s=w["wall_s"], sim_s=w["sim_s"])
json.dump(out, open(f"{SP}/mgen/results6n.json", "w"), indent=1, ensure_ascii=False)
for k, v in out.items(): print(k, v)
