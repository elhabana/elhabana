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
            images=root.findall('.//{http://www.w3.org/2000/svg}image')
            self.assertEqual(len(images),len(avatar.FRAMES))
            self.assertTrue(all(image.get('href','').startswith('data:image/png;base64,') for image in images))
            for node in root.findall('.//{http://www.w3.org/2000/svg}animate'):
                self.assertEqual(len(node.get('values').split(';')),len(node.get('keyTimes').split(';')))
                self.assertEqual(node.get('repeatCount'),'indefinite')
            ET.fromstring(banner.project(theme))

    def test_readme_local_assets(self):
        readme=(ASSETS.parent/'README.md').read_text(encoding='utf-8')
        for path in re.findall(r'(?:src|srcset)="(assets/[^\"]+)"',readme):
            full=ASSETS.parent/path
            self.assertTrue(full.is_file(),path)
            ET.parse(full)

if __name__=='__main__': unittest.main()
