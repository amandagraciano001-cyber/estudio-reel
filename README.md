# Estúdio reel

Uma skill gratuita pro Claude Code que organiza os seus reels prontos: o que postar hoje, o que sai na semana, o calendário do mês e o histórico do que já foi pro ar.

Você junta os vídeos prontos numa pasta, chama `/estudio-reel` e o Claude:

1. **Monta o Estúdio**: uma página no seu computador com um cartão por vídeo, a capa, a palavra-chave e a legenda de cada rede (Instagram, TikTok e LinkedIn) com botão de copiar.
2. **Diz o que sai hoje**: "o que eu posto hoje?" responde com o vídeo, a legenda pronta e a palavra-chave. E avisa o que ficou atrasado.
3. **Organiza a semana**: você diz em que dias posta e ele propõe uma data pra cada vídeo pronto, pulando os dias que já têm. Só grava depois do seu OK.
4. **Mostra o calendário**: mês a mês, com o que está programado e o que já foi postado.
5. **Guarda o histórico**: a aba "Postados" com a data e as métricas que você anotar (views, salvos, comentários), pra comparar o que funcionou.

Data e "postado" também dá pra marcar direto na página. Nada sai do seu computador, e o Estúdio não posta nada sozinho: quem aperta "publicar" é você.

Feita por [Amanda Graciano](https://amandagraciano.com), a partir do jeito que ela organiza os próprios posts.

## O que você precisa

- [Claude Code](https://claude.com/claude-code)
- Python 3.10 ou mais novo
- [ffmpeg](https://ffmpeg.org) (pra tirar a capa de cada vídeo): no Mac, `brew install ffmpeg`

## Como instalar

**Jeito mais fácil:** abra o Claude Code e cole:

```
https://github.com/amandagraciano001-cyber/estudio-reel

Instala essa skill pra mim e confere se as dependências estão instaladas.
```

**Ou você mesma:**

```bash
git clone https://github.com/amandagraciano001-cyber/estudio-reel.git estudio-reel
cp -r estudio-reel/estudio-reel ~/.claude/skills/
```

## Como usar

```
/estudio-reel monta o Estúdio com os vídeos que estão em ~/prontos
```

```
/estudio-reel o que eu posto hoje?
```

```
/estudio-reel organiza os prontos pra segunda, quarta e sexta
```

```
/estudio-reel postei o vídeo da planilha ontem, teve 1.200 views e 40 salvos
```

## A família

Estúdio reel é a terceira de três skills que funcionam juntas, cada uma sozinha também:

1. **[Roteiro reel](https://github.com/amandagraciano001-cyber/roteiro-reel)**: antes de gravar. Ideia entra, roteiro sai, com capa, legendas e palavra-chave.
2. **[Edita reel](https://github.com/amandagraciano001-cyber/edita-reel)**: depois de gravar. Vídeo bruto entra, reel editado sai.
3. **Estúdio reel** (esta): depois de editar. Os vídeos prontos viram fila, calendário e histórico. Com `--roteiro`, o título, as legendas e a palavra-chave vêm direto do roteiro.

## O que vem em cada arquivo

| Arquivo | O que faz |
|---|---|
| `estudio-reel/SKILL.md` | O passo a passo que o Claude segue |
| `scripts/estudio.py` | Monta a página, preenche cada vídeo, mostra o resumo do dia e distribui as datas |

## Licença

MIT. Use, adapte e compartilhe.
