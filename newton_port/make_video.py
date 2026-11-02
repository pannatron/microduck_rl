"""รวมโฟลเดอร์ภาพจาก newton_duck.py --video เป็น mp4 (H.264) — วางหลายโฟลเดอร์เคียงกันพร้อมป้ายได้
usage: make_video.py out.mp4 fps dirA[:label] [dirB[:label] ...]"""
import sys, glob, os, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg
out, fps, srcs = sys.argv[1], int(sys.argv[2]), [x.split(":", 1) + [""] for x in sys.argv[3:]]
lists = [sorted(glob.glob(d + "/f_*.png")) for d, *_ in srcs]
n = min(len(l) for l in lists)
font = ImageFont.truetype(os.path.join(os.path.dirname(__import__("matplotlib").__file__), "mpl-data/fonts/ttf/DejaVuSans-Bold.ttf"), 34)
tmp = tempfile.mkdtemp()
for k in range(n):
    ims = [Image.open(l[k]).convert("RGB") for l in lists]
    W, H = ims[0].size; S = Image.new("RGB", (W * len(ims) + 8 * (len(ims) - 1), H), (20, 20, 24))
    for i, im in enumerate(ims):
        S.paste(im, (i * (W + 8), 0)); lab = srcs[i][1]
        if lab:
            d = ImageDraw.Draw(S); x, y = i * (W + 8) + 24, 20
            bb = d.textbbox((x, y), lab, font=font); d.rectangle((bb[0] - 12, bb[1] - 8, bb[2] + 12, bb[3] + 8), fill=(14, 22, 33))
            d.text((x, y), lab, font=font, fill=(244, 243, 238))
    if S.width > 1920: S = S.resize((1920, int(S.height * 1920 / S.width) // 2 * 2))
    S.save(f"{tmp}/f_{k:04d}.png")
    if k == n // 2: S.save(out[:-4] + "_still.png")
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-framerate", str(fps), "-i", f"{tmp}/f_%04d.png",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "24", "-movflags", "+faststart", out], check=True)
print(out, n, "frames", os.path.getsize(out) // 1024, "KB")
