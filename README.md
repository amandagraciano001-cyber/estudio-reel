# Estúdio reel

Uma skill gratuita pro Claude Code e pro Codex que organiza os seus reels prontos: o que postar hoje, o que sai na semana, o calendário do mês e o histórico do que já foi pro ar.

Você junta os vídeos prontos numa pasta, chama `/estudio-reel` (ou `$estudio-reel` no Codex) e o agente:

1. **Monta o Estúdio**: uma página no seu computador com um cartão por vídeo, a capa, a palavra-chave e a legenda de cada rede (Instagram, TikTok e LinkedIn) com botão de copiar.
2. **Diz o que sai hoje**: "o que eu posto hoje?" responde com o vídeo, a legenda pronta e a palavra-chave. E avisa o que ficou atrasado.
3. **Organiza a semana**: você diz em que dias posta e ele propõe uma data pra cada vídeo pronto, pulando os dias que já têm. Só grava depois do seu OK.
4. **Mostra o calendário**: mês a mês, com o que está programado e o que já foi postado.
5. **Guarda o histórico**: a aba "Postados" com a data e as métricas que você anotar (views, salvos, comentários), pra comparar o que funcionou.

Data e "postado" também dá pra marcar direto na página. Nada sai do seu computador, e o Estúdio não posta nada sozinho: quem aperta "publicar" é você.

Feita por [Amanda Graciano](https://amandagraciano.com), a partir do jeito que ela organiza os próprios posts.

## Funciona em

Claude Code e Codex, no Mac, no Windows e no Linux. O instalador acha sozinho qual agente você tem e coloca a skill no lugar certo de cada um.

| Agente | Onde a skill fica | Como chamar |
|---|---|---|
| Claude Code | `~/.claude/skills/estudio-reel` | `/estudio-reel` |
| Codex | `~/.agents/skills/estudio-reel` | `$estudio-reel` |

## O que você precisa

- [Claude Code](https://claude.com/claude-code) ou [Codex](https://developers.openai.com/codex)

| | Mac | Windows | Linux |
|---|---|---|---|
| Python 3.9 ou mais novo | já vem no Mac (ou `brew install python`) | `winget install Python.Python.3.12` | `sudo apt install python3 python3-venv` |
| ffmpeg | `brew install ffmpeg` | `winget install Gyan.FFmpeg` | `sudo apt install ffmpeg` |

## Como instalar

**Jeito mais fácil:** abra o Claude Code ou o Codex e cole:

```
https://github.com/amandagraciano001-cyber/estudio-reel

Instala essa skill pra mim e confere se as dependências estão instaladas.
```

**Pelo instalador.** Baixe o repositório (com o `git clone` abaixo, ou pelo botão Code > Download ZIP aqui no GitHub) e rode o instalador dentro da pasta.

Mac ou Linux, no Terminal:

```bash
git clone https://github.com/amandagraciano001-cyber/estudio-reel.git
cd estudio-reel
bash instalar.sh
```

Windows, no PowerShell:

```powershell
git clone https://github.com/amandagraciano001-cyber/estudio-reel.git
cd estudio-reel
powershell -ExecutionPolicy Bypass -File instalar.ps1
```

Pra instalar só num agente: `--claude` ou `--codex` no Mac e no Linux, `-Claude` ou `-Codex` no Windows. Já tinha instalado? Rode o instalador de novo: ele troca os arquivos e mantém o que já foi baixado.

## Como usar

No Claude Code a skill é chamada com `/estudio-reel`; no Codex, com `$estudio-reel`. O resto do pedido é igual.

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
| `instalar.sh` e `instalar.ps1` | Os instaladores do Mac e Linux e do Windows |
| `estudio-reel/agents/openai.yaml` | O nome e a descrição que o Codex mostra |
| `estudio-reel/SKILL.md` | O passo a passo que o agente segue |
| `scripts/estudio.py` | Monta a página, preenche cada vídeo, mostra o resumo do dia e distribui as datas |

## Licença

MIT. Use, adapte e compartilhe.
