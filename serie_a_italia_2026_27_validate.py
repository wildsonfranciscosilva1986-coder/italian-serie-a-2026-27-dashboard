import csv,collections,json

RESULTS='serie_a_italia_2026_27_results.csv'
OFFICIAL='serie_a_italia_2026_27_official_verification.csv'
INDEPENDENT_BASE='serie_a_italia_2026_27_independent_baseline.csv'
INDEPENDENT_RECENT='serie_a_italia_2026_27_independent_results.csv'
rows=list(csv.DictReader(open(RESULTS,encoding='utf-8-sig')))
off=list(csv.DictReader(open(OFFICIAL,encoding='utf-8-sig')))
ind=list(csv.DictReader(open(INDEPENDENT_RECENT,encoding='utf-8-sig')))
assert len(rows)==100
assert len(off)==65
assert len(ind)==5
finished=[r for r in rows if r['status']=='finished' and r['home_goals']!='' and r['away_goals']!='']
assert len(finished)==65
assert len({(r['matchday'],r['home_team'],r['away_team']) for r in rows})==100
assert len({(r['matchday'],r['home_team'],r['away_team']) for r in finished})==65
bykey={(int(r['matchday']),r['home_team'],r['away_team']):r for r in finished}
# Exact match-by-match score comparison against Lega Serie A snapshot evidence (65/65).
for r in off:
    k=(int(r['matchday']),r['home_team'],r['away_team'])
    assert k in bykey,k
    src=bykey[k]
    assert int(r['home_goals'])==int(src['home_goals']) and int(r['away_goals'])==int(src['away_goals']),k
assert set(bykey)=={(int(r['matchday']),r['home_team'],r['away_team']) for r in off}
# The independent worldfootball baseline includes MD1-6 + the completed Frosinone-Sassuolo MD7 game.
base={r['team']:{k:int(r[k]) for k in ('P','W','D','L','GF','GA','PTS')} for r in csv.DictReader(open(INDEPENDENT_BASE,encoding='utf-8-sig'))}
assert len(base)==20
# Add the four other completed MD7 games independently listed by Global Sports Archive.
for r in ind:
    k=(int(r['matchday']),r['home_team'],r['away_team'])
    if k==(7,'Frosinone','Sassuolo'):continue # already included in independent baseline
    h,a=int(r['home_goals']),int(r['away_goals'])
    for t,gf,ga in ((r['home_team'],h,a),(r['away_team'],a,h)):
        x=base[t];x['P']+=1;x['GF']+=gf;x['GA']+=ga
        if gf>ga:x['W']+=1;x['PTS']+=3
        elif gf<ga:x['L']+=1
        else:x['D']+=1;x['PTS']+=1
# Compute table from the 65 verified official scores.
computed=collections.defaultdict(lambda:dict(P=0,W=0,D=0,L=0,GF=0,GA=0,PTS=0))
for r in finished:
    h,a=int(r['home_goals']),int(r['away_goals'])
    for t,gf,ga in ((r['home_team'],h,a),(r['away_team'],a,h)):
        z=computed[t];z['P']+=1;z['GF']+=gf;z['GA']+=ga
        if gf>ga:z['W']+=1;z['PTS']+=3
        elif gf<ga:z['L']+=1
        else:z['D']+=1;z['PTS']+=1
assert len(computed)==20
for t in computed:
    assert computed[t]==base[t],(t,computed[t],base[t])
# The only live game at the cutoff is intentionally scoreless in the dataset and excluded from finished metrics.
live=[r for r in rows if r['status']=='live']
assert len(live)==1 and live[0]['home_team']=='Fiorentina' and live[0]['away_team']=='Como'
assert not live[0]['home_goals'] and not live[0]['away_goals']
# Round fixture rows in the local verified excerpt cover the first 10 matchdays.
assert all(sum(1 for r in rows if int(r['matchday'])==md)==10 for md in range(1,11))
# Assert key embedded dashboard data count and responsive markers.
html=open('serie_a_italia_2026_27_dashboard.html',encoding='utf-8').read()
assert '<meta name="viewport"' in html and '@media(max-width:800px)' in html
assert 'data-tab="matchup"' in html and 'data-tab="top5"' in html
report=(
'Snapshot: 2026-10-18 10:54 America/Sao_Paulo\n'
'League: Italy Serie A 2026/27; 20 clubs.\n'
'Fixture rows: 100, exactly 10 each for MD1–10; the source excerpt ends at MD10.\n'
'Finished matches included: 65 (MD1–6: 60; MD7: 5).\n'
'Official match-by-match score validation: PASS, all 65 scores and home/away orientations matched Lega Serie A calendar pages (MD1–6 10/10 each; MD7 5/5).\n'
'Live fixture excluded: Fiorentina–Como; no in-play score included. Four other MD7 fixtures were not yet started at the cutoff.\n'
'Independent table validation: PASS, all 20 clubs. WorldFootball.net baseline standings (MD1–6 plus Frosinone–Sassuolo 4–2) reconstructed and compared with the 65-match computed table after adding four further MD7 results independently listed by Global Sports Archive; P/W/D/L/GF/GA/points all match 20/20.\n'
'Independent latest-result verification: Global Sports Archive listed all five completed MD7 scores; Sportstar/The Hindu also reported the three Saturday fixtures.\n'
'Classifica official: live table was not used as a frozen table because Fiorentina–Como was still in progress.\n'
'Fixture interaction: player details, venue splits, 5 latest, available upcoming fixtures through MD10; H2H from this season; projection thresholds; top-5 splits and rate denominators.\n'
'JS/mobile validation: passed separately in local browser session; responsive viewport and breakpoint are present in HTML.\n'
'Qualification display: verified CL positions 1–4 and relegation 18–20 only; other European slots left unshaded due cup/access-list dependency.\n'
'No bookmaker, prediction feed, other league data, recurring jobs or external league project files used.\n'
)
open('serie_a_italia_2026_27_validation.txt','w',encoding='utf-8').write(report)
print(report)
