"""Shared SVG primitives and the space-black palette. Python standard library only."""
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "Consolas, 'Liberation Mono', Menlo, monospace"

THEMES = {
    'dark': dict(
        bg='#090B0F', panel='#10141B', line='#242C37',
        text='#E8EDF4', muted='#93A0B2', accent='#A9C0DD',
        title_from='#FFFFFF', title_to='#9EB4D2',
        glow='#7C8FBF', glow2='#8E7FC0', glow_op='0.16', glow2_op='0.06',
    ),
    'light': dict(
        bg='#F4F6F9', panel='#FFFFFF', line='#D3DAE3',
        text='#1F2937', muted='#5A6B80', accent='#42658D',
        title_from='#1F2937', title_to='#42658D',
        glow='#8FA6CC', glow2='#9C8FC0', glow_op='0.12', glow2_op='0.05',
    ),
}


def text(x, y, value, color, size=16, anchor='start', weight=400, tracking=None,
         opacity=None, extra=''):
    attrs = (f'x="{x}" y="{y}" fill="{color}" font-size="{size}" '
             f'text-anchor="{anchor}" font-weight="{weight}"')
    if tracking is not None:
        attrs += f' letter-spacing="{tracking}"'
    if opacity is not None:
        attrs += f' opacity="{opacity}"'
    if extra:
        attrs += ' ' + extra
    return f'<text {attrs}>{escape(str(value))}</text>'


def rect(x, y, w, h, fill, stroke='none', radius=8, extra=''):
    body = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" '
            f'fill="{fill}" stroke="{stroke}"')
    if extra:
        body += ' ' + extra
    return body + '/>'


def line(x1, y1, x2, y2, color, extra=''):
    body = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}"'
    if extra:
        body += ' ' + extra
    return body + '/>'


def svg(w, h, theme, title, body, radius=14, font=SANS):
    c = THEMES[theme]
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-labelledby="title" font-family="{font}">'
        f'<title id="title">{escape(title)}</title>'
        + rect(.5, .5, w - 1, h - 1, c['bg'], c['line'], radius)
        + ''.join(body)
        + '</svg>\n'
    )


def save(name, content):
    path = ASSETS / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')
