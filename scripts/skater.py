"""Roller Hunter card: the hero skates through two demons, in the style of the UN-CREDIBLES cover.

The hero ("here we go", on skates, slingshot in hand) and a demon were extracted once from
the comic that opens the game's trailer into assets/rollerhunter/particles.json; the
frames are not kept in the repo. The hero skates in, slings a stone at the first demon, kickflips
over the second one hitting it from the air, lands in a puff of dust and skates off;
the demons respawn for the next loop. Static renderers show everyone standing.
"""
import json
import math
import random
from functools import lru_cache

from visuals import ASSETS
from heroes import burst, dots_path, schedule

LOOP = 6
DT = .05
GROUND = 276                    # same ground line as the UN-CREDIBLES cover
HERO_H, DEMON_H = 190, 150      # drawn heights in the card
# hero x over time: in from the left, a glide, the kickflip, off to the right
PATH = ((0, -110), (.3, -110), (1.4, 330), (2.6, 700), (3.3, 1010), (4.3, 1300), (LOOP, 1300))
JUMP = (2.6, 3.3, 40)           # start, landing, height
DEMONS = (600, 860)             # x of each demon
SHOTS = ((1.4, 0), (2.95, 1))   # (time, demon): the second one from the top of the flip
FLIGHT = .22                    # seconds a slingshot stone takes to reach its demon
RESPAWN = 5.2
STATIC_X = 330                  # where the hero stands for static renderers


@lru_cache(maxsize=None)
def drawing(name):
    pose = json.loads((ASSETS / 'rollerhunter' / 'particles.json').read_text(encoding='utf-8'))[name]
    return [tuple(d) for d in pose['dots']], pose['width'], pose['height']

def ramp(t, points):
    for (t0, v0), (t1, v1) in zip(points, points[1:]):
        if t0 <= t <= t1:
            return v0 + (v1 - v0) * (t - t0) / (t1 - t0) if t1 > t0 else v1
    return points[-1][1]

def hero(t):
    """x, dy (up is negative) and angle of the hero at t."""
    start, land, height = JUMP
    x = ramp(t, PATH)
    dy, angle = 2 * math.sin(2 * math.pi * t / .6), 5       # stride bob, leaning into the skate
    if start <= t <= land:
        u = (t - start) / (land - start)
        dy = -4 * height * u * (1 - u)
        angle = 5 + 360 * u * u * (3 - 2 * u)               # kickflip
    elif t > land:
        angle += 360    # same pose after the flip; dropping back to 5 would spin it backwards
    return x, dy, angle

def demon_dead(i, t):
    """Hidden from just after its hit until the respawn."""
    when = SHOTS[i][0] + FLIGHT
    return when + .15 <= t < RESPAWN

def scale(name):
    _, _, h = drawing(name)
    return (HERO_H if name == 'go' else DEMON_H) / h

def pivot():
    """Centre of the hero, relative to its feet."""
    return -HERO_H * .5

def gun(t):
    """Card position of the hero's slingshot hand at t, rotation included (the drawing is mirrored)."""
    dots, w, h = drawing('go')
    # the slingshot is in the hand on the drawing's left; mirrored it is on the right
    hand = [(x, y) for x, y, _, _ in dots if x < w * .45 and h * .3 < y < h * .52]
    gx = max(w - x for x, _ in hand) - w / 2
    gy = sum(y for _, y in hand) / len(hand) - h
    s = scale('go')
    px, py = gx * s, gy * s - pivot()
    x, dy, angle = hero(t)
    a = math.radians(angle)
    return (round(x + px * math.cos(a) - py * math.sin(a)),
            round(GROUND + dy + pivot() + px * math.sin(a) + py * math.cos(a)))

def place(name, mirror=False):
    _, w, h = drawing(name)
    s = scale(name)
    return f'scale({-s if mirror else s:.4f} {s:.4f}) translate({-w / 2:.0f} {-h})'

def explode(when, cx, ink, seed):
    """The demon's own particles flying apart and falling."""
    dots, w, h = drawing('demon')
    s, rnd = scale('demon'), random.Random(seed)
    k = lambda u: f'{min(u, LOOP) / LOOP:.4f}'
    out = []
    for x, y, r, _ in rnd.sample(dots, 34):
        sx, sy = round(cx + (x - w / 2) * s), round(GROUND + (y - h) * s)
        ex, ey = round(rnd.uniform(-1, 1) * 70 + 30), round(rnd.uniform(-60, 10))
        fall = round(GROUND - sy + rnd.uniform(-4, 0))
        out.append(f'<circle cx="{sx}" cy="{sy}" r="{max(1.2, r * s):.1f}" fill="{ink}" opacity="0">'
                   f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;{k(when)};{k(when + .02)};{k(when + .5)};{k(when + .8)};1" '
                   f'dur="{LOOP}s" repeatCount="indefinite"/>'
                   f'<animateTransform attributeName="transform" type="translate" values="0 0;0 0;{ex // 2} {ey};{ex} {fall};{ex} {fall}" '
                   f'keyTimes="0;{k(when)};{k(when + .25)};{k(when + .7)};1" dur="{LOOP}s" repeatCount="indefinite"/></circle>')
    return out

def scene(c):
    ink, hot = c['accent'], c['text']
    k = lambda u: f'{u / LOOP:.4f}'
    times = [round(i * DT, 2) for i in range(int(LOOP / DT) + 1)]
    keys = ';'.join(k(t) for t in times)
    track = [hero(t) for t in times]
    parts = [f'<defs><g id="rh-hero">{dots_path(drawing("go")[0])}</g><g id="rh-demon">{dots_path(drawing("demon")[0])}</g></defs>',
             f'<line x1="40" y1="{GROUND + 2}" x2="1140" y2="{GROUND + 2}" stroke="{c["line"]}" stroke-dasharray="2 6"/>']
    # demons: idle bob, hit flash, knocked back, gone until the respawn (which fades them in)
    for i, x in enumerate(DEMONS):
        when = SHOTS[i][0] + FLIGHT     # everything happens when the stone lands
        shown = schedule('opacity', lambda t, i=i: 0 if demon_dead(i, t) else 1, LOOP)
        flash = schedule('stroke', lambda t, when=when: hot if when <= t < when + .12 else ink, LOOP)
        knock = (f'<animateTransform attributeName="transform" type="translate" '
                 f'values="0 0;0 0;14 -4;18 0;18 0;0 0" keyTimes="0;{k(when)};{k(when + .08)};{k(when + .15)};{k(RESPAWN)};1" '
                 f'dur="{LOOP}s" repeatCount="indefinite"/>')
        rise = (f'<animate attributeName="opacity" values="1;1;0;0;1;1" keyTimes="0;{k(when)};{k(when + .01)};{k(RESPAWN)};{k(RESPAWN + .4)};1" '
                f'dur="{LOOP}s" repeatCount="indefinite"/>')
        bob = (f'<animateTransform attributeName="transform" type="translate" values="0 0;0 -3;0 0" '
               f'dur="{.9 + i * .23:.2f}s" repeatCount="indefinite"/>')
        parts.append(f'<ellipse cx="{x}" cy="{GROUND + 2}" rx="22" ry="4" fill="{ink}" opacity=".12">{shown}</ellipse>'
                     f'<g>{knock}<g>{rise}<g>{bob}<g stroke="{ink}" stroke-linecap="round" fill="none">{flash}'
                     f'<use href="#rh-demon" transform="translate({x} {GROUND}) {place("demon")}">{shown}</use></g></g></g></g>'
                     f'<text x="{x}" y="{GROUND - DEMON_H - 10}" fill="{c["muted"]}" font-size="12" font-weight="700" text-anchor="middle">'
                     f'DEMON{schedule("opacity", lambda t, i=i: 0 if demon_dead(i, t) else 1, LOOP)}</text>')
        parts += explode(when + .15, x + 18, ink, i)
    # the hero: shadow on the ground, then the moving body; static renderers see it at STATIC_X
    moves = ';'.join(f'{x:.0f} {dy:.1f}' for x, dy, _ in track)
    turns = ';'.join(f'{a:.0f} 0 {GROUND + pivot():.0f}' for _, _, a in track)
    shadow = ';'.join(f'{x:.0f} 0' for x, _, _ in track)
    shadow_rx = ';'.join(f'{30 * max(.4, 1 + dy / 120):.1f}' for _, dy, _ in track)
    parts.append(f'<ellipse cx="0" cy="{GROUND + 2}" rx="30" ry="5" fill="{ink}" opacity=".14" transform="translate({STATIC_X} 0)">'
                 f'<animateTransform attributeName="transform" type="translate" values="{shadow}" keyTimes="{keys}" dur="{LOOP}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="rx" values="{shadow_rx}" keyTimes="{keys}" dur="{LOOP}s" repeatCount="indefinite"/></ellipse>'
                 f'<g transform="translate({STATIC_X} 0)">'
                 f'<animateTransform attributeName="transform" type="translate" values="{moves}" keyTimes="{keys}" dur="{LOOP}s" repeatCount="indefinite"/>'
                 f'<g><animateTransform attributeName="transform" type="rotate" values="{turns}" keyTimes="{keys}" dur="{LOOP}s" repeatCount="indefinite"/>'
                 f'<g stroke="{ink}" stroke-linecap="round" fill="none">'
                 f'<use href="#rh-hero" transform="translate(0 {GROUND}) {place("go", mirror=True)}"/></g></g>'
                 # the label follows the hero but never spins with it
                 f'<text x="0" y="{GROUND - HERO_H - 12}" fill="{c["muted"]}" font-size="12" font-weight="700" text-anchor="middle">P1</text>'
                 '</g>')
    # shots: in the game he hunts with a slingshot. The band snaps, a stone arcs to the demon's chest.
    for when, i in SHOTS:
        gx, gy = gun(when)
        tx, ty = DEMONS[i] + 4, round(GROUND - DEMON_H * .55)
        steps = [j / 6 for j in range(7)]
        arc = ';'.join(f'{(tx - gx) * u:.0f} {(ty - gy) * u - 28 * 4 * u * (1 - u):.0f}' for u in steps)
        keys = ';'.join(['0'] + [k(when + FLIGHT * u) for u in steps] + ['1'])
        first, last = arc.split(';')[0], arc.split(';')[-1]
        parts.append(f'<circle cx="{gx}" cy="{gy}" r="3.5" fill="{hot}" opacity="0">'
                     f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;{k(when)};{k(when + .01)};{k(when + FLIGHT - .01)};{k(when + FLIGHT)};1" '
                     f'dur="{LOOP}s" repeatCount="indefinite"/>'
                     f'<animateTransform attributeName="transform" type="translate" values="{first};{arc};{last}" keyTimes="{keys}" '
                     f'dur="{LOOP}s" repeatCount="indefinite"/></circle>'
                     # the band snapping back: a small V at the hand
                     f'<path d="M{gx - 7} {gy - 8}L{gx + 3} {gy}L{gx - 7} {gy + 8}" fill="none" stroke="{hot}" stroke-width="2" stroke-linecap="round" opacity="0">'
                     f'<animate attributeName="opacity" values="0;0;1;0;0" keyTimes="0;{k(when)};{k(when + .01)};{k(when + .12)};1" '
                     f'dur="{LOOP}s" repeatCount="indefinite"/></path>')
        when += FLIGHT
        parts += burst(when, round(tx), round(ty), hot, loop=LOOP)
    # skate sparks while gliding, a big puff of dust on landing
    for when in (.9, 1.9, 2.4, 3.7):
        x, _, _ = hero(when)
        parts += burst(when, round(x), GROUND, ink, ground=True, loop=LOOP)[:6]
    parts += burst(JUMP[1], round(hero(JUMP[1])[0]), GROUND, ink, ground=True, loop=LOOP)
    return parts
