"""Build Harbor and Quay from the immutable Selvedge continuity baseline."""
from pathlib import Path
import hashlib

ROOT=Path(__file__).resolve().parents[2]
raw=(ROOT/'selvedge.html').read_bytes()
blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
if blob!='9b10a9094ba149429c36a2c36a78b35cb0e26dc1':
    raise SystemExit('Selvedge source differs from the reviewed baseline: '+blob)
base=raw.decode()
for name,template in [('harbor',0),('quay',1)]:
    s=base.replace('<title>Selvedge — Hive</title>',f'<title>{name.title()} — Hive</title>').replace('&larr; Back · Selvedge</a>',f'&larr; Compare · {name.title()}</a>').replace('class="back" href="index.html"','class="back" href="manifold.html"')
    def replace(a,b):
        global s
        if s.count(a)!=1:raise ValueError(f'{name}: expected one match for {a[:80]!r}, found {s.count(a)}')
        s=s.replace(a,b)
    replace('function rectArea(r) { return (r[2] - r[0]) * (r[3] - r[1]); }','function rectArea(r) { return r.mfArea === undefined ? (r[2] - r[0]) * (r[3] - r[1]) : r.mfArea; }')
    replace('rectCenter(r) { return [this.PW * (r[0] + r[2]) / 2, this.PH * (r[1] + r[3]) / 2]; }','rectCenter(r) { return r.mfSeed ? [this.PW*r.mfSeed[0],this.PH*r.mfSeed[1]] : [this.PW * (r[0] + r[2]) / 2, this.PH * (r[1] + r[3]) / 2]; }')
    replace('const spec = scenes[name] ? scenes[name](this.COLS, this.ROWS, content.length) : null;',"const spec = this.depth===0 && (name==='hero'||name==='frame') ? mfScene(this,name,content.length) : scenes[name] ? scenes[name](this.COLS, this.ROWS, content.length) : null;")
    replace('if (same) { stays.add(same); continue; }','if (same) { if(r.mfSites) { same.rect=r; same.formRect=r; } stays.add(same); continue; }')
    replace("k += b.id + ':' + r.join(',') + ';';","k += b.id + ':' + r.join(',') + ':' + (r.mfKey || '') + ';';")
    replace('if (target.length) v.wvTo = target;','if (rv.mfSites) v.wvTo=rv.mfSites.map(p=>({...p}));\n      else if (target.length) v.wvTo = target;')
    replace('  steer(dt, t) {', '''  mfFreedom(b) {
    // The destination already has valid geometry. Ambient wobble and
    // repulsion must not permanently displace its seeds from that solution.
    // Fade these forces over the existing journey, with no extra clock,
    // pin, geometry switch, or change to the number of content sites.
    return this.depth===0 && b.rect && b.rect.mfRest && !b.leaving
      ? 1 - (b.progress || 0) : 1 - b.crystal;
  }

  steer(dt, t) {''')
    replace('const wob = 2.5 * (1 - b.crystal);','const wob = 2.5 * this.mfFreedom(b);')
    replace('''          const f = F * (1 - Math.min(A.crystal, B.crystal)) * (1 - d / R) * dt / dn;
          A.vx -= dx * f * (1 - A.crystal); A.vy -= dy * f * (1 - A.crystal);
          B.vx += dx * f * (1 - B.crystal); B.vy += dy * f * (1 - B.crystal);''','''          const a=this.mfFreedom(A), b=this.mfFreedom(B);
          const f = F * Math.max(a,b) * (1 - d / R) * dt / dn;
          A.vx -= dx * f * a; A.vy -= dy * f * a;
          B.vx += dx * f * b; B.vy += dy * f * b;''')
    # Recompile aspect-dependent rest quotas on resize through the ordinary
    # scene handover. Existing void sites/weights survive this retarget.
    replace('if (C === this.COLS && R === this.ROWS) return;',"if (C === this.COLS && R === this.ROWS && !(this.depth===0 && this.mfResize)) return;\n    this.mfResize=false;")
    replace('if (this.wantCols() !== this.COLS || this.wantRows() !== this.ROWS) this.layoutAt = this.t;',"if (this.depth===0 && (this.scene==='hero'||this.scene==='frame')) this.mfResize=true;\n    if (this.mfResize || this.wantCols() !== this.COLS || this.wantRows() !== this.ROWS) this.layoutAt = this.t;")
    code=(Path(__file__).parent/'targets.js').read_text()
    replace('/* --------------------------------------------------------------- START */',f'const MF_TEMPLATE_HERO={template};\n'+code+'\n/* --------------------------------------------------------------- START */')
    (ROOT/f'{name}.html').write_text(s)
    print(name,hashlib.sha256(s.encode()).hexdigest())
