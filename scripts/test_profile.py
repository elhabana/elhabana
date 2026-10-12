"""Validate the generated profile graphics and local README assets."""
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET
import banner
import avatar
from visuals import ASSETS, THEMES

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
            overlay=root.find('.//{http://www.w3.org/2000/svg}g[@id="boot"]')
            self.assertIsNotNone(overlay)
            self.assertEqual(overlay.get('opacity'),'0')

    def test_readme_local_assets(self):
        readme=(ASSETS.parent/'README.md').read_text(encoding='utf-8')
        for path in re.findall(r'(?:src|srcset)="(assets/[^\"]+)"',readme):
            full=ASSETS.parent/path
            self.assertTrue(full.is_file(),path)
            ET.parse(full)

if __name__=='__main__': unittest.main()
