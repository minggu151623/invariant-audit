"""Create the minimal author-review source archive from the current LaTeX project."""
from hashlib import sha256
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'paper/arxiv'
MEMBERS = ('main.tex', 'body.tex', 'images/brier-decomposition.pdf')
DESTINATION = ROOT / 'paper/arxiv-source-draft.zip'
with zipfile.ZipFile(DESTINATION, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
    for member in MEMBERS:
        info = zipfile.ZipInfo(member, date_time=(2026, 10, 22, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        archive.writestr(info, (PROJECT / member).read_bytes())
with zipfile.ZipFile(DESTINATION) as archive:
    assert archive.namelist() == list(MEMBERS)
    assert archive.testzip() is None
    for member in MEMBERS:
        assert archive.read(member) == (PROJECT / member).read_bytes()
print(json.dumps({'path':str(DESTINATION), 'sha256':sha256(DESTINATION.read_bytes()).hexdigest(),
                  'members':list(MEMBERS)}, indent=2))
