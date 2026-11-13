"""Roller Hunter card: the hero skates through two demons, in the style of the UN-CREDIBLES cover.

The hero ("here we go", on skates, slingshot in hand) and a demon were extracted once from
the comic that opens the game's trailer into assets/rollerhunter/particles.json; the
frames are not kept in the repo. The hero skates in, slings a stone at the first demon, jumps
and hits the second one from the top of the jump, lands in a puff of dust and skates off;
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
# hero x over time: in from the left, a glide, the jump, off to the right
# he lands just short of the second demon, which is gone by the time he skates through
PATH = ((0, -110), (.3, -110), (1.4, 330), (2.6, 640), (3.3, 800), (4.3, 1300), (LOOP, 1300))
JUMP = (2.6, 3.3, 55)           # take-off, landing, height
DEMONS = (600, 860)             # x of each demon
SHOTS = ((1.4, 0), (2.95, 1))   # (release, demon): the second one from the top of the jump
AIM = .35                       # seconds spent drawing the band back before each release
STRIDE = .6                     # seconds per pair of skating pushes
HIP = .67                       # the legs swing from just under the shorts
ANKLE = .82                     # and the skates this far: they stay flat on the ground
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
    dy, angle = 2 * math.sin(2 * math.pi * t / STRIDE), 5   # stride bob, leaning into the skate
    if start <= t <= land:
        u = (t - start) / (land - start)
        dy = -4 * height * u * (1 - u)
        angle = 5 + 6 * math.sin(math.pi * u)               # a slight forward tilt in the air
    return x, dy, angle

def squash(t):
    """Vertical scale around the feet: crouch before take-off, stretch leaving the ground,
    squash on landing."""
    start, land, _ = JUMP
    return ramp(t, ((0, 1), (start - .18, 1), (start - .02, .88), (start + .08, 1.06), (start + .2, 1),
                    (land - .02, 1), (land + .05, .86), (land + .22, 1), (LOOP, 1)))

def jumping(t):
    start, land, _ = JUMP
    return math.sin(math.pi * (t - start) / (land - start)) if start <= t <= land else 0

def leg(side, t):
    """Angle of one leg around its hip and how far it is tucked up. On the ground the legs
    push outwards in turn; in the
    air both knees come up and out."""
    out = 1 if body()[3][side][0] < 0 else -1      # turning clockwise swings a foot to the left
    if jumping(t):
        return out * 12 * jumping(t), -16 * jumping(t)
    push = math.sin(2 * math.pi * t / STRIDE + (0 if side == 0 else math.pi))
    return out * 16 * max(0, push), -4 * max(0, -push)

@lru_cache(maxsize=None)
def body():
    """The hero split into torso, two legs and two skates, each its own particle set, plus
    each hip and ankle in the hero's local coordinates (feet at 0, GROUND; mirrored like
    the drawing)."""
    dots, w, h = drawing('go')
    s, hip, ankle = scale('go'), h * HIP, h * ANKLE
    local = lambda x, y: (round(-s * (x - w / 2), 1), round(GROUND + s * (y - h), 1))
    side_of = lambda d: 0 if d[0] < w / 2 else 1
    top = [d for d in dots if d[1] < hip]
    legs = [[d for d in dots if hip <= d[1] < ankle and side_of(d) == side] for side in (0, 1)]
    feet = [[d for d in dots if d[1] >= ankle and side_of(d) == side] for side in (0, 1)]
    mean_x = lambda part, y0, y1: (lambda xs: sum(xs) / len(xs))([d[0] for d in part if y0 <= d[1] < y1] or [d[0] for d in part])
    hips = [local(mean_x(legs[side], hip, hip + 20), hip) for side in (0, 1)]
    ankles = [local(mean_x(legs[side], ankle - 20, ankle), ankle) for side in (0, 1)]
    return top, legs, feet, hips, ankles

def hand():
    """The slingshot hand in the hero's local coordinates (the drawing's left hand, mirrored)."""
    dots, w, h = drawing('go')
    s = scale('go')
    grip = [(x, y) for x, y, _, _ in dots if x < w * .45 and h * .3 < y < h * .52]
    return (max(w - x for x, _ in grip) - w / 2) * s, GROUND + (sum(y for _, y in grip) / len(grip) - h) * s

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
    hx, hy = hand()
    px, py = hx, hy - GROUND - pivot()
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
    top, legs, feet, hips, ankles = body()
    parts = [f'<defs><g id="rh-top">{dots_path(top)}</g>'
             + ''.join(f'<g id="rh-leg{i}">{dots_path(legs[i])}</g><g id="rh-foot{i}">{dots_path(feet[i])}</g>' for i in (0, 1))
             + f'<g id="rh-demon">{dots_path(drawing("demon")[0])}</g></defs>',
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
        parts.append(f'<g>{shown}<ellipse cx="{x}" cy="{GROUND + 2}" rx="22" ry="4" fill="{ink}" opacity=".08"/></g>'
                     f'<g>{knock}<g>{rise}<g>{bob}<g stroke="{ink}" stroke-linecap="round" fill="none">{flash}'
                     f'<use href="#rh-demon" transform="translate({x} {GROUND}) {place("demon")}">{shown}</use></g></g></g></g>'
                     f'<text x="{x}" y="{GROUND - DEMON_H - 10}" fill="{c["muted"]}" font-size="12" font-weight="700" text-anchor="middle">'
                     f'DEMON{schedule("opacity", lambda t, i=i: 0 if demon_dead(i, t) else 1, LOOP)}</text>')
        parts += explode(when + .15, x + 18, ink, i)
    # the hero: shadow on the ground, then the moving body; static renderers see it at STATIC_X
    moves = ';'.join(f'{x:.0f} {dy:.1f}' for x, dy, _ in track)
    turns = ';'.join(f'{a:.0f} 0 {GROUND + pivot():.0f}' for _, _, a in track)
    shadow = ';'.join(f'{x:.0f} 0' for x, _, _ in track)
    squashes = ';'.join(f'{1 + (1 - squash(t)) * .5:.3f} {squash(t):.3f}' for t in times)
    limbs = ''
    for side in (0, 1):
        hx, hy = hips[side]
        turn = ';'.join(f'{leg(side, t)[0]:.1f} {hx} {hy}' for t in times)
        tuck = ';'.join(f'0 {leg(side, t)[1]:.1f}' for t in times)
        # the skate follows the ankle as the leg swings but stays flat on the ground
        ax, ay = ankles[side]
        def follow(t, side=side, hx=hx, hy=hy, ax=ax, ay=ay):
            a, lift = leg(side, t)
            r = math.radians(a)
            dx = (ax - hx) * math.cos(r) - (ay - hy) * math.sin(r) + hx - ax
            dy = (ax - hx) * math.sin(r) + (ay - hy) * math.cos(r) + hy - ay
            # the leg's tuck is applied inside its rotation, so the skate's must be rotated too
            return f'{dx - lift * math.sin(r):.1f} {dy + lift * math.cos(r):.1f}'
        step = ';'.join(follow(t) for t in times)
        limbs += (f'<g><animateTransform attributeName="transform" type="rotate" values="{turn}" keyTimes="{keys}" dur="{LOOP}s" repeatCount="indefinite"/>'
                  f'<g><animateTransform attributeName="transform" type="translate" values="{tuck}" keyTimes="{keys}" dur="{LOOP}s" repeatCount="indefinite"/>'
                  f'<use href="#rh-leg{side}" transform="translate(0 {GROUND}) {place("go", mirror=True)}"/></g></g>'
                  f'<g><animateTransform attributeName="transform" type="translate" values="{step}" keyTimes="{keys}" dur="{LOOP}s" repeatCount="indefinite"/>'
                  f'<use href="#rh-foot{side}" transform="translate(0 {GROUND}) {place("go", mirror=True)}"/></g>')
    # aiming: the band of the slingshot is drawn back to the pouch, then snaps forward on release
    hx, hy = hand()
    pull, seen = [(0, hx)], [(0, 0)]
    for when, _ in SHOTS:
        pull += [(when - AIM, hx), (when - .01, hx - 24), (when + .03, hx + 6), (when + .1, hx)]
        seen += [(when - AIM - .01, 0), (when - AIM, 1), (when + .1, 1), (when + .11, 0)]
    pull.append((LOOP, hx))
    seen.append((LOOP, 0))
    anim = lambda attr, pts: (f'<animate attributeName="{attr}" values="{";".join(f"{v:.0f}" for _, v in pts)}" '
                              f'keyTimes="{";".join(k(t) for t, _ in pts)}" dur="{LOOP}s" repeatCount="indefinite"/>')
    band = ''.join(f'<line x1="{hx + 3:.0f}" y1="{hy + d:.0f}" x2="{hx:.0f}" y2="{hy:.0f}" stroke="{hot}" stroke-width="1.5" opacity="0">'
                   f'{anim("x2", pull)}{anim("opacity", seen)}</line>' for d in (-8, 8))
    shadow_rx = ';'.join(f'{30 * max(.4, 1 + dy / 120):.1f}' for _, dy, _ in track)
    parts.append(f'<ellipse cx="0" cy="{GROUND + 2}" rx="30" ry="5" fill="{ink}" opacity=".14" transform="translate({STATIC_X} 0)">'
                 f'<animateTransform attributeName="transform" type="translate" values="{shadow}" keyTimes="{keys}" dur="{LOOP}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="rx" values="{shadow_rx}" keyTimes="{keys}" dur="{LOOP}s" repeatCount="indefinite"/></ellipse>'
                 f'<g transform="translate({STATIC_X} 0)">'
                 f'<animateTransform attributeName="transform" type="translate" values="{moves}" keyTimes="{keys}" dur="{LOOP}s" repeatCount="indefinite"/>'
                 f'<g><animateTransform attributeName="transform" type="rotate" values="{turns}" keyTimes="{keys}" dur="{LOOP}s" repeatCount="indefinite"/>'
                 f'<g transform="translate(0 {GROUND})"><g>'
                 f'<animateTransform attributeName="transform" type="scale" values="{squashes}" keyTimes="{keys}" dur="{LOOP}s" repeatCount="indefinite"/>'
                 f'<g transform="translate(0 {-GROUND})"><g stroke="{ink}" stroke-linecap="round" fill="none">'
                 f'<use href="#rh-top" transform="translate(0 {GROUND}) {place("go", mirror=True)}"/>{limbs}</g>{band}</g></g></g></g>'
                 # the label follows the hero but never spins with it
                 f'<text x="0" y="{GROUND - HERO_H - 12}" fill="{c["muted"]}" font-size="12" font-weight="700" text-anchor="middle">P1</text>'
                 '</g>')
    # shots: in the game he hunts with a slingshot. He aims (a sight closes on the demon),
    # the band snaps, a stone arcs to the demon's chest.
    for when, i in SHOTS:
        gx, gy = gun(when)
        tx, ty = DEMONS[i] + 4, round(GROUND - DEMON_H * .55)
        parts.append(f'<g opacity="0" stroke="{hot}" fill="none" stroke-width="1.5">'
                     f'<animate attributeName="opacity" values="0;0;.9;.9;0;0" keyTimes="0;{k(when - AIM)};{k(when - AIM + .05)};{k(when + FLIGHT)};{k(when + FLIGHT + .05)};1" '
                     f'dur="{LOOP}s" repeatCount="indefinite"/>'
                     f'<circle cx="{tx}" cy="{ty}" r="22"><animate attributeName="r" values="22;22;9;9" keyTimes="0;{k(when - AIM)};{k(when)};1" '
                     f'dur="{LOOP}s" repeatCount="indefinite"/></circle>'
                     f'<path d="M{tx - 30} {ty}h12M{tx + 18} {ty}h12M{tx} {ty - 30}v12M{tx} {ty + 18}v12"/></g>')
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
