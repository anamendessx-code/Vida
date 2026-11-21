"""Gera o PDF '300 ideias para gravar' da Alê (Multiplica Cortes).

Uso: python3 gerar_pdf.py  ->  300-ideias-gravacao-ale.pdf (nesta pasta)
"""
import html, pathlib, subprocess, json

AQUI = pathlib.Path(__file__).parent

# (código, título, onde, look, formatos, ideias)
CATS = [
 ("A", "Melasma · falas de autoridade", "Fundo neutro ou janela", "Look 1 · jaleco AM", "Reels", [
  '"Seu melasma não voltou do nada": os 5 gatilhos',
  '"O erro que mais vejo em quem tem melasma"',
  '"Por que o melasma piora no verão… e no inverno também"',
  '"Luz do celular mancha?" A verdade',
  'Protetor com cor ou sem cor para melasma?',
  '"Melasma tem cura?" A resposta honesta',
  'Calor do fogão, academia e carro: o gatilho escondido',
  'Anticoncepcional e melasma: o que conversar com o seu médico',
  'Por que a mancha volta quando você para o tratamento',
  '"3 coisas que eu nunca faço em pele com melasma"',
  'Melasma × mancha de sol: como diferenciar no espelho',
  'O produto de manutenção que segura o resultado',
  'Quanto tempo leva para clarear melasma',
  'Gravidez e melasma: o que fazer e o que esperar',
  'Reaplicar protetor por cima da maquiagem: como eu ensino',
  '"Melasma em homem existe?" Existe, sim',
  '"Laser resolve melasma?" Por que às vezes piora',
  'História: a cliente que chorou ao ver a foto do mês 3',
  'Brasília seca + sol forte = melasma: cuidado extra',
  '"Se você tem melasma, salva esse vídeo"',
 ]),
 ("B", "Mito ou verdade", "Fundo neutro · placas MITO / VERDADE", "Look 1", "Reels · Carrossel", [
  'Limão clareia mancha', 'Pasta de dente seca espinha', 'Protetor só em dia de sol',
  'Pele oleosa não precisa de hidratante', 'Espremer cravo em casa não tem problema', 'Água quente limpa melhor o rosto',
  'Quanto mais ácido, mais rápido clareia', 'Maquiagem causa acne', 'Bicarbonato tira mancha',
  'Pele negra não precisa de protetor', 'Peeling só no inverno', 'Limpeza de pele abre os poros',
  'Chocolate dá espinha', 'Toxina trava o rosto', 'Preenchimento deixa boca de pato',
  'Skincare de 10 passos é melhor', 'Gelo no rosto fecha poro', 'Sabonete de glicerina serve para todo mundo',
  'Vitamina C de dia mancha', 'Protetor de corpo serve no rosto', 'Pele fina não pode fazer microagulhamento',
  'Dormir de maquiagem uma noite não faz mal', 'Rosa mosqueta tira melasma', 'Celular encostado no rosto dá espinha',
  '"Glass skin é só filtro"',
 ]),
 ("C", "Glass Skin", "Maca + LED + bancada coreana", "Look 1 · com cliente/modelo autorizada", "Reels · Stories", [
  '"Fiz Glass Skin": o passo a passo em 30 s (time-lapse)', 'Abrindo a caixa dos cosméticos coreanos', 'ASMR: a espuma da limpeza coreana',
  'A máscara que deixa a pele de vidro (close)', 'LED: por que essa cor? (close das luzes)', 'Antes e depois na luz da janela (com autorização)',
  '"Pele de vidro não é brilho, é textura"', 'POV: você saindo do Glass Skin e passando a mão no rosto', 'O que vem no home care do Glass Skin (flat lay)',
  'Por que o peeling vem na sessão seguinte', 'O produto de manutenção em 15 s', '"Glass Skin para quem tem melasma pode?"',
  '"Coreana não tem segredo, tem rotina"', 'A reação da cliente no espelho (som original)', 'Quanto tempo dura o efeito glass',
  'Glass Skin antes de evento: quantos dias antes', 'Os 6 passos do Glass Skin (fotos para carrossel)', 'Glass Skin × limpeza comum: a diferença',
  'Transição: pele opaca → pele de vidro (corte no estalo)', '"Esse é o protocolo que eu faria na minha filha" (com a Ana)',
 ]),
 ("D", "Protocolo AM", "Maca · close das algas", "Look 1", "Reels · Stories", [
  '"Peeling sem ácido existe?"', 'Close das algas na mão e no pincel (textura)', 'ASMR aplicando o peeling de algas',
  'Para quem é o Protocolo AM', '"Ardeu?" A reação real da cliente', 'Antes e depois das manchas de acne (com autorização)',
  'Protocolo AM antes de casamento ou formatura', '"Por que eu criei o Protocolo AM"', 'O que fazer nos 3 dias depois',
  'Protocolo AM × peeling químico', 'Mancha de sol: uma sessão já muda o tom?', 'A pele antes e depois na lupa',
  'Mostrando o produto de algas embalado', '"Posso fazer no verão?"', 'Série "AM em 1 minuto": uma dúvida por vídeo',
 ]),
 ("E", "Procedimentos e técnica", "Maca + bancada", "Look 1", "Reels", [
  'Limpeza de pele: extração com técnica (ASMR)', 'Vapor de ozônio em câmera lenta', '"Isso é limpeza de pele?" (Ana de cobaia)',
  'Microagulhamento + vitamina C: passo a passo', 'Close da caneta de microagulhamento', 'Por que a vitamina C turbina o microagulhamento',
  'BB Glow: o glow na hora', 'Blindagem da pele: a máscara de hidratação', 'Lupa: "o que eu vejo que você não vê"',
  'Como eu tiro as fotos padronizadas da sua pele', 'A avaliação facial passo a passo (com a Ana)', 'Tour pela minha bancada',
  'Esterilização dos materiais', 'Montando a sala para a cliente (time-lapse)', 'Luva, touca e máscara: o protocolo de higiene',
  'O som do consultório (ASMR)', 'A cliente relaxando: a música da sala', '"Quanto tempo dura uma limpeza?" (timer na tela)',
  'Oleosa × seca × mista: teste do papel', 'Teste do lenço: descubra sua pele', 'A quantidade certa de protetor (2 dedos)',
  'Poros antes e depois da limpeza (close)', 'Vermelhidão normal × não normal depois do procedimento', '"Não aperta isso em casa": por quê',
  'Escova, esponja, algodão: o que eu uso e o que não uso',
 ]),
 ("F", "Harmonização e toxina · explicações", "Espelho + lápis branco", "Look 1", "Reels · Carrossel", [
  'Full face natural: harmonizar sem mudar você', 'Os terços do rosto medidos com régua no espelho', 'Uma sobrancelha mais alta: linha na tela mostrando',
  'Malar: sustentação e efeito lifting (desenho com lápis branco)', 'Mento: por que o queixo muda o perfil', 'Mandíbula: contorno sem exagero',
  'Têmporas: o detalhe que rejuvenesce', 'Olheira funda × olheira escura', 'Lábios naturais: contorno × volume',
  'Rinomodelação explicada com desenho', 'Testa, glabela e pés de galinha: onde a toxina age', '"Toxina trava?" Mostrando a expressão natural',
  'Mapeamento facial com lápis branco (muito visual)', 'Simetria medida pela IA na tela do celular', 'Por que começar pela pele antes da harmonização',
 ]),
 ("G", "Rotina e produtos", "Bancada de produtos", "Look 2 · roupa creme", "Reels · Carrossel", [
  'Minha rotina da manhã em 60 s', 'Minha rotina da noite em 60 s', 'Rotina para pele oleosa', 'Rotina para pele seca', 'Rotina para pele mista',
  'Rotina para quem tem melasma', 'Rotina para acne adulta', 'Rotina de 3 passos para quem tem preguiça', 'A ordem certa dos produtos',
  'Quanto produto usar (demonstração na mão)', 'O produto que eu jogaria fora hoje', '3 produtos baratos que funcionam', 'O protetor ideal para cada pele',
  'Kit de viagem da esteticista', 'O que tem na minha nécessaire', 'Skincare para homem em 3 passos', 'Rotina para adolescente (para os pais)',
  'Rotina depois do procedimento', 'Vitamina C: manhã ou noite?', 'Niacinamida: para quem serve', 'Ceramidas: por que eu amo',
  'Esfoliar quantas vezes por semana?', 'Água micelar: quando usar', 'Lavar o rosto do jeito certo em 30 s', 'Validade do protetor e onde guardar',
 ]),
 ("H", "Trends, humor e ideias bestas", "Qualquer canto · celular na mão", "Look 3 · casual", "Reels · Stories", [
  '"Coisas que esteticista não aguenta ouvir" (dublagem)', 'POV: a cliente que espremeu a espinha antes de vir', 'POV: a cliente que esqueceu o protetor na praia',
  'Ana fingindo ser a cliente difícil', '"Minha filha foi cobaia de novo"', 'Dublagem de áudio viral de jaleco',
  'Trend da transição: casual → jaleco', 'Reagindo a skincare de influencer (dueto)', 'Reagindo a receita caseira do TikTok (limão, pasta de dente)',
  'Testando produto viral: funciona ou não?', 'Adivinhe o produto pelo cheiro (Ana vendada)', '"Tipos de cliente": a pontual, a atrasada, a ansiosa',
  'Esteticista olhando pele em todo lugar (mercado, festa)', '"Quando a cliente diz que usa protetor todo dia"', 'O meme do Yoda do peeling, agora em vídeo',
  'O pet "fazendo skincare" (se tiver)', 'Dancinha curta com a Ana', 'Expectativa × realidade do skincare',
  'Quiz na tela: "você sabe seu tipo de pele?"', 'Unboxing exagerado do pedido de produtos', 'ASMR silencioso arrumando a bancada',
  '"Um dia na vida da Alê" (vlog em cortes)', '"Antes de sair de casa × depois do Glass Skin"', 'Frase do dia falada bem rápido',
  '"Se a sua pele falasse…" (voz engraçada)', 'Reagindo a uma foto antiga dela, de 30 anos atrás', '"Errei!": os erros de gravação',
  'Trend "nunca fiz isso" com procedimentos', 'Ping-pong: a Alê responde com uma palavra', '"Esteticista explica como se você tivesse 5 anos"',
 ]),
 ("I", "Bastidores do consultório", "Consultório inteiro", "Look 2", "Stories · Reels", [
  'Abrindo o consultório de manhã (chave, luz, café)', 'Tour pelo consultório em 20 s', 'O cantinho favorito da Alê',
  'Detalhes: toalhas dobradas, flores, aroma', 'Café com a Alê antes da primeira cliente', 'Recebendo a cliente na porta',
  'A agenda do dia (sem nomes)', 'Fim de expediente: a sala organizada', 'Lavando os pincéis',
  'Repondo produtos', 'A playlist do consultório', 'Arrumando a mala de atendimento para Goiânia',
  'Chegando no Setor Marista (no dia da viagem)', 'Águas Claras: a rua e a vista do consultório', 'Making of desta gravação',
  'A maca vista de cima (top shot)', 'Escrevendo um cartão para a cliente', 'Embalando o home care para entrega',
  'Mensagens de clientes chegando (prints autorizados)', 'O silêncio da sala antes do atendimento',
 ]),
 ("J", "História e humanização", "Sentada, luz da janela", "Look 2", "Reels", [
  'Por que eu escolhi a estética há 30 anos', 'Minha primeira cliente', 'O erro que mais me ensinou',
  'Por que eu me apaixonei pelo melasma', 'O que me emociona nesse trabalho', 'Mãe e esteticista: a Ana na minha vida',
  'Um conselho para a Alê de 20 anos', 'O que eu faço na minha folga', 'Minha rotina de pele pessoal',
  '3 coisas que ninguém sabe sobre mim', 'O que mudou na estética em 30 anos', 'Por que eu não prometo milagre',
  'A cliente que voltou depois de anos', 'Meu ritual antes de atender', 'O que significa "Alê da pele"',
  'Como eu cuido da cliente ansiosa', 'O dia mais difícil da minha carreira', 'O que eu sinto ao ver um antes e depois',
  'Para quem tem vergonha da própria pele', '"30 anos em 30 segundos": obrigada',
 ]),
 ("K", "Perguntas da caixinha", "Fundo neutro · texto da pergunta na tela", "Look 2", "Reels · Stories", [
  'Posso fazer limpeza menstruada?', 'Grávida pode fazer o quê?', 'Quanto tempo entre uma limpeza e outra?', 'Posso pegar sol depois do peeling?',
  'Pode malhar depois do procedimento?', 'Maquiagem depois da limpeza?', 'Quantas sessões para melasma?', 'Microagulhamento dói?',
  'Homem pode fazer Glass Skin?', 'Idade mínima para limpeza de pele?', 'Tomo Roacutan, e agora?', 'Tenho rosácea, posso?',
  'Pele negra pode fazer peeling?', '"Quanto custa?" (avaliação + link)', 'Atende em Goiânia?', 'Parcela?',
  'Como agendar em 1 minuto (WhatsApp e Lezinha)', '"Faço skincare e nada muda", por quê?', 'Por que minha pele descama?', 'Devo trocar de produto toda hora?',
 ]),
 ("L", "Lezinha e análise com IA", "Celular gravando a tela + Alê", "Look 2", "Reels · Stories", [
  '"Conheça a Lezinha, minha assistente"', 'A análise com IA na Ana (tela gravada)', '"A IA viu isso no meu rosto": reação',
  'Pergunta para a Lezinha ao vivo', 'Como liberar sua análise grátis', 'IA × olho da esteticista: quem acertou?',
  '"A Lezinha responde até às 3 da manhã" (humor)', 'Simetria do rosto medida pela IA', 'Antes e depois simulado × real',
  '"Manda sua foto que eu analiso"',
 ]),
 ("M", "Ofertas e chamadas", "Fundo neutro · fala direta 10 s", "Looks 1, 2 e 3 (variar)", "Reels · Stories", [
  '"Hoje tem 10% OFF" (gravar 5 variações)', 'A agenda aberta da semana', 'Últimas vagas em Goiânia', 'O presente para quem agendar hoje (rotina embalada)',
  '"Me chama no WhatsApp com a palavra GLASS"', '"Comenta MANCHA que eu te mando o teste"', 'Indique uma amiga', 'Glass Skin de presente (datas comemorativas)',
  'O combo do mês', 'Contagem regressiva da oferta (stories)', 'Prova social: agenda cheia (sem nomes)', '"Vaga liberada amanhã às 14h"',
  'Chamada para a análise grátis', 'Chamada Águas Claras', 'Chamada Setor Marista',
 ]),
 ("N", "Fotos", "Janela, bancada, maca", "Looks 1, 2 e 3", "Foto", [
  'Retrato de frente sorrindo, jaleco, fundo neutro (perfil)', 'Meio corpo, braços cruzados (autoridade)', 'Olhando a pele da cliente na lupa',
  'Mãos aplicando produto (close)', 'Mãos segurando frasco coreano', 'Flat lay do home care na toalha branca',
  'Bancada organizada (plano aberto)', 'Detalhe: logo AM, cartão e flores', 'Na janela, luz natural (editorial)',
  'Rindo de verdade (espontânea)', 'Perfil 3/4 pensativa', 'Com a Ana (mãe e filha)',
  'Atendendo (plano aberto, cliente de costas)', 'LED ligado (cor dramática)', 'Máscara na cliente, vista de cima',
  'Pele de vidro em close (luz lateral)', 'Escrevendo a rotina da cliente', 'Segurando o celular com a análise de IA',
  '10 expressões para capas de Reels', 'Apontando para cima (espaço para texto)', 'Apontando para o lado (texto lateral)',
  'Mão no queixo (dúvida)', 'Segurando as placas MITO e VERDADE', 'Foto para a página de vendas (espaço para texto)',
  'Fotos para os destaques do Instagram', 'Montagem da luz de antes e depois + marca no chão', 'Fachada e entrada',
  'Looks 2 e 3 para variar o feed', 'Textura dos produtos (swatch)', 'Editorial em preto e branco',
 ]),
 ("O", "Séries recorrentes", "Gravar 3 episódios de cada", "Variar", "Reels", [
  '"Segunda do melasma"', '"Mito da quarta"', '"Sexta do Glass"', '"Pergunta da caixinha" (diária)', '"Antes de dormir com a Alê"',
  '"1 minuto de pele"', '"A Ana pergunta, a Alê responde"', '"Resultado da semana" (com autorização)', '"O que eu faria na sua pele"',
  '"Diário do tratamento": uma cliente por 12 semanas',
 ]),
]
assert sum(len(c[5]) for c in CATS) == 300, sum(len(c[5]) for c in CATS)

CRONO = [
 ("7h30", "Montagem", "Luz na janela ou ring light, lapela testada, lentes limpas, bancada organizada, sacolas e fios fora do quadro."),
 ("8h00", "Fotos · look 1", "Bloco N (fotos 1 a 15): retratos, mãos, bancada, capas de Reels."),
 ("8h45", "Falas · look 1", "Blocos A, B e F. Gravar cada gancho 3 vezes. Placas MITO e VERDADE prontas."),
 ("10h30", "Procedimentos · look 1", "Blocos C, D e E com a Ana e 2 clientes ou modelos autorizadas."),
 ("12h30", "Almoço + Stories", "Bastidores do bloco I com o segundo celular."),
 ("13h30", "Bancada · look 2", "Blocos G e L (rotina, produtos, Lezinha e análise com IA)."),
 ("15h00", "Humor · look 3", "Bloco H com a Ana. Áudios virais baixados antes."),
 ("16h00", "História · look 2", "Blocos J e K, sentada na luz da janela."),
 ("17h00", "Fechamento", "Blocos M e O, fotos 16 a 30 e regravação dos ganchos que ficaram fracos."),
]
CHECK = [
 "3 looks: jaleco AM, roupa creme, casual", "Maquiagem leve e cabelo pronto", "2 celulares carregados + powerbank", "Tripé + suporte de mesa",
 "2 microfones de lapela", "Ring light ou luz de janela", "Espelho de mão e lupa", "Placas MITO e VERDADE",
 "Cosméticos coreanos, algas, máscaras e LED", "Home care embalado (para flat lay)", "Toalhas brancas e flores", "Lápis branco (mapeamento)",
 "Termo de autorização de imagem impresso", "Lista de áudios virais salvos", "Água e lanche", "Este PDF impresso para ir marcando",
]
REGRAS = [
 "Vertical, 4K, 30 fps. Celular na altura dos olhos.",
 "Gancho nos 3 primeiros segundos. Gravar 3 versões de cada gancho.",
 "Uma ideia por vídeo. Respirar 2 s antes de começar e depois de terminar (facilita o corte).",
 "Olhar para a lente, não para a tela.",
 "Falas longas (2 a 5 min) rendem de 3 a 5 cortes cada.",
 "Nada de preço em vídeo: a chamada é sempre WhatsApp, análise grátis ou Lezinha.",
]
CUIDADOS = [
 "Cliente ou modelo só aparece com autorização de imagem assinada.",
 "Antes e depois só de clientes reais, com autorização e a mesma luz.",
 "Sem promessa de cura ou resultado garantido.",
 "Harmonização e toxina: só mostrar quem é habilitado para fazer.",
]

def e(s): return html.escape(s, quote=False)

def build():
    n = 0; cats = []
    for code, title, onde, look, fmt, ideas in CATS:
        items = []
        for it in ideas:
            n += 1
            items.append(f'<li><span class="box"></span><span class="num">{n:03d}</span><span class="txt">{e(it)}</span></li>')
        cats.append(f'''<section class="cat"><div class="cat-h"><span class="code">{code}</span><div><h2>{e(title)}</h2>
          <div class="meta"><span>📍 {e(onde)}</span><span>👗 {e(look)}</span><span>🎬 {e(fmt)}</span><span>{len(ideas)} ideias</span></div></div></div>
          <ol class="list">{''.join(items)}</ol></section>''')
    crono = ''.join(f'<tr><td class="t">{a}</td><td class="b">{e(b)}</td><td>{e(c)}</td></tr>' for a,b,c in CRONO)
    check = ''.join(f'<li><span class="box"></span>{e(x)}</li>' for x in CHECK)
    regras = ''.join(f'<li>{e(x)}</li>' for x in REGRAS)
    cuid = ''.join(f'<li>{e(x)}</li>' for x in CUIDADOS)
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>
@page{{size:A4;margin:16mm 14mm 16mm 14mm}}
:root{{--p:#FAF6F2;--ink:#2B1F1A;--ink2:#6E5A50;--clay:#B9705A;--blush:#F3DCD2;--line:#E8DCD2}}
*{{box-sizing:border-box}}
body{{margin:0;font-family:"Inter",sans-serif;color:var(--ink);font-size:10.2pt;line-height:1.45}}
h1,h2,h3{{font-family:"Inter Display","Inter",sans-serif;letter-spacing:-.03em;margin:0}}
.mono{{font-family:"JetBrains Mono",monospace;font-size:8pt;letter-spacing:.08em;text-transform:uppercase;color:var(--clay)}}
.cover{{height:265mm;border-radius:10mm;background:radial-gradient(circle at 85% 10%,#F7C9B2,transparent 45%),radial-gradient(circle at 10% 90%,#EAD3AE,transparent 45%),var(--p);padding:18mm 16mm;display:flex;flex-direction:column;justify-content:space-between;page-break-after:always}}
.cover .am{{width:16mm;height:16mm;border-radius:50%;background:var(--ink);color:var(--p);display:grid;place-items:center;font-weight:700;font-size:12pt}}
.cover h1{{font-size:54pt;line-height:.92;font-weight:800}}
.cover h1 span{{color:var(--clay)}}
.cover p{{font-size:14pt;color:var(--ink2);max-width:120mm;margin:6mm 0 0}}
.stats{{display:flex;gap:8mm}}
.stats div{{background:rgba(255,255,255,.7);border-radius:5mm;padding:5mm 6mm}}
.stats b{{display:block;font-family:"Inter Display";font-size:26pt;letter-spacing:-.04em}}
.stats small{{color:var(--ink2)}}
.page{{page-break-after:always;font-size:9.2pt}}
.page h2{{font-size:17pt!important}}
.sec{{margin-bottom:4.5mm}}
.sec h2{{font-size:20pt;margin:2mm 0 3mm}}
table{{width:100%;border-collapse:collapse}}
td{{padding:1.5mm 2mm;border-bottom:.3mm solid var(--line);vertical-align:top}}
td.t{{font-family:"JetBrains Mono";color:var(--clay);white-space:nowrap;width:16mm}}
td.b{{font-weight:700;white-space:nowrap;width:42mm}}
.two{{display:grid;grid-template-columns:1fr 1fr;gap:7mm}}
ul.ck{{list-style:none;padding:0;margin:0;columns:2;column-gap:6mm}}
ul.ck li{{display:flex;gap:2.5mm;align-items:flex-start;margin-bottom:1.2mm;break-inside:avoid}}
.box{{width:3.6mm;height:3.6mm;border:.35mm solid var(--clay);border-radius:1mm;flex:none;margin-top:.6mm}}
.card{{background:var(--p);border-radius:5mm;padding:3.5mm 5mm}}
.card ul{{margin:0;padding-left:5mm}}
.card li{{margin-bottom:.8mm}}
.warn{{background:#FBE9E2}}
.cat{{margin-bottom:6mm}}
.cat-h{{display:flex;gap:4mm;align-items:center;border-top:.6mm solid var(--ink);padding-top:3mm;margin-bottom:3mm;break-after:avoid}}
.cat-h .code{{width:11mm;height:11mm;border-radius:3mm;background:var(--clay);color:#fff;display:grid;place-items:center;font-family:"Inter Display";font-weight:800;font-size:15pt;flex:none}}
.cat-h h2{{font-size:17pt}}
.meta{{display:flex;flex-wrap:wrap;gap:2mm 5mm;font-size:8.6pt;color:var(--ink2);margin-top:1mm}}
ol.list{{list-style:none;padding:0;margin:0;columns:2;column-gap:7mm}}
ol.list li{{display:flex;gap:2.4mm;align-items:flex-start;padding:1.6mm 0;border-bottom:.25mm solid var(--line);break-inside:avoid}}
.num{{font-family:"JetBrains Mono";font-size:8pt;color:var(--clay);padding-top:.4mm;flex:none}}
.txt{{flex:1}}
</style></head><body>
<div class="cover">
  <div style="display:flex;justify-content:space-between;align-items:center"><div class="am">AM</div><span class="mono">Multiplica Cortes · dia de gravação</span></div>
  <div><span class="mono">Alê da Pele · Águas Claras e Setor Marista</span><h1>300 ideias<br>para gravar<br><span>amanhã.</span></h1>
  <p>Vídeos, fotos e até umas ideias bestas para transformar um dia de consultório em semanas de conteúdo, um corte por dia.</p></div>
  <div class="stats"><div><b>300</b><small>ideias numeradas</small></div><div><b>15</b><small>blocos de gravação</small></div><div><b>+400</b><small>cortes possíveis</small></div></div>
</div>
<div class="page">
  <div class="sec"><span class="mono">O dia</span><h2>Cronograma de gravação</h2><table>{crono}</table></div>
  <div class="two">
    <div class="sec"><span class="mono">Levar</span><h2>Checklist</h2><ul class="ck">{check}</ul></div>
    <div>
      <div class="card sec"><span class="mono">Regras de ouro</span><ul>{regras}</ul></div>
      <div class="card warn"><span class="mono">Cuidados obrigatórios</span><ul>{cuid}</ul></div>
    </div>
  </div>
</div>
{''.join(cats)}
</body></html>'''

FOOTER = '<div style="font-family:Inter,sans-serif;font-size:7.5pt;color:#6E5A50;width:100%;padding:0 14mm;display:flex;justify-content:space-between"><span>Alê da Pele · 300 ideias para gravar</span><span><span class="pageNumber"></span>/<span class="totalPages"></span></span></div>'
JS = """
const { chromium } = require('playwright');
(async () => {
  const [src, out, footer] = process.argv.slice(2);
  const b = await chromium.launch(); const pg = await b.newPage();
  await pg.goto('file://' + src); await pg.waitForTimeout(300);
  await pg.pdf({path: out, format: 'A4', printBackground: true, displayHeaderFooter: true, headerTemplate: '<span></span>', footerTemplate: footer,
    margin: {top: '16mm', bottom: '16mm', left: '14mm', right: '14mm'}});
  await b.close();
})();
"""

def main():
    html_path = AQUI / '300-ideias.html'; html_path.write_text(build(), encoding='utf-8')
    js = AQUI / '_render.js'; js.write_text(JS)
    try:
        subprocess.run(['node', str(js), str(html_path), str(AQUI / '300-ideias-gravacao-ale.pdf'), FOOTER], check=True)
    finally:
        js.unlink(); html_path.unlink()

main()
print('ok')
