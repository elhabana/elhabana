"""Validate the README wiring, the SVG generators and the animation loops."""
import re
import unittest
import xml.etree.ElementTree as ET

import banner
import motion
from visuals import ASSETS, THEMES

SVG = '{http://www.w3.org/2000/svg}'
README = ASSETS.parent / 'README.md'
MAX_BYTES = 150_000
# Widgets we deliberately dropped: abandoned hosts, vanity counters and the
# giant typing header that competed with the hero.
BANNED_IN_README = ('Cristian Habana', 'readme-typing-svg', 'komarev.com',
                    'github-profile-trophy', 'activity-graph.herokuapp.com',
                    'cyclic.app')


class ReadmeTests(unittest.TestCase):
    def read(self):
        return README.read_text(encoding='utf-8')

    def test_local_assets_exist_and_parse(self):
        sources = set(re.findall(r'(?:src|srcset)="(assets/[^"]+)"', self.read()))
        self.assertGreaterEqual(len(sources), 10)
        for source in sources:
            path = ASSETS.parent / source
            self.assertTrue(path.is_file(), f'README points at a missing file: {source}')
            ET.parse(path)

    def test_identity_is_habana(self):
        readme = self.read()
        self.assertIn('Habana', readme)
        self.assertIn('@elhabana', readme)
        self.assertIn('Cristian Rivero Llácer', readme)

    def test_removed_widgets_stay_removed(self):
        readme = self.read()
        for banned in BANNED_IN_README:
            self.assertNotIn(banned, readme, f'drop {banned!r}')

    def test_dark_and_light_variants_are_paired(self):
        readme = self.read()
        self.assertEqual(readme.count('prefers-color-scheme: dark'),
                         readme.count('prefers-color-scheme: light'))
        self.assertGreaterEqual(readme.count('prefers-color-scheme: dark'), 6)

    def test_banner_images_are_fluid_and_described(self):
        # Fixed-size app icons are excluded on purpose: only the panels and
        # covers have to stretch with the column.
        tags = re.findall(r'<img src="assets/(?!icons/)[^"]+"[^>]*>', self.read())
        # hero, dev-humour banner, UN-CREDIBLES cover and the Selected Work slot
        self.assertEqual(len(tags), 4)
        for tag in tags:
            self.assertIn('width="100%"', tag, tag)
            self.assertIn('alt="', tag, tag)


class HeroTests(unittest.TestCase):
    def test_hero_states_the_role_without_the_legal_name(self):
        for theme in THEMES:
            markup = banner.hero(theme)
            self.assertIn('Gameplay Programmer', markup)
            self.assertIn('Audiovisual Creator', markup)
            self.assertIn('Habana', markup)
            self.assertNotIn('Cristian', markup)

    def test_every_static_asset_is_valid_svg(self):
        for theme in THEMES:
            for markup in (banner.hero(theme), banner.project(theme), banner.reserved(theme)):
                self.assertEqual(ET.fromstring(markup).tag, f'{SVG}svg')


class MotionTests(unittest.TestCase):
    def test_fade_tracks_are_well_formed(self):
        for index in range(len(motion.SCENES)):
            key_times, values = motion.fade_track(index)
            self.assertEqual(len(key_times), len(values))
            self.assertEqual(key_times, sorted(key_times), 'keyTimes must increase')
            self.assertEqual(len(set(key_times)), len(key_times))
            self.assertEqual(key_times[0], 0.0)
            self.assertEqual(key_times[-1], 1.0)
            self.assertEqual(values[0], values[-1], 'the loop seam must match')
            self.assertIn(1.0, values, 'every scene must reach full opacity')
            self.assertTrue(0.0 <= min(values) <= max(values) <= 1.0)

    def test_scenes_always_cover_the_loop(self):
        steps = 720

        def opacity(index, moment):
            key_times, values = motion.fade_track(index)
            position = moment / motion.DURATION
            for left, right, start, end in zip(key_times, key_times[1:],
                                               values, values[1:]):
                if left <= position <= right:
                    if right == left:
                        return start
                    return start + (position - left) / (right - left) * (end - start)
            return 0.0

        for step in range(steps):
            moment = step * motion.DURATION / steps
            total = sum(opacity(index, moment) for index in range(len(motion.SCENES)))
            self.assertAlmostEqual(total, 1.0, places=2, msg=f'gap at t={moment:.2f}s')

    def test_banner_is_self_contained_and_animated(self):
        for theme in THEMES:
            markup = motion.render(theme)
            for banned in ('<script', 'foreignObject', 'base64', '<image', 'href='):
                self.assertNotIn(banned, markup)
            self.assertEqual(markup.count('http'), 1, 'only the SVG namespace may be a URL')
            animations = ET.fromstring(markup).findall(f'.//{SVG}animate')
            self.assertGreaterEqual(len(animations), len(motion.SCENES))
            self.assertIn(f'dur="{motion.DURATION}s"', markup)
            for node in animations:
                self.assertEqual(len(node.get('values').split(';')),
                                 len(node.get('keyTimes').split(';')))
                self.assertEqual(node.get('repeatCount'), 'indefinite')

    def test_static_fallback_shows_a_single_scene(self):
        # Renderers without SMIL use the base opacity, so exactly one scene may
        # carry opacity="1" and every other scene must start hidden.
        markup = motion.render('dark')
        groups = re.findall(r'<g opacity="([^"]+)">', markup)
        self.assertEqual(groups.count('1'), 1)
        self.assertEqual(set(groups), {'0', '1'})


class AssetTests(unittest.TestCase):
    def test_generated_assets_are_present_and_light(self):
        for theme in THEMES:
            for name in (f'banner-{theme}.svg', f'uncredibles-{theme}.svg',
                         f'projects/reserved-{theme}.svg', f'memes/dev-memes-{theme}.svg'):
                path = ASSETS / name
                self.assertTrue(path.is_file(),
                                f'{name} is missing: run python scripts/banner.py')
                self.assertLess(path.stat().st_size, MAX_BYTES,
                                f'{name} is heavier than it needs to be')

    def test_old_particle_payload_is_gone(self):
        self.assertFalse((ASSETS / 'memes/contours.json').exists())


if __name__ == '__main__':
    unittest.main()
