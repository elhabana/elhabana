"""Render six-axis interest maps from editable JSON, never objective skill ratings."""
import json
import math
from visuals import ASSETS, THEMES, text, line, svg, save

def render(data,theme):
    axes=data['axes']
    if len(axes)!=6 or any(type(a['value']) not in (int,float) or not math.isfinite(a['value']) or not 0<=a['value']<=100 for a in axes):
        raise ValueError('Expected six axes with finite values in [0, 100]')
    c=THEMES[theme]
    cx,cy,r=240,216,112
    def point(i,scale):
        a=-math.pi/2+i*math.tau/6
        return cx+math.cos(a)*r*scale,cy+math.sin(a)*r*scale
    def points(scale):
        return ' '.join(f'{x:.2f},{y:.2f}' for x,y in [point(i,scale) for i in range(6)])
    b=[text(24,33,data['title'],c['text'],18,weight=700),text(24,58,'INTEREST / FOCUS MAP',c['muted'],12),line(24,74,456,74,c['line'])]
    for ring in [.25,.5,.75,1]:
        b.append(f'<polygon points="{points(ring)}" fill="none" stroke="{c["line"]}"/>')
    for i in range(6):
        x,y=point(i,1)
        b.append(line(cx,cy,round(x,2),round(y,2),c['line']))
    p=[point(i,a['value']/100) for i,a in enumerate(axes)]
    coords=' '.join(f'{x:.2f},{y:.2f}' for x,y in p)
    b.append(f'<polygon points="{coords}" fill="{c["accent"]}" fill-opacity=".16" stroke="{c["accent"]}" stroke-width="2"/>')
    for x,y in p: b.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3" fill="{c["text"]}"/>')
    labels=[(240,92,'middle'),(353,153,'start'),(353,279,'start'),(240,351,'middle'),(127,279,'end'),(127,153,'end')]
    for axis,(x,y,anchor) in zip(axes,labels):
        words=axis['label'].split()
        if len(axis['label'])>11:
            split=2 if len(words)>2 else 1
            b += [text(x,y,' '.join(words[:split]),c['text'],14,anchor),text(x,y+18,' '.join(words[split:]),c['text'],14,anchor)]
        else: b.append(text(x,y,axis['label'],c['text'],14,anchor))
    b.append(text(240,389,'Personal emphasis / not proficiency',c['muted'],12,'middle'))
    return svg(480,412,theme,data['title']+' — personal interests, not measured proficiency',b)

if __name__=='__main__':
    for category in ['game','creative']:
        data=json.loads((ASSETS/'data'/f'{category}-skills.json').read_text(encoding='utf-8'))
        for theme in THEMES: save(f'radar-{category}-{theme}.svg',render(data,theme))
