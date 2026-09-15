from pathlib import Path
import os
ROOT=Path(__file__).resolve().parents[2]
DIR=ROOT/'probe-runtime';DIR.mkdir(exist_ok=True)
PW=os.environ.get('PLAYWRIGHT_MODULE','/opt/pyvenv/lib/python3.13/site-packages/playwright/driver/package')
CHROME=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium')
CLIP='''function metricPicture(pic){if(!pic)return pic;return {...pic,leaves:pic.leaves.map(l=>({...l,loops:l.loops.map(lp=>{let p={pts:lp,labs:lp.map(()=>-1)};for(const [a,b,c] of [[-1,0,0],[0,-1,0],[1,0,W],[0,1,H]]){if(p.pts.length<3)break;p=clipHalfPlane(p,a,b,c,-1);}const q=p.pts;if(lp.hole)q.hole=true;return q;}).filter(lp=>lp.length>=3)})).filter(l=>l.loops.length)};}'''
for name in ['score','strobe','flicker']:
 s=(ROOT/'.claude/gauntlet'/f'{name}.js').read_text()
 s=s.replace('/opt/node22/lib/node_modules/playwright',PW)
 s=s.replace("executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',", f"executablePath: '{CHROME}'," if CHROME else '')
 s=s.replace('await p.addInitScript(CLOCK);','await p.evaluate(CLOCK);').replace("await p.goto('file://' + dst);","await p.setContent(fs.readFileSync(dst, 'utf8'));")
 s=s.replace('window.__advance = (n) => {','window.__warmup=Math.ceil(3600/DT); window.__advance = (n) => {')
 s=s.replace('for (let i = 0; i < 120; i++) step();','for (let i = 0; i < window.__warmup; i++) step();')
 s=s.replace('X.setMouse(700, 400)','X.setMouse(-1000, -1000)')
 # The observer crops world-space leaves. Rendering and simulation are untouched.
 s=s.replace('window.__X = { fn:',CLIP+' window.__X = { fn:')
 s=s.replace("`${n}: typeof ${n} !== 'undefined' ? ${n} : undefined`", "n==='picture'?'picture:metricPicture(picture)':`${n}: typeof ${n} !== 'undefined' ? ${n} : undefined`")
 (DIR/f'{name}.js').write_text(s)
