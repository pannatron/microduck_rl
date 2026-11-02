"""Microduck deck 2 — Module 3–5 Sim Playground. Usage: gen3.py <deck_root> [ids...]"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from lib import H, M, SEC, head, code, task, result, think, table, slide, divider, answer

NAVY = "background:#0E1621;color:#F4F3EE;font-family:'IBM Plex Sans Thai', Arial, sans-serif"
G = '<span style="color:#7AC943">$</span>'
C = lambda t: f'<span style="color:#7A8492">{t}</span>'
K = lambda t: f'<span style="color:#FFB86B">{t}</span>'
SP = "&#160;" * 4
B = lambda i: f"/_blob/{i}"

slides, order = {}, []


def put(sid, html, notes=None):
    if notes:
        html = html.rstrip()
        html = html[: -len("</section>")] + f"<aside>{notes}</aside></section>\n"
    slides[sid] = html
    order.append(sid)


def p(t, size=33, color="#1B2430", extra=""):
    return f'<p style="font-size:{size}px;color:{color};line-height:1.45{extra}">{t}</p>'


def card(title, body, bg="#FBFAF6", border="1px solid #DDDBD2", tcolor="#0E1621"):
    return (f'<div style="flex:1;background:{bg};border:{border};border-radius:24px;padding:40px 44px;display:flex;flex-direction:column;gap:22px">'
            f'<h3 style="{H};font-size:44px;font-weight:600;color:{tcolor};line-height:1.15">{title}</h3>{body}</div>')


def big(v, label, color="#1F4D06"):
    return f'<div><p style="{H};font-size:68px;font-weight:600;color:{color};line-height:1">{v}</p>{p(label, 26)}</div>'


def bigrow(*items):
    return f'<div style="display:flex;flex-direction:row;gap:44px">{"".join(items)}</div>'


def section(sid, eyebrow, title, sub, img, alt):
    return (f'<section id="{sid}" data-transition="fade" style="{NAVY};padding:128px;display:flex;flex-direction:row;gap:64px;align-items:center">'
            f'<div style="flex:1;display:flex;flex-direction:column;gap:28px">'
            f'<p style="font-size:24px;letter-spacing:3px;text-transform:uppercase;color:#7AC943;font-weight:600">{eyebrow}</p>'
            f'<h1 style="{H};font-size:110px;font-weight:600;line-height:1.05;color:#F4F3EE">{title}</h1>'
            f'<p style="font-size:36px;color:#B8C4D0;line-height:1.4">{sub}</p></div>'
            f'<img src="{img}" alt="{alt}" style="width:620px;height:760px;object-fit:cover;border-radius:24px"></section>\n')


def strip(src, alt, h=300):
    return f'<img src="{src}" alt="{alt}" style="width:1696px;height:{h}px;object-fit:cover;border-radius:20px">'

