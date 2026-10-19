"""O Estúdio: uma página local com os reels prontos, a fila do que postar, o calendário e o histórico.

Uso:
    python estudio.py PASTA                       varre os .mp4 da pasta e gera PASTA/estudio.html
    python estudio.py PASTA --video reel.mp4 [--roteiro roteiro.md] [--titulo "..."] [--palavra PALAVRA]
                            [--legenda-instagram "..."] [--legenda-tiktok "..."] [--legenda-linkedin "..."]
                            [--estado pronto|programado|postado] [--data 2026-10-25] [--nota "..."]
                            [--metricas "views=1200,salvos=40,comentarios=12"]
    python estudio.py PASTA --resumo              o que sai hoje, os próximos 7 dias e o que está sem data
    python estudio.py PASTA --distribuir --dias seg,qua,sex [--a-partir 2026-10-21] [--aplicar]
                                                  propõe uma data pra cada vídeo pronto sem data; só grava com --aplicar

Os dados ficam em PASTA/estudio.json (um item por vídeo), que você também pode editar na mão. --roteiro lê o
título (a capa escolhida), a palavra-chave e as legendas direto de um arquivo da skill Roteiro reel. A capa de
cada vídeo é tirada do segundo 1 e guardada em PASTA/capas/.

Abra PASTA/estudio.html no navegador: "Pra postar" é a fila (os programados por data, depois os prontos sem
data), "Postados" é o histórico com as métricas e "Calendário" mostra mês a mês o que está marcado. Em cada
cartão dá pra escolher a data e marcar como postado direto na página (fica salvo no navegador); o botão
"Baixar estudio.json" devolve o arquivo com essas mudanças pra você trocar na pasta. Nada sai do seu computador.
"""
import argparse
import sys
import html
import json
import os
import re
import subprocess
from datetime import date, timedelta

ESTADOS = ["pronto", "programado", "postado"]
DIAS = {"seg": 0, "ter": 1, "qua": 2, "qui": 3, "sex": 4, "sab": 5, "sáb": 5, "dom": 6}
NOMES_DIA = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]
REDES = (("Instagram", "legenda_instagram"), ("TikTok", "legenda_tiktok"), ("LinkedIn", "legenda_linkedin"))

CSS = """
:root{--fundo:#f4f4f1;--tinta:#16181d;--suave:rgba(22,24,29,.6);--linha:rgba(22,24,29,.12);--cor:#2552d9;--ok:#1f8a4c;--meio:#b7791f;--branco:#fff}
*{box-sizing:border-box;margin:0;padding:0}body{font-family:-apple-system,Inter,Segoe UI,sans-serif;background:var(--fundo);color:var(--tinta);padding:36px 18px 80px}
.wrap{max-width:1000px;margin:0 auto}h1{font-size:34px;letter-spacing:-.03em;margin-bottom:6px}.sub{color:var(--suave);margin-bottom:18px}
.abas{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:22px}.abas button{border-radius:999px}.abas button.on{background:var(--tinta);color:var(--branco);border-color:var(--tinta)}
.abas .conta{align-self:center;margin-left:auto;font-size:13px;color:var(--suave)}
.card{display:grid;grid-template-columns:220px 1fr;gap:22px;background:var(--branco);border:1px solid var(--linha);border-radius:18px;padding:18px;margin-bottom:16px}
.card.postado{opacity:.6}.card.postado:hover{opacity:1}
.card video{width:220px;aspect-ratio:9/16;border-radius:12px;background:#000;display:block}
h2{font-size:20px;letter-spacing:-.01em;margin:2px 0 8px}.meta{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px}
.tag{font-size:12px;font-weight:600;padding:4px 10px;border-radius:999px;background:#eef0f4;color:var(--suave)}
.tag.pronto{background:#e8f0ff;color:var(--cor)}.tag.programado{background:#fff4e0;color:var(--meio)}.tag.postado{background:#e6f5ec;color:var(--ok)}
.leg{white-space:pre-wrap;font-size:14px;line-height:1.55;background:#f7f7f5;border-radius:10px;padding:12px;margin:6px 0 10px;max-height:220px;overflow:auto}
.acoes{display:flex;gap:8px;flex-wrap:wrap;align-items:center}button,a.bt{font:inherit;font-size:13px;font-weight:600;padding:8px 14px;border-radius:9px;border:1px solid var(--linha);background:var(--branco);color:var(--tinta);cursor:pointer;text-decoration:none}
button:hover,a.bt:hover{border-color:var(--cor);color:var(--cor)}.nota{font-size:13px;color:var(--suave);margin-top:8px}
.quando{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-top:14px;padding-top:12px;border-top:1px dashed var(--linha);font-size:13px;font-weight:600}
.quando input{font:inherit;font-size:13px;padding:7px 9px;border:1px solid var(--linha);border-radius:9px;background:var(--branco)}
.quando button.on{background:var(--ok);border-color:var(--ok);color:var(--branco)}
.mes{background:var(--branco);border:1px solid var(--linha);border-radius:18px;padding:16px;margin-bottom:16px}
.mes h2{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:10px}.mes h2 small{font-size:13px;font-weight:500;color:var(--suave)}
.grade{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:6px}.dsem{font-size:11px;font-weight:600;color:var(--suave);text-align:center;padding:2px 0 4px}
.dia{min-height:76px;border:1px solid var(--linha);border-radius:10px;padding:5px;background:var(--fundo);font-size:11.5px}.dia.fora{visibility:hidden}
.dia.hoje{outline:2px solid var(--cor)}.dia .n{display:block;font-size:11px;font-weight:600;color:var(--suave);margin-bottom:3px}
.chip{display:block;margin-top:3px;padding:4px 6px;border-radius:7px;background:var(--branco);border-left:3px solid var(--meio);line-height:1.25;overflow:hidden;text-overflow:ellipsis;cursor:pointer}
.chip.postado{border-left-color:var(--ok)}.chip.pronto{border-left-color:var(--cor)}
.vazio{color:var(--suave);padding:20px 0}#cards{display:flex;flex-direction:column}
.met{display:flex;gap:6px;flex-wrap:wrap;margin-top:10px}.met .tag{background:transparent;border:1px solid var(--linha);color:var(--tinta)}
@media(prefers-color-scheme:dark){:root{--fundo:#0e1015;--tinta:#eef0f5;--suave:rgba(238,240,245,.6);--linha:rgba(238,240,245,.13);--cor:#7c9cff;--ok:#4cc38a;--meio:#e0a948;--branco:#171a22}
.tag{background:#222634}.tag.pronto{background:#1d2747}.tag.programado{background:#3a2e17}.tag.postado{background:#16352a}.leg{background:#1d212c}.quando button.on,.abas button.on{color:#0e1015}}
@media(max-width:640px){.card{grid-template-columns:1fr}.card video{width:100%;max-width:300px}.grade{grid-template-columns:repeat(2,1fr)}.dsem,.dia.fora{display:none}.dia{min-height:0}}
"""

JS = """
function copiar(id,bt){const t=document.getElementById(id).innerText;navigator.clipboard.writeText(t).then(()=>{const o=bt.innerText;bt.innerText='Copiado';setTimeout(()=>bt.innerText=o,1200)})}
const K='estudio-mudancas';
function mud(){try{return JSON.parse(localStorage.getItem(K)||'{}')}catch(e){return {}}}
function guarda(o){try{localStorage.setItem(K,JSON.stringify(o))}catch(e){}}
function item(arq){const m=mud()[arq]||{};const base=DADOS.itens.find(i=>i.arquivo===arq)||{};return Object.assign({},base,m)}
function marca(arq,estado){const o=mud();o[arq]=o[arq]||{};const atual=item(arq).estado;o[arq].estado=(atual===estado&&estado==='postado')?'pronto':estado;
 if(o[arq].estado==='postado'&&!item(arq).data){o[arq].data=new Date().toISOString().slice(0,10)}guarda(o);pinta()}
function data(arq,v){const o=mud();o[arq]=o[arq]||{};o[arq].data=v;if(v&&item(arq).estado==='pronto')o[arq].estado='programado';if(!v&&item(arq).estado==='programado')o[arq].estado='pronto';guarda(o);pinta()}
function fmt(d){if(!d)return '';const x=new Date(d+'T12:00:00');return x.toLocaleDateString('pt-BR',{weekday:'short',day:'2-digit',month:'2-digit'}).replace('.','')}
function pinta(){const hoje=new Date().toISOString().slice(0,10);let n={postar:0,postados:0};
 document.querySelectorAll('.card').forEach(c=>{const it=item(c.dataset.arq);c.className='card '+it.estado;
  const t=c.querySelector('.tag.estado');t.className='tag estado '+it.estado;t.textContent=it.estado+(it.data?' · '+fmt(it.data):'');
  c.querySelector('.quando input').value=it.data||'';c.querySelector('.quando .pt').classList.toggle('on',it.estado==='postado');
  c.querySelector('.quando .pt').textContent=it.estado==='postado'?'Postado ✓':'Marcar como postado';
  const fila=it.estado!=='postado';c.dataset.fila=fila?'postar':'postados';n[fila?'postar':'postados']++;
  c.style.order=fila?(it.data?Number(it.data.replace(/-/g,'')):99999999):-Number((it.data||'0000-00-00').replace(/-/g,''))});
 document.querySelector('.conta').textContent=n.postar+' na fila · '+n.postados+(n.postados===1?' postado':' postados');aba(ABA);calendario()}
let ABA='postar';try{ABA=localStorage.getItem('estudio-aba')||'postar'}catch(e){}
function aba(t){ABA=t;try{localStorage.setItem('estudio-aba',t)}catch(e){}
 document.querySelectorAll('.abas button[data-t]').forEach(b=>b.classList.toggle('on',b.dataset.t===t));
 document.getElementById('cards').style.display=t==='calendario'?'none':'';document.getElementById('cal').style.display=t==='calendario'?'':'none';
 document.querySelectorAll('.card').forEach(c=>c.style.display=(t==='calendario'||c.dataset.fila===t)?'':'none');
 const vazio=document.getElementById('vazio');if(vazio)vazio.style.display=(t!=='calendario'&&![...document.querySelectorAll('.card')].some(c=>c.dataset.fila===t))?'':'none'}
function calendario(){const box=document.getElementById('cal');const hoje=new Date();const hj=hoje.toISOString().slice(0,10);const porDia={};
 DADOS.itens.forEach(i=>{const it=item(i.arquivo);if(it.data)(porDia[it.data]=porDia[it.data]||[]).push(it)});
 const datas=Object.keys(porDia).sort();let y=hoje.getFullYear(),m=hoje.getMonth();const ult=datas.length?datas[datas.length-1]:hj;const fy=+ult.slice(0,4),fm=+ult.slice(5,7)-1;
 const nomes=['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro'];let h='',conta=0;
 while((y<fy||(y===fy&&m<=fm))||conta<2){const nd=new Date(y,m+1,0).getDate(),ini=(new Date(y,m,1).getDay()+6)%7;let marcados=0;
  let cel=['seg','ter','qua','qui','sex','sáb','dom'].map(d=>'<div class="dsem">'+d+'</div>').join('');for(let k=0;k<ini;k++)cel+='<div class="dia fora"></div>';
  for(let d=1;d<=nd;d++){const iso=y+'-'+String(m+1).padStart(2,'0')+'-'+String(d).padStart(2,'0');const its=porDia[iso]||[];marcados+=its.length;
   cel+='<div class="dia'+(iso===hj?' hoje':'')+'"><span class="n">'+d+'</span>'+its.map(it=>'<span class="chip '+it.estado+'" data-arq="'+esc(it.arquivo)+'" title="'+esc(it.titulo)+'">'+esc(it.titulo)+'</span>').join('')+'</div>'}
  h+='<div class="mes"><h2>'+nomes[m]+' de '+y+'<small>'+(marcados?marcados+' marcado'+(marcados>1?'s':''):'nada marcado')+'</small></h2><div class="grade">'+cel+'</div></div>';
  m++;if(m>11){m=0;y++}conta++;if(conta>18)break}
 box.innerHTML=h;box.onclick=ev=>{const c=ev.target.closest('.chip[data-arq]');if(c)abre(c.dataset.arq)}}
function esc(t){return String(t).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function abre(arq){const c=[...document.querySelectorAll('.card')].find(c=>c.dataset.arq===arq);if(!c)return;aba(c.dataset.fila);c.scrollIntoView({block:'start',behavior:'smooth'})}
function baixar(){const o=mud();const d=JSON.parse(JSON.stringify(DADOS));d.itens.forEach(i=>{const m=o[i.arquivo];if(m){if(m.estado)i.estado=m.estado;if('data' in m)i.data=m.data||''}delete i.capa});
 const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(d,null,1)],{type:'application/json'}));a.download='estudio.json';a.click()}
pinta();
"""


def carregar(pasta):
    p = os.path.join(pasta, "estudio.json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {"itens": []}


def salvar(pasta, dados):
    json.dump(dados, open(os.path.join(pasta, "estudio.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def capa(pasta, arquivo):
    os.makedirs(os.path.join(pasta, "capas"), exist_ok=True)
    destino = os.path.join(pasta, "capas", os.path.splitext(arquivo)[0] + ".jpg")
    if not os.path.exists(destino):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "1", "-i", os.path.join(pasta, arquivo), "-frames:v", "1",
                        "-vf", "scale=540:-2", destino], check=False)
    return os.path.relpath(destino, pasta) if os.path.exists(destino) else None


def varrer(pasta, dados):
    existentes = {i["arquivo"] for i in dados["itens"]}
    for f in sorted(os.listdir(pasta)):
        if f.lower().endswith(".mp4") and f not in existentes:
            dados["itens"].append({"arquivo": f, "titulo": os.path.splitext(f)[0].replace("-", " ").replace("_", " "),
                                   "estado": "pronto", "palavra": "", "legenda_instagram": "", "legenda_tiktok": "",
                                   "nota": "", "data": "", "adicionado_em": date.today().isoformat()})
    dados["itens"] = [i for i in dados["itens"] if os.path.exists(os.path.join(pasta, i["arquivo"]))]
    for i in dados["itens"]:
        i["capa"] = capa(pasta, i["arquivo"])


def pagina(pasta, dados):
    cards = []
    e = html.escape
    for k, i in enumerate(dados["itens"]):
        legs = ""
        for rede, chave in REDES:
            if i.get(chave):
                legs += (f'<div class="tag">{rede}</div><div class="leg" id="leg{k}{rede}">{e(i[chave])}</div>'
                         f'<div class="acoes"><button onclick="copiar(\'leg{k}{rede}\',this)">Copiar legenda do {rede}</button></div>')
        poster = f' poster="{e(i["capa"])}"' if i.get("capa") else ""
        palavra = f'<span class="tag">Palavra: {e(i["palavra"])}</span>' if i.get("palavra") else ""
        nota = f'<div class="nota">{e(i["nota"])}</div>' if i.get("nota") else ""
        if i.get("metricas"):
            nota += '<div class="met">' + "".join(f'<span class="tag">{e(k)}: {e(str(v))}</span>' for k, v in i["metricas"].items()) + "</div>"
        arq = e(i["arquivo"])
        cards.append(f"""<div class="card {e(i['estado'])}" data-arq="{arq}"><div><video controls preload="metadata" src="{arq}"{poster}></video></div>
<div><h2>{e(i['titulo'])}</h2><div class="meta"><span class="tag estado {e(i['estado'])}">{e(i['estado'])}</span>{palavra}<span class="tag">{arq}</span></div>
{legs}<div class="acoes" style="margin-top:10px"><a class="bt" href="{arq}" download>Baixar o vídeo</a></div>{nota}
<div class="quando">Data <input type="date" onchange="data('{arq}',this.value)"> <button class="pt" onclick="marca('{arq}','postado')">Marcar como postado</button></div></div></div>""")
    n = len(dados["itens"])
    publico = {"itens": [{c: v for c, v in i.items() if c != "capa"} for i in dados["itens"]]}
    doc = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Estúdio</title><style>{CSS}</style></head><body><div class="wrap"><h1>Estúdio</h1>
<p class="sub">{n} {'vídeo' if n == 1 else 'vídeos'}. Gerado em {date.today().strftime('%d/%m/%Y')}. A data e o estado que você marcar aqui ficam salvos neste navegador; "Baixar estudio.json" devolve o arquivo com as mudanças pra você trocar na pasta.</p>
<div class="abas"><button data-t="postar" onclick="aba('postar')">Pra postar</button><button data-t="postados" onclick="aba('postados')">Postados</button><button data-t="calendario" onclick="aba('calendario')">Calendário</button><button onclick="baixar()">Baixar estudio.json</button><span class="conta"></span></div>
<div id="cards">{''.join(cards)}<p class="vazio" id="vazio">Nada aqui ainda.</p></div><div id="cal" style="display:none"></div>
{'' if n else '<p class="sub">Nenhum .mp4 nesta pasta ainda.</p>'}</div><script>const DADOS={json.dumps(publico, ensure_ascii=False)};{JS}</script></body></html>"""
    open(os.path.join(pasta, "estudio.html"), "w", encoding="utf-8").write(doc)


def ler_roteiro(caminho):
    """Lê um arquivo da skill Roteiro reel: o cabeçalho entre --- e as seções que começam com ## ."""
    t = open(caminho, encoding="utf-8").read()
    meta, corpo = {}, t
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?", t, re.S)
    if m:
        for linha in m.group(1).splitlines():
            if ":" in linha:
                k, v = linha.split(":", 1)
                meta[k.strip()] = v.strip()
        corpo = t[m.end():]
    secoes = {}
    for bloco in re.split(r"(?m)^## ", "\n" + corpo)[1:]:
        nome, _, texto = bloco.partition("\n")
        texto = texto.strip()
        if texto and not (texto.startswith("(") and texto.endswith(")") and "\n" not in texto):
            secoes[nome.strip()] = texto
    return meta, secoes


def do_roteiro(item, caminho):
    meta, sec = ler_roteiro(caminho)
    titulo = meta.get("capa") or meta.get("titulo")
    if titulo:
        item["titulo"] = titulo
    if meta.get("palavra"):
        item["palavra"] = meta["palavra"].upper()
    for rede, chave in REDES:
        if sec.get(f"Legenda {rede}"):
            item[chave] = sec[f"Legenda {rede}"]
    item["roteiro"] = os.path.basename(caminho)


def metricas(txt):
    out = {}
    for par in txt.split(","):
        if "=" in par:
            k, v = par.split("=", 1)
            v = v.strip()
            out[k.strip()] = int(v) if v.isdigit() else v
    return out


def fmt_dia(iso):
    d = date.fromisoformat(iso)
    return f"{NOMES_DIA[d.weekday()]} {d.strftime('%d/%m')}"


def resumo(dados, hoje=None):
    hoje = hoje or date.today()
    fila = [i for i in dados["itens"] if i["estado"] != "postado"]
    datados = sorted((i for i in fila if i.get("data")), key=lambda i: i["data"])
    sem_data = [i for i in fila if not i.get("data")]
    print(f"Hoje, {fmt_dia(hoje.isoformat())}:")
    hj = [i for i in datados if i["data"] == hoje.isoformat()]
    atrasados = [i for i in datados if i["data"] < hoje.isoformat()]
    for i in hj:
        print(f"  postar: {i['titulo']}  ({i['arquivo']})" + (f"  palavra {i['palavra']}" if i.get("palavra") else ""))
    if not hj:
        print("  nada marcado pra hoje")
    for i in atrasados:
        print(f"  atrasado desde {fmt_dia(i['data'])}: {i['titulo']}  (marque como postado ou mude a data)")
    print("\nPróximos 7 dias:")
    for k in range(1, 8):
        d = (hoje + timedelta(days=k)).isoformat()
        its = [i["titulo"] for i in datados if i["data"] == d]
        print(f"  {fmt_dia(d)}: " + (" | ".join(its) if its else "vazio"))
    print(f"\nProntos sem data: {len(sem_data)}")
    for i in sem_data:
        print(f"  {i['titulo']}  ({i['arquivo']})")
    postados = [i for i in dados["itens"] if i["estado"] == "postado"]
    print(f"\nPostados: {len(postados)}" + (f", o último em {fmt_dia(max(i['data'] for i in postados if i.get('data')))}"
                                            if any(i.get("data") for i in postados) else ""))


def distribuir(dados, dias, a_partir):
    """Uma data pra cada pronto sem data, nos dias da semana pedidos, pulando os dias que já têm vídeo marcado."""
    ocupados = {i["data"] for i in dados["itens"] if i.get("data") and i["estado"] != "postado"}
    livres, d = [], a_partir
    sem_data = [i for i in dados["itens"] if i["estado"] == "pronto" and not i.get("data")]
    while len(livres) < len(sem_data):
        if d.weekday() in dias and d.isoformat() not in ocupados:
            livres.append(d.isoformat())
        d += timedelta(days=1)
    return list(zip(sem_data, livres))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pasta")
    ap.add_argument("--video", help="arquivo .mp4 dentro da pasta pra atualizar os campos abaixo")
    ap.add_argument("--titulo")
    ap.add_argument("--legenda-instagram")
    ap.add_argument("--legenda-tiktok")
    ap.add_argument("--palavra")
    ap.add_argument("--estado", choices=ESTADOS)
    ap.add_argument("--data", help="dia de postar, no formato 2026-10-25 (vazio tira a data)")
    ap.add_argument("--nota")
    ap.add_argument("--legenda-linkedin")
    ap.add_argument("--roteiro", help="arquivo .md da skill Roteiro reel: preenche título, palavra e legendas")
    ap.add_argument("--metricas", help='ex.: "views=1200,salvos=40,comentarios=12"')
    ap.add_argument("--resumo", action="store_true", help="mostra hoje, os próximos 7 dias e o que está sem data")
    ap.add_argument("--distribuir", action="store_true", help="propõe datas pros prontos sem data")
    ap.add_argument("--dias", default="seg,qua,sex", help="dias da semana pra postar, ex.: seg,qua,sex")
    ap.add_argument("--a-partir", help="primeiro dia possível, no formato 2026-10-21 (padrão: amanhã)")
    ap.add_argument("--aplicar", action="store_true", help="grava as datas propostas pelo --distribuir")
    a = ap.parse_args()
    pasta = os.path.abspath(a.pasta)
    dados = carregar(pasta)
    varrer(pasta, dados)
    if a.video:
        item = next((i for i in dados["itens"] if i["arquivo"] == os.path.basename(a.video)), None)
        if not item:
            raise SystemExit(f"{a.video} não está na pasta {pasta}")
        if a.roteiro:
            do_roteiro(item, a.roteiro)
        if a.metricas:
            item.setdefault("metricas", {}).update(metricas(a.metricas))
        for campo, valor in (("titulo", a.titulo), ("legenda_instagram", a.legenda_instagram), ("legenda_tiktok", a.legenda_tiktok),
                             ("legenda_linkedin", a.legenda_linkedin), ("palavra", a.palavra), ("estado", a.estado),
                             ("data", a.data), ("nota", a.nota)):
            if valor is not None:
                item[campo] = valor
        if a.data and item["estado"] == "pronto":
            item["estado"] = "programado"
    if a.distribuir:
        try:
            dias = sorted({DIAS[x.strip().lower()] for x in a.dias.split(",") if x.strip()})
        except KeyError as erro:
            raise SystemExit(f"Dia não reconhecido: {erro}. Use seg, ter, qua, qui, sex, sab, dom.")
        inicio = date.fromisoformat(a.a_partir) if a.a_partir else date.today() + timedelta(days=1)
        plano = distribuir(dados, dias, inicio)
        if not plano:
            print("Nenhum vídeo pronto sem data.")
        for item, dia in plano:
            print(f"  {fmt_dia(dia)}: {item['titulo']}  ({item['arquivo']})")
            if a.aplicar:
                item["data"], item["estado"] = dia, "programado"
        if plano and not a.aplicar:
            print("\nNada foi gravado. Rode de novo com --aplicar pra marcar essas datas.")
            return
    salvar(pasta, dados)
    pagina(pasta, dados)
    if a.resumo:
        resumo(dados)
        return
    print(f"Estúdio: {os.path.join(pasta, 'estudio.html')}  ({len(dados['itens'])} vídeos)")
    for i in dados["itens"]:
        print(f"  [{i['estado']:10s}] {i.get('data') or '          '}  {i['titulo']}  ({i['arquivo']})")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
