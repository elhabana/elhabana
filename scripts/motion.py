"""Morph original meme contours into SVG particles; standard library only."""
import bisect
import json
import math
from pathlib import Path
import random
import re

DURATION = 18
TIMES = [0, .16, .24, .34, .50, .60, .76, .86, 1]
COUNT = 1200
SOURCE = Path(__file__).resolve().parents[1] / 'assets/memes/contours.json'


def animate(attribute, values, times=TIMES, mode='linear'):
    return (f'<animate attributeName="{attribute}" dur="{DURATION}s" '
            f'values="{";".join(str(v) for v in values)}" '
            f'keyTimes="{";".join(str(t) for t in times)}" '
            f'calcMode="{mode}" repeatCount="indefinite"/>')


def segments(path):
    """Flatten our small absolute M/L/Q/C/Z drawing vocabulary into segments."""
    tokens=re.findall(r'[MLQCZ]|-?\d+(?:\.\d+)?',path)
    cursor=0
    point=(0.,0.)
    origin=point
    result=[]
    while cursor<len(tokens):
        command=tokens[cursor]
        cursor+=1
        count={'M':2,'L':2,'Q':4,'C':6,'Z':0}[command]
        values=list(map(float,tokens[cursor:cursor+count]))
        cursor+=count
        if command=='M':
            point=origin=tuple(values)
            continue
        start=point
        if command=='Z': curve=[origin]
        elif command=='L': curve=[tuple(values)]
        else:
            curve=[]
            for step in range(1,25):
                t=step/24
                u=1-t
                if command=='Q':
                    curve.append(tuple(u*u*start[k]+2*u*t*values[k]+t*t*values[k+2] for k in (0,1)))
                else:
                    curve.append(tuple(u**3*start[k]+3*u*u*t*values[k]+3*u*t*t*values[k+2]+t**3*values[k+4] for k in (0,1)))
        for end in curve:
            if math.dist(point,end)>0: result.append((point,end))
            point=end
    return result


def sample(paths,count):
    lines=[segment for path in paths for segment in segments(path)]
    lengths=[]
    total=0
    for a,b in lines:
        total+=math.dist(a,b)
        lengths.append(total)
    points=[]
    for i in range(count):
        distance=(i+.5)*total/count
        j=bisect.bisect_left(lengths,distance)
        before=lengths[j-1] if j else 0
        fraction=(distance-before)/(lengths[j]-before)
        a,b=lines[j]
        # Fit the 300px drawing inside the left pane, leaving breathing room.
        points.append(tuple(round(offset+(a[k]+fraction*(b[k]-a[k]))*.95,2) for k,offset in enumerate((101,177))))
    return points


def match(source,target):
    """Greedy nearest matching keeps morph travel local without SciPy."""
    pool=list(target)
    result=[]
    for x,y in source:
        j=min(range(len(pool)),key=lambda j:(pool[j][0]-x)**2+(pool[j][1]-y)**2)
        result.append(pool.pop(j))
    return result


def particle_frames(count=COUNT):
    memes=json.loads(SOURCE.read_text(encoding='utf-8'))['memes']
    first=sample(memes[0]['paths'],count)
    second=match(first,sample(memes[1]['paths'],count))
    third=match(second,sample(memes[2]['paths'],count))
    rng=random.Random(72)
    def dissolve(a,b):
        return [(round((x+xx)/2+rng.uniform(-16,16),2),round((y+yy)/2+rng.uniform(-16,16),2)) for (x,y),(xx,yy) in zip(a,b)]
    return [first,first,dissolve(first,second),second,second,third,third,dissolve(third,first),first]


def scene(c):
    frames=particle_frames()
    parts=['<defs><clipPath id="scene-clip"><rect x="49" y="144" width="389" height="367"/></clipPath></defs>', '<g clip-path="url(#scene-clip)">']
    for i,(x,y) in enumerate(frames[0]):
        parts.append(f'<circle cx="{x}" cy="{y}" r="1.05" fill="{c["accent"]}" opacity=".95">'
                     +animate('cx',[frame[i][0] for frame in frames])
                     +animate('cy',[frame[i][1] for frame in frames])+'</circle>')
    parts.append('</g>')
    memes=json.loads(SOURCE.read_text(encoding='utf-8'))['memes']
    for i,meme in enumerate(memes):
        values=([1,0,0,1,1],[0,1,0,0,0],[0,0,1,0,0])[i]
        parts.append(f'<g opacity="{values[0]}">'+animate('opacity',values,[0,.28,.56,.84,1],'discrete')
                     +f'<text x="54" y="538" fill="{c["accent"]}" font-size="14">{meme["caption"]}</text></g>')
    return parts
