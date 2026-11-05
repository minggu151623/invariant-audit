"""Check R3 delivery, preserved evidence, extracted source and portable replay."""
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


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    source = HERE / 'tex/main.tex'
    text = source.read_text()
    old = (REPO / 'paper/context-edit-stability-r2/tex/main.tex').read_text()
    baseline = json.loads((REPO / 'milestones/M33-preserved-artifacts.json').read_text())
    for rel, expected in baseline.items():
        need(digest(REPO / rel) == expected, f'Prior artifact changed: {rel}')
    pattern = r'\\begin\{(?:theorem|lemma|corollary|proposition)\}.*?\\end\{(?:proof|corollary)\}'
    preserved = re.findall(pattern, old, re.S)
    need(len(preserved) == 5 and all(block in text for block in preserved),
         'Previous structural statement/proof changed')
    begin, end = r'\section{Finite validation and constructed computation}', r'\section{Related work and scope}'
    need(old[old.index(begin):old.index(end)] == text[text.index(begin):text.index(end)],
         'Original empirical results changed')
    e012 = REPO / 'experiments/E012-acceptance-complexity'
    results = json.loads((e012 / 'results.json').read_text())
    need(results['implementation_sha256'] == digest(e012 / 'verify_reduction.py')
         and results['protocol_sha256'] == digest(e012 / 'protocol.md'), 'E012 artifact drift')
    need(results['all_predictions_match'] and results['case_count'] == 111,
         'Wrong finite outcome')
    built = REPO / 'tmp/pdfs/M33-build/main.pdf'
    warning = r'Overfull|Underfull|undefined|Missing character|LaTeX Warning'
    need(not re.search(warning, (built.parent / 'main.log').read_text()), 'Compiler warning')
    shutil.copyfile(built, HERE / 'preview.pdf')
    pdf = PdfReader(HERE / 'preview.pdf')
    pages = [p.extract_text() for p in pdf.pages]
    need(len(pages) == 10 and 'Trần Vũ Bảo Minh' in pages[0], 'PDF pages or author differ')
    need('Theorem 3' in '\n'.join(pages) and '147,523' in '\n'.join(pages), 'New content missing')
    fonts = {}
    for page in pdf.pages:
        for value in page['/Resources'].get_object()['/Font'].get_object().values():
            font = value.get_object()
            for item in font.get('/DescendantFonts', [font]):
                descriptor = item.get_object().get('/FontDescriptor')
                need(descriptor is not None, 'Missing font descriptor')
                d = descriptor.get_object()
                fonts[str(d['/FontName'])] = any(k in d for k in ('/FontFile', '/FontFile2', '/FontFile3'))
    need(fonts and all(fonts.values()), 'Unembedded font')
    with zipfile.ZipFile(HERE / 'source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('main.tex', source.read_bytes())
    with tempfile.TemporaryDirectory(prefix='r3-source-') as directory:
        root = Path(directory)
        with zipfile.ZipFile(HERE / 'source.zip') as archive:
            need(archive.namelist() == ['main.tex'] and archive.testzip() is None, 'Bad source ZIP')
            archive.extractall(root)
        env = dict(os.environ, TECTONIC_CACHE_DIR='/Users/mac/Library/Application Support/ChatGPT/latex/tectonic')
        run = subprocess.run([COMPILER, '--only-cached', '--keep-logs', 'main.tex'], cwd=root,
                             env=env, capture_output=True, text=True)
        need(run.returncode == 0, 'Extracted source compilation failed: '+run.stderr[-2000:])
        need(not re.search(warning, (root / 'main.log').read_text()), 'Extracted compile warning')
        need([p.extract_text() for p in PdfReader(root / 'main.pdf').pages] == pages,
             'Extracted source text differs')
    report = dict(date='2026-11-05', pages=10, tables=text.count(r'\begin{table}'),
                  references=text.count(r'\bibitem'), fonts=fonts, all_fonts_embedded=True,
                  author_exact_unicode=True, prior_artifacts_unchanged=len(baseline),
                  previous_structural_blocks_unchanged=len(preserved),
                  original_E008_E011_results_text_unchanged=True,
                  E012_cases=111, E012_radii=222, E012_destinations=147523,
                  compiler='Tectonic 0.17.0 with bundled cache', compiler_warnings=0,
                  extracted_source_compile_text_identical=True,
                  visual_pages_inspected=list(range(1, 11)),
                  source_reproduction_this_revision=False, independent_review=False,
                  author_approval='not_given', license=None, actual_submission='absent',
                  artifact_sha256={str(p.relative_to(REPO)): digest(p) for p in
                                   [source, HERE / 'preview.pdf', HERE / 'source.zip',
                                    e012 / 'verify_reduction.py', e012 / 'results.json']})
    verification = HERE / 'revision-verification.json'
    verification.write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    members = {'main.tex': source, 'README.md': HERE / 'README.md',
               'replay_e012.py': HERE / 'replay_e012.py',
               'revision-verification.json': verification,
               'complexity-positioning.md': REPO / 'literature/acceptance-complexity-positioning-20261105.md',
               'owner-guide-vi.md': REPO / 'to_human/M33-theory-progress-vi.md'}
    for name in ('protocol.md', 'verify_reduction.py', 'results.json', 'analysis.md', 'theory.md'):
        members['E012/'+name] = e012 / name
    manifest = {name: digest(path) for name, path in members.items()}
    with zipfile.ZipFile(HERE / 'supplement.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, path in members.items():
            archive.writestr(name, path.read_bytes())
        archive.writestr('manifest.json', json.dumps(manifest, indent=2, sort_keys=True)+'\n')
    with tempfile.TemporaryDirectory(prefix='r3-supplement-') as directory:
        root = Path(directory)
        with zipfile.ZipFile(HERE / 'supplement.zip') as archive:
            need(set(archive.namelist()) == set(members) | {'manifest.json'}
                 and archive.testzip() is None, 'Bad supplement ZIP')
            archive.extractall(root)
        for name, expected in manifest.items():
            need(digest(root / name) == expected, 'Extracted supplement hash differs')
        run = subprocess.run(['python3', '-I', '-S', '-B', 'replay_e012.py'], cwd=root,
                             capture_output=True, text=True)
        need(run.returncode == 0, 'Portable E012 replay failed: '+run.stderr[-2000:])
        replay = json.loads(run.stdout)
        need(replay['exact_replay'], 'Portable replay not exact')
    supplement = dict(date='2026-11-05', members=len(members)+1,
                      sha256=digest(HERE / 'supplement.zip'),
                      all_member_hashes_and_CRC_verified=True,
                      extracted_portable_replay=replay, no_git_or_third_party_imports_required=True)
    (HERE / 'supplement-verification.json').write_text(json.dumps(supplement, indent=2, sort_keys=True)+'\n')
    print(json.dumps(dict(pages=10, fonts_embedded=len(fonts),
                         prior_artifacts_unchanged=len(baseline), supplement=supplement), indent=2))


if __name__ == '__main__':
    main()
