#!/usr/bin/env node
'use strict';
/* AuxFarma dashboard auditor — READ-ONLY. Node >=16, sem dependências.
   uso: node audit_dashboards.js [dir] */
const fs = require('fs'), path = require('path'), vm = require('vm');

const DIR = process.argv[2] || '/workspace/output';
const NAMES = (process.argv.length > 3 ? process.argv.slice(3) : [
  'dashboard-auxfarmacia.html','dashboard-auxfarmacia-FREE.html','dashboard-auxfarmacia-PRO.html',
  'dashboard-auxfarmacia-PREMIUM.html','dashboard-auxfarmacia-ENTERPRISE.html',
  'dashboard-auxfarmacia-educativo.html']).filter(n => /\.html$/.test(n));

const G = new Set(('if for while switch catch return typeof function new do else await yield delete void in of instanceof try finally case default break continue var let const class super this import export throw debugger parseInt parseFloat isNaN isFinite String Number Boolean Array Object JSON Math Date RegExp Error TypeError RangeError console setTimeout setInterval clearTimeout clearInterval requestAnimationFrame cancelAnimationFrame alert confirm prompt structuredClone encodeURIComponent decodeURIComponent Intl Symbol Promise Map Set WeakMap WeakSet Proxy Reflect BigInt localStorage sessionStorage document window navigator history location fetch Headers FormData URL URLSearchParams Blob File FileReader TextDecoder TextEncoder AbortController CustomEvent Event EventTarget MutationObserver ResizeObserver IntersectionObserver performance crypto atob btoa queueMicrotask matchMedia getComputedStyle scrollTo scrollBy open close focus blur click addEventListener removeEventListener dispatchEvent querySelector querySelectorAll getElementById getElementsByClassName getElementsByTagName createElement appendChild removeChild remove replaceWith insertAdjacentHTML setAttribute getAttribute hasAttribute removeAttribute closest contains toFixed toString valueOf hasOwnProperty find filter map forEach reduce some every sort splice push pop shift unshift slice concat join indexOf includes startsWith endsWith trim split replace padStart padEnd repeat charAt substring substr toUpperCase toLowerCase keys values entries assign freeze fromEntries isArray parse stringify now random min max abs round floor ceil sqrt pow log exp sin cos tan atan2 hypot cbrt trunc sign log10 log2 require module exports __dirname __filename process Buffer globalThis Image Option NodeList HTMLCollection DOMParser XMLHttpRequest Notification getSelection Range Selection postMessage onmessage onclick onload onerror onchange oninput scrollIntoView requestIdleCallback').split(/\s+/));

const FIND = [];
const add = (sev, file, line, kind, desc, repro, fix) => FIND.push({sev,file,line,kind,desc,repro,fix});
const REV = [];

function lineIndex(src){ const s=[0]; for(let i=0;i<src.length;i++) if(src[i]==='\n') s.push(i+1);
  return idx=>{let lo=0,hi=s.length-1;while(lo<hi){const m=(lo+hi+1)>>1;if(s[m]<=idx)lo=m;else hi=m-1;}return lo+1;};}

function mask(code){const o=code.split('');let i=0,m=null;const n=code.length;
  while(i<n){const c=code[i],d=code[i+1];
    if(!m){ if(c==='/'&&d==='/'){o[i]=' ';o[i+1]=' ';i+=2;continue;}
      if(c==='/'&&d==='*'){o[i]=' ';o[i+1]=' ';i+=2;continue;}
      if(c==='"'||c==="'"||c==='`'){m=c;o[i]=' ';i++;continue;} i++; continue; }
    if(m==='`'){ if(c==='\\'){o[i]=' ';if(i+1<n)o[i+1]=code[i+1]==='\n'?'\n':' ';i+=2;continue;}
      if(c==='`'){o[i]=' ';m=null;i++;continue;}
      // dentro de template literal: preserva apenas ${ ... }
      if(c==='$'&&code[i+1]==='{'){o[i]='$';o[i+1]='{';i+=2;let d=1;while(i<n&&d>0){const ch=code[i];
        if(ch==='{')d++;else if(ch==='}')d--;
        o[i]=d===0?'}':ch;i++;} continue;}
      o[i]=c==='\n'?'\n':' ';i++;continue; }
    if(c==='\\'){o[i]=' ';if(i+1<n)o[i+1]=code[i+1]==='\n'?'\n':' ';i+=2;continue;}
    if(c===m){o[i]=' ';m=null;i++;continue;} o[i]=c==='\n'?'\n':' ';i++;}
  return o.join('');}

function matchPair(mk, open, o, c){let d=0;for(let i=open;i<mk.length;i++){const ch=mk[i];
  if(ch===o)d++; else if(ch===c){d--;if(!d)return i;}} return -1;}

function analyze(file){
  const p = path.join(DIR,file);
  if(!fs.existsSync(p)){console.error('AUSENTE: '+file);return;}
  const src = fs.readFileSync(p,'utf8'), lineAt = lineIndex(src);
  const blocks=[], externals=[];
  const sre=/<script\b([^>]*)>([\s\S]*?)<\/script>/gi; let m;
  while((m=sre.exec(src))){ const attrs=m[1]||'', code=m[2];
    const abs=m.index+m[0].length-code.length;
    if(/\bsrc\s*=/i.test(attrs)) externals.push(attrs.trim()); else blocks.push({attrs,code,abs}); }

  const defs=new Map(), calls=[];
  blocks.forEach(b=>{
    const mk=mask(b.code);
    let re,x;
    re=/\bfunction\s*\*?\s*([A-Za-z_$][\w$]*)\s*\(/g;
    while((x=re.exec(mk))) defs.set(x[1],{line:lineAt(b.abs+x.index)});
    re=/\b([A-Za-z_$][\w$]*)\s*=\s*(?:async\s+)?(?:function\b|\(|[A-Za-z_$][\w$]*\s*=>)/g;
    while((x=re.exec(mk))) if(!G.has(x[1])&&!defs.has(x[1])) defs.set(x[1],{line:lineAt(b.abs+x.index)});
    re=/\b(?:var|let|const)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?(?:function\b|\(|[A-Za-z_$][\w$]*\s*=>)/g;
    while((x=re.exec(mk))) defs.set(x[1],{line:lineAt(b.abs+x.index)});
    re=/(?:^|[,{;\n]\s*)([A-Za-z_$][\w$]*)\s*\([^;{}]*\)\s*\{/g;
    while((x=re.exec(mk))){const nm=x[1];
      if(['if','for','while','switch','catch','function','return','typeof','do','else','try','with'].includes(nm))continue;
      if(!G.has(nm)&&!defs.has(nm)) defs.set(nm,{line:lineAt(b.abs+x.index)});}
    re=/(?<![.\w$])([A-Za-z_$][\w$]*)\s*\(/g;
    while((x=re.exec(mk))){ const nm=x[1],pos=x.index,before=mk.slice(Math.max(0,pos-16),pos);
      if(/\bfunction\s*\*?\s*$/.test(before)) continue;
      if(/\b(?:var|let|const)\s*$/.test(before)) continue;
      if(G.has(nm)) continue;
      calls.push({nm,line:lineAt(b.abs+pos)}); }
  });

  const undef=new Map();
  calls.forEach(c=>{ if(!defs.has(c.nm)){ if(!undef.has(c.nm)) undef.set(c.nm,{line:c.line,n:0}); undef.get(c.nm).n++; }});
  for(const [nm,o] of undef) add('ALTA',file,o.line,'função-inexistente',
    `\`${nm}()\` é chamada ${o.n}x mas não há definição em nenhum <script> do arquivo.`,
    `Abrir console → chamar ${nm}() → ReferenceError${externals.length?' (scripts externos: '+externals.join(', ')+')':''}.`,
    `Definir a função ou corrigir o nome da chamada.`);

  const CSS_FN=new Set(['translateY','translateX','translate','rotate','scale','scaleX','scaleY','rgba','rgb','hsl','cubicBezier','calc','var','clamp','min','max','blur','grayscale','brightness','contrast','skew','perspective','matrix','translate3d','scale3d','rotate3d','linear-gradient','radial-gradient','repeating-linear-gradient','repeating-radial-gradient','conic-gradient','steps','cubic-bezier','translateZ','perspective']);
  const hre=/(?:^|[\s"'])on([a-z]+)\s*=\s*(?:"([^"]*)"|'([^']*)')/gim;
  while((m=hre.exec(src))){ const body=m[2]!==undefined?m[2]:(m[3]||''); const ev=m[1];
    const cre=/(?<![.\w$])([A-Za-z_$][\w$]*)\s*\(/g; let c;
    while((c=cre.exec(body))){ const nm=c[1];
      if(G.has(nm)||defs.has(nm)) continue;
      if(CSS_FN.has(nm)) continue;
      add('CRÍTICA',file,lineAt(m.index),'handler-quebrado',
        `atributo on${ev}="${body.trim().slice(0,80)}" invoca \`${nm}\` que não existe no arquivo.`,
        `Clicar no elemento → ReferenceError: ${nm} is not defined.`,
        `Corrigir o nome ou implementar ${nm}();`); } }

  const wmUse=/window\.meds/.test(src);
  if(wmUse && !/window\.meds\s*=/.test(src)) add('CRÍTICA',file,1,'window.meds-nunca-atribuido',
    '`window.meds` é lido mas nunca atribuído.','Qualquer código que leia window.meds.length em carga inicial → TypeError/undefined.','Atribuir `window.meds = meds`.');

  blocks.forEach(b=>{ const mk=mask(b.code);
    const iire=/\(\s*(?:function\s*\(\s*\)|\(\s*\))\s*(?:::[^{]*)?\{/g; let x;
    while((x=iire.exec(mk))){ const open=mk.indexOf('{',x.index); if(open<0)continue;
      const close=matchPair(mk,'{','}',open); if(close<0)continue;
      const inner=mk.slice(open+1,close);
      const dre=/\b(?:var|let|const)\s+([A-Za-z_$][\w$]*)/g; let d;
      while((d=dre.exec(inner))){ const nm=d[1];
        if(G.has(nm))continue;
        const outside=new RegExp('(?<![.\\w$])'+nm.replace(/\$/g,'\\$')+'\\b');
        const m2=outside.exec(mk);
        if(m2 && !(m2.index>open && m2.index<close)){
          add('ALTA',file,lineAt(b.abs+m2.index),'escopo-IIFE',
            `\`${nm}\` declarado dentro de IIFE (linha ${lineAt(b.abs+open)}) mas usado fora → ReferenceError.`,
            `Executar o trecho que usa ${nm} fora da IIFE → ReferenceError.`,
            `Expor via window.` + nm + ` = ` + nm + ` ou mover a declaração.`);
        }
      }
    }
  });

  const lre=/localStorage\.(getItem|setItem|removeItem)\s*\(\s*(['"])([^'"]*)\2\s*\)/g;
  while((m=lre.exec(src))){ if(m[1]!=='getItem')continue;
    const end=m.index+m[0].length, tail=src.slice(end,end+220);
    const stop=tail.search(/[;\n]/); const stmt=stop>=0?tail.slice(0,stop):tail;
    if(/^\s*[.\[]/.test(stmt)) add('ALTA',file,lineAt(m.index),'localStorage-sem-guarda',
      `localStorage.getItem('${m[3]}') dereferenciado sem checar null → TypeError.`,
      `DevTools → localStorage.removeItem('${m[3]}') → recarregar → TypeError.`,
      `const v = localStorage.getItem('${m[3]}') || '';`); }

  const jp=/JSON\.parse\(\s*localStorage\.getItem\([^)]*\)\s*\)\s*[.\[]/g;
  while((m=jp.exec(src))) add('ALTA',file,lineAt(m.index),'localStorage-json-null',
    'JSON.parse(localStorage.getItem(...))PPPderivado — chave ausente devolve null e o acesso quebra.',
    `localStorage.removeItem(<chave>) + reload → TypeError: Cannot read properties of null.`,
    `const raw = localStorage.getItem(k); const o = raw ? JSON.parse(raw) : null;`);

  const ae=/([A-Za-z_$][\w$]*(?:\s*\.\s*[A-Za-z_$][\w$]*|\s*\[\s*['"][^'"]+['"]\s*\])*)\s*\.\s*addEventListener\s*\(\s*(['"])([^'"]+)\2\s*,\s*([A-Za-z_$][\w$]*|[A-Za-z_$][\w$]*\([^()]*\))/g;
  const seen=new Map(); const pair=new Map();
  while((m=ae.exec(src))){ const t=m[1].replace(/\s+/g,''), ev=m[3], h=m[4].replace(/\s+/g,'');
    const k=t+'|'+ev+'|'+h; if(!seen.has(k)) seen.set(k,{line:lineAt(m.index),n:0}); seen.get(k).n++;
    const k2=t+'|'+ev; if(!pair.has(k2)) pair.set(k2,{line:lineAt(m.index),h:new Set()}); pair.get(k2).h.add(h); }
  for(const [k,o] of seen) if(o.n>1) add('ALTA',file,o.line,'listener-duplicado',
    `addEventListener registrado ${o.n}x com mesmo alvo/evento/handler (${k}) → double-fire.`,
    `Disparar o evento → handler roda ${o.n}x.`,
    `Registrar uma única vez.`);
  for(const [k,o] of pair) if(o.h.size>1) add('MÉDIA',file,o.line,'listener-conflitante',
    `mesmo alvo+evento (${k}) com handlers diferentes → ambos executam.`,
    `Dois handlers rodam, um pode sobrescrever o estado do outro.`,
    `Unificar em um único handler.`);

  const nl=/((?:document|window)\s*\.\s*getElementById\s*\([^)]*\)|(?:document\s*\.\s*)?querySelector(?:All)?\s*\([^)]*\))\s*\.\s*addEventListener/g;
  while((m=nl.exec(src))) add('ALTA',file,lineAt(m.index),'elemento-inexistente',
    `addEventListener direto em resultado de ${m[1].replace(/\s+/g,' ').slice(0,70)} sem guarda de null.`,
    `Se o elemento não existir no DOM → TypeError: Cannot read properties of null.`,
    `const el = document.getElementById('x'); if (el) el.addEventListener(...);`);

  const am=/(?:window\.)?meds\s*=\s*\[/g;
  while((m=am.exec(src))){ const mk=mask(src); const open=src.indexOf('[',m.index);
    const close=matchPair(mk,'[',']',open); if(close<0)continue;
    const lit=src.slice(open,close+1);
    let arr=null; try{ arr=vm.runInNewContext('('+lit+')',Object.create(null),{timeout:3000}); }catch(e){ REV.push({file,line:lineAt(m.index),txt:'não consegui evaluate meds: '+e.message}); }
    if(!Array.isArray(arr))continue;
    if(arr.length!==61) add('MÉDIA',file,lineAt(m.index),'meds-contagem',
      `Array meds tem ${arr.length} itens (referência: 61).`,'KPIs e comparador assumem 61 → divergência.','Conferir a lista.');
    const freq={}; arr.forEach(o=>{ if(o&&typeof o==='object') Object.keys(o).forEach(k=>freq[k]=(freq[k]||0)+1); });
    const required=Object.keys(freq).filter(k=>freq[k]>=arr.length*0.5);
    arr.forEach((o,i)=>{ if(!o||typeof o!=='object')return;
      const miss=required.filter(k=>!(k in o));
      if(miss.length) add('ALTA',file,lineAt(m.index),'meds-campo-ausente',
        `meds[${i}] (${String(o.nome||o.name||o.id||i).slice(0,40)}) não tem: ${miss.join(', ')}.`,
        `Renderizar lista → item sem dose/classe → cálculo quebrado.`,
        `Completar o objeto com os campos obrigatórios.`); }); }

  const doseCands=[];
  blocks.forEach(b=>{ const mk=mask(b.code);
    const re=/\b(?:function\s+([A-Za-z_$][\w$]*)|(?:var|let|const)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?(?:function|\())/g; let x;
    while((x=re.exec(mk))){ const nm=x[1]||x[2]; const open=mk.indexOf('{',x.index);
      if(open<0)continue; const close=matchPair(mk,'{','}',open); if(close<0)continue;
      const body=src.slice(open,close+1);
      if(/mg\s*\/\s*kg|mg\/m|BSA|Mosteller|superficie|superfície|dose|dosagem/i.test(body)){
        doseCands.push({nm, line:lineAt(b.abs+x.index), body, abs:open}); } } });

  const probe = (()=>{ try{
    const mockEl=()=>({style:{},dataset:{},classList:{add(){},remove(){},contains(){return false},toggle(){}},children:[],appendChild(){},removeChild(){},setAttribute(){},getAttribute(){return null},addEventListener(){},removeEventListener(){},querySelector(){return null},querySelectorAll(){return []},insertAdjacentHTML(){},innerHTML:'',textContent:'',value:'',checked:false,focus(){},blur(){},click(){},getBoundingClientRect(){return{top:0,left:0,width:0,height:0}}});
    const doc={getElementById:()=>mockEl(),querySelector:()=>mockEl(),querySelectorAll:()=>[],createElement:()=>mockEl(),body:mockEl(),head:mockEl(),documentElement:mockEl(),addEventListener(){},readyState:'complete',cookie:''};
    const ls={getItem:()=>null,setItem(){},removeItem(){},clear(){}};
    const sb={document:doc,localStorage:ls,sessionStorage:ls,location:{href:'',hash:'',search:''},navigator:{userAgent:'node',platform:'Linux',language:'pt-BR',clipboard:{}},innerWidth:1280,innerHeight:800,addEventListener(){},removeEventListener(){},matchMedia:()=>({matches:false,addEventListener(){},addListener(){}}),scrollTo(){},open(){},close(){},alert(){},confirm(){return false},prompt(){return null},setTimeout,clearTimeout,setInterval,clearInterval,requestAnimationFrame,console,getComputedStyle:()=>({getPropertyValue:()=>''}),crypto:{getRandomValues:a=>a}};
    sb.window=sb; sb.self=sb; sb.globalThis=sb;
    blocks.forEach(b=>{ try{ vm.runInNewContext(b.code, sb, {timeout:4000}); }catch(e){} });
    return sb;
  }catch(e){ return null; } })();

  const ARGS=[[15,10,3],[15,10],[10,15,3],[15,10,3,70],[15,10,3,1.7],[{peso:15,pesoKg:15,idade:8},10,3]];
  doseCands.forEach(c=>{
    const f=probe&&probe[c.nm]; if(typeof f!=='function')return;
    const res=[];
    ARGS.forEach(a=>{ try{ let v=f.apply(null,a); if(v&&typeof v==='object'){ v=v.mg??v.dose??v.doseMg??v.total??v.valor; } if(typeof v==='number'&&isFinite(v)) res.push(`${JSON.stringify(a)}=>${v}`); }catch(e){} });
    const nums=res.map(r=>Number(r.split('=>')[1]));
    const off=nums.filter(v=>v===150||v===450||v===5||v===750||v===2250);
    if(off.length) add('CRÍTICA',file,c.line,'dose-matematica',
      `\`${c.nm}\` retorna ${off.join('/')} onde o correto é 50 mg/dose (15 kg, 10 mg/kg/dia, 3×/dia).`,
      `Chamar ${c.nm}(15,10,3) → ${off[0]} (esperado 50).`,
      `dose = peso(kg) × mg/kg/dia ÷ nº administrações.`);
    if(/BSA|superficie|superfície/i.test(c.body)){
      if(/Math\.sqrt/i.test(c.body)&&!/0\.707/.test(c.body)&&!/Math\.pow/i.test(c.body))
        REV.push({file,line:c.line,txt:`BSA de ${c.nm} não usa Mosteller (0.707) nem Du Bois: `+c.body.replace(/\s+/g,' ').slice(0,150)});
      if(/Math\.sqrt\([^)]*altura[^)]*\)/i.test(c.body)&&!/100|1\.64/.test(c.body))
        add('CRÍTICA',file,c.line,'bsa-unidade',
          `BSA de \`${c.nm}\` usa sqrt(altura) sem converter cm→m → BSA em cm², doses mg/m² ~100× off.`,
          `Paciente 150 cm → BSA ~12,25 (cm²) em vez de 0,87 m² → dose 14× maior.`,
          `BSA = 0.707 × √(altura_cm) → m².`);
      if(/\*\s*(freq|vezes|times|dia|porDia|qtdDoses)\b/i.test(c.body)&&!/\/\s*(freq|vezes|times|dia|porDia|qtdDoses)\b/i.test(c.body))
        add('ALTA',file,c.line,'dose-frequencia',
          `\`${c.nm}\` multiplica pela frequência em vez de dividir → dose 3× maior.`,
          `15 kg, 10 mg/kg/dia, 3×/dia → 150 mg/dose em vez de 50.`,
          `Dividir pelo número de administrações diárias.`);
    } });
  return {file, doseCands: doseCands.map(c=>({nm:c.nm,line:c.line})), rev: REV.filter(r=>r.file===file)};
}

const SEV={ 'CRÍTICA':0,'ALTA':1,'MÉDIA':2,'BAIXA':3 };
let all=[], revs=[];
for(const f of NAMES){ const r=analyze(f); if(r){ all.push(...FIND.filter(x=>x.file===f)); revs.push(...r.rev); } }

all.sort((a,b)=>SEV[a.sev]-SEV[b.sev]||a.file.localeCompare(b.file)||a.line-b.line);
console.log('=== BUGS CONFIRMADOS (ordenado por severidade) ===');
for(const b of all) console.log(`[${b.sev}] ${b.file}:${b.line} · ${b.kind}\n  ${b.desc}\n  repro: ${b.repro}\n  fix: ${b.fix}\n`);
console.log('\n=== REVISAR (pontos para olho humano) ===');
for(const r of revs) console.log(`${r.file}:${r.line} · ${r.txt}`);
console.log(`\nTotal confirmados: ${all.length} | para revisar: ${revs.length}`);
fs.writeFileSync('/tmp/dashboard_bugs.json', JSON.stringify(all,null,2));
fs.writeFileSync('/tmp/dashboard_review.txt', revs.map(r=>`${r.file}:${r.line} · ${r.txt}`).join('\n'));
