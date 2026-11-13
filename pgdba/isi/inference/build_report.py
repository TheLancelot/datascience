# -*- coding: utf-8 -*-
import os, matplotlib
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, KeepTogether, HRFlowable, NextPageTemplate
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ---------------------------------------------------------------------------
# Register Unicode fonts (needed for the Rupee sign and clean typography)
# ---------------------------------------------------------------------------
FONT_DIR = os.path.join(os.path.dirname(matplotlib.__file__), "mpl-data", "fonts", "ttf")
pdfmetrics.registerFont(TTFont("DejaVuSans", os.path.join(FONT_DIR, "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("DejaVuSans-Oblique", os.path.join(FONT_DIR, "DejaVuSans-Oblique.ttf")))

F_REG, F_BOLD, F_IT = "DejaVuSans", "DejaVuSans-Bold", "DejaVuSans-Oblique"
FIGS = "figs"

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
NAVY   = colors.HexColor("#1b3a5c")
TEAL   = colors.HexColor("#0f7a7a")
CORAL  = colors.HexColor("#d1495b")
GOLD   = colors.HexColor("#e0a458")
GREY   = colors.HexColor("#6b6b6b")
DARK   = colors.HexColor("#1c1c1c")
LGREY  = colors.HexColor("#f2f3f5")
LTEAL  = colors.HexColor("#e6f3f3")
LCORAL = colors.HexColor("#fdeef0")
LGOLD  = colors.HexColor("#fbf1e3")

PAGE_W, PAGE_H = letter
MARGIN = 0.75 * inch
CONTENT_W = PAGE_W - 2*MARGIN

# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
styles = getSampleStyleSheet()
def add_style(name, **kw):
    if name in styles: styles.__dict__  # no-op guard
    styles.add(ParagraphStyle(name=name, **kw))

add_style("ReportTitle", fontName=F_BOLD, fontSize=24, leading=29, textColor=NAVY)
add_style("ReportSubtitle", fontName=F_REG, fontSize=12.5, leading=17, textColor=GREY)
add_style("CoverMeta", fontName=F_REG, fontSize=10, leading=15, textColor=DARK)
add_style("CoverMetaB", fontName=F_BOLD, fontSize=10, leading=15, textColor=DARK)
add_style("SectionNum", fontName=F_BOLD, fontSize=9.5, textColor=TEAL)
add_style("H1", fontName=F_BOLD, fontSize=16, leading=20, textColor=NAVY, spaceBefore=4, spaceAfter=10)
add_style("H2", fontName=F_BOLD, fontSize=12, leading=15.5, textColor=TEAL, spaceBefore=13, spaceAfter=6)
add_style("H3", fontName=F_BOLD, fontSize=10.4, leading=13.5, textColor=NAVY, spaceBefore=9, spaceAfter=4)
add_style("Body", fontName=F_REG, fontSize=9.6, leading=13.8, textColor=DARK, alignment=TA_JUSTIFY, spaceAfter=7)
add_style("BulletPt", fontName=F_REG, fontSize=9.5, leading=13.4, textColor=DARK, alignment=TA_JUSTIFY, spaceAfter=3, leftIndent=12)
add_style("Caption", fontName=F_IT, fontSize=8.2, leading=10.8, textColor=GREY, alignment=TA_CENTER, spaceBefore=3, spaceAfter=10)
add_style("Callout", fontName=F_REG, fontSize=9.4, leading=13.6, textColor=DARK, alignment=TA_JUSTIFY)
add_style("CalloutHead", fontName=F_BOLD, fontSize=9.7, textColor=NAVY, spaceAfter=3)
add_style("TOCSection", fontName=F_BOLD, fontSize=11.5, leading=22, textColor=NAVY)
add_style("TOCEntry", fontName=F_REG, fontSize=9.8, leading=17, textColor=DARK, leftIndent=14)
add_style("QuoteText", fontName=F_IT, fontSize=10, leading=14.5, textColor=colors.HexColor("#333333"))
add_style("TableCell", fontName=F_REG, fontSize=8.6, leading=11, textColor=DARK)
add_style("TableCellB", fontName=F_BOLD, fontSize=8.6, leading=11, textColor=colors.white)
add_style("EquationBox", fontName=F_REG, fontSize=10, leading=15, textColor=NAVY, alignment=TA_CENTER)

# ---------------------------------------------------------------------------
# Helper flowables
# ---------------------------------------------------------------------------
def hr(color=NAVY, thickness=1.1, sb=2, sa=8, width="100%"):
    return HRFlowable(width=width, thickness=thickness, color=color, spaceBefore=sb, spaceAfter=sa)

def section_header(number, title):
    return [
        Paragraph(f'SECTION {number}', styles["SectionNum"]),
        Paragraph(title, styles["H1"]),
        hr(color=NAVY, thickness=1.4, sa=12),
    ]

def P(text, style="Body"):
    return Paragraph(text, styles[style])

def bullets(items, style="BulletPt"):
    return [Paragraph(f'<font color="#0f7a7a">\u25aa</font>&nbsp;&nbsp;{it}', styles[style]) for it in items]

def stat_table(data, col_widths=None, font_size=8.6, first_col_left=True, highlight_rows=None):
    """data: list of rows (list of str/Paragraph); first row = header"""
    rows = []
    for r_i, row in enumerate(data):
        new_row = []
        for c_i, cell in enumerate(row):
            if isinstance(cell, str):
                st = "TableCellB" if r_i == 0 else "TableCell"
                al = "LEFT" if (c_i == 0 and first_col_left) else "CENTER"
                ps = ParagraphStyle("tmp", parent=styles[st], alignment=TA_LEFT if al=="LEFT" else TA_CENTER)
                new_row.append(Paragraph(cell, ps))
            else:
                new_row.append(cell)
        rows.append(new_row)
    t = Table(rows, colWidths=col_widths, hAlign="LEFT", repeatRows=1)
    style = [
        ("TOPPADDING", (0,0), (-1,-1), 4.5), ("BOTTOMPADDING", (0,0), (-1,-1), 4.5),
        ("LEFTPADDING", (0,0), (-1,-1), 7), ("RIGHTPADDING", (0,0), (-1,-1), 7),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#d7dde3")),
        ("BACKGROUND", (0,0), (-1,0), NAVY),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, LGREY]),
    ]
    if highlight_rows:
        for r in highlight_rows:
            style.append(("BACKGROUND", (0,r), (-1,r), LGOLD))
    t.setStyle(TableStyle(style))
    return t

def callout_box(head, paragraphs, bgcolor=LTEAL, bar_color=TEAL, icon="\u25c6"):
    inner = [Paragraph(f"{icon}&nbsp; {head}", styles["CalloutHead"])]
    for p in paragraphs:
        inner.append(Paragraph(p, styles["Callout"]))
    inner_tbl = Table([[c] for c in inner], colWidths=[CONTENT_W - 22])
    inner_tbl.setStyle(TableStyle([
        ("LEFTPADDING",(0,0),(-1,-1),0), ("RIGHTPADDING",(0,0),(-1,-1),0),
        ("TOPPADDING",(0,0),(-1,-1),1.5), ("BOTTOMPADDING",(0,0),(-1,-1),1.5),
    ]))
    outer = Table([[inner_tbl]], colWidths=[CONTENT_W])
    outer.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1), bgcolor),
        ("LINEBEFORE",(0,0),(0,-1), 3.2, bar_color),
        ("TOPPADDING",(0,0),(-1,-1), 9), ("BOTTOMPADDING",(0,0),(-1,-1), 9),
        ("LEFTPADDING",(0,0),(-1,-1), 12), ("RIGHTPADDING",(0,0),(-1,-1), 10),
    ]))
    return outer

def fig(path, width=6.5*inch, caption=None):
    img = Image(os.path.join(FIGS, path))
    ratio = img.imageHeight / float(img.imageWidth)
    img.drawWidth = width
    img.drawHeight = width * ratio
    flow = [img]
    if caption:
        flow.append(Paragraph(caption, styles["Caption"]))
    return flow

def two_col_figs(path1, path2, cap1, cap2, width=3.15*inch):
    img1 = Image(os.path.join(FIGS, path1)); r1 = img1.imageHeight/float(img1.imageWidth)
    img1.drawWidth = width; img1.drawHeight = width*r1
    img2 = Image(os.path.join(FIGS, path2)); r2 = img2.imageHeight/float(img2.imageWidth)
    img2.drawWidth = width; img2.drawHeight = width*r2
    t = Table([[img1, img2],
               [Paragraph(cap1, styles["Caption"]), Paragraph(cap2, styles["Caption"])]],
              colWidths=[width+0.1*inch, width+0.1*inch])
    t.setStyle(TableStyle([
        ("LEFTPADDING",(0,0),(-1,-1),3), ("RIGHTPADDING",(0,0),(-1,-1),3),
        ("TOPPADDING",(0,0),(-1,-1),0), ("BOTTOMPADDING",(0,0),(-1,-1),0),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
    ]))
    return t

def eq(text):
    tbl = Table([[Paragraph(text, styles["EquationBox"])]], colWidths=[CONTENT_W])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1), LGREY),
        ("BOX",(0,0),(-1,-1), 0.6, colors.HexColor("#c9d3da")),
        ("TOPPADDING",(0,0),(-1,-1), 8), ("BOTTOMPADDING",(0,0),(-1,-1), 8),
    ]))
    return tbl

# ---------------------------------------------------------------------------
# Header / Footer / Cover
# ---------------------------------------------------------------------------
REPORT_TAG = "A Statistical Inference Case Report"

def draw_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#d7dde3")); canvas.setLineWidth(0.6)
    canvas.line(MARGIN, 0.62*inch, PAGE_W-MARGIN, 0.62*inch)
    canvas.setFont(F_REG, 8); canvas.setFillColor(GREY)
    canvas.drawString(MARGIN, 0.42*inch, "MediGlucose Pharma Ltd.  |  Commercial Analytics Report")
    canvas.drawRightString(PAGE_W-MARGIN, 0.42*inch, f"Page {doc.page}")
    canvas.restoreState()

def draw_header(canvas, doc):
    canvas.saveState()
    canvas.setFont(F_BOLD, 8.2); canvas.setFillColor(NAVY)
    canvas.drawString(MARGIN, PAGE_H-0.55*inch, REPORT_TAG.upper())
    canvas.setFont(F_REG, 7.8); canvas.setFillColor(GREY)
    canvas.drawRightString(PAGE_W-MARGIN, PAGE_H-0.55*inch, "Confidential \u2014 Executive Committee Review")
    canvas.setStrokeColor(colors.HexColor("#d7dde3")); canvas.setLineWidth(0.6)
    canvas.line(MARGIN, PAGE_H-0.62*inch, PAGE_W-MARGIN, PAGE_H-0.62*inch)
    canvas.restoreState()

def content_page(canvas, doc):
    draw_header(canvas, doc); draw_footer(canvas, doc)

def cover_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY); canvas.rect(0, PAGE_H-2.5*inch, PAGE_W, 2.5*inch, fill=1, stroke=0)
    canvas.setFillColor(TEAL); canvas.rect(0, PAGE_H-2.56*inch, PAGE_W, 0.06*inch, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#eef1f4")); canvas.rect(0, 0, PAGE_W, 1.0*inch, fill=1, stroke=0)
    canvas.setFillColor(GOLD); canvas.rect(0, 1.0*inch, PAGE_W, 0.045*inch, fill=1, stroke=0)
    canvas.restoreState()

doc = BaseDocTemplate(
    "D:\\college_coding\\datascience\\pgdba\\isi\\inference\\infcase2.pdf",
    pagesize=letter, leftMargin=MARGIN, rightMargin=MARGIN, topMargin=0.95*inch, bottomMargin=0.85*inch,
    title="MediGlucose Pharma Ltd. - Statistical Inference Report", author="Priya Nair, Commercial Analytics",
)
frame_cover = Frame(0, 0, PAGE_W, PAGE_H, id="cover", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
frame_content = Frame(MARGIN, 0.85*inch, CONTENT_W, PAGE_H-0.95*inch-0.85*inch, id="content")
doc.addPageTemplates([
    PageTemplate(id="Cover", frames=[frame_cover], onPage=cover_page),
    PageTemplate(id="Content", frames=[frame_content], onPage=content_page),
])

story = []

# =============================================================================
# COVER PAGE
# =============================================================================
story.append(NextPageTemplate("Content"))
story.append(Spacer(1, 0.7*inch))

cover_title_style = ParagraphStyle("CoverTitleW", fontName=F_BOLD, fontSize=14.5, leading=18, textColor=colors.white)
cover_tag_style = ParagraphStyle("CoverTagW", fontName=F_REG, fontSize=10, leading=14, textColor=colors.HexColor("#cfe0e0"))

story.append(Table([[Paragraph("MEDIGLUCOSE PHARMA LTD.", cover_title_style)],
                     [Paragraph("Commercial Analytics  |  Genome Valley, Hyderabad", cover_tag_style)]],
                    colWidths=[7*inch],
                    style=TableStyle([("LEFTPADDING",(0,0),(-1,-1), 0.6*inch), ("TOPPADDING",(0,0),(0,0), 4)])))

story.append(Spacer(1, 1.45*inch))
story.append(Table([[Paragraph("The Oral Diabetes Portfolio", styles["ReportTitle"])]], colWidths=[7*inch],
                    style=TableStyle([("LEFTPADDING",(0,0),(-1,-1), 0.6*inch)])))
story.append(Spacer(1, 0.06*inch))
story.append(Table([[Paragraph("Resolving Four Boardroom Disputes Through Statistical Inference:<br/>"
                                "Quota-Setting &bull; Clinical Efficacy &bull; Promotional ROI &bull; Shelf-Life",
                                styles["ReportSubtitle"])]], colWidths=[7*inch],
                    style=TableStyle([("LEFTPADDING",(0,0),(-1,-1), 0.6*inch)])))

story.append(Spacer(1, 0.5*inch))
story.append(Table([[hr(color=colors.HexColor("#c9d3da"), thickness=1, sb=0, sa=0, width=5.8*inch)]],
                    colWidths=[7*inch], style=TableStyle([("LEFTPADDING",(0,0),(-1,-1), 0.6*inch)])))
story.append(Spacer(1, 0.28*inch))

meta_data = [
    ("Prepared for", "Rajeev Menon, Chief Operating Officer — Executive Committee"),
    ("Prepared by", "Priya Nair, Head of Commercial Analytics"),
    ("Datasets analysed", "Territory_Sales_Gluconil.csv &bull; Patient_HbA1c_Trial_Data.csv<br/>"
                          "Marketing_Spend_vs_Sales.csv &bull; Drug_Stability_Potency.csv"),
    ("Scope", "120 territories &bull; 120-patient surveillance cohort &bull; 24-month stability study"),
    ("Date", "September 2026"),
]
meta_rows = [[Paragraph(k, styles["CoverMetaB"]), Paragraph(v, styles["CoverMeta"])] for k, v in meta_data]
meta_tbl = Table(meta_rows, colWidths=[1.5*inch, 5*inch])
meta_tbl.setStyle(TableStyle([("LEFTPADDING",(0,0),(-1,-1),0), ("TOPPADDING",(0,0),(-1,-1),3.5),
                               ("BOTTOMPADDING",(0,0),(-1,-1),3.5), ("VALIGN",(0,0),(-1,-1),"TOP")]))
story.append(Table([[meta_tbl]], colWidths=[7*inch], style=TableStyle([("LEFTPADDING",(0,0),(-1,-1), 0.6*inch)])))

story.append(Spacer(1, 0.7*inch))
story.append(Table([[Paragraph('&ldquo;I do not want textbook jargon. I want an objective narrative grounded '
                                'in the data.&rdquo;<br/>&mdash; Rajeev Menon, Chief Operating Officer',
                                styles["QuoteText"])]], colWidths=[6.2*inch],
                    style=TableStyle([("LEFTPADDING",(0,0),(-1,-1), 0.6*inch)])))
story.append(PageBreak())

print("Cover built.")

# =============================================================================
# TABLE OF CONTENTS
# =============================================================================
story.append(Paragraph("Table of Contents", styles["H1"]))
story.append(hr(color=NAVY, thickness=1.4, sa=14))

toc_entries = [
    ("Executive Summary", "3"),
    ("Section 1 — Territory Sales & the Quota-Setting Dispute", "4"),
    ("Section 2 — Clinical Efficacy & Patient Response Variation", "8"),
    ("Section 3 — Marketing Spend & the Promotional ROI Dispute", "12"),
    ("Section 4 — Stability Kinetics & the Shelf-Life Recommendation", "16"),
    ("Synthesis — From Instinct to Inference", "20"),
    ("Appendix — Methods, Formulae & Data Notes", "21"),
]
toc_rows = []
for title, pg in toc_entries:
    toc_rows.append([Paragraph(title, styles["TOCEntry"]), Paragraph(pg, ParagraphStyle("pgn", parent=styles["TOCEntry"], alignment=TA_CENTER))])
toc_tbl = Table(toc_rows, colWidths=[5.7*inch, 0.8*inch])
toc_tbl.setStyle(TableStyle([
    ("LEFTPADDING",(0,0),(-1,-1),0), ("TOPPADDING",(0,0),(-1,-1),4), ("BOTTOMPADDING",(0,0),(-1,-1),4),
    ("LINEBELOW", (0,0), (-1,-2), 0.4, colors.HexColor("#e3e6ea")),
]))
story.append(toc_tbl)
story.append(Spacer(1, 0.3*inch))
story.append(callout_box(
    "How to read this report",
    ["Each section opens with the operational dispute as Menon described it, walks through the statistical "
     "diagnosis, and closes with a specific recommendation. Boxes marked with a diamond (&#9670;) flag "
     "additional analysis beyond the base notebook output &mdash; findings that sharpen or, in one case, "
     "materially change the recommendation the functional heads were expecting."],
    bgcolor=LGREY, bar_color=NAVY, icon="\u2139"
))
story.append(PageBreak())

# =============================================================================
# EXECUTIVE SUMMARY
# =============================================================================
story.extend(section_header("\u2014", "Executive Summary"))

story.append(P(
    "Every one of the four disputes Rajeev Menon brought to this desk shares the same root cause: a single "
    "summary number &mdash; a mean, a straight-line slope, a round-number expiry date &mdash; was being asked "
    "to describe a reality that is not simple, symmetric, or linear. In three of the four cases, a more careful "
    "look at the shape of the data materially changes what leadership should do next. In the fourth, it reverses "
    "the direction of the ask entirely."
))

story.append(Table([[
    Paragraph("Dispute", ParagraphStyle("h", parent=styles["TableCellB"], alignment=TA_LEFT)),
    Paragraph("What the functional head assumed", ParagraphStyle("h", parent=styles["TableCellB"], alignment=TA_LEFT)),
    Paragraph("What the data actually shows", ParagraphStyle("h", parent=styles["TableCellB"], alignment=TA_LEFT)),
]], colWidths=[1.15*inch, 2.55*inch, 2.65*inch], style=TableStyle([
    ("BACKGROUND",(0,0),(-1,-1), NAVY), ("TOPPADDING",(0,0),(-1,-1),6), ("BOTTOMPADDING",(0,0),(-1,-1),6),
    ("LEFTPADDING",(0,0),(-1,-1),7),
])))

exec_rows = [
    ["Territory\nquota", "Mean sales of 830 units justify a flat 15% quota hike everywhere.",
     "Mean is inflated by 5 tender-driven territories sitting in a class of their own. Typical (median) territory sells 687; a uniform hike would be unachievable for ~90% of the network."],
    ["Clinical\nefficacy", "A mean HbA1c drop of 1.28pp settles the safety debate.",
     "True on average, but the response distribution has heavy tails (excess kurtosis 1.92) and 4 statistically atypical patients — 2 poor responders, 2 hyper-responders — that need individual clinical review before the regulatory filing."],
    ["Marketing\nROI", "Every extra ₹1 lakh buys the same extra volume (straight-line payback).",
     "A logarithmic, diminishing-returns model beats the straight line on R², RMSE, AIC and BIC simultaneously. The finance controller's instinct is the statistically preferred model."],
    ["Shelf\nlife", "The 18-month legacy expiry is conservative; there is room to extend it.",
     "The opposite is true. Even the point estimate crosses the 90% floor at 13.4 months; a statistically defensible (95% prediction-interval) shelf life is only ~11.8 months. The current 18-month label is not supported by this batch's data."],
]
for r in exec_rows:
    tbl = Table([[Paragraph(f"<b>{r[0]}</b>", ParagraphStyle("c0", parent=styles["TableCell"], alignment=TA_LEFT)),
                  Paragraph(r[1], styles["TableCell"]),
                  Paragraph(r[2], styles["TableCell"])]],
                colWidths=[1.15*inch, 2.55*inch, 2.65*inch])
    tbl.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1), 0.5, colors.HexColor("#d7dde3")),
        ("TOPPADDING",(0,0),(-1,-1),6), ("BOTTOMPADDING",(0,0),(-1,-1),6), ("LEFTPADDING",(0,0),(-1,-1),7),
        ("VALIGN",(0,0),(-1,-1),"TOP"), ("BACKGROUND",(0,0),(0,-1), LTEAL),
    ]))
    story.append(tbl)

story.append(Spacer(1, 10))
story.append(P(
    "The single most important finding in this report is the last one. Manufacturing framed the shelf-life "
    "question as an opportunity to <i>extend</i> the printed expiry from 18 to something longer, in order to "
    "reduce return-and-destroy write-offs. The stability data says the opposite: on the evidence of this "
    "validation batch, product may already be crossing the legal 90% potency floor several months "
    "<i>before</i> the current label expires. This is flagged prominently in Section 4 and should be treated as "
    "a compliance question, not a supply-chain optimisation."
))
story.append(PageBreak())

# =============================================================================
# SECTION 1 — TERRITORY SALES
# =============================================================================
story.extend(section_header("1", "Territory Sales & the Quota-Setting Dispute"))

story.append(P(
    "The national sales head's memorandum cited an average of 830 units per territory against a 750-unit "
    "baseline, and proposed a uniform 15% quota increase across all 120 territories. Depot managers "
    "immediately pushed back, reporting unsold inventory piling up. Both sides are, in a narrow sense, "
    "correct \u2014 which is exactly the problem with using a single number to settle the argument."
))

story.append(P("<b>1.1&nbsp;&nbsp;Why the Arithmetic Mean Is the Wrong Anchor</b>", "Body"))
story.append(P(
    "Monthly territory volumes range from 195 to 3,792 units \u2014 a nearly 20-fold spread. Because the "
    "distribution is this asymmetric, a classical bin-width rule (Sturges' or Scott's) tuned for roughly "
    "bell-shaped data would badly misrepresent it. The Freedman&ndash;Diaconis rule, which sets bin width "
    "from the interquartile range (IQR) rather than the standard deviation, is the appropriate choice because "
    "it is not distorted by the extreme values in the right tail."
))
story.append(eq("Bin width = 2 &times; IQR &times; n<super>&minus;1/3</super> &nbsp;=&nbsp; 2 &times; 410.5 &times; 120<super>&minus;1/3</super> &nbsp;&asymp;&nbsp; 166.4  &nbsp;&rarr;&nbsp; 22 bins"))
story.append(Spacer(1,6))
# story.extend(fig("sales_hist.png", caption="Figure 1.1 \u2014 Territory sales distribution, Freedman&ndash;Diaconis binning. "
#                                             "The bulk of territories cluster between 350 and 1,000 units; a thin, "
#                                             "separated tail extends past 3,500."))

story.append(P(
    "The histogram confirms the visual complaint from the field: this is a strongly right-skewed distribution "
    "with a small number of extreme values pulling the mean well above where most territories actually sit. "
    "The choice of \"typical territory\" summary statistic therefore matters enormously for target-setting."
))

story.append(stat_table([
    ["Central tendency measure", "Value (units)", "Comment"],
    ["Arithmetic mean", "829.99", "Distorted upward by 5 extreme territories"],
    ["Median", "687.00", "Robust \u2014 unaffected by tail values"],
    ["10% trimmed mean", "705.39", "Drops top/bottom 10% before averaging"],
    ["Winsorized mean", "727.21", "Caps rather than removes extreme values"],
], col_widths=[2.3*inch, 1.3*inch, 3.3*inch]))
story.append(Paragraph("Table 1.1 \u2014 The mean overstates the \"typical\" territory by 21&ndash;24% versus every robust alternative.", styles["Caption"]))

story.append(callout_box(
    "Reading for the board",
    ["A uniform 15% hike on a baseline of 830 asks every territory to hit roughly 954 units. Against a median "
     "of 687, that target sits above the 75th percentile (909.5) of the <i>entire current network</i> \u2014 "
     "meaning the sales head's own \"average performer\" target would already be a top-quartile ask for most "
     "reps even before the proposed increase."]
))

story.append(P("<b>1.2&nbsp;&nbsp;Identifying Structurally Unusual Territories</b>", "Body"))
story.append(P(
    "Tukey's fence method flags observations using multiples of the IQR beyond Q1 and Q3 \u2014 a distribution-free "
    "rule well suited to skewed data. \"Soft\" fences (1.5&times;IQR) catch moderate departures; \"hard\" fences "
    "(3.0&times;IQR) catch severe ones."
))
story.append(stat_table([
    ["Statistic", "Value"],
    ["Q1 / Q3", "499.00 / 909.50"], ["IQR", "410.50"],
    ["Soft fences (1.5\u00d7IQR)", "&minus;116.75  /  1,525.25"],
    ["Hard fences (3.0\u00d7IQR)", "&minus;732.50  /  2,141.00"],
    ["Soft outliers (n)", "7"], ["Hard outliers (n)", "5"],
], col_widths=[2.6*inch, 4.3*inch]))

# story.extend(fig("sales_box.png", caption="Figure 1.2 \u2014 Boxplot of monthly territory sales; circles mark Tukey outliers, "
#                                            "diamond marks the mean."))

story.append(P(
    "Five territories \u2014 selling between 3,520 and 3,792 units \u2014 clear even the <i>hard</i> fence of "
    "2,141 units. Two further territories (1,535 and 1,925 units) are soft outliers only. The case narrative "
    "hints at the likely explanation: periodic institutional hospital tenders rather than steady retail "
    "prescription volume. Section 1.6 tests this hypothesis directly."
))

story.append(P("<b>1.3&nbsp;&nbsp;Quantifying the Skew</b>", "Body"))
story.append(P(
    "The third and fourth standardized moments confirm what the histogram shows and give the board a precise "
    "vocabulary for the mean-median gap."
))
story.append(stat_table([
    ["Moment", "Value", "Interpretation"],
    ["Skewness", "3.26", "Strong positive (right) skew \u2014 the mean-median gap of 143 units is a direct, textbook consequence"],
    ["Excess kurtosis", "11.32", "Extremely leptokurtic \u2014 far heavier tails than a normal distribution; a handful of very large values dominate the shape"],
], col_widths=[1.6*inch, 1.0*inch, 4.3*inch]))

story.append(P("<b>1.4&nbsp;&nbsp;Robust Dispersion: Looking Past the Standard Deviation</b>", "Body"))
story.append(P(
    "The sample standard deviation (665.3) is itself inflated by the same extreme values that inflate the "
    "mean \u2014 squaring deviations punishes outliers disproportionately. Mean Absolute Deviation (MAD about "
    "the median) and Median Absolute Deviation (MedAD) use absolute rather than squared distances and are far "
    "more resistant to contamination."
))
story.append(stat_table([
    ["Dispersion measure", "Value (units)"],
    ["Standard deviation", "665.34"],
    ["Mean absolute deviation (about median)", "349.13"],
    ["Median absolute deviation (about median)", "205.50"],
], col_widths=[3.8*inch, 3.1*inch]))
story.append(P(
    "The gap between these numbers is itself diagnostic: if the data were close to normal, MAD would be "
    "about 0.8&times;SD and MedAD about 0.67&times;SD. Here MAD is only 0.52&times;SD and MedAD only "
    "0.31&times;SD \u2014 both far below what normality would predict, which is exactly what a small number of "
    "very large outliers does to the SD."
))

story.append(P("<b>1.5&nbsp;&nbsp;A Distribution-Free Safety Guarantee: Chebyshev vs. Reality</b>", "Body"))
story.append(P(
    "Chebyshev's inequality guarantees a minimum proportion of any distribution \u2014 regardless of shape "
    "\u2014 that must fall within k standard deviations of the mean:"
))
story.append(eq("P(|X &minus; &mu;| &lt; k&sigma;) &ge; 1 &minus; 1/k&sup2;  &nbsp;&rArr;&nbsp;  for k = 2: at least 1 &minus; 1/4 = <b>75%</b> guaranteed"))
story.append(P(
    "The empirical figure is 95.83% of territories within 2 standard deviations of the mean. The gap between "
    "the 75% worst-case guarantee and the 95.8% actual outcome is a useful teaching point for the board: "
    "Chebyshev's bound is deliberately conservative because it must hold for <i>any</i> distribution shape, "
    "including this one's heavy right tail; the empirical concentration around the centre is still much "
    "tighter than the guarantee alone would suggest."
))

# story.extend(fig("sales_ogive.png", caption="Figure 1.3 \u2014 Ogive (cumulative distribution) of territory sales. Field "
#                                              "directors can read P25, P50 and P90 directly off this curve without software."))
story.append(P(
    "This ogive is the practical deliverable for the field organisation: a rep can locate any territory's "
    "percentile rank at a glance, which is a far more actionable planning tool than a single average that a "
    "given rep either clears easily or can never reach."
))
story.append(PageBreak())

story.append(callout_box(
    "Unique insight: the tender cluster is not really part of this distribution",
    ["Sorting all 120 territories by volume and examining consecutive gaps reveals something the summary "
     "statistics alone do not show directly: between the 115th-ranked territory (1,925 units) and the "
     "116th-ranked territory (3,520 units) sits a gap of <b>1,595 units</b> \u2014 by far the largest jump "
     "anywhere in the sorted data (the next-largest gap is 390 units, and the typical gap between adjacent "
     "territories is under 15 units). No territory in the entire network sells between roughly 1,930 and "
     "3,520 units a month.",
     "The five territories above that gap are also unusually tightly clustered among themselves \u2014 "
     "3,520 to 3,792, a spread of only 272 units (7.2% of their own mean), versus a coefficient of variation "
     "of over 45% for the rest of the network. Tight internal clustering combined with a large, otherwise-"
     "unpopulated gap is the classic statistical signature of a genuinely separate data-generating process, "
     "not simply \"five lucky retail territories\" at the extreme end of one continuous distribution. This is "
     "precisely what one would expect if these territories' volumes are dominated by lumpy, periodic "
     "institutional tender orders rather than the same steady physician-detailing dynamic driving the other "
     "115 territories."],
    bgcolor=LCORAL, bar_color=CORAL, icon="\u25c6"
))
# story.extend(fig("sales_gap.png", caption="Figure 1.4 \u2014 Territories ranked by volume. The shaded band is a 1,595-unit "
#                                            "range with zero observations, separating a tight 5-territory cluster from "
#                                            "the rest of the network."))

story.append(KeepTogether([P("<b>1.6&nbsp;&nbsp;Recommendation to the COO</b>", "Body")] + bullets([
    "<b>Reject the uniform 15% hike.</b> Anchoring quotas to the mean (830) sets an unreachable bar for roughly "
    "90% of the network while barely stretching the five tender-driven outliers.",
    "<b>Anchor organic retail quotas to the trimmed mean (&asymp;705) or median (687)</b>, with graduated tiers "
    "by territory size rather than one flat percentage uplift.",
    "<b>Report the five hard-outlier (tender) territories as a separate institutional-sales KPI</b>, tracked and "
    "incentivised on tender-win-rate rather than folded into a rep's monthly retail quota \u2014 mixing the two "
    "creates exactly the kind of unachievable-quota complaints depot managers are already raising.",
    "<b>Use the ogive, not the mean,</b> as the field-facing planning tool so reps and depot managers can see "
    "where their territory actually sits in the distribution.",
])))
story.append(PageBreak())

# =============================================================================
# SECTION 2 — CLINICAL EFFICACY
# =============================================================================
story.extend(section_header("2", "Clinical Efficacy & Patient Response Variation"))

story.append(P(
    "A 12-week post-marketing surveillance study of 120 patients reported a mean HbA1c reduction of 1.28 "
    "percentage points \u2014 comfortably above the threshold treatment guidelines consider clinically "
    "meaningful. Two medical directors nonetheless flagged concern over non-responders and unusually large "
    "responses. The statistical question is whether the mean is hiding a genuine safety signal in the tails."
))

story.append(P("<b>2.1&nbsp;&nbsp;The Response Distribution</b>", "Body"))
# story.extend(fig("hba1c_hist.png", caption="Figure 2.1 \u2014 Distribution of 12-week HbA1c reduction (n=120), "
#                                             "Freedman&ndash;Diaconis binning."))
story.append(stat_table([
    ["Statistic", "Value"],
    ["Mean", "1.278 pp"], ["Median", "1.280 pp"], ["Standard deviation", "0.412 pp"],
    ["Skewness", "&minus;0.20 (mild left skew)"], ["Excess kurtosis", "1.92 (leptokurtic)"],
], col_widths=[2.6*inch, 4.3*inch]))
story.append(P(
    "Mean and median are almost identical here (1.278 vs. 1.280) \u2014 unlike the sales data, this "
    "distribution is close to symmetric. The concern is not skew but tail weight: excess kurtosis of 1.92 "
    "means genuinely extreme responses, in both directions, occur measurably more often than a normal "
    "distribution would predict."
))

story.append(P("<b>2.2&nbsp;&nbsp;Flagging Atypical Responders</b>", "Body"))
# story.extend(fig("hba1c_box.png", caption="Figure 2.2 \u2014 Five-number summary with Tukey (1.5\u00d7IQR) fences; "
#                                            "flagged patients are labelled."))
story.append(stat_table([
    ["Patient", "HbA1c change (pp)", "Age", "Read"],
    ["P036", "&minus;0.24", "52", "Non-responder / mild deterioration"],
    ["P091", "+0.15", "83", "Minimal responder"],
    ["P059", "+2.52", "60", "Hyper-responder"],
    ["P114", "+2.63", "76", "Hyper-responder"],
], col_widths=[1.0*inch, 1.55*inch, 0.75*inch, 3.6*inch]))
story.append(P(
    "None of these four clear the stricter 3.0&times;IQR \"hard\" fence (&minus;0.39 to 2.97 pp) \u2014 the "
    "hard-outlier count is zero. All four are, however, soft outliers, and clinically distinct enough to "
    "warrant individual chart review rather than automatic dismissal or automatic inclusion."
))
story.append(callout_box(
    "What to verify before the regulatory dossier is finalised",
    ["The case narrative correctly frames this as a judgement call, not a statistical one. Before any of "
     "these four records is excluded or specially annotated, medical affairs should check, in order: "
     "(i) transcription or lab-assay error on the raw HbA1c reading, (ii) documented non-compliance "
     "(missed doses, concurrent unlisted medication) for P036 and P091, (iii) baseline insulin resistance "
     "or beta-cell reserve for the two hyper-responders, and only then (iv) true pharmacological "
     "hypersensitivity. Regulatory bodies view undocumented outlier exclusion unfavourably \u2014 the "
     "verification trail matters as much as the statistical flag itself."],
    bgcolor=LGREY, bar_color=NAVY, icon="\u2139"
))

story.append(P("<b>2.3&nbsp;&nbsp;Why the Coefficient of Variation Does Not Belong Here</b>", "Body"))
story.append(P(
    "A junior analyst's instinct to report CV = SD/mean (32.4% as computed) is methodologically unsound for "
    "this variable. CV is only meaningful on a ratio scale with a non-arbitrary, strictly-positive zero point "
    "\u2014 it answers \"how large is the spread relative to a meaningful positive baseline?\" HbA1c "
    "<i>reduction</i> is a change score that can legitimately be zero or negative (deterioration). Dividing by "
    "a mean that sits close to zero, or by an average whose sign is not fixed across patients, makes the "
    "ratio unstable and clinically uninterpretable \u2014 a patient near zero change would produce an "
    "arbitrarily large CV despite an unremarkable outcome. Standard deviation and the IQR-based fences used "
    "above are the correct dispersion tools for a change score of this kind."
))

story.append(P("<b>2.4&nbsp;&nbsp;Age Representation in the Trial Cohort</b>", "Body"))
# story.extend(fig("age_ogive.png", caption="Figure 2.3 \u2014 Cumulative age distribution. The youngest quartile of the "
#                                             "cohort is 49 years or younger."))
story.append(callout_box(
    "Unique insight: the elderly under-representation concern does not hold up",
    ["The regulatory panel's stated concern was that the trial under-represents elderly patients. The "
     "cumulative distribution answers the literal question asked in the case (the youngest-quartile boundary "
     "is 49 years) \u2014 but the more decision-relevant number is on the other tail: <b>25.8% of the cohort "
     "(31 of 120 patients) is aged 65 or older</b>, and 12.5% are 70+. Given that Type 2 diabetes prevalence "
     "itself rises sharply with age in the Indian population this trial is meant to represent, a quarter of "
     "the cohort being 65+ is a reasonably proportionate &mdash; not deficient &mdash; representation. This "
     "reframes the regulatory question: the filing can cite this figure directly rather than only the age "
     "quartile boundary."],
    bgcolor=LTEAL, bar_color=TEAL, icon="\u25c6"
))

story.append(P("<b>2.5&nbsp;&nbsp;Does Age Predict Efficacy? The Renal-Clearance Hypothesis</b>", "Body"))
# story.extend(fig("age_vs_hba1c.png", caption="Figure 2.4 \u2014 Age vs. HbA1c reduction. The near-flat regression line "
#                                               "and low r confirm no population-level association."))
story.append(P(
    "The Pearson correlation between age and HbA1c reduction is r = &minus;0.041 (p = 0.65) \u2014 not "
    "distinguishable from zero. There is therefore no population-level evidence that impaired renal clearance "
    "or altered metabolic capacity in older patients is blunting Gluconil's efficacy; a rank-based (Spearman) "
    "check gives an essentially identical result, confirming the conclusion is not an artefact of the linear "
    "assumption or the tail outliers."
))
story.append(callout_box(
    "Unique insight: a nuance worth flagging for medical affairs, even though the topline is reassuring",
    ["The four flagged outlier patients from Section 2.2 average 67.75 years old, versus 56.13 for the "
     "remaining 116 patients \u2014 nearly 12 years older on average. With only four data points this cannot "
     "be treated as statistical evidence of an age effect (and it does not contradict the population-level "
     "null correlation above), but it is a pattern worth a targeted clinical look: the patients furthest from "
     "the typical response, in either direction, skew notably older than the rest of the cohort. This "
     "supports doing the individual-patient verification recommended in 2.2 with particular attention to "
     "age-related pharmacokinetics for these four records specifically, even though no broad age-based "
     "dosing signal exists across the trial as a whole."],
    bgcolor=LCORAL, bar_color=CORAL, icon="\u25c6"
))

story.append(KeepTogether([P("<b>2.6&nbsp;&nbsp;Recommendation</b>", "Body")] + bullets([
    "<b>The topline efficacy claim stands.</b> Mean and median reduction both comfortably clear the clinically "
    "meaningful threshold, and the distribution is not skewed.",
    "<b>Route the four flagged patients through documented clinical verification</b> (compliance records, "
    "repeat labs, baseline characteristics) before any decision to annotate or exclude them from the filing.",
    "<b>Do not report the coefficient of variation for this endpoint</b> &mdash; report SD and the IQR-based "
    "fences instead.",
    "<b>Cite the 25.8% aged-65+ figure directly</b> in response to the regulatory under-representation query, "
    "in addition to the age-quartile boundary.",
    "<b>Flag no population-level age-efficacy relationship,</b> while asking medical affairs to give the four "
    "outlier patients' age-related pharmacokinetics a closer individual look.",
])))
story.append(PageBreak())

# =============================================================================
# SECTION 3 — MARKETING SPEND
# =============================================================================
story.extend(section_header("3", "Marketing Spend & the Promotional ROI Dispute"))

story.append(P(
    "The sales VP wants a straight-line payback model: every additional lakh of promotional spend buys an "
    "identical increment in prescriptions. The finance controller expects diminishing returns as detailing "
    "saturates the available physician base. With ₹8 lakh and ₹15 lakh scenarios both on the table for next "
    "year's budget, the choice of functional form is a real capital-allocation decision, not an academic one."
))

story.append(P("<b>3.1&nbsp;&nbsp;Four Candidate Models</b>", "Body"))
# story.extend(fig("mkt_models.png", caption="Figure 3.1 \u2014 Marketing spend vs. units sold, with linear, logarithmic, "
#                                             "power and quadratic fits overlaid. The curved models track the visible "
#                                             "saturation at high spend noticeably better than the straight line."))

story.append(stat_table([
    ["Model", "Equation", "R\u00b2", "RMSE"],
    ["Linear", "Y = 932.84 + 52.04 X", "0.7609", "197.99"],
    ["Logarithmic", "Y = 317.72 + 544.59 ln(X)", "0.8242", "169.79"],
    ["Power", "Y = 599.52 X<super>0.399</super>", "0.8104", "176.31"],
    ["Quadratic", "Y = 638.25 + 112.84 X &minus; 2.304 X&sup2;", "0.8160", "173.72"],
], col_widths=[1.15*inch, 3.05*inch, 0.9*inch, 1.0*inch]))

story.append(P(
    "The straight line explains 76.1% of territory-to-territory variation in sales \u2014 not bad in isolation, "
    "but every curved alternative explains more of it with the same or fewer effective parameters. As a "
    "cross-check, the reported correlation coefficient of 0.8723 satisfies r&sup2; = R&sup2; for the linear "
    "fit exactly (0.8723&sup2; = 0.7609), confirming the R&sup2; figure is being computed correctly."
))

story.append(P("<b>3.2&nbsp;&nbsp;Interpreting the Logarithmic Model</b>", "Body"))
story.append(P(
    "In Y = a + b&nbsp;ln(X), the coefficient b converts naturally into a percentage-change statement: a 1% "
    "increase in marketing spend is associated with an increase of b/100 &asymp; 5.45 units sold, "
    "<i>regardless of the starting spend level</i>. This is the mathematical expression of the finance "
    "controller's intuition &mdash; the same percentage increase in budget buys a shrinking number of "
    "absolute units as the base spend grows, because the base itself is growing."
))

story.append(P("<b>3.3&nbsp;&nbsp;Model Selection: Penalising Complexity, Not Just Rewarding Fit</b>", "Body"))
story.append(callout_box(
    "Unique insight: information criteria settle the dispute more rigorously than R\u00b2 alone",
    ["R&sup2; and RMSE cannot by themselves adjudicate between models with different numbers of parameters "
     "&mdash; a model with an extra free parameter will typically fit marginally better even if it is not "
     "truly superior. Akaike and Bayesian Information Criteria (AIC, BIC) penalise that extra flexibility "
     "directly. Recomputing them from the same fitted residuals settles the question decisively:"],
    bgcolor=LTEAL, bar_color=TEAL, icon="\u25c6"
))
story.append(Spacer(1,4))
story.append(stat_table([
    ["Model", "Parameters (k)", "AIC", "AICc", "BIC"],
    ["Linear", "2", "1273.18", "1273.28", "1278.75"],
    ["Logarithmic", "2", "1236.30", "1236.40", "1241.87"],
    ["Power", "2", "1245.34", "1245.44", "1250.91"],
    ["Quadratic", "3", "1243.78", "1243.99", "1252.15"],
], col_widths=[1.15*inch, 1.25*inch, 1.1*inch, 1.1*inch, 1.1*inch], highlight_rows=[2]))
story.append(P(
    "Lower is better on every criterion. The logarithmic model wins on AIC, AICc <i>and</i> BIC "
    "simultaneously, despite using the same two parameters as the linear model and one fewer than the "
    "quadratic. The quadratic model's marginally higher R&sup2; than the log model (0.816 vs. 0.824 \u2014 "
    "actually lower) is not enough to justify its extra parameter once complexity is penalised by BIC. "
    "<b>The finance controller's diminishing-returns hypothesis is the statistically preferred model, not "
    "merely a plausible alternative to the sales VP's straight line.</b>"
))

story.append(P("<b>3.4&nbsp;&nbsp;Quantifying Diminishing Returns Directly</b>", "Body"))
story.append(callout_box(
    "Unique insight: the marginal-return curve makes the overfitting risk visible, not just theoretical",
    ["Differentiating each fitted equation gives the marginal units sold per additional &#8377;1 lakh at any "
     "spend level \u2014 the number that should actually drive a capital-allocation decision, since it answers "
     "\"is the next lakh worth spending?\" rather than \"how good is the overall fit?\""],
    bgcolor=LCORAL, bar_color=CORAL, icon="\u25c6"
))
# story.extend(fig("mkt_marginal.png", caption="Figure 3.2 \u2014 Marginal units sold per additional &#8377;1 lakh of spend, "
#                                               "by model. The linear model's marginal return is flat by construction "
#                                               "&mdash; the VP's claim, made visible and testable."))
story.append(stat_table([
    ["Spend (&#8377; lakh)", "Linear", "Log", "Power", "Quadratic"],
    ["3", "52.0", "181.5", "123.5", "99.0"],
    ["8", "52.0", "68.1", "68.5", "76.0"],
    ["15", "52.0", "36.3", "46.9", "43.7"],
    ["24", "52.0", "22.7", "35.4", "2.2"],
], col_widths=[1.3*inch, 1.05*inch, 1.05*inch, 1.05*inch, 1.25*inch]))
story.append(P(
    "The linear model's marginal return is constant at 52.0 units/lakh by construction \u2014 it cannot show "
    "saturation because none was assumed. Every other model shows marginal returns falling sharply as spend "
    "rises. The quadratic model is the most striking: its marginal return crosses zero at "
    "&#8377;24.48 lakh \u2014 essentially at the edge of the observed data (max spend in the sample is "
    "&#8377;24.94 lakh). Extrapolate this model even slightly beyond the data actually collected and it "
    "predicts that <i>more</i> marketing spend <i>reduces</i> sales, which has no operational meaning. This is "
    "the overfitting danger the case describes, made concrete and numerical rather than left as a general "
    "warning."
))

story.append(P("<b>3.5&nbsp;&nbsp;Residual Diagnostics</b>", "Body"))
# story.extend(fig("mkt_residuals.png", caption="Figure 3.3 \u2014 Residuals for the linear (left) and logarithmic (right) "
#                                                "models. The linear residuals show a faint bow-shaped pattern (positive "
#                                                "in the middle, negative at both ends) consistent with an unmodelled "
#                                                "curvature; the logarithmic residuals scatter more evenly around zero."))

story.append(P("<b>3.6&nbsp;&nbsp;Budget Scenarios</b>", "Body"))
story.append(stat_table([
    ["Spend scenario", "Linear", "Logarithmic", "Power", "Quadratic"],
    ["&#8377;8 lakh", "1,349", "1,450", "1,374", "1,393"],
    ["&#8377;15 lakh", "1,713", "1,793", "1,765", "1,812"],
    ["Implied gain (8\u219215L)", "+364", "+343", "+391", "+419"],
], col_widths=[1.75*inch, 1.25*inch, 1.25*inch, 1.15*inch, 1.25*inch]))
story.append(P(
    "The four models bracket a reasonably tight range for both scenarios (roughly &plusmn;5% of the "
    "logarithmic-model estimate), which is itself a useful robustness statement for the board: the "
    "<i>direction and rough magnitude</i> of the budget increase's payoff is not highly sensitive to which "
    "curve is used, even though the underlying shape assumption differs sharply. The logarithmic model's "
    "&#8377;1,792.5 estimate at &#8377;15 lakh should be treated as the central planning number."
))

story.append(P("<b>3.7&nbsp;&nbsp;Why Not Simply Use a Non-Parametric Smoother?</b>", "Body"))
story.append(P(
    "A LOESS curve or spline would likely track the scatter even more closely than any of the four models "
    "above. It would also hand field managers no usable formula: a locally-adaptive smoother has no single "
    "slope or exponent that can be written into a quota sheet or an Excel budget model, and its shape changes "
    "depending on exactly which territories are or are not in the training data at any given time. For a "
    "recurring, board-level capital allocation decision, an explicit, stable, low-parameter equation that "
    "field teams can apply consistently is worth more than an incremental gain in curve-fitting accuracy."
))

story.append(KeepTogether([P("<b>3.8&nbsp;&nbsp;Recommendation</b>", "Body")] + bullets([
    "<b>Adopt the logarithmic model</b> as the basis for territory-level budget allocation \u2014 it wins on "
    "R&sup2;, RMSE, AIC and BIC simultaneously against all three alternatives.",
    "<b>Reject the sales VP's straight-line payback assumption</b> for planning purposes; it is not merely a "
    "simplification but a statistically dominated model.",
    "<b>Do not use the quadratic model to guide spend above roughly &#8377;20&ndash;22 lakh</b> \u2014 its "
    "marginal-return curve turns negative almost exactly at the edge of the data used to fit it.",
    "<b>Budget expectation for &#8377;15 lakh:</b> approximately 1,790&ndash;1,810 units, versus "
    "approximately 1,350&ndash;1,450 units at &#8377;8 lakh \u2014 a real but decelerating gain from the "
    "additional &#8377;7 lakh.",
])))
story.append(PageBreak())

# =============================================================================
# SECTION 4 — SHELF LIFE
# =============================================================================
story.extend(section_header("4", "Stability Kinetics & the Shelf-Life Recommendation"))

story.append(P(
    "Manufacturing wants to extend Gluconil's printed expiry beyond the current 18-month legacy estimate, "
    "citing four-month rural supply-chain lead times and return-and-destroy write-offs. Quality assurance "
    "wants any change to survive regulatory scrutiny. The CDSCO/pharmacopeia floor is an active-ingredient "
    "potency of 90.0% of labelled strength; below that, product is legally adulterated."
))

story.append(P("<b>4.1&nbsp;&nbsp;Two Kinetic Models</b>", "Body"))
story.append(P(
    "Chemical degradation of an active ingredient is rarely constant in absolute terms (zero-order); more "
    "commonly, the rate of loss is proportional to how much intact drug remains \u2014 first-order kinetics, "
    "which produces exponential decay. Both a simple linear model and an exponential decay model (fit by "
    "linearizing via the natural log of potency) were evaluated against 25 monthly readings from one "
    "commercial validation batch."
))
# story.extend(fig("stability_fit.png", caption="Figure 4.1 \u2014 Observed potency with both fitted models overlaid. "
#                                                "Over this 24-month window the two curves are visually almost "
#                                                "indistinguishable."))
story.append(stat_table([
    ["Model", "Equation", "R\u00b2", "RMSE", "90% crossing"],
    ["Linear", "Y = 99.6975 &minus; 0.7228 t", "0.98955", "0.5356", "13.42 months"],
    ["Exponential", "Y = 99.9724 &middot; e<super>&minus;0.007952t</super>", "0.98950", "0.5368", "13.21 months"],
], col_widths=[1.1*inch, 2.7*inch, 0.85*inch, 0.8*inch, 1.2*inch]))
story.append(P(
    "The two models are nearly indistinguishable in fit quality (R&sup2; differs in the fourth decimal place) "
    "and agree on the crossing point to within two weeks. This is not a coincidence: over a range where total "
    "potency loss is under 20%, an exponential curve is very well approximated by the linear (first-order "
    "Taylor) term of its own equation \u2014 the two models are mathematically close cousins at this scale, "
    "even though only the exponential form has a genuine mechanistic basis in reaction kinetics."
))

story.append(P("<b>4.2&nbsp;&nbsp;Residual Diagnostics</b>", "Body"))
# story.extend(fig("stability_resid.png", caption="Figure 4.2 \u2014 Residuals vs. time for both models. Neither shows "
#                                                  "a strong systematic curvature within the observed 24-month window, "
#                                                  "supporting either fit locally."))
story.append(P(
    "Because the two models cannot be separated on this batch's data alone, the choice between them should "
    "be made on mechanistic grounds rather than statistical ones: exponential (first-order) decay is the "
    "correct model of active-pharmaceutical-ingredient degradation chemistry, and is the only one of the two "
    "that extrapolates sensibly \u2014 a linear model would eventually predict negative potency, which is "
    "physically meaningless, whereas the exponential model asymptotically approaches zero."
))

story.append(P("<b>4.3&nbsp;&nbsp;The Point-Estimate Shelf Life</b>", "Body"))
story.append(P(
    "Solving either fitted equation for the month at which potency first reaches 90.0% gives a point estimate "
    "of <b>13.2&ndash;13.4 months</b>. Taken at face value, this already falls well short of both the current "
    "18-month printed expiry <i>and</i> manufacturing's hoped-for extension. But a point estimate from a "
    "single batch of 25 monthly readings carries real statistical uncertainty, and for a number that "
    "determines a legal expiry date, that uncertainty cannot be waved away."
))

story.append(callout_box(
    "Critical insight: the point estimate is the wrong number to certify a shelf life on",
    ["There are three meaningfully different questions one could ask of this regression, and they give three "
     "different answers:",
     "<b>(1) Where does the fitted average line cross 90%?</b> This is the point estimate above: 13.42 months. "
     "It assumes the fitted line is exactly the true degradation trend, with no allowance for sampling error.",
     "<b>(2) Where does the 95% confidence interval for the true mean trend cross 90%?</b> Accounting for "
     "uncertainty in <i>where the average line itself sits</i> (standard error of the regression), the lower "
     "confidence bound crosses 90% at <b>13.09 months</b>.",
     "<b>(3) Where does the 95% prediction interval for a single new future batch or carton cross 90%?</b> "
     "This is the actually relevant question for a printed expiry date, because a regulatory shelf life must "
     "hold for any individual unit sitting on a pharmacy shelf, not just for the long-run average across "
     "infinitely many batches. Accounting for both regression uncertainty <i>and</i> batch-to-batch/measurement "
     "variability, the lower prediction bound crosses 90% at only <b>11.79 months</b>."],
    bgcolor=LCORAL, bar_color=CORAL, icon="\u25c6"
))
# story.extend(fig("stability_pi.png", caption="Figure 4.3 \u2014 95% prediction interval (shaded) around the fitted "
#                                               "regression line. The statistically defensible shelf life is where the "
#                                               "<i>lower</i> edge of this band crosses the 90% floor \u2014 not where the "
#                                               "central fitted line does."))

story.append(P(
    "The practical consequence is stark. The point estimate (13.4 months) is already below the current "
    "18-month label. The number that should actually be used to set or defend a regulatory expiry date "
    "&mdash; the 95% prediction-interval bound &mdash; is lower still, at roughly <b>11.8 months</b>. "
    "Rounding down conservatively for a whole-month label, this analysis does not support an "
    "<i>extension</i> of shelf life at all; if anything, it suggests the current 18-month expiry may already "
    "be running past the point at which some units in the field fall below the legal potency floor."
))

story.append(callout_box(
    "This is a compliance flag, not a supply-chain optimisation",
    ["Manufacturing's request was framed as \"how far can we extend the shelf life?\" The honest answer from "
     "this validation batch is \"the data does not support extension, and quite possibly supports "
     "tightening.\" This should be escalated to quality assurance and regulatory affairs as a priority item, "
     "independent of the board's supply-chain discussion, with three concrete next steps: "
     "(i) do not proceed with any shelf-life extension on the strength of this single batch; "
     "(ii) commission confirmatory stability testing on at least two further production batches \u2014 "
     "ICH stability guidelines generally expect multiple primary batches before a shelf-life claim is "
     "finalised, and a one-batch estimate is not sufficient evidence either way; "
     "(iii) in the interim, review whether any currently distributed stock older than roughly 12 months "
     "warrants a proactive quality check, given what this batch's degradation curve implies."],
    bgcolor=LGOLD, bar_color=GOLD, icon="\u26a0"
))

story.append(P("<b>4.4&nbsp;&nbsp;Why Splines Would Be the Wrong Tool Here</b>", "Body"))
story.append(P(
    "A flexible, piecewise-smooth spline could fit these 25 points at least as well as either parametric "
    "model, and possibly better in-sample. But shelf-life estimation is fundamentally an extrapolation "
    "problem &mdash; the number the board needs (when does potency cross 90%) sits right at or beyond the "
    "edge of 24 months of observed data. Splines are locally fitted and have no constraint forcing them to "
    "behave sensibly outside the observed range: depending on the knot placement, an unconstrained spline can "
    "flatten, reverse direction, or oscillate just past the last data point, none of which has any grounding "
    "in degradation chemistry. The exponential model, by contrast, is anchored to a mechanistic assumption "
    "(first-order kinetics) that is known to hold for pharmaceutical degradation and therefore extrapolates "
    "predictably. For a number with direct regulatory and patient-safety consequences, a theoretically "
    "grounded parametric model that extrapolates safely is strongly preferable to a flexible curve that fits "
    "well only inside the data it was trained on."
))

story.append(KeepTogether([P("<b>4.5&nbsp;&nbsp;Recommendation</b>", "Body")] + bullets([
    "<b>Do not extend the printed shelf life beyond 18 months</b> \u2014 the data does not support this, and "
    "in fact suggests the opposite direction.",
    "<b>Adopt a provisional, statistically defensible shelf life of approximately 12 months</b> pending "
    "confirmatory testing, based on the 95% prediction-interval bound of 11.8 months rounded to a practical "
    "whole-month label with a small additional safety margin.",
    "<b>Escalate to QA/regulatory as a compliance matter</b>, independent of the supply-chain conversation, "
    "and commission at least two further batch stability studies before any label change is finalised.",
    "<b>Use the exponential (first-order kinetics) model, not a spline,</b> for any future extrapolation "
    "beyond the observed 24-month window.",
])))
story.append(PageBreak())

# =============================================================================
# SYNTHESIS
# =============================================================================
story.extend(section_header("\u2014", "Synthesis — From Instinct to Inference"))

story.append(P(
    "Menon's opening challenge was to strip out textbook jargon and deliver an objective narrative. Stripped "
    "to its essentials, that narrative is the same story told four times over: <b>every functional head's "
    "instinct was built on an assumption about shape</b> &mdash; that territory sales are roughly symmetric, "
    "that a mean settles a clinical safety question, that promotional payback is a straight line, that a "
    "round-number expiry date is conservative by default &mdash; and in every case, actually looking at the "
    "shape of the data was necessary before the number could be trusted."
))
story.append(stat_table([
    ["Shared failure mode", "Where it showed up", "The fix"],
    ["Treating a skewed distribution as if symmetric", "Territory sales (skew = 3.26)", "Median / trimmed mean; robust dispersion (MAD)"],
    ["Treating the mean as the whole story", "HbA1c reduction, tail risk", "Five-number summary; kurtosis; individual outlier review"],
    ["Assuming linearity without testing curvature", "Marketing spend vs. sales", "Log-linear model; AIC/BIC selection over R\u00b2 alone"],
    ["Trusting a point estimate for a regulatory number", "Shelf-life crossing point", "Prediction interval, not the fitted line, sets the safety margin"],
], col_widths=[2.5*inch, 2.0*inch, 2.4*inch]))

story.append(P(
    "Two of these four findings are directionally reassuring for MediGlucose (clinical efficacy holds up; "
    "the marketing budget increase is worth making, just not at the VP's assumed rate). One requires an "
    "operational correction rather than a crisis response (segment tender territories out of retail quotas). "
    "The fourth &mdash; shelf life &mdash; is the one finding in this report that should move up the agenda "
    "ahead of the board's original framing: it surfaces a potential compliance exposure that none of the four "
    "functional heads were looking for, because none of them asked the question in a way that would have "
    "revealed it."
))
story.append(callout_box(
    "A standing recommendation for the analytics function",
    ["Beyond the four specific decisions above, this exercise argues for three standing practices in "
     "MediGlucose's commercial and quality reporting: (1) pair every reported mean with a robust alternative "
     "(median or trimmed mean) whenever a distribution has known potential for extreme values \u2014 tender "
     "business, institutional bulk orders, and similar lumpy revenue sources; (2) require an information-"
     "criterion comparison (AIC/BIC), not R&sup2; alone, before adopting any linear ROI or payback assumption "
     "for capital allocation; (3) for any number that will support a regulatory claim or a legal specification "
     "(shelf life, dosing, safety thresholds), report the appropriate confidence or prediction interval "
     "alongside the point estimate, and let the interval \u2014 not the point estimate \u2014 govern the "
     "final recommendation."],
    bgcolor=LGREY, bar_color=NAVY, icon="\u2139"
))
story.append(PageBreak())

# =============================================================================
# APPENDIX
# =============================================================================
story.extend(section_header("\u2014", "Appendix — Methods, Formulae & Data Notes"))

story.append(P("<b>A.1&nbsp;&nbsp;Summary Statistics of the Four Source Datasets</b>", "Body"))
story.append(stat_table([
    ["Dataset", "n", "Key variable", "Mean", "Median", "SD", "Min", "Max"],
    ["Territory sales", "120", "Units sold / month", "830.0", "687.0", "668.1", "195", "3,792"],
    ["HbA1c trial", "120", "HbA1c reduction (pp)", "1.278", "1.280", "0.414", "&minus;0.24", "2.63"],
    ["HbA1c trial", "120", "Age (years)", "56.52", "56.0", "11.89", "23", "84"],
    ["Marketing / sales", "120", "Spend (&#8377; lakh)", "13.54", "14.21", "6.82", "2.06", "24.94"],
    ["Marketing / sales", "120", "Units sold", "1,637.4", "1,723.5", "406.6", "508", "2,364"],
    ["Stability", "25", "Potency (%)", "91.02", "90.86", "5.35", "82.17", "99.82"],
], col_widths=[1.2*inch, 0.4*inch, 1.5*inch, 0.75*inch, 0.75*inch, 0.6*inch, 0.6*inch, 0.7*inch]))

story.append(P("<b>A.2&nbsp;&nbsp;Formulae Referenced in This Report</b>", "Body"))
story.extend(bullets([
    "<b>Freedman&ndash;Diaconis bin width:</b> h = 2&middot;IQR&middot;n<super>&minus;1/3</super>, chosen over "
    "Sturges'/Scott's rules because it scales with spread of the middle 50% rather than the (outlier-sensitive) "
    "standard deviation.",
    "<b>Trimmed / Winsorized mean:</b> trimmed mean drops the top and bottom p% of ordered values before "
    "averaging; Winsorized mean instead caps them at the p-th/1&minus;p-th percentile value and retains them.",
    "<b>Tukey fences:</b> soft = [Q1&minus;1.5&middot;IQR, Q3+1.5&middot;IQR]; hard = [Q1&minus;3&middot;IQR, "
    "Q3+3&middot;IQR].",
    "<b>Skewness / kurtosis:</b> g<sub rise=1>1</sub> = m<sub rise=1>3</sub>/m<sub rise=1>2</sub><super>3/2</super>; "
    "excess kurtosis = m<sub rise=1>4</sub>/m<sub rise=1>2</sub><super>2</super> &minus; 3, where m<sub rise=1>k</sub> "
    "is the k-th central sample moment.",
    "<b>Chebyshev's inequality:</b> P(|X&minus;&mu;| &ge; k&sigma;) &le; 1/k&sup2; for any distribution with "
    "finite variance; used here as a distribution-free lower bound, contrasted with the empirical proportion.",
    "<b>Coefficient of determination:</b> R&sup2; = 1 &minus; SS<sub rise=1>res</sub>/SS<sub rise=1>tot</sub>; "
    "for simple linear regression, R&sup2; = r&sup2; where r is the Pearson correlation.",
    "<b>Log-linear and power-law linearization:</b> Y = a+b&middot;ln(X) fit directly by OLS on ln(X); "
    "Y = a&middot;X<super>b</super> fit by OLS of ln(Y) on ln(X), then exponentiating the intercept.",
    "<b>AIC / BIC:</b> AIC = n&middot;ln(RSS/n) + 2k; BIC = n&middot;ln(RSS/n) + k&middot;ln(n), where k is the "
    "number of estimated parameters and RSS the residual sum of squares; lower values indicate a better "
    "complexity-adjusted fit.",
    "<b>Exponential decay linearization:</b> Y = A&middot;e<super>&minus;kt</super> fit by OLS of ln(Y) on t, "
    "giving ln(A) as intercept and &minus;k as slope.",
    "<b>Prediction interval vs. confidence interval:</b> a 95% CI for the mean response reflects uncertainty in "
    "the fitted regression line itself; a 95% prediction interval additionally incorporates the residual "
    "variance of a single new observation around that line, and is always wider &mdash; it is the appropriate "
    "interval when the claim must hold for an individual future unit rather than a long-run average.",
]))

story.append(P("<b>A.3&nbsp;&nbsp;Limitations &amp; Caveats</b>", "Body"))
story.extend(bullets([
    "The marketing spend-sales relationship is observational, not experimental: territories with structurally "
    "higher potential may simply receive larger promotional budgets (reverse causation / confounding by "
    "territory size), so the fitted curves describe association, not a guaranteed causal payback.",
    "The shelf-life analysis rests on a single validation batch (n=25 monthly readings). Regulatory shelf-life "
    "claims typically require multiple primary batches; the 11.8&ndash;13.4 month range in this report should "
    "be treated as a strong preliminary signal demanding confirmatory testing, not a final label value.",
    "The clinical trial is a post-marketing surveillance cohort, not a randomised controlled trial; the "
    "absence of an age-efficacy correlation and the outlier flags are statistical observations that require "
    "clinical, not purely statistical, adjudication before any patient-level action is taken.",
    "The territory-tender hypothesis in Section 1.6 is inferred from the shape of the sales distribution "
    "alone; MediGlucose's own institutional sales records should be used to confirm which of the five flagged "
    "territories actually carry hospital tender business before quotas are formally restructured.",
]))

story.append(Spacer(1, 14))
story.append(hr(color=colors.HexColor("#c9d3da"), thickness=0.8, sa=8))
story.append(Paragraph("End of report.", styles["Caption"]))

# =============================================================================
# BUILD
# =============================================================================
doc.build(story)
print("PDF built successfully.")