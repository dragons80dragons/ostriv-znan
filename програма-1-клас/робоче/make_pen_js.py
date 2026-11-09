# -*- coding: utf-8 -*-
"""Збирає САМОДОСТАТНІЙ контрольний аркуш з наявного PEN у index.html плюс
нові літери: рівно те, що потім буде в грі. Зовнішній <script src> у
статичному перегляді не вантажиться, тому код вшивається в сторінку."""
import io, re, os
G = r'G:\ostriv-znan'
W = r'G:\ostriv-znan\програма-1-клас\робоче'
src = io.open(os.path.join(G, 'index.html'), encoding='utf-8').read()
pen = re.search(r'const PEN = \{.*?\n\};', src, re.S).group(0)
add = io.open(os.path.join(W, '\u0432\u0441\u0442\u0430\u0432\u043a\u0430_1_\u043f\u0440\u043e\u043f\u0438\u0441\u0438.js'),
              encoding='utf-8').read()
asg = re.search(r'Object\.assign\(PEN, \{.*?\n\}\);', add, re.S).group(0)

HTML = u"""<!doctype html>
<meta charset="utf-8">
<title>Перевірка рукописних літер</title>
<style>
 body{font:14px system-ui;background:#fdfbf6;margin:12px}
 .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(88px,1fr));gap:6px}
 figure{margin:0;background:#fff;border:1px solid #e3dccd;border-radius:8px;padding:2px;text-align:center}
 figcaption{font-size:12px;color:#555}
 svg{width:100%;height:auto;display:block}
 .rl{stroke:#cfe0f0;stroke-width:.7}
 .sl{stroke:#eee4d2;stroke-width:.6}
 .pen{fill:none;stroke:#2f6fa8;stroke-width:3.2;stroke-linecap:round;stroke-linejoin:round}
 .dot{fill:#d9534f}
 h2{margin:14px 0 4px;font-size:15px}
 .bad figcaption{color:#c00;font-weight:600}
</style>
<body><div id="out"></div>
<script>
__PEN__
__ASG__
const PEN_VB=[8,10,84,84], penT='translate(7 0) skewX(-8)';
const GR=[['Малі','абвгґдеєжзиіїйклмнопрстуфхцчшщьюя'],
          ['Великі','АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЮЯ'],
          ['Цифри','0123456789']];
const rules=[18,35,72,90].map(y=>'<line class="rl" x1="2" y1="'+y+'" x2="98" y2="'+y+'"/>').join('')
 +[10,26,42,58,74,90].map(x=>'<line class="sl" x1="'+x+'" y1="90" x2="'+(x+10)+'" y2="18"/>').join('');
let h='';
for (const [title,list] of GR){
  h+='<h2>'+title+' ('+list.length+')</h2><div class="grid">';
  for (const ch of list){
    const st=PEN[ch];
    h+='<figure class="'+(st?'':'bad')+'"><svg viewBox="'+PEN_VB.join(' ')+'">'+rules;
    if(st) h+='<g transform="'+penT+'">'+st.map(d=>'<path class="pen" d="'+d+'"/>').join('')+'</g>';
    h+='</svg><figcaption>'+(st?ch:ch+' НЕМА')+'</figcaption></figure>';
  }
  h+='</div>';
}
document.getElementById('out').innerHTML=h;
for (const g of document.querySelectorAll('svg g'))
  for (const p of g.querySelectorAll('.pen')){
    const a=p.getPointAtLength(0);
    g.insertAdjacentHTML('beforeend','<circle class="dot" cx="'+a.x+'" cy="'+a.y+'" r="2"/>');
  }
</script>
"""
out = HTML.replace('__PEN__', pen).replace('__ASG__', asg)
p = os.path.join(W, '\u043f\u0435\u0440\u0435\u0432\u0456\u0440\u043a\u0430_\u043b\u0456\u0442\u0435\u0440.html')
io.open(p, 'w', encoding='utf-8').write(out)
print('ok', len(out))
