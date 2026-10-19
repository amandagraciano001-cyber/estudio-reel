---
name: estudio-reel
description: Organiza os reels prontos numa página local, o Estúdio, com a fila do que postar, o calendário mês a mês, o histórico do que já foi postado e as métricas de cada um. Diz o que sai hoje, distribui os vídeos prontos nos dias da semana e guarda a legenda de cada rede pronta pra copiar. Use quando a pessoa pedir "monta o Estúdio", "o que eu posto hoje", "organiza minha semana de posts", "programa esses vídeos", "marca como postado", "anota as métricas" ou chamar /estudio-reel.
---

# Estúdio reel

Você cuida da agenda de publicação da pessoa. Os vídeos já estão prontos; você organiza quando cada um sai, guarda a legenda de cada rede, lembra o que é pra hoje e registra o que já foi postado e como foi. Esta skill não edita vídeo e não posta nada sozinha: quem aperta "publicar" na rede é a pessoa.

O script fica em `scripts/estudio.py` dentro desta pasta da skill. Precisa de Python 3.10 ou mais novo e do `ffmpeg` (só pra tirar a capa de cada vídeo). Todo comando recebe o caminho absoluto da pasta dos vídeos prontos.

## A pasta do Estúdio

Uma pasta com os `.mp4` prontos (pergunte qual na primeira vez; sugestão: `~/prontos`). O script cria nela:
- `estudio.json`: os dados de cada vídeo (título, palavra-chave, legendas, estado, data, notas, métricas). Dá pra editar na mão.
- `estudio.html`: a página. Abra no navegador.
- `capas/`: uma imagem por vídeo, tirada do segundo 1.

Cada vídeo tem um estado: **pronto** (sem data), **programado** (com data) ou **postado**.

## Montar ou atualizar o Estúdio

```
python scripts/estudio.py PASTA
```
Varre a pasta, acrescenta os vídeos novos como "pronto", tira os que não existem mais e gera a página. Rode sempre que entrar vídeo novo. Abra o `estudio.html` no navegador e entregue o caminho.

## Preencher um vídeo

```
python scripts/estudio.py PASTA --video nome.mp4 --titulo "..." --palavra GUIA --legenda-instagram "..." --legenda-tiktok "..." --legenda-linkedin "..."
```
- Se o vídeo nasceu de um roteiro da skill **Roteiro reel**, use `--roteiro caminho/do/roteiro.md`: o título (a capa escolhida), a palavra-chave e as três legendas vêm de lá.
- Se a pessoa não tem legenda, escreva com ela: primeira linha é um gancho, corpo curto, uma chamada só. No TikTok, sem palavra-chave. Mostre antes de gravar.
- `--nota` guarda um lembrete (por exemplo "marcar o @ do convidado").

## Quando postar

**"O que eu posto hoje?"**
```
python scripts/estudio.py PASTA --resumo
```
Mostra o que está marcado pra hoje, o que ficou atrasado, os próximos 7 dias e os prontos sem data. Responda com o vídeo de hoje, a legenda da rede que ela vai usar (pronta pra copiar) e a palavra-chave. Se nada estiver marcado, ofereça o próximo pronto.

**"Organiza minha semana" ou "programa esses vídeos"**
1. Pergunte em que dias ela posta, se ainda não souber (por exemplo seg, qua, sex). Respeite o ritmo dela: constância vale mais que volume.
2. Mostre a proposta, sem gravar:
   ```
   python scripts/estudio.py PASTA --distribuir --dias seg,qua,sex [--a-partir 2026-10-21]
   ```
   Ela dá uma data pra cada pronto sem data, em ordem, pulando os dias que já têm vídeo.
3. Antes de aplicar, olhe a sequência: dois vídeos do mesmo assunto ou dois pedindo palavra-chave seguidos cansam quem segue. Se for o caso, sugira trocar a ordem com `--data` em um deles.
4. Com o OK dela, grave com o mesmo comando mais `--aplicar`.

Uma data só também vale: `--video nome.mp4 --data 2026-10-25` (o estado vira "programado").

**Na página**, ela também pode escolher a data e marcar "postado" em cada cartão. Isso fica salvo no navegador dela; o botão "Baixar estudio.json" gera o arquivo com as mudanças pra trocar na pasta. Se ela disser que mexeu pela página, peça o arquivo baixado e coloque no lugar do `estudio.json` antes de rodar o script de novo, senão as mudanças da página se perdem.

## Depois de postar

```
python scripts/estudio.py PASTA --video nome.mp4 --estado postado --data 2026-10-21
python scripts/estudio.py PASTA --video nome.mp4 --metricas "views=1200,curtidas=90,comentarios=34,salvos=40,compartilhamentos=12"
```
As métricas aparecem no cartão, na aba "Postados". Anote o que a pessoa disser, com os nomes que ela usar, e nunca invente número: sem o dado, o campo fica de fora. Quando houver alguns postados com métricas, compare em voz alta: qual formato teve mais salvamentos, qual palavra-chave trouxe mais comentários. Diga que é observação de poucos vídeos, não regra.

## Regras
- Esta skill não publica nada. Ela organiza; quem posta é a pessoa.
- Nunca invente data, número ou métrica.
- Nunca apague vídeo. Se um vídeo saiu da pasta, ele sai do Estúdio, mas o arquivo não é tocado.
- Mudança de data ou de estado em lote (o `--aplicar`) só com o OK da pessoa.
