"""An 8-bit Space Invaders round, simulated in Python and baked into SMIL.

The player shoots a few invaders, gets hit, GAME OVER flashes and the screen
switches off like an old CRT. Then the boot sequence takes over.
"""
import random
from html import escape

DIE = 4.9        # seconds: the last bomb hits the player
SWITCH_OFF = 5.5 # the CRT starts collapsing
INTRO = 6.0      # the screen is dark and the boot sequence begins
SHAPE = 'M14 65 H1166 V586 Q1166 596 1156 596 H24 Q14 596 14 586 Z'
PX = 3           # one sprite pixel in banner units
DT = .05         # simulation step

SPRITES = {
    'squid': (('...##...', '..####..', '.######.', '##.##.##', '########', '..#..#..', '.#.##.#.', '#.#..#.#'),
              ('...##...', '..####..', '.######.', '##.##.##', '########', '.#.##.#.', '#......#', '.#....#.')),
    'crab': (('..#.....#..', '...#...#...', '..#######..', '.##.###.##.', '###########', '#.#######.#', '#.#.....#.#', '...##.##...'),
             ('..#.....#..', '#..#...#..#', '#.#######.#', '###.###.###', '###########', '.#########.', '..#.....#..', '.#.......#.')),
    'octopus': (('....####....', '.##########.', '############', '###..##..###', '############', '...##..##...', '..##.##.##..', '##........##'),
                ('....####....', '.##########.', '############', '###..##..###', '############', '..###..###..', '.##..##..##.', '..##....##..')),
}
PLAYER = ('......#......', '.....###.....', '.....###.....', '.###########.', '#############', '#############', '#############', '#############')
BOOM = ('....#...#....', '..#..#.#..#..', '...#.....#...', '##.........##', '...#.....#...', '..#..#.#..#..', '....#...#....')
WRECK = (('....#........', '..........#..', '....#.##.....', '..#.#####.#..', '.###########.', '#############'),
         ('#.....#....#.', '...#.........', '..#..##.#...#', '#..#####..#..', '.##########..', '###.#####.###'))
UFO = ('.....######.....', '...##########...', '..############..', '.##.##.##.##.##.', '################', '..###..##..###..', '...#........#...')

ROWS = ('squid', 'crab', 'crab', 'octopus', 'octopus')
COLS = 11
CELL_W, CELL_H = 48, 34
START_X, START_Y = 470, 140
STEP_X, STEP_Y = 16, 18
LEFT, RIGHT = 60, 1120
SHIP_Y = 540
GROUND = 576


def path(bitmap):
    """Pixel art as one compact path in sprite-pixel units."""
    d = ''
    for y, row in enumerate(bitmap):
        x = 0
        while x < len(row):
            if row[x] == '#':
                run = len(row[x:]) - len(row[x:].lstrip('#'))
                d += f'M{x} {y}h{run}v1h-{run}z'
                x += run
            else:
                x += 1
    return d

def width(bitmap):
    return len(bitmap[0]) * PX

def formation():
    """Discrete formation offsets: [(time, dx, dy)] until the player dies."""
    t, dx, dy, direction, interval, out = 0, 0, 0, 1, .3, [(0, 0, 0)]
    while t + interval < DIE:
        t = round(t + interval, 2)
        nxt = dx + STEP_X * direction
        if START_X + nxt < LEFT or START_X + nxt + COLS * CELL_W > RIGHT:
            dy, direction, interval = dy + STEP_Y, -direction, max(.18, interval - .04)
        else:
            dx = nxt
        out.append((t, dx, dy))
    return out

def offset(steps, t):
    for when, dx, dy in reversed(steps):
        if when <= t:
            return dx, dy
    return 0, 0

def invader_box(row, col, dx, dy):
    w = width(SPRITES[ROWS[row]][0])
    x = START_X + dx + col * CELL_W + (CELL_W - w) / 2
    y = START_Y + dy + row * CELL_H
    return x, y, w, 8 * PX

def simulate():
    """Play the round. Returns player track, shots, kills and bombs."""
    rnd, steps = random.Random(42), formation()
    alive = {(r, c) for r in range(len(ROWS)) for c in range(COLS)}
    px, target, shot = 590., None, None
    track, shots, kills, bombs = [], [], [], []
    t, score = 0., 0
    while t < DIE:
        dx, dy = offset(steps, t)
        if t < DIE - .55:                               # the player stops just before the fatal bomb
            if target is None or target not in alive:
                columns = sorted({c for _, c in alive})
                col = rnd.choice(columns)
                target = max((r, c) for r, c in alive if c == col)
            x, _, w, _ = invader_box(*target, dx, dy)
            goal = x + w / 2 - width(PLAYER) / 2
            px += max(-18, min(18, goal - px))          # 360 px/s
            if shot is None and abs(goal - px) < 4:
                shot = [round(t, 2), px + width(PLAYER) / 2, SHIP_Y - 6]
        track.append((round(t, 2), round(px, 1)))
        if shot:
            shot[2] -= 45                                # 900 px/s
            # check the whole stretch travelled this step, or the shot could skip an invader
            boxes = {rc: invader_box(*rc, dx, dy) for rc in alive}
            hits = [rc for rc, (x, y, w, h) in boxes.items()
                    if x <= shot[1] <= x + w and y <= shot[2] + 45 and shot[2] <= y + h]
            hit = max(hits) if hits else None
            if hit:
                shot[2] = boxes[hit][1] + boxes[hit][3]
            if hit or shot[2] < 110:
                end = round(t + DT, 2)
                shots.append((shot[0], end, shot[1], SHIP_Y - 6, shot[2]))
                if hit:
                    alive.discard(hit)
                    score += (30, 20, 20, 10, 10)[hit[0]]
                    kills.append((end, hit, score))
                shot = None
        t = round(t + DT, 2)
    # a couple of harmless bombs, then the one that lands on the player
    for when in (1.1, 2.2, 3.3):
        dx, dy = offset(steps, when)
        far = [(r, c) for r, c in alive if abs(invader_box(r, c, dx, dy)[0] - dict(track)[round(when, 2)]) > 90]
        if not far:
            continue
        x, y, w, h = invader_box(*max(far, key=lambda rc: (rc[0], rnd.random())), dx, dy)
        bombs.append((when, x + w / 2, y + h, GROUND - 6))
    ship_x = track[-1][1] + width(PLAYER) / 2
    fall = (SHIP_Y + 4 - (START_Y + offset(steps, DIE)[1] + len(ROWS) * CELL_H)) / 400
    bombs.append((round(DIE - fall, 2), ship_x, SHIP_Y + 4 - fall * 400, SHIP_Y + 4))
    return steps, track, shots, kills, bombs

def window(begin, end):
    return f'<set attributeName="opacity" to="1" begin="{begin}s" end="{end}s"/>'

def hud(x, y, value, c, anchor='start', size=18):
    return (f'<text x="{x}" y="{y}" fill="{c}" font-size="{size}" text-anchor="{anchor}" '
            f'font-weight="700" letter-spacing="2">{escape(value)}</text>')

def invaders(c):
    """The overlay is hidden by default, so static renderers show the banner."""
    steps, track, shots, kills, bombs = simulate()
    ink, frac = c['accent'], lambda t: f'{t / INTRO:.4f}'
    defs = ['<defs>']
    for name, (a, b) in SPRITES.items():
        defs.append(f'<g id="inv-{name}">'
                    f'<path d="{path(a)}"><animate attributeName="opacity" values="1;0" dur=".6s" calcMode="discrete" repeatCount="indefinite"/></path>'
                    f'<path d="{path(b)}" opacity="0"><animate attributeName="opacity" values="0;1" dur=".6s" calcMode="discrete" repeatCount="indefinite"/></path></g>')
    defs += [f'<path id="inv-boom" d="{path(BOOM)}"/>', '</defs>']

    p = ['<g id="invaders" opacity="0">',
         f'<animate attributeName="opacity" values="1;1;0" keyTimes="0;.999;1" dur="{INTRO}s" fill="freeze"/>',
         # old TV switching off: squash to a line, then to a dot
         '<g transform="translate(590 330)"><g>',
         f'<animateTransform attributeName="transform" type="scale" values="1 1;1 1;1 .006;.003 .006" '
         f'keyTimes="0;{frac(SWITCH_OFF)};{frac(SWITCH_OFF + .25)};1" dur="{INTRO}s" fill="freeze"/>',
         '<g transform="translate(-590 -330)">',
         f'<path d="{SHAPE}" fill="{c["panel"]}"/>', *defs, f'<g fill="{ink}">']

    # HUD
    p += [hud(60, 100, 'SCORE<1>', c['muted'], size=14), hud(590, 100, 'HI-SCORE', c['muted'], 'middle', 14),
          hud(1120, 100, 'CREDIT 00', c['muted'], 'end', 14), hud(590, 124, '1980', c['text'], 'middle')]
    marks = [(0, 0)] + [(t, s) for t, _, s in kills] + [(INTRO, None)]
    for (begin, value), (end, _) in zip(marks, marks[1:]):
        p.append(f'<g opacity="0">{hud(60, 124, f"{value:04d}", c["text"])}{window(begin, end)}</g>')
    p.append(f'<rect x="40" y="{GROUND}" width="1100" height="2" fill="{ink}" opacity=".7"/>')
    p.append(f'<g transform="translate(60 584) scale(2)"><path d="{path(PLAYER)}"/></g>')
    p.append(f'<text x="100" y="594" fill="{c["muted"]}" font-size="14" font-weight="700">1</text>')

    # UFO crossing the top
    p.append(f'<g transform="translate(1180 132)"><animateTransform attributeName="transform" type="translate" '
             f'values="1180 132;1180 132;-60 132" keyTimes="0;.12;1" dur="{DIE + .4:.1f}s" fill="freeze"/>'
             f'<g transform="scale(2.5)"><path d="{path(UFO)}" fill="{c["text"]}"/></g></g>')

    # the formation: discrete steps, killed invaders vanish into an explosion
    keys = ';'.join(frac(t) for t, _, _ in steps) + ';1'
    vals = ';'.join(f'{dx} {dy}' for _, dx, dy in steps) + f';{steps[-1][1]} {steps[-1][2]}'
    p.append(f'<g><animateTransform attributeName="transform" type="translate" values="{vals}" '
             f'keyTimes="{keys}" dur="{INTRO}s" calcMode="discrete" fill="freeze"/>')
    killed = {hit: t for t, hit, _ in kills}
    for r, name in enumerate(ROWS):
        for col in range(COLS):
            x, y, _, _ = invader_box(r, col, 0, 0)
            gone = ''
            if (r, col) in killed:
                gone = f'<set attributeName="opacity" to="0" begin="{killed[(r, col)]}s" fill="freeze"/>'
            p.append(f'<use href="#inv-{name}" transform="translate({x:g} {y:g}) scale({PX})">{gone}</use>')
    for t, (r, col), _ in kills:
        x, y, _, _ = invader_box(r, col, 0, 0)
        p.append(f'<g opacity="0" transform="translate({x - 4:g} {y + 2:g}) scale({PX})"><use href="#inv-boom"/>{window(t, round(t + .25, 2))}</g>')
    p.append('</g>')

    # shots and bombs
    for begin, end, x, y0, y1 in shots:
        p.append(f'<rect x="{x - 1.5:.1f}" y="{y0}" width="3" height="14" opacity="0">{window(begin, end)}'
                 f'<animate attributeName="y" from="{y0}" to="{y1:.0f}" begin="{begin}s" dur="{end - begin:.2f}s" fill="freeze"/></rect>')
    for begin, x, y0, y1 in bombs:
        dur = round((y1 - y0) / 400, 2)
        p.append(f'<path d="M0 0h3v4h-3zM3 4h3v4h-3zM0 8h3v4h-3z" opacity="0" transform="translate({x - 3:.1f} 0)">'
                 f'{window(begin, round(begin + dur, 2))}<animateTransform attributeName="transform" type="translate" '
                 f'from="{x - 3:.1f} {y0:.0f}" to="{x - 3:.1f} {y1:.0f}" begin="{begin}s" dur="{dur}s" fill="freeze"/></path>')

    # the player: moves, gets hit, wreck flickers
    keys = ';'.join(frac(t) for t, _ in track) + ';1'
    vals = ';'.join(f'{x} {SHIP_Y}' for _, x in track) + f';{track[-1][1]} {SHIP_Y}'
    p.append(f'<g><animateTransform attributeName="transform" type="translate" values="{vals}" keyTimes="{keys}" '
             f'dur="{INTRO}s" fill="freeze"/>'
             f'<g transform="scale({PX})"><path d="{path(PLAYER)}"><set attributeName="opacity" to="0" begin="{DIE}s" fill="freeze"/></path>'
             f'<path d="{path(WRECK[0])}" transform="translate(0 2)" opacity="0">{window(DIE, round(DIE + .6, 2))}'
             '<animate attributeName="opacity" values="1;0" dur=".2s" calcMode="discrete" repeatCount="indefinite"/></path>'
             f'<path d="{path(WRECK[1])}" transform="translate(0 2)" opacity="0">{window(round(DIE + .1, 2), round(DIE + .6, 2))}'
             '<animate attributeName="opacity" values="0;1" dur=".2s" calcMode="discrete" repeatCount="indefinite"/></path></g></g>')

    p += [f'<g opacity="0">{window(DIE + .1, SWITCH_OFF + .3)}'
          f'<text x="590" y="470" fill="{c["text"]}" font-size="44" font-weight="700" text-anchor="middle" letter-spacing="8">GAME OVER</text></g>',
          '</g>',
          # brightness flash as the tube switches off
          f'<path d="{SHAPE}" fill="{c["text"]}" opacity="0">'
          f'<animate attributeName="opacity" values="0;0;.35;0;0" keyTimes="0;{frac(SWITCH_OFF)};{frac(SWITCH_OFF + .08)};{frac(SWITCH_OFF + .25)};1" '
          f'dur="{INTRO}s" fill="freeze"/></path>',
          '</g></g></g>',
          '</g>',
          # the last glowing dot fades on the dark screen
          f'<circle cx="590" cy="330" r="5" fill="{c["text"]}" opacity="0">'
          f'<animate attributeName="opacity" values="0;0;1;0" keyTimes="0;{(SWITCH_OFF + .25) / (INTRO + .5):.3f};{(SWITCH_OFF + .5) / (INTRO + .5):.3f};1" '
          f'dur="{INTRO + .5:.2f}s" fill="freeze"/></circle>']
    return p
