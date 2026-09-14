"""Retain the tested frame-step transport, comparing Astra I with Astra II."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
s = (ROOT/'astra-i-compare.html').read_text()
assert "['hive.html','astra-i.html']" in s
s = s.replace('Astra I / Hive','Astra I / Astra II').replace('Hive → Astra I','Astra I → Astra II')
s = s.replace('<h2>Reference Hive</h2>','<h2>Astra I</h2>').replace('title="Reference Hive"','title="Astra I reference"').replace('<h2>Astra I</h2><div class="viewport"><iframe title="Astra I"','<h2>Astra II</h2><div class="viewport"><iframe title="Astra II"')
s = s.replace("['hive.html','astra-i.html']","['astra-i.html','astra-ii.html']")
s = s.replace('<a href="hive.html">Open original Hive</a> · <a href="astra-i.html">Open Astra I</a> · <a href="astra-i-results.json">','<a href="astra-i.html">Open Astra I</a> · <a href="astra-ii.html">Open Astra II</a> · <a href="astra-ii-results.json">')
(ROOT/'astra-ii-compare.html').write_text(s)
