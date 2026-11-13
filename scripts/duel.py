"""Particle soldiers trading shots; static renderers keep both players aiming."""
import json
import math
from functools import lru_cache

from heroes import dots_path, burst, schedule
from visuals import ASSETS, THEMES, line, rect, text

LOOP = 5.6
DT = .05
HEIGHT = 180
GROUND = 276
PLAYERS = ((300, 1), (880, -1))
# (trigger time, shooter, kill); arrival effects follow the bullet's flight.
SHOTS = ((.60, 0, False), (1.45, 1, True), (3.55, 0, True))
FLIGHT = .18


@lru_cache(maxsize=1)
def drawing():
    """Load the left-facing soldier once, retaining bright and dim particles."""
    aim = json.loads((ASSETS / 'fpsonline' / 'particles.json').read_text(encoding='utf-8'))['aim']
    return [tuple(d) for d in aim['dots']]


def geometry():
    dots = drawing()
    top, bottom = min(d[1] for d in dots), max(d[1] for d in dots)
    sy = HEIGHT / (bottom - top)
    sx = sy
    waist = [x for x, y, _, _ in dots if y >= bottom - 9]
    anchor = sum(waist) / len(waist)
    tip = min(d[0] for d in dots)
    tip_y = sum(d[1] for d in dots if d[0] == tip) / sum(d[0] == tip for d in dots)
    return sx, sy, anchor, bottom, tip, tip_y


def ramp(t, points):
    """Piecewise-linear pulse, zero outside its endpoints (as in heroes.brawl)."""
    if t <= points[0][0] or t >= points[-1][0]:
        return 0
    for (a, u), (b, v) in zip(points, points[1:]):
        if a <= t <= b:
            return u + (v - u) * (t - a) / (b - a)
    return 0


def pose(player, t):
    """Breathing, recoil and the one successful duck, in card coordinates."""
    facing = PLAYERS[player][1]
    dx = angle = 0
    dy = 1.4 * math.sin(2 * math.pi * (t / LOOP * 5 + player * .5))
    for when, shooter, kill in SHOTS:
        if shooter == player:
            kick = ramp(t, [(when, 0), (when + .03, 1), (when + .15, 0)])
            dx -= facing * 6 * kick
            angle -= facing * 4 * kick
        elif not kill:
            dy += ramp(t, [(when - .20, 0), (when - .06, 160),
                           (when + FLIGHT + .06, 160), (when + FLIGHT + .28, 0)])
    return round(dx, 1), round(dy, 1), round(angle, 1)


def animate(attribute, events, transform=False):
    """Explicit continuous keys for short effects and sampled motion tracks."""
    tag = 'animateTransform' if transform else 'animate'
    kind = f' type="{attribute}"' if transform else ''
    name = 'transform' if transform else attribute
    keys = ';'.join(f'{t / LOOP:.4f}' for t, _ in events)
    values = ';'.join(str(value) for _, value in events)
    return (f'<{tag} attributeName="{name}"{kind} values="{values}" keyTimes="{keys}" '
            f'dur="{LOOP}s" repeatCount="indefinite"/>')


def pulse(when, duration):
    return animate('opacity', [(0, 0), (when, 0), (when + .01, 1),
                               (when + duration, 0), (LOOP, 0)])


def track(player):
    times = sorted({round(i * DT, 2) for i in range(round(LOOP / DT) + 1)} |
                   {round(when + offset, 2) for when, _, _ in SHOTS
                    for offset in (0, .03, .15)})
    poses = [(t, pose(player, t)) for t in times]
    x = PLAYERS[player][0]
    return (animate('translate', [(t, f'{dx:g} {dy:g}') for t, (dx, dy, _) in poses], True),
            animate('rotate', [(t, f'{a:g} {x} 224') for t, (_, _, a) in poses], True))


def alive(player, t):
    for when, shooter, kill in SHOTS:
        death = round(when + FLIGHT, 2)
        if kill and shooter != player:
            if death + .10 <= t < death + .80:
                return 0
            if death + .80 <= t < death + 1.10:
                return round((t - death - .80) / .30, 1)
    return 1


def dissolve(player, death, c):
    """36 body samples scatter ballistically, then retrace their paths to respawn."""
    sx, sy, anchor, bottom, _, _ = geometry()
    x, facing = PLAYERS[player]
    body = [d for d in drawing() if d[0] >= anchor - 35]
    samples = [body[i * len(body) // 36] for i in range(36)]
    points = [(x - facing * sx * (px - anchor), 270 + sy * (py - bottom))
              for px, py, _, _ in samples]

    def path(progress):
        out = []
        for i, (px, py) in enumerate(points):
            angle = i * 2.4
            vx, vy = math.cos(angle) * (22 + i % 6 * 6), -24 - i % 7 * 5
            # Stable particle order lets one path interpolate all 36 trajectories.
            xx = px + vx * progress
            yy = min(GROUND, py + vy * progress + 100 * progress * progress)
            out.append(f'M{xx:.0f} {yy:.0f}h0')
        return ''.join(out)

    rest, middle, far = path(0), path(.5), path(1)
    start = round(death + .10, 2)
    keys = [(0, rest), (start, rest), (death + .35, middle), (death + .65, far),
            (death + .80, far), (death + .95, middle), (death + 1.10, rest), (LOOP, rest)]
    opacity = [(0, 0), (start, 0), (start + .01, 1), (death + .65, 0),
               (death + .80, 0), (death + .95, 1), (death + 1.10, 0), (LOOP, 0)]
    return (f'<path d="{rest}" fill="none" stroke="{c["text"]}" stroke-width="3" '
            f'stroke-linecap="round" opacity="0">{animate("d", keys)}'
            f'{animate("opacity", opacity)}</path>')


def scene(c) -> list[str]:
    """SVG fragments for the stage and score of an 1180 by 300 project cover."""
    sx, sy, anchor, bottom, tip, tip_y = geometry()
    parts = [f'<defs><g id="duel-soldier">{dots_path(drawing())}</g>'
             f'<linearGradient id="duel-trail" gradientUnits="userSpaceOnUse" '
             f'x1="-33" y1="0" x2="-9" y2="0"><stop stop-color="{c["text"]}" stop-opacity="0"/>'
             f'<stop offset="1" stop-color="{c["text"]}"/></linearGradient>'
             '<clipPath id="duel-bounds"><rect x="40" y="56" width="1100" height="236"/></clipPath>'
             '<clipPath id="duel-floor"><rect x="40" y="56" width="1100" height="220"/></clipPath></defs>',
             '<g clip-path="url(#duel-bounds)"><g>']
    shake = [(0, '0 0')]
    for when, _, _ in SHOTS:
        shake.extend((when + offset, value) for offset, value in
                     ((0, '0 0'), (.02, '-3 2'), (.05, '3 -2'),
                      (.08, '-2 1'), (.11, '2 -1'), (.15, '0 0')))
    shake.append((LOOP, '0 0'))
    parts.append(animate('translate', shake, True))
    parts.append(line(40, GROUND + 2, 1140, GROUND + 2, c['line'], 'stroke-dasharray="2 6"'))
    for player, (x, facing) in enumerate(PLAYERS):
        move, turn = track(player)
        place = (f'translate({x} 270) scale({-facing * sx:.4f} {sy:.4f}) '
                 f'translate({-anchor:.2f} {-bottom})')
        flash = schedule('stroke', lambda t: c['text'] if any(
            kill and shooter != player and round(when + FLIGHT, 2) <= t < round(when + FLIGHT + .10, 2)
            for when, shooter, kill in SHOTS) else c['accent'], loop=LOOP)
        visibility = schedule('opacity', lambda t: alive(player, t), loop=LOOP)
        parts.append(f'<ellipse cx="{x}" cy="{GROUND + 1}" rx="39" ry="4" '
                     f'fill="{c["accent"]}" opacity=".12"/>')
        parts.append(f'<g clip-path="url(#duel-floor)"><g>{move}<g>{turn}<g stroke="{c["accent"]}" '
                     f'stroke-linecap="round" fill="none">{flash}'
                     f'<use href="#duel-soldier" transform="{place}">{visibility}</use>'
                     '</g></g>' + text(x, 78, f'P{player + 1}', c['muted'], 11, 'middle', 700) + '</g></g>')
    # Dissolution stays behind cover, just like the waist and the ducked drawing.
    for when, shooter, kill in SHOTS:
        if kill:
            parts.append('<g clip-path="url(#duel-floor)">' +
                         dissolve(1 - shooter, round(when + FLIGHT, 2), c) + '</g>')
    for x, _ in PLAYERS:
        parts.extend((rect(x - 43, 226, 86, 50, c['panel'], c['line'], 3),
                      line(x - 36, 234, x + 36, 234, c['line']),
                      line(x - 34, 268, x + 34, 239, c['line']),
                      line(x - 34, 239, x + 34, 268, c['line'])))
    for when, shooter, kill in SHOTS:
        x, facing = PLAYERS[shooter]
        dx, dy, _ = pose(shooter, when)
        mx = round(x - facing * sx * (tip - anchor) + dx, 1)
        my = round(270 + sy * (tip_y - bottom) + dy, 1)
        victim = 1 - shooter
        tx = PLAYERS[victim][0] + facing * 5
        ty = my if kill else 226
        rays = ''.join(f'M{mx + math.cos(i * math.pi / 4) * 4:.1f} '
                       f'{my + math.sin(i * math.pi / 4) * 4:.1f}'
                       f'l{math.cos(i * math.pi / 4) * 14:.1f} '
                       f'{math.sin(i * math.pi / 4) * 14:.1f}' for i in range(8))
        parts.append(f'<path d="{rays}" fill="none" stroke="{c["text"]}" '
                     f'stroke-width="2.5" opacity="0">{pulse(when, .08)}</path>')
        arrival = round(when + FLIGHT, 2)
        flight = animate('translate', [(0, f'{mx} {my}'), (when, f'{mx} {my}'),
                                       (arrival, f'{tx} {ty}'), (LOOP, f'{tx} {ty}')], True)
        visible = schedule('opacity', lambda t: int(when <= t < arrival), loop=LOOP)
        angle = math.degrees(math.atan2(ty - my, tx - mx))
        parts.append(f'<g class="duel-bullet" opacity="0">{visible}{flight}'
                     f'<g transform="rotate({angle:.2f})">'
                     '<line x1="-33" y1="0" x2="-9" y2="0" stroke="url(#duel-trail)" '
                     'stroke-width="2" opacity=".35"/>'
                     f'<line x1="-7.5" y1="0" x2="-1.5" y2="0" stroke="{c["text"]}" '
                     'stroke-width="3" stroke-linecap="round"/></g></g>')
        # Ejected brass arcs up and back, then falls to the ground.
        for i in range(3):
            start = round(when + i * .02, 2)
            ex = round(mx - facing * 22, 1)
            trajectory = [(0, '0 0'), (start, '0 0'),
                          (start + .12, f'{-facing * (12 + i * 4)} {-22 - i * 3}'),
                          (start + .28, f'{-facing * (24 + i * 6)} -12'),
                          (start + .50, f'{-facing * (35 + i * 8)} {GROUND - my:.1f}'),
                          (LOOP, f'{-facing * (35 + i * 8)} {GROUND - my:.1f}')]
            parts.append(f'<path d="M{ex} {my}l2 -1" stroke="{c["accent"]}" '
                         f'stroke-width="2" opacity="0">{pulse(start, .55)}'
                         f'{animate("translate", trajectory, True)}</path>')
        if not kill:
            parts.extend(burst(round(when + FLIGHT, 2), tx, round(ty), c['muted'], loop=LOOP))
    parts.append('</g></g>')
    # Text contents stay static; discrete opacity switches complete score states.
    for state, score in enumerate(('0 – 0', '0 – 1', '1 – 1')):
        shown = schedule('opacity', lambda t: int(sum(
            kill and t >= round(when + FLIGHT, 2) for when, _, kill in SHOTS) == state), loop=LOOP)
        parts.append(f'<text x="590" y="40" text-anchor="middle" font-size="13" font-weight="700" '
                     f'fill="{c["muted"]}" opacity="{1 if state == 0 else 0}">{shown}'
                     f'<tspan>P1</tspan> {score} '
                     f'<tspan font-weight="{900 if state == 1 else 700}">P2</tspan></text>')
    return parts


if __name__ == '__main__':
    # Local self-check only: no files are written or generators invoked.
    from xml.etree import ElementTree as ET

    assert len(drawing()) >= 36
    assert .16 <= FLIGHT <= .20
    for (when, _, kill), (next_shot, _, _) in zip(SHOTS, (*SHOTS[1:], (LOOP, 0, False))):
        assert when + FLIGHT + (1.10 if kill else 0) < next_shot, 'Arrival or respawn overlaps next shot'
    for player in range(2):
        assert pose(player, 0) == pose(player, LOOP), 'Idle motion must loop'
    for when, shooter, kill in SHOTS:
        assert pose(shooter, when + .03)[0] == -PLAYERS[shooter][1] * 6
        assert abs(pose(shooter, when + .03)[2]) == 4
        if kill:
            death = round(when + FLIGHT, 2)
            assert alive(1 - shooter, death + .20) == 0
            assert 0 < alive(1 - shooter, death + .95) < 1
            assert alive(1 - shooter, death + 1.11) == 1
        else:
            assert pose(1 - shooter, when + FLIGHT)[1] > 155
    sx, sy, anchor, bottom, tip, _ = geometry()
    assert sx == sy, 'Soldiers must retain their original proportions'
    assert PLAYERS[0][0] + sx * (anchor - tip) < PLAYERS[1][0] - sx * (anchor - tip), 'Pistols overlap'
    for x, facing in PLAYERS:
        for px, py, _, _ in drawing():
            assert 40 <= x - facing * sx * (px - anchor) <= 1140
            assert 56 <= 270 + sy * (py - bottom) <= 292
    for theme in THEMES.values():
        content = ''.join(scene(theme))
        root = ET.fromstring(f'<svg>{content}</svg>')
        size = len(content.encode('utf-8'))
        assert size < 45_000, f'Scene exceeds 45 KB: {size} bytes'
        bounds = root.find('.//clipPath[@id="duel-bounds"]/rect')
        assert bounds.attrib == dict(x='40', y='56', width='1100', height='236')
        floor = root.find('.//clipPath[@id="duel-floor"]/rect')
        assert floor.attrib == dict(x='40', y='56', width='1100', height='220')
        hud = root.findall('./text')
        assert len(hud) == 3
        assert all(label.get('x') == '590' and label.get('y') == '40' and
                   label.get('font-size') == '13' and label.get('font-weight') == '700'
                   for label in hud)
        assert [label.get('opacity') for label in hud] == ['1', '0', '0']
        assert len(root.findall('.//use')) == 2
        assert len(root.findall('.//g[@id="duel-soldier"]')) == 1
        bullets = root.findall('.//g[@class="duel-bullet"]')
        assert len(bullets) == len(SHOTS)
        for bullet, (when, _, _) in zip(bullets, SHOTS):
            assert bullet.get('opacity') == '0', 'Bullets must be hidden without SMIL'
            motion = bullet.find('animateTransform')
            keys = [float(t) for t in motion.get('keyTimes').split(';')]
            assert abs(keys[1] * LOOP - when) < .001
            assert abs(keys[2] * LOOP - when - FLIGHT) < .001
            positions = motion.get('values').split(';')
            assert positions[0] == positions[1] and positions[2] == positions[3]
            visibility = bullet.find('animate')
            assert visibility.get('values') == '0;1;0'
            assert visibility.get('keyTimes').split(';') == motion.get('keyTimes').split(';')[:3]
            streak, round_ = bullet.findall('./g/line')
            assert float(streak.get('x2')) - float(streak.get('x1')) == 24
            assert streak.get('opacity') == '.35'
            assert round_.get('stroke-width') == '3' and round_.get('stroke-linecap') == 'round'
        for animation in list(root.iter('animate')) + list(root.iter('animateTransform')):
            values = animation.attrib['values'].split(';')
            keys = [float(t) for t in animation.attrib['keyTimes'].split(';')]
            assert len(values) == len(keys), animation.attrib
            assert keys[0] == 0 and keys[-1] <= 1
            assert all(a < b for a, b in zip(keys, keys[1:])), animation.attrib
            assert animation.get('repeatCount') == 'indefinite'
        for effect in root.findall('.//path') + root.findall('.//line'):
            if effect.find('animate') is not None:
                assert effect.get('opacity') == '0', 'Effects must be hidden without SMIL'
        print(f'Duel checks passed: {size:,} bytes.')
