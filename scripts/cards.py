"""Fetch public GitHub facts, then render local SVGs. No private repo access.

python scripts/cards.py           # refresh public data and render
python scripts/cards.py --offline # render the saved, dated snapshot
Any API failure aborts before modifying the snapshot or cards.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import os
import urllib.request
from visuals import ASSETS, THEMES, text, rect, line, svg, save

USER = 'elhabana'
SNAPSHOT = ASSETS / 'data' / 'github.json'

def api(route):
    headers={'User-Agent':'elhabana-profile-generator','Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'}
    token=os.environ.get('GITHUB_TOKEN')
    if token: headers['Authorization']='Bearer '+token
    request=urllib.request.Request('https://api.github.com'+route,headers=headers)
    with urllib.request.urlopen(request,timeout=30) as response:
        return json.load(response)

def fetch():
    repos=[]
    page=1
    while True:
        batch=api(f'/users/{USER}/repos?type=owner&per_page=100&page={page}&sort=full_name')
        repos.extend(batch)
        if len(batch)<100: break
        page+=1
    owned=[r for r in repos if not r['fork'] and not r['private']]
    languages=Counter()
    for repo in owned:
        # Endpoint derived from the public response; API host is fixed in api().
        language_data=api(f'/repos/{repo["full_name"]}/languages')
        languages.update(language_data)
    return {
        'user':USER,
        'fetched_at':datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'source':f'https://api.github.com/users/{USER}/repos',
        'scope':'Public owned repositories, excluding forks; includes archived repositories. Languages weighted by GitHub-reported bytes.',
        'repositories':len(owned),
        'stars':sum(r['stargazers_count'] for r in owned),
        'forks':sum(r['forks_count'] for r in owned),
        'languages':dict(sorted(languages.items(),key=lambda item:(-item[1],item[0]))),
    }

def stats(data,theme):
    c=THEMES[theme]
    b=[text(26,36,'elhabana / github telemetry',c['text'],18,weight=700),line(26,54,574,54,c['line'])]
    for i,(key,label) in enumerate([('repositories','Repositories'),('stars','Stars received'),('forks','Forks received')]):
        x=26+i*188
        b += [text(x,110,f'{data[key]:,}',c['text'],36,weight=700),text(x,140,label,c['muted'],14)]
    b += [line(26,162,574,162,c['line']),text(26,188,'PUBLIC OWNED REPOS / EXCLUDES FORKS',c['muted'],12),text(26,211,'Snapshot: '+data['fetched_at'][:10]+' UTC',c['muted'],12)]
    return svg(600,232,theme,'GitHub public repository statistics for elhabana, snapshot '+data['fetched_at'],b)

def language_card(data,theme):
    c=THEMES[theme]
    langs=list(data['languages'].items())
    if len(langs)>6: langs=langs[:5]+[('Other',sum(v for _,v in langs[5:]))]
    total=sum(data['languages'].values())
    b=[text(26,34,'Repository languages',c['text'],18,weight=700),text(26,58,'Byte distribution / not a skill ranking',c['muted'],12)]
    shades=['#A9C0DD','#8FA5C2','#788DA9','#637893','#50647F','#3C506C'] if theme=='dark' else ['#42658D','#587BA2','#7390B1','#8FA6C0','#A8BAD0','#C0CDDD']
    if not total:
        b.append(text(26,110,'No language bytes reported by GitHub.',c['muted'],15))
    else:
        x=26
        for i,(name,value) in enumerate(langs):
            width=548*value/total
            b.append(rect(round(x,3),80,round(width,3),12,shades[i],radius=0))
            x+=width
        for i,(name,value) in enumerate(langs):
            x=26+(i%2)*282
            y=124+(i//2)*30
            b += [rect(x,y-11,9,9,shades[i],radius=2),text(x+17,y,f'{name}  {100*value/total:.1f}%',c['text'],13)]
    height=152+max(0,(len(langs)-1)//2)*30
    b.append(text(26,height-14,'Public owned repos / includes archived / '+data['fetched_at'][:10],c['muted'],11))
    return svg(600,height,theme,'Language bytes in public non-fork repositories, not personal proficiency',b)

def validate(data):
    if data['user']!=USER: raise ValueError('Snapshot belongs to another user')
    datetime.fromisoformat(data['fetched_at'])
    for field in ['repositories','stars','forks']:
        if type(data[field]) is not int or data[field]<0: raise ValueError('Invalid metric: '+field)
    if any(type(n) is not int or n<0 for n in data['languages'].values()): raise ValueError('Invalid language bytes')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--offline',action='store_true')
    args=parser.parse_args()
    data=json.loads(SNAPSHOT.read_text(encoding='utf-8')) if args.offline else fetch()
    validate(data)
    outputs={}
    for theme in THEMES:
        outputs[f'github-stats-{theme}.svg']=stats(data,theme)
        outputs['languages.svg' if theme=='dark' else 'languages-light.svg']=language_card(data,theme)
    # Build everything before writing so API/render errors preserve the last good set.
    if not args.offline: SNAPSHOT.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    for name,body in outputs.items(): save(name,body)
    print('Rendered verified public snapshot from '+data['fetched_at'])

if __name__=='__main__': main()
