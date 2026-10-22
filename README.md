# Pannello Serie A Italia 2026/27

Dashboard responsivo e interativo da Serie A italiana, separado dos demais campeonatos. O build local foi reconstruído e validado em 22/10/2026; o horário de corte é gerado automaticamente a cada atualização.

## Reconstruir e validar

Na raiz do repositório:

```bash
python3 serie_a_italia_2026_27_build.py
python3 serie_a_italia_2026_27_validate.py
```

O builder gera `index.html` e `serie_a_italia_2026_27_dashboard.html` a partir de `serie_a_italia_2026_27_results.csv`. O calendário oficial completo contém 380 confrontos em 38 jornadas, transcritos do PDF da Lega Serie A e verificados por participação de clubes e pares casa/fora. Para MD11–38, o documento oferece apenas uma data-guia da jornada; datas e horários individuais ficam vazios até confirmação e nunca são inferidos.

## Atualização de resultados

A rotina `serie_a_italia_2026_27_refresh.py` consulta o placar público da ESPN para os últimos dez dias, aplica somente partidas finalizadas que correspondam a um confronto do calendário oficial e recusa sobrescrever resultados finais divergentes. Resultados novos recebem o ID ESPN e um arquivo de evidência. Ela não preenche horários futuros com estimativas.

Teste sem gravar alterações:

```bash
python3 serie_a_italia_2026_27_refresh.py --check-only
```

A rotina diária está definida em `.github/workflows/serie-a-italia-refresh.yml` para 06:10 de São Paulo (09:10 UTC). Ela busca resultados, reconstrói o painel, valida e só então grava/publica alterações. Só será considerada operacional após uma execução bem-sucedida no GitHub Actions e conferência da URL pública.

## Estado validado do snapshot local

- 20 clubes, 70 resultados finais confirmados (jornadas 1–7 completas).
- 380 jogos distribuídos em 38 jornadas; 10 por jornada e cada confronto disputado duas vezes, com mandos invertidos.
- Datas e horários individuais de MD1–10 preservados; MD11–38 exibem somente a data-guia oficial da jornada até que os horários sejam publicados.
- Os 65 resultados iniciais conferem com evidências jogo a jogo da Lega Serie A; os dez resultados da jornada 7 conferem com snapshots ESPN. Resultados recentes também foram verificados com fontes jornalísticas independentes.
- A tabela calculada a partir dos 70 resultados coincide com o snapshot independente ESPN de 22/10/2026. A página de classificação da Lega retornou “NO DATA” durante a verificação; portanto, não alegamos uma comparação ao vivo com a tabela oficial.
- A interface local passou nas verificações estruturais: seis seções, calendário selecionável, classificação, fichas de equipes, recortes casa/fora, H2H, confronto e Top 5. A interação no navegador e o deploy público ainda precisam ser conferidos após a publicação.

## Fontes

- Lega Serie A: [calendário/resultados](https://www.legaseriea.it/serie-a/calendario-risultati), [classificação](https://www.legaseriea.it/serie-a/classifica) e [calendário oficial completo 2026/27 em PDF](https://images.legaseriea.it/image/private/fl_attachment/prd/blpfycdm1ozusg4otblb.pdf).
- ESPN: [placares da Serie A](https://www.espn.com/soccer/scoreboard/_/league/ita.1) e [classificação](https://www.espn.com/soccer/standings/_/league/ita.1); os snapshots usados ficam em `source_snapshots/`.
- [Global Sports Archive — Serie A 2026/27](https://globalsportsarchive.com/en/soccer/competition/serie-a-enilive-2026-2027/80361).
- Checagens independentes da jornada 7: [Sky TG24](https://tg24.sky.it/sport/2026/10/18/serie-a-partite-oggi-risultati-gol-highlights-video) e [Gazzetta di Parma](https://www.gazzettadiparma.it/parma-calcio/2026/10/19/news/aspetti-il-cagliari-ma-esplode-il-monza-4-0-e-tre-punti-salvezza-d-oro-risultati-e-classifica-975572/).

## Publicação

URL atual: https://wildsonfranciscosilva1986-coder.github.io/italian-serie-a-2026-27-dashboard/ . Ela ainda serve a versão antiga até que o build validado seja enviado ao repositório. O Pages está configurado para publicar a raiz de `main`; após o primeiro push da nova versão, confira a página pública e a primeira execução automática antes de marcar a rotina como ativa.
