"""Verify the local R2 document and unchanged prior scientific artifacts."""
from hashlib import sha256
import json
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
    old = (REPO / 'paper/context-edit-stability/main.tex').read_text()
    baseline = json.loads((REPO / 'milestones/M32-preserved-artifacts.json').read_text())
    for rel, expected in baseline.items():
        need(digest(REPO / rel) == expected, f'Prior artifact changed: {rel}')
    pattern = r'\\begin\{(?:theorem|lemma|corollary)\}.*?\\end\{(?:proof|corollary)\}'
    preserved = re.findall(pattern, old, re.S)
    need(len(preserved) == 4, 'Unexpected number of original structural blocks')
    need(all(block in text for block in preserved), 'Changed original structural statement/proof')
    begin, end = r'\section{Finite validation and constructed computation}', r'\section{Related work and scope}'
    need(old[old.index(begin):old.index(end)] == text[text.index(begin):text.index(end)],
         'Changed original empirical results')
    checks = json.loads((HERE / 'example-checks.json').read_text())
    need(checks['implementation_sha256'] == digest(HERE / 'verify_examples.py'), 'Example code drift')
    need(checks['all_predictions_match'] and checks['case_count'] == 8
         and checks['destinations_enumerated'] == 285032, 'Wrong example denominator/outcome')
    built = REPO / 'tmp/pdfs/M32-build/main.pdf'
    log = (built.parent / 'main.log').read_text()
    need(not re.search(r'Overfull|Underfull|undefined|Missing character|LaTeX Warning', log), 'Compiler warning')
    shutil.copyfile(built, HERE / 'preview.pdf')
    pdf = PdfReader(HERE / 'preview.pdf')
    need(len(pdf.pages) == 9, 'Unexpected page count')
    pages = [p.extract_text() for p in pdf.pages]
    need('Trần Vũ Bảo Minh' in pages[0], 'Author Unicode mismatch')
    fonts = {}
    for p in pdf.pages:
        resources = p['/Resources'].get_object()
        for f in resources.get('/Font', {}).get_object().values():
            font = f.get_object()
            for item in font.get('/DescendantFonts', [font]):
                item = item.get_object()
                descriptor = item.get('/FontDescriptor')
                need(descriptor is not None, 'Missing font descriptor')
                d = descriptor.get_object()
                fonts[str(d['/FontName'])] = any(k in d for k in ('/FontFile', '/FontFile2', '/FontFile3'))
    need(fonts and all(fonts.values()), 'Unembedded font')
    with zipfile.ZipFile(HERE / 'source.zip', 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('main.tex', source.read_bytes())
    with tempfile.TemporaryDirectory(prefix='r2-source-') as directory:
        root = Path(directory)
        with zipfile.ZipFile(HERE / 'source.zip') as archive:
            need(archive.namelist() == ['main.tex'] and archive.testzip() is None, 'Bad source archive')
            archive.extractall(root)
        import os
        env = dict(os.environ, TECTONIC_CACHE_DIR='/Users/mac/Library/Application Support/ChatGPT/latex/tectonic')
        run = subprocess.run([COMPILER, '--only-cached', '--keep-logs', 'main.tex'], cwd=root,
                             env=env, capture_output=True, text=True)
        need(run.returncode == 0, 'Extracted source compilation failed: '+run.stderr[-2000:])
        need(not re.search(r'Overfull|Underfull|undefined|Missing character|LaTeX Warning',
                           (root / 'main.log').read_text()), 'Extracted source warning')
        other = PdfReader(root / 'main.pdf')
        need([p.extract_text() for p in other.pages] == pages, 'Extracted source text differs')
    report = dict(date='2026-11-05', pages=len(pdf.pages), tables=text.count(r'\begin{table}'),
                  references=text.count(r'\bibitem'), fonts=fonts, all_fonts_embedded=True,
                  author_exact_unicode=True, prior_artifacts_unchanged=len(baseline),
                  original_structural_blocks_unchanged=len(preserved),
                  original_E008_E011_results_text_unchanged=True,
                  example_checks=8, enumerated_destinations=285032,
                  compiler='Tectonic 0.17.0 with bundled cache', compiler_warnings=0,
                  desktop_compiler_success=True, extracted_source_compile_text_identical=True,
                  visual_pages_inspected=list(range(1, 10)),
                  source_reproduction_this_revision=False, independent_review=False,
                  author_approval='not_given', license=None, actual_submission='absent',
                  artifact_sha256={str(p.relative_to(REPO)): digest(p) for p in
                                   [source, HERE / 'preview.pdf', HERE / 'source.zip',
                                    HERE / 'verify_examples.py', HERE / 'example-checks.json']})
    (HERE / 'revision-verification.json').write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    print(json.dumps({k: v for k, v in report.items() if k not in ('artifact_sha256', 'fonts')}, indent=2))


if __name__ == '__main__':
    main()
