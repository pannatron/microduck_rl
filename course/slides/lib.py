"""Helpers to write exercise slides in the deck design system."""
H = "font-family:'Prompt', Arial, sans-serif"
M = "font-family:'JetBrains Mono', monospace"
SEC = "background:#F4F3EE;color:#1B2430;font-family:'IBM Plex Sans Thai', Arial, sans-serif"


def head(eyebrow, title, num=None):
    n = f'<p style="{H};font-size:150px;font-weight:600;color:#DDDBD2;line-height:1">{num}</p>' if num else ""
    return (f'<div style="display:flex;flex-direction:row;justify-content:space-between;align-items:end">'
            f'<div style="display:flex;flex-direction:column;gap:16px">'
            f'<p style="font-size:28px;letter-spacing:4px;text-transform:uppercase;color:#B85C00;font-weight:600">{eyebrow}</p>'
            f'<h2 style="{H};font-size:76px;font-weight:600;line-height:1.1;color:#0E1621">{title}</h2></div>{n}</div>')


def code(html, size=28):
    return (f'<div style="background:#0E1621;border-radius:24px;padding:32px 40px">'
            f'<p style="{M};font-size:{size}px;color:#E6EDF3;line-height:1.55">{html}</p></div>')


def task(items):
    li = "".join(f'<p style="font-size:30px;color:#1B2430;line-height:1.4"><span style="color:#B85C00;font-weight:600">{i+1}.</span> {t}</p>' for i, t in enumerate(items))
    return (f'<div style="flex:1;background:#FBFAF6;border:1px solid #DDDBD2;border-radius:24px;padding:36px 40px;display:flex;flex-direction:column;gap:18px">'
            f'<p style="font-size:24px;letter-spacing:3px;text-transform:uppercase;color:#4A5563;font-weight:600">โจทย์</p>{li}</div>')


def result(inner, label="ผลบนเครื่องทดสอบ · RTX 3060 Laptop 6 GB"):
    return (f'<div style="flex:1;background:#E6F2DA;border-radius:24px;padding:36px 40px;display:flex;flex-direction:column;gap:18px">'
            f'<p style="font-size:24px;letter-spacing:3px;text-transform:uppercase;color:#1F4D06;font-weight:600">{label}</p>{inner}</div>')


def think(text):
    return (f'<div style="background:#FBEBDD;border-left:8px solid #B85C00;border-radius:16px;padding:24px 36px">'
            f'<p style="font-size:30px;color:#1B2430"><b style="color:#B85C00">คิดต่อ:</b> {text}</p></div>')


def table(rows, head_row, size=28, hi=None):
    th = "".join(f'<th style="color:#F4F3EE">{h}</th>' for h in head_row)
    body = ""
    for i, r in enumerate(rows):
        bg = ' style="background:#FFFFFF"' if hi == i else ""
        body += f"<tr{bg}>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>"
    return f'<table style="font-size:{size}px;color:#1B2430"><tr style="background:#1F4D06">{th}</tr>{body}</table>'


def slide(sid, *parts, row=None, at=2, pad="100px 112px 90px"):
    """parts go top-to-bottom; `row` (blocks side by side, stretched to fill) is inserted after `at` parts."""
    mid = ""
    if row:
        cells = "".join(b if b.startswith("<div") else f'<div style="flex:1;display:flex;flex-direction:column">{b}</div>' for b in row)
        mid = f'<div style="flex:1;display:flex;flex-direction:row;gap:32px">{cells}</div>'
    top, bottom = "".join(parts[:at]), parts[at:]
    return (f'<section id="{sid}" data-transition="fade" style="{SEC};padding:{pad};display:flex;flex-direction:column;gap:32px">'
            f'{top}{mid}{"".join(bottom)}</section>\n')


def divider(sid, eyebrow, title, sub):
    return (f'<section id="{sid}" data-transition="fade" style="background:#B85C00;color:#FFF7EE;font-family:\'IBM Plex Sans Thai\', Arial, sans-serif;padding:120px 112px 110px;display:flex;flex-direction:column;justify-content:space-between">'
            f'<p style="font-size:30px;letter-spacing:4px;text-transform:uppercase;color:#FFE2C4;font-weight:600">{eyebrow}</p>'
            f'<div style="display:flex;flex-direction:column;gap:28px"><h1 style="{H};font-size:150px;font-weight:600;line-height:1;color:#FFF7EE">{title}</h1>'
            f'<p style="font-size:44px;color:#FFE2C4;line-height:1.4">{sub}</p></div></section>\n')


def answer(sid, ex, title, items, side=None, summary=None, side_w=760):
    """Answer-key slide: numbered answers (matching the exercise's โจทย์), optional side block, summary bar."""
    rows = "".join(
        f'<div style="display:flex;flex-direction:row;gap:20px;align-items:start;border-bottom:1px solid #CFE3BC;padding:0px 0px 16px 0px">'
        f'<p style="{H};font-size:34px;font-weight:600;color:#3D7A12;width:40px;line-height:1.25">{i+1}</p>'
        f'<p style="flex:1;font-size:28px;color:#1B2430;line-height:1.45">{t}</p></div>' for i, t in enumerate(items))
    left = f'<div style="flex:1;display:flex;flex-direction:column;gap:16px;justify-content:center">{rows}</div>'
    right = f'<div style="width:{side_w}px;display:flex;flex-direction:column;gap:20px;justify-content:center">{side}</div>' if side else ""
    summ = (f'<div style="background:#1F4D06;border-radius:16px;padding:24px 36px"><p style="font-size:30px;color:#F4F3EE">'
            f'<b style="color:#B8E68F">สรุป:</b> {summary}</p></div>') if summary else ""
    return (f'<section id="{sid}" data-transition="fade" style="background:#EEF6E6;color:#1B2430;font-family:\'IBM Plex Sans Thai\', Arial, sans-serif;padding:96px 112px 90px;display:flex;flex-direction:column;gap:30px">'
            f'<div style="display:flex;flex-direction:column;gap:14px">'
            f'<p style="font-size:28px;letter-spacing:4px;text-transform:uppercase;color:#3D7A12;font-weight:600">เฉลย · Exercise {ex}</p>'
            f'<h2 style="{H};font-size:68px;font-weight:600;line-height:1.1;color:#0E1621">{title}</h2></div>'
            f'<div style="flex:1;display:flex;flex-direction:row;gap:48px">{left}{right}</div>{summ}</section>\n')
