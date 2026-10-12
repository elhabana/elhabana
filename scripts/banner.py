"""Generate an original editor-inspired header and compact project cover."""
from html import escape

from visuals import THEMES, text, rect, line, svg, save
from avatar import scene
from boot import boot, END
from invaders import invaders


CYCLE = 16  # seconds: the live terminal types its commands, holds, clears and starts again
SESSION = (('whoami', (('Cristian Habana', 'text', 700), (' / Game Developer', 'muted', 400))),
           ('ls skills/', (('unity  csharp  netcode  blender  animation  video', 'text', 400),)),
           ('cat focus.txt', (('gameplay systems · multiplayer · game AI', 'text', 400),)),
           ('cat now_building.txt', (('UN-CREDIBLES', 'accent', 700), (' [IN DEVELOPMENT]', 'accent', 400))))

def loop(attribute, full, start, done):
    """Hidden until start, grows to full by done, cleared at the end of each cycle.
    Static renderers keep the base value, so the whole session is readable."""
    k = lambda t: f'{t/CYCLE:.4f}'
    return (f'<animate attributeName="{attribute}" values="0;0;{full};{full};0;0" '
            f'keyTimes="0;{k(start)};{k(done)};{k(CYCLE-.6)};{k(CYCLE-.5)};1" '
            f'dur="{CYCLE}s" begin="{END}s" repeatCount="indefinite"/>')

def terminal(c):
    out,t=[],.5
    for i,(command,result) in enumerate(SESSION):
        y=180+i*90
        width=(len(command)+2)*10+12
        typed=t+len(command)*.06
        out.append(f'<clipPath id="term-c{i}"><rect x="492" y="{y-22}" width="{width}" height="30">{loop("width",width,t,typed)}</rect></clipPath>')
        out.append(f'<text x="494" y="{y}" font-size="18" clip-path="url(#term-c{i})"><tspan fill="{c["accent"]}" font-weight="700">$ </tspan>'
                   f'<tspan fill="{c["text"]}">{escape(command)}</tspan></text>')
        shown=typed+.3
        spans=''.join(f'<tspan fill="{c[colour]}" font-weight="{weight}">{escape(value)}</tspan>' for value,colour,weight in result)
        out.append(f'<text x="494" y="{y+32}" font-size="18" xml:space="preserve">{loop("opacity",1,shown,shown+.01)}{spans}</text>')
        t=shown+.9
    chars=sum(len(value) for value,_,_ in SESSION[-1][1])
    out.append(f'<g>{loop("opacity",1,t-.9,t-.89)}<rect x="{494+chars*10+6}" y="{180+3*90+32-16}" width="10" height="20" fill="{c["accent"]}">'
               '<animate attributeName="opacity" values="1;0" dur="1s" calcMode="discrete" repeatCount="indefinite"/></rect></g>')
    return out

def render(theme):
    c = THEMES[theme]
    b = [rect(14,14,1152,582,c['panel'],c['line'],10)]
    for i in range(3):
        b.append(f'<circle cx="{38+i*21}" cy="38" r="5" fill="{c["muted"]}" opacity="{.4+i*.25}"/>')
    b += [text(590,44,'elhabana // interactive systems',c['text'],16,'middle'),line(14,64,1166,64,c['line'])]
    # CRT power-on: the panels expand from a centre line once the boot screen is gone.
    b += ['<g transform="translate(0 330)"><g>',
          f'<animateTransform attributeName="transform" type="scale" values="1 .004;1 .004;1 1" '
          f'keyTimes="0;{END/(END+.45):.3f};1" dur="{END+.45:.2f}s" fill="freeze"/>',
          '<g transform="translate(0 -330)">']
    b += [rect(34,88,418,468,c['bg'],c['line'],5),rect(474,88,672,468,c['bg'],c['line'],5)]
    b += [text(50,114,'SYSTEM.VIEW',c['accent'],15,weight=700),line(34,130,452,130,c['line'])]
    b += [text(492,114,'DEVELOPER.PROFILE',c['accent'],15,weight=700),text(1127,114,'@elhabana',c['text'],15,'end'),line(474,130,1146,130,c['line'])]
    b += scene(c)
    b += terminal(c)
    b += ['</g></g></g>',text(1146,581,'CODE / CREATE / ITERATE',c['muted'],12,'end')]
    b += boot(c)
    b += invaders(c)
    return svg(1180,610,theme,'elhabana: Unity and C# game developer; gameplay, multiplayer, 3D and audiovisual',b)

def project(theme):
    c=THEMES[theme]
    b=[text(32,38,'SELECTED WORK / 01',c['muted'],14),text(1148,38,'IN DEVELOPMENT',c['accent'],14,'end',700)[:-7]+'<animate attributeName="opacity" values="1;.25" dur="1.6s" calcMode="discrete" repeatCount="indefinite"/></text>',line(32,56,1148,56,c['line']),
       f'<rect x="32" y="55" width="160" height="2" fill="{c["accent"]}"><animate attributeName="x" values="32;988;32" dur="4s" calcMode="linear" repeatCount="indefinite"/></rect>',text(32,128,'UN-CREDIBLES',c['text'],52,weight=700),text(34,168,'Multiplayer superhero party game',c['muted'],20)]
    for i in range(4):
        x=904+i*61
        b += [rect(x,92,44,58,c['panel'],c['line'],5),text(x+22,130,f'P{i+1}',c['accent'],17,'middle')]
    return svg(1180,210,theme,'UN-CREDIBLES: multiplayer superhero party game, in development',b)

if __name__=='__main__':
    for theme in THEMES:
        save(f'banner-{theme}.svg',render(theme))
        save(f'uncredibles-{theme}.svg',project(theme))
