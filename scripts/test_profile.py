"""Data-integrity checks for automated profile generation."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error
import xml.etree.ElementTree as ET
import cards
import radar
import banner
from visuals import ASSETS, THEMES

class ProfileTests(unittest.TestCase):
    def test_pagination_and_scope(self):
        def repo(i):
            return dict(full_name=f'elhabana/r{i}',fork=False,private=False,stargazers_count=2,forks_count=1)
        first=[repo(i) for i in range(100)]
        first[0]['fork']=True
        first[1]['private']=True
        first[2]['archived']=True
        def api(route):
            if '/users/' in route: return first if 'page=1&' in route else [repo(100)]
            return {'C#':100,'ShaderLab':20}
        with patch.object(cards,'api',side_effect=api): result=cards.fetch()
        self.assertEqual(result['repositories'],99)
        self.assertEqual(result['stars'],198)
        self.assertEqual(result['forks'],99)
        self.assertEqual(result['languages'],{'C#':9900,'ShaderLab':1980})

    def test_api_failure_keeps_snapshot(self):
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder)/'github.json'
            target.write_text('last good snapshot',encoding='utf-8')
            with patch.object(cards,'SNAPSHOT',target), patch.object(cards,'api',side_effect=urllib.error.URLError('offline')), patch.object(cards,'save') as save, patch('sys.argv',['cards.py']):
                with self.assertRaises(urllib.error.URLError): cards.main()
            self.assertEqual(target.read_text(encoding='utf-8'),'last good snapshot')
            save.assert_not_called()

    def test_radar_rejects_invalid_values(self):
        data=json.loads((ASSETS/'data/game-skills.json').read_text())
        for bad in [float('nan'),float('inf'),-1,101,True]:
            data['axes'][0]['value']=bad
            with self.assertRaises(ValueError): radar.render(data,'dark')

    def test_empty_languages_and_other_sum(self):
        data={'languages':{},'fetched_at':'2026-01-01T00:00:00+00:00'}
        self.assertIn('No language bytes',cards.language_card(data,'dark'))
        data['languages']={f'Lang{i}':10 for i in range(8)}
        result=cards.language_card(data,'dark')
        self.assertIn('Other  37.5%',result)
        ET.fromstring(result)

    def test_themes_and_xml_escaping(self):
        data=json.loads((ASSETS/'data/game-skills.json').read_text())
        data['title']='Art & Code <test>'
        for theme in THEMES:
            for output in [banner.render(theme),banner.project(theme),radar.render(data,theme)]:
                ET.fromstring(output)

    def test_snapshot_and_local_asset_links(self):
        import re
        cards.validate(json.loads(cards.SNAPSHOT.read_text()))
        readme=(ASSETS.parent/'README.md').read_text(encoding='utf-8')
        for path in re.findall(r'(?:src|srcset)="(assets/[^\"]+)"',readme):
            full=ASSETS.parent/path
            self.assertTrue(full.is_file(),path)
            ET.parse(full)

if __name__=='__main__': unittest.main()
