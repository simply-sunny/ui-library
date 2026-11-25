import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

class UiParts(unittest.TestCase):
    UI=ROOT/'ui'

    def ui(self,*args):
        return subprocess.run([sys.executable,str(ROOT/'create.py'),*args],capture_output=True,text=True)

    def test_docs_are_written_from_the_manifest(self):
        result=self.ui('--docs')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual((ROOT/'docs/COMPONENTS.md').read_text(),result.stdout,'run: python3 create.py --docs > docs/COMPONENTS.md')

    def test_every_part_is_defined_where_the_manifest_says(self):
        m=json.loads((self.UI/'components.json').read_text())
        names=[c['name'] for c in m['components']]
        self.assertEqual(len(names),len(set(names)))
        sources={'ui.css':(self.UI/'ui.css').read_text(),'ui.js':(self.UI/'ui.js').read_text(),'base.css':(ROOT/'base.css').read_text()}
        for c in m['components']:
            for key in ['name','kind','from','selector','use','example']:
                self.assertIn(key,c,c.get('name'))
            for sel in c['selector'].split(','):
                sel=sel.strip().split('.')[-1] if c['kind']=='class' else sel.strip()
                needle=('.'+sel) if c['kind']=='class' else "'"+sel+"'"
                self.assertIn(needle,sources[c['from']],f"{c['name']}: {needle} not in {c['from']}")

    def test_gallery_shows_every_part(self):
        m=json.loads((self.UI/'components.json').read_text())
        with tempfile.TemporaryDirectory() as directory:
            dest=Path(directory)/'gallery'
            result=self.ui('--gallery',str(dest))
            self.assertEqual(result.returncode,0,result.stderr)
            page=(dest/'index.html').read_text()
            for c in m['components']:
                self.assertIn(c['example'],page,c['name'])
            for f in ['assets/ui/ui.css','assets/ui/ui.js','assets/base.css','assets/ui/sample.wav','assets/ui/sample-new.wav']:
                self.assertTrue((dest/f).is_file(),f)

    def test_adding_to_a_site_never_overwrites_changed_parts_unasked(self):
        with tempfile.TemporaryDirectory() as directory:
            dest=Path(directory)/'assets/ui'
            self.assertEqual(self.ui('--dest',str(dest)).returncode,0)
            self.assertEqual((dest/'ui.js').read_text(),(self.UI/'ui.js').read_text())
            (dest/'ui.css').write_text('/* changed */')
            self.assertNotEqual(self.ui('--dest',str(dest)).returncode,0)
            self.assertEqual((dest/'ui.css').read_text(),'/* changed */')
            self.assertEqual(self.ui('--dest',str(dest),'--update').returncode,0)
            self.assertEqual((dest/'ui.css').read_text(),(self.UI/'ui.css').read_text())

    def test_script_parses(self):
        node=shutil.which('node')
        if not node:
            self.skipTest('no node')
        result=subprocess.run([node,'--check',str(self.UI/'ui.js')],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)

if __name__=='__main__':unittest.main()
