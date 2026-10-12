"""UN-CREDIBLES cover: four identical particle heroes brawling in two duels.

The hero comes from the team's concept sketch (side view) in
assets/uncredibles/hero.png. Line art becomes bright particles; the body below
the neck is filled with dimmer particles as a plain suit.
"""
import math
import random
from collections import deque
from functools import lru_cache

from avatar import read_png
from visuals import ASSETS

STEP = 6            # particle spacing in source pixels
NECK = 178          # source row where the head ends and the suit starts
HEIGHT = 220        # hero height in the cover
GROUND = 276
LOOP = 6            # seconds: one round of the brawl
DT = .05
# x of each hero's feet and the way it faces (+1 right, -1 left): two duels
HEROES = ((230, 1), (430, -1), (750, 1), (950, -1))
# (time, attacker, victim, big): a big hit sends the victim flying
HITS = ((.5, 0, 1, False), (1.1, 3, 2, False), (1.9, 1, 0, False),
        (2.6, 2, 3, False), (3.4, 0, 1, True), (4.2, 3, 2, True))


@lru_cache(maxsize=None)
def particles():
    """[(x, y, radius, opacity)] in source pixels; deterministic."""
    img = read_png(ASSETS / 'uncredibles' / 'hero.png')
    h, w = len(img), len(img[0])
    lum = [[p[0] for p in row] for row in img]
    # thicken the strokes so the flood fill cannot leak through gaps in the sketch
    wall = [[False] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            if lum[y][x] < 150:
                for j in range(max(0, y - 2), min(h, y + 3)):
                    for i in range(max(0, x - 2), min(w, x + 3)):
                        wall[j][i] = True
    outside = [[False] * w for _ in range(h)]
    queue = deque([(x, y) for y in range(h) for x in (0, w - 1)] + [(x, y) for x in range(w) for y in (0, h - 1)])
    while queue:
        x, y = queue.popleft()
        if 0 <= x < w and 0 <= y < h and not outside[y][x] and not wall[y][x]:
            outside[y][x] = True
            queue.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    rnd, dots = random.Random(5), []
    for gy in range(0, h, STEP):
        for gx in range(0, w, STEP):
            cells = [(x, y) for y in range(gy, min(gy + STEP, h)) for x in range(gx, min(gx + STEP, w))]
            ink = 1 - min(lum[y][x] for x, y in cells) / 255
            jitter = STEP * .25
            x, y = round(gx + STEP / 2 + rnd.uniform(-jitter, jitter), 1), round(gy + STEP / 2 + rnd.uniform(-jitter, jitter), 1)
            if ink > .45:
                dots.append((x, y, round(STEP * (.22 + .14 * ink), 2), round(.55 + .45 * ink, 2)))
            elif gy > NECK and sum(not outside[y][x] for x, y in cells) > len(cells) * .7:
                dots.append((x, y, round(STEP * .22, 2), .42))
    return dots, w, h

def ramp(t, points):
    """Piecewise-linear value at t from [(time, value)]; 0 outside."""
    if t <= points[0][0] or t >= points[-1][0]:
        return 0
    for (t0, v0), (t1, v1) in zip(points, points[1:]):
        if t0 <= t <= t1:
            return v0 + (v1 - v0) * (t - t0) / (t1 - t0)
    return 0

def pose(hero, t):
    """dx, dy, angle of one hero at time t: idle bob plus every hit it takes part in."""
    facing = HEROES[hero][1]
    dx = dy = angle = 0
    dy += 2.5 * math.sin(2 * math.pi * (t / 1.2 + hero * .3))
    for when, attacker, victim, big in HITS:
        if hero == attacker:
            dx += facing * ramp(t, [(when - .15, 0), (when, 34), (when + .35, 0)])
        if hero == victim and not big:
            dx -= facing * ramp(t, [(when, 0), (when + .12, 46), (when + .7, 0)])
            angle -= facing * ramp(t, [(when, 0), (when + .12, 16), (when + .6, 0)])
        if hero == victim and big:
            dx -= facing * ramp(t, [(when, 0), (when + .35, 80), (when + .7, 95), (when + .9, 95), (when + 1.6, 0)])
            dy -= ramp(t, [(when, 0), (when + .35, 70), (when + .7, 0)])
            angle -= facing * ramp(t, [(when, 0), (when + .35, 200), (when + .7, 360)])
    return round(dx, 1), round(dy, 1), round(angle, 1)

def track(hero):
    times = [round(i * DT, 2) for i in range(int(LOOP / DT) + 1)]
    poses, turned = [], 0
    for t in times:
        dx, dy, angle = pose(hero, t)
        # after a full flip the angle snaps back to 0; keep it continuous (360 looks the same)
        while poses and angle + turned - poses[-1][2] > 180:
            turned -= 360
        while poses and angle + turned - poses[-1][2] < -180:
            turned += 360
        poses.append((dx, dy, round(angle + turned, 1)))
    keys = ';'.join(f'{t / LOOP:.4f}' for t in times)
    moves = ';'.join(f'{dx} {dy}' for dx, dy, _ in poses)
    x = HEROES[hero][0]
    turns = ';'.join(f'{a} {x} {GROUND - HEIGHT * .45:.0f}' for _, _, a in poses)
    return keys, moves, turns

def burst(when, x, y, ink):
    """A few particles fly out of the impact point."""
    rnd, out = random.Random(int(when * 100)), []
    k = lambda t: f'{min(t, LOOP) / LOOP:.4f}'
    for _ in range(12):
        angle, reach = rnd.uniform(0, 2 * math.pi), rnd.uniform(18, 46)
        ex, ey = round(math.cos(angle) * reach), round(math.sin(angle) * reach)
        out.append(f'<circle cx="{x}" cy="{y}" r="{rnd.uniform(1.2, 2.4):.1f}" fill="{ink}" opacity="0">'
                   f'<animate attributeName="opacity" values="0;0;1;0;0" keyTimes="0;{k(when)};{k(when + .05)};{k(when + .4)};1" '
                   f'dur="{LOOP}s" repeatCount="indefinite"/>'
                   f'<animateTransform attributeName="transform" type="translate" values="0 0;0 0;{ex} {ey};{ex} {ey}" '
                   f'keyTimes="0;{k(when)};{k(when + .4)};1" dur="{LOOP}s" repeatCount="indefinite"/></circle>')
    return out

def brawl(c):
    dots, w, h = particles()
    scale = HEIGHT / h
    parts = ['<defs><g id="hero">' + ''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill-opacity="{o}"/>' for x, y, r, o in dots) + '</g></defs>',
             f'<line x1="40" y1="{GROUND + 2}" x2="1140" y2="{GROUND + 2}" stroke="{c["line"]}" stroke-dasharray="2 6"/>']
    for i, (x, facing) in enumerate(HEROES):
        keys, moves, turns = track(i)
        # the sketch faces left; mirror it for heroes facing right
        place = f'translate({x} {GROUND}) scale({-facing * scale:.4f} {scale:.4f}) translate({-w / 2:.0f} {-h})'
        parts.append(f'<ellipse cx="{x}" cy="{GROUND + 2}" rx="38" ry="5" fill="{c["accent"]}" opacity=".12"/>'
                     f'<g><animateTransform attributeName="transform" type="translate" values="{moves}" keyTimes="{keys}" dur="{LOOP}s" repeatCount="indefinite"/>'
                     f'<g><animateTransform attributeName="transform" type="rotate" values="{turns}" keyTimes="{keys}" dur="{LOOP}s" repeatCount="indefinite"/>'
                     f'<use href="#hero" fill="{c["accent"]}" transform="{place}"/>'
                     f'<text x="{x}" y="{GROUND - HEIGHT - 10}" fill="{c["muted"]}" font-size="13" font-weight="700" text-anchor="middle">P{i + 1}</text>'
                     '</g></g>')
    for when, attacker, victim, _ in HITS:
        x = (HEROES[attacker][0] + HEROES[victim][0]) / 2
        parts += burst(when, round(x), round(GROUND - HEIGHT * .55), c['text'])
    return parts
