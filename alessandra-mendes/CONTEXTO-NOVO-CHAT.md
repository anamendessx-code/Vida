# Contexto para continuar o projeto Alê da Pele

Sou da agência que cuida do posicionamento da **Alessandra Mendes, a "Alê da Pele"**. Ela é esteticista especialista em melasma e atende em **Águas Claras (Brasília-DF)** e no **Setor Marista (Goiânia-GO)**. WhatsApp (61) 99114-0713, Instagram @alessandramendes.x.

**Objetivo:** tornar a Alê referência, com imagem premium e profissional. Entre 20 profissionais, a cliente tem que lembrar dela e querer ser atendida por ela.

**Missão (usar no tom de tudo):** "Não é para vender produto. É acompanhar pessoas, devolver a autoestima e fazer elas voltarem a confiar em profissionais da estética." O diferencial é o **acompanhamento real**: avaliação, rotina para casa com o nome da cliente, produto de manutenção e suporte pelo WhatsApp.

## Onde está tudo

Repositório `anamendessx-code/Vida`, branch `claude/keen-davinci-gycv8v`, pasta `alessandra-mendes/`. O `README.md` da pasta lista todos os arquivos.

| O quê | Arquivo |
|---|---|
| Pesquisa de dores (melasma que volta) | `01-pesquisa-dores.md` |
| Método Multiplica Cortes aplicado | `02-metodo-multiplica-cortes.md` |
| Funil e CRM | `03-funil-e-crm.md`, `crm/crm_alessandra_modelo.csv` |
| Quiz + estratégia de tráfego | `04-quiz-e-trafego.md` |
| Direção visual aprovada | `prototipo/direcao-visual.html` |
| Página de vendas | `prototipo/pagina-de-vendas.html` (+ `prototipo/banco/`) |
| Quiz de qualificação (versão mais recente) | `prototipo/quiz.html` (+ `prototipo/quiz/`) |
| Espelho da Pele (análise por foto com IA) | `prototipo/analise-de-pele.html` (+ `prototipo/espelho/` com face-api) |
| Protótipo do CRM e funil | `prototipo/crm-funil.html` |
| Banco de antes e depois (CC BY) | `prototipo/banco-antes-depois.html` |
| PDFs de gravação | `gravacao/300-ideias-gravacao-ale.pdf`, `gravacao/banco-de-takes-ale.pdf` |
| Atendimento no WhatsApp (mensagens com o nome) | `gravacao/atendimento-whatsapp-ale.pdf` |
| Vídeo motion "Acompanhamento real" (57 s, 9:16) | `motion-acompanhamento/ACOMPANHAMENTO_REAL_ALE.mp4` (scripts em `scripts/`) |

Páginas publicadas (privadas, só a dona da conta abre):
- Quiz: https://claude.ai/artifact/M1FDaPj3jntcAUC5huWaFU (com `#exemplo` no fim mostra um resultado pronto)
- Página de vendas: https://claude.ai/artifact/XwN3NvapCG6B6AQU6RH4Zu
- Direção visual: https://claude.ai/artifact/WfoGk267VRCJNR52Qwj1vz
- Espelho da Pele: https://claude.ai/artifact/6w5gF46s4C2wpDXyexz23z
- CRM e funil: https://claude.ai/artifact/9MJrM97Azo3Uf1hsMYyKu7
- Banco de antes e depois: https://claude.ai/artifact/3AQ7orA5iHeeUUjetMSrBL

## Regras de estilo (já aprovadas)

- Tons claros do estúdio AM: porcelana `#FAF6F2`, tinta `#2B1F1A`, argila `#B9705A` / `#97523E`, blush `#F3DCD2`, pêssego `#F7C9B2`, champagne `#EAD3AE`.
- Fonte Plus Jakarta Sans. Visual moderno de site/IA, com animações. **Nada com cara de Canva**, nada escuro e nada de boneca/desenho: tudo realista.
- **Mais inclusivo para pessoas mais velhas:** letra grande, botões grandes, palavras simples, botão "Letra maior" e botão "Ouvir".
- Muitos CTAs para o WhatsApp, oferta de 10% OFF hoje com contagem regressiva.
- Protocolos da Alê:
  - **Glass Skin:** limpeza profunda com produtos coreanos, máscaras, LED, peeling, home care, produto de manutenção e rotina por tipo de pele.
  - **Protocolo AM:** peeling coreano de algas, sem ácidos.
- Não mostrar contatos de dermatologista ou parceiros: a Alê passa isso no privado.
- Lezinha é a assistente virtual da página (responde dúvidas e passa para o WhatsApp).

## Cuidados legais

- Sem promessa de cura ou de resultado garantido.
- Antes e depois só com autorização por escrito da cliente.
- Imagens de estudos científicos marcadas como "ilustrativo".
- Injetáveis: "feito por profissional habilitado".
- LGPD: autorização obrigatória antes de pegar o contato.

## O que falta fazer

1. **Quiz:** trocar o preço de entrada (hoje "R$ 350", só exemplo, em `CONFIG.precoAPartir`) pelo valor real.
2. **Publicar em link público** (domínio da Alê, Vercel ou Netlify) com o pixel do Meta. O quiz já dispara `QuizIniciado`, `QuizConcluido`, `LeadQualificado` (só AM-1 e AM-2) e `WhatsAppClique`. A campanha deve otimizar para `LeadQualificado`.
3. **Mandar as respostas do quiz e da página para uma planilha ou CRM** (hoje ficam só no navegador e no texto do WhatsApp).
4. **Trocar as imagens de estudos científicos por depoimentos e antes e depois reais** das clientes (gravados no consultório, com autorização).
5. **Versão mais calma do vídeo** para o público mais velho: mais lenta, letras maiores, legenda completa. Possível troca da voz de IA ("Pri", ElevenLabs) pela voz real da Alê, se ela mandar áudio ou vídeo.
6. **Espelho da Pele:** aplicar a direção visual aprovada e usar a face-api para medições reais do rosto. Lead só libera a análise com nome, WhatsApp, e-mail e autorização.
7. **Funil e CRM** no mesmo estilo visual aprovado.
8. **Automação do WhatsApp** com o nome da cliente (Kommo, RD Station ou ManyChat), usando as mensagens do PDF de atendimento.
