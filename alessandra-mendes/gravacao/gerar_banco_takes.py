"""Gera o PDF 'Banco de takes reaproveitáveis' (Multiplica Cortes) da Alê.

Uso: python3 gerar_banco_takes.py  ->  banco-de-takes-ale.pdf (nesta pasta)
Renderiza com o Chromium do Playwright (Node).
"""
import html, pathlib, subprocess

AQUI = pathlib.Path(__file__).parent
e = lambda s: html.escape(s, quote=False)

# (código, estilo, como gravar (regra do bloco), takes[(take, como, variações, serve para)])
BLOCOS = [
 ("1", "Reações mudas", "Fundo liso, plano médio com espaço em cima, SEM falar. Segure 4 a 6 s. Grave cada uma olhando para a câmera, para a esquerda e para a direita (é para onde o vídeo reagido vai ficar).", [
  ("Mão no queixo, olhando para cima", "pensando, desconfiada", "3 direções", "react, dúvida da caixinha, mito/verdade"),
  ("Mão no queixo, olhando para o lado", "como se lesse o vídeo ao lado", "esq. e dir.", "react, dueto, print de comentário"),
  ("Choque: boca aberta, mão na boca", "exagerar um pouco", "2 intensidades", "receita caseira, erro grave, antes e depois"),
  ("Dedo negando: “não, não, não”", "sorrindo e séria", "2 tons", "mito, produto que não usaria, erro"),
  ("Cabeça dizendo “sim”, sorrindo", "aprovação tranquila", "2 tons", "verdade, produto que aprova, resultado"),
  ("Facepalm", "mão na testa e respiração", "2 tons", "POV cliente, receita do TikTok"),
  ("Rindo de verdade", "peça para a Ana contar algo engraçado", "3 risadas", "humor, bastidor, tipos de cliente"),
  ("Revirando os olhos", "leve, sem ofender", "1", "“quando a cliente diz que usa protetor”"),
  ("Sobrancelha levantada", "desconfiada, “hum…”", "esq. e dir.", "promessa milagrosa, produto viral"),
  ("Braços cruzados, séria", "julgando com carinho", "1", "react a erro, antes de explicar"),
  ("Aplaudindo", "animada", "1", "resultado de cliente, acerto da seguidora"),
  ("Mão no peito, emocionada", "“que lindo”", "1", "antes e depois, depoimento"),
  ("Chegando perto da câmera", "para “ver melhor”", "1", "react de pele, close de textura"),
  ("Tirando os óculos devagar", "dramático", "1", "virada, “agora é sério”"),
  ("Beijo de chef", "“perfeito”", "1", "produto aprovado, resultado"),
  ("Joinha e coração com as mãos", "dois gestos separados", "2", "finais, agradecimento, CTA"),
  ("Anotando no caderno", "analisando", "esq. e dir.", "análise de foto, “vou te explicar”"),
  ("Lupa na mão olhando a tela", "como se examinasse o vídeo", "esq. e dir.", "react de pele, análise com IA"),
  ("Ombros: “fazer o quê”", "conformada, sorrindo", "1", "humor, “depende da pele”"),
  ("Olhar para a câmera e sorrir", "pausa de 3 s antes", "3 looks", "abertura e final de qualquer vídeo"),
 ]),
 ("2", "Bordões curtos com áudio", "Uma frase por take, 1 a 3 s, olhando para a lente. Grave cada uma em 3 tons: séria, sorrindo e animada. Encaixam em qualquer vídeo.", [
  ("“Mito!”", "", "3 tons", "mito/verdade, react"), ("“Verdade!”", "", "3 tons", "mito/verdade, react"),
  ("“Gente, não faz isso!”", "", "3 tons", "receita caseira, erro"), ("“Isso aqui é perfeito.”", "", "3 tons", "produto, resultado"),
  ("“Olha que resultado.”", "", "3 tons", "antes e depois"), ("“Presta atenção nisso.”", "", "3 tons", "abertura, virada"),
  ("“Ninguém te conta isso.”", "", "3 tons", "gancho"), ("“Salva esse vídeo.”", "", "3 tons", "final"),
  ("“Manda pra uma amiga que precisa.”", "", "3 tons", "final"), ("“Comenta MANCHA que eu te mando.”", "", "3 tons", "CTA"),
  ("“Me chama no WhatsApp.”", "", "3 tons", "CTA"), ("“Hoje tem 10% OFF.”", "", "3 tons", "oferta"),
  ("“Calma, tem solução.”", "", "3 tons", "depois do problema"), ("“Por isso a sua mancha volta.”", "", "3 tons", "melasma"),
  ("“Esse eu aprovo.”", "", "3 tons", "react de produto"), ("“Esse eu não usaria.”", "", "3 tons", "react de produto"),
  ("“Depende da sua pele.”", "", "3 tons", "dúvidas"), ("“Não é milagre, é método.”", "", "3 tons", "autoridade"),
  ("“Quer que eu analise a sua?”", "", "3 tons", "CTA análise com IA"), ("“Quer parte 2?”", "", "3 tons", "série"),
  ("“Responde aqui embaixo.”", "", "3 tons", "engajamento"), ("“Eu avisei.”", "", "3 tons", "humor"),
  ("“Vem que eu te explico.”", "", "3 tons", "transição para explicação"), ("“Faz sentido pra você?”", "", "3 tons", "final"),
  ("“Pele de vidro, gente.”", "", "3 tons", "Glass Skin"),
 ]),
 ("3", "Ganchos de abertura", "Os 3 primeiros segundos, gravados soltos para colar na frente de qualquer conteúdo. 3 tentativas cada.", [
  ("“Se você tem mancha, para tudo.”", "", "3", "melasma, Protocolo AM"),
  ("“Eu atendo há 30 anos e preciso te falar isso.”", "", "3", "autoridade"),
  ("“Você está fazendo isso errado.”", "", "3", "rotina, erro"),
  ("“3 coisas que eu nunca faria na sua pele.”", "", "3", "lista"),
  ("“Pare de comprar isso.”", "", "3", "react de produto"),
  ("“Isso aqui mudou a pele da minha cliente.”", "", "3", "resultado"),
  ("“Antes de marcar qualquer procedimento, assiste isso.”", "", "3", "procedimentos"),
  ("“O que eu faria se fosse você.”", "", "3", "análise de foto"),
  ("“Teste rápido: …”", "", "3", "quiz, tipo de pele"),
  ("“A pergunta que mais chega no meu WhatsApp.”", "", "3", "caixinha"),
  ("“Reagindo a isso aqui.”", "apontando para o lado", "3", "qualquer react"),
  ("“Mito ou verdade?”", "", "3", "série mito/verdade"),
  ("“POV:”", "pausa, cara de deboche", "3", "humor"),
  ("“Spoiler: tem solução.”", "", "3", "problema → solução"),
  ("“Ninguém fala disso sobre pele.”", "", "3", "educativo"),
 ]),
 ("4", "Cenas silenciosas para narração", "Sem falar. Servem de fundo para texto na tela ou para a voz da Alê gravada depois. 5 s e 15 s de cada.", [
  ("Andando até a câmera e parando", "", "3 looks", "abertura, vinheta"), ("Sentada, olhando para a câmera, sorrindo", "", "3 looks", "fundo para texto longo"),
  ("Mexendo no celular e sorrindo", "", "2", "WhatsApp, Lezinha, mensagens"), ("Digitando no notebook", "", "1", "análise, organização"),
  ("Tomando café", "", "2", "bastidor, “bom dia”"), ("Ajeitando o jaleco", "", "1", "antes de atender"),
  ("Ajeitando o cabelo no espelho", "", "1", "rotina, humanização"), ("Olhando pela janela", "", "1", "história, reflexão"),
  ("Arrumando a bancada", "", "1", "bastidor, organização"), ("Passando protetor no rosto", "", "2", "rotina, CTA protetor"),
  ("Lavando o rosto", "", "1", "rotina"), ("Escrevendo um cartão", "", "1", "cuidado com a cliente"),
  ("Abrindo a porta da sala", "", "1", "boas-vindas, tour"), ("Sentando na cadeira de atendimento", "", "1", "começo de explicação"),
  ("Caminhando no corredor", "", "1", "transição, vlog"),
 ]),
 ("5", "Detalhes do consultório e dos procedimentos", "Só mãos e objetos. Grave também em câmera lenta. Ilustram qualquer vídeo de técnica, produto ou oferta.", [
  ("Aplicando produto no rosto da modelo", "close", "2", "Glass Skin, rotina"), ("Pincel com máscara", "", "2", "Glass Skin, Protocolo AM"),
  ("Gota de sérum caindo", "câmera lenta", "2", "vitamina C, rotina"), ("LED acendendo", "trocar as cores", "3", "Glass Skin, tecnologia"),
  ("Vapor de ozônio", "câmera lenta", "1", "limpeza de pele"), ("Extração com técnica", "close, sem sangue", "2", "limpeza, ASMR"),
  ("Caneta de microagulhamento", "", "1", "microagulhamento"), ("Pipeta de vitamina C", "", "1", "microagulhamento + vit C"),
  ("Algas sendo misturadas", "", "1", "Protocolo AM"), ("Espuma na mão", "", "1", "limpeza coreana"),
  ("Borrifador contra a luz", "névoa brilhando", "1", "hidratação, glow"), ("Textura do produto (swatch)", "", "3", "produto"),
  ("Toalha sendo dobrada", "", "1", "cuidado, bastidor"), ("Luvas sendo calçadas", "", "1", "higiene, início"),
  ("Maca vista de cima", "", "1", "abertura, tour"), ("Lupa acendendo", "", "1", "avaliação"),
  ("Tela da análise com IA", "gravar a tela", "1", "Lezinha, Espelho"), ("Mensagem chegando no WhatsApp", "gravar a tela", "1", "CTA, prova social"),
  ("Home care sendo embalado", "", "1", "oferta, presente"), ("Produtos coreanos girando na mão", "", "2", "Glass Skin, produto"),
 ]),
 ("6", "Transições", "Gravar o começo e o fim de cada transição no mesmo enquadramento, com cada um dos 3 looks.", [
  ("Tapar a lente com a mão", "", "3 looks", "troca de look ou cena"), ("Estalar os dedos", "", "3 looks", "antes/depois, troca"),
  ("Girar de costas e voltar", "", "3 looks", "troca de look"), ("Jogar a toalha na câmera", "", "2", "bastidor → resultado"),
  ("Entrar pulando no quadro", "", "2", "abertura divertida"), ("Aproximar o produto da lente", "", "2", "revelar produto"),
  ("Piscar para a câmera", "", "2", "final"), ("Apontar para cima, para baixo e para os lados", "4 direções", "4", "encaixar texto ou vídeo"),
 ]),
 ("7", "Placas e objetos de cena", "Mostrar cada placa para a câmera, séria e sorrindo. Entram em react, quiz e mito/verdade.", [
  ("MITO / VERDADE", "", "3 tons", "mito/verdade"), ("APROVO / REPROVO", "", "3 tons", "react de produto"),
  ("Notas de 0 a 10", "uma por vez", "11", "nota para produto ou rotina"), ("SIM / NÃO", "", "2", "quiz"),
  ("Placa de “?”", "", "1", "dúvida da caixinha"), ("Espelho de mão", "", "1", "olhar a pele, POV"),
  ("Lápis branco desenhando no rosto", "modelo", "1", "harmonização explicada"), ("Régua ou fita no rosto", "modelo", "1", "simetria, terços"),
 ]),
]

RECEITAS = [
 ("React de skincare viral", "Gancho “Reagindo a isso aqui” + vídeo de terceiro (pelo dueto ou remix do app) + reação muda + bordão “Esse eu não usaria” + “Me chama no WhatsApp”", "1 reação muda vira dezenas de reacts"),
 ("Mito ou verdade", "Pergunta em texto + placa MITO/VERDADE + bordão + 10 s de explicação + “Salva esse vídeo”", "1 placa serve para 25+ mitos"),
 ("Antes e depois", "Foto do resultado + “Olha que resultado” + mão no peito + “Comenta MANCHA”", "cada foto real vira 3 vídeos"),
 ("POV de humor", "Texto “POV: …” + reação muda + áudio viral", "infinito: só muda o texto"),
 ("Dúvida da caixinha", "Print da pergunta + mão no queixo + resposta curta + “Me chama no WhatsApp”", "1 take de dúvida para 50 respostas"),
 ("Tutorial narrado", "Cenas silenciosas + detalhes + narração gravada depois + texto na tela", "a mesma cena cobre várias rotinas"),
 ("Oferta do dia", "“Hoje tem 10% OFF” + detalhes (home care, LED) + “Me chama no WhatsApp”", "1 bordão, ofertas da semana toda"),
 ("Nota de 0 a 10", "Produto ou rotina em tela + placa da nota + “Esse eu aprovo / não usaria”", "11 placas para qualquer produto"),
]

REGRAS = [
 "Mesmo enquadramento sempre: plano médio, cabeça um pouco abaixo do topo (espaço para texto).",
 "Fundo liso e claro atrás da Alê: facilita recortar e colocar outro vídeo atrás.",
 "Segurar 3 s parada antes e depois de cada take: é o que deixa o corte limpo.",
 "Reações em 3 direções: câmera, esquerda e direita. O vídeo reagido entra do lado para onde ela olha.",
 "4K vertical: dá para recortar em close sem perder qualidade.",
 "Nomear os arquivos na hora, ou anotar no PDF o número do take (ex.: 1-04 = choque).",
 "Reagir a vídeo de outra pessoa: usar o dueto ou remix do próprio app e dar crédito. Não baixar e repostar.",
]

def build():
    total = sum(len(b[3]) for b in BLOCOS)
    secs = []
    for code, nome, regra, takes in BLOCOS:
        rows = ''.join(f'<tr><td class="ck"><span class="box"></span></td><td class="n">{code}-{i:02d}</td><td class="tk"><b>{e(t)}</b>{(" <span class=c>" + e(c) + "</span>") if c else ""}</td><td class="v">{e(v)}</td><td class="u">{e(u)}</td></tr>' for i,(t,c,v,u) in enumerate(takes,1))
        secs.append(f'''<section class="blk"><div class="bh"><span class="code">{code}</span><div><h2>{e(nome)}</h2><p>{e(regra)}</p></div><span class="cnt">{len(takes)} takes</span></div>
          <table class="tk-t"><thead><tr><th></th><th>nº</th><th>take</th><th>variações</th><th>serve para</th></tr></thead><tbody>{rows}</tbody></table></section>''')
    rec = ''.join(f'<div class="rc"><b>{e(a)}</b><p>{e(b)}</p><span>{e(c)}</span></div>' for a,b,c in RECEITAS)
    reg = ''.join(f'<li>{e(x)}</li>' for x in REGRAS)
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>
:root{{--p:#FAF6F2;--ink:#2B1F1A;--ink2:#6E5A50;--clay:#B9705A;--blush:#F3DCD2;--line:#E8DCD2}}
*{{box-sizing:border-box}}
body{{margin:0;font-family:"Inter",sans-serif;color:var(--ink);font-size:9.6pt;line-height:1.42}}
h1,h2{{font-family:"Inter Display","Inter",sans-serif;letter-spacing:-.03em;margin:0}}
.mono{{font-family:"JetBrains Mono",monospace;font-size:8pt;letter-spacing:.08em;text-transform:uppercase;color:var(--clay)}}
.cover{{height:265mm;border-radius:10mm;background:radial-gradient(circle at 85% 10%,#F7C9B2,transparent 45%),radial-gradient(circle at 10% 90%,#EAD3AE,transparent 45%),var(--p);padding:18mm 16mm;display:flex;flex-direction:column;justify-content:space-between;page-break-after:always}}
.cover .am{{width:16mm;height:16mm;border-radius:50%;background:var(--ink);color:var(--p);display:grid;place-items:center;font-weight:700;font-size:12pt}}
.cover h1{{font-size:50pt;line-height:.92;font-weight:800}}
.cover h1 span{{color:var(--clay)}}
.cover p{{font-size:13.5pt;color:var(--ink2);max-width:125mm;margin:6mm 0 0}}
.flow{{display:flex;align-items:center;gap:4mm;flex-wrap:wrap}}
.flow div{{background:rgba(255,255,255,.75);border-radius:5mm;padding:4mm 5mm}}
.flow b{{display:block;font-family:"Inter Display";font-size:22pt;letter-spacing:-.04em}}
.flow small{{color:var(--ink2)}}
.flow i{{font-style:normal;font-size:18pt;color:var(--clay)}}
.page{{page-break-after:always}}
h2.big{{font-size:20pt;margin:1.5mm 0 4mm}}
.rcs{{display:grid;grid-template-columns:1fr 1fr;gap:3.5mm}}
.rc{{background:var(--p);border-radius:4mm;padding:3.5mm 4.5mm;break-inside:avoid}}
.rc b{{font-family:"Inter Display";font-size:11.5pt}}
.rc p{{margin:1mm 0 1.5mm}}
.rc span{{font-family:"JetBrains Mono";font-size:7.6pt;color:var(--clay);text-transform:uppercase;letter-spacing:.05em}}
.rules{{margin:5mm 0 0;padding:4mm 5mm 4mm 9mm;background:#FBE9E2;border-radius:4mm}}
.rules li{{margin-bottom:1mm}}
.blk{{margin-bottom:6mm}}
.bh{{display:flex;gap:4mm;align-items:flex-start;border-top:.6mm solid var(--ink);padding-top:3mm;margin-bottom:2.5mm;break-after:avoid}}
.bh .code{{width:11mm;height:11mm;border-radius:3mm;background:var(--clay);color:#fff;display:grid;place-items:center;font-family:"Inter Display";font-weight:800;font-size:15pt;flex:none}}
.bh h2{{font-size:16pt}}
.bh p{{margin:1mm 0 0;color:var(--ink2);font-size:8.8pt;max-width:140mm}}
.bh .cnt{{margin-left:auto;font-family:"JetBrains Mono";font-size:8pt;color:var(--clay);white-space:nowrap}}
table.tk-t{{width:100%;border-collapse:collapse}}
.tk-t th{{text-align:left;font-family:"JetBrains Mono";font-size:7.2pt;color:var(--ink2);text-transform:uppercase;letter-spacing:.06em;font-weight:400;padding:1mm 1.5mm;border-bottom:.3mm solid var(--ink)}}
.tk-t td{{padding:1.5mm 1.5mm;border-bottom:.25mm solid var(--line);vertical-align:top}}
.tk-t tr{{break-inside:avoid}}
td.ck{{width:6mm}} td.n{{width:11mm;font-family:"JetBrains Mono";font-size:7.8pt;color:var(--clay)}}
td.tk .c{{color:var(--ink2)}} td.v{{width:24mm;color:var(--ink2)}} td.u{{width:62mm;color:var(--ink2);font-size:8.6pt}}
.box{{display:inline-block;width:3.4mm;height:3.4mm;border:.35mm solid var(--clay);border-radius:1mm}}
</style></head><body>
<div class="cover">
  <div style="display:flex;justify-content:space-between;align-items:center"><div class="am">AM</div><span class="mono">Multiplica Cortes · banco de takes</span></div>
  <div><span class="mono">Alê da Pele · dia de gravação</span><h1>Grave uma vez.<br><span>Use em 300<br>vídeos.</span></h1>
  <p>Reações, bordões, ganchos, cenas silenciosas, detalhes e transições: peças curtas e genéricas que se encaixam em qualquer conteúdo. Uma mão no queixo vira 50 reacts.</p></div>
  <div class="flow"><div><b>{total}</b><small>takes coringa</small></div><i>×</i><div><b>8</b><small>fórmulas de montagem</small></div><i>=</i><div><b>300+</b><small>vídeos possíveis</small></div></div>
</div>
<div class="page">
  <span class="mono">Como multiplicar</span><h2 class="big">8 fórmulas de montagem</h2>
  <div class="rcs">{rec}</div>
  <ul class="rules">{reg}</ul>
</div>
{''.join(secs)}
</body></html>'''

FOOTER = '<div style="font-family:Inter,sans-serif;font-size:7.5pt;color:#6E5A50;width:100%;padding:0 14mm;display:flex;justify-content:space-between"><span>Alê da Pele · Banco de takes reaproveitáveis</span><span><span class="pageNumber"></span>/<span class="totalPages"></span></span></div>'
JS = """
const { chromium } = require('playwright');
(async () => {
  const [src, out, footer] = process.argv.slice(2);
  const b = await chromium.launch(); const pg = await b.newPage();
  await pg.goto('file://' + src); await pg.waitForTimeout(300);
  await pg.pdf({path: out, format: 'A4', printBackground: true, displayHeaderFooter: true, headerTemplate: '<span></span>', footerTemplate: footer,
    margin: {top: '15mm', bottom: '15mm', left: '14mm', right: '14mm'}});
  await b.close();
})();
"""

def main():
    h = AQUI / '_banco.html'; h.write_text(build(), encoding='utf-8')
    js = AQUI / '_render.js'; js.write_text(JS)
    try:
        subprocess.run(['node', str(js), str(h), str(AQUI / 'banco-de-takes-ale.pdf'), FOOTER], check=True)
    finally:
        js.unlink(); h.unlink()

main()
print('ok', sum(len(b[3]) for b in BLOCOS), 'takes')
