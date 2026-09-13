#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,sys,urllib.parse

ROOT=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
OUT=Path(sys.argv[2] if len(sys.argv)>2 else 'data/videha-pdf-catalog.json')
BASE='https://videha-ejournal.github.io/videha-ejournal/'
RAW='https://raw.githubusercontent.com/videha-ejournal/videha-ejournal/main/'
REPO='https://github.com/videha-ejournal/videha-ejournal'
LARGE_WARNING=95*1024*1024
GOHI_ORIGINAL='Gohi_Sabhak_Beech_Jalsamadhi.pdf'
GOHI_FAMILY_ID='gohi-sabhak-beech-jalsamadhi'
GOHI_FAMILY_TITLE='Gohi Sabhak Beech Jalsamadhi'

CURATED_METADATA={
    '37_CHILDREN_NOVELS.pdf':{
        'title':'37 Children Novels — English Translation',
        'language':'English',
        'languageCode':'en',
        'editionNote':'English translation of the Maithili collection “37 Maithili Children Novels”.',
        'translationOf':'GAJENDRA_THAKUR_SAMAGRA_37_MAITHILI_CHILDREN_NOVELS.pdf',
        'translationOfTitle':'Gajendra Thakur Samagra: 37 Maithili Children Novels — Maithili Original',
    },
    'GAJENDRA_THAKUR_SAMAGRA_37_MAITHILI_CHILDREN_NOVELS.pdf':{
        'title':'Gajendra Thakur Samagra: 37 Maithili Children Novels — Maithili Original',
        'language':'Maithili',
        'languageCode':'mai',
        'editionNote':'Maithili original collection.',
        'translatedAs':'37_CHILDREN_NOVELS.pdf',
        'translatedAsTitle':'37 Children Novels — English Translation',
    },
    'GADYA_PADYA_BHARTI_1.pdf':{
        'title':'GADYA PADYA BHARTI 1',
        'seriesTitle':'GADYA PADYA BHARTI',
        'seriesPart':1,
    },
    'GAJENDRA_THAKUR_SAMAGRA_ANUVAD_KHAND.pdf':{
        'title':'GADYA PADYA BHARTI 2 — Gajendra Thakur Samagra Anuvad Khand',
        'alternateTitle':'GAJENDRA THAKUR SAMAGRA ANUVAD KHAND',
        'seriesTitle':'GADYA PADYA BHARTI',
        'seriesPart':2,
        'editionNote':'Catalogued as GADYA PADYA BHARTI 2; repository filename retained unchanged.',
    },
    GOHI_ORIGINAL:{
        'title':'Gohi Sabhak Beech Jalsamadhi — Principal Maithili Novel',
        'language':'Maithili',
        'languageCode':'mai',
        'workFamilyId':GOHI_FAMILY_ID,
        'workFamilyTitle':GOHI_FAMILY_TITLE,
        'workFamilyRole':'principal-work',
        'editionNote':'Principal Maithili novel; the largest Maithili novel in the Videha corpus. Source work for the Bal Sanskaran, Kishor Sanskaran, English translation, and teaching resources.',
        'translatedAs':'Water_Burial_Among_the_Crocodiles.pdf',
        'translatedAsTitle':'Water-Burial Among the Crocodiles — English Translation',
        'relatedResources':[
            {'path':'Gohi_Jalsamadhi_Bal_Sanskaran.pdf','title':'Gohi Jalsamadhi — Bal Sanskaran','relation':'bal-sanskaran'},
            {'path':'Gohi_Jalsamadhi_Kishor_Sanskaran.pdf','title':'Gohi Jalsamadhi — Kishor Sanskaran','relation':'kishor-sanskaran'},
            {'path':'Water_Burial_Among_the_Crocodiles.pdf','title':'Water-Burial Among the Crocodiles — English Translation','relation':'english-translation'},
            {'path':'Videha_Teaching_Gohi_Jalsamadhi.pdf','title':'Videha Teaching: Gohi Jalsamadhi','relation':'teaching-resource'},
            {'path':'Gohi_Jalsamadhi_Teaching_merge.pdf','title':'Gohi Jalsamadhi — Teaching Merge','relation':'teaching-resource'},
        ],
    },
    'Gohi_Jalsamadhi_Bal_Sanskaran.pdf':{
        'title':'Gohi Jalsamadhi — Bal Sanskaran',
        'language':'Maithili',
        'languageCode':'mai',
        'workFamilyId':GOHI_FAMILY_ID,
        'workFamilyTitle':GOHI_FAMILY_TITLE,
        'workFamilyRole':'bal-sanskaran',
        'editionNote':'Bal Sanskaran (children’s adaptation) of Gohi Sabhak Beech Jalsamadhi.',
        'isBasedOn':GOHI_ORIGINAL,
        'isBasedOnTitle':'Gohi Sabhak Beech Jalsamadhi — Principal Maithili Novel',
    },
    'Gohi_Jalsamadhi_Kishor_Sanskaran.pdf':{
        'title':'Gohi Jalsamadhi — Kishor Sanskaran',
        'language':'Maithili',
        'languageCode':'mai',
        'workFamilyId':GOHI_FAMILY_ID,
        'workFamilyTitle':GOHI_FAMILY_TITLE,
        'workFamilyRole':'kishor-sanskaran',
        'editionNote':'Kishor Sanskaran (adolescent edition) of Gohi Sabhak Beech Jalsamadhi.',
        'isBasedOn':GOHI_ORIGINAL,
        'isBasedOnTitle':'Gohi Sabhak Beech Jalsamadhi — Principal Maithili Novel',
    },
    'Water_Burial_Among_the_Crocodiles.pdf':{
        'title':'Water-Burial Among the Crocodiles — English Translation',
        'language':'English',
        'languageCode':'en',
        'workFamilyId':GOHI_FAMILY_ID,
        'workFamilyTitle':GOHI_FAMILY_TITLE,
        'workFamilyRole':'english-translation',
        'editionNote':'English translation of the Maithili novel Gohi Sabhak Beech Jalsamadhi.',
        'translationOf':GOHI_ORIGINAL,
        'translationOfTitle':'Gohi Sabhak Beech Jalsamadhi — Principal Maithili Novel',
    },
    'Videha_Teaching_Gohi_Jalsamadhi.pdf':{
        'title':'Videha Teaching: Gohi Jalsamadhi',
        'workFamilyId':GOHI_FAMILY_ID,
        'workFamilyTitle':GOHI_FAMILY_TITLE,
        'workFamilyRole':'teaching-resource',
        'editionNote':'Videha teaching resource based on Gohi Sabhak Beech Jalsamadhi.',
        'isBasedOn':GOHI_ORIGINAL,
        'isBasedOnTitle':'Gohi Sabhak Beech Jalsamadhi — Principal Maithili Novel',
    },
    'Gohi_Jalsamadhi_Teaching_merge.pdf':{
        'title':'Gohi Jalsamadhi — Teaching Merge',
        'workFamilyId':GOHI_FAMILY_ID,
        'workFamilyTitle':GOHI_FAMILY_TITLE,
        'workFamilyRole':'teaching-resource',
        'editionNote':'Combined teaching resource based on Gohi Sabhak Beech Jalsamadhi.',
        'isBasedOn':GOHI_ORIGINAL,
        'isBasedOnTitle':'Gohi Sabhak Beech Jalsamadhi — Principal Maithili Novel',
    },
}

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
    curated=CURATED_METADATA.get(rel,{})
    item={
        'path':rel,
        'name':p.name,
        'title':curated.get('title',title_for(p)),
        'url':BASE+encoded,
        'rawUrl':RAW+encoded,
        'repositoryUrl':REPO+'/blob/main/'+encoded,
        'mediaType':'application/pdf',
        'bytes':size,
        'sha256':sha256_file(p),
        'largeFileWarning':size>=LARGE_WARNING
    }
    item.update({key:value for key,value in curated.items() if key!='title'})
    items.append(item)
items.sort(key=lambda x:x['path'].lower())
payload={
    'schemaVersion':4,
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
