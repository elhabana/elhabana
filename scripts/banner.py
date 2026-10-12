"""Generate an original editor-inspired header and compact project cover."""
import random
from html import escape

from visuals import THEMES, text, rect, line, svg, save
from avatar import scene
from boot import boot, END
from invaders import invaders
from heroes import brawl


CYCLE = 10  # seconds: the live terminal types, decrypts, holds, clears and starts again
FRAME = .05 # seconds per decryption frame
LEAD = 4    # frames of pure noise before the first letter locks in
NOISE = '#$%&@!?*<>/=+0123456789ABCDEFX'
SESSION = (('whoami', (('Cristian Habana', 'text', 700), (' / Game Developer', 'muted', 400))),
           ('cat now_building.txt', (('UN-CREDIBLES', 'accent', 700), (' [IN DEVELOPMENT]', 'accent', 400))))
ROW = lambda i: 214+i*124   # y of each command; its output goes 40 below

def loop(attribute, full, start, done):
    """Hidden until start, grows to full by done, cleared at the end of each cycle.
    Static renderers keep the base value, so the whole session is readable."""
    k = lambda t: f'{t/CYCLE:.4f}'
    return (f'<animate attributeName="{attribute}" values="0;0;{full};{full};0;0" '
            f'keyTimes="0;{k(start)};{k(done)};{k(CYCLE-.6)};{k(CYCLE-.5)};1" '
            f'dur="{CYCLE}s" begin="{END}s" repeatCount="indefinite"/>')

def window(start, end):
    """Visible only between start and end of each cycle (discrete)."""
    k = lambda t: f'{t/CYCLE:.4f}'
    return (f'<animate attributeName="opacity" values="0;1;0" keyTimes="0;{k(start)};{k(end)}" '
            f'dur="{CYCLE}s" begin="{END}s" calcMode="discrete" repeatCount="indefinite"/>')

def script():
    """When each command is typed and each output decrypted: [(i, start, end, start, end)].
    The avatar reads along, so its mouth uses the same timings."""
    out,t=[],.5
    for i,(command,result) in enumerate(SESSION):
        typed=t+len(command)*.06
        shown=typed+.25
        read=shown+(LEAD+sum(len(value) for value,_,_ in result))*FRAME
        out.append((i,t,typed,shown,read))
        t=read+.7
    assert out[-1][4]<CYCLE-.8, 'the session does not fit in one cycle'
    return out

def speech():
    """Typing stretches for the avatar's mouth: (begin, cycle, [(start, end)])."""
    return END,CYCLE,[span for _,a,b,c,d in script() for span in ((a,b),(c,d))]

def decrypt(c, i, y, result, shown, read):
    """Noise that locks into the real text one letter at a time, then the real text."""
    rnd=random.Random(i)
    plain=''.join(value for value,_,_ in result)
    frames=[]
    for f in range(LEAD+len(plain)):
        locked=max(0,f-LEAD+1)
        noise=''.join(ch if ch==' ' else rnd.choice(NOISE) for ch in plain[locked:])
        t=shown+f*FRAME
        frames.append(f'<text x="494" y="{y}" font-size="20" xml:space="preserve" opacity="0">{window(t,t+FRAME)}'
                      f'<tspan fill="{c["text"]}">{escape(plain[:locked])}</tspan>'
                      f'<tspan fill="{c["accent"]}" fill-opacity=".6">{escape(noise)}</tspan></text>')
    spans=''.join(f'<tspan fill="{c[colour]}" font-weight="{weight}">{escape(value)}</tspan>' for value,colour,weight in result)
    frames.append(f'<text x="494" y="{y}" font-size="20" xml:space="preserve">{window(read,CYCLE-.5)}{spans}</text>')
    return frames

def terminal(c):
    out=[]
    for i,start,typed,shown,read in script():
        command,result=SESSION[i]
        y=ROW(i)
        width=(len(command)+2)*11+12
        out.append(f'<clipPath id="term-c{i}"><rect x="492" y="{y-24}" width="{width}" height="32">{loop("width",width,start,typed)}</rect></clipPath>')
        out.append(f'<text x="494" y="{y}" font-size="20" clip-path="url(#term-c{i})"><tspan fill="{c["accent"]}" font-weight="700">$ </tspan>'
                   f'<tspan fill="{c["text"]}">{escape(command)}</tspan></text>')
        out+=decrypt(c,i,y+40,result,shown,read)
    i,_,_,_,read=script()[-1]
    chars=sum(len(value) for value,_,_ in SESSION[-1][1])
    out.append(f'<g>{window(read,CYCLE-.5)}<rect x="{494+chars*11+8}" y="{ROW(i)+40-18}" width="11" height="22" fill="{c["accent"]}">'
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
    b += scene(c,speech())
    b += terminal(c)
    b += ['</g></g></g>',text(1146,581,'CODE / CREATE / ITERATE',c['muted'],12,'end')]
    b += boot(c)
    b += invaders(c)
    return svg(1180,610,theme,'elhabana: Unity and C# game developer; gameplay, multiplayer, 3D and audiovisual',b)

def project(theme):
    c=THEMES[theme]
    b=[text(32,40,'UN-CREDIBLES',c['text'],18,weight=700),
       text(1148,40,'IN DEVELOPMENT',c['accent'],13,'end',700)[:-7]+'<animate attributeName="opacity" values="1;.25" dur="1.6s" calcMode="discrete" repeatCount="indefinite"/></text>']
    b+=brawl(c)
    return svg(1180,300,theme,'UN-CREDIBLES: four particle heroes brawling; multiplayer superhero party game, in development',b)

if __name__=='__main__':
    for theme in THEMES:
        save(f'banner-{theme}.svg',render(theme))
        save(f'uncredibles-{theme}.svg',project(theme))
