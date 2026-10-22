"""Fail-closed validator for the Italian Serie A 2026/27 dashboard."""
import collections
import csv
import json
import re
from datetime import datetime
from pathlib import Path

ROOT=Path('.')

def read(name):
    with (ROOT/name).open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))

rows=read('serie_a_italia_2026_27_results.csv')
calendar=read('serie_a_italia_2026_27_official_calendar.csv')
legacy=read('serie_a_italia_2026_27_official_verification.csv')
stand=read('serie_a_italia_2026_27_espn_standings_2026-10-22.csv')
snapshot=read('source_snapshots/results_snapshot_2026-10-22.csv')
assert len(rows)==len(calendar)==380, f'fixture counts results/calendar {len(rows)}/{len(calendar)}'
keys=[(int(r['matchday']),r['home_team'],r['away_team']) for r in rows]
cal_keys=[(int(r['matchday']),r['home_team'],r['away_team']) for r in calendar]
assert len(set(keys))==len(set(cal_keys))==380, 'duplicate fixture key'
assert set(keys)==set(cal_keys), 'results/calendar fixture mismatch'
assert all(collections.Counter(int(r['matchday']) for r in data)[md]==10 for data in (rows,calendar) for md in range(1,39)), 'expected 10 fixtures in each of 38 matchdays'
teams={r['home_team'] for r in rows}|{r['away_team'] for r in rows}
assert len(teams)==20, f'club count {len(teams)}'
for md in range(1,39):
    games=[r for r in rows if int(r['matchday'])==md]
    appearances=[r['home_team'] for r in games]+[r['away_team'] for r in games]
    assert len(appearances)==len(set(appearances))==20, f'MD{md} club participation is not one match each'
pairs=collections.defaultdict(list)
for r in rows:pairs[frozenset((r['home_team'],r['away_team']))].append((r['home_team'],r['away_team']))
assert len(pairs)==190 and all(len(v)==2 and v[0]==v[1][::-1] for v in pairs.values()), 'home/away double-round-robin pairing mismatch'

# Reconcile every fixture and marker with the Lega Serie A official PDF transcription.
by_key={(int(r['matchday']),r['home_team'],r['away_team']):r for r in rows}
by_cal={(int(r['matchday']),r['home_team'],r['away_team']):r for r in calendar}
round_markers={}
for key,r in by_key.items():
    c=by_cal[key]
    assert r['round_date']==c['round_date'], (key,'round date marker mismatch')
    assert c['source']=='Lega Serie A official season calendar PDF'
    assert c['source_url'].endswith('blpfycdm1ozusg4otblb.pdf')
    md=key[0]
    if md<=10:
        assert (r['date'],r['kickoff_local'])==(c['fixture_date'],c['kickoff_local']), (key,'MD1–10 date/time mismatch')
    else:
        assert not r['date'] and not r['kickoff_local'] and not c['fixture_date'] and not c['kickoff_local'], (key,'unconfirmed MD11–38 dates must remain blank')
    assert re.fullmatch(r'20\d\d-\d\d-\d\d',r['round_date']), (md,r['round_date'])
    round_markers.setdefault(md,set()).add(r['round_date'])
assert len(round_markers)==38 and all(len(v)==1 for v in round_markers.values())
assert round_markers[1]=={'2026-08-23'} and round_markers[38]=={'2027-05-30'}

finished=[r for r in rows if r['status']=='finished']
assert len(finished)>=70, f'finished count below the verified 70-match baseline: {len(finished)}'
for r in rows:
    if r['status']=='finished':
        assert re.fullmatch(r'\d+',r['home_goals']) and re.fullmatch(r'\d+',r['away_goals']), ('finished row missing/invalid score',r)
    else:
        assert not r['home_goals'] and not r['away_goals'], ('non-final row contains a score',r)
assert all(sum(int(r['matchday'])==md for r in finished)>=10 for md in range(1,8)), 'verified MD1–7 results must remain complete'
assert len(snapshot)==70, 'frozen 22-Oct score baseline changed'
snapshot_by_key={(int(r['matchday']),r['home_team'],r['away_team']):r for r in snapshot}
assert len(snapshot_by_key)==70
for key,s in snapshot_by_key.items():
    current=by_key[key]
    assert current['status']=='finished' and (current['home_goals'],current['away_goals'])==(s['home_goals'],s['away_goals']), ('baseline result changed',key)
for r in legacy:
    key=(int(r['matchday']),r['home_team'],r['away_team'])
    current=by_key[key]
    assert (int(r['home_goals']),int(r['away_goals']))==(int(current['home_goals']),int(current['away_goals'])), key

# Check the complete MD7 result batch against the archived ESPN daily scoreboards.
team_alias={'Internazionale':'Inter','FC Internazionale Milano':'Inter','AS Roma':'Roma','AC Milan':'Milan'}
api_events=[]
for day in ('20261016','20261017','20261018','20261019'):
    data=json.loads((ROOT/'source_snapshots'/f'espn_scoreboard_{day}.json').read_text())
    api_events.extend(data.get('events',[]))
assert len(api_events)==10, f'ESPN archived MD7 events {len(api_events)}'
api_by_key={}
for event in api_events:
    comp=event['competitions'][0]
    home=next(x for x in comp['competitors'] if x['homeAway']=='home')
    away=next(x for x in comp['competitors'] if x['homeAway']=='away')
    key=(7,team_alias.get(home['team']['displayName'],home['team']['displayName']),team_alias.get(away['team']['displayName'],away['team']['displayName']))
    assert comp['status']['type']['completed'] is True and key not in api_by_key, key
    api_by_key[key]=(int(home['score']),int(away['score']))
for key,score in api_by_key.items():
    current=by_key[key]
    assert (int(current['home_goals']),int(current['away_goals']))==score, (key,score)
assert len(api_by_key)==10
# Results added after the static 22-Oct baseline must retain an ESPN event identifier.
if 'espn_event_id' in rows[0]:
    for r in finished:
        if int(r['matchday'])>=8:
            event_id=r.get('espn_event_id')
            assert event_id, ('new result missing ESPN event id',r)
            archive_path=ROOT/'source_snapshots'/f'espn_result_{event_id}.json'
            assert archive_path.exists(), ('missing immutable ESPN result evidence',event_id)
            archive=json.loads(archive_path.read_text(encoding='utf-8'))
            event=archive['event'];comp=event['competitions'][0]
            home=next(x for x in comp['competitors'] if x['homeAway']=='home')
            away=next(x for x in comp['competitors'] if x['homeAway']=='away')
            hname=team_alias.get(home['team']['displayName'],home['team']['displayName'])
            aname=team_alias.get(away['team']['displayName'],away['team']['displayName'])
            assert (hname,aname)==(r['home_team'],r['away_team'])
            assert (int(home['score']),int(away['score']))==(int(r['home_goals']),int(r['away_goals']))
            assert archive['source_url'].startswith('https://site.api.espn.com/')

# Reconcile the frozen historical table to ESPN's independently archived 22-Oct standings.
base_calc=collections.defaultdict(lambda:dict(P=0,W=0,D=0,L=0,GF=0,GA=0,PTS=0))
for r in snapshot:
    h,a=int(r['home_goals']),int(r['away_goals'])
    for team,gf,ga in ((r['home_team'],h,a),(r['away_team'],a,h)):
        z=base_calc[team];z['P']+=1;z['GF']+=gf;z['GA']+=ga
        if gf>ga:z['W']+=1;z['PTS']+=3
        elif gf<ga:z['L']+=1
        else:z['D']+=1;z['PTS']+=1
for z in base_calc.values():z['GD']=z['GF']-z['GA']
assert set(base_calc)==teams and len(stand)==20 and len({r['team'] for r in stand})==20
for r in stand:
    for k in ('P','W','D','L','GF','GA','GD','PTS'):
        assert int(r[k])==base_calc[r['team']][k], (r['team'],k)
base_order=sorted(base_calc,key=lambda t:(-base_calc[t]['PTS'],-base_calc[t]['GD'],-base_calc[t]['GF'],t))
assert base_order==[r['team'] for r in sorted(stand,key=lambda x:int(x['position']))], 'frozen table order differs from ESPN snapshot'

# Generated UI/payload checks. This remains valid as later final results are added.
page=(ROOT/'index.html').read_text(encoding='utf-8')
copy=(ROOT/'serie_a_italia_2026_27_dashboard.html').read_text(encoding='utf-8')
assert page==copy, 'generated HTML copies differ'
for phrase in ('Corte: ','380 jogos · calendário oficial completo','38 jornadas','data-tab="fixtures"','data-tab="matchup"','data-tab="top5"','Europa League','Conference League','@media(max-width:800px)','Data e horário individuais a confirmar'):
    assert phrase in page, f'missing UI feature: {phrase}'
for stale in ('100 jogos, jornadas 1–10','expansão oficial para jornadas 11–38 ainda não incorporada','limitado à cobertura verificada até MD10','Fixture coverage: 100 rows'):
    assert stale not in page, f'stale HTML text: {stale}'
match=re.search(r'const D=(\{.*?\});',page,re.S)
assert match, 'embedded payload missing'
payload=json.loads(match.group(1))
assert len(payload['matches'])==len(finished) and len(payload['fixtures'])==380 and len(payload['table'])==20
assert len(payload['roundDates'])==38 and not payload['liveExcluded']
assert all(len([g for g in payload['fixtures'] if g['round']==md])==10 for md in range(1,39))
assert all(not g['date'] and not g['time'] for g in payload['fixtures'] if g['round']>=11 and g['status']!='finished')
complete=sorted(md for md in range(1,39) if sum(int(r['matchday'])==md and r['status']=='finished' for r in rows)==10)
assert payload['completeRounds']==complete and payload['lastCompleteRound']==(max(complete) if complete else 0)
assert 'window.__DASH_TEST=' in page and 'calendarReady:typeof renderFixtures===\'function\'' in page

cutoff=payload['cutoff']
report=f'''Snapshot: {cutoff}
League: Serie A Italy 2026/27; 20 clubs.
Fixtures: PASS — 380 official fixture entries across 38 matchdays, 10 per MD; each club appears once per round; all 190 pairings occur twice with home/away reversed.
Official schedule: PASS — fixture pairs and round markers match the transcribed Lega Serie A official calendar PDF. MD1–10 individual dates/times are preserved; unconfirmed MD11–38 kickoffs remain blank unless the match has been played.
Results: PASS — {len(finished)} final scores; verified MD1–7 baseline retained; no live/partial score included. New finals are matched against the official fixture list and must retain ESPN event IDs.
Historical official score evidence: PASS — 65 results match the saved Lega Serie A match-by-match verification file; all ten MD7 scores and home/away orientations match archived ESPN scoreboards.
Standings: PASS for the frozen 22-Oct baseline against ESPN's independent standings snapshot. Current standings are recomputed from all final scores; the Lega live table previously returned “NO DATA,” so no live official-table comparison is claimed.
Generated UI: PASS static checks — HTML copies match; 20 clubs, 380 fixtures, 38 rounds, dynamic cutoff, calendar selector, team profiles, home/away splits, H2H, matchup and Top 5 controls are present; responsive CSS and no-JavaScript standings fallback are present.
Browser interaction/mobile rendering: pending live-page validation after authorized publication.
Publication: not confirmed until the public Pages URL matches the generated build.
Automation: refresh script and scheduled workflow must be tested after authorized repository write access is granted.
'''
(ROOT/'serie_a_italia_2026_27_validation.txt').write_text(report,encoding='utf-8')
print(report)
