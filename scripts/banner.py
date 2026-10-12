"""Generate an original editor-inspired header and compact project cover."""
from visuals import THEMES, text, rect, line, svg, save
from avatar import scene
from boot import boot, END


def animate(attribute, values, times=(0, .16, .24, .34, .50, .60, .76, .86, 1)):
    return (f'<animate attributeName="{attribute}" dur="18s" '
            f'values="{";".join(str(v) for v in values)}" '
            f'keyTimes="{";".join(str(t) for t in times)}" '
            'calcMode="linear" repeatCount="indefinite"/>')

def reveal(i):
    """Fade a row in right after the boot screen; static renderers keep it visible."""
    begin=END+.12*i
    return (f'<animate attributeName="opacity" values="0;0;1" keyTimes="0;{begin/(begin+.4):.3f};1" '
            f'dur="{begin+.4:.2f}s" fill="freeze"/>')

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
    rows = [('Name','Cristian Habana'),('Role','Game Developer'),('Stack','Unity · C# · Netcode'),('Focus','Gameplay & Multiplayer'),('Create','3D · Animation · Video'),('Building','UN-CREDIBLES')]
    ys=[178+i*54 for i in range(len(rows))]
    hold=[y-22 for y in ys]
    b.append(f'<rect x="484" y="{hold[0]}" width="652" height="32" rx="3" fill="{c["accent"]}" opacity=".08">'
             +animate('y',hold+[hold[0]],[round(i/len(rows),3) for i in range(len(rows))]+[1]).replace('linear','discrete')+'</rect>')
    for i,((label,value),y) in enumerate(zip(rows,ys)):
        b.append(f'<g>{reveal(i)}')
        b += [text(494,y,label.upper(),c['muted'],13,weight=700),text(1126,y,value,c['text'],18,'end',700 if i in (0,5) else 400)]
        start=494+len(label)*9+14
        end=1126-len(value)*10-14
        if end>start: b.append(line(start,y-5,end,y-5,c['line'],'stroke-dasharray="1 5"'))
        b.append('</g>')
    b.append(f'<rect x="1131" y="{ys[-1]-15}" width="9" height="18" fill="{c["accent"]}">'
             '<animate attributeName="opacity" values="1;0" dur="1s" calcMode="discrete" repeatCount="indefinite"/></rect>')
    b += [line(494,513,1126,513,c['line']),text(494,539,'CURRENT BUILD // IN DEVELOPMENT',c['accent'],13,weight=700)]
    b.append(f'<rect x="494" y="512" width="140" height="3" fill="{c["accent"]}">'
             '<animate attributeName="x" values="494;986;494" dur="4s" calcMode="linear" repeatCount="indefinite"/></rect>')
    b += ['</g></g></g>',text(1146,581,'CODE / CREATE / ITERATE',c['muted'],12,'end')]
    b += boot(c)
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
