"""Shared space-black SVG primitives. Python standard library only."""
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
THEMES = {
    'dark': dict(bg='#090B0F', panel='#10141B', line='#2B333F', text='#E8EDF4', muted='#9BA8BA', accent='#A9C0DD'),
    'light': dict(bg='#F4F6F9', panel='#FFFFFF', line='#CFD6E0', text='#202A38', muted='#526277', accent='#42658D'),
}

def text(x, y, value, color, size=16, anchor='start', weight=400):
    return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}">{escape(str(value))}</text>'

def rect(x, y, w, h, fill, stroke='none', radius=8):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}"/>'

def line(x1, y1, x2, y2, color, extra=''):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" {extra}/>'

def svg(w, h, theme, title, body):
    c = THEMES[theme]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            'role="img" aria-labelledby="title" font-family="Consolas, Liberation Mono, monospace">'
            f'<title id="title">{escape(title)}</title>'
            + rect(.5, .5, w-1, h-1, c['bg'], c['line'], 14) + ''.join(body) + '</svg>\n')

def save(name, content):
    ASSETS.mkdir(exist_ok=True)
    (ASSETS / name).write_text(content, encoding='utf-8')
