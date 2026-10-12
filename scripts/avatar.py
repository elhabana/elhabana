"""Turn the supplied avatar poses into a particle bust for the profile SVG."""
import math
import random
import struct
import zlib
from functools import lru_cache

from boot import END
from visuals import ASSETS, line, rect, text

FRAMES = ('neutral', 'blink', 'talk', 'blink-talk')
TIMES = (0, .20, .21, .34, .44, .45, .52, .54, .62, .73, .74, .88, .89, 1)
STATES = ('neutral', 'blink', 'neutral', 'talk', 'neutral', 'blink-talk',
          'talk', 'neutral', 'neutral', 'talk', 'neutral', 'blink',
          'neutral', 'neutral')

CROP = (98, 0, 338, 240)      # source pixels: head and shoulders
BOX = (68, 145, 355)          # where the bust is drawn: x, y, size
FACE = (218, 102, 62, 40)     # source ellipse: centre x, centre y, radius x, radius y
FINE, COARSE = 1.7, 3.2       # particle spacing in source pixels, face vs. the rest
SWARMS = 36                   # particles fly in as this many independent swarms
EASE = .003                   # fraction of the 18 s loop an eye change takes
FLAP = .16                    # seconds: one open-and-close of the mouth while reading


def read_png(path):
    """Decode an 8-bit RGBA, non-interlaced PNG into rows of (r, g, b, a)."""
    data, pos, idat = path.read_bytes(), 8, b''
    while pos < len(data):
        size, kind = struct.unpack('>I4s', data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + size]
        pos += 12 + size
        if kind == b'IHDR':
            width, height, depth, colour, _, _, interlace = struct.unpack('>IIBBBBB', body)
            assert (depth, colour, interlace) == (8, 6, 0), f'{path.name}: expected 8-bit RGBA'
        elif kind == b'IDAT':
            idat += body
    raw, stride = zlib.decompress(idat), width * 4
    prev, rows, i = bytearray(stride), [], 0
    for _ in range(height):
        kind, row = raw[i], bytearray(raw[i + 1:i + 1 + stride])
        i += 1 + stride
        for x in range(stride):
            a = row[x - 4] if x >= 4 else 0
            b = prev[x]
            c = prev[x - 4] if x >= 4 else 0
            if kind == 1:
                row[x] = (row[x] + a) & 255
            elif kind == 2:
                row[x] = (row[x] + b) & 255
            elif kind == 3:
                row[x] = (row[x] + (a + b) // 2) & 255
            elif kind == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                row[x] = (row[x] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        rows.append([tuple(row[k:k + 4]) for k in range(0, stride, 4)])
        prev = row
    return rows

def in_face(x, y):
    return math.hypot((x - FACE[0]) / FACE[2], (y - FACE[1]) / FACE[3]) < 1

def spacing(x, y):
    """Dense around the face so eyes and mouth read clearly, sparser outwards."""
    d = math.hypot((x - FACE[0]) / FACE[2], (y - FACE[1]) / FACE[3])
    return FINE + (COARSE - FINE) * min(1, max(0, d - .7))

def points():
    """Fixed seed: the same particle positions on every run and for every pose."""
    rnd, y = random.Random(7), CROP[1]
    while y < CROP[3]:
        x = CROP[0]
        while x < CROP[2]:
            s = spacing(x, y)
            if rnd.random() < (FINE / s) ** 2:
                jitter = .12 if s < FINE * 1.3 else .35
                yield x + rnd.uniform(-jitter, jitter) * s, y + rnd.uniform(-jitter, jitter) * s, s
            x += FINE
        y += FINE

def sample(img, x, y, s):
    """Alpha coverage and brightness (0..1) around a particle."""
    half, cover, light, n = max(1, round(s / 2)), 0, 0, 0
    for j in range(int(y) - half + 1, int(y) + half):
        for i in range(int(x) - half + 1, int(x) + half):
            if 0 <= i < len(img[0]) and 0 <= j < len(img):
                r, g, b, a = img[j][i]
                cover += a
                light += a * (.299 * r + .587 * g + .114 * b)
                n += 1
    return cover / (max(n, 1) * 255), (light / cover / 255 if cover else 0)

@lru_cache(maxsize=None)
def particles(invert):
    """[(x, y, {frame: (radius, opacity)})] in banner coordinates."""
    poses = {frame: read_png(ASSETS / 'avatar' / f'{frame}.png') for frame in FRAMES}
    scale, out = BOX[2] / (CROP[2] - CROP[0]), []
    for x, y, s in points():
        looks = {}
        for frame, img in poses.items():
            cover, light = sample(img, x, y, s)
            if cover > .3:
                level = min(1, max(0, (light - .08) / .8)) ** .9
                level = 1 - level if invert else level
                looks[frame] = (round(s * (.14 + .40 * level) * scale, 1), round(.3 + .7 * level, 2))
            else:
                looks[frame] = (0, 0)
        if any(r for r, _ in looks.values()):
            # Only clear changes inside the face animate; the poses are not pixel-identical,
            # so small differences anywhere else are noise.
            base = looks['neutral']
            looks = {frame: look if in_face(x, y) and (abs(look[0] - base[0]) >= .4 or abs(look[1] - base[1]) >= .3)
                     else base for frame, look in looks.items()}
            out.append((round(BOX[0] + (x - CROP[0]) * scale, 1), round(BOX[1] + (y - CROP[1]) * scale, 1), looks))
    return out

def timeline(looks, index):
    """Hold each pose and change quickly, so the mouth and eyes snap but do not pop."""
    points = [(0, looks[STATES[0]][index])]
    for i in range(1, len(STATES)):
        if STATES[i] != STATES[i - 1]:
            points += [(TIMES[i], looks[STATES[i - 1]][index]), (round(TIMES[i] + EASE, 3), looks[STATES[i]][index])]
    points.append((1, looks[STATES[-1]][index]))
    return (';'.join(str(v) for _, v in points), ';'.join(str(t) for t, _ in points))

def reading(looks, index, speech):
    """Flap the mouth while the terminal types; closed the rest of the cycle."""
    _, cycle, spans = speech
    closed, open_ = looks['neutral'][index], looks['talk'][index]
    points = [(0, closed)]
    for start, end in spans:
        t, opened = start, True
        while t < end - 1e-6:
            points.append((t, open_ if opened else closed))
            t, opened = t + FLAP / 2, not opened
        points.append((end, closed))
    keys, values = [], []
    for t, v in points:
        k = round(t / cycle, 4)
        if keys and k <= keys[-1]:
            continue
        keys.append(k)
        values.append(v)
    return ';'.join(map(str, values)), ';'.join(map(str, keys))

def dot(x, y, looks, speech):
    r, o = looks['neutral']
    if looks['talk'] != looks['neutral']:
        # mouth: reads along with the live terminal
        begin, cycle, _ = speech
        anims = ''.join(f'<animate attributeName="{attribute}" values="{values}" keyTimes="{times}" '
                        f'dur="{cycle}s" begin="{begin}s" calcMode="discrete" repeatCount="indefinite"/>'
                        for index, attribute in enumerate(('r', 'fill-opacity'))
                        for values, times in [reading(looks, index, speech)])
    elif looks['blink'] != looks['neutral']:
        # eyes: keep blinking on their own 18-second loop
        eyes = {frame: looks['blink'] if 'blink' in frame else looks['neutral'] for frame in FRAMES}
        anims = ''.join(f'<animate attributeName="{attribute}" dur="18s" values="{values}" '
                        f'keyTimes="{times}" repeatCount="indefinite"/>'
                        for index, attribute in enumerate(('r', 'fill-opacity'))
                        for values, times in [timeline(eyes, index)])
    else:
        return f'<circle cx="{x}" cy="{y}" r="{r}" fill-opacity="{o}"/>'
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill-opacity="{o}">{anims}</circle>'

def swarm(i, rnd):
    """Each swarm flies in from its own direction once the banner powers on."""
    angle, distance = rnd.uniform(0, 2 * math.pi), rnd.uniform(140, 320)
    dx, dy = round(math.cos(angle) * distance), round(math.sin(angle) * distance)
    begin = END + .3 + rnd.uniform(0, .7)
    dur = begin + rnd.uniform(.7, 1.1)
    k = f'{begin / dur:.3f}'
    return (f'<g><animateTransform attributeName="transform" type="translate" values="{dx} {dy};{dx} {dy};0 0" '
            f'keyTimes="0;{k};1" dur="{dur:.2f}s" fill="freeze"/>'
            f'<animate attributeName="opacity" values="0;0;1" keyTimes="0;{k};1" dur="{dur:.2f}s" fill="freeze"/>')

def bust(c, speech):
    invert = int(c['bg'][1:3], 16) > 128
    rnd = random.Random(11)
    groups = [[] for _ in range(SWARMS)]
    for x, y, looks in particles(invert):
        groups[rnd.randrange(SWARMS)].append(dot(x, y, looks, speech))
    parts = [f'<g fill="{c["accent"]}">']
    for i, dots in enumerate(groups):
        parts.append(swarm(i, rnd))
        if i % 6 == 0:  # a few swarms keep shimmering so the bust feels alive
            parts.append(f'<g><animate attributeName="opacity" values="1;.45;1" dur="{rnd.uniform(2.5, 4.5):.1f}s" '
                         'repeatCount="indefinite"/>' + ''.join(dots) + '</g>')
        else:
            parts.append(''.join(dots))
        parts.append('</g>')
    return parts + ['</g>']

def scene(c, speech):
    """Static renderers show the neutral pose fully assembled; SMIL adds the motion."""
    parts = [
        '<defs><clipPath id="avatar-clip"><rect x="49" y="144" width="389" height="367" rx="4"/></clipPath></defs>',
        rect(49, 144, 389, 367, c['panel'], c['line'], 4),
        f'<circle cx="244" cy="329" r="148" fill="none" stroke="{c["line"]}"/>',
        f'<circle cx="244" cy="329" r="111" fill="none" stroke="{c["accent"]}" stroke-dasharray="3 8" opacity=".55">'
        '<animateTransform attributeName="transform" type="rotate" from="0 244 329" to="360 244 329" '
        'dur="30s" repeatCount="indefinite"/></circle>',
        line(244, 150, 244, 500, c['line'], 'opacity=".45"'),
        line(55, 329, 432, 329, c['line'], 'opacity=".45"'),
        '<g clip-path="url(#avatar-clip)">',
    ]
    parts += bust(c, speech)
    parts += [
        f'<rect x="49" y="144" width="389" height="2" fill="{c["accent"]}" opacity=".45">'
        '<animate attributeName="y" values="144;509;144" dur="6s" calcMode="linear" repeatCount="indefinite"/></rect>',
        '</g>',
        rect(53, 518, 135, 25, c['panel'], c['line'], 3),
        text(63, 535, 'X_X // AVATAR', c['accent'], 12, weight=700),
        f'<circle cx="378" cy="531" r="4" fill="{c["accent"]}">'
        '<animate attributeName="opacity" values="1;.2;1" dur="1.6s" calcMode="linear" repeatCount="indefinite"/></circle>',
        text(432, 535, 'ONLINE', c['muted'], 12, 'end'),
    ]
    return parts
