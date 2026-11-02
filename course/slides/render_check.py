import json,re,sys,os,subprocess,glob
S=os.path.expanduser('~/slide_render')
m=json.load(open(f"{S}/blobmap.json"))
deck=sys.argv[1]; ids=sys.argv[2:]
d=json.load(open(f"{S}/{deck}/project/deck.json"))
order=ids or d["order"]
out=f"{S}/render/{deck}"; os.makedirs(out,exist_ok=True)
head='<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Prompt:wght@400;500;600;700&family=IBM+Plex+Sans+Thai:wght@400;500;600&family=JetBrains+Mono:wght@400;600&display=swap"><style>html,body{margin:0;width:1920px;height:1080px;overflow:hidden}section{position:relative;width:1920px;height:1080px;box-sizing:border-box;overflow:hidden}*{margin:0;box-sizing:border-box}aside{display:none}x-shape{display:block;clip-path:polygon(0 30%,60% 30%,60% 0,100% 50%,60% 100%,60% 70%,0 70%)}ul{padding-left:1.2em}td,th{padding:.35em .6em;border-bottom:1px solid #ccc;text-align:left}table{border-collapse:collapse}</style></head><body>'
for i,sid in enumerate(order):
    h=open(f"{S}/{deck}/project/slides/{sid}.html").read()
    h=re.sub(r'/_blob/([0-9a-f]{32})',lambda x:"file://"+S+"/"+m.get(x.group(1),"missing"),h)
    p=f"{out}/{i+1:02d}_{sid}.html"; open(p,"w").write(head+h+"</body></html>")
    subprocess.run(["firefox","--headless","--no-remote","--profile",S+"/ffprof","--window-size=1920,1080","--screenshot",p[:-5]+".png","file://"+p],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=60)
print("ok",len(order))
