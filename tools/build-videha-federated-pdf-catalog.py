#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

OWNER = os.environ.get('VIDEHA_GITHUB_OWNER', 'videha-ejournal')
ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else 'data/videha-federated-pdf-catalog.json')
REVIEW_OUT = Path(sys.argv[3] if len(sys.argv) > 3 else 'data/videha-federated-pdf-review.json')
PREVIOUS_PATH = ROOT / OUT if not OUT.is_absolute() else OUT
LOCAL_CATALOG_PATH = ROOT / 'data' / 'videha-pdf-catalog.json'
CURATED_PATH = ROOT / 'data' / 'federated-pdf-metadata.json'
TOKEN = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
USER_AGENT = 'Videha-Federated-PDF-Catalog/1.0'
HASH_BUDGET_BYTES = int(os.environ.get('VIDEHA_FEDERATED_HASH_BUDGET_BYTES', str(1024 * 1024 * 1024)))

MACHINE_KEYS = {
    'path', 'name', 'title', 'url', 'rawUrl', 'repositoryUrl', 'mediaType', 'bytes',
    'sha256', 'largeFileWarning', 'repository', 'branch', 'gitBlobSha', 'pagesUrl',
}


def utc_now():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def api_get(url):
    headers = {'User-Agent': USER_AGENT, 'Accept': 'application/vnd.github+json'}
    if TOKEN:
        headers['Authorization'] = f'Bearer {TOKEN}'
        headers['X-GitHub-Api-Version'] = '2022-11-28'
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def iter_owner_repositories():
    page = 1
    while True:
        query = urllib.parse.urlencode({'per_page': 100, 'page': page, 'type': 'owner', 'sort': 'full_name'})
        rows = api_get(f'https://api.github.com/users/{OWNER}/repos?{query}')
        if not rows:
            break
        for row in rows:
            if row.get('archived') or row.get('disabled'):
                continue
            yield row
        if len(rows) < 100:
            break
        page += 1


def repository_tree(repository, branch):
    encoded_branch = urllib.parse.quote(branch, safe='')
    return api_get(f'https://api.github.com/repos/{repository}/git/trees/{encoded_branch}?recursive=1')


def hash_stream(url):
    headers = {'User-Agent': USER_AGENT, 'Accept-Encoding': 'identity'}
    if TOKEN and url.startswith('https://raw.githubusercontent.com/'):
        headers['Authorization'] = f'Bearer {TOKEN}'
    request = urllib.request.Request(url, headers=headers)
    digest = hashlib.sha256()
    total = 0
    prefix = b''
    with urllib.request.urlopen(request, timeout=180) as response:
        while True:
            block = response.read(1024 * 1024)
            if not block:
                break
            if len(prefix) < 256:
                prefix += block[:256 - len(prefix)]
            digest.update(block)
            total += len(block)
    if prefix.startswith(b'version https://git-lfs.github.com/spec/v1'):
        raise RuntimeError('raw download returned a Git LFS pointer instead of PDF bytes')
    return digest.hexdigest(), total


def title_for(path):
    stem = Path(path).stem.replace('_', ' ').replace('-', ' ')
    return ' '.join(stem.split()) or Path(path).name


def metadata_needs_editorial_review(path):
    folded = path.lower().replace('-', '_')
    relation_markers = (
        'translation', 'translated', 'english_', '_english', 'anuvad', 'original', 'source_',
        'bilingual', 'samagra', 'maithili_english', 'english_maithili', 'translator', 'edited',
    )
    return any(marker in folded for marker in relation_markers)


def pages_url(repository_name, encoded_path):
    if repository_name == f'{OWNER}.github.io':
        return f'https://{OWNER}.github.io/{encoded_path}'
    return f'https://{OWNER}.github.io/{repository_name}/{encoded_path}'


def load_json(path, default):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except FileNotFoundError:
        return default


previous_payload = load_json(PREVIOUS_PATH, {})
previous_by_key = {item['key']: item for item in previous_payload.get('items', []) if item.get('key')}
curated_payload = load_json(CURATED_PATH, {})
if not isinstance(curated_payload, dict):
    raise SystemExit(f'{CURATED_PATH} must contain a JSON object')
curated = curated_payload.get('resources', curated_payload)
if not isinstance(curated, dict):
    raise SystemExit(f'{CURATED_PATH} resources must be an object keyed by repository:path')
local_catalog = load_json(LOCAL_CATALOG_PATH, {'items': []})
local_by_path = {item['path']: item for item in local_catalog.get('items', []) if item.get('path')}

now = utc_now()
discovered = []
warnings = []
repositories = list(iter_owner_repositories())
for repo in repositories:
    repository = repo['full_name']
    repository_name = repo['name']
    branch = repo.get('default_branch') or 'main'
    try:
        tree = repository_tree(repository, branch)
    except Exception as exc:
        warnings.append(f'{repository}: tree discovery failed: {exc}')
        continue
    if tree.get('truncated'):
        warnings.append(f'{repository}: recursive Git tree was truncated; catalogue may be incomplete for this repository')
    for node in tree.get('tree', []):
        path = node.get('path') or ''
        if node.get('type') != 'blob' or not path.lower().endswith('.pdf'):
            continue
        encoded_path = urllib.parse.quote(path, safe='/')
        key = f'{repository}:{path}'
        raw_url = f'https://raw.githubusercontent.com/{repository}/{urllib.parse.quote(branch, safe="")}/{encoded_path}'
        metadata = curated.get(key, {})
        item = {
            'key': key,
            'repository': repository,
            'branch': branch,
            'path': path,
            'name': Path(path).name,
            'title': metadata.get('title', title_for(path)),
            'mediaType': 'application/pdf',
            'bytes': node.get('size'),
            'gitBlobSha': node.get('sha'),
            'pagesUrl': pages_url(repository_name, encoded_path),
            'rawUrl': raw_url,
            'repositoryUrl': f'https://github.com/{repository}/blob/{urllib.parse.quote(branch, safe="")}/{encoded_path}',
        }
        for field, value in metadata.items():
            if field != 'title':
                item[field] = value
        old = previous_by_key.get(key)
        if old and old.get('gitBlobSha') == item['gitBlobSha'] and old.get('sha256'):
            item['sha256'] = old['sha256']
            item['hashStatus'] = 'verified'
            item['bytes'] = old.get('bytes', item['bytes'])
            item['firstSeenAt'] = old.get('firstSeenAt', now)
        else:
            item['sha256'] = None
            item['hashStatus'] = 'pending'
            item['firstSeenAt'] = old.get('firstSeenAt', now) if old else now
        if repository == f'{OWNER}/videha-ejournal' and path in local_by_path:
            central = local_by_path[path]
            item['sha256'] = central.get('sha256')
            item['bytes'] = central.get('bytes', item['bytes'])
            item['hashStatus'] = 'verified'
            editorial_fields = {k: v for k, v in central.items() if k not in MACHINE_KEYS}
            if editorial_fields:
                for field, value in editorial_fields.items():
                    item.setdefault(field, value)
                item['metadataStatus'] = 'catalogued-scholarly-metadata'
            else:
                item['metadataStatus'] = 'legacy-catalogued'
        elif metadata:
            item['metadataStatus'] = 'curated'
        elif metadata_needs_editorial_review(path):
            item['metadataStatus'] = 'review-needed'
        else:
            item['metadataStatus'] = 'machine-complete'
        discovered.append(item)

# Prioritize truly new/changed resources before legacy pending backlog.
def hash_priority(item):
    old = previous_by_key.get(item['key'])
    if not old:
        return (0, item['bytes'] or 0, item['key'].lower())
    if old.get('gitBlobSha') != item.get('gitBlobSha'):
        return (1, item['bytes'] or 0, item['key'].lower())
    return (2, item['bytes'] or 0, item['key'].lower())

budget_used = 0
for item in sorted((x for x in discovered if not x.get('sha256')), key=hash_priority):
    expected = item.get('bytes') or 0
    if budget_used and expected and budget_used + expected > HASH_BUDGET_BYTES:
        item['hashStatus'] = 'pending-budget'
        continue
    try:
        digest, downloaded = hash_stream(item['rawUrl'])
        item['sha256'] = digest
        item['bytes'] = downloaded
        item['hashStatus'] = 'verified'
        budget_used += downloaded
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, RuntimeError) as exc:
        item['hashStatus'] = 'error'
        item['hashError'] = str(exc)
        warnings.append(f"{item['key']}: SHA-256 calculation failed: {exc}")

items = sorted(discovered, key=lambda item: (item['repository'].lower(), item['path'].lower()))
keys = {item['key'] for item in items}
removed = sorted(key for key in previous_by_key if key not in keys)
review = []
for item in items:
    if item.get('metadataStatus') != 'review-needed':
        continue
    review.append({
        'key': item['key'],
        'repository': item['repository'],
        'path': item['path'],
        'suggestedTitle': item['title'],
        'sha256': item.get('sha256'),
        'hashStatus': item.get('hashStatus'),
        'editorialDecision': 'Review only if title, authorship, language, translation/editorship, edition or source relationships require scholarly correction.',
    })

catalog_core = {
    'schemaVersion': 1,
    'owner': OWNER,
    'repositoryCount': len(repositories),
    'itemCount': len(items),
    'verifiedHashCount': sum(1 for item in items if item.get('sha256')),
    'pendingHashCount': sum(1 for item in items if not item.get('sha256')),
    'metadataReviewCount': len(review),
    'hashBudgetBytes': HASH_BUDGET_BYTES,
    'warnings': warnings,
    'items': items,
}
previous_core = {key: value for key, value in previous_payload.items() if key != 'generatedAt'}
generated_at = now if catalog_core != previous_core else previous_payload.get('generatedAt', now)
payload = {'generatedAt': generated_at, **catalog_core}
review_payload = {
    'schemaVersion': 1,
    'generatedAt': generated_at,
    'owner': OWNER,
    'reviewCount': len(review),
    'instructions': 'Machine-verifiable fields are automatic. Edit data/federated-pdf-metadata.json only where scholarly metadata needs an editorial decision.',
    'items': review,
}

for target, value in ((OUT, payload), (REVIEW_OUT, review_payload)):
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

print(
    f"Federated PDF catalogue: {len(items)} PDF(s) across {len(repositories)} repositories; "
    f"{payload['verifiedHashCount']} hash-verified, {payload['pendingHashCount']} pending, "
    f"{len(review)} scholarly metadata review item(s); downloaded {budget_used} byte(s) this run; "
    f"{len(removed)} removed since the previous catalogue."
)
if warnings:
    print(f'Warnings: {len(warnings)}')
