"""Static project cards for the README, in the header's terminal style. Each card is linked in the README."""
from visuals import THEMES, text, rect, line, svg

W, H = 580, 210
# (file slug, title, tags, description lines)
CARDS = (
    ('roller-hunter', 'ROLLER HUNTER', 'SHOOTER · ROGUELIKE · UNITY',
     ('Third-person skating and combat,', 'with hordes and roguelike progression.')),
    ('fps-online', 'FPS ONLINE', 'MULTIPLAYER · FPS · UNITY',
     ('Online combat prototype with synced', 'players and hitscan shooting.')),
)

def card(theme, slug, title, tags, lines):
    c = THEMES[theme]
    b = [rect(14, 14, W-28, H-28, c['panel'], c['line'], 10)]
    b += [f'<circle cx="{36+i*18}" cy="36" r="4" fill="{c["muted"]}" opacity="{.4+i*.25}"/>' for i in range(3)]
    b += [text(W-34, 41, f'~/projects/{slug}', c['muted'], 13, 'end'), line(14, 56, W-14, 56, c['line'])]
    b += [text(34, 92, title, c['text'], 24, weight=700), text(34, 116, tags, c['accent'], 12, weight=700)]
    b += [text(34, 146+i*22, value, c['muted'], 15) for i, value in enumerate(lines)]
    # The whole image is the link, so the footer only says where it goes.
    b += [text(W-34, 186, '> view on The Rookies', c['accent'], 13, 'end', 700)]
    return svg(W, H, theme, f'{title}: {" ".join(lines)} View on The Rookies.', b)

def render_all():
    """{file name: svg} for every card and theme."""
    return {f'card-{slug}-{theme}.svg': card(theme, slug, title, tags, lines)
            for slug, title, tags, lines in CARDS for theme in THEMES}
