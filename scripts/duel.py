"""Particle soldiers raising their rifles to fire; static renderers show low ready."""
import json
import math
from functools import lru_cache

from heroes import dots_path, burst, schedule
from visuals import ASSETS, THEMES, line, text

LOOP = 5.6
DT = .05
HEIGHT = 214
GROUND = 276
HIP_Y = GROUND - HEIGHT * .4
FENCE_TOP = 224
FENCE_HALF = 80
PLAYERS = ((300, 1), (880, -1))
# (trigger time, shooter, kill); arrival effects follow the bullet's flight.
SHOTS = ((.60, 0, False), (1.45, 1, True), (3.55, 0, True))
FLIGHT = .18


@lru_cache(maxsize=1)
def soldier():
    """Source geometry includes an explicit muzzle on the drawing's right."""
    return json.loads((ASSETS / 'fpsonline' / 'particles.json').read_text(encoding='utf-8'))['soldier']


@lru_cache(maxsize=2)
def drawing(rifle=False):
    """Separate body and rifle particles, in the same source coordinates."""
    return [tuple(d) for d in soldier()['rifle' if rifle else 'dots']]


def geometry():
    dots = drawing()
    top, bottom = min(d[1] for d in dots), max(d[1] for d in dots)
    sy = round(HEIGHT / (bottom - top), 4)
    sx = sy
    anchor = soldier()['width'] / 2
    tip, tip_y = soldier()['muzzle']
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
    """Breathing, recoil, fatal stagger and the successful duck, in card coordinates."""
    facing = PLAYERS[player][1]
    dx = angle = 0
    dy = 1.4 * math.sin(2 * math.pi * (t / LOOP * (5 + player) + player * .25))
    for when, shooter, kill in SHOTS:
        if shooter == player:
            kick = ramp(t, [(when, 0), (when + .03, 1), (when + .12, 0)])
            dx -= facing * 5 * kick
            angle -= facing * 2 * kick
        elif kill:
            death = round(when + FLIGHT, 2)
            hit = ramp(t, [(death, 0), (death + .10, 1),
                           (death + .65, 1), (death + .80, 0)])
            dx -= facing * 10 * hit
            angle -= facing * 8 * hit
        else:
            # Move the entire drawing below the floor clip, even through translucent mesh.
            duck = HEIGHT + 10
            dy += ramp(t, [(when - .20, 0), (when - .06, duck),
                           (when + FLIGHT + .06, duck),
                           (when + FLIGHT + .10, duck + 4), (when + FLIGHT + .28, 0)])
    return round(dx, 1), round(dy, 1), round(angle, 1)


def upper(player, t):
    """Source-space rifle angle: low ready, eased raise, aim, kick, reload dip, lower."""
    for when, shooter, _ in SHOTS:
        if shooter != player or not when - .35 < t < when + .70:
            continue
        if t < when - .15:
            u = (t - (when - .35)) / .20
            return -35.4 * (1 - (1 - u) ** 3)
        if t < when - .10:
            u = (t - (when - .15)) / .05
            return -33.4 - 2 * (1 - u) ** 2
        angle = -33.4 + math.sin(2 * math.pi * (t - (when - .10)) / .20)
        angle -= 6 * ramp(t, [(when, 0), (when + .03, 1), (when + .12, 0)])
        angle += 4 * ramp(t, [(when + .12, 0), (when + .22, 1), (when + .35, 0)])
        u = max(0, (t - (when + .40)) / .30)
        return angle * (1 - u * u * (3 - 2 * u))
    return 0


def positioned(player, px, py, t, rifle=False):
    """Rotate rifle points in source space, then apply the SVG's placement and pose."""
    sx, sy, anchor, bottom, _, _ = geometry()
    x, facing = PLAYERS[player]
    if rifle:
        hx, hy = soldier()['pivot']
        a = math.radians(round(upper(player, t), 1))
        px, py = (hx + (px - hx) * math.cos(a) - (py - hy) * math.sin(a),
                  hy + (px - hx) * math.sin(a) + (py - hy) * math.cos(a))
    xx, yy = x + facing * sx * (px - anchor), GROUND + sy * (py - bottom)
    dx, dy, angle = pose(player, t)
    a = math.radians(angle)
    return (x + (xx - x) * math.cos(a) - (yy - HIP_Y) * math.sin(a) + dx,
            HIP_Y + (xx - x) * math.sin(a) + (yy - HIP_Y) * math.cos(a) + dy)


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
                    for offset in (0, .03, .12, .22, .35, .40, .70, FLIGHT, FLIGHT + .10,
                                   FLIGHT + .28, FLIGHT + .65, FLIGHT + .80,
                                   -.35, -.20, -.15, -.10, -.06, FLIGHT + .06)})
    poses = [(t, pose(player, t)) for t in times]
    x = PLAYERS[player][0]
    hx, hy = soldier()['pivot']
    return (animate('translate', [(t, f'{dx:g} {dy:g}') for t, (dx, dy, _) in poses], True),
            animate('rotate', [(t, f'{a:g} {x} {HIP_Y:g}') for t, (_, _, a) in poses], True),
            animate('rotate', [(t, f'{upper(player, t):.1f} {hx} {hy:g}') for t in times], True))


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
    """36 body and rifle samples scatter, then retrace their paths to respawn."""
    sx, sy, anchor, bottom, _, _ = geometry()
    x, facing = PLAYERS[player]
    body = [(d, rifle) for rifle in (False, True) for d in drawing(rifle)]
    samples = [body[i * len(body) // 36] for i in range(36)]
    points = [(x + facing * sx * (px - anchor), GROUND + sy * (py - bottom))
              for (px, py, _, _), _ in samples]
    staggered = [positioned(player, px, py, death + .10, rifle)
                 for (px, py, _, _), rifle in samples]

    def path(progress, returning=False):
        out = []
        for i, (px, py) in enumerate(points):
            angle = i * 2.4
            vx, vy = math.cos(angle) * (22 + i % 6 * 6), -24 - i % 7 * 5
            # Stable particle order lets one path interpolate all 36 trajectories.
            hit_x, hit_y = staggered[i]
            weight = 0 if returning else 1 - progress
            xx = px + (hit_x - px) * weight + vx * progress
            yy = min(GROUND, py + (hit_y - py) * weight + vy * progress + 100 * progress * progress)
            out.append(f'M{xx:.0f} {yy:.0f}h0')
        return ''.join(out)

    rest, middle, far = path(0), path(.5), path(1)
    start = round(death + .10, 2)
    keys = [(0, rest), (start, rest), (death + .35, middle), (death + .65, far),
            (death + .80, far), (death + .95, path(.5, True)),
            (death + 1.10, path(0, True)), (LOOP, path(0, True))]
    opacity = [(0, 0), (start, 0), (start + .01, 1), (death + .65, 0),
               (death + .80, 0), (death + .95, 1), (death + 1.10, 0), (LOOP, 0)]
    return (f'<path d="{rest}" fill="none" stroke="{c["text"]}" stroke-width="3" '
            f'stroke-linecap="round" opacity="0">{animate("d", keys)}'
            f'{animate("opacity", opacity)}</path>')


def scene(c) -> list[str]:
    """SVG fragments for the stage and score of an 1180 by 300 project cover."""
    sx, sy, anchor, bottom, tip, tip_y = geometry()
    parts = [f'<defs><g id="duel-body">{dots_path(drawing())}</g>'
             f'<g id="duel-rifle">{dots_path(drawing(True))}</g>'
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
        move, turn, aim = track(player)
        place = (f'translate({x} {GROUND}) scale({facing * sx:.4f} {sy:.4f}) '
                 f'translate({-anchor:.2f} {-bottom})')
        flash = schedule('stroke', lambda t: c['text'] if any(
            kill and shooter != player and round(when + FLIGHT, 2) <= t < round(when + FLIGHT + .10, 2)
            for when, shooter, kill in SHOTS) else c['accent'], loop=LOOP)
        visibility = schedule('opacity', lambda t: alive(player, t), loop=LOOP)
        parts.append(f'<ellipse cx="{x}" cy="{GROUND + 1}" rx="39" ry="4" '
                     f'fill="{c["accent"]}" opacity=".12"/>')
        parts.append(f'<g clip-path="url(#duel-floor)"><g>{move}<g>{turn}<g stroke="{c["accent"]}" '
                     f'stroke-linecap="round" fill="none">{flash}'
                     f'<g>{visibility}<g transform="{place}"><use href="#duel-body"/>'
                     f'<g>{aim}<use href="#duel-rifle"/></g></g></g>'
                     '</g></g>' + text(x - facing * 70, 78, f'P{player + 1}', c['muted'], 11, 'middle', 700) + '</g></g>')
    # Magazine particles are drawn before the fences, so they fall behind the mesh.
    for when, shooter, _ in SHOTS:
        x, facing = PLAYERS[shooter]
        start = when + .10
        # The magazine falls from the rifle, just inboard of the tracked muzzle.
        mx, my = positioned(shooter, tip - 12, tip_y + 4, start, rifle=True)
        mx, my = round(mx, 1), round(my, 1)
        drop = [(0, '0 0'), (start, '0 0'), (start + .12, f'{-facing * 4} 12'),
                (start + .30, f'{-facing * 8} {GROUND - my:.1f}'),
                (LOOP, f'{-facing * 8} {GROUND - my:.1f}')]
        parts.append(f'<path class="duel-magazine" d="M{mx} {my}l1 3" '
                     f'stroke="{c["accent"]}" stroke-width="2" opacity="0">'
                     f'{pulse(start, .32)}{animate("translate", drop, True)}</path>')
    # Dissolution stays behind cover, just like the waist and the ducked drawing.
    for when, shooter, kill in SHOTS:
        if kill:
            parts.append('<g clip-path="url(#duel-floor)">' +
                         dissolve(1 - shooter, round(when + FLIGHT, 2), c) + '</g>')
    for player, (x, _) in enumerate(PLAYERS):
        left, right = x - FENCE_HALF, x + FENCE_HALF
        height = GROUND - FENCE_TOP
        parts.append('<g class="duel-fence">')
        for when, shooter, kill in SHOTS:
            if not kill and shooter != player:
                arrival = round(when + FLIGHT, 2)
                parts.append(animate('translate', [(0, '0 0'), (arrival, '0 0'),
                    (arrival + .03, '2 0'), (arrival + .07, '-2 0'),
                    (arrival + .11, '1 0'), (arrival + .15, '0 0'), (LOOP, '0 0')], True))
        parts.append(f'<rect x="{left}" y="{FENCE_TOP}" width="{FENCE_HALF * 2}" height="{height}" '
                     f'fill="{c["bg"]}" fill-opacity=".85"/>')
        mesh = []
        for start in range(-height, FENCE_HALF * 2, 14):
            a, b = max(0, start), min(FENCE_HALF * 2, start + height)
            for direction in (1, -1):
                y = FENCE_TOP if direction == 1 else GROUND
                mesh.append(f'M{left + a} {y + direction * (a - start)}'
                            f'L{left + b} {y + direction * (b - start)}')
        parts.append(f'<path class="duel-mesh" d="{"".join(mesh)}" fill="none" '
                     f'stroke="{c["line"]}" stroke-width=".7"/>')
        for post in (left, x, right):
            parts.append(line(post, FENCE_TOP - 4, post, GROUND, c['line'], 'stroke-width="2"'))
        for rail in (FENCE_TOP, GROUND - 12):
            parts.append(line(left, rail, right, rail, c['line'], 'stroke-width="2"'))
        parts.append(line(left, FENCE_TOP, right, FENCE_TOP, c['accent'],
                          'stroke-width="2" opacity=".4"'))
        parts.append('</g>')
    for when, shooter, kill in SHOTS:
        x, facing = PLAYERS[shooter]
        mx, my = (round(value, 1) for value in positioned(shooter, tip, tip_y, when, rifle=True))
        victim = 1 - shooter
        arrival = round(when + FLIGHT, 2)
        if kill:
            tx, ty = (round(value, 1) for value in positioned(
                victim, anchor, bottom - HEIGHT / sy * .63, arrival))
        else:
            tx, ty = PLAYERS[victim][0] + facing * 5, FENCE_TOP
        rays = ''.join(f'M{mx + math.cos(i * math.pi / 4) * 4:.1f} '
                       f'{my + math.sin(i * math.pi / 4) * 4:.1f}'
                       f'l{math.cos(i * math.pi / 4) * 14:.1f} '
                       f'{math.sin(i * math.pi / 4) * 14:.1f}' for i in range(8))
        parts.append(f'<path d="{rays}" fill="none" stroke="{c["text"]}" '
                     f'stroke-width="2.5" opacity="0">{pulse(when, .08)}</path>')
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
    from cards import CARDS, card
    from xml.etree import ElementTree as ET

    assert len(drawing()) >= 36
    assert .16 <= FLIGHT <= .20
    for (when, _, kill), (next_shot, _, _) in zip(SHOTS, (*SHOTS[1:], (LOOP, 0, False))):
        assert when + FLIGHT + (1.10 if kill else 0) < next_shot, 'Arrival or respawn overlaps next shot'
    for player in range(2):
        assert pose(player, 0) == pose(player, LOOP), 'Idle motion must loop'
        assert upper(player, 0) == upper(player, LOOP) == 0, 'Idle rifles must stay in low ready'
        angles = [upper(player, i / 1000) for i in range(round(LOOP * 1000) + 1)]
        assert max(abs(a - b) for a, b in zip(angles, angles[1:])) < .6, 'Rifle motion must not jump'
        for i in range(round(LOOP / DT) + 1):
            t = round(i * DT, 2)
            assert positioned(player, *soldier()['pivot'], t, rifle=True) == positioned(
                player, *soldier()['pivot'], t), 'The rifle butt must stay at the shoulder'
    for when, shooter, kill in SHOTS:
        assert upper(shooter, when - .35) == 0
        assert abs(upper(shooter, when - .15) + 35.4) < 1e-9, 'Raise must overshoot by two degrees'
        assert abs(upper(shooter, when) + 33.4) < 1e-9, 'Rifle must aim horizontally at the trigger'
        assert upper(shooter, when + .70) == 0, 'Rifle must return to low ready'
        assert pose(shooter, when + .03)[0] == -PLAYERS[shooter][1] * 5
        assert abs(pose(shooter, when + .03)[2]) == 2
        peak = when + .03
        sway = math.sin(2 * math.pi * (peak - (when - .10)) / .20)
        assert abs(upper(shooter, peak) + 33.4 - sway + 6) < 1e-9, 'Rifle recoil must kick upward'
        if kill:
            death = round(when + FLIGHT, 2)
            victim = 1 - shooter
            hit = pose(victim, death + .10)
            assert hit[0] == -PLAYERS[victim][1] * 10
            assert hit[2] == -PLAYERS[victim][1] * 8
            particles = ET.fromstring(dissolve(victim, death, THEMES['dark']))
            px, py = positioned(victim, *drawing()[0][:2], death + .10)
            assert particles.get('d').startswith(f'M{px:.0f} {min(GROUND, py):.0f}h0'), 'Dissolve must start in the staggered pose'
            assert alive(1 - shooter, death + .20) == 0
            assert 0 < alive(1 - shooter, death + .95) < 1
            assert alive(1 - shooter, death + 1.11) == 1
        else:
            assert upper(1 - shooter, when - .20) == 0, 'Lower the rifle before ducking'
            for i in range(7):
                t = when + FLIGHT - .03 + i * .01
                assert all(positioned(1 - shooter, px, py, t, rifle)[1] - r * geometry()[1] > GROUND
                           for rifle in (False, True) for px, py, r, _ in drawing(rifle)), 'Duck must fully hide every particle'
    sx, sy, anchor, bottom, tip, _ = geometry()
    assert sx == sy, 'Soldiers must retain their original proportions'
    assert 210 <= sy * (max(d[1] for d in drawing()) - min(d[1] for d in drawing())) <= 220
    assert tip > anchor, 'The source muzzle must face right'
    px, py = soldier()['pivot']
    mx, my = soldier()['muzzle']
    assert abs(math.degrees(math.atan2(my - py, mx - px)) - 33.4) < .1
    assert PLAYERS[0][0] + sx * (tip - anchor) < PLAYERS[1][0] - sx * (tip - anchor), 'Rifles overlap'
    for x, facing in PLAYERS:
        for px, py, _, _ in drawing() + drawing(True):
            assert 40 <= x + facing * sx * (px - anchor) <= 1140
            assert 56 <= GROUND + sy * (py - bottom) <= GROUND
    for theme_name, theme in THEMES.items():
        content = ''.join(scene(theme))
        root = ET.fromstring(f'<svg>{content}</svg>')
        # Match cards.py's complete FPS card, including its title and SVG wrapper.
        slug, title, tags, _, about = CARDS[1]
        card_size = len(card(theme_name, slug, title, tags, scene, about).encode('utf-8'))
        assert card_size < 80_000, f'Card exceeds 80 KB: {card_size} bytes'
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
        assert len(root.findall('.//use')) == 4
        assert len(root.findall('.//g[@id="duel-body"]')) == 1
        assert len(root.findall('.//g[@id="duel-rifle"]')) == 1
        assert len(root.findall('.//path[@class="duel-magazine"]')) == len(SHOTS)
        placements = [node for node in root.iter('g') if node.find('use[@href="#duel-body"]') is not None]
        for player, (_, facing) in enumerate(PLAYERS):
            placement = placements[player]
            assert f'scale({facing * sx:.4f} {sy:.4f})' in placement.get('transform'), 'Soldiers must face each other'
            rifle = placement.find('g')
            assert rifle.get('transform') is None, 'Static rifles must retain the photo pose'
            assert rifle.find('use').get('href') == '#duel-rifle'
            aim = rifle.find('animateTransform')
            assert all(tuple(map(float, value.split()[1:])) == tuple(soldier()['pivot'])
                       for value in aim.get('values').split(';')), 'Rotate in source units about the shoulder'
            for when, shooter, _ in SHOTS:
                if shooter == player:
                    index = aim.get('keyTimes').split(';').index(f'{when / LOOP:.4f}')
                    assert float(aim.get('values').split(';')[index].split()[0]) == -33.4
        for magazine in root.findall('.//path[@class="duel-magazine"]'):
            assert magazine.get('opacity') == '0'
            assert list(root.find('./g/g')).index(magazine) < next(
                i for i, node in enumerate(root.find('./g/g')) if node.get('class') == 'duel-fence')
        fences = root.findall('.//g[@class="duel-fence"]')
        assert len(fences) == len(PLAYERS)
        for fence, (x, _) in zip(fences, PLAYERS):
            backing = fence.find('rect')
            assert backing.get('fill') == theme['bg'] and backing.get('fill-opacity') == '.85'
            assert float(backing.get('x')) == x - FENCE_HALF
            assert float(backing.get('width')) == 160 and float(backing.get('y')) == FENCE_TOP
            assert float(backing.get('height')) == GROUND - FENCE_TOP
            assert len(fence.findall('line')) == 6
            mesh = fence.find('path[@class="duel-mesh"]')
            assert mesh.get('stroke') == theme['line'] and mesh.get('stroke-width') == '.7'
            assert mesh.get('d').count('M') >= 30
        assert fences[0].find('animateTransform') is None
        shake = fences[1].find('animateTransform')
        assert shake.get('values') == '0 0;0 0;2 0;-2 0;1 0;0 0;0 0'
        shake_keys = [float(t) * LOOP for t in shake.get('keyTimes').split(';')]
        assert abs(shake_keys[1] - SHOTS[0][0] - FLIGHT) < .001
        assert abs(shake_keys[-2] - shake_keys[1] - .15) < .001
        bullets = root.findall('.//g[@class="duel-bullet"]')
        assert len(bullets) == len(SHOTS)
        for bullet, (when, shooter, kill) in zip(bullets, SHOTS):
            assert bullet.get('opacity') == '0', 'Bullets must be hidden without SMIL'
            motion = bullet.find('animateTransform')
            keys = [float(t) for t in motion.get('keyTimes').split(';')]
            assert abs(keys[1] * LOOP - when) < .001
            assert abs(keys[2] * LOOP - when - FLIGHT) < .001
            positions = motion.get('values').split(';')
            assert positions[0] == positions[1] and positions[2] == positions[3]
            muzzle = tuple(round(v, 1) for v in positioned(shooter, *soldier()['muzzle'], when, rifle=True))
            assert tuple(map(float, positions[1].split())) == muzzle, 'Bullet must start at the moving muzzle'
            if kill:
                chest = tuple(round(v, 1) for v in positioned(
                    1 - shooter, anchor, bottom - HEIGHT / sy * .63, round(when + FLIGHT, 2)))
                assert tuple(map(float, positions[2].split())) == chest, 'Bullet must hit the chest'
            if not kill:
                tx, ty = map(float, positions[2].split())
                assert abs(tx - PLAYERS[1 - shooter][0]) < FENCE_HALF and ty == FENCE_TOP
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
        print(f'Duel checks passed: {card_size:,} bytes per card.')
