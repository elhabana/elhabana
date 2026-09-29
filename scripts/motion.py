"""Procedural particle morphs for the profile SVG; no JavaScript or libraries."""
import math
import random

DURATION = 18
TIMES = [0, .16, .24, .34, .50, .60, .76, .86, 1]

def animate(attribute, values, times=TIMES, mode='linear'):
    return (f'<animate attributeName="{attribute}" dur="{DURATION}s" '
            f'values="{";".join(str(v) for v in values)}" '
            f'keyTimes="{";".join(str(t) for t in times)}" '
            f'calcMode="{mode}" repeatCount="indefinite"/>')

def project(point, angle, expand=1):
    x,y,z = [v*expand for v in point]
    xx=x*math.cos(angle)-z*math.sin(angle)
    zz=x*math.sin(angle)+z*math.cos(angle)
    return 244+xx, 308+y*.86+zz*.38

def particle_frames(count=720):
    rng=random.Random(72)
    frames=[[] for _ in TIMES]
    nodes=[(244,213),(344,269),(344,385),(244,435),(144,385),(144,269)]
    for i in range(count):
        # Sample the surfaces of a cube, not a random cloud.
        p=[rng.uniform(-79,79) for _ in range(3)]
        p[i%3]=79 if i%2 else -79
        a=i*math.tau/120
        node=nodes[i%6]
        radius=18+5*math.sin(a*3)
        graph=(node[0]+math.cos(a)*radius,node[1]+math.sin(a)*radius)
        column=i%90
        x=82+column*3.65
        envelope=17+58*(.5+.5*math.sin(column*.13))
        y=315+((i//90)/7*2-1)*envelope*math.sin(column*.51)
        wave=(x,y)
        wave2=(x,315+(y-315)*(.6+.4*math.cos(column*.19)))
        positions=[project(p,.55),project(p,1.4),project(p,1.7,1.17),graph,graph,wave,wave2,project(p,-.2),project(p,.55)]
        for frame,point in zip(frames,positions): frame.append(tuple(round(v,2) for v in point))
    return frames

def scene(c):
    frames=particle_frames()
    parts=['<defs><clipPath id="scene-clip"><rect x="49" y="144" width="389" height="367"/></clipPath></defs>',
           '<g clip-path="url(#scene-clip)">']
    # A visible network scaffold fades in only during the systems phase.
    parts.append('<g opacity="0">'+animate('opacity',[0,0,0,1,1,0,0,0,0]))
    nodes=[(244,213),(344,269),(344,385),(244,435),(144,385),(144,269)]
    for x,y in nodes:
        parts.append(f'<path d="M244 320 {x} {y}" fill="none" stroke="{c["muted"]}" stroke-dasharray="3 6"/>')
    parts.append(f'<path d="M244 213 344 269 344 385 244 435 144 385 144 269Z" fill="none" stroke="{c["line"]}"/>')
    parts.append(f'<circle cx="244" cy="320" r="26" fill="{c["panel"]}" stroke="{c["accent"]}"/>')
    parts.append(f'<text x="244" y="325" text-anchor="middle" font-size="12" fill="{c["text"]}">CORE</text></g>')
    for i,(x,y) in enumerate(frames[0]):
        parts.append(f'<circle cx="{x}" cy="{y}" r="{1.15 if i%4 else 1.7}" fill="{c["accent"]}" opacity="{.55+(i%4)*.15}">'
                     +animate('cx',[frame[i][0] for frame in frames])
                     +animate('cy',[frame[i][1] for frame in frames])+'</circle>')
    # Audiovisual timeline and a moving playhead: conceptual graphics, not audio data.
    parts.append('<g opacity="0">'+animate('opacity',[0,0,0,0,0,1,1,0,0]))
    for y in [408,435,462]:
        parts.append(f'<rect x="82" y="{y}" width="325" height="16" rx="3" fill="{c["panel"]}" stroke="{c["line"]}"/>')
    for x,y,w in [(90,412,92),(190,412,137),(90,439,170),(267,439,125),(126,466,201)]:
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="8" rx="2" fill="{c["accent"]}" opacity=".4"/>')
    parts.append(f'<rect x="82" y="280" width="1.5" height="204" fill="{c["text"]}">'
                 +animate('x',[82,82,82,82,82,82,407,407,82])+'</rect></g></g>')
    for i,label in enumerate(['01 / SCENE GEOMETRY','02 / GAMEPLAY NETWORK','03 / AUDIOVISUAL']):
        values=([1,0,0,1,1],[0,1,0,0,0],[0,0,1,0,0])[i]
        parts.append(f'<g opacity="{values[0]}">'+animate('opacity',values,[0,.28,.56,.84,1],'discrete')
                     +f'<text x="54" y="538" fill="{c["accent"]}" font-size="14">{label}</text></g>')
    return parts
