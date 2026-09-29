"""Validate the particle loop and the local README assets."""
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET
import banner
import motion
from visuals import ASSETS, THEMES

class ProfileTests(unittest.TestCase):
    def test_motion_loop_and_viewport_bounds(self):
        frames=motion.particle_frames()
        self.assertEqual(len(frames),len(motion.TIMES))
        self.assertEqual(frames[0],frames[-1])
        self.assertNotEqual(frames[0],frames[3])
        self.assertNotEqual(frames[3],frames[5])
        for frame in frames:
            self.assertEqual(len(frame),motion.COUNT)
            self.assertTrue(all(49<x<438 and 144<y<511 for x,y in frame))

    def test_animation_markup_and_themes(self):
        for theme in THEMES:
            root=ET.fromstring(banner.render(theme))
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
