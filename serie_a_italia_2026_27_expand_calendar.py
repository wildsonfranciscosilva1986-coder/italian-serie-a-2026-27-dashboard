"""Extend the verified Italian Serie A 2026/27 fixture list from the official Lega calendar PDF.

The PDF gives one matchday reference date, not individual kickoff dates for every fixture.
For MD11-38, fixture_date and kickoff_local intentionally remain blank until confirmed.
"""
import csv
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "serie_a_italia_2026_27_results.csv"
CALENDAR = ROOT / "serie_a_italia_2026_27_official_calendar.csv"
PDF_URL = "https://images.legaseriea.it/image/private/fl_attachment/prd/blpfycdm1ozusg4otblb.pdf"
ROUND_DATES = {
    1:"2026-08-23",2:"2026-08-30",3:"2026-09-06",4:"2026-09-13",5:"2026-09-20",
    6:"2026-10-11",7:"2026-10-18",8:"2026-10-25",9:"2026-10-28",10:"2026-11-01",
    11:"2026-11-08",12:"2026-11-22",13:"2026-11-29",14:"2026-12-06",15:"2026-12-13",
    16:"2026-12-20",17:"2027-01-03",18:"2027-01-06",19:"2027-01-10",20:"2027-01-17",
    21:"2027-01-24",22:"2027-01-31",23:"2027-02-07",24:"2027-02-14",25:"2027-02-21",
    26:"2027-02-28",27:"2027-03-07",28:"2027-03-14",29:"2027-03-21",30:"2027-04-04",
    31:"2027-04-11",32:"2027-04-18",33:"2027-04-25",34:"2027-05-02",35:"2027-05-09",
    36:"2027-05-16",37:"2027-05-23",38:"2027-05-30",
}
# Matchups transcribed from the two-page official Lega Serie A 2026/27 season-calendar PDF.
# First ten rounds are also compared to the existing source rows before any output is written.
PDF_FIXTURES = {
1:[("Atalanta","Sassuolo"),("Bologna","Lazio"),("Frosinone","Juventus"),("Genoa","Napoli"),("Inter","Monza"),("Parma","Cagliari"),("Roma","Fiorentina"),("Torino","Milan"),("Udinese","Como"),("Venezia","Lecce")],
2:[("Atalanta","Bologna"),("Cagliari","Inter"),("Fiorentina","Frosinone"),("Juventus","Parma"),("Lazio","Genoa"),("Lecce","Roma"),("Milan","Venezia"),("Monza","Udinese"),("Napoli","Como"),("Sassuolo","Torino")],
3:[("Bologna","Sassuolo"),("Cagliari","Lecce"),("Fiorentina","Torino"),("Frosinone","Venezia"),("Genoa","Como"),("Inter","Napoli"),("Juventus","Milan"),("Parma","Monza"),("Roma","Atalanta"),("Udinese","Lazio")],
4:[("Atalanta","Cagliari"),("Como","Parma"),("Genoa","Frosinone"),("Inter","Udinese"),("Lazio","Milan"),("Lecce","Monza"),("Napoli","Bologna"),("Sassuolo","Juventus"),("Torino","Roma"),("Venezia","Fiorentina")],
5:[("Bologna","Torino"),("Fiorentina","Napoli"),("Frosinone","Como"),("Juventus","Atalanta"),("Milan","Lecce"),("Monza","Sassuolo"),("Parma","Genoa"),("Roma","Inter"),("Udinese","Cagliari"),("Venezia","Lazio")],
6:[("Atalanta","Venezia"),("Cagliari","Juventus"),("Como","Roma"),("Genoa","Fiorentina"),("Inter","Parma"),("Lazio","Monza"),("Lecce","Bologna"),("Napoli","Frosinone"),("Sassuolo","Milan"),("Torino","Udinese")],
7:[("Bologna","Inter"),("Fiorentina","Como"),("Frosinone","Sassuolo"),("Juventus","Lazio"),("Milan","Atalanta"),("Monza","Cagliari"),("Parma","Torino"),("Roma","Genoa"),("Udinese","Lecce"),("Venezia","Napoli")],
8:[("Atalanta","Frosinone"),("Cagliari","Bologna"),("Como","Sassuolo"),("Genoa","Venezia"),("Inter","Fiorentina"),("Lazio","Parma"),("Lecce","Juventus"),("Napoli","Roma"),("Torino","Monza"),("Udinese","Milan")],
9:[("Fiorentina","Atalanta"),("Frosinone","Lecce"),("Genoa","Juventus"),("Milan","Bologna"),("Monza","Napoli"),("Parma","Udinese"),("Roma","Cagliari"),("Sassuolo","Lazio"),("Torino","Como"),("Venezia","Inter")],
10:[("Atalanta","Parma"),("Bologna","Monza"),("Como","Venezia"),("Frosinone","Torino"),("Juventus","Napoli"),("Lazio","Cagliari"),("Lecce","Genoa"),("Milan","Inter"),("Sassuolo","Fiorentina"),("Udinese","Roma")],
11:[("Cagliari","Frosinone"),("Fiorentina","Juventus"),("Genoa","Milan"),("Inter","Como"),("Monza","Atalanta"),("Napoli","Lazio"),("Parma","Bologna"),("Roma","Sassuolo"),("Torino","Lecce"),("Venezia","Udinese")],
12:[("Atalanta","Inter"),("Bologna","Udinese"),("Como","Cagliari"),("Juventus","Venezia"),("Lazio","Lecce"),("Milan","Frosinone"),("Monza","Fiorentina"),("Napoli","Torino"),("Parma","Roma"),("Sassuolo","Genoa")],
13:[("Cagliari","Milan"),("Como","Juventus"),("Frosinone","Parma"),("Inter","Genoa"),("Lecce","Atalanta"),("Roma","Monza"),("Sassuolo","Napoli"),("Torino","Lazio"),("Udinese","Fiorentina"),("Venezia","Bologna")],
14:[("Bologna","Roma"),("Fiorentina","Cagliari"),("Frosinone","Inter"),("Genoa","Torino"),("Juventus","Udinese"),("Lazio","Atalanta"),("Milan","Parma"),("Monza","Como"),("Napoli","Lecce"),("Venezia","Sassuolo")],
15:[("Atalanta","Genoa"),("Cagliari","Venezia"),("Como","Bologna"),("Inter","Torino"),("Juventus","Monza"),("Lazio","Roma"),("Lecce","Sassuolo"),("Napoli","Milan"),("Parma","Fiorentina"),("Udinese","Frosinone")],
16:[("Atalanta","Napoli"),("Fiorentina","Bologna"),("Frosinone","Lazio"),("Genoa","Udinese"),("Lecce","Inter"),("Milan","Como"),("Roma","Juventus"),("Sassuolo","Parma"),("Torino","Cagliari"),("Venezia","Monza")],
17:[("Bologna","Juventus"),("Cagliari","Genoa"),("Como","Lecce"),("Fiorentina","Lazio"),("Inter","Sassuolo"),("Monza","Milan"),("Parma","Napoli"),("Roma","Frosinone"),("Torino","Venezia"),("Udinese","Atalanta")],
18:[("Atalanta","Como"),("Frosinone","Bologna"),("Genoa","Monza"),("Juventus","Torino"),("Lazio","Inter"),("Lecce","Parma"),("Milan","Fiorentina"),("Napoli","Cagliari"),("Sassuolo","Udinese"),("Venezia","Roma")],
19:[("Bologna","Genoa"),("Cagliari","Sassuolo"),("Como","Lazio"),("Fiorentina","Lecce"),("Inter","Juventus"),("Monza","Frosinone"),("Parma","Venezia"),("Roma","Milan"),("Torino","Atalanta"),("Udinese","Napoli")],
20:[("Atalanta","Roma"),("Cagliari","Como"),("Juventus","Genoa"),("Lazio","Bologna"),("Lecce","Udinese"),("Milan","Torino"),("Napoli","Fiorentina"),("Parma","Inter"),("Sassuolo","Monza"),("Venezia","Frosinone")],
21:[("Bologna","Atalanta"),("Como","Napoli"),("Fiorentina","Sassuolo"),("Frosinone","Milan"),("Genoa","Parma"),("Inter","Venezia"),("Juventus","Cagliari"),("Lecce","Torino"),("Monza","Lazio"),("Roma","Udinese")],
22:[("Atalanta","Fiorentina"),("Cagliari","Parma"),("Genoa","Lecce"),("Lazio","Venezia"),("Milan","Juventus"),("Monza","Roma"),("Napoli","Inter"),("Sassuolo","Como"),("Torino","Frosinone"),("Udinese","Bologna")],
23:[("Atalanta","Lazio"),("Bologna","Milan"),("Como","Monza"),("Fiorentina","Udinese"),("Inter","Cagliari"),("Juventus","Sassuolo"),("Lecce","Napoli"),("Parma","Frosinone"),("Roma","Torino"),("Venezia","Genoa")],
24:[("Bologna","Como"),("Cagliari","Lazio"),("Frosinone","Fiorentina"),("Genoa","Atalanta"),("Inter","Milan"),("Monza","Lecce"),("Napoli","Juventus"),("Roma","Parma"),("Torino","Sassuolo"),("Udinese","Venezia")],
25:[("Atalanta","Monza"),("Como","Torino"),("Fiorentina","Inter"),("Juventus","Bologna"),("Lazio","Napoli"),("Lecce","Frosinone"),("Milan","Genoa"),("Sassuolo","Roma"),("Udinese","Parma"),("Venezia","Cagliari")],
26:[("Bologna","Lecce"),("Cagliari","Udinese"),("Como","Milan"),("Frosinone","Napoli"),("Genoa","Lazio"),("Inter","Atalanta"),("Monza","Juventus"),("Parma","Sassuolo"),("Roma","Venezia"),("Torino","Fiorentina")],
27:[("Atalanta","Torino"),("Fiorentina","Venezia"),("Juventus","Roma"),("Lazio","Frosinone"),("Lecce","Como"),("Milan","Cagliari"),("Monza","Genoa"),("Napoli","Parma"),("Sassuolo","Bologna"),("Udinese","Inter")],
28:[("Bologna","Napoli"),("Cagliari","Fiorentina"),("Como","Udinese"),("Frosinone","Monza"),("Genoa","Roma"),("Lazio","Juventus"),("Milan","Sassuolo"),("Parma","Lecce"),("Torino","Inter"),("Venezia","Atalanta")],
29:[("Atalanta","Milan"),("Fiorentina","Genoa"),("Inter","Frosinone"),("Juventus","Como"),("Monza","Bologna"),("Napoli","Venezia"),("Parma","Lazio"),("Roma","Lecce"),("Sassuolo","Cagliari"),("Udinese","Torino")],
30:[("Cagliari","Napoli"),("Como","Fiorentina"),("Frosinone","Udinese"),("Genoa","Inter"),("Lecce","Lazio"),("Milan","Monza"),("Roma","Bologna"),("Sassuolo","Atalanta"),("Torino","Juventus"),("Venezia","Parma")],
31:[("Bologna","Venezia"),("Cagliari","Atalanta"),("Fiorentina","Milan"),("Frosinone","Genoa"),("Inter","Roma"),("Juventus","Lecce"),("Lazio","Torino"),("Napoli","Sassuolo"),("Parma","Como"),("Udinese","Monza")],
32:[("Atalanta","Udinese"),("Bologna","Cagliari"),("Como","Frosinone"),("Fiorentina","Parma"),("Milan","Napoli"),("Monza","Inter"),("Roma","Lazio"),("Sassuolo","Lecce"),("Torino","Genoa"),("Venezia","Juventus")],
33:[("Cagliari","Monza"),("Frosinone","Roma"),("Genoa","Sassuolo"),("Inter","Bologna"),("Juventus","Fiorentina"),("Lazio","Como"),("Lecce","Milan"),("Napoli","Udinese"),("Parma","Atalanta"),("Venezia","Torino")],
34:[("Atalanta","Juventus"),("Bologna","Fiorentina"),("Como","Inter"),("Lecce","Cagliari"),("Milan","Lazio"),("Monza","Venezia"),("Roma","Napoli"),("Sassuolo","Frosinone"),("Torino","Parma"),("Udinese","Genoa")],
35:[("Fiorentina","Roma"),("Frosinone","Atalanta"),("Genoa","Cagliari"),("Inter","Lecce"),("Lazio","Sassuolo"),("Napoli","Monza"),("Parma","Milan"),("Torino","Bologna"),("Udinese","Juventus"),("Venezia","Como")],
36:[("Bologna","Frosinone"),("Cagliari","Torino"),("Como","Atalanta"),("Juventus","Inter"),("Lazio","Udinese"),("Lecce","Fiorentina"),("Milan","Roma"),("Monza","Parma"),("Napoli","Genoa"),("Sassuolo","Venezia")],
37:[("Atalanta","Lecce"),("Fiorentina","Monza"),("Frosinone","Cagliari"),("Genoa","Bologna"),("Inter","Lazio"),("Parma","Juventus"),("Roma","Como"),("Torino","Napoli"),("Udinese","Sassuolo"),("Venezia","Milan")],
38:[("Bologna","Parma"),("Cagliari","Roma"),("Como","Genoa"),("Juventus","Frosinone"),("Lazio","Fiorentina"),("Lecce","Venezia"),("Milan","Udinese"),("Monza","Torino"),("Napoli","Atalanta"),("Sassuolo","Inter")],
}

assert set(PDF_FIXTURES) == set(range(1,39))
assert set(ROUND_DATES) == set(range(1,39))
assert all(len(PDF_FIXTURES[r]) == 10 for r in range(1,39))
all_fixtures=[(r,h,a) for r,pairs in PDF_FIXTURES.items() for h,a in pairs]
teams=sorted({t for _,h,a in all_fixtures for t in (h,a)})
assert len(all_fixtures)==380 and len(teams)==20, (len(all_fixtures), teams)
assert all(len({x for rr,h,a in all_fixtures if rr==r for x in (h,a)})==20 for r in range(1,39)), 'each matchday must use every club exactly once'
assert len({(r,h,a) for r,h,a in all_fixtures})==380, 'duplicate oriented fixture'
by_pair=defaultdict(list)
for r,h,a in all_fixtures: by_pair[frozenset((h,a))].append((r,h,a))
assert len(by_pair)==190 and all(len(v)==2 and v[0][1]==v[1][2] and v[0][2]==v[1][1] for v in by_pair.values()), 'double round-robin pair/venue mismatch'

with RESULTS.open(encoding='utf-8-sig',newline='') as f: old=list(csv.DictReader(f))
old_by_round=defaultdict(set)
for r in old: old_by_round[int(r['matchday'])].add((r['home_team'],r['away_team']))
for md in range(1,11):
    assert old_by_round[md]==set(PDF_FIXTURES[md]), f'existing MD{md} fixtures differ from the official PDF: {old_by_round[md]^set(PDF_FIXTURES[md])}'
assert len(old)==100 and all(len(old_by_round[md])==10 for md in range(1,11))

seen={(int(r['matchday']),r['home_team'],r['away_team']) for r in old}
for md in range(11,39):
    for home,away in PDF_FIXTURES[md]:
        key=(md,home,away)
        assert key not in seen,key
        old.append({'matchday':str(md),'date':'','kickoff_local':'','home_team':home,'home_goals':'','away_goals':'','away_team':away,'status':'scheduled','official_match_id':''})
        seen.add(key)

# Add a distinct official matchday marker; it is not an exact fixture date/time.
fields=list(old[0].keys())
if 'round_date' not in fields: fields.append('round_date')
for row in old:
    row['round_date']=ROUND_DATES[int(row['matchday'])]
with RESULTS.open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(old)

calendar_fields=['matchday','round_date','fixture_date','kickoff_local','home_team','away_team','status','source','source_url']
with CALENDAR.open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=calendar_fields);w.writeheader()
    for md in range(1,39):
        old_map={(r['home_team'],r['away_team']):r for r in old if int(r['matchday'])==md}
        for home,away in PDF_FIXTURES[md]:
            r=old_map.get((home,away),{})
            w.writerow({'matchday':md,'round_date':ROUND_DATES[md],'fixture_date':r.get('date',''),'kickoff_local':r.get('kickoff_local',''),'home_team':home,'away_team':away,'status':r.get('status','scheduled'),'source':'Lega Serie A official season calendar PDF','source_url':PDF_URL})
print(f'PASS: {len(old)} fixtures, {len(teams)} teams, 38 matchdays x10; all home/away pairs occur once each direction.')
print('PASS: current fixtures for MD1-10 match the official PDF exactly; MD11-38 added with no individual date/time inferred.')
print('Official round date markers:', ', '.join(f'MD{md} {ROUND_DATES[md]}' for md in range(1,39)))
