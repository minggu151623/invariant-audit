"""Derive LaTeX from the authoritative Markdown; optionally compile a preview."""
import argparse
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "paper/arxiv"


def prepare():
    markdown = (ROOT / "paper/main.md").read_text()
    body = "## Abstract" + markdown.split("## Abstract", 1)[1]
    with tempfile.TemporaryDirectory(prefix="invariantaudit-pandoc-") as temporary:
        source = Path(temporary) / "body.md"
        source.write_text(body)
        tex = subprocess.check_output([
            "pandoc", str(source), "--from=markdown", "--to=latex",
            "--top-level-division=section", "--shift-heading-level-by=-1"], text=True)
    tex = tex.replace("arxiv/images/brier-decomposition.pdf", "images/brier-decomposition.pdf")
    tex = tex.replace(r"\includegraphics{images/brier-decomposition.pdf}",
                      r"\includegraphics[width=\linewidth]{images/brier-decomposition.pdf}")
    tex = re.sub(r"\\texttt\{([^{}]{50,})\}", lambda match: r"\path|" +
                 match.group(1).replace(r"\_", "_").replace(r"\ ", " ") + "|", tex)
    def keep_table_together(match):
        table = match.group(2).replace(r"\begin{longtable}[]", r"\begin{tabular}")
        table = table.replace(r"\end{longtable}", r"\end{tabular}").replace(r"\endhead", "")
        return ("\\noindent\\begin{minipage}{\\linewidth}\n\\noindent " + match.group(1) +
                "\n\\par\\medskip\\centering\n" + table + "\n\\end{minipage}\n")
    tex = re.sub(r"(Table [0-9]+\.[^\n]*(?:\n(?!\n)[^\n]*)*)\n\n(\\begin\{longtable\}.*?\\end\{longtable\})",
                 keep_table_together, tex, flags=re.DOTALL)
    (PROJECT / "body.tex").write_text(tex)
    main = (PROJECT / "main.tex").read_text()
    if "secnumdepth" not in main:
        main = main.replace(r"\begin{document}", "\\setcounter{secnumdepth}{0}\n\\begin{document}")
    (PROJECT / "main.tex").write_text(main)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", type=Path)
    options = parser.parse_args()
    prepare()
    if options.engine:
        out = ROOT / "paper/build"
        out.mkdir(exist_ok=True)
        subprocess.run([str(options.engine.resolve()), "main.tex", "--keep-logs", "--outdir", str(out)],
                       cwd=PROJECT, check=True)
        shutil.copyfile(out / "main.pdf", ROOT / "paper/arxiv-preview.pdf")
