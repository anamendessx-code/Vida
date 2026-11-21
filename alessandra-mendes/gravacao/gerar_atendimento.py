"""Gera o PDF 'Atendimento WhatsApp' da Alê: mensagens personalizadas e jornada.
Uso: python3 gerar_atendimento.py -> atendimento-whatsapp-ale.pdf
"""
import html, pathlib, subprocess
AQUI = pathlib.Path(__file__).parent
e = lambda s: html.escape(s, quote=False)

FLUXO = [
 ("1", "Chegou", "A cliente manda a mensagem pronta da página, da Lezinha ou do anúncio. Já vem com o nome, o interesse e às vezes o dia e o horário."),
 ("2", "Boas-vindas em até 5 min", "Mensagem pelo nome + áudio curto da Alê. Ela sente que foi esperada."),
 ("3", "Entender o caso", "Duas perguntas e um pedido de foto. Nada de preço antes de entender."),
 ("4", "Proposta personalizada", "O plano dela (Glass Skin, Protocolo AM ou melasma), com valor, horários e os 10% do dia."),
 ("5", "Confirmação", "Sinal no Pix, endereço, o que levar e lembrete na véspera."),
 ("6", "Acompanhamento", "Pós do dia seguinte, rotina com o nome dela, check-in semanal e foto do mês."),
]

MSGS = [
 ("Boas-vindas · Glass Skin", "Oi, {nome}! Que alegria te receber aqui 🤍 Sou a Alê. Vi que você quer o Glass Skin, a pele de vidro coreana que é o meu xodó. Antes de tudo, quero entender a sua pele: me conta o que mais te incomoda hoje? Se puder, me manda uma foto de frente, sem filtro, que eu olho com carinho."),
 ("Boas-vindas · Protocolo AM", "Oi, {nome}! Seja muito bem-vinda 🤍 Aqui é a Alê. O Protocolo AM é o meu peeling coreano de algas, sem ácidos, ótimo para manchas de acne, de sol e de melasma. Me conta: há quanto tempo essas manchas te incomodam? Manda uma foto de frente que eu já te digo como ele fica na sua pele."),
 ("Boas-vindas · Melasma", "{nome}, que bom que você chegou até mim 🤍 Melasma é a minha especialidade, e eu sei o quanto ele cansa. Me conta: ele já voltou depois de algum tratamento? Você usa anticoncepcional? Com essas respostas e uma foto, eu monto o seu plano."),
 ("Boas-vindas · Análise com IA", "Oi, {nome}! Vi que você fez a sua análise de pele com IA ✨ Agora quero completar com o meu olhar. Pode me mandar a mesma foto aqui? Eu te explico cada ponto que apareceu e o que eu faria por você."),
 ("Boas-vindas · Harmonização", "Oi, {nome}! Que alegria 🤍 Harmonização aqui é sempre natural: realçar você, nunca mudar quem você é. Me conta o que você gostaria de melhorar e manda uma foto de frente e uma de lado, que eu te explico o caminho com calma."),
 ("Boas-vindas · Goiânia", "Oi, {nome}! Seja bem-vinda 🤍 Estou atendendo no Setor Marista nos dias [datas]. As vagas são poucas, então já vou separar uma para você. Me conta o que você quer tratar?"),
 ("Áudio da Alê (30 s)", "“Oi, {nome}, aqui é a Alê! Que alegria você ter me chamado. Eu vi o que você me contou e quero muito te ajudar. Aqui você não vai fazer uma sessão e ficar sozinha: eu vou te acompanhar de verdade. Me manda uma fotinho da sua pele que eu já te respondo com o seu plano, tá? Um beijo.”"),
 ("Proposta", "{nome}, olhei a sua foto com atenção 🤍 O que eu vejo: [2 pontos]. O que eu faria: [protocolo] + rotina em casa + produto de manutenção para não voltar. Você terá o meu suporte aqui durante todo o tratamento. Investimento: [valor], com 10% OFF hoje, em até [x] vezes. Tenho [dia] às [hora] em [local]. Posso reservar para você?"),
 ("Confirmação", "Reservado, {nome}! 🥰 [dia] às [hora], em [Águas Claras / Setor Marista]. Para garantir a vaga, o sinal é de R$ [valor] no Pix (chave abaixo), abatido no dia. Venha sem maquiagem e traga uma foto dos produtos que você usa. Estou te esperando!"),
 ("Véspera", "Oi, {nome}! Amanhã é o seu dia ✨ [hora], em [local]. Aqui o endereço: [link]. Qualquer coisa, é só me chamar. Mal posso esperar para cuidar da sua pele!"),
 ("Dia seguinte", "Bom dia, {nome}! Como acordou a pele hoje? 🤍 Lembra: sabonete suave, hidratante e protetor com cor de 2 em 2 horas. Te mandei a sua rotina em PDF com o seu nome. Qualquer dúvida, eu estou aqui."),
 ("Check-in semanal", "{nome}, passando para saber de você 🤍 Está conseguindo seguir a rotina? Me manda uma foto rapidinha, de frente e na luz da janela, que eu acompanho a sua evolução."),
 ("Foto do mês", "{nome}, hoje faz um mês! 📸 Olha o seu antes e depois lado a lado. Estou muito orgulhosa de você. Vamos para a próxima fase?"),
 ("Reativação (sumiu)", "Oi, {nome}! Lembrei de você hoje 🤍 Ainda quer cuidar da sua pele? Separei uma condição especial esta semana. Se fizer sentido, é só me responder com um 'sim' que eu te mando os horários."),
]

IDEIAS = [
 ("Áudio com o nome", "A Alê grava o áudio de boas-vindas falando o nome da cliente. Leva 30 segundos e é o que mais encanta."),
 ("Rotina em PDF com o nome", "Cada cliente recebe a rotina dela, com o nome na capa e os produtos certos para o tipo de pele."),
 ("Relatório da Pele", "Depois da avaliação: fotos, pontos de atenção e plano em 3 fases, com a identidade da AM."),
 ("Kit de boas-vindas", "Nécessaire AM com amostras e um cartão escrito à mão no primeiro atendimento."),
 ("Antes e depois mensal", "Foto padronizada todo mês, enviada lado a lado. A cliente vê a evolução e indica."),
 ("Resposta em 5 minutos", "Horário comercial com resposta rápida. A Lezinha cobre a noite e o fim de semana."),
 ("Etiquetas no WhatsApp", "Lead novo, em conversa, agendada, cliente ativa, manutenção. Ninguém fica esquecida."),
 ("Datas especiais", "Aniversário da cliente e aniversário do início do tratamento, com um mimo."),
 ("Pesquisa de satisfação", "Uma pergunta depois de 30 dias: de 0 a 10, quanto você indicaria a Alê?"),
 ("Grupo de melhores amigas", "Close friends ou grupo VIP com bastidores, dicas e vagas antes de todo mundo."),
]

AUTO = [
 ("Hoje, sem custo", "WhatsApp Business com respostas rápidas: digite /glass, /am, /melasma e a mensagem aparece. Troque {nome} pelo nome que veio na primeira mensagem."),
 ("Próximo passo", "Uma ferramenta de WhatsApp com CRM (como Kommo, RD Station ou ManyChat) preenche o nome sozinha, marca o interesse e dispara o check-in e a véspera no dia certo."),
 ("Ligado à página", "O cadastro da página e da Lezinha já manda nome, WhatsApp e interesse. Quando a página estiver publicada, esses dados podem cair direto no CRM."),
]

def build():
    flx = ''.join(f'<div class="st"><span>{n}</span><b>{e(a)}</b><p>{e(b)}</p></div>' for n,a,b in FLUXO)
    msgs = ''.join(f'<div class="msg"><div class="t">{e(a)}</div><div class="bub">{e(b).replace("{nome}","<i>{nome}</i>")}</div></div>' for a,b in MSGS)
    ids = ''.join(f'<li><b>{e(a)}.</b> {e(b)}</li>' for a,b in IDEIAS)
    aut = ''.join(f'<div class="au"><b>{e(a)}</b><p>{e(b)}</p></div>' for a,b in AUTO)
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>
:root{{--p:#FAF6F2;--ink:#2B1F1A;--ink2:#6E5A50;--clay:#B9705A;--blush:#F3DCD2;--line:#E8DCD2;--wa:#DCF3D0}}
*{{box-sizing:border-box}} body{{margin:0;font-family:"Inter",sans-serif;color:var(--ink);font-size:9.8pt;line-height:1.45}}
h1,h2{{font-family:"Inter Display","Inter",sans-serif;letter-spacing:-.03em;margin:0}}
.mono{{font-family:"JetBrains Mono",monospace;font-size:8pt;letter-spacing:.08em;text-transform:uppercase;color:var(--clay)}}
.cover{{border-radius:8mm;background:radial-gradient(circle at 85% 10%,#F7C9B2,transparent 45%),radial-gradient(circle at 10% 90%,#EAD3AE,transparent 45%),var(--p);padding:14mm;margin-bottom:7mm}}
.cover h1{{font-size:36pt;line-height:.98;margin:3mm 0}} .cover h1 span{{color:var(--clay)}}
.cover p{{font-size:12pt;color:var(--ink2);margin:0;max-width:150mm}}
h2{{font-size:17pt;margin:2mm 0 3mm}}
.flow{{display:grid;grid-template-columns:repeat(3,1fr);gap:3mm;margin-bottom:7mm}}
.st{{background:var(--p);border-radius:4mm;padding:3.5mm 4mm}}
.st span{{display:inline-grid;place-items:center;width:7mm;height:7mm;border-radius:50%;background:var(--clay);color:#fff;font-weight:700;font-size:9pt}}
.st b{{display:block;margin-top:1.5mm;font-size:11pt}} .st p{{margin:1mm 0 0;color:var(--ink2);font-size:9pt}}
.msgs{{columns:2;column-gap:5mm}}
.msg{{break-inside:avoid;margin-bottom:4mm}}
.msg .t{{font-family:"JetBrains Mono";font-size:7.6pt;color:var(--clay);text-transform:uppercase;letter-spacing:.06em;margin-bottom:1mm}}
.bub{{background:var(--wa);border-radius:3.5mm 3.5mm 3.5mm 1mm;padding:3mm 3.5mm;font-size:9.4pt}}
.bub i{{font-style:normal;background:#fff;border-radius:1.5mm;padding:0 1.2mm;color:var(--clay);font-weight:700}}
.pg{{page-break-before:always}}
ul.ids{{columns:2;column-gap:6mm;padding-left:4.5mm;margin:0}} ul.ids li{{break-inside:avoid;margin-bottom:2mm}}
.aus{{display:grid;grid-template-columns:repeat(3,1fr);gap:3mm;margin-top:3mm}}
.au{{background:var(--p);border-radius:4mm;padding:3.5mm 4mm}} .au p{{margin:1mm 0 0;color:var(--ink2);font-size:9pt}}
.note{{font-size:8.6pt;color:var(--ink2);margin-top:3mm}}
</style></head><body>
<div class="cover"><span class="mono">Alê da Pele · atendimento</span><h1>Cada cliente recebida<br><span>como única.</span></h1>
<p>Mensagens pelo nome, áudio da Alê e acompanhamento de verdade, do primeiro "oi" ao antes e depois do mês. A cliente chega com interesse e sai querendo indicar.</p></div>
<span class="mono">A jornada</span><h2>Do primeiro “oi” ao acompanhamento</h2><div class="flow">{flx}</div>
<span class="mono">Copiar e colar</span><h2>Mensagens prontas (troque <i style="font-style:normal;color:#B9705A">{{nome}}</i> pelo nome)</h2>
<div class="msgs">{msgs}</div>
<div class="pg"><span class="mono">Para impressionar</span><h2>10 ideias para o atendimento ser inesquecível</h2><ul class="ids">{ids}</ul>
<span class="mono" style="display:block;margin-top:6mm">Automação</span><h2>Como o nome entra sozinho</h2><div class="aus">{aut}</div>
<p class="note">Antes e depois e fotos da cliente só com autorização. Nada de promessa de cura ou resultado garantido. Valores e condições sempre por escrito.</p></div>
</body></html>'''

FOOTER = '<div style="font-family:Inter,sans-serif;font-size:7.5pt;color:#6E5A50;width:100%;padding:0 14mm;display:flex;justify-content:space-between"><span>Alê da Pele · Atendimento no WhatsApp</span><span><span class="pageNumber"></span>/<span class="totalPages"></span></span></div>'
JS = """
const { chromium } = require('playwright');
(async () => { const [src, out, footer] = process.argv.slice(2); const b = await chromium.launch(); const pg = await b.newPage();
  await pg.goto('file://' + src); await pg.waitForTimeout(300);
  await pg.pdf({path: out, format: 'A4', printBackground: true, displayHeaderFooter: true, headerTemplate: '<span></span>', footerTemplate: footer, margin: {top: '14mm', bottom: '15mm', left: '14mm', right: '14mm'}});
  await b.close(); })();
"""
h = AQUI / '_at.html'; h.write_text(build(), encoding='utf-8'); js = AQUI / '_r.js'; js.write_text(JS)
try: subprocess.run(['node', str(js), str(h), str(AQUI / 'atendimento-whatsapp-ale.pdf'), FOOTER], check=True)
finally: js.unlink(); h.unlink()
print('ok')
