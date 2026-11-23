"""Build the 2-page beginner install guide PDF (Windows PC + Fir) for NDAC team members.

    python make_install_guide.py [OUTPUT.pdf]

Default output: ndac-foundation_install_guide.pdf next to this script. Needs reportlab
(`pip install reportlab`, ideally in a venv) and the Windows fonts Segoe UI and Consolas.
Edit the text in the story section below, rebuild, and check both pages before sharing.
"""
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, Preformatted,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("ndac-foundation_install_guide.pdf")
URL = "https://github.com/acreagelab/ndac-foundation"

F = "C:/Windows/Fonts/"
pdfmetrics.registerFont(TTFont("Body", F + "segoeui.ttf"))
pdfmetrics.registerFont(TTFont("Body-Bold", F + "segoeuib.ttf"))
pdfmetrics.registerFont(TTFont("Body-Italic", F + "segoeuii.ttf"))
pdfmetrics.registerFont(TTFont("Mono", F + "consola.ttf"))
pdfmetrics.registerFont(TTFont("Body-BI", F + "segoeuiz.ttf"))
pdfmetrics.registerFontFamily("Body", normal="Body", bold="Body-Bold", italic="Body-Italic",
                              boldItalic="Body-BI")

GREEN = colors.HexColor("#2a5f3c")
LIGHT_GREEN = colors.HexColor("#e8f1eb")
CODE_BG = colors.HexColor("#f3f4f6")
CODE_EDGE = colors.HexColor("#d0d4da")
AMBER_BG = colors.HexColor("#fff6e0")
AMBER_EDGE = colors.HexColor("#e0b84a")
GREY = colors.HexColor("#555b63")

body = ParagraphStyle("body", fontName="Body", fontSize=10, leading=14, alignment=TA_LEFT)
small = ParagraphStyle("small", parent=body, fontSize=8.5, leading=11.5, textColor=GREY)
h1 = ParagraphStyle("h1", parent=body, fontName="Body-Bold", fontSize=16, leading=20,
                    textColor=GREEN, spaceBefore=6, spaceAfter=6)
h2 = ParagraphStyle("h2", parent=body, fontName="Body-Bold", fontSize=11.5, leading=15,
                    spaceBefore=10, spaceAfter=3)
cell = ParagraphStyle("cell", parent=body, fontSize=9, leading=12)
cell_b = ParagraphStyle("cellb", parent=cell, fontName="Body-Bold")
code_style = ParagraphStyle("code", fontName="Mono", fontSize=8.3, leading=11)

W = letter[0] - 2 * 0.8 * inch  # text width


def P(text, style=body):
    return Paragraph(text, style)


def code(text):
    t = Table([[Preformatted(text.strip("\n"), code_style)]], colWidths=[W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CODE_BG),
        ("BOX", (0, 0), (-1, -1), 0.6, CODE_EDGE),
        ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def box(label, text, bg, edge):
    t = Table([[P(f"<b>{label}</b>&nbsp;&nbsp;{text}", cell)]], colWidths=[W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg), ("LINEBEFORE", (0, 0), (0, -1), 3, edge),
        ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def check(text):
    return box("Check:", text, LIGHT_GREEN, GREEN)


def tip(text):
    return box("Tip:", text, AMBER_BG, AMBER_EDGE)


def step(num, title, *flow):
    head = Table([[P(f"<font color='white'><b>{num}</b></font>", ParagraphStyle(
        "n", parent=body, alignment=1, fontSize=9.5)), P(f"<b>{title}</b>", h2)]],
        colWidths=[0.32 * inch, W - 0.32 * inch])
    head.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), GREEN), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (0, 0), 0), ("RIGHTPADDING", (0, 0), (0, 0), 0),
        ("LEFTPADDING", (1, 0), (1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 1), ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    items = [Spacer(1, 8), head, Spacer(1, 4)]
    for f in flow:
        items += [f, Spacer(1, 4)]
    return KeepTogether(items)


def bullets(*lines):
    return [P(f"&bull;&nbsp; {l}", ParagraphStyle("b", parent=body, leftIndent=12,
                                                  firstLineIndent=-9, spaceAfter=2))
            for l in lines]


def grid(rows, widths, header=True):
    data = [[P(c, cell_b if (header and i == 0) else cell) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    style = [
        ("GRID", (0, 0), (-1, -1), 0.5, CODE_EDGE), ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    if header:
        style.append(("BACKGROUND", (0, 0), (-1, 0), LIGHT_GREEN))
    t.setStyle(TableStyle(style))
    return t


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Body", 8)
    canvas.setFillColor(GREY)
    canvas.drawString(0.8 * inch, 0.5 * inch, f"ndac-foundation install guide  ·  {URL}")
    canvas.drawRightString(letter[0] - 0.8 * inch, 0.5 * inch, f"Page {doc.page}")
    canvas.restoreState()


def first_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(GREEN)
    canvas.rect(0, letter[1] - 1.35 * inch, letter[0], 1.35 * inch, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Body-Bold", 21)
    canvas.drawString(0.8 * inch, letter[1] - 0.72 * inch, "Getting started with ndac-foundation")
    canvas.setFont("Body", 11)
    canvas.drawString(0.8 * inch, letter[1] - 1.02 * inch,
                      "Install guide for NDAC team members  ·  your Windows PC and the Fir cluster")
    canvas.restoreState()
    header_footer(canvas, doc)


s = []
s += [Spacer(1, 0.75 * inch)]
s += [P("Install once on your PC and once on Fir. Then just ask Claude, e.g. "
        "<i>\"Start a new project called wetland_mb\"</i>. No GitHub account needed.")]

s += [P("Before you start", h2)]
s += bullets("<b>VS Code</b> (code.visualstudio.com), <b>Git</b> (git-scm.com) and <b>Python</b> "
             "(python.org; tick <b>\"Add python.exe to PATH\"</b>)",
             "In VS Code: <b>Extensions</b> &rarr; install <b>Claude Code</b> &rarr; sign in with "
             "your <b>USask account</b>",
             "For Fir: an Alliance account in group <b>def-kanj241</b>, with Duo on your phone")
s += [Spacer(1, 4), tip("Copy the grey text, paste it into the VS Code terminal "
                        "(<b>Terminal &rarr; New Terminal</b>) and press Enter.")]

s += [P("1 · On your Windows PC", h1)]
s += [step("1", "Paste these four lines (nothing to edit)",
           code(r"""
mkdir C:\$env:USERNAME\Projects
git clone https://github.com/acreagelab/ndac-foundation C:\$env:USERNAME\Projects\ndac-foundation
powershell -ExecutionPolicy Bypass -File C:\$env:USERNAME\Projects\ndac-foundation\install.ps1
setx PROJECTS_ROOT C:\$env:USERNAME\Projects
"""))]
s += [step("2", "Check",
           check("Close and reopen VS Code, click the <b>Claude</b> icon and type <b>/</b>. "
                 "You should see <b>init-data-project</b>."))]

s += [P("2 · On Fir", h1)]
s += [step("1", "Connect VS Code to Fir (first time only)",
           *bullets("<b>Extensions</b> &rarr; install <b>Remote - SSH</b>.",
                    "<b>Settings</b> &rarr; search <b>useLocalServer</b> &rarr; turn it <b>off</b>.",
                    "<b>Ctrl+Shift+P</b> &rarr; <b>Remote-SSH: Connect to Host</b> &rarr; "
                    "<font name='Mono'>username@fir.alliancecan.ca</font> &rarr; password &rarr; "
                    "type <b>1</b> &rarr; approve <b>Duo</b>.",
                    "In the Fir window: <b>Extensions</b> &rarr; <b>Claude Code</b> &rarr; "
                    "<b>Install in SSH</b> &rarr; sign in."))]
s += [step("2", "Paste this block in a Fir terminal (nothing to edit)",
           code("""
cd ~
git clone https://github.com/acreagelab/ndac-foundation
bash ndac-foundation/install.sh
echo 'export PROJECTS_ROOT=/project/def-kanj241/'$USER'/Projects' >> ~/.bashrc
source ~/.bashrc && mkdir -p $PROJECTS_ROOT
sh ~/.claude/skills/fir-resources/fir_share.sh
sh ~/.claude/skills/fir-resources/fir_share.sh --check
"""))]
s += [step("3", "Check",
           check("The last line says <b>All as intended.</b> Then <b>Ctrl+Shift+P</b> &rarr; "
                 "<b>Developer: Reload Window</b>, and type <b>/</b> in Claude."))]

s += [P("Who can see your projects on Fir", h1)]
s += [grid([
    ["Who", "Can"],
    ["You", "Do everything"],
    ["Dr. Kwabena Nketia (PI) and Thuan Ha (data manager)", "Read and edit everything"],
    ["Other team members", "<b>Read only</b> (can't edit or delete)"],
], [3.0 * inch, W - 3.0 * inch])]
s += [Spacer(1, 6), tip("Restricted data (field-level yield, soil, producer or land data)? "
                        "<b>Before</b> copying it in, tell Claude <i>\"this project will have "
                        "restricted data\"</i>. Only you, the PI and the data manager will see it.")]

s += [P("Using it", h1)]
s += [grid([
    ["Ask Claude", "You get"],
    ["<i>Start a new project called wetland_mb</i>", "A ready project folder"],
    ["<i>/export-check this figure</i>", "A safety check before sharing anything"],
    ["On Fir: <i>Run my analysis on the cluster</i>", "Claude plans and submits the job"],
], [3.0 * inch, W - 3.0 * inch])]

s += [P("Updating", h1)]
s += [P("<b>PC:</b>", cell), code(r"""
git -C C:\$env:USERNAME\Projects\ndac-foundation pull
powershell -ExecutionPolicy Bypass -File C:\$env:USERNAME\Projects\ndac-foundation\install.ps1
"""), Spacer(1, 4), P("<b>Fir:</b>", cell),
      code("git -C ~/ndac-foundation pull && bash ~/ndac-foundation/install.sh")]

s += [P("Stuck?", h1)]
s += [grid([
    ["You see", "Do this"],
    ["<i>'git' / 'python' is not recognized</i>", "Install it, then reopen VS Code"],
    ["<i>already exists</i>", "Already done; carry on (or use Updating)"],
    ["<b>/</b> doesn't show init-data-project", "Reload VS Code"],
    ["Fir keeps asking for Duo or hangs", "Check <b>useLocalServer</b> is off, reconnect"],
], [3.0 * inch, W - 3.0 * inch])]
s += [Spacer(1, 8), box("Help:", "contact <b>Thuan Ha</b> (NDAC data manager) with a "
                        "screenshot of the error.", LIGHT_GREEN, GREEN)]

doc = SimpleDocTemplate(str(OUT), pagesize=letter, leftMargin=0.8 * inch, rightMargin=0.8 * inch,
                        topMargin=0.75 * inch, bottomMargin=0.8 * inch,
                        title="Getting started with ndac-foundation",
                        author="Thuan Ha, NDAC", subject="Install guide: Windows PC and Fir")
doc.build(s, onFirstPage=first_page, onLaterPages=header_footer)
print(OUT)
