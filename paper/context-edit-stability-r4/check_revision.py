"""Build and check the R4 delivery: preserved evidence, PDF, source ZIP, supplement, replay."""
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import zipfile

from pypdf import PdfReader

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
COMPILER = '/Applications/ChatGPT.app/Contents/Resources/tectonic/tectonic'
CACHE = '/Users/mac/Library/Application Support/ChatGPT/latex/tectonic'
WARNING = r'Overfull|Underfull|undefined|Missing character|LaTeX Warning'
PAGES = 10
# Appended on 2026-11-07 (SYNASC slide addendum); intentionally not preserved.
APPENDED = {'literature/schema-width-positioning-20261105.md'}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def compile_tex(root):
    env = dict(os.environ, TECTONIC_CACHE_DIR=CACHE)
    run = subprocess.run([COMPILER, '--only-cached', '--keep-logs', 'main.tex'], cwd=root,
                         env=env, capture_output=True, text=True)
    need(run.returncode == 0, 'Compilation failed: ' + run.stderr[-2000:])
    need(not re.search(WARNING, (root / 'main.log').read_text()), 'Compiler warning in log')
    return root / 'main.pdf'


def replay(root, *flags):
    run = subprocess.run(['python3', '-I', '-S', '-B', 'replay_e013.py', *flags], cwd=root,
                         capture_output=True, text=True)
    need(run.returncode == 0 and 'E013 replay passed.' in run.stdout,
         'Replay failed: ' + run.stdout[-1000:] + run.stderr[-2000:])
    return json.loads(run.stdout[:run.stdout.rindex('}') + 1])


def main():
    # 1. Earlier evidence and manuscripts are unchanged.
    baseline = json.loads((REPO / 'milestones/M33-preserved-artifacts.json').read_text())
    for rel, expected in baseline.items():
        need(digest(REPO / rel) == expected, f'Prior artifact changed: {rel}')
    r3 = json.loads((REPO / 'paper/context-edit-stability-r3/revision-verification.json').read_text())
    for rel, expected in r3['artifact_sha256'].items():
        need(digest(REPO / rel) == expected, f'R3 artifact changed: {rel}')
    m35 = json.loads((REPO / 'milestones/M35-verification.json').read_text())
    kept = {rel: h for rel, h in m35['artifact_sha256'].items() if rel not in APPENDED}
    for rel, expected in kept.items():
        need(digest(REPO / rel) == expected, f'M35 artifact changed: {rel}')

    e013 = REPO / 'experiments/E013-schema-width'
    summary = json.loads((e013 / 'results/summary.json').read_text())
    need(summary['all_predictions_match'] and summary['totals']['rejected_pairs_checked'] == 81893,
         'Unexpected E013 summary')

    # 2. Build the PDF from the source.
    source = HERE / 'tex/main.tex'
    with tempfile.TemporaryDirectory(prefix='r4-build-') as directory:
        root = Path(directory)
        shutil.copyfile(source, root / 'main.tex')
        shutil.copyfile(compile_tex(root), HERE / 'preview.pdf')
    pdf = PdfReader(HERE / 'preview.pdf')
    pages = [p.extract_text() for p in pdf.pages]
    text = '\n'.join(pages)
    need(len(pages) == PAGES and 'Trần Vũ Bảo Minh' in pages[0], 'Page count or author differs')
    for phrase in ('Exchange bound', 'Sharpness for every family', 'Laminar characterization',
                   '81,893', '39,379', 'Mureșan', 'Miclăuș'):
        need(phrase in text, f'Missing content: {phrase}')
    fonts = {}
    for page in pdf.pages:
        for value in page['/Resources'].get_object()['/Font'].get_object().values():
            font = value.get_object()
            for item in font.get('/DescendantFonts', [font]):
                d = item.get_object()['/FontDescriptor'].get_object()
                fonts[str(d['/FontName'])] = any(k in d for k in ('/FontFile', '/FontFile2', '/FontFile3'))
    need(fonts and all(fonts.values()), 'Unembedded font')

    # 3. Source ZIP compiles to the same text.
    with zipfile.ZipFile(HERE / 'source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('main.tex', source.read_bytes())
    with tempfile.TemporaryDirectory(prefix='r4-source-') as directory:
        root = Path(directory)
        with zipfile.ZipFile(HERE / 'source.zip') as archive:
            need(archive.namelist() == ['main.tex'] and archive.testzip() is None, 'Bad source ZIP')
            archive.extractall(root)
        need([p.extract_text() for p in PdfReader(compile_tex(root)).pages] == pages,
             'Extracted source text differs')

    report = dict(date='2026-11-07', pages=PAGES, tables=source.read_text().count(r'\begin{table}'),
                  references=source.read_text().count(r'\bibitem'), fonts=fonts,
                  all_fonts_embedded=True, author_exact_unicode=True,
                  prior_artifacts_unchanged=len(baseline), r3_artifacts_unchanged=len(r3['artifact_sha256']),
                  m35_artifacts_unchanged=len(kept), intentionally_appended=sorted(APPENDED),
                  compiler='Tectonic with bundled cache (--only-cached)', compiler_warnings=0,
                  extracted_source_compile_text_identical=True,
                  visual_pages_inspected='recorded separately in milestones/M36-R4.md',
                  independent_review=False, author_approval='not_given', license=None,
                  actual_submission='absent',
                  artifact_sha256={str(p.relative_to(REPO)): digest(p) for p in
                                   [source, HERE / 'preview.pdf', HERE / 'source.zip',
                                    HERE / 'replay_e013.py']})
    verification = HERE / 'revision-verification.json'
    verification.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')

    # 4. Supplement with manifest; extracted replay in both modes.
    members = {'main.tex': source, 'README.md': HERE / 'README.md',
               'replay_e013.py': HERE / 'replay_e013.py',
               'revision-verification.json': verification,
               'schema-width-positioning.md': REPO / 'literature/schema-width-positioning-20261105.md',
               'owner-guide-vi.md': REPO / 'to_human/M36-R4-progress-vi.md'}
    for name in ('protocol.md', 'verify_width.py', 'theory.md', 'analysis.md',
                 'proof-audit-20261107.md', 'reanalyze_e011.py', 'results/summary.json',
                 'results/cases.jsonl.gz', 'results/e011-analytical-reanalysis.json'):
        members['E013/' + name] = e013 / name
    manifest = {name: digest(path) for name, path in members.items()}
    with zipfile.ZipFile(HERE / 'supplement.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, path in members.items():
            archive.writestr(name, path.read_bytes())
        archive.writestr('manifest.json', json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    with tempfile.TemporaryDirectory(prefix='r4-supplement-') as directory:
        root = Path(directory)
        with zipfile.ZipFile(HERE / 'supplement.zip') as archive:
            need(set(archive.namelist()) == set(members) | {'manifest.json'}
                 and archive.testzip() is None, 'Bad supplement ZIP')
            archive.extractall(root)
        for name, expected in manifest.items():
            need(digest(root / name) == expected, f'Extracted hash differs: {name}')
        records = replay(root)
        enumerated = replay(root, '--reenumerate')
        need(enumerated['reenumerated'], 'Re-enumeration not performed')
    supplement = dict(date='2026-11-07', members=len(members) + 1,
                      sha256=digest(HERE / 'supplement.zip'),
                      all_member_hashes_and_CRC_verified=True,
                      extracted_record_replay=records, extracted_reenumeration=enumerated,
                      no_git_or_third_party_imports_required=True)
    (HERE / 'supplement-verification.json').write_text(json.dumps(supplement, indent=2, sort_keys=True) + '\n')
    print(json.dumps(dict(pages=PAGES, fonts_embedded=len(fonts),
                          prior_artifacts_unchanged=len(baseline), supplement=supplement), indent=2))


if __name__ == '__main__':
    main()
