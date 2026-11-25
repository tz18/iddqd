"""Download Blake's works from Wikisource (page HTML, politely: 1 request/s), following sub-pages of each work.
Writes plain text per page into blakecrawl/ and a combined blake_corpus.txt."""
import os, re, sys, time, html, urllib.request, urllib.parse
D = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(D, 'sources', 'blake', 'raw')
works = [w.replace('&amp;', '&') for w in open(os.path.join(D, 'blake', 'works.txt')).read().split('\n') if w and 'redlink' not in w]
def get(page):
    url = 'https://en.wikisource.org/wiki/' + urllib.parse.quote(page, safe='/(),\'')
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (research text download)'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=40) as r: return r.read().decode('utf-8', 'replace')
        except Exception as e:
            time.sleep(5 * (attempt + 1)); err = e
    print('FAIL', page, err, flush=True); return ''
def text_of(h):
    m = h.find('class="mw-content-ltr mw-parser-output"')
    body = h[m:] if m >= 0 else h
    body = body[:body.find('<div class="printfooter"')] if '<div class="printfooter"' in body else body
    body = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', body, flags=re.S)
    body = re.sub(r'<(div|span)[^>]*class="[^"]*(ws-noexport|wst-header|header|navbox|reference|mw-editsection|pagenum|ws-pagenum)[^"]*"[^>]*>.*?</\1>', ' ', body, flags=re.S)
    body = re.sub(r'<br\s*/?>|</p>|</div>|</li>|</h\d>', '\n', body)
    t = html.unescape(re.sub(r'<[^>]+>', ' ', body)); t = re.sub(r'[ \t]+', ' ', t); t = re.sub(r'\n\s*\n+', '\n', t)
    return t.strip()
seen = set(); queue = list(works); n = 0
while queue:
    p = queue.pop(0)
    if p in seen: continue
    seen.add(p); h = get(p); time.sleep(1.0); n += 1
    if not h: continue
    fn = os.path.join(OUT, re.sub(r'[^A-Za-z0-9_.-]', '_', p)[:150] + '.txt'); open(fn, 'w').write(text_of(h))
    for sub in re.findall(r'href="(?:https://en\.wikisource\.org/wiki/|\./)(' + re.escape(urllib.parse.quote(p.split('/')[0], safe='(),\'')) + r'/[^"#?]+)"', h):
        s = urllib.parse.unquote(sub)
        if s not in seen: queue.append(s)
    if n % 20 == 0: print(n, 'pages fetched, queue', len(queue), flush=True)
print('done', n, 'pages', flush=True)
