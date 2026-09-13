#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
import re
import sys
import urllib.parse

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else 'data/videha-pdf-catalog.json')
METADATA_PATH = ROOT / 'data' / 'curated-pdf-metadata.json'
BASE = 'https://videha-ejournal.github.io/videha-ejournal/'
RAW = 'https://raw.githubusercontent.com/videha-ejournal/videha-ejournal/main/'
REPO = 'https://github.com/videha-ejournal/videha-ejournal'
LARGE_WARNING = 95 * 1024 * 1024

if not METADATA_PATH.exists():
    raise SystemExit(f'Missing curated metadata file: {METADATA_PATH}')

CURATED_METADATA = json.loads(METADATA_PATH.read_text(encoding='utf-8'))


def title_for(path):
    title = path.stem.replace('_', ' ').replace('-', ' ')
    title = re.sub(r'\s+', ' ', title).strip()
    return title or path.name


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


items = []
for pdf_path in ROOT.rglob('*.pdf'):
    if '.git' in pdf_path.parts:
        continue
    relative = pdf_path.relative_to(ROOT).as_posix()
    encoded = urllib.parse.quote(relative, safe='/')
    size = pdf_path.stat().st_size
    curated = CURATED_METADATA.get(relative, {})
    item = {
        'path': relative,
        'name': pdf_path.name,
        'title': curated.get('title', title_for(pdf_path)),
        'url': BASE + encoded,
        'rawUrl': RAW + encoded,
        'repositoryUrl': REPO + '/blob/main/' + encoded,
        'mediaType': 'application/pdf',
        'bytes': size,
        'sha256': sha256_file(pdf_path),
        'largeFileWarning': size >= LARGE_WARNING,
    }
    item.update({key: value for key, value in curated.items() if key != 'title'})
    items.append(item)

items.sort(key=lambda value: value['path'].lower())
payload = {
    'schemaVersion': 5,
    'version': '2026-09-13',
    'repository': 'videha-ejournal/videha-ejournal',
    'baseUrl': BASE,
    'count': len(items),
    'totalBytes': sum(item['bytes'] for item in items),
    'largeFileWarningThresholdBytes': LARGE_WARNING,
    'largeFileWarningCount': sum(1 for item in items if item['largeFileWarning']),
    'items': items,
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
print(
    f"Wrote {len(items)} PDF entries ({payload['totalBytes']} bytes) to {OUT}; "
    f"{payload['largeFileWarningCount']} at or above 95 MiB."
)
