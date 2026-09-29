"""Generate an original editor-inspired header and compact project cover."""
import math
from visuals import THEMES, text, rect, line, svg, save
from motion import scene, animate

def render(theme):
    c = THEMES[theme]
    b = [rect(14,14,1152,582,c['panel'],c['line'],10)]
    for i in range(3):
        b.append(f'<circle cx="{38+i*21}" cy="38" r="5" fill="{c["muted"]}" opacity="{.4+i*.25}"/>')
    b += [text(590,44,'elhabana // interactive systems',c['text'],16,'middle'),line(14,64,1166,64,c['line'])]
    b += [rect(34,88,418,468,c['bg'],c['line'],5),rect(474,88,672,468,c['bg'],c['line'],5)]
    b += [text(50,114,'SYSTEM.VIEW',c['accent'],15,weight=700),text(434,114,'MOTION STUDY',c['muted'],12,'end'),line(34,130,452,130,c['line'])]
    b += [text(492,114,'DEVELOPER.PROFILE',c['accent'],15,weight=700),text(1127,114,'@elhabana',c['text'],15,'end'),line(474,130,1146,130,c['line'])]
    # Perspective construction grid and an isometric wireframe system core.
    for i in range(9):
        b.append(line(55+i*47,487,244,298,c['line'],'opacity=".6"'))
    for y in [365,384,410,444,487]:
        b.append(line(54,y,432,y,c['line'],'opacity=".6"'))
    b += scene(c)
    b.append(f'<rect x="484" y="200" width="652" height="27" rx="3" fill="{c["accent"]}" opacity=".07">'
             +animate('y',[200,200,256,256,256,424,424,200,200])+'</rect>')
    rows = [('Name','Cristian Habana'),('Role','Game Developer / Digital Creator'),('Engine','Unity'),('Language','C#'),('Focus','Gameplay / Game Systems'),('Architecture','Reusable / Modular'),('Multiplayer','Local / Online'),('AI','Game AI / Player Systems'),('3D','Blender / Animation'),('Visual','Photoshop'),('Video','DaVinci Resolve / CapCut'),('Building','UN-CREDIBLES')]
    for i,(label,value) in enumerate(rows):
        y=163+i*28
        b += [text(494,y,label,c['muted'],15),text(1126,y,value,c['text'],15,'end')]
        start=494+len(label)*9+12
        end=1126-len(value)*9-12
        if end>start: b.append(line(start,y-5,end,y-5,c['line'],'stroke-dasharray="1 5"'))
    b += [line(494,513,1126,513,c['line']),text(494,539,'CURRENT BUILD // IN DEVELOPMENT',c['accent'],13)]
    b.append(f'<rect x="494" y="513" width="0" height="1" fill="{c["accent"]}">'
             +animate('width',[0,632],[0,1])+'</rect>')
    b += [text(34,581,'UNITY + C#',c['muted'],12),text(1146,581,'CODE / CREATE / ITERATE',c['muted'],12,'end')]
    return svg(1180,610,theme,'elhabana: Unity and C# game developer; gameplay, 3D, animation and audiovisual systems',b)

def project(theme):
    c=THEMES[theme]
    b=[text(32,38,'SELECTED WORK / 01',c['muted'],14),text(1148,38,'IN DEVELOPMENT',c['accent'],14,'end'),line(32,56,1148,56,c['line']),text(32,128,'UN-CREDIBLES',c['text'],52,weight=700),text(34,168,'Multiplayer superhero party game',c['muted'],20)]
    for i in range(4):
        x=904+i*61
        b += [rect(x,92,44,58,c['panel'],c['line'],5),text(x+22,130,f'P{i+1}',c['accent'],17,'middle')]
    return svg(1180,210,theme,'UN-CREDIBLES: multiplayer superhero party game, in development',b)

if __name__=='__main__':
    for theme in THEMES:
        save(f'banner-{theme}.svg',render(theme))
        save(f'uncredibles-{theme}.svg',project(theme))
