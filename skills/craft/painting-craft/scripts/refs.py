"""Fetch public-domain reference images to look at before and while painting.

usage: python3 refs.py "QUERY" OUTDIR [--source met|commons] [--n 4] [--width 1200]

met:     The Met's open-access collection (armour, costume, objects, paintings), public domain only.
commons: Wikimedia Commons files (paintings by named artists, places, vehicles).
Prints each saved file with its title and source page, so the source can be named.
"""
import argparse, json, os, re, urllib.parse, urllib.request

ap = argparse.ArgumentParser()
ap.add_argument('query'); ap.add_argument('outdir')
ap.add_argument('--source', choices=['met', 'commons'], default='commons')
ap.add_argument('--n', type=int, default=4)
ap.add_argument('--width', type=int, default=1200)
a = ap.parse_args()
os.makedirs(a.outdir, exist_ok=True)
UA = {'User-Agent': 'painting-craft-refs/1.0 (reference lookup)'}


def get(url, raw=False):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        data = r.read()
    return data if raw else json.loads(data)


def save(url, title, page):
    name = re.sub(r'[^A-Za-z0-9]+', '-', title)[:60].strip('-') + os.path.splitext(urllib.parse.urlparse(url).path)[1]
    path = os.path.join(a.outdir, name)
    with open(path, 'wb') as f:
        f.write(get(url, raw=True))
    print(f'{path}\t{title}\t{page}')


if a.source == 'met':
    base = 'https://collectionapi.metmuseum.org/public/collection/v1.1'
    q = urllib.parse.urlencode({'q': a.query, 'hasImages': 'true', 'limit': a.n * 4, 'offset': 0})
    got = 0
    for oid in get(f'{base}/search?{q}').get('objectIDs') or []:
        o = get(f'https://collectionapi.metmuseum.org/public/collection/v1/objects/{oid}')
        img = o.get('primaryImageSmall') or o.get('primaryImage')
        if o.get('isPublicDomain') and img:
            save(img, f"{o.get('title', '')} {o.get('objectDate', '')}", o.get('objectURL', ''))
            got += 1
            if got >= a.n:
                break
else:
    api = 'https://commons.wikimedia.org/w/api.php'
    q = urllib.parse.urlencode({'action': 'query', 'list': 'search', 'srnamespace': 6, 'srsearch': a.query,
                                'srlimit': a.n, 'format': 'json'})
    for hit in get(f'{api}?{q}')['query']['search']:
        q2 = urllib.parse.urlencode({'action': 'query', 'titles': hit['title'], 'prop': 'imageinfo',
                                     'iiprop': 'url', 'iiurlwidth': a.width, 'format': 'json'})
        info = list(get(f'{api}?{q2}')['query']['pages'].values())[0].get('imageinfo', [{}])[0]
        if info.get('thumburl'):
            save(info['thumburl'].split('?')[0], hit['title'][5:], info.get('descriptionurl', ''))
