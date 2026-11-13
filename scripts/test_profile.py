"""Validate the generated profile graphics and local README assets."""
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET
import banner
import avatar
import cards
from visuals import ASSETS, THEMES
import visuals

class ProfileTests(unittest.TestCase):
    def test_avatar_frames(self):
        self.assertEqual(len(avatar.TIMES),len(avatar.STATES))
        self.assertEqual(avatar.STATES[0],avatar.STATES[-1])
        for frame in avatar.FRAMES:
            self.assertTrue((ASSETS/'avatar'/f'{frame}.png').is_file())

    def test_animation_markup_and_themes(self):
        for theme in THEMES:
            root=ET.fromstring(banner.render(theme))
            self.assertFalse(root.findall('.//{http://www.w3.org/2000/svg}image'))
            dots=avatar.particles(theme=='light')
            self.assertGreater(len(dots),2000)
            talking=[looks for _,_,looks in dots if looks['talk']!=looks['neutral']]
            blinking=[looks for _,_,looks in dots if looks['blink']!=looks['neutral']]
            self.assertTrue(talking and blinking)
            for node in root.findall('.//{http://www.w3.org/2000/svg}animate'):
                if node.get('keyTimes'):
                    self.assertEqual(len(node.get('values').split(';')),len(node.get('keyTimes').split(';')))
                self.assertTrue(node.get('repeatCount')=='indefinite' or node.get('fill')=='freeze')
            ET.fromstring(banner.project(theme))

    def test_boot_overlay_is_static_safe(self):
        for theme in THEMES:
            root=ET.fromstring(banner.render(theme))
            for name in ('boot','invaders'):
                overlay=root.find(f'.//{{http://www.w3.org/2000/svg}}g[@id="{name}"]')
                self.assertIsNotNone(overlay,name)
                self.assertEqual(overlay.get('opacity'),'0',name)

    def test_dots_d_round_trip(self):
        points=[(283.1,407.5),(216.3,356.4),(216.0,356.4),(300,10.1),(5.5,.2),(0,0)]
        d=visuals.dots_d(points)
        self.assertEqual(d.count('h0'),len(points))
        x=y=0;out=[]
        for i,(dx,dy) in enumerate(re.findall(r'[Mm](-?\d*\.?\d+) ?(-?\d*\.?\d+)h0',d)):
            x,y=(float(dx),float(dy)) if i==0 else (x+float(dx),y+float(dy))
            out.append((round(x,1),round(y,1)))
        self.assertEqual(out,sorted(points,key=lambda p:(p[1],p[0])))
        self.assertEqual(visuals.dots_d([(1.4,2.6),(3.6,-1.2)],whole=True),'M4-1h0m-3 4h0')

    def test_reduced_motion_versions(self):
        readme=(ASSETS.parent/'README.md').read_text(encoding='utf-8')
        for theme in THEMES:
            for name,content in ((f'banner-{theme}',banner.render(theme)),(f'uncredibles-{theme}',banner.project(theme))):
                root=ET.fromstring(banner.still(content))
                self.assertFalse([n for n in root.iter() if n.tag.split('}')[1] in ('animate','animateTransform','set')],name)
                self.assertRegex(readme,r'media="\(prefers-reduced-motion: reduce\)[^"]*" srcset="assets/'+name+'-static.svg"')

    def test_cards_link_to_rookies(self):
        readme=(ASSETS.parent/'README.md').read_text(encoding='utf-8')
        for name in cards.render_all():
            self.assertRegex(readme,r'(?s)<a href="https://www\.therookies\.co/projects/\d+"><picture>(?:(?!</a>).)*'+re.escape(name),name)

    def test_readme_local_assets(self):
        readme=(ASSETS.parent/'README.md').read_text(encoding='utf-8')
        for path in re.findall(r'(?:src|srcset)="(assets/[^\"]+)"',readme):
            full=ASSETS.parent/path
            self.assertTrue(full.is_file(),path)
            ET.parse(full)

if __name__=='__main__': unittest.main()
