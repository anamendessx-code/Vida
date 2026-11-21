# Quiz + tráfego: como filtrar os leads da Alê

**O problema:** o anúncio traz muita gente curiosa, de outra cidade ou sem condição de pagar agora. A Alê gasta horas no WhatsApp e quase nada vira agendamento.

**A solução:** o anúncio leva para um quiz de 7 perguntas. A própria pessoa se qualifica, vê um resultado simples e personalizado e só então chama a Alê. A mensagem já chega com tudo o que ela respondeu.

```
Anúncio → Quiz (1 min) → Resultado com o nome dela → WhatsApp com as respostas → Alê fecha
```

Protótipo: `prototipo/quiz.html`. Abra com `#exemplo` no fim do link para ver um resultado pronto.

## As 7 perguntas e o que cada uma filtra

| # | Pergunta | Para que serve |
|---|---|---|
| 1 | Qual é o seu nome? | Personaliza todas as telas e a mensagem |
| 2 | O que mais te incomoda? | Define o plano: Melasma, Protocolo AM, Glass Skin, Linhas, Harmonização ou Avaliação |
| 3 | Há quanto tempo? | Dor antiga = mais vontade de resolver |
| 4 | Já tentou tratar? | "Já gastei e voltou" é a cliente ideal da Alê |
| 5 | Onde quer ser atendida? | Tira quem é de outra cidade |
| 6 | Quando quer começar? | Separa quem quer agora de quem está só pesquisando |
| 7 | O valor a partir de R$ ___ cabe agora? | Filtra o preço **antes** da conversa |
| 8 | WhatsApp + autorização | Contato confirmado (LGPD) |

**Trocar o valor da pergunta 7** no topo do arquivo (`precoAPartir`). É a pergunta que mais filtra.

## Os 4 níveis de lead (código no fim da mensagem)

| Código | Quem é | O que a página mostra | O que a Alê faz |
|---|---|---|---|
| **AM-1** | Na região, quer começar esta semana ou este mês, o valor cabe | Prioridade + 10% hoje com contagem | Responde primeiro, com áudio, e já oferece horário |
| **AM-2** | Na região, quer começar mais para frente ou só se for parcelado | Dúvidas sem pressa + 10% hoje | Responde no mesmo dia, mostra o parcelamento |
| **AM-3** | Só pesquisando ou o valor não cabe agora | Dicas de cuidado em casa + Instagram | Mensagem curta e lista de remarketing |
| **AM-4** | Outra cidade | "Te aviso quando eu for perto de você" | Lista de espera por cidade |

## Página mais inclusiva (pessoas mais velhas)

- Uma pergunta por tela, botões grandes, letra grande e alto contraste.
- Botão **Letra maior** e botão **Ouvir** (o celular lê a tela em voz alta).
- Palavras simples: "manchas escuras" em vez de "hiperpigmentação".
- Botão **Voltar** em todas as telas, barra de progresso "3 de 8".
- Número do WhatsApp escrito na tela, para quem prefere salvar.
- Resultado em 4 blocos: O que é · Por que acontece · O que a Alê faz · O que esperar.

## Configuração do tráfego (Meta)

1. **Destino do anúncio:** o quiz, não o WhatsApp direto. Clique direto no WhatsApp é o que traz lead esquisito.
2. **Pixel na página.** O quiz já dispara estes eventos se o pixel estiver instalado:
   - `QuizIniciado`: clicou em "Começar"
   - `QuizConcluido`: respondeu tudo
   - `LeadQualificado`: só AM-1 e AM-2 ← **otimizar a campanha para este evento**
   - `WhatsAppClique`: tocou no botão do WhatsApp
3. **Conversão personalizada** no Gerenciador de Eventos com `LeadQualificado`. Depois de ~50 por semana, o Meta passa a buscar gente parecida com as leads boas.
4. **Localização:** raio de 10 a 15 km de Águas Claras e do Setor Marista (campanhas separadas por cidade).
5. **Texto do anúncio que já filtra:** citar a cidade e "tratamento com acompanhamento". Evitar "grátis" na chamada principal, porque atrai curiosos.
6. **Criativos:** o motion "Acompanhamento real", depoimentos das clientes (gravar amanhã) e a Alê falando para a câmera.
7. **Remarketing:** quem fez o quiz e não chamou no WhatsApp (AM-2 e AM-3) vê depoimentos por 7 a 14 dias.

## O que medir toda semana

| Métrica | Meta inicial |
|---|---|
| Quem começa o quiz e termina | acima de 60% |
| Leads AM-1 + AM-2 sobre o total | acima de 40% |
| Clique no WhatsApp sobre AM-1/AM-2 | acima de 70% |
| Conversa que vira agendamento | acima de 30% |
| Custo por lead qualificado | acompanhar e reduzir semana a semana |

## Para colocar no ar

O link do protótipo é privado. Para o anúncio, a página precisa de hospedagem pública (ex.: Vercel, Netlify ou o domínio da Alê) com o pixel instalado. As respostas podem ir para uma planilha ou CRM ao mesmo tempo em que abrem o WhatsApp.
