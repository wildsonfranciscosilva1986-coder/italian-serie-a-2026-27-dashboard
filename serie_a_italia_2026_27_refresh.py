"""Refresh final Serie A scores from ESPN's public scoreboard, bound to Lega's official fixture calendar.

Only completed events that match a unique official fixture are applied. Existing final scores are immutable: any conflict aborts the run. Scheduled kickoffs for future matchdays are never inferred from ESPN.
"""
import argparse
import csv
import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / 'serie_a_italia_2026_27_results.csv'
SNAPSHOTS = ROOT / 'source_snapshots'
ROME = ZoneInfo('Europe/Rome')
ALIASES = {
    'Internazionale':'Inter', 'FC Internazionale Milano':'Inter', 'Inter Milan':'Inter',
    'AS Roma':'Roma', 'Roma':'Roma', 'AC Milan':'Milan',
    'Atalanta BC':'Atalanta', 'Bologna FC 1909':'Bologna', 'Cagliari Calcio':'Cagliari',
    'Como 1907':'Como', 'Frosinone Calcio':'Frosinone', 'Genoa CFC':'Genoa',
    'Juventus FC':'Juventus', 'SS Lazio':'Lazio', 'US Lecce':'Lecce',
    'AC Monza':'Monza', 'SSC Napoli':'Napoli', 'Parma Calcio 1913':'Parma',
    'US Sassuolo Calcio':'Sassuolo', 'Torino FC':'Torino', 'Udinese Calcio':'Udinese',
    'Venezia FC':'Venezia'
}


def fetch_scoreboard(day):
    url = f'https://site.api.espn.com/apis/site/v2/sports/soccer/ita.1/scoreboard?dates={day:%Y%m%d}'
    request = urllib.request.Request(url, headers={'User-Agent':'DIN-Mercado-dashboard/1.0','Accept':'application/json'})
    last_error = None
    for attempt in range(2):
        try:
            with urllib.request.urlopen(request, timeout=35) as response:
                payload = json.loads(response.read())
            if not isinstance(payload.get('events'), list):
                raise RuntimeError(f'ESPN payload missing events for {day}: {list(payload)[:8]}')
            return url, payload
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, RuntimeError) as exc:
            last_error = exc
            if attempt == 0:
                time.sleep(2)
    raise RuntimeError(f'ESPN scoreboard failed for {day}: {last_error}')


def canon(name):
    return ALIASES.get(name, name)


def final_event(event):
    competitions = event.get('competitions') or []
    if not competitions:
        return None
    comp = competitions[0]
    status = comp.get('status', {}).get('type', {})
    if status.get('completed') is not True:
        return None
    competitors = comp.get('competitors') or []
    home = next((x for x in competitors if x.get('homeAway') == 'home'), None)
    away = next((x for x in competitors if x.get('homeAway') == 'away'), None)
    if not home or not away:
        raise RuntimeError(f"Completed ESPN event missing home/away: {event.get('id')}")
    try:
        hs, as_ = int(home['score']), int(away['score'])
    except (KeyError, TypeError, ValueError):
        raise RuntimeError(f"Completed ESPN event has invalid score: {event.get('id')}")
    raw_date = event.get('date')
    if not raw_date:
        raise RuntimeError(f"Completed ESPN event missing date: {event.get('id')}")
    kickoff = datetime.fromisoformat(raw_date.replace('Z', '+00:00')).astimezone(ROME)
    return {
        'event_id': str(event.get('id') or ''),
        'home': canon(home.get('team', {}).get('displayName', '')),
        'away': canon(away.get('team', {}).get('displayName', '')),
        'home_goals': hs,
        'away_goals': as_,
        'date': kickoff.strftime('%Y-%m-%d'),
        'time': kickoff.strftime('%H:%M'),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check-only', action='store_true', help='fetch and validate without writing files')
    parser.add_argument('--days-back', type=int, default=10, help='calendar days to re-check before today (default 10)')
    args = parser.parse_args()
    if args.days_back < 1 or args.days_back > 30:
        raise SystemExit('--days-back must be 1–30')

    with RESULTS.open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fields = list(reader.fieldnames or [])
    key_to_row = {}
    for row in rows:
        key = (row['home_team'], row['away_team'])
        if key in key_to_row:
            raise RuntimeError(f'Duplicate official home/away fixture in season schedule: {key}')
        key_to_row[key] = row
    if len(rows) != 380:
        raise RuntimeError(f'Official fixture list has {len(rows)} rows; expected 380')
    if 'espn_event_id' not in fields:
        fields.append('espn_event_id')
        for row in rows:
            row['espn_event_id'] = ''

    today = datetime.now(ROME).date()
    fetched = []
    candidate_events = {}
    for offset in range(args.days_back, -1, -1):
        day = today - timedelta(days=offset)
        url, payload = fetch_scoreboard(day)
        events = payload.get('events', [])
        if events:
            fetched.append((day, url, payload))
        for event in events:
            item = final_event(event)
            if item is None:
                continue
            item['source_url'] = url
            item['scoreboard_date'] = day.strftime('%Y%m%d')
            item['raw_event'] = event
            key = (item['home'], item['away'])
            if key not in key_to_row:
                raise RuntimeError(f"Finished ESPN fixture not found in official PDF schedule: {key}, event {item['event_id']}")
            if key in candidate_events:
                prior = candidate_events[key]
                if (prior['home_goals'], prior['away_goals']) != (item['home_goals'], item['away_goals']):
                    raise RuntimeError(f'Conflicting ESPN finals for {key}: {prior} vs {item}')
                continue
            candidate_events[key] = item

    updates = []
    result_sources = {}
    for key, item in candidate_events.items():
        row = key_to_row[key]
        score = (str(item['home_goals']), str(item['away_goals']))
        if row['status'] == 'finished':
            existing = (row['home_goals'], row['away_goals'])
            if existing != score:
                raise RuntimeError(f'Final score conflict for {key}: existing {existing}, ESPN {score}; refusing overwrite')
            continue
        row['home_goals'], row['away_goals'] = score
        row['date'], row['kickoff_local'] = item['date'], item['time']
        row['status'] = 'finished'
        row['espn_event_id'] = item['event_id']
        updates.append({'match':f"{key[0]}–{key[1]}",'score':f"{score[0]}–{score[1]}",'date':item['date'],'event_id':item['event_id'],'source_url':item['source_url']})
        result_sources[key]={'event_id':item['event_id'],'source_url':item['source_url'],'scoreboard_date':item['scoreboard_date'],'raw_event':item['raw_event']}

    if not args.check_only:
        SNAPSHOTS.mkdir(exist_ok=True)
        retrieved_at=datetime.now(ROME).isoformat(timespec='seconds')
        for key, source in result_sources.items():
            path=SNAPSHOTS/f"espn_result_{source['event_id']}.json"
            archive={'source_url':source['source_url'],'scoreboard_date':source['scoreboard_date'],'retrieved_at':retrieved_at,'official_fixture':{'home':key[0],'away':key[1]},'event':source['raw_event']}
            archive_bytes=(json.dumps(archive,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
            if path.exists() and path.read_bytes()!=archive_bytes:
                raise RuntimeError(f'Refusing to overwrite existing ESPN result archive: {path.name}')
            if not path.exists():path.write_bytes(archive_bytes)
        with RESULTS.open('w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader(); writer.writerows(rows)
        log = {
            'cutoff':datetime.now(ROME).isoformat(timespec='minutes'),
            'scoreboard':'ESPN public soccer scoreboard API, Italy Serie A (ita.1)',
            'dates_checked':[str(today-timedelta(days=x)) for x in range(args.days_back,-1,-1)],
            'completed_events_checked':len(candidate_events),
            'new_results_applied':updates,
            'note':'Only final scores matched to the official Lega fixture list are applied; existing results are never overwritten; future individual kickoffs are not inferred.'
        }
        (SNAPSHOTS / f'refresh_log_{today:%Y%m%d}.json').write_text(json.dumps(log,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Checked {args.days_back+1} dates; {len(candidate_events)} completed fixtures matched; {len(updates)} new final results.' + (' No files changed (--check-only).' if args.check_only else ''))
    for item in updates:
        print(f"NEW {item['date']} {item['match']} {item['score']}")


if __name__ == '__main__':
    main()
