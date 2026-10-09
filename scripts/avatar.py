"""Embed the supplied avatar poses in the self-contained profile SVG."""
import base64
from pathlib import Path

from visuals import ASSETS, line, rect, text

FRAMES = ('neutral', 'blink', 'talk', 'blink-talk')
TIMES = (0, .20, .21, .34, .44, .45, .52, .54, .62, .73, .74, .88, .89, 1)
STATES = ('neutral', 'blink', 'neutral', 'talk', 'neutral', 'blink-talk',
          'talk', 'neutral', 'neutral', 'talk', 'neutral', 'blink',
          'neutral', 'neutral')


def scene(c):
    """The first pose is a complete static fallback; SMIL swaps expressions."""
    parts = [
        '<defs><clipPath id="avatar-clip"><rect x="49" y="144" width="389" height="367" rx="4"/></clipPath></defs>',
        rect(49, 144, 389, 367, c['panel'], c['line'], 4),
        f'<circle cx="244" cy="329" r="148" fill="none" stroke="{c["line"]}"/>',
        f'<circle cx="244" cy="329" r="111" fill="none" stroke="{c["line"]}" stroke-dasharray="3 8"/>',
        line(244, 150, 244, 500, c['line'], 'opacity=".45"'),
        line(55, 329, 432, 329, c['line'], 'opacity=".45"'),
        '<g clip-path="url(#avatar-clip)">',
    ]
    for frame in FRAMES:
        image = base64.b64encode((ASSETS / 'avatar' / f'{frame}.png').read_bytes()).decode('ascii')
        values = ';'.join('1' if state == frame else '0' for state in STATES)
        opacity = '1' if frame == 'neutral' else '0'
        parts.append(
            f'<image x="68" y="145" width="355" height="355" opacity="{opacity}" '
            f'href="data:image/png;base64,{image}">'
            f'<animate attributeName="opacity" dur="18s" values="{values}" '
            f'keyTimes="{";".join(map(str, TIMES))}" calcMode="discrete" repeatCount="indefinite"/>'
            '</image>'
        )
    parts += [
        '</g>',
        rect(53, 518, 135, 25, c['panel'], c['line'], 3),
        text(63, 535, 'X_X // AVATAR', c['accent'], 12, weight=700),
        text(432, 535, 'ONLINE', c['muted'], 12, 'end'),
    ]
    return parts
