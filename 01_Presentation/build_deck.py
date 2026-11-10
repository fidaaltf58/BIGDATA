"""Génère la présentation du projet Big Data (python build_deck.py)."""
import json
from pathlib import Path

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

HERE = Path(__file__).resolve().parent
S = json.load(open(HERE.parent / "02_Dataset" / "stats.json", encoding="utf-8"))

# ---------- Palette "Océan" (hôtellerie balnéaire) ----------
NAVY = RGBColor(0x0B, 0x3C, 0x49)
TEAL = RGBColor(0x1F, 0x8A, 0x8A)
SEA = RGBColor(0xD9, 0xEF, 0xEE)
CORAL = RGBColor(0xF2, 0x6B, 0x4F)
INK = RGBColor(0x1E, 0x29, 0x33)
MUTED = RGBColor(0x5B, 0x6B, 0x77)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT = RGBColor(0xF4, 0xF8, 0xF9)
HEAD, BODY = "Cambria", "Calibri"

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]
W = 13.333


def bg(slide, color):
    f = slide.background.fill
    f.solid()
    f.fore_color.rgb = color


def text(slide, x, y, w, h, content, size=16, color=INK, bold=False, font=BODY, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, italic=False, name=None, spacing=6):
    """content: str ou liste de str / (str, dict) ; une entrée = un paragraphe."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    if name:
        tb.name = name
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0)
    tf.margin_top = tf.margin_bottom = Inches(0.02)
    items = content if isinstance(content, list) else [content]
    for i, it in enumerate(items):
        t, o = (it, {}) if isinstance(it, str) else it
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = o.get("align", align)
        p.space_after = Pt(o.get("spacing", spacing))
        r = p.add_run()
        r.text = ("•  " + t) if o.get("bullet") else t
        f = r.font
        f.size = Pt(o.get("size", size))
        f.bold = o.get("bold", bold)
        f.italic = o.get("italic", italic)
        f.name = o.get("font", font)
        f.color.rgb = o.get("color", color)
    return tb


def box(slide, x, y, w, h, fill, shape=MSO_SHAPE.ROUNDED_RECTANGLE, line=None, radius=0.08, shadow=False):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(1.25)
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = radius
    if not shadow:
        s.shadow.inherit = False
    return s


def badge(slide, x, y, d, label, fill=TEAL, color=WHITE, size=16):
    c = box(slide, x, y, d, d, fill, shape=MSO_SHAPE.OVAL)
    tf = c.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Inches(0)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = label
    r.font.size, r.font.bold, r.font.name, r.font.color.rgb = Pt(size), True, BODY, color
    return c


def title(slide, t, kicker=None, dark=False):
    if kicker:
        text(slide, 0.6, 0.38, 10, 0.35, kicker.upper(), size=12, bold=True, color=CORAL)
    text(slide, 0.6, 0.68, 12.1, 0.8, t, size=34, bold=True, font=HEAD, color=WHITE if dark else NAVY)


def footer(slide, n, dark=False):
    c = RGBColor(0x9F, 0xC4, 0xC6) if dark else MUTED
    text(slide, 0.6, 7.02, 8, 0.3, "Projet Big Data — Hotel Booking Demand  ·  Évaluation mi-parcours",
         size=10, color=c)
    text(slide, 11.73, 7.02, 1, 0.3, str(n), size=10, color=c, align=PP_ALIGN.RIGHT)


def arrow(slide, x1, y1, x2, y2, color=TEAL, width=2):
    a = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    a.line.color.rgb = color
    a.line.width = Pt(width)
    ln = a.line._get_or_add_ln()
    from pptx.oxml.ns import qn
    from lxml import etree
    tail = etree.SubElement(ln, qn("a:tailEnd"))
    tail.set("type", "triangle")
    return a


def style_chart(chart, colors, legend=False):
    chart.has_title = False
    chart.has_legend = legend
    chart.font.size = Pt(12)
    chart.font.name = BODY
    chart.font.color.rgb = MUTED
    plot = chart.plots[0]
    plot.gap_width = 60
    plot.has_data_labels = True
    dl = plot.data_labels
    dl.font.size, dl.font.bold, dl.font.color.rgb = Pt(12), True, INK
    dl.number_format, dl.number_format_is_linked = '0"%"', False
    dl.position = XL_LABEL_POSITION.OUTSIDE_END
    va = chart.value_axis
    va.visible = False
    va.has_major_gridlines = False
    va.maximum_scale = 100
    chart.category_axis.format.line.color.rgb = RGBColor(0xC8, 0xD3, 0xD8)
    chart.category_axis.tick_labels.font.size = Pt(12)
    for i, pt in enumerate(plot.series[0].points):
        pt.format.fill.solid()
        pt.format.fill.fore_color.rgb = colors[i] if isinstance(colors, list) else colors


n = 0


def new(dark=False):
    global n
    n += 1
    s = prs.slides.add_slide(BLANK)
    bg(s, NAVY if dark else WHITE)
    return s


# =================== 1. TITRE ===================
s = new(dark=True)
box(s, 8.9, -1.2, 6.2, 6.2, TEAL, shape=MSO_SHAPE.OVAL)
box(s, 10.6, 3.9, 4.2, 4.2, CORAL, shape=MSO_SHAPE.OVAL)
text(s, 0.8, 1.2, 8, 0.4, "PROJET BIG DATA  ·  ÉVALUATION MI-PARCOURS", size=14, bold=True, color=CORAL)
text(s, 0.8, 1.75, 8.3, 2.4, "Big Data & hôtellerie : anticiper les annulations et optimiser l'occupation",
     size=40, bold=True, font=HEAD, color=WHITE)
text(s, 0.8, 4.25, 7.8, 0.9, "Étude de cas sur 119 390 réservations hôtelières — architecture Kafka, Flume, Sqoop & HDFS",
     size=18, color=RGBColor(0xCF, 0xE6, 0xE6))
text(s, 0.8, 5.65, 7.5, 0.9, ["Groupe : Nom Prénom 1  ·  Nom Prénom 2  ·  Nom Prénom 3",
                              "CIC — Module Big Data  ·  Novembre 2026"], size=14, color=WHITE)
s.notes_slide.notes_text_frame.text = (
    "(30 s) Présentation du groupe. Thème : l'hôtellerie, secteur où les annulations représentent "
    "une perte majeure de revenus. Plan : partie générale (4 questions), cas d'étude et dataset, "
    "architecture et outils, démonstration.")

# =================== 2. SOMMAIRE ===================
s = new()
title(s, "Déroulé de la présentation", "Sommaire")
parts = [("01", "Partie générale", "Pourquoi, où et comment le Big Data est utilisé dans l'hôtellerie — et ses étapes"),
         ("02", "Problématique & dataset", "Le cas Hotel Booking Demand : 119 390 réservations, 32 variables"),
         ("03", "Architecture & outils", "Kafka, Flume et Sqoop autour d'un Data Lake HDFS"),
         ("04", "Démonstration", "Installation, exécution des trois flux et traces techniques")]
for i, (num, t, d) in enumerate(parts):
    x = 0.6 + i * 3.09
    box(s, x, 2.0, 2.85, 4.3, LIGHT)
    text(s, x + 0.3, 2.3, 2.3, 0.9, num, size=44, bold=True, font=HEAD, color=CORAL)
    text(s, x + 0.3, 3.45, 2.3, 0.8, t, size=20, bold=True, color=NAVY)
    text(s, x + 0.3, 4.35, 2.3, 1.8, d, size=14, color=MUTED)
footer(s, n)
s.notes_slide.notes_text_frame.text = "(20 s) Les 4 parties, conformes à la description du projet."

# =================== 3. POURQUOI ===================
s = new()
title(s, "Pourquoi recourir au Big Data dans l'hôtellerie ?", "Partie générale · 1")
stats = [(f"{S['total']:,}".replace(",", " "), "réservations à analyser\n(2 hôtels, 3 saisons)"),
         (f"{S['cancel_rate']:.0f} %", "des réservations\nsont annulées"),
         (f"{S['lost_revenue'] / 1e6:.1f} M€".replace(".", ","), "de chiffre d'affaires\nannulé sur la période")]
for i, (v, l) in enumerate(stats):
    x = 0.6 + i * 2.55
    text(s, x, 1.95, 2.4, 1.0, v, size=40, bold=True, font=HEAD, color=CORAL if i == 1 else NAVY)
    text(s, x, 2.95, 2.4, 0.9, l, size=14, color=MUTED)
text(s, 0.6, 4.25, 7.3, 0.4, "Les 3 V appliqués à un hôtel", size=20, bold=True, color=NAVY)
vs = [("Volume", "PMS, OTA (Booking, Expedia), site web, avis clients : des millions d'événements"),
      ("Vélocité", "réservations, annulations et prix changent en continu, 24 h/24"),
      ("Variété", "tables SQL, logs web, flux JSON, textes d'avis, données météo")]
for i, (k, d) in enumerate(vs):
    y = 4.8 + i * 0.68
    badge(s, 0.6, y, 0.45, k[0], fill=TEAL, size=16)
    text(s, 1.25, y + 0.04, 6.7, 0.5, [(k + " — ", {}),], size=15, bold=True, color=INK)
    s.shapes[-1].text_frame.paragraphs[0].add_run().text = d
    r = s.shapes[-1].text_frame.paragraphs[0].runs[1]
    r.font.size, r.font.name, r.font.color.rgb, r.font.bold = Pt(15), BODY, INK, False
box(s, 8.4, 1.95, 4.33, 4.75, NAVY)
text(s, 8.75, 2.25, 3.7, 0.4, "LIMITE DES OUTILS CLASSIQUES", size=12, bold=True, color=CORAL)
text(s, 8.75, 2.75, 3.7, 3.8, [
    ("Un SGBD unique et des fichiers Excel ne permettent pas :", {"spacing": 12}),
    ("de croiser réservations, logs web et flux temps réel", {"bullet": True}),
    ("de réagir en temps réel à une vague d'annulations", {"bullet": True}),
    ("de stocker l'historique complet à faible coût", {"bullet": True}),
    ("de passer à l'échelle d'une chaîne d'hôtels", {"bullet": True})], size=15, color=WHITE)
footer(s, n)
s.notes_slide.notes_text_frame.text = (
    "(1 min) Chiffres calculés sur notre dataset : 37 % d'annulations, 16,7 M€ de CA annulé. "
    "L'hôtel doit croiser des sources hétérogènes, rapides et volumineuses : c'est la définition des 3V.")

# =================== 4. À QUEL NIVEAU ===================
s = new()
title(s, "À quel niveau le Big Data est-il utilisé ?", "Partie générale · 2")
lv = [("€", "Revenue management", "Tarification dynamique, prévision de la demande, gestion du surbooking selon le risque d'annulation"),
      ("M", "Marketing & distribution", "Segmentation clients, choix des canaux (direct vs OTA), campagnes ciblées, fidélisation"),
      ("O", "Opérations", "Planning du personnel, ménage, restauration et stocks ajustés à l'occupation prévue"),
      ("C", "Expérience client", "Personnalisation du séjour, analyse des avis, recommandations d'offres et de services")]
for i, (ic, t, d) in enumerate(lv):
    x = 0.6 + (i % 2) * 6.17
    y = 1.95 + (i // 2) * 2.45
    box(s, x, y, 5.93, 2.2, LIGHT)
    badge(s, x + 0.35, y + 0.4, 0.75, ic, fill=CORAL if i == 0 else TEAL, size=22)
    text(s, x + 1.4, y + 0.38, 4.3, 0.5, t, size=20, bold=True, color=NAVY)
    text(s, x + 1.4, y + 0.95, 4.3, 1.2, d, size=15, color=INK)
footer(s, n)
s.notes_slide.notes_text_frame.text = (
    "(1 min) Le Big Data intervient du niveau stratégique (prix, distribution) au niveau opérationnel "
    "(personnel, stocks) et relationnel (client). Notre projet cible le revenue management.")

# =================== 5. COMMENT ===================
s = new()
title(s, "Comment le Big Data a été utilisé : exemples", "Partie générale · 3")
ex = [("Marriott", "Revenue management", "Systèmes de tarification qui ajustent les prix selon la demande, les événements locaux et l'historique de réservations."),
      ("Booking.com", "Expérimentation massive", "Des centaines de tests A/B menés en parallèle sur des flux d'événements utilisateurs pour optimiser la conversion."),
      ("Airbnb", "Smart Pricing", "Modèles de machine learning qui suggèrent un prix par nuit à partir de la saisonnalité, du quartier et de la demande.")]
for i, (co, t, d) in enumerate(ex):
    x = 0.6 + i * 4.1
    box(s, x, 1.95, 3.85, 3.6, LIGHT)
    text(s, x + 0.35, 2.25, 3.2, 0.55, co, size=24, bold=True, font=HEAD, color=NAVY)
    text(s, x + 0.35, 2.85, 3.2, 0.4, t.upper(), size=12, bold=True, color=CORAL)
    text(s, x + 0.35, 3.35, 3.2, 2.1, d, size=15, color=INK)
box(s, 0.6, 5.8, 12.13, 0.95, NAVY)
text(s, 0.95, 5.8, 11.5, 0.95, "Point commun : collecte continue, stockage massif, modèles prédictifs, décision automatisée",
     size=17, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
footer(s, n)
s.notes_slide.notes_text_frame.text = (
    "(1 min) Trois cas publics. Insister sur le schéma commun que nous reproduisons à petite échelle.")

# =================== 6. ÉTAPES ===================
s = new()
title(s, "Les différentes étapes d'un projet Big Data", "Partie générale · 4")
steps = [("Collecte", "Sources : PMS, site web, OTA"), ("Ingestion", "Sqoop · Flume · Kafka"),
         ("Stockage", "Data Lake HDFS"), ("Traitement", "Hive / Spark"),
         ("Analyse", "KPI, modèle d'annulation"), ("Décision", "Tableaux de bord, alertes")]
for i, (t, d) in enumerate(steps):
    x = 0.6 + i * 2.06
    hl = i == 1
    box(s, x, 2.3, 1.8, 2.6, NAVY if hl else LIGHT)
    text(s, x + 0.2, 2.5, 1.4, 0.7, f"{i + 1:02d}", size=30, bold=True, font=HEAD, color=CORAL)
    text(s, x + 0.2, 3.25, 1.45, 0.5, t, size=18, bold=True, color=WHITE if hl else NAVY)
    text(s, x + 0.2, 3.8, 1.45, 1.0, d, size=14, color=WHITE if hl else MUTED)
    if i < 5:
        arrow(s, x + 1.83, 3.6, x + 2.03, 3.6)
text(s, 0.6, 5.35, 12.1, 1.2, [
    ("Focus de l'évaluation mi-parcours : l'étape 02, l'ingestion, avec les trois outils recommandés.", {"bold": True, "color": NAVY}),
    ("Les étapes 04 à 06 (Hive/Spark, modèle prédictif, tableau de bord) seront développées pour l'évaluation finale.", {"color": MUTED})],
    size=16)
footer(s, n)
s.notes_slide.notes_text_frame.text = "(1 min) Chaîne de valeur de la donnée ; notre démonstration couvre l'ingestion et le stockage."

# =================== 7. PROBLÉMATIQUE ===================
s = new(dark=True)
text(s, 0.8, 0.9, 8, 0.4, "PARTIE SPÉCIFIQUE · PROBLÉMATIQUE", size=14, bold=True, color=CORAL)
text(s, 0.8, 1.5, 11.5, 2.0, "Comment un hôtel peut-il anticiper les annulations et ajuster ses décisions en temps réel grâce à une architecture Big Data ?",
     size=34, bold=True, font=HEAD, color=WHITE)
obj = [("Centraliser", "les réservations (SGBDR), les logs du site web et le flux temps réel dans un Data Lake"),
       ("Détecter", "en temps réel les réservations à fort risque d'annulation"),
       ("Mesurer", "les KPI mensuels (taux d'annulation, ADR, nuitées, CA) et les renvoyer au SI de l'hôtel")]
for i, (k, d) in enumerate(obj):
    x = 0.8 + i * 4.0
    badge(s, x, 4.2, 0.6, str(i + 1), fill=CORAL, size=18)
    text(s, x, 5.0, 3.6, 0.45, k, size=20, bold=True, color=WHITE)
    text(s, x, 5.5, 3.6, 1.3, d, size=15, color=RGBColor(0xCF, 0xE6, 0xE6))
footer(s, n, dark=True)
s.notes_slide.notes_text_frame.text = "(45 s) Énoncer la problématique et les 3 objectifs, chacun lié à un outil."

# =================== 8. DATASET ===================
s = new()
title(s, "Le dataset : Hotel Booking Demand", "Partie spécifique · Données")
facts = [(f"{S['total']:,}".replace(",", " "), "lignes"), ("32", "variables"), (str(S["countries"]), "pays d'origine"),
         ("2015–17", "juil. 2015 → août 2017")]
for i, (v, l) in enumerate(facts):
    x = 0.6 + i * 1.95
    box(s, x, 1.95, 1.8, 1.45, LIGHT)
    text(s, x + 0.2, 2.1, 1.5, 0.6, v, size=26, bold=True, font=HEAD, color=NAVY)
    text(s, x + 0.2, 2.8, 1.5, 0.5, l, size=13, color=MUTED)
text(s, 0.6, 3.75, 7.6, 3.0, [
    ("Source : Antonio, Almeida & Nunes (2019), « Hotel booking demand datasets », Data in Brief — publié sur Kaggle.", {"spacing": 10}),
    ("Deux hôtels réels au Portugal : un City Hotel (Lisbonne) et un Resort Hotel (Algarve).", {"spacing": 10}),
    ("Fichier : hotel_bookings.csv (16 Mo), données anonymisées, cible is_canceled.", {"spacing": 10}),
    ("Compléments générés par le groupe : web_access.log (logs du site de réservation, pour Flume) et kpi_monthly.csv (pour l'export Sqoop).", {})],
    size=15, color=INK)
box(s, 8.55, 1.95, 4.18, 4.8, NAVY)
text(s, 8.9, 2.2, 3.6, 0.4, "FAMILLES DE VARIABLES", size=12, bold=True, color=CORAL)
groups = [("Séjour", "dates d'arrivée, nuits semaine / week-end"), ("Client", "adultes, enfants, pays, fidélité"),
          ("Commercial", "segment, canal, agent, type de dépôt"), ("Chambre", "type réservé / attribué, repas"),
          ("Prix", "ADR (prix moyen par nuit)"), ("Statut", "annulée, check-out, no-show")]
text(s, 8.9, 2.7, 3.6, 4.0, [(f"{g} — {d}", {"spacing": 9}) for g, d in groups], size=14, color=WHITE)
footer(s, n)
s.notes_slide.notes_text_frame.text = (
    "(1 min) Dataset choisi en fonction du domaine hôtelier. Réel, volumineux, riche. "
    "Nous l'avons chargé dans MySQL pour simuler le PMS de l'hôtel.")

# =================== 9. INSIGHTS ===================
s = new()
title(s, "Premiers constats : où se concentrent les annulations", "Partie spécifique · Exploration")
cd = CategoryChartData()
seg_order = ["Groups", "Online TA", "Offline TA/TO", "Corporate", "Direct"]
cd.categories = seg_order
cd.add_series("Taux d'annulation", [S["by_segment"][k][1] for k in seg_order])
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.6), Inches(2.35), Inches(6.0), Inches(3.6), cd)
style_chart(gf.chart, [CORAL, TEAL, TEAL, TEAL, TEAL])
text(s, 0.6, 1.85, 6, 0.4, "Taux d'annulation par segment de marché", size=16, bold=True, color=NAVY)
cd2 = CategoryChartData()
lead_order = ["0-30 j", "31-90 j", "91-180 j", "> 180 j"]
cd2.categories = lead_order
cd2.add_series("Taux d'annulation", [S["lead"][k][1] for k in lead_order])
gf2 = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(6.9), Inches(2.35), Inches(5.8), Inches(3.6), cd2)
style_chart(gf2.chart, [TEAL, TEAL, TEAL, CORAL])
text(s, 6.9, 1.85, 5.8, 0.4, "Taux d'annulation selon le délai de réservation", size=16, bold=True, color=NAVY)
box(s, 0.6, 6.1, 12.13, 0.75, SEA)
text(s, 0.9, 6.1, 11.6, 0.75,
     (f"City Hotel : {S['by_hotel']['City Hotel'][1]} % d'annulations contre {S['by_hotel']['Resort Hotel'][1]} % au Resort  ·  "
     f"Dépôt « Non Refund » : {S['by_deposit']['Non Refund'][1]} % annulées (anomalie à investiguer)").replace(".", ","),
     size=15, bold=True, color=NAVY, anchor=MSO_ANCHOR.MIDDLE)
footer(s, n)
s.notes_slide.notes_text_frame.text = (
    "(1 min) Les groupes et les réservations anticipées (> 180 j) sont les plus annulés. "
    "Ces constats alimentent les règles d'alerte du consommateur Kafka.")

# =================== 10. ARCHITECTURE ===================
s = new()
title(s, "Architecture Big Data proposée", "Partie spécifique · Solution")
col = lambda x, y, w, h, t, sub, fill=LIGHT, tc=NAVY, sc=MUTED: (
    box(s, x, y, w, h, fill),
    text(s, x + 0.15, y + 0.1, w - 0.3, 0.4, t, size=15, bold=True, color=tc, align=PP_ALIGN.CENTER),
    text(s, x + 0.15, y + 0.5, w - 0.3, h - 0.55, sub, size=12, color=sc, align=PP_ALIGN.CENTER))
text(s, 0.6, 1.7, 2.6, 0.3, "SOURCES", size=12, bold=True, color=CORAL)
text(s, 3.95, 1.7, 2.6, 0.3, "INGESTION", size=12, bold=True, color=CORAL)
text(s, 7.3, 1.7, 2.6, 0.3, "STOCKAGE", size=12, bold=True, color=CORAL)
text(s, 10.25, 1.7, 2.6, 0.3, "TRAITEMENT & USAGE", size=12, bold=True, color=CORAL)
rows = [(2.1, "PMS · MySQL", "table bookings\n119 390 lignes", "Sqoop import", "SGBDR → HDFS, 4 mappers"),
        (3.7, "Site web", "logs Apache\nweb_access.log", "Flume", "spooldir → file channel → HDFS"),
        (5.3, "Réservations live", "événements de réservation", "Kafka", "topic hotel-bookings, 3 partitions")]
for y, src, sd, tool, td in rows:
    col(0.6, y, 2.6, 1.3, src, sd)
    col(3.95, y, 2.75, 1.3, tool, td, fill=NAVY, tc=WHITE, sc=RGBColor(0xCF, 0xE6, 0xE6))
    arrow(s, 3.25, y + 0.65, 3.9, y + 0.65)
    arrow(s, 6.75, y + 0.65, 7.25, y + 0.65)
box(s, 7.3, 2.1, 2.45, 4.5, TEAL)
text(s, 7.45, 2.35, 2.15, 0.5, "HDFS", size=24, bold=True, font=HEAD, color=WHITE, align=PP_ALIGN.CENTER)
text(s, 7.45, 3.0, 2.15, 3.4, ["Data Lake", "/data/hotel/bookings", "/data/hotel/weblogs", "/data/hotel/stream",
                               "/data/hotel/kpi"], size=12, color=WHITE, align=PP_ALIGN.CENTER, spacing=8)
col(10.25, 2.1, 2.48, 1.3, "Hive / Spark", "nettoyage, KPI,\nmodèle prédictif")
col(10.25, 3.7, 2.48, 1.3, "Sqoop export", "KPI → MySQL\n(table kpi_monthly)", fill=NAVY, tc=WHITE, sc=RGBColor(0xCF, 0xE6, 0xE6))
col(10.25, 5.3, 2.48, 1.3, "Alertes temps réel", "consommateur Kafka\nrisque d'annulation", fill=SEA)
arrow(s, 9.8, 2.75, 10.2, 2.75)
arrow(s, 9.8, 4.35, 10.2, 4.35)
arrow(s, 6.75, 6.25, 10.2, 6.25, color=CORAL)
text(s, 7.45, 5.8, 2.15, 0.35, "flux direct temps réel", size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
text(s, 0.6, 6.72, 12, 0.3, "Flume (source Kafka) archive aussi le flux temps réel dans HDFS : l'analyse batch dispose de tout l'historique.",
     size=12, italic=True, color=MUTED)
footer(s, n)
s.notes_slide.notes_text_frame.text = (
    "(1 min 30) Trois chemins d'ingestion, un outil par type de source : Sqoop pour le relationnel, "
    "Flume pour les fichiers de logs, Kafka pour le temps réel. HDFS centralise. "
    "Sqoop export renvoie les KPI au SI. Le flux Kafka alimente des alertes et est archivé par Flume.")

# =================== 11-13. OUTILS ===================
tools = [
    ("Apache Kafka", "Outil 1 · Temps réel",
     "Plateforme distribuée de streaming : des producteurs publient des messages dans des topics partitionnés et répliqués, lus par des consommateurs indépendants.",
     ["Producteur : rejoue le CSV comme un flux de réservations (5 / s)",
      "Topic hotel-bookings : 3 partitions, mode KRaft (sans ZooKeeper)",
      "Consommateurs : console, alertes Python, Flume (archivage)"],
     ["Télécharger Kafka 3.7 (ou image apache/kafka:3.7.0)", "Configurer server.properties (KRaft)",
      "kafka-storage.sh format, puis kafka-server-start.sh", "kafka-topics.sh --create --topic hotel-bookings"],
     "kafka-console-producer.sh --bootstrap-server kafka:9092 --topic hotel-bookings"),
    ("Apache Flume", "Outil 2 · Fichiers de logs",
     "Service distribué de collecte et d'agrégation de logs. Un agent = Source → Channel → Sink, configuré par un simple fichier .conf.",
     ["Source spooldir : chaque fichier de log déposé est ingéré",
      "Channel file : durable, aucune perte en cas de redémarrage",
      "Sink HDFS : partitionnement par date (dt=AAAA-MM-JJ)"],
     ["Télécharger Flume 1.11.0 (archive.apache.org)", "Définir JAVA_HOME et HADOOP_HOME",
      "Retirer l'ancienne guava-*.jar (conflit Hadoop 3)", "Écrire weblogs-hdfs.conf, lancer flume-ng agent"],
     "flume-ng agent -n weblogs -f weblogs-hdfs.conf"),
    ("Apache Sqoop", "Outil 3 · SGBDR ↔ HDFS",
     "Outil de transfert en masse entre bases relationnelles et Hadoop. Il génère des jobs MapReduce parallèles pour l'import et l'export.",
     ["Import : table bookings MySQL → HDFS (4 mappers, split sur la clé)",
      "Import filtré (--where) et incrémental (--incremental append)",
      "Export : KPI mensuels HDFS → table MySQL kpi_monthly"],
     ["Télécharger Sqoop 1.4.7 + driver mysql-connector-j", "Configurer sqoop-env.sh (HADOOP_HOME)",
      "Ajouter commons-lang-2.6.jar (Hadoop 3)", "Tester : sqoop list-databases"],
     "sqoop import --connect jdbc:mysql://mysql/hotel_db --table bookings --target-dir /data/hotel/bookings -m 4"),
]
for name, kick, role, usage, install, cmd in tools:
    s = new()
    title(s, name, kick)
    text(s, 0.6, 1.6, 12.1, 0.8, role, size=17, color=INK)
    box(s, 0.6, 2.6, 5.95, 3.35, LIGHT)
    text(s, 0.95, 2.85, 5.3, 0.4, "DANS NOTRE CAS D'USAGE", size=12, bold=True, color=CORAL)
    for i, u in enumerate(usage):
        badge(s, 0.95, 3.4 + i * 0.82, 0.42, str(i + 1), size=14)
        text(s, 1.55, 3.42 + i * 0.82, 4.75, 0.75, u, size=15, color=INK)
    box(s, 6.78, 2.6, 5.95, 3.35, NAVY)
    text(s, 7.13, 2.85, 5.3, 0.4, "ÉTAPES D'INSTALLATION", size=12, bold=True, color=CORAL)
    for i, st in enumerate(install):
        text(s, 7.13, 3.38 + i * 0.6, 0.45, 0.5, f"{i + 1}.", size=15, bold=True, color=CORAL)
        text(s, 7.58, 3.38 + i * 0.6, 4.9, 0.55, st, size=15, color=WHITE)
    box(s, 0.6, 6.15, 12.13, 0.65, INK)
    text(s, 0.9, 6.15, 11.6, 0.65, "$ " + cmd, size=13, font="Courier New", color=RGBColor(0x9F, 0xE8, 0xD8),
         anchor=MSO_ANCHOR.MIDDLE)
    footer(s, n)
    s.notes_slide.notes_text_frame.text = (
        f"(1 min) Rôle de {name}, son utilisation dans notre cas, puis les étapes d'installation. "
        "Les commandes complètes sont dans l'annexe et le dossier 03_Demo.")

# =================== 14. DÉMO ===================
s = new()
title(s, "Démonstration technique", "Démo · 4 minutes")
text(s, 0.6, 1.6, 12.1, 0.6, "Environnement : Docker Compose sur Windows (WSL 2) — 5 conteneurs : namenode, datanode, mysql, kafka, tools (Flume + Sqoop).",
     size=16, color=INK)
demo = [("Sqoop import", "docker exec -it tools bash /scripts/01_sqoop_import.sh", "119 390 lignes dans /data/hotel/bookings"),
        ("Flume", "docker exec -it tools bash /scripts/02_flume_weblogs.sh", "logs visibles dans /data/hotel/weblogs"),
        ("Kafka", "docker exec -it kafka sh /scripts/produce_bookings.sh", "flux live + alertes Python"),
        ("Sqoop export", "docker exec -it tools bash /scripts/04_sqoop_export.sh", "KPI dans MySQL kpi_monthly")]
for i, (t, c, r) in enumerate(demo):
    y = 2.4 + i * 1.08
    badge(s, 0.6, y + 0.12, 0.6, str(i + 1), fill=CORAL, size=18)
    text(s, 1.45, y + 0.02, 2.3, 0.5, t, size=18, bold=True, color=NAVY)
    text(s, 1.45, y + 0.5, 2.6, 0.4, r, size=12, color=MUTED)
    box(s, 4.25, y + 0.05, 8.48, 0.75, INK)
    text(s, 4.5, y + 0.05, 8.1, 0.75, "$ " + c, size=13, font="Courier New", color=RGBColor(0x9F, 0xE8, 0xD8),
         anchor=MSO_ANCHOR.MIDDLE)
text(s, 0.6, 6.6, 12.1, 0.35, "Vérification à chaque étape : interface HDFS http://localhost:9870 → Utilities → Browse the file system",
     size=13, italic=True, color=MUTED)
footer(s, n)
s.notes_slide.notes_text_frame.text = (
    "Lancer la stack AVANT la séance (docker compose up -d). Suivre 03_Demo/DEMO_SCRIPT.md. "
    "Plan B en cas de panne : montrer les captures d'écran du dossier 04_Annexe/captures.")

# =================== 15. TRACES ===================
s = new()
title(s, "Traces techniques : problèmes et corrections", "Démo · Journal d'installation")
issues = [("Flume → HDFS : NoSuchMethodError (Guava)", "Flume embarque Guava 11, Hadoop 3 attend Guava 27", "Suppression de lib/guava-*.jar de Flume"),
          ("Sqoop : NoClassDefFoundError StringUtils", "Sqoop 1.4.7 compilé pour Hadoop 2, commons-lang absent", "Ajout de commons-lang-2.6.jar dans sqoop/lib"),
          ("Sqoop : Public Key Retrieval is not allowed", "MySQL 8 utilise caching_sha2_password", "allowPublicKeyRetrieval=true & mysql_native_password"),
          ("Kafka : client Windows ne se connecte pas", "advertised.listeners pointait sur kafka:9092", "Listener EXTERNAL sur localhost:29092"),
          ("Import CSV : valeurs « NA » et « NULL »", "colonnes children / agent non numériques", "NULLIF() au chargement MySQL")]
hdr = ["Problème (connu ou rencontré)", "Cause", "Correction appliquée"]
xs, ws = [0.6, 5.0, 8.85], [4.3, 3.75, 3.88]
for j, h in enumerate(hdr):
    text(s, xs[j], 1.75, ws[j], 0.35, h.upper(), size=12, bold=True, color=CORAL)
for i, row in enumerate(issues):
    y = 2.2 + i * 0.86
    box(s, 0.5, y, 12.33, 0.76, LIGHT if i % 2 == 0 else WHITE)
    for j, v in enumerate(row):
        text(s, xs[j], y, ws[j] - 0.15, 0.76, v, size=13 if j else 14, bold=(j == 0), color=NAVY if j == 0 else INK,
             anchor=MSO_ANCHOR.MIDDLE)
text(s, 0.6, 6.6, 12.1, 0.35, "Captures d'écran, logs complets et fichier d'instructions : voir l'annexe (04_Annexe).",
     size=13, italic=True, color=MUTED)
footer(s, n)
s.notes_slide.notes_text_frame.text = (
    "(1 min) Montrer l'effort d'installation : chaque erreur rencontrée, sa cause et la correction. "
    "Adapter ce tableau aux erreurs réellement rencontrées par le groupe et ajouter les captures.")

# =================== 16. CONCLUSION ===================
s = new(dark=True)
text(s, 0.8, 0.9, 8, 0.4, "BILAN & PROCHAINES ÉTAPES", size=14, bold=True, color=CORAL)
text(s, 0.8, 1.45, 11.5, 1.0, "Les trois chemins d'ingestion sont en place ; l'évaluation finale portera sur l'analyse",
     size=32, bold=True, font=HEAD, color=WHITE)
done = ["Problématique et dataset définis (119 390 réservations)", "Architecture conçue et justifiée",
        "Kafka, Flume et Sqoop installés et interconnectés à HDFS"]
todo = ["Traitement Hive / Spark sur le Data Lake", "Modèle de prédiction des annulations",
        "Tableau de bord de revenue management"]
for k, (lab, items, c) in enumerate([("Réalisé", done, TEAL), ("Évaluation finale", todo, CORAL)]):
    x = 0.8 + k * 6.0
    text(s, x, 3.2, 5.5, 0.45, lab, size=20, bold=True, color=c)
    for i, it in enumerate(items):
        badge(s, x, 3.85 + i * 0.85, 0.42, "✓" if k == 0 else "→", fill=c, size=14)
        text(s, x + 0.65, 3.87 + i * 0.85, 4.9, 0.7, it, size=16, color=WHITE)
text(s, 0.8, 6.35, 11, 0.4, "Merci — questions ?", size=20, bold=True, font=HEAD, color=WHITE)
footer(s, n, dark=True)
s.notes_slide.notes_text_frame.text = "(30 s) Conclure, ouvrir aux questions."

out = HERE / "Projet_BigData_Hotel_MiParcours.pptx"
prs.save(out)
print("OK", out, n, "slides")
