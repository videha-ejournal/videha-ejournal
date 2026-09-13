#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,sys,urllib.parse

ROOT=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
OUT=Path(sys.argv[2] if len(sys.argv)>2 else 'data/videha-pdf-catalog.json')
BASE='https://videha-ejournal.github.io/videha-ejournal/'
RAW='https://raw.githubusercontent.com/videha-ejournal/videha-ejournal/main/'
REPO='https://github.com/videha-ejournal/videha-ejournal'
LARGE_WARNING=95*1024*1024

def title_for(path):
    s=path.stem.replace('_',' ').replace('-',' ')
    s=re.sub(r'\s+',' ',s).strip()
    return s or path.name

def sha256_file(path):
    h=hashlib.sha256()
    with path.open('rb') as fh:
        for block in iter(lambda:fh.read(1024*1024),b''):
            h.update(block)
    return h.hexdigest()

items=[]
for p in ROOT.rglob('*.pdf'):
    if '.git' in p.parts:
        continue
    rel=p.relative_to(ROOT).as_posix()
    encoded=urllib.parse.quote(rel,safe='/')
    size=p.stat().st_size
    items.append({
        'path':rel,
        'name':p.name,
        'title':title_for(p),
        'url':BASE+encoded,
        'rawUrl':RAW+encoded,
        'repositoryUrl':REPO+'/blob/main/'+encoded,
        'mediaType':'application/pdf',
        'bytes':size,
        'sha256':sha256_file(p),
        'largeFileWarning':size>=LARGE_WARNING
    })
items.sort(key=lambda x:x['path'].lower())
payload={
    'schemaVersion':2,
    'version':'2026-09-13',
    'repository':'videha-ejournal/videha-ejournal',
    'baseUrl':BASE,
    'count':len(items),
    'totalBytes':sum(x['bytes'] for x in items),
    'largeFileWarningThresholdBytes':LARGE_WARNING,
    'largeFileWarningCount':sum(1 for x in items if x['largeFileWarning']),
    'items':items
}
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
print(f"Wrote {len(items)} PDF entries ({payload['totalBytes']} bytes) to {OUT}; {payload['largeFileWarningCount']} at or above 95 MiB.")
