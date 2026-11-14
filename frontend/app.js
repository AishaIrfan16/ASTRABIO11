const $=s=>document.querySelector(s),COL={normal:'#34D399',watch:'#FACC15',warning:'#FF7A3D',critical:'#EF4444'},
IC={normal:'✓',watch:'◆',warning:'▲',critical:'⚠'},LB={normal:'Normal',watch:'Watch',warning:'Warning',critical:'Critical'},
CH={stable:['Stable','✓','#34D399'],watch:['Watch','◆','#FACC15'],alert:['Alert','▲','#FF7A3D']},
NAV=[['home','⌂','Home'],['checkin','✎','Check-in'],['body','☍','Body Map'],['radiation','☢','Radiation'],['gravity','⇩','Gravity'],['immune','✚','Immune'],['mind','☾','MindSpace'],['habitat','▣','Habitat'],['companion','◉','Companion'],['research','⚗','Research']],
HZ=['all','radiation','gravity','immune','mind','habitat'],LAY=['skin','muscle','skeleton','organs','brain'],
CMDS=['How am I doing today?','Explain my radiation level','Show my body map','I feel lonely','Open my daily check-in'],
ORDER=l=>['normal','watch','warning','critical'].indexOf(l),phone=()=>innerWidth<900,SR=window.SpeechRecognition||window.webkitSpeechRecognition;
let S,day=142,screen='home',sel=null,flt='all',layer='skin',body=null,pulse=null,LOG=[],muted=false,rsel='legs',speaking=false,rec,wasPhone=phone();
const stChip=l=>`<span class="st" style="color:${COL[l]}; border-color:${COL[l]}33; background:${COL[l]}11">${IC[l]} ${LB[l]}</span>`,
modChip=c=>{const[a,b,k]=CH[c];return `<span class="st" style="color:${k}; border-color:${k}33; background:${k}11">${b} ${a}</span>`};
function chart(v,col,h=90){const mn=Math.min(...v),mx=Math.max(...v),r=(mx-mn)||1,p=v.map((y,i)=>`${i*(300/(v.length-1))},${h-8-(y-mn)/r*(h-24)}`).join(' ');
return `<svg viewBox="0 0 300 ${h}" width="100%"><defs><linearGradient id="grad_${col.replace('#','')}" x1="0%" y1="0%" x2="0%" y2="100%"><stop offset="0%" stop-color="${col}" stop-opacity="0.3"/><stop offset="100%" stop-color="${col}" stop-opacity="0"/></linearGradient></defs><polyline points="${p}" fill="none" stroke="${col}" stroke-width="3" stroke-linejoin="round" style="filter: drop-shadow(0 0 6px ${col})"/><text x="0" y="12" fill="#94A3B8" font-size="11" font-weight="500">${mx}</text><text x="0" y="${h-1}" fill="#94A3B8" font-size="11" font-weight="500">${mn}</text></svg>`}
const met=m=>`<div class="card"><h3>${m.label}</h3><div class="val">${m.value} <small>${m.unit}</small></div>${stChip(m.level)}${chart(m.series,COL[m.level])}<small style="color:var(--mut); display:block; margin-top:8px;">last 14 days</small></div>`;
function toast(t){const e=$('#toast');e.textContent=t;e.classList.add('show');setTimeout(()=>e.classList.remove('show'),2600)}

/* ---------- 3D body ---------- */
function mkBody(cv,o){
const W=cv.clientWidth||400,H=cv.clientHeight||400,r=new THREE.WebGLRenderer({canvas:cv,alpha:true,antialias:true});r.setPixelRatio(devicePixelRatio);r.setSize(W,H,false);
const sc=new THREE.Scene(),cam=new THREE.PerspectiveCamera(35,W/H,.1,50);cam.position.set(0,1.0,o.cz||5);cam.lookAt(0,.98,0);
sc.add(new THREE.AmbientLight(0x88aacc,1.2));const dl=new THREE.DirectionalLight(0x22D3EE,1.5);dl.position.set(2,3,4);sc.add(dl);
const pl=new THREE.PointLight(0xFF7A3D,1,10);pl.position.set(-2,1,2);sc.add(pl);
const root=new THREE.Group();sc.add(root);const L={};LAY.forEach(k=>{L[k]=new THREE.Group();root.add(L[k])});
const SG=new THREE.SphereGeometry(1,24,16),CG=new THREE.CylinderGeometry(1,1,1,20),mt=(c,op)=>new THREE.MeshStandardMaterial({color:c,transparent:true,opacity:op,roughness:.3,metalness:.2});
const add=(g,geo,m,x,y,z,sx,sy,sz)=>{const e=new THREE.Mesh(geo,m);e.position.set(x,y,z);e.scale.set(sx,sy,sz);g.add(e);return e};
const parts=(g,m,k)=>{add(g,SG,m,0,1.73,0,.12*k,.14*k,.13*k);add(g,CG,m,0,1.25,0,.21*k,.6,.13*k);add(g,SG,m,0,.93,0,.2*k,.12,.13*k);
[-1,1].forEach(s=>{add(g,CG,m,s*.11,.65,0,.085*k,.5,.085*k);add(g,CG,m,s*.11,.2,0,.065*k,.45,.065*k);add(g,CG,m,s*.3,1.28,0,.05*k,.55,.05*k)})};
const skinM=mt(0x22D3EE,.25);parts(L.skin,skinM,1);parts(L.muscle,mt(0xEF4444,.45),.8);
const bm=mt(0xF8FAFC,.85);add(L.skeleton,SG,bm,0,1.73,0,.095,.11,.1);add(L.skeleton,CG,bm,0,1.22,-.05,.02,.62,.02);
for(let i=0;i<4;i++)add(L.skeleton,SG,bm,0,1.5-i*.1,0,.17,.012,.1);add(L.skeleton,SG,bm,0,.93,0,.17,.07,.09);
[-1,1].forEach(s=>{add(L.skeleton,CG,bm,s*.11,.65,0,.03,.5,.03);add(L.skeleton,CG,bm,s*.11,.2,0,.025,.45,.025);add(L.skeleton,CG,bm,s*.3,1.28,0,.02,.55,.02);add(L.organs,SG,mt(0xF472B6,.75),s*.1,1.42,0,.07,.12,.06)});
add(L.organs,SG,mt(0xEF4444,.85),.07,1.4,.04,.05,.05,.05);add(L.organs,SG,mt(0xFB923C,.85),0,1.06,.03,.12,.09,.07);add(L.brain,SG,mt(0xF472B6,.9),0,1.74,0,.085,.085,.085);add(L.brain,SG,mt(0xF8FAFC,.15),0,1.73,0,.12,.14,.13);
function setLayer(k){layer=k;LAY.forEach(x=>L[x].visible=x==k||(k=='organs'&&x=='skeleton'));skinM.opacity=k=='skin'?.25:.06}
const mk=[];S.markers.forEach(m=>{const g=new THREE.Group();g.position.set(...m.pos);const c=new THREE.MeshBasicMaterial({color:0x34D399}),h=new THREE.MeshBasicMaterial({color:0x34D399,transparent:true,opacity:.3,blending:THREE.AdditiveBlending,depthWrite:false});
const a=new THREE.Mesh(new THREE.SphereGeometry(.04,16,12),c),b=new THREE.Mesh(new THREE.SphereGeometry(.14,16,12),h);b.userData.id=m.id;g.add(a,b);root.add(g);mk.push({m,g,c,h,a,b})});
function update(){mk.forEach(k=>{const m=S.markers.find(x=>x.id==k.m.id),col=new THREE.Color(COL[m.level]);k.m=m;k.c.color=col;k.h.color=col;k.g.visible=!o.filter||o.filter=='all'||m.hazards.includes(o.filter)})}
update();setLayer(o.layer||'skin');
let drag=0,mv=0,lx=0;cv.onpointerdown=e=>{drag=1;mv=0;lx=e.clientX;cv.setPointerCapture(e.pointerId)};
cv.onpointermove=e=>{if(drag){root.rotation.y+=(e.clientX-lx)*.01;mv+=Math.abs(e.clientX-lx);lx=e.clientX}};
cv.onpointerup=e=>{drag=0;if(mv<5&&o.onPick){const rc=cv.getBoundingClientRect(),v=new THREE.Vector2((e.clientX-rc.left)/rc.width*2-1,-(e.clientY-rc.top)/rc.height*2+1),ra=new THREE.Raycaster();ra.setFromCamera(v,cam);
const hit=ra.intersectObjects(mk.filter(k=>k.g.visible).map(k=>k.b))[0];if(hit)o.onPick(hit.object.userData.id)}};
let t=0,raf;(function loop(){raf=requestAnimationFrame(loop);t+=.016;if(o.auto&&!drag)root.rotation.y=Math.sin(t*.5)*.6;
mk.forEach((k,i)=>{const bad=k.m.level=='warning'||k.m.level=='critical',pu=pulse==k.m.id,s=pu?1.6+.5*Math.sin(t*10):bad?1.2+.2*Math.sin(t*4+i):1+.06*Math.sin(t*2+i);k.a.scale.setScalar(s);k.b.scale.setScalar(s*(k.m.id==sel?1.5:1))});r.render(sc,cam)})();
return{update,setLayer,filter:f=>{o.filter=f;update()},destroy(){cancelAnimationFrame(raf);r.dispose()}}}

/* ---------- screens ---------- */
const SC={};
const sideHTML=m=>`<div class="card side"><div class="row" style="justify-content:space-between"><b style="font-size:20px">${m.name}</b>${stChip(m.level)}</div><p style="margin:8px 0;color:var(--mut)">Affected by: ${m.hazards.join(', ')}</p><h3>${m.label}</h3><div class="val">${m.value} <small>${m.unit}</small></div>${chart(m.series,COL[m.level],60)}<p style="margin:10px 0; font-size: 14px;">${m.text}</p><div class="row" style="margin-top: 14px;"><button class="btn" onclick="ask('Tell me about my ${m.name}')">Ask ASTRA</button><button class="btn o" onclick="toast('Medical review requested (demo)')">Escalate review</button></div></div>`;
SC.home=()=>{const n=S.attention,al=Object.entries(S.modules).filter(([k,m])=>m.chip=='alert').map(([k])=>k);
return `${S.rad.spe?`<div class="card warn" style="margin-bottom:16px">⚠ <b>Space weather alert.</b> ${S.rad.spe_text}</div>`:''}<div class="hero"><div class="orbw"><div class="orb ${speaking?'sp':''}" id="orb"></div></div>
<h1>Good morning. ${n?'Some items need attention.':'Your overall status is stable.'}</h1>
<p style="color:var(--mut);margin:0;max-width:560px">Tracks an astronaut's health on a long Mars mission and warns early when something changes.</p>
<div class="row"><span class="badge">Health score ${S.checkin.score}/100</span><span class="badge d">🔥 ${S.checkin.streak}-day streak</span></div>
<p style="color:var(--mut);margin:0">${n?`${n} item${n>1?'s':''} require${n>1?'':'s'} attention.`:'All monitored parameters nominal.'} ${al.length?'Critical flags: '+al.join(', ')+'.':''}</p>
<div class="chips" style="justify-content:center">${CMDS.map(c=>`<button class="cmd" onclick="ask('${c}')">“${c}”</button>`).join('')}</div></div>
${nba()}<div class="grid2"><div class="card" style="height:340px;padding:6px"><canvas class="b" id="cv"></canvas></div><div style="align-self:center">${remCard()}</div></div>
<div class="mods">${Object.entries(S.modules).map(([k,m])=>`<div class="card mod" style="border-top:2px solid ${CH[m.chip][2]}" onclick="go('${k}')"><span style="font-size:24px">${NAV.find(n=>n[0]==k)?.[1]||''}</span><b style="font-size: 15px;">${k[0].toUpperCase()+k.slice(1)}</b>${modChip(m.chip)}</div>`).join('')}</div>
<div class="chips"><span style="color:var(--mut);font-size:13px">Demo:</span><button class="f" onclick="demo(20)">Normal day</button><button class="f" onclick="demo(142)">Solar storm</button><button class="f" onclick="demo(60,{hr:118,sleep:5,mood:4})">Health warning</button></div>
<p class="hint" style="text-align:center">Prototype with simulated data. Health ranges are placeholders until reviewed by NASA HRP or a flight surgeon.</p>`};
SC.body=()=>{const m=S.markers.find(x=>x.id==sel);
return `<div class="chips" style="margin-top:0">${HZ.map(h=>`<button class="f ${flt==h?'on':''}" onclick="flt='${h}';body.filter('${h}');go('body',1)">${h[0].toUpperCase()+h.slice(1)}</button>`).join('')}<span style="flex:1"></span>${LAY.map(l=>`<button class="f ${layer==l?'on':''}" onclick="body.setLayer('${l}');go('body',1)">${l[0].toUpperCase()+l.slice(1)}</button>`).join('')}</div>
<div class="card tr" style="padding:6px"><canvas class="b" id="cv"></canvas>${m?sideHTML(m):'<div class="hint" style="position:absolute;top:16px;left:50%;transform:translateX(-50%);pointer-events:none">Tap a glowing dot to see details</div>'}
<div style="position:absolute;left:20px;bottom:16px;color:var(--mut);font-size:13px; font-weight: 500; background: rgba(3,7,18,0.6); padding: 6px 14px; border-radius: 99px; border: 1px solid var(--glass-border); backdrop-filter: blur(8px);">${['normal','watch','warning','critical'].map(l=>`<span style="color:${COL[l]}">${IC[l]} ${LB[l]}</span>`).join(' &nbsp;·&nbsp; ')} &nbsp;·&nbsp; drag to rotate, tap marker</div></div>
<div class="card" style="margin-top:16px"><div class="row" style="justify-content:space-between"><b>Mission day ${day} of ${S.total}</b><span id="cap" style="color:var(--cy); font-weight: 500;">“${LOG.filter(x=>x.n).slice(-1)[0]?.t||'Tap a marker or ask ASTRA about your body.'}”</span></div><input type="range" min="1" max="${S.total}" value="${day}" oninput="loadDay(+this.value)"></div>`};
function mod(k){const M=S.modules[k],R=S.rad;let x='';
if(k=='radiation'){const p=Math.min(1,M.metrics[0].value/R.limit);x=(R.spe?`<div class="card warn">⚠ <b>Space weather alert.</b> ${R.spe_text}</div>`:'')+`<div class="card row" style="align-items: center; justify-content: space-around;"><svg viewBox="0 0 200 115" width="220"><path d="M10 100A90 90 0 0 1 190 100" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="16" stroke-linecap="round"/><path d="M10 100A90 90 0 0 1 190 100" fill="none" stroke="${p>.75?COL.warning:p>.5?COL.watch:COL.normal}" stroke-width="16" stroke-linecap="round" stroke-dasharray="${p*283} 283" style="filter:drop-shadow(0 0 8px currentColor)"/><text x="100" y="86" text-anchor="middle" fill="#fff" font-size="28" font-weight="700">${Math.round(p*100)}%</text><text x="100" y="108" text-anchor="middle" fill="#94A3B8" font-size="11" font-weight="500">${M.metrics[0].value} of ${R.limit} mSv</text></svg><div><h3>Mars Transit vs Surface</h3>Transit: <b style="color:var(--tx);">${M.metrics[1].value} mSv/d</b><br>Surface: <b style="color:var(--tx);">${M.metrics[2].value} mSv/d</b></div></div>`}
if(k=='gravity')x=`<div class="card"><h3>Exercise adherence (last 7 days)</h3><div class="dots" style="margin: 12px 0;">${S.adherence.map(a=>`<i style="background:${a?COL.normal:COL.warning};color:#030712">${a?'✓':'✕'}</i>`).join('')}</div><p style="font-weight: 500;">${S.adherence.filter(a=>a).length} of 7 mandatory sessions completed</p></div>`;
if(k=='immune'){const v=M.metrics[3].value;x=`<div class="card"><h3>Infection risk index</h3><div class="bar"><b style="width:${v*2}%;background:${COL[M.metrics[3].level]}"></b></div><div class="row" style="justify-content: space-between; margin-top: 8px;"><span style="font-weight:700; font-size:18px;">${v}%</span>${stChip(M.metrics[3].level)}</div></div>`}
if(k=='mind')x=`<div class="card"><h3>Calming protocols</h3><div class="row"><button class="cmd" onclick="ask('Breathing exercise')">🫁 Breathing</button><button class="cmd" onclick="ask('Play music')">♫ Spatial Audio</button><button class="cmd" onclick="go('companion')">☎ Comms Link</button></div></div>`;
const cut=`<svg viewBox="0 0 320 200" width="100%"><rect x="10" y="40" width="300" height="120" rx="60" fill="rgba(3,7,18,0.7)" stroke="rgba(34,211,238,0.3)" stroke-width="2"/>${[['Crew',50,'normal'],['Lab',130,'watch'],['Sleep pods',210,'watch'],['Greenhouse',275,'normal']].map(([n,cx,l])=>`<rect x="${cx-35}" y="70" width="70" height="60" rx="12" fill="${COL[l]}15" stroke="${COL[l]}"/><text x="${cx}" y="105" text-anchor="middle" fill="#fff" font-size="11" font-weight="600">${n}</text><text x="${cx}" y="124" text-anchor="middle" fill="${COL[l]}" font-size="11">${IC[l]}</text>`).join('')}</svg>`;
return `<div class="row" style="justify-content:space-between"><div class="row"><h2>${M.title}</h2>${modChip(M.chip)}</div><button class="btn" onclick="ask('${M.ask}')">🎙 ${M.askLabel}</button></div>
<div class="mgrid"><div class="col">${x}<div class="metrics">${M.metrics.map(met).join('')}</div>${k=='habitat'?`<div class="card"><h3>Anomaly alerts</h3>${M.anomalies.map(a=>`<p style="margin:4px 0;">▲ ${a}</p>`).join('')||'None detected'}</div>`:''}</div>
<div class="col"><div class="card" style="${k=='habitat'?'':'height:340px;padding:6px'}">${k=='habitat'?'<h3>Habitat schematic</h3>'+cut:'<canvas class="b" id="cv"></canvas>'}</div><div class="card ins"><h3>AI diagnostic insight</h3><p style="margin:0; font-size:14px; line-height: 1.5;">${M.insight}</p></div></div></div>`}
['radiation','gravity','immune','mind','habitat'].forEach(k=>SC[k]=()=>mod(k));
SC.companion=()=>`<div class="row" style="align-items:flex-start;flex-wrap:nowrap"><div class="orb sm ${speaking?'sp':''}" id="orb"></div><div class="card chat" id="chat" style="flex:1">${LOG.map(b=>`<div class="bub ${b.n?'':'u'}">${b.t}</div>`).join('')||'<div class="bub">Greetings Commander Amara. ASTRA secure channel active. How are you feeling today?</div>'}</div></div>
<div class="chips" style="margin-top: 16px;">${['Explain my status','I feel lonely','Play music','Breathing exercise','Tell me a story','Messages from home','Play a game'].map(c=>`<button class="cmd" onclick="ask('${c}')">${c}</button>`).join('')}</div>
<div class="card" style="margin-top: 16px;"><h3>Messages from home</h3>${S.messages.map(m=>`<p style="margin:6px 0">${m}</p>`).join('')}</div>
<div class="card ins" style="margin-top: 16px;"><b>External Communication Link</b><div class="row" style="margin-top:10px"><button class="btn" onclick="toast('Calling Earth Mission Control… 12 min light-speed delay (demo)')">Direct to Earth</button><button class="btn o" onclick="toast('Pinging habitat crewmate (demo)')">Inter-module Comms</button></div></div>`;
SC.research=()=>{const m=S.markers.find(x=>x.id==rsel),E={Strong:'●●●',Moderate:'●●○',Emerging:'●○○'};
return `<h2>Countermeasure research repository</h2><div class="chips">${S.markers.map(x=>`<button class="f ${rsel==x.id?'on':''}" onclick="rsel='${x.id}';go('research',1)">${x.name}</button>`).join('')}</div>
<div class="card warn" style="margin-bottom:14px">Informational research database only. Not a medical prescription.</div>
<div class="metrics">${m.hazards.flatMap(h=>S.counter[h].map(c=>({h,c}))).map(({h,c})=>`<div class="card"><h3>${h}</h3><b style="font-size:18px; color:var(--tx);">${c[0]}</b><p style="margin:8px 0 4px;"><span class="ev">${E[c[1]]} ${c[1]} evidence</span></p><p style="color:var(--mut); margin:0;">Safety profile: ${c[2]}</p></div>`).join('')}</div>`};

/* ---------- daily check-in ---------- */
const remCard=()=>{const C=S.checkin;return `<div class="card ${C.due.length?'warn':''}"><div class="row" style="justify-content:space-between"><div><b style="font-size: 16px;">Daily check-in: ${C.items.length-C.due.length} of ${C.items.length} logged</b><div style="color:var(--mut); margin-top:2px;">${C.due.length?'Pending metrics: '+C.due.join(', '):'All metrics logged successfully. Streak: '+C.streak+' days.'}</div></div><button class="btn" onclick="go('checkin')">Open Check-in</button></div></div>`},
nba=()=>{const w=S.checkin.items.reduce((a,b)=>ORDER(b.level)>ORDER(a.level)?b:a),ok=w.level=='normal';return `<div class="card ${ok?'ins':'warn'}" style="margin-bottom:16px"><h3>Next best action</h3><b>${ok?'All check-in values are normal.':w.label+' is '+w.level+'.'}</b><p style="margin:4px 0 0">${w.action}</p>${w.escalate?'<button class="btn o" style="margin-top:10px" onclick="toast(\'Flight surgeon notified (demo)\')">Contact flight surgeon</button>':''}</div>`};
SC.checkin=()=>{const C=S.checkin;
const card=i=>`<div class="card"><div class="row" style="justify-content:space-between"><h3>${i.label}</h3>${stChip(i.level)}</div><div class="val">${i.value} <small>${i.unit}</small></div>${chart(i.series,COL[i.level])}<p style="margin:8px 0 4px"><small style="color:var(--mut)">${i.logged?'Logged today':'Pending today'} · baseline ${i.baseline} (${i.dev>0?'+':''}${i.dev}%)</small></p><p style="margin:4px 0 10px"><b>Protocol:</b> ${i.action}</p><details><summary style="cursor:pointer;color:var(--cy); font-weight: 500;">Methodology &amp; Context</summary><p style="margin-top:6px;"><b>Orbital relevance:</b> ${i.why}</p><p><b>Measurement:</b> ${i.how}</p><p style="color:var(--mut); margin-bottom:0;">Normal parameters: ${i.n[0]}–${i.n[1]} ${i.unit}. ${i.src}</p></details>${i.escalate?'<button class="btn o" style="margin-top:12px;" onclick="toast(\'Flight surgeon notified (demo)\')">Contact flight surgeon</button>':''}</div>`;
return `<div class="row" style="justify-content:space-between"><h2>Daily Physiological Check-in</h2><div class="row"><span class="st" style="color:var(--cy); border-color:rgba(34,211,238,0.3); background:rgba(34,211,238,0.08)">Health Score ${C.score}/100</span><span class="st" style="color:var(--yl); border-color:rgba(250,204,21,0.3); background:rgba(250,204,21,0.08)">🔥 ${C.streak}-Day Streak</span></div></div>
<div class="card warn" style="margin:16px 0">Clinical guidance telemetry only, not an automated medical diagnosis. Demo parameters active.</div>
${C.escalate?'<div class="card warn" style="margin-bottom:16px">▲ <b>Critical marker deviation detected.</b> Immediate flight surgeon consultation recommended.</div>':''}
<div class="card"><div class="row" style="justify-content:space-between"><h3>Input Today's Telemetry</h3><button class="cmd" onclick="dictateCheckin()">🎙 Dictate readings</button></div><p style="color:var(--mut);margin:0">Say, for example: “heart rate 72, blood pressure 120 over 80, sleep 7 hours.” Review the fields, then save.</p><div id="voiceStatus" role="status" style="color:var(--cy);margin-top:8px"></div><div class="metrics" style="margin-top:12px">${C.items.map(i=>`<label>${i.label} (${i.unit})<input id="in_${i.key}" type="number" step="any" placeholder="${i.value}" class="ti" onkeydown="if(event.key=='Enter')submitCheckin()"></label>`).join('')}</div><div class="row" style="margin-top:16px"><button class="btn" onclick="submitCheckin()">Save Telemetry</button><button class="f" onclick="resetCheckin()">Reset Demo State</button></div><div id="cerr" style="color:var(--or);margin-top:8px; font-weight:500;"></div></div>
<div class="metrics" style="margin-top:16px">${C.items.map(card).join('')}</div>`};
async function submitCheckin(){const v={};document.querySelectorAll('.ti').forEach(e=>{if(e.value!=='')v[e.id.slice(3)]=e.value});
if(!Object.keys(v).length)return toast('Please enter at least one metric value');
const j=await (await fetch('/api/checkin',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({values:v})})).json();
S=await (await fetch('/api/state?day='+day)).json();render();
if(j.errors&&j.errors.length){for(const k in v){const e=$('#in_'+k);if(e)e.value=v[k]}$('#cerr').textContent=j.errors.join(' ');return}toast('Telemetry saved successfully');
const w=S.checkin.items.find(i=>i.escalate);if(w)say('Your '+w.label.toLowerCase()+' is '+w.level+'. '+w.action)}
async function parseCheckinVoice(text){const st=$('#voiceStatus');
try{const res=await fetch('/api/checkin/parse',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text})}),j=await res.json();
if(!res.ok){st.textContent=(j.errors||['Could not parse the readings.']).join(' ');return}
Object.entries(j.values).forEach(([k,v])=>{const i=$('#in_'+k);if(i)i.value=v});$('#cerr').textContent='';
const lb=Object.fromEntries(S.checkin.items.map(i=>[i.key,i.label]));
st.textContent='Readings entered: '+Object.keys(j.values).map(k=>lb[k]||k).join(', ')+'. Review them, then save.'}
catch(e){st.textContent='Could not process voice entry: '+e.message}}
function dictateCheckin(){const st=$('#voiceStatus');
if(!SR){st.textContent='Speech recognition is not supported in this browser. You can enter readings below.';return}
if(rec){rec.stop();return}
let txt='',failed=false;rec=new SR();rec.lang='en-US';rec.interimResults=true;
$('#mic').classList.add('on');$('#wave').classList.add('on');st.textContent='Listening for measurements…';
rec.onresult=e=>{const r=[...e.results],f=r.filter(x=>x.isFinal);st.textContent='Listening… '+r.map(x=>x[0].transcript).join(' ');if(f.length)txt=f.map(x=>x[0].transcript).join(' ')};
rec.onerror=e=>{failed=true;st.textContent='Voice entry failed: '+e.error};
rec.onend=()=>{rec=null;$('#mic').classList.remove('on');if(!speaking)$('#wave').classList.remove('on');
if(!failed&&txt.trim())parseCheckinVoice(txt.trim());else if(!failed)st.textContent='No speech detected. Try again or enter readings below.'};
try{rec.start()}catch(e){rec=null;$('#mic').classList.remove('on');$('#wave').classList.remove('on');st.textContent='Could not start voice entry: '+e.message}}
async function resetCheckin(){await fetch('/api/checkin/reset',{method:'POST'});S=await (await fetch('/api/state?day='+day)).json();render();toast('Demo state reset')}

/* ---------- control ---------- */
async function demo(d,vals){await fetch('/api/checkin/reset',{method:'POST'});
if(vals)await fetch('/api/checkin',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({values:vals})});
day=d;S=await (await fetch('/api/state?day='+d)).json();go('home');
const w=S.checkin.items.find(i=>i.escalate);if(S.rad.spe)say(S.rad.spe_text);else if(w)say('Your '+w.label.toLowerCase()+' is '+w.level+'. '+w.action)}
function go(s,keep){screen=s;if(phone())$('#app').classList.add('collapsed');if(body){body.destroy();body=null}render();if(!keep)$('#main').animate([{opacity:0,transform:'translateY(14px)'},{opacity:1,transform:'none'}],{duration:400,easing:'ease-out'})}
function render(){$('#who').textContent=S.astronaut;$('#dn').textContent='Mission day '+day+' / '+S.total;$('#rail').innerHTML=NAV.map(([k,i,l])=>{const c=S.modules[k]?.chip,x=c&&c!='stable'?CH[c][2]:'';return `<button class="${screen==k?'on':''}" onclick="go('${k}')"><i>${i}</i>${l}${x?`<b class="dot" style="background:${x};box-shadow:0 0 8px ${x}"></b>`:''}</button>`}).join('');
$('#main').innerHTML=SC[screen]();const cv=$('#cv');if(cv){const hz=['radiation','gravity','immune','mind'].includes(screen)?screen:flt;
body=mkBody(cv,screen=='home'?{auto:1,cz:5.4}:screen=='body'?{filter:flt,layer,onPick:id=>{sel=id;go('body',1)}}:{filter:hz,cz:5.2,auto:1})}
const c=$('#chat');if(c)c.scrollTop=1e9}
async function loadDay(d){const old=S;day=d;S=await (await fetch('/api/state?day='+d)).json();$('#dn').textContent='Mission day '+day+' / '+S.total;
const w=S.markers.find((m,i)=>ORDER(m.level)>ORDER(old.markers[i].level));
if(body){body.update();body.filter(flt)}if(w){pulse=w.id;const t=`Anomaly alert: your ${w.name.toLowerCase()} is now ${w.level}. ${w.label}: ${w.value} ${w.unit}.`;const b=$('#bn');b.textContent='▲ '+t;b.classList.add('show');setTimeout(()=>{b.classList.remove('show');pulse=null},5000);say(t)}
const sd=document.querySelector('.side');if(sd&&sel)sd.outerHTML=sideHTML(S.markers.find(x=>x.id==sel));if(screen!='body'&&screen!='home')render()}
function say(t){LOG.push({n:1,t});const tt=$('#tt');tt.textContent='ASTRA transmitting… '+t;const c=$('#cap');if(c)c.textContent='“'+t+'”';
speaking=true;$('#wave').classList.add('on');document.querySelectorAll('.orb').forEach(o=>o.classList.add('sp'));
const end=()=>{speaking=false;$('#wave').classList.remove('on');document.querySelectorAll('.orb').forEach(o=>o.classList.remove('sp'));tt.textContent='ASTRA is ready'};
if(!muted&&'speechSynthesis' in window){speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(t);u.onend=end;u.onerror=end;speechSynthesis.speak(u)}else setTimeout(end,Math.min(6000,t.length*45));
const ch=$('#chat');if(ch){ch.insertAdjacentHTML('beforeend',`<div class="bub">${t}</div>`);ch.scrollTop=1e9}}
async function ask(text){text=text.replace(/^hey astra[, ]*/i,'');LOG.push({n:0,t:text});const ch=$('#chat');if(ch)ch.insertAdjacentHTML('beforeend',`<div class="bub u">${text}</div>`);
const r=await (await fetch('/api/astra',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text,day})})).json();
S=await (await fetch('/api/state?day='+day)).json();if(r.select)sel=r.select;if(r.nav&&r.nav!=screen)go(r.nav);else if(r.select)go('body',1);else if(r.nav=='checkin')render();say(r.reply)}

/* ---------- events and start ---------- */
$('#ti').onkeydown=e=>{if(e.key=='Enter'&&e.target.value.trim()){ask(e.target.value.trim());e.target.value=''}};
$('#mute').onclick=()=>{muted=!muted;$('#mute').innerHTML=muted?'🔇<span class="lb"> Voice off</span>':'🔊<span class="lb"> Voice on</span>';if(muted)speechSynthesis.cancel()};
$('#wave').innerHTML='<i></i>'.repeat(26);document.querySelectorAll('#wave i').forEach((e,i)=>e.style.animationDelay=(i*.05)+'s');
$('#mic').onclick=()=>{if(!SR)return toast('Speech recognition unsupported. Type message instead.');if(rec){rec.stop();return}
rec=new SR();rec.lang='en-US';rec.interimResults=true;$('#mic').classList.add('on');$('#wave').classList.add('on');$('#tt').textContent='Listening…';
rec.onresult=e=>{const t=[...e.results].map(r=>r[0].transcript).join('');$('#tt').textContent='Listening… '+t;if(e.results[0].isFinal)ask(t)};
rec.onend=()=>{rec=null;$('#mic').classList.remove('on');if(!speaking)$('#wave').classList.remove('on')};rec.start()};
$('#hamburger').onclick=()=>{$('#app').classList.toggle('collapsed');dispatchEvent(new Event('resize'))};
$('#app').classList.toggle('collapsed',wasPhone);addEventListener('resize',()=>{if(phone()!=wasPhone){wasPhone=phone();$('#app').classList.toggle('collapsed',wasPhone)}});
fetch('/api/state?day='+day).then(r=>r.json()).then(s=>{S=s;render()},()=>{$('#main').innerHTML='<div class="hero"><h2>Can’t reach ASTRABIO</h2><p style="color:var(--mut);margin:0">The server is not answering. Check that it is running, then try again.</p><button class="btn" onclick="location.reload()">Try again</button></div>'});
addEventListener('unhandledrejection',()=>toast('Something went wrong. Please try again.'));
$('#enter').onclick=()=>$('#intro').classList.add('out');