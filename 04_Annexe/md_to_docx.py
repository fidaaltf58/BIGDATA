"""Convertit Annexe_Installation.md en .docx (python md_to_docx.py)."""
import re
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor

HERE = Path(__file__).resolve().parent
NAVY = RGBColor(0x0B, 0x3C, 0x49)
doc = Document()
st = doc.styles["Normal"]
st.font.name, st.font.size = "Calibri", Pt(11)
for lvl, size in ((1, 20), (2, 15), (3, 12.5)):
    h = doc.styles[f"Heading {lvl}"]
    h.font.name, h.font.size, h.font.color.rgb = "Cambria", Pt(size), NAVY


def inline(p, txt):
    for part in re.split(r"(`[^`]+`|\*\*[^*]+\*\*)", txt):
        if part.startswith("`"):
            r = p.add_run(part[1:-1]); r.font.name = "Courier New"; r.font.size = Pt(10)
        elif part.startswith("**"):
            p.add_run(part[2:-2]).bold = True
        elif part:
            p.add_run(part)


lines = (HERE / "Annexe_Installation.md").read_text(encoding="utf-8").splitlines()
i = 0
while i < len(lines):
    ln = lines[i]
    if ln.startswith("```"):
        i += 1
        code = []
        while not lines[i].startswith("```"):
            code.append(lines[i]); i += 1
        p = doc.add_paragraph()
        r = p.add_run("\n".join(code)); r.font.name = "Courier New"; r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(0x1E, 0x29, 0x33)
        p.paragraph_format.left_indent = Pt(14)
    elif ln.startswith("|"):
        rows = []
        while i < len(lines) and lines[i].startswith("|"):
            if not re.match(r"^\|[-| ]+\|$", lines[i]):
                rows.append([c.strip() for c in lines[i].strip("|").split("|")])
            i += 1
        t = doc.add_table(rows=len(rows), cols=len(rows[0])); t.style = "Light Grid Accent 1"
        for r_, row in enumerate(rows):
            for c_, v in enumerate(row):
                cell = t.cell(r_, c_); cell.text = ""
                inline(cell.paragraphs[0], v)
                for run in cell.paragraphs[0].runs:
                    run.font.size = Pt(9.5); run.bold = run.bold or r_ == 0
        continue
    elif ln.startswith("# "):
        h = doc.add_heading(ln[2:], 0); h.alignment = WD_ALIGN_PARAGRAPH.LEFT
    elif ln.startswith("## "):
        doc.add_heading(ln[3:], 1)
    elif ln.startswith("### "):
        doc.add_heading(ln[4:], 2)
    elif re.match(r"^- (\[ \] )?", ln):
        inline(doc.add_paragraph(style="List Bullet"), re.sub(r"^- (\[ \] )?", "", ln))
    elif re.match(r"^\d+\. ", ln):
        inline(doc.add_paragraph(style="List Number"), re.sub(r"^\d+\. ", "", ln))
    elif ln.strip():
        inline(doc.add_paragraph(), ln)
    i += 1

doc.save(HERE / "Annexe_Installation.docx")
print("OK")
