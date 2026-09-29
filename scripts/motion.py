"""Animated developer-humour banner.

Five original scenes about ordinary programming pain, cross-faded with SMIL.
No JavaScript, no external references, no copyrighted characters: only
monospace text, small windows and geometric faces.
"""
from visuals import THEMES, MONO, text, rect, line, svg

DURATION = 18.0
FADE = 0.45
W, H = 1180, 300
X = 46
CAPTION_Y = 272
ADV = 0.55  # monospace advance width, in em


def animate(attribute, values, key_times, dur=DURATION):
    return (f'<animate attributeName="{attribute}" dur="{dur}s" '
            f'values="{";".join(str(v) for v in values)}" '
            f'keyTimes="{";".join(str(t) for t in key_times)}" '
            'calcMode="linear" repeatCount="indefinite"/>')


def _close_loop(key_times, values, last=0):
    """Append the loop-closing keyframe so the track restarts cleanly."""
    return list(key_times) + [1.0], list(values) + [last]


def fade_track(index, count=None, dur=DURATION, fade=FADE):
    """Opacity keyframes that cross-fade scene `index` into its neighbours.

    The fades of two neighbouring scenes overlap and sum to 1, so the banner
    never blinks through black and the first/last values match across the loop.
    """
    count = count or len(SCENES)
    slot = dur / count
    center = (index + 0.5) * slot
    plateau = slot / 2 - fade

    def value(t):
        distance = abs(((t - center + dur / 2) % dur) - dur / 2)
        if distance <= plateau:
            return 1.0
        if distance >= plateau + 2 * fade:
            return 0.0
        return (plateau + 2 * fade - distance) / (2 * fade)

    edges = (center - plateau - 2 * fade, center - plateau,
             center + plateau, center + plateau + 2 * fade)
    times = {0.0, float(dur)}
    for edge in edges:
        times.add(round(edge % dur, 4))
    ordered = sorted(times)
    return ([round(t / dur, 4) for t in ordered],
            [round(value(t), 4) for t in ordered])


def _cursor(c, x, y):
    return (f'<rect x="{x}" y="{y - 14}" width="11" height="18" fill="{c["accent"]}">'
            '<animate attributeName="opacity" dur="1.2s" values="1;0;1" '
            'keyTimes="0;0.5;1" calcMode="linear" repeatCount="indefinite"/></rect>')


def _face(c, cx, cy, kind):
    colour = c['accent']
    out = [rect(cx - 28, cy - 28, 56, 56, 'none', c['line'], 16)]
    if kind == 'flat':
        out += [
            f'<circle cx="{cx - 11}" cy="{cy - 6}" r="3.2" fill="{colour}"/>',
            f'<circle cx="{cx + 11}" cy="{cy - 6}" r="3.2" fill="{colour}"/>',
            line(cx - 10, cy + 14, cx + 10, cy + 14, colour,
                 'stroke-linecap="round" stroke-width="2.4"'),
        ]
    else:
        out += [
            f'<path d="M {cx - 16} {cy - 12} L {cx - 6} {cy - 2} '
            f'M {cx - 6} {cy - 12} L {cx - 16} {cy - 2}" stroke="{colour}" '
            'stroke-width="2.4" stroke-linecap="round" fill="none"/>',
            f'<path d="M {cx + 6} {cy - 12} L {cx + 16} {cy - 2} '
            f'M {cx + 16} {cy - 12} L {cx + 6} {cy - 2}" stroke="{colour}" '
            'stroke-width="2.4" stroke-linecap="round" fill="none"/>',
            f'<path d="M {cx - 10} {cy + 14} Q {cx - 3} {cy + 7} {cx + 4} {cy + 14} '
            f'Q {cx + 9} {cy + 18} {cx + 12} {cy + 11}" stroke="{colour}" '
            'stroke-width="2.4" stroke-linecap="round" fill="none"/>',
        ]
    return out


def _scene_machine(c, index):
    prompt = '$ git push origin main'
    # textLength pins the command width so the cursor lands in the same place
    # whatever monospace font the renderer picks.
    width = round(len(prompt) * 18 * ADV)
    return [
        text(X, 112, prompt, c['text'], 18,
             extra=f'textLength="{width}" lengthAdjust="spacing"'),
        text(X, 146, 'remote: build passed', c['muted'], 17),
        text(X, 176, 'remote: deploy queued', c['muted'], 17),
        text(X, 234, 'works on my machine', c['accent'], 21, weight=700),
        _cursor(c, X + width + 5, 112),
        *_face(c, 1012, 168, 'flat'),
    ], 'trust me, it works'


def _scene_compile(c, index):
    bar = 520
    start = index * DURATION / len(SCENES)
    key_times, values = _close_loop(
        [0, round((start + 0.3) / DURATION, 4), round((start + 2.4) / DURATION, 4), 0.99],
        [0, 0, bar, bar])
    return [
        text(X, 112, '$ unity build --release', c['text'], 18),
        text(X, 146, 'compiling...', c['muted'], 17),
        rect(X, 160, bar, 10, c['panel'], c['line'], 5),
        f'<rect x="{X}" y="160" width="0" height="10" rx="5" fill="{c["accent"]}">'
        f'{animate("width", values, key_times)}</rect>',
        text(X, 208, 'Build succeeded · 0 errors · 47 warnings', c['text'], 17),
        text(X, 244, 'it was just a small change', c['accent'], 21, weight=700),
    ], 'compiles here, fails in CI'


def _scene_bugs(c, index):
    start = index * DURATION / len(SCENES)
    out = [
        text(X, 112, '$ fix bug #412', c['text'], 18),
        text(X, 146, '- bug #412 closed', c['accent'], 17),
        text(X, 178, '+ bug #413 opened', c['text'], 17),
        text(X, 206, '+ bug #414 opened', c['text'], 17),
        text(X, 234, '+ bug #415 opened', c['text'], 17),
    ]
    for i in range(3):
        appeared = start + 0.7 + i * 0.5
        key_times, values = _close_loop(
            [0, round(appeared / DURATION, 4), round((appeared + 0.4) / DURATION, 4), 0.99],
            [0, 0, 1, 1])
        out.append(
            f'<g opacity="0">{animate("opacity", values, key_times)}'
            f'<rect x="{984 + i * 46}" y="172" width="30" height="30" rx="8" fill="none" '
            f'stroke="{c["accent"]}" stroke-opacity="{round(0.9 - i * 0.22, 2)}"/></g>')
    return out, 'one fixed, three born'


def _scene_null(c, index):
    return [
        text(X, 112, '$ play', c['text'], 18),
        text(X, 148, 'NullReferenceException: Object reference not set', c['text'], 17),
        text(X, 178, 'at PlayerController.Update ()', c['muted'], 16),
        text(X, 204, 'in PlayerController.cs:87', c['muted'], 16),
        text(X, 244, 'it worked ten minutes ago', c['accent'], 21, weight=700),
        *_face(c, 1012, 168, 'dizzy'),
    ], 'the code was fine yesterday'


def _scene_stackoverflow(c, index):
    return [
        text(X, 112, 'search: how to fix a NullReferenceException', c['muted'], 17),
        text(X, 158, 'accepted answer', c['accent'], 20, weight=700),
        text(X, 192, 'copy, paste', c['text'], 17),
        text(X, 244, 'build passed', c['accent'], 21, weight=700),
    ], 'stack overflow, still undefeated'


SCENES = (_scene_machine, _scene_compile, _scene_bugs, _scene_null, _scene_stackoverflow)


def render(theme):
    c = THEMES[theme]
    body = []
    for i in range(3):
        body.append(f'<circle cx="{38 + i * 21}" cy="42" r="5" fill="{c["muted"]}" '
                    f'opacity="{0.35 + i * 0.25}"/>')
    body.append(text(590, 47, 'dev_mood.log', c['muted'], 14, 'middle', 500, 2))
    body.append(line(14, 66, 1166, 66, c['line']))

    for index, builder in enumerate(SCENES):
        elements, caption = builder(c, index)
        inner = ''.join(elements) + text(X, CAPTION_Y, caption, c['accent'], 14,
                                         weight=400, tracking=1.5)
        key_times, values = fade_track(index)
        # The base opacity is only a fallback for renderers that ignore SMIL:
        # they show scene 0 and hide the rest. Browsers always use the
        # animated values, which cross-fade through the whole loop.
        base = 1 if index == 0 else 0
        body.append(f'<g opacity="{base}">'
                    f'{animate("opacity", values, key_times)}{inner}</g>')

    title = ('Animated banner with original programming jokes: it works on my machine, '
             'it was just a small change, one bug becomes three, a NullReferenceException, '
             'and Stack Overflow saving the day.')
    return svg(W, H, theme, title, body, 18, MONO)
