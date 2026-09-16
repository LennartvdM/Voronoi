"""Build the Brim mark: Murmur with the overflow buffer deleted outright.

THE CONTROL, AND A CANDIDATE IN ITS OWN RIGHT.

Murmur moves well and then skips, twice per change. Measured at 30 ms with
.claude/gauntlet/jolt.js, the page rests moving 0.2 px per frame, and then:

    scene     frame 0     ...      the closing frame     its neighbours
    hero      33.3 px              172.6 px              1.1 - 5 px
    sidebar   32.5 px              127.2 px              0.9 - 5 px
    frame     33.0 px              183.9 px              1.0 - 4 px

muOpen() is true on the first of those frames and false on the last. jolt.js
finds exactly two spike frames per transition scene and they sit at normalised
positions 0.00 and 1.00 — the first frame of the change and the last. Nothing
in between exceeds twice its neighbours. Bleed, whose margin is permanently
open and therefore never switches, has no spike at all (worst 1.4).

So the buffer's SWITCH is the skip. Two marks follow from that, and each is
the other's proof:

  BRIM (this one) deletes the buffer. If the page is fine without it, the
  buffer was never needed, and no amount of making it smoother would have
  been worth the code.

  BELLOWS makes the buffer continuous — a domain that grows and shrinks with
  what the page has asked for, never switching. If that removes the skip AND
  the page is measurably worse without it, the buffer was load-bearing all
  along.

Brim is therefore Murmur MINUS EXACTLY ONE THING. It keeps the single species
(the root hive's crystal pinned to 0, so no walls, no half-plane blend, no
flubber) and it keeps every body seated with a path to follow. It drops the
ring, the reserve, its four guards, the swell and the seed box. The domain is
the window, always, as it is in the reference.

What that predicts, and what to check: with no margin to borrow, a travelling
body's room can only come from its neighbours, so if the buffer was doing
anything the price appears as GRIDLOCK — cells driven thin. The sliver share
and the worst-cell figures in tests/brim/validate.py are where that would
show.

The reference is never modified; the mark is regenerated from it.
"""
from pathlib import Path
import hashlib
import os
import re

ROOT = Path(__file__).resolve().parents[2]
raw = (ROOT / 'hive.html').read_bytes()
blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
EXPECTED = '2c02b2dc66d05fb152feffcd952f18b4d39f3634'
if blob != EXPECTED:
    raise SystemExit(f'Reference changed: expected {EXPECTED}, found {blob}; rebaseline before rebuilding.')
s = raw.decode()


def replace(old, new, count=1):
    global s
    found = s.count(old)
    if found != count:
        raise ValueError(f'Expected {count} matches for {old[:70]!r}; found {found}')
    s = s.replace(old, new)


replace('<title>Hive</title>', '<title>Brim — Hive</title>')
replace('&larr; Back</a>', '&larr; Back · Brim</a>')

# ------------------------------------------------------------- one kind of body
# Murmur's whole mark, unchanged. A wall is a rectangle cut out of the ground; a
# hole is the half-plane blend between a cell and a rectangle, and the blend is
# the flubber. Refusing to leave zero refuses both, and a single site's power
# cell is convex — so three-to-nine corners is not a rule that has to be
# policed, it is the shape a bidder has. Nested hives are untouched.
replace('''  updateCrystal(b, t) {
    if (b.table && b.table.mode === 'open') return;      // an opening void reads its vacators' clocks''',
'''  updateCrystal(b, t) {
    // ONE SPECIES. A rectangle is a DESTINATION — a place to travel to and an
    // area to claim — never a category the body belongs to.
    if (this.depth === 0) { b.crystal = 0; b.pin = 0; return; }
    if (b.table && b.table.mode === 'open') return;      // an opening void reads its vacators' clocks''')

# ----------------------------------------------------------- a journey that ends
# The reference ends a journey only for a body that has NO rectangle, which is
# sound there because a body that has one announces its arrival by reaching
# crystal 1 and becoming a wall. Nothing here ever does, so without this every
# body would carry a finished journey for the rest of the page's life. Nothing
# in Brim reads a journey to decide anything about the ground — that is the
# point of Brim — but the two marks have to differ in exactly one thing for
# either to prove anything about the other, so this stays.
replace('        if (!b.rect && !b.leaving && !b.table && u >= 1 && b.crystal === 0) b.journey = null;',
        '        if (!b.leaving && !b.table && u >= 1 && b.crystal === 0) b.journey = null;')

# development only: BRIM_OUT=<path> writes elsewhere and skips the gallery
OUT = Path(os.environ.get('BRIM_OUT', str(ROOT / 'brim.html')))
OUT.write_text(s)
if os.environ.get('BRIM_OUT'):
    print('Built variant', OUT)
    raise SystemExit(0)

# --- the gallery card -------------------------------------------------------
index_path = ROOT / 'index.html'
index = index_path.read_text()
card = '''
        <!-- BRIM -->
        <a href="brim.html" class="version-card latest">
            <h2>Brim</h2><span class="latest-flag">Latest</span>
            <span class="mk">Brim</span>
            <span class="tag preview">Tested experiment</span>
            <p>Murmur with the overflow buffer deleted. Murmur skips twice per change — 33 px in the frame the margin opens, 130 to 184 px in the frame it shuts, against neighbours moving 1 to 5 px — and the switch is the skip. Brim removes the switch by removing the thing that switches: the page is the window, always, and a travelling cell's room can only come from its neighbours. It is the control that says whether the buffer was ever needed.</p>
            <ul>
                <li>No margin, no reserve, no loan: one domain, never resized</li>
                <li>Every cell still a bidder — no walls, no blend, no flubber</li>
                <li>The skip gone by construction; the question is what it costs</li>
                <li>Read against Bellows, which keeps the buffer and makes it continuous</li>
            </ul>
        </a>
        <!-- /BRIM -->
'''
anchor = '<div class="previews">'
if index.count(anchor) != 1:
    raise ValueError('Gallery anchor missing or ambiguous')
IS_LATEST = True   # only the newest mark wears the flag
if not IS_LATEST:
    card = card.replace(' latest"', '"').replace('<span class="latest-flag">Latest</span>', '')
own = re.compile(r'\n?[ \t]*<!-- BRIM -->.*?<!-- /BRIM -->[ \t]*\n?', re.S)
index = own.sub(lambda m: card, index, count=1) if own.search(index) else index.replace(anchor, anchor + card, 1)
index_path.write_text(index)
print('Built brim.html from reference blob', EXPECTED)
print('Brim SHA256', hashlib.sha256(s.encode()).hexdigest())
