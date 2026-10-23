"""Derive review-only arXiv fields from the current structural manuscript."""
from hashlib import sha256
import json
from pathlib import Path
import re
import unicodedata

ROOT = Path(__file__).resolve().parent
tex = (ROOT / 'main.tex').read_text()
title = re.search(r'\\title\{(.*?)\}\s*\\author', tex, re.S).group(1)
title = re.sub(r'\s+', ' ', title.replace('\\\\', ' ')).strip()
abstract = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', tex, re.S).group(1)
abstract = re.sub(r'\s+', ' ', abstract).strip()
if not title.isascii() or not abstract.isascii() or len(abstract) > 1920:
    raise ValueError('Non-ASCII or overlength form field')
render = json.loads((ROOT / 'render-verification.json').read_text())
repo = ROOT.parents[1]
for path, digest in render['artifact_sha256'].items():
    if sha256((repo / path).read_bytes()).hexdigest() != digest:
        raise ValueError(f'M30 artifact drift: {path}')
author = 'Trần Vũ Bảo Minh'
if author not in tex or 'Independent Researcher' not in tex:
    raise ValueError('User-supplied identity missing')
form_author = unicodedata.normalize('NFKD', author).encode('ascii', 'ignore').decode()
fields = dict(status='review_only_not_submitted', title=title, abstract=abstract,
              abstract_characters=len(abstract), authors_display=[author],
              authors_form_ascii_proposal=[form_author], authors_form_proposal_approved=False,
              authors_form_rendering_verified=False, affiliation='Independent Researcher',
              category_candidate='cs.DB', category_basis='Fixed FD detectors, database context edits and source-table analysis; technical recommendation, not moderator confirmation.',
              category_confirmed=False, cross_lists=[], comments='7 pages, 2 tables, no figures',
              processor='xelatex', tex_live_candidate='2025', top_level_source='main.tex',
              source_upload='context-edit-stability-source.zip', license=None,
              doi=None, journal_ref=None, report_no=None, owner_content_approval='not_given',
              actual_submission='absent', arxiv_identifier=None,
              artifact_sha256=render['artifact_sha256'],
              guidance_checked='2026-10-23',
              official_sources=['https://info.arxiv.org/help/prep.html',
                                'https://info.arxiv.org/help/faq/texlive.html',
                                'https://info.arxiv.org/help/faq/font-info-tl2025.html',
                                'https://arxiv.org/category_taxonomy'])
(ROOT / 'submission-fields-draft.json').write_text(json.dumps(fields, ensure_ascii=False, indent=2, sort_keys=True)+'\n')
(ROOT / 'abstract.txt').write_text(abstract+'\n')
print(json.dumps(dict(title=title, abstract_characters=len(abstract), authors_form_ascii_proposal=[form_author],
                      category_candidate='cs.DB', license=None, submitted=False), ensure_ascii=False))
