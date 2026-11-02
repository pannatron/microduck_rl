"""แปลง checkpoint rsl_rl (จาก Isaac Lab/Newton) → ONNX แบบเดียวกับที่ microduck_rl export (normalizer ฝังในโมเดล)
และ npz สำหรับ newton_duck.py — รันด้วย venv ของ microduck_rl:
  .venv/bin/python newton_port/ckpt2onnx.py <model_XXXX.pt> exports/<name>.onnx
"""
import os, subprocess, sys
import numpy as np, torch

ckpt, out = sys.argv[1], sys.argv[2]
sd = torch.load(ckpt, map_location="cpu", weights_only=False)["actor_state_dict"]
EPS = 1e-2   # rsl_rl EmpiricalNormalization: (x - mean) / (std + eps)


class Actor(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.register_buffer("mean", sd["obs_normalizer._mean"])
        self.register_buffer("den", sd["obs_normalizer._std"] + EPS)
        self.mlp = torch.nn.Sequential(torch.nn.Linear(61, 512), torch.nn.ELU(), torch.nn.Linear(512, 256), torch.nn.ELU(),
                                       torch.nn.Linear(256, 128), torch.nn.ELU(), torch.nn.Linear(128, 14))
        self.mlp.load_state_dict({k[4:]: v for k, v in sd.items() if k.startswith("mlp.")})

    def forward(self, obs):
        return self.mlp((obs - self.mean) / self.den)


a = Actor().eval()
torch.onnx.export(a, torch.zeros(1, 61), out, input_names=["obs"], output_names=["actions"], opset_version=17, dynamo=False)
print("wrote", out)
# npz ให้ newton_duck.py ใช้ (default pose / IMU เหมือนไฟล์อื่น)
npz = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.basename(out)[:-5] + ".npz")
subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "onnx2npz.py"), out, npz], check=True)
