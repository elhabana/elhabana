"""One-shot terminal boot sequence that wipes away to reveal SYSTEM.VIEW."""
from visuals import line, rect, text

MODULES = ('unity', 'csharp', 'netcode', 'blender', 'photoshop', 'davinci-resolve')
WIPE = 6.6    # seconds: the boot screen starts collapsing
END = 7.4     # seconds: the banner underneath is fully revealed
SHAPE = 'M14 65 H1166 V586 Q1166 596 1156 596 H24 Q14 596 14 586 Z'


def show(begin):
    return f'<set attributeName="opacity" to="1" begin="{begin}s" fill="freeze"/>'

def typed(i, x, y, width, begin, body):
    """Reveal a line left to right, like it is being typed."""
    return (f'<clipPath id="boot-l{i}"><rect x="{x-2}" y="{y-20}" width="0" height="28">'
            f'<animate attributeName="width" from="0" to="{width}" begin="{begin}s" dur=".35s" fill="freeze"/>'
            f'</rect></clipPath><g clip-path="url(#boot-l{i})">{body}</g>')

def boot(c):
    """The overlay is hidden by default, so static renderers show the banner."""
    p = [f'<clipPath id="boot-wipe"><rect x="0" y="65" width="1180" height="531">'
         f'<animate attributeName="y" values="65;596" begin="{WIPE}s" dur="{END-WIPE:.1f}s" fill="freeze"/>'
         '</rect></clipPath>',
         '<g opacity="0">',
         f'<animate attributeName="opacity" values="1;1;0" keyTimes="0;.99;1" dur="{END}s" fill="freeze"/>',
         f'<g clip-path="url(#boot-wipe)"><path d="{SHAPE}" fill="{c["panel"]}"/>',
         text(1146, 96, 'BOOT // elhabana.sys', c['muted'], 12, 'end')]
    rows = [(.3, 110, [text(60, 110, '> booting elhabana.sys ...', c['text'], 16)], 260)]
    for i, name in enumerate(MODULES):
        y = 150 + i * 30
        rows.append((.9 + i * .45, y, [text(60, y, f'> loading module: {name}', c['muted'], 16),
                                    line(60 + (18 + len(name)) * 9 + 14, y - 5, 560, y - 5, c['line'], 'stroke-dasharray="1 5"')], 520))
        p.append(f'<g opacity="0">{text(574, y, "[OK]", c["accent"], 16, weight=700)}{show(1.25 + i * .45)}</g>')
    rows += [(3.8, 340, [text(60, 340, '> mounting project: UN-CREDIBLES', c['text'], 16)], 340),
             (4.3, 370, [text(84, 370, 'status: IN DEVELOPMENT', c['accent'], 16, weight=700)], 230),
             (4.9, 414, [text(60, 414, '> ACCESS GRANTED', c['accent'], 20, weight=700)], 210)]
    for i, (begin, y, body, width) in enumerate(rows):
        p.append(typed(i, 60, y, width, begin, ''.join(body)))
    p += [f'<g opacity="0">{show(5.4)}',
          text(60, 482, 'Cristian Habana', c['text'], 36, weight=700),
          text(62, 516, 'Game Developer · Unity / C#', c['muted'], 18),
          f'<rect x="340" y="501" width="11" height="19" fill="{c["accent"]}">'
          '<animate attributeName="opacity" values="1;0" dur="1s" calcMode="discrete" repeatCount="indefinite"/></rect>',
          '</g>',
          rect(60, 556, 1060, 6, c['bg'], c['line'], 3),
          f'<rect x="60" y="556" width="0" height="6" rx="3" fill="{c["accent"]}">'
          '<animate attributeName="width" from="0" to="1060" begin=".3s" dur="4.6s" fill="freeze"/></rect>',
          text(1120, 584, 'LOADING PROFILE', c['muted'], 12, 'end'),
          '</g>',
          f'<rect x="14" y="64" width="1152" height="2" fill="{c["accent"]}" opacity="0">'
          f'<set attributeName="opacity" to="1" begin="{WIPE}s"/>'
          f'<animate attributeName="y" values="64;595" begin="{WIPE}s" dur="{END-WIPE:.1f}s" fill="freeze"/></rect>',
          '</g>']
    return p
