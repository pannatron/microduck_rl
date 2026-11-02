#!/bin/bash
# baseline MuJoCo CPU (infer_policy) ทุก policy × คำสั่ง × BAM/no-BAM → native.txt
cd ~/repos/microduck_rl
one(){ pol=$1; vx=$2; mode=$3; extra=""; [ "$mode" = nobam ] && extra="--no-bam"
  log=$(mktemp); PYTHONUNBUFFERED=1 CUDA_VISIBLE_DEVICES= timeout 100 .venv/bin/python scripts/infer_policy.py --walking $pol --new-cmd-obs --lin-vel-x $vx $extra < /dev/null > $log 2>&1
  grep "vel 1s avg" $log | tail -10 | python3 -c "
import sys,re
L=[re.findall(r'fwd=([+-][\d.]+).*yaw=([+-][\d.]+)',l)[0] for l in sys.stdin]
print('$(basename $pol .onnx) $vx $mode %.3f %.3f'%(sum(float(x[0]) for x in L)/len(L), sum(float(x[1]) for x in L)/len(L)))"; rm -f $log; }
export -f one
for p in ${POLS:-exports/walk_2000.onnx exports/official/alpha_walking.onnx exports/official/velstand.onnx exports/rough_ft.onnx}; do for v in ${VXS:-0.2 0.25 0.3 0.4}; do for m in bam nobam; do echo "$p $v $m"; done; done; done | xargs -P 14 -n 3 bash -c 'one "$0" "$1" "$2"'
