"""Build the isolated buffer mark from the exact, unchanged Astra II reference."""
from pathlib import Path
import hashlib
ROOT=Path(__file__).resolve().parents[2]
EXPECTED='ec30d312ef52cf397f3ca1fafabc3130cfaac56f0b741eab9f6be68375536e81'
reference=(ROOT/'astra-ii.html').read_bytes()
assert hashlib.sha256(reference).hexdigest()==EXPECTED, 'Astra II reference changed; rebaseline explicitly'
s=reference.decode()
anchor='/* --------------------------------------------------------------- START */'
assert s.count(anchor)==1
engine=(ROOT/'tests/buffer/engine.js').read_text()+'\n'+(ROOT/'tests/buffer/view.js').read_text()
s=s.replace(anchor,engine+'\n'+anchor)
a='!(b.a2SwapCount>0));';assert s.count(a)==1
s=s.replace(a,'!(b.a2SwapCount>0)&&!(b.bufferReservedUntil>t));')
s=s.replace('<title>Astra II — Hive</title>','<title>Astra II — True Buffer</title>')
(ROOT/'astra-buffer.html').write_text(s)
index=ROOT/'index.html'
if index.exists():
 text=index.read_text()
 if '<!-- TRUE BUFFER -->' not in text:
  anchor='<div class="previews">';assert text.count(anchor)==1
  card='''
        <!-- TRUE BUFFER -->
        <a href="astra-buffer.html" class="version-card">
            <h2>Astra II · True Buffer</h2><span class="tag preview">Buffer experiment</span>
            <p>A real exterior partition and a lendable area reserve. Inspect the actual outside polygons and connected yielding routes; compare the same mechanism with its reserve locked.</p>
            <ul><li>Separate total, visible and off-screen area</li><li>No proportional inflation of every cell</li><li>Motion quality remains experimental</li></ul>
        </a>
        <a href="astra-buffer-compare.html" class="version-card">
            <h2>Compare the buffer</h2><span class="tag preview">Frame stepping</span>
            <p>Open versus locked reserve, no-cascade control, or the unchanged Astra II reference. Identical viewports and clocks.</p>
        </a>
        <!-- /TRUE BUFFER -->
'''
  index.write_text(text.replace(anchor,anchor+card))
print(hashlib.sha256(s.encode()).hexdigest())
