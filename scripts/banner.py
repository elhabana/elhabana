"""Generate the profile hero, the UN-CREDIBLES cover and the open-work slot."""
from visuals import THEMES, SANS, text, rect, line, svg, save

W = 1180


def _title_gradient(c):
    return (f'<linearGradient id="titleGrad" x1="0" y1="0" x2="0.6" y2="1">'
            f'<stop offset="0" stop-color="{c["title_from"]}"/>'
            f'<stop offset="1" stop-color="{c["title_to"]}"/>'
            f'</linearGradient>')


def hero(theme):
    """Quiet keynote-style header: one name, two lines, a lot of air."""
    c = THEMES[theme]
    body = [
        '<defs>' + _title_gradient(c)
        + f'<radialGradient id="glowGrad" cx="0.5" cy="0.5" r="0.5">'
          f'<stop offset="0" stop-color="{c["glow"]}" stop-opacity="{c["glow_op"]}"/>'
          f'<stop offset="0.6" stop-color="{c["glow2"]}" stop-opacity="{c["glow2_op"]}"/>'
          f'<stop offset="1" stop-color="{c["glow2"]}" stop-opacity="0"/>'
          f'</radialGradient></defs>',
        '<ellipse cx="590" cy="188" rx="540" ry="168" fill="url(#glowGrad)"/>',
        text(590, 64, '@elhabana', c['muted'], 15, 'middle', 500, 4),
        text(590, 198, 'Habana', 'url(#titleGrad)', 96, 'middle', 600, 1.5),
        line(497, 238, 683, 238, c['accent'], 'stroke-opacity=".45"'),
        text(590, 296, 'Unity Developer · Gameplay Programmer', c['text'], 27, 'middle', 500),
        text(590, 332, '3D Artist · Audiovisual Creator', c['muted'], 19, 'middle'),
        text(590, 378, 'gameplay systems · multiplayer · 3D · audiovisual', c['muted'], 13, 'middle', 400, 1.5),
    ]
    title = ('Habana — Unity developer and gameplay programmer; '
             '3D artist and audiovisual creator (@elhabana)')
    return svg(W, 400, theme, title, body, 18, SANS)


def _glyph(kind, cx, cy, color, opacity):
    stroke = (f'stroke="{color}" stroke-width="2.4" fill="none" '
              f'stroke-linejoin="round" opacity="{opacity}"')
    if kind == 'triangle':
        return f'<path d="M {cx - 11} {cy + 9} L {cx} {cy - 11} L {cx + 11} {cy + 9} Z" {stroke}/>'
    if kind == 'circle':
        return f'<circle cx="{cx}" cy="{cy}" r="10" {stroke}/>'
    if kind == 'diamond':
        return f'<path d="M {cx} {cy - 12} L {cx + 12} {cy} L {cx} {cy + 12} L {cx - 12} {cy} Z" {stroke}/>'
    return (f'<path d="M {cx - 10} {cy - 7} L {cx} {cy - 12} L {cx + 10} {cy - 7} '
            f'L {cx + 10} {cy + 7} L {cx} {cy + 12} L {cx - 10} {cy + 7} Z" {stroke}/>')


def project(theme):
    """UN-CREDIBLES cover: abstract player tokens, no in-game screenshot."""
    c = THEMES[theme]
    body = [
        '<defs>' + _title_gradient(c) + '</defs>',
        text(52, 52, 'FEATURED PROJECT', c['muted'], 13, weight=600, tracking=3),
        text(1128, 52, '@elhabana', c['muted'], 13, 'end', 400, 2),
        line(52, 72, 1128, 72, c['line']),
        text(52, 166, 'UN-CREDIBLES', 'url(#titleGrad)', 62, weight=700, tracking=1),
        text(54, 204, 'Multiplayer superhero party game for up to four players', c['muted'], 19),
        text(54, 240, 'Unity 6000.3 · C# · Netcode for GameObjects', c['accent'], 15, tracking=0.5),
        rect(54, 254, 152, 28, 'none', c['accent'], 14, 'stroke-opacity=".5"'),
        text(130, 273, 'IN DEVELOPMENT', c['accent'], 12, 'middle', 600, 2),
    ]
    for i, kind in enumerate(('triangle', 'circle', 'diamond', 'hexagon')):
        x = 852 + i * 68
        body.append(rect(x, 126, 58, 58, c['panel'], c['line'], 14))
        body.append(_glyph(kind, x + 29, 155, c['accent'], round(1 - i * 0.15, 2)))
    body.append(text(983, 220, '1 – 4 PLAYERS', c['muted'], 12, 'middle', 500, 2))
    title = ('UN-CREDIBLES — a multiplayer superhero party game for up to '
             'four players, in development.')
    return svg(W, 300, theme, title, body, 18, SANS)


def reserved(theme):
    """Placeholder for the next entries in Selected Work."""
    c = THEMES[theme]
    body = [
        text(52, 46, 'SELECTED WORK', c['muted'], 13, weight=600, tracking=3),
        rect(52, 62, 520, 66, 'none', c['line'], 12, 'stroke-dasharray="7 7"'),
        text(312, 101, '02 — reserved', c['muted'], 15, 'middle'),
        rect(608, 62, 520, 66, 'none', c['line'], 12, 'stroke-dasharray="7 7"'),
        text(868, 101, '03 — reserved', c['muted'], 15, 'middle'),
    ]
    return svg(W, 158, theme, 'Selected work: two slots reserved for upcoming projects.',
               body, 18, SANS)


if __name__ == '__main__':
    import motion
    for theme in THEMES:
        save(f'banner-{theme}.svg', hero(theme))
        save(f'uncredibles-{theme}.svg', project(theme))
        save(f'projects/reserved-{theme}.svg', reserved(theme))
        save(f'memes/dev-memes-{theme}.svg', motion.render(theme))
