// Diagnostic camera: these are the solver's actual world polygons, not a
// second animation. Showing the ring does not resize or rerun the simulation.
const bfView=document.createElement('div');
bfView.style.cssText='position:absolute;right:16px;top:12px;z-index:8;color:#ccd;font:12px system-ui;max-width:calc(100% - 32px)';
bfView.innerHTML='<div style="display:flex;justify-content:flex-end;gap:6px"><span id="bf-meter" style="padding:6px 8px;background:#10111cdd;border-radius:5px"></span><button type="button" class="btn" id="bf-toggle">Show actual buffer</button></div><div id="bf-panel" hidden style="margin-top:6px;padding:10px;background:#0d0e17f5;border:1px solid #44445a;border-radius:8px"><canvas id="bf-map" width="560" height="400" style="width:560px;max-width:100%;height:auto"></canvas><p id="bf-caption" style="margin-top:7px;line-height:1.4"></p><p style="margin-top:6px"><a style="color:#b9baff" href="astra-buffer-compare.html">Compare open / locked reserve</a> · <a style="color:#b9baff" href="astra-ii.html">Astra II reference</a></p></div>';
document.querySelector('.stage').appendChild(bfView);
const bfPanel=bfView.querySelector('#bf-panel'),bfMap=bfView.querySelector('#bf-map'),bfCtx=bfMap.getContext('2d');
bfView.querySelector('#bf-toggle').onclick=()=>{bfPanel.hidden=!bfPanel.hidden;bfView.querySelector('#bf-toggle').textContent=bfPanel.hidden?'Show actual buffer':'Hide buffer view';bfDrawWorld();};
if(bfParams.get('world')==='1')bfPanel.hidden=false;
function bfDrawWorld(){
 const h=root,w=h.bufferWorld;if(!w)return;
 const fmt=x=>Math.round(x||0).toLocaleString('en-US');
 bfView.querySelector('#bf-meter').textContent=(BUFFER_SETTINGS.locked?'Reserve locked · ':'')+'Outside: '+fmt(h.bufferContentOutside)+' px²';
 if(bfPanel.hidden)return;
 const B=bfMargin(h),W=h.W,H=h.H,scale=Math.min(536/(W+2*B),336/(H+2*B)),ox=(560-(W+2*B)*scale)/2+B*scale,oy=12+B*scale;
 const c=bfCtx;c.clearRect(0,0,560,400);c.fillStyle='#151724';c.fillRect(ox-B*scale,oy-B*scale,(W+2*B)*scale,(H+2*B)*scale);
 c.save();c.translate(ox,oy);c.scale(scale,scale);
 w.cells.forEach((cell,i)=>{const b=w.bodies[i];if(!b)return;c.fillStyle=b.isVoid?'#08090e':b.color;c.beginPath();for(const p of cell.pieces||[cell]){if(!p.pts.length)continue;c.moveTo(...p.pts[0]);for(const q of p.pts.slice(1))c.lineTo(...q);c.closePath();}c.fill();});
 c.fillStyle='#00000045';c.fillRect(0,0,W,H);c.strokeStyle='#ffffff';c.lineWidth=1.5/scale;c.setLineDash([7/scale,4/scale]);c.strokeRect(0,0,W,H);c.setLineDash([]);
 for(const r of h.bufferRoutes||[]){if(bfLevel(r,h.t)<.001)continue;const nodes=[r.taker,...r.nodes.map(n=>n.b)];c.strokeStyle='#ffffffa0';c.lineWidth=1.2/scale;c.beginPath();nodes.forEach((b,i)=>{i?c.lineTo(b.x,b.y):c.moveTo(b.x,b.y)});c.stroke();}
 c.font=`bold ${11/scale}px system-ui`;c.textAlign='center';c.textBaseline='middle';
 for(const b of h.bodies){if(b.isVoid||b.leaving)continue;c.fillStyle='#08090eaa';c.beginPath();c.arc(b.x,b.y,9/scale,0,Math.PI*2);c.fill();c.fillStyle='#fff';c.fillText(String(b.id+1),b.x,b.y);}
 c.restore();c.fillStyle='#bcc3d5';c.font='12px system-ui';c.textAlign='left';c.fillText('Dashed box: viewport. Dark exterior: unused reserve.',12,377);
 bfView.querySelector('#bf-caption').textContent=`Content outside ${fmt(h.bufferContentOutside)} px² · whitespace outside ${fmt(h.bufferVoidOutside)} px² · reserve ${fmt(h.bufferReserveArea)} px² · balance error ${(h.bufferLedgerError||0).toExponential(1)} px². Lines show active yielding routes.`;
}
const bfOriginalTick=tick;
tick=function(t){bfOriginalTick(t);bfDrawWorld();};
