# Pannello Serie A Italia 2026/27

Dashboard statico e mobile-first, separato da tutti gli altri pannelli.

## Rigenerazione deterministica

Dalla root del repository:

```bash
python3 serie_a_italia_2026_27_build.py
python3 serie_a_italia_2026_27_validate.py
```

Il primo comando legge `serie_a_italia_2026_27_results.csv` e rigenera `index.html` e `serie_a_italia_2026_27_dashboard.html`. Il secondo verifica i 65 risultati finali contro `serie_a_italia_2026_27_official_verification.csv`, ricostruisce la classifica e confronta le statistiche di tutte le 20 squadre con il baseline indipendente di WorldFootball più i risultati recenti di Global Sports Archive.

## Procedura per un aggiornamento giornaliero futuro

1. Recuperare calendario, risultati e classifica aggiornati da Lega Serie A; non convertire una gara live o una data/ora non confermata in risultato o orario definitivo.
2. Aggiornare il CSV principale mantenendo solo risultati finali confermati; preservare i record delle gare differite.
3. Aggiornare i file di verifica ufficiale e indipendente e `serie_a_italia_2026_27_validation.txt`; confrontare punteggi e orientamento casa/trasferta.
4. Eseguire i due comandi di rigenerazione/validazione sopra.
5. Pubblicare il commit del repo; GitHub Pages serve il nuovo `index.html`.

**Nessuna schedulazione è attiva.** Questo repository contiene solo la Serie A italiana. La copertura del dataset iniziale termina alla giornata 10; per un aggiornamento giornaliero è necessario estendere il calendario verificato senza inferire date o orari.

## Stato del dataset iniziale

- Cutoff: 18/10/2026 10:54 (America/Sao_Paulo).
- 20 club; 65 partite concluse (giornate 1–6 complete e 5 partite concluse della giornata 7).
- Fiorentina–Como era live al cutoff: punteggio parziale omesso e gara esclusa dalle statistiche.
- Gli indicatori, H2H, forma, tabelle Top 5 e proiezioni usano solo i 65 risultati finali.
- Le proiezioni sono stime semplici Poisson basate sui gol, non xG o previsioni validate.

## Fonti

- Lega Serie A: [calendario e risultati](https://www.legaseriea.it/serie-a/calendario-risultati), [classifica](https://www.legaseriea.it/serie-a/classifica), [calendario ufficiale 2026/27 (PDF)](https://images.legaseriea.it/image/private/fl_attachment/prd/blpfycdm1ozusg4otblb.pdf).
- Global Sports Archive: [Serie A 2026/27, results/fixtures/standings](https://globalsportsarchive.com/en/soccer/competition/serie-a-enilive-2026-2027/80361).
- WorldFootball.net: [Serie A 2026/27, results and table](https://www.worldfootball.net/competition/co111/italy-serie-a/results-and-standings/).
- Sportstar / The Hindu: [résumé risultati della giornata 7](https://sportstar.thehindu.com/football/serie-a-2026-27-score-results-inter-milan-roma-napoli-goals-table-standings-football-news/article71599154.ece).
