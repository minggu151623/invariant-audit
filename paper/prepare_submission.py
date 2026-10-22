"""Prepare local review fields without choosing a license or submitting anything."""
from hashlib import sha256
import json
from pathlib import Path
import unicodedata

ROOT = Path(__file__).resolve().parent
metadata = json.loads((ROOT / 'submission-metadata.json').read_text())
render = json.loads((ROOT / 'render-verification.json').read_text())
markdown = (ROOT / 'main.md').read_text()
abstract = markdown.split('## Abstract\n\n', 1)[1].split('\n\n## ', 1)[0]
title = markdown.splitlines()[0].removeprefix('# ')
if title != metadata['title'] or not abstract.isascii() or len(abstract) > 1920:
    raise ValueError('Manuscript/title/abstract metadata requires review')
for filename, field in [('arxiv-preview.pdf', 'preview_pdf_sha256'),
                        ('arxiv-source-draft.zip', 'source_zip_sha256')]:
    if sha256((ROOT / filename).read_bytes()).hexdigest() != render[field]:
        raise ValueError(f'Render verification does not match {filename}')
ascii_authors = [unicodedata.normalize('NFKD', author).encode('ascii', 'ignore').decode()
                 for author in metadata['authors']]
fields = {
    'status': 'local_draft_for_author_review_not_submitted',
    'title': title, 'authors_display': metadata['authors'],
    'affiliation': metadata['affiliation'],
    'authors_ascii_fallback_for_live_form_review': ascii_authors,
    'ascii_fallback_approved': False,
    'abstract': abstract, 'abstract_characters': len(abstract),
    'comments': f"{render['pdf_pages']} pages, {render['figure_count']} figures",
    'category_candidate': metadata['category_candidate'],
    'category_confirmed': metadata['category_confirmed'],
    'license': metadata['license'], 'journal_ref': None, 'doi': None, 'report_no': None,
    'source_upload': 'arxiv-source-draft.zip', 'top_level_source': 'main.tex',
    'processor': 'xelatex', 'processor_basis': 'fontspec and Unicode author name',
    'owner_review': metadata['owner_review'],
}
readiness = {
    'date': '2026-10-23', 'status': 'not_submission_ready', 'goal_complete': False,
    'previous_goal_turn': 'progress_M21_named_manuscript_and_M22_portable_evidence',
    'current_artifacts': {name: sha256((ROOT / name).read_bytes()).hexdigest()
                          for name in ('main.md', 'arxiv-preview.pdf', 'arxiv-source-draft.zip')},
    'requirements': {
        'author_name_and_affiliation': 'user_supplied_in_manuscript',
        'local_source_compile_and_visual_review': 'pass_Tectonic_only',
        'frozen_evidence_portable_verification': 'pass_M22',
        'owner_substantive_review': metadata['owner_review'],
        'independent_scientific_review': 'absent_project_quality_limitation_not_claimed_arxiv_requirement',
        'archival_interest': 'unresolved_no_moderation_outcome',
        'arxiv_account': 'absent_per_user_reply',
        'endorsement': 'unknown_requires_actual_account_submission_flow',
        'category': 'candidate_only_not_confirmed',
        'license': 'unselected',
        'metadata_live_form_rendering': 'not_tested',
        'arxiv_server_compile_and_pdf_review': 'not_run',
        'remove_working_draft_markers_after_approval': 'pending',
        'actual_submission': 'not_done',
        'public_arxiv_record': 'absent',
    },
    'official_guidance_checked': [
        'https://info.arxiv.org/help/submit/index.html',
        'https://info.arxiv.org/help/prep.html',
        'https://info.arxiv.org/help/faq/texlive.html',
        'https://info.arxiv.org/help/faq/font-info-tl2025.html',
        'https://info.arxiv.org/help/endorsement.html',
        'https://info.arxiv.org/help/license/index.html',
        'https://info.arxiv.org/help/moderation/index.html',
        'https://arxiv.org/category_taxonomy',
    ],
}
(ROOT / 'abstract.txt').write_text(abstract+'\n', encoding='ascii')
for filename, value in [('submission-fields-draft.json', fields),
                        ('submission-readiness.json', readiness)]:
    (ROOT / filename).write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2)+'\n')
print(json.dumps({'status': readiness['status'], 'abstract_characters': len(abstract),
                  'processor': fields['processor'], 'owner_review': fields['owner_review']}))
