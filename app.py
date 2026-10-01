#!/usr/bin/env python3
"""Local, explainable ticket explorer. No network/model calls."""
import argparse, csv, html, json, re
from collections import Counter, defaultdict
from datetime import datetime, date
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

STOP = set('a an the and or but if then this that i me my we our you your it is are was were be been to of for in on at with from by as have has had do did does not no so very just can could would should will about please thanks thank hi hello hey'.split())
THEMES = {
 'Connectivity': ('connect','pair','pairing','bluetooth','disconnect','wifi','wi-fi'),
 'Battery and charging': ('battery','charge','charging','charger','charging case','drain','power'),
 'Audio quality': ('sound','audio','volume','mic','microphone','noise','bass','distortion','static'),
 'Fit and comfort': ('fit','comfort','ear','ears','hurt','pain','loose','fall'),
 'Delivery and fulfillment': ('delivery','deliver','courier','shipping','shipment','tracking','late','arrived'),
 'Returns and refunds': ('refund','return','replace','replacement','exchange','warranty'),
 'App and setup': ('app','setup','install','update','firmware','watchface','sync'),
 'Device fault': ('broken','defective','faulty','not working','stopped','dead','damage','damaged') }
ALIASES = {
 'date': ['created_at','created_date','ticket_created_at','opened_at','date','created','ticket_date'],
 'id': ['ticket_id','id','case_id'], 'customer': ['customer_message','opening_message','customer_opening_message','message','description','subject'],
 'note': ['agent_note','closing_note','agent_closing_note','resolution_note','close_note'],
 'agent': ['agent_id','agent_name','assigned_agent','owner','assignee'],
 'status': ['status','ticket_status','state'], 'channel': ['channel','contact_channel'],
 'hours': ['handle_hours','hours_worked','work_hours','agent_hours'], 'closed': ['closed_at','resolved_at','completed_at'] }

def load_csv(path):
    with open(path, newline='', encoding='utf-8-sig') as f:
        reader=csv.DictReader(f)
        if not reader.fieldnames: raise ValueError(f'{path}: no header row')
        rows=list(reader)
    return [x.strip() for x in reader.fieldnames], rows

def detect(headers, key):
    norm={re.sub(r'[^a-z0-9]','',h.lower()):h for h in headers}
    for alias in ALIASES[key]:
        if re.sub(r'[^a-z0-9]','',alias) in norm: return norm[re.sub(r'[^a-z0-9]','',alias)]
    return None

def parse_date(s):
    if not s: return None
    s=s.strip()
    for fmt in ('%Y-%m-%d','%Y-%m-%d %H:%M:%S','%m/%d/%Y','%d/%m/%Y','%Y-%m-%dT%H:%M:%S','%Y-%m-%dT%H:%M:%S%z'):
        try: return datetime.strptime(s,fmt).date()
        except ValueError: pass
    try: return datetime.fromisoformat(s.replace('Z','+00:00')).date()
    except ValueError: return None

def week_start(d): return date.fromordinal(d.toordinal()-d.weekday())
def terms(text):
    toks=re.findall(r"[a-zA-Z][a-zA-Z']{2,}", (text or '').lower())
    return [t for t in toks if t not in STOP]

def top_terms(texts, n=5):
    docs=[Counter(set(terms(t))) for t in texts if terms(t)]
    if not docs:return []
    df=Counter()
    for x in docs: df.update(x)
    score=Counter()
    for x in docs:
        for t,c in x.items(): score[t] += c * (1 + (len(docs)/(1+df[t])))
    return [t for t,_ in score.most_common(n)]

def classify(text):
    s=(text or '').lower()
    matches=[]
    for theme, cues in THEMES.items():
        hits=[cue for cue in cues if cue in s]
        if hits: matches.append((theme,len(hits),hits))
    return max(matches,key=lambda x:x[1]) if matches else ('Other / inspect',0,[])

def build_report(tickets_path, agents_path=None):
    headers, rows=load_csv(tickets_path)
    cols={k:detect(headers,k) for k in ALIASES}
    if not cols['date'] or not cols['customer']:
        raise ValueError('Could not detect required date and customer-message columns. Headers: '+', '.join(headers))
    dated=[]; bad_dates=0
    for r in rows:
        d=parse_date(r.get(cols['date'],'') or '')
        if d: dated.append((d,r))
        else: bad_dates+=1
    weeks=defaultdict(list)
    for d,r in dated: weeks[week_start(d)].append(r)
    dupes=0
    if cols['id']:
        ids=[r.get(cols['id'],'') for _,r in dated]; dupes=len(ids)-len(set(i for i in ids if i))
    weekly=[]
    for w, group in sorted(weeks.items()):
        msgs=[r.get(cols['customer'],'') for r in group]
        phrases=top_terms(msgs)
        theme_counts=Counter(classify(m)[0] for m in msgs)
        examples=defaultdict(list)
        for m in msgs:
            theme,_,_=classify(m)
            if theme!='Other / inspect' and m.strip() and len(examples[theme])<1: examples[theme].append(m.strip())
        channel_counts=Counter((r.get(cols['channel']) or 'unknown').strip() for r in group) if cols['channel'] else Counter()
        top_themes=theme_counts.most_common(4)
        weekly.append({'week':w.isoformat(),'count':len(group),'terms':phrases,'themes':top_themes,'examples':dict(examples),'channels':channel_counts.most_common(4)})
    agents={}
    if agents_path:
        try:
            ah, ar=load_csv(agents_path)
            agent_col=detect(ah,'agent') or ah[0]
            agents={r.get(agent_col,''):r for r in ar}
        except OSError: pass
    # Count closures by closure date when available, otherwise creation week; expose this assumption.
    agent_week=defaultdict(Counter); agent_total=Counter(); agent_assigned=Counter(); agent_channels=defaultdict(Counter)
    for d,r in dated:
        a=(r.get(cols['agent']) or '').strip()
        if not a: continue
        agent_assigned[a]+=1
        s=(r.get(cols['status']) or '').lower()
        is_closed= any(x in s for x in ('closed','resolved','complete')) if cols['status'] else True
        if is_closed:
            cd=parse_date(r.get(cols['closed'],'') or '') if cols['closed'] else None
            wk=week_start(cd or d).isoformat()
            agent_week[wk][a]+=1; agent_total[a]+=1
        if cols['channel']: agent_channels[a][(r.get(cols['channel']) or 'unknown').strip()]+=1
    return {'headers':headers,'columns':cols,'total':len(rows),'dated':len(dated),'bad_dates':bad_dates,'dupes':dupes,'weeks':weekly,
            'agents':sorted(agent_total.items(),key=lambda x:(-x[1],x[0])),'agent_assigned':dict(agent_assigned),'agent_weeks':{w:dict(c) for w,c in sorted(agent_week.items())},
            'agent_channels':{a:dict(c) for a,c in agent_channels.items()},'roster_count':len(agents),'agent_name_map':agents}

def render(report):
    esc=html.escape
    weekrows=[]
    for x in report['weeks']:
        themes='; '.join(f'{k} ({v}, {100*v/x["count"]:.0f}%)' for k,v in x['themes']) or '—'
        terms_text='; '.join(x['terms']) or '—'
        channels_text=', '.join(f'{k}: {v}' for k,v in x['channels']) or '—'
        weekrows.append(f"<tr><td>{esc(x['week'])}</td><td>{x['count']}</td><td>{esc(themes)}</td><td>{esc(terms_text)}</td><td>{esc(channels_text)}</td></tr>")
    sections=''.join(weekrows)
    ar=[]
    for a,n in report['agents']:
        by_week=', '.join(f'{w}: {d[a]}' for w,d in report['agent_weeks'].items() if d.get(a))
        channels=', '.join(f'{k}: {v}' for k,v in report['agent_channels'].get(a,{}).items())
        ar.append(f'<tr><td>{esc(a)}</td><td>{n}</td><td>{report["agent_assigned"].get(a,0)}</td><td>{esc(by_week)}</td><td>{esc(channels)}</td></tr>')
    agent_rows=''.join(ar)
    maprows=''.join(f'<li><b>{esc(k)}</b>: {esc(v or "not detected")}</li>' for k,v in report['columns'].items())
    return f'''<!doctype html><meta charset="utf-8"><title>Vireo Support Signals</title><style>body{{font:15px system-ui;max-width:1100px;margin:35px auto;padding:0 22px;color:#202a38}}h1{{color:#173c55}}.cards{{display:flex;gap:12px}}.card{{background:#eff5f8;border-radius:9px;padding:14px 18px}}table{{border-collapse:collapse;width:100%;margin:12px 0 28px}}th,td{{border-bottom:1px solid #dce2e5;padding:9px;text-align:left}}th{{background:#f4f7f8}}.note{{background:#fff6da;padding:12px;border-radius:8px}}small{{color:#54616a}}</style><h1>Vireo Support Signals</h1><p>Local weekly ticket explorer · explainable keyword rules, not model-verified themes.</p><div class="cards"><div class="card"><b>{report['total']:,}</b><br>tickets loaded</div><div class="card"><b>{report['dated']:,}</b><br>with usable dates</div><div class="card"><b>{len(report['weeks'])}</b><br>weeks covered</div><div class="card"><b>{report['bad_dates']:,}</b><br>unparsed dates</div></div><h2>Weekly complaint digest</h2><p><small>Each ticket is assigned to one theme by keyword cues in its opening message. Percent is of dated tickets that week. Themes and terms need review against source text before operational use.</small></p><table><thead><tr><th>Week starting</th><th>Tickets</th><th>Top theme hints</th><th>Frequent terms</th><th>Channel mix</th></tr></thead><tbody>{sections}</tbody></table><h2>Agent workload context</h2><div class="note">Counts are descriptive, not a performance leaderboard. If a status field exists, only statuses containing “closed”, “resolved”, or “complete” count; otherwise all assigned tickets count as a proxy. Closure week uses closed/resolved date if detected, else creation week. This does not adjust for hours, shift, complexity, tenure, or reopen rate.</div><table><thead><tr><th>Agent</th><th>Counted closures</th><th>Assigned tickets</th><th>Weekly counts</th><th>Assigned channel mix</th></tr></thead><tbody>{agent_rows or '<tr><td colspan="5">No agent field detected</td></tr>'}</tbody></table><h2>Input checks</h2><p>{report['dupes']:,} repeated ticket IDs among dated rows; roster rows loaded: {report['roster_count']}. Fields detected:</p><ul>{maprows}</ul><p>Raw files stay local. This prototype makes no external AI calls.</p>'''

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--tickets',default='data/tickets.csv'); ap.add_argument('--agents',default='data/agents.csv'); ap.add_argument('--port',type=int,default=8765)
    ap.add_argument('--report',default='report.html',help='Write an HTML report instead of serving it')
    a=ap.parse_args()
    try: report=build_report(a.tickets,a.agents if Path(a.agents).exists() else None)
    except (OSError,ValueError) as e: raise SystemExit(str(e))
    if a.report:
        Path(a.report).write_text(render(report),encoding='utf-8'); print(f'Wrote {a.report}')
    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            body=render(report).encode()
            self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
        def log_message(self,*_): pass
    server=HTTPServer(('127.0.0.1',a.port),H)
    print(f'Open http://127.0.0.1:{a.port}  (Ctrl-C to stop)'); server.serve_forever()
if __name__=='__main__': main()
