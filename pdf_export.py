from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from db import get_conn

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="MyTitle", fontSize=14, leading=16, textColor=colors.HexColor("#2c3e50"), spaceAfter=6))
styles.add(ParagraphStyle(name="Cell", fontSize=8, leading=10))
styles.add(ParagraphStyle(name="Header", fontSize=9, leading=11, textColor=colors.white))
def P(t): return Paragraph(str(t), styles["Cell"])

def on_page(c: Canvas, doc):
    c.setFont("Helvetica", 7)
    c.drawRightString(200*mm, 10*mm, f"Pagina {c.getPageNumber()}")

def build_mealprep_pdf(filename, week:int):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("""SELECT p.day, p.slot, p.portions, r.title, r.steps, r.ref_link
                   FROM plan p JOIN recipes r ON p.recipe_id=r.id
                   WHERE p.week=? ORDER BY p.day, p.slot""",(week,))
    rows = cur.fetchall(); conn.close()

    header = ["Giorno","Pasto/Ricetta","Porz.","Preparazione","Link"]
    data = [[Paragraph(h, styles["Header"]) for h in header]]
    for r in rows:
        data.append([P(f"Giorno {r['day']}"),
                     P(f"{r['slot']} – {r['title']}"),
                     P(f"x{r['portions']}"),
                     P((r['steps'] or '—').strip()),
                     P(r['ref_link'] or '—')])

    doc = SimpleDocTemplate(filename, pagesize=A4,
                            leftMargin=12*mm, rightMargin=12*mm,
                            topMargin=12*mm, bottomMargin=14*mm)
    flow = [Paragraph(f"📦 Meal Prep – Settimana {week}", styles["MyTitle"]), Spacer(1,4)]
    table = Table(data, colWidths=[35, 140, 30, 210, 55], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#2c3e50")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("ALIGN", (2,1), (2,-1), "CENTER"),
        ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("LEFTPADDING", (0,0), (-1,-1), 3),
        ("RIGHTPADDING", (0,0), (-1,-1), 3),
        ("TOPPADDING", (0,0), (-1,-1), 2),
        ("BOTTOMPADDING", (0,0), (-1,-1), 2),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, colors.HexColor("#f2f2f2")]),
    ]))
    flow.append(table)
    doc.build(flow, onFirstPage=on_page, onLaterPages=on_page)
    return filename
