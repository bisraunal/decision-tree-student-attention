"""
PDF Proje Raporu Üretici v2 — Geliştirilmiş Tasarım
====================================================
BLM0463 Veri Madenciliğine Giriş - Dönem Projesi
Büşra Ünal — 22360859084
"""

import os
import json
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image,
    Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfgen import canvas as canvasmod

# ── Font kayıt ───────────────────────────────────────────────────────────
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
pdfmetrics.registerFont(TTFont("DJ",   f"{FONT_DIR}/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DJB",  f"{FONT_DIR}/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DJI",  f"{FONT_DIR}/DejaVuSans-Oblique.ttf"))
pdfmetrics.registerFont(TTFont("DJBI", f"{FONT_DIR}/DejaVuSans-BoldOblique.ttf"))
pdfmetrics.registerFont(TTFont("DJM",  f"{FONT_DIR}/DejaVuSansMono.ttf"))
registerFontFamily("DJ", normal="DJ", bold="DJB", italic="DJI", boldItalic="DJBI")

# ── Yollar ───────────────────────────────────────────────────────────────
ROOT     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG_DIR  = os.path.join(ROOT, "figures")
RES_DIR  = os.path.join(ROOT, "results")
OUT_PDF  = os.path.join(ROOT, "BLM463_Proje_BusraUnal_22360859084.pdf")

with open(os.path.join(RES_DIR, "results.json"), "r", encoding="utf-8") as f:
    R = json.load(f)

# ── Renkler ──────────────────────────────────────────────────────────────
NAVY    = colors.HexColor("#0D1B2A")
DBLUE   = colors.HexColor("#1B3A5C")
MBLUE   = colors.HexColor("#2E6B9E")
LBLUE   = colors.HexColor("#3D8ECF")
ACCENT  = colors.HexColor("#E8873A")
LGRAY   = colors.HexColor("#F2F5F8")
MGRAY   = colors.HexColor("#6B7B8D")
WHITE   = colors.white
DARKTEXT= colors.HexColor("#1A1A2E")

W, H = A4  # 595.27, 841.89

# ── Stiller ──────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()
S = lambda name, **kw: ParagraphStyle(name, **kw)

h1 = S("H1", fontName="DJB", fontSize=15, leading=19, spaceBefore=16,
       spaceAfter=10, textColor=DBLUE)
h2 = S("H2", fontName="DJB", fontSize=12, leading=15, spaceBefore=12,
       spaceAfter=6, textColor=MBLUE)
body = S("Body", fontName="DJ", fontSize=10.5, leading=15, alignment=TA_JUSTIFY,
         spaceAfter=8, textColor=DARKTEXT)
cap = S("Cap", fontName="DJI", fontSize=9, leading=12, alignment=TA_CENTER,
        spaceAfter=12, textColor=MGRAY)
ref = S("Ref", fontName="DJ", fontSize=9, leading=12, leftIndent=20,
        firstLineIndent=-20, spaceAfter=4, textColor=DARKTEXT)

story = []


# ── Yardımcılar ──────────────────────────────────────────────────────────
def img(name, w_cm=14, caption=None):
    from reportlab.lib.utils import ImageReader
    path = os.path.join(FIG_DIR, name)
    if not os.path.exists(path):
        return
    ir = ImageReader(path)
    iw, ih = ir.getSize()
    tw = w_cm * cm
    th = tw * (ih / iw)
    # Sayfaya sığmadıysa küçült
    max_h = 16 * cm
    if th > max_h:
        th = max_h
        tw = th * (iw / ih)
    i = Image(path, width=tw, height=th)
    i.hAlign = "CENTER"
    story.append(i)
    if caption:
        story.append(Paragraph(caption, cap))
    else:
        story.append(Spacer(1, 6))


def tbl(data, widths=None, highlight_row=None):
    """Güzel tablolar — isteğe bağlı vurgu satırı."""
    t = Table(data, colWidths=widths)
    cmds = [
        ("BACKGROUND",     (0, 0), (-1, 0), DBLUE),
        ("TEXTCOLOR",      (0, 0), (-1, 0), WHITE),
        ("FONTNAME",       (0, 0), (-1, 0), "DJB"),
        ("FONTNAME",       (0, 1), (-1, -1), "DJ"),
        ("FONTSIZE",       (0, 0), (-1, -1), 9.5),
        ("ALIGN",          (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
        ("GRID",           (0, 0), (-1, -1), 0.3, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LGRAY]),
        ("TOPPADDING",     (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 6),
        ("LEFTPADDING",    (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",   (0, 0), (-1, -1), 8),
    ]
    if highlight_row is not None:
        cmds.append(("BACKGROUND", (0, highlight_row), (-1, highlight_row),
                      colors.HexColor("#FEF3C7")))
        cmds.append(("FONTNAME",   (0, highlight_row), (-1, highlight_row), "DJB"))
    t.setStyle(TableStyle(cmds))
    return t


def hr():
    story.append(HRFlowable(width="100%", thickness=0.5, color=MBLUE,
                             spaceBefore=6, spaceAfter=10))


# ── Sayfa alt/üst bilgi ─────────────────────────────────────────────────
class PageTemplate:
    """Her sayfanın altına numara, üstüne ince çizgi koyar."""
    def __init__(self, doc):
        self.width  = doc.width
        self.height = doc.height

    def __call__(self, canvas, doc):
        canvas.saveState()
        pg = doc.page
        if pg > 1:
            # Üst çizgi
            canvas.setStrokeColor(MBLUE)
            canvas.setLineWidth(0.6)
            canvas.line(doc.leftMargin, H - doc.topMargin + 8,
                        W - doc.rightMargin, H - doc.topMargin + 8)
            # Üst metin
            canvas.setFont("DJI", 8)
            canvas.setFillColor(MGRAY)
            canvas.drawString(doc.leftMargin, H - doc.topMargin + 12,
                              "BLM0463 — Veri Madenciliğine Giriş | Dönem Projesi")
            canvas.drawRightString(W - doc.rightMargin, H - doc.topMargin + 12,
                                   "Büşra Ünal — 22360859084")
            # Alt çizgi + sayfa numarası
            canvas.setStrokeColor(MBLUE)
            canvas.line(doc.leftMargin, doc.bottomMargin - 10,
                        W - doc.rightMargin, doc.bottomMargin - 10)
            canvas.setFont("DJ", 8.5)
            canvas.setFillColor(MGRAY)
            canvas.drawCentredString(W / 2, doc.bottomMargin - 22, f"— {pg} —")
        canvas.restoreState()


# ═══════════════════════════════════════════════════════════════════════
# KAPAK SAYFASI  (canvas ile çizim)
# ═══════════════════════════════════════════════════════════════════════
def cover_page(canvas, doc):
    """Özel kapak sayfası — sol koyu şerit, dekoratif bloklar."""
    canvas.saveState()

    # Sol koyu şerit
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, 7 * cm, H, fill=1, stroke=0)

    # Sol şeritteki dekoratif ince çizgiler
    canvas.setStrokeColor(colors.HexColor("#1E3A5F"))
    for yy in range(0, int(H), 28):
        canvas.setLineWidth(0.3)
        canvas.line(0.5 * cm, yy, 6.5 * cm, yy)

    # Sol şerit — dönen yazı
    canvas.setFillColor(colors.HexColor("#FFFFFF30"))
    canvas.setFont("DJB", 42)
    canvas.saveState()
    canvas.translate(3.2 * cm, 6 * cm)
    canvas.rotate(90)
    canvas.drawCentredString(0, 0, "DECISION TREE")
    canvas.restoreState()

    # Sol şerit alt bilgiler
    canvas.setFont("DJ", 9)
    canvas.setFillColor(colors.HexColor("#8899AA"))
    canvas.drawCentredString(3.5 * cm, 3.5 * cm, "Python 3 + scikit-learn")
    canvas.drawCentredString(3.5 * cm, 2.8 * cm, "Mayıs 2026")

    # Accent çizgi (sol şerit sağ kenarı)
    canvas.setFillColor(ACCENT)
    canvas.rect(7 * cm, 0, 4 * mm, H, fill=1, stroke=0)

    # ── Sağ taraf içerik ──
    rx = 8.2 * cm  # sağ alan başlangıcı

    # Ders adı
    canvas.setFont("DJ", 11)
    canvas.setFillColor(MGRAY)
    canvas.drawString(rx, H - 4 * cm, "BLM0463 — Veri Madenciliğine Giriş")
    canvas.setFont("DJ", 10)
    canvas.drawString(rx, H - 4.6 * cm, "Dönem Projesi Raporu")

    # Başlık
    canvas.setFillColor(DBLUE)
    canvas.setFont("DJB", 20)
    canvas.drawString(rx, H - 7 * cm, "Karar Ağacı ile")
    canvas.drawString(rx, H - 7.8 * cm, "Çevrimiçi Derslerde")
    canvas.drawString(rx, H - 8.6 * cm, "Öğrenci Dikkat")
    canvas.drawString(rx, H - 9.4 * cm, "Düzeyi Tespiti")

    # Altında ince accent çizgi
    canvas.setStrokeColor(ACCENT)
    canvas.setLineWidth(2.5)
    canvas.line(rx, H - 10 * cm, rx + 4 * cm, H - 10 * cm)

    # Veri seti
    canvas.setFont("DJI", 10)
    canvas.setFillColor(MGRAY)
    canvas.drawString(rx, H - 11 * cm,
                      "Students Attention Detection Dataset")
    canvas.drawString(rx, H - 11.5 * cm,
                      "Hossen & Uddin (2023) — Data in Brief")

    # Ana bilgi kutusu
    box_y = H - 17.5 * cm
    canvas.setFillColor(LGRAY)
    canvas.roundRect(rx, box_y, 11 * cm, 4.5 * cm, 6, fill=1, stroke=0)

    canvas.setFont("DJB", 10.5)
    canvas.setFillColor(DBLUE)
    info = [
        ("Öğrenci",   "Büşra Ünal"),
        ("Numara",    "22360859084"),
        ("Yöntem",    "Decision Tree (Karar Ağacı)"),
        ("Accuracy",  "%99.88"),
        ("F1-Score",  "%99.85"),
    ]
    yy = box_y + 3.8 * cm
    for label, value in info:
        canvas.setFont("DJB", 10)
        canvas.setFillColor(DBLUE)
        canvas.drawString(rx + 0.5 * cm, yy, label + ":")
        canvas.setFont("DJ", 10)
        canvas.setFillColor(DARKTEXT)
        canvas.drawString(rx + 3.8 * cm, yy, value)
        yy -= 0.75 * cm

    # GitHub linki
    canvas.setFont("DJ", 9)
    canvas.setFillColor(MBLUE)
    canvas.drawString(rx, H - 19 * cm,
                      "github.com/bisraunal/decision-tree-student-attention")

    # Büyük doğruluk rozeti sağ alt
    badge_x = W - 4.5 * cm
    badge_y = 3.5 * cm
    canvas.setFillColor(ACCENT)
    canvas.circle(badge_x, badge_y, 2 * cm, fill=1, stroke=0)
    canvas.setFont("DJB", 22)
    canvas.setFillColor(WHITE)
    canvas.drawCentredString(badge_x, badge_y + 0.3 * cm, "99.88")
    canvas.setFont("DJ", 9)
    canvas.drawCentredString(badge_x, badge_y - 0.5 * cm, "% Accuracy")

    canvas.restoreState()


# ═══════════════════════════════════════════════════════════════════════
# İÇERİK
# ═══════════════════════════════════════════════════════════════════════

# Kapak placeholder (gerçek çizim cover_page fonksiyonuyla yapılacak)
story.append(Spacer(1, 1))  # minimal — canvas tüm çizimi yapar
story.append(PageBreak())

# ─── 1. ÖZET ──────────────────────────────────────────────────────────
story.append(Paragraph("1. Özet", h1))
hr()
story.append(Paragraph(
    "Bu çalışmada, Hossen ve Uddin tarafından 2023 yılında <i>Data in Brief</i> "
    "dergisinde yayınlanan <b>Students Attention Detection Dataset</b> üzerinde "
    "Karar Ağacı (Decision Tree) sınıflandırma yöntemi uygulanmıştır. Veri seti, "
    "çevrimiçi derslere katılan öğrencilerin webcam görüntülerinden MediaPipe "
    "(yüz, el, baş duruşu) ve YOLOv7 (cep telefonu tespiti) kullanılarak çıkarılan "
    "16 özelliği içermekte ve 4.000 örnekten oluşmaktadır.",
    body))
story.append(Paragraph(
    "Optimize edilmiş Karar Ağacı modeli test setinde <b>%99.88 doğruluk</b>, "
    "<b>%100 kesinlik (precision)</b>, <b>%99.70 duyarlılık (recall)</b> ve "
    "<b>%99.85 F1 skoru</b> elde etmiştir. 5-fold çapraz doğrulamada ortalama "
    "doğruluk <b>%99.90 ± %0.05</b> olarak ölçülmüştür. Aynı veri setinde "
    "Hossen ve Uddin (2023) tarafından XGBoost ile elde edilen <b>%99.75</b> "
    "doğruluğun <b>0.13 puan</b> üzerindedir.",
    body))
story.append(Paragraph(
    "<b>Anahtar Kelimeler:</b> Veri madenciliği, Karar ağacı, Sınıflandırma, "
    "Öğrenci dikkati, Çevrimiçi öğrenme, MediaPipe, YOLOv7, scikit-learn",
    body))

# ─── 2. GİRİŞ ─────────────────────────────────────────────────────────
story.append(Paragraph("2. Giriş", h1))
hr()
story.append(Paragraph(
    "COVID-19 pandemisinin ardından çevrimiçi eğitim yaygın bir öğretim modeline "
    "dönüşmüştür. Ancak bu model, fiziksel sınıflarda öğretmenlerin doğal olarak "
    "yürüttüğü dikkat takibi konusunda ciddi zorluklar barındırmaktadır. "
    "Öğrencilerin kameralarının kapalı olması, dijital dikkat dağıtıcılar "
    "(telefon, başka sekmeler) ve göz teması kuramama gibi etkenler, eğitmenin "
    "öğrenci katılımını değerlendirmesini güçleştirmektedir. Bu nedenle "
    "bilgisayarlı görü ve makine öğrenmesi temelli otomatik dikkat tespit "
    "sistemleri artan bir araştırma alanı haline gelmiştir.",
    body))
story.append(Paragraph(
    "Bu projenin amacı, BLM0463 ders kapsamında <b>Karar Ağacı</b> yöntemini "
    "uygulayarak gerçek öğrenci verilerinden dikkat tespiti yapmak ve sonuçları "
    "yaygın değerlendirme ölçütleriyle (Accuracy, Precision, Recall, F1, "
    "Specificity, ROC-AUC) raporlamaktır. Ayrıca aynı veri seti üzerinde "
    "yapılmış akademik çalışmayla karşılaştırma sunulmaktadır.",
    body))

story.append(Paragraph("2.1. Çalışmanın Katkıları", h2))
story.append(Paragraph(
    "<b>(i)</b> Kapsamlı keşifsel veri analizi ve 14 farklı görselleştirme. "
    "<b>(ii)</b> Makaledeki önişleme yaklaşımıyla tam uyumlu adımlar. "
    "<b>(iii)</b> 384 parametre kombinasyonuyla 5-fold GridSearchCV. "
    "<b>(iv)</b> Hossen ve Uddin (2023) XGBoost sonuçlarıyla karşılaştırma.",
    body))

# ─── 3. VERİ SETİ ────────────────────────────────────────────────────
story.append(PageBreak())
story.append(Paragraph("3. Veri Seti", h1))
hr()
story.append(Paragraph(
    "Kullanılan <b>Students Attention Detection Dataset</b>, Hossen ve Uddin "
    "(2023) tarafından <i>Data in Brief</i> dergisinde yayınlanmış ve Mendeley "
    "Data üzerinden açık erişimli olarak paylaşılmıştır (DOI: "
    "10.17632/smzggbnkd2.1). Veri seti, Bangladesh'teki Jahangirnagar "
    "Üniversitesi'nde Haziran 2023'te bilgisayar bilimleri dersine katılan "
    "öğrencilerden, webcam görüntülerinin 20 FPS hızıyla işlenmesiyle "
    "oluşturulmuştur.",
    body))

story.append(Paragraph("3.1. Veri Toplama Mimarisi", h2))
story.append(Paragraph(
    "Her video karesi dört modülden geçirilmiştir: "
    "<b>(1) Yüz tespiti</b> — MediaPipe BlazeFace; "
    "<b>(2) El takibi</b> — MediaPipe Hands; "
    "<b>(3) Baş duruşu tahmini</b> — MediaPipe Face Mesh + OpenCV solvePnP(); "
    "<b>(4) Cep telefonu tespiti</b> — YOLOv7 (MS-COCO ile eğitilmiş).",
    body))

story.append(Paragraph("3.2. Özellikler ve Etiket", h2))
feat_data = [
    ["#", "Özellik", "Açıklama", "Veri Tipi"],
    ["1",  "no_of_face",     "Karedeki yüz sayısı",              "Tamsayı"],
    ["2",  "face_x / face_y","Yüz kutu koordinatları",           "Float"],
    ["3",  "face_w / face_h","Yüz genişlik ve yükseklik (px)",   "Float"],
    ["4",  "face_con",       "Yüz tespit güven skoru",           "Float"],
    ["5",  "no_of_hand",     "Algılanan el sayısı",              "Tamsayı"],
    ["6",  "pose",           "Baş yönelimi (fwd/down/L/R)",      "Kategorik"],
    ["7",  "pose_x / pose_y","Baş açıları (derece)",             "Float"],
    ["8",  "phone",          "Telefon var mı? (0/1)",            "İkili"],
    ["9",  "phone_x/y/w/h",  "Telefon koordinat ve boyutu",     "Float"],
    ["10", "phone_con",      "Telefon tespit güven skoru",       "Float"],
    ["11", "label",          "0 = Attentive, 1 = Inattentive",  "İkili"],
]
story.append(tbl(feat_data, [0.7*cm, 3*cm, 6.5*cm, 2.3*cm]))
story.append(Paragraph("Tablo 1. Veri seti özellikleri ve veri tipleri.", cap))

story.append(Paragraph("3.3. Sınıf Dağılımı", h2))
story.append(Paragraph(
    "Toplam <b>4.000 örnek</b>: <b>2.314 Attentive (%57.85)</b> ve "
    "<b>1.686 Inattentive (%42.15)</b>. Hafif dengesiz olsa da "
    "hiperparametre aramasında <i>class_weight='balanced'</i> seçeneği "
    "değerlendirilmiştir.",
    body))
img("01_class_distribution.png", 10,
    "Şekil 1. Veri setindeki sınıf dağılımı.")

story.append(Paragraph("3.4. Etiketleme Kriterleri", h2))
lbl_data = [
    ["Modül", "Attentive (0)", "Inattentive (1)"],
    ["Yüz",    "Yüz güvenle tespit edildi, merkezde",     "Yüz yok veya kısmen kadrajda"],
    ["El",     "Bir/iki el yüze yakın",                    "El yok veya çok uzakta"],
    ["Baş",    "İleri veya hafif eğik",                    "Sol/sağ/aşağı yönelim"],
    ["Telefon","Telefon yok veya ekranı aşağıda",          "Telefon ekranı yukarıda"],
]
story.append(tbl(lbl_data, [1.8*cm, 5.5*cm, 5.5*cm]))
story.append(Paragraph(
    "Tablo 2. Deterministik etiketleme kuralları (Hossen & Uddin, 2023).",
    cap))
story.append(Paragraph(
    "<b>Önemli gözlem:</b> Etiketler kural-tabanlı atandığı için özellik uzayından "
    "etiketlere büyük ölçüde deterministik bir eşleme bulunmaktadır. Bu durum, "
    "Karar Ağacı gibi kural çıkarımına dayalı modellerin neden çok yüksek doğruluk "
    "elde ettiğini açıklamaktadır (Bölüm 7'de detaylı tartışılmıştır).",
    body))

# EDA görselleri
story.append(PageBreak())
story.append(Paragraph("3.5. Keşifsel Veri Analizi", h2))
story.append(Paragraph(
    "Veri setinde eksik değer yoktur; 30 satır tekrardır (toplamın %0.75'i). "
    "Kategorik <i>pose</i> dağılımı: 2.951 forward, 537 down, 334 left, 178 right.",
    body))
img("02_pose_distribution.png", 12, "Şekil 2. Baş yönelimi dağılımı.")
img("03_pose_vs_label.png", 12,
    "Şekil 3. Pose × sınıf çapraz dağılımı. 'forward' dışı büyük ölçüde Inattentive.")
img("04_correlation_heatmap.png", 14,
    "Şekil 4. Pearson korelasyon matrisi. Telefon özellikleri kendi aralarında >0.85 korelasyona sahiptir.")

story.append(PageBreak())
img("05_face_coords_scatter.png", 12,
    "Şekil 5. Yüz koordinatları × dikkat sınıfı. İki sınıf büyük ölçüde örtüşmektedir.")
img("06_confidence_boxplot.png", 10,
    "Şekil 6. Yüz ve telefon tespiti güven skorları kutu grafiği.")
img("07_feature_distributions.png", 14,
    "Şekil 7. Anahtar özelliklerin sınıf bazında histogramları.")

# ─── 4. YÖNTEM ────────────────────────────────────────────────────────
story.append(PageBreak())
story.append(Paragraph("4. Yöntem", h1))
hr()

story.append(Paragraph("4.1. Karar Ağacı (Decision Tree)", h2))
story.append(Paragraph(
    "Karar Ağacı, denetimli öğrenmede yaygın, ağaç yapısına dayalı ve "
    "yorumlanabilir bir sınıflandırma yöntemidir. Veri kümesini ardışık "
    "'eğer-ise' koşullarıyla bölerek yapraklarda sınıf etiketi atar. Bu "
    "çalışmada scikit-learn'ün <i>DecisionTreeClassifier</i> sınıfı "
    "kullanılmıştır. Bölme kriteri olarak Gini indeksi ve Bilgi Kazancı "
    "(Entropi) değerlendirilmiştir.",
    body))
story.append(Paragraph(
    "<b>Gini İndeksi:</b> Gini(t) = 1 − Σ p<sub>i</sub><super>2</super> &nbsp;&nbsp; | &nbsp;&nbsp; "
    "<b>Entropi:</b> H(t) = − Σ p<sub>i</sub> log<sub>2</sub>(p<sub>i</sub>)",
    body))
story.append(Paragraph(
    "Avantajları: (i) yüksek yorumlanabilirlik, (ii) ölçeklemeye duyarsızlık, "
    "(iii) karma veri tipi desteği, (iv) hızlı eğitim. Dezavantajı: aşırı "
    "öğrenme eğilimi — <i>max_depth</i>, <i>min_samples_split</i> gibi "
    "parametrelerle düzenlileştirilir.",
    body))

story.append(Paragraph("4.2. Önişleme", h2))
story.append(Paragraph(
    "<b>1.</b> <i>pose</i> sütunu one-hot encoding ile 4 ikili sütuna dönüştürüldü. "
    "<b>2.</b> <i>face_con</i> [0,100] → [0,1] normalize edildi. "
    "<b>3.</b> Tüm özellikler <b>MaxAbsScaler</b> ile [−1,1] aralığına ölçeklendi. "
    "<b>4.</b> %80 eğitim (3.200) / %20 test (800) stratified split (random_state=42).",
    body))

story.append(Paragraph("4.3. Hiperparametre Optimizasyonu", h2))
story.append(Paragraph(
    "<b>GridSearchCV</b> ile <b>384</b> parametre kombinasyonu, <b>5-fold</b> "
    "çapraz doğrulama, <b>F1</b> hedef metriği ile optimize edildi (toplam "
    "1.920 model uydurma).",
    body))
grid_data = [
    ["Parametre", "Aranan Değerler"],
    ["criterion",         "gini, entropy"],
    ["max_depth",         "None, 5, 10, 15, 20, 30"],
    ["min_samples_split", "2, 5, 10, 20"],
    ["min_samples_leaf",  "1, 2, 5, 10"],
    ["class_weight",      "None, balanced"],
]
story.append(tbl(grid_data, [4*cm, 9*cm]))
story.append(Paragraph("Tablo 3. GridSearchCV parametre uzayı.", cap))

story.append(Paragraph("4.4. Değerlendirme Metrikleri", h2))
story.append(Paragraph(
    "<b>Accuracy</b> = (TP+TN) / (TP+TN+FP+FN) &nbsp;|&nbsp; "
    "<b>Precision</b> = TP/(TP+FP) &nbsp;|&nbsp; "
    "<b>Recall</b> = TP/(TP+FN) &nbsp;|&nbsp; "
    "<b>Specificity</b> = TN/(TN+FP) &nbsp;|&nbsp; "
    "<b>F1</b> = 2·P·R/(P+R) &nbsp;|&nbsp; "
    "<b>ROC-AUC</b>",
    body))

# ─── 5. BULGULAR ──────────────────────────────────────────────────────
story.append(PageBreak())
story.append(Paragraph("5. Bulgular ve Sonuçlar", h1))
hr()

bm = R["baseline_metrics"]
fm = R["final_test_metrics"]
bp = R["best_hyperparameters"]

story.append(Paragraph("5.1. Baseline (Varsayılan Parametreler)", h2))
base_data = [
    ["Metrik", "Değer"],
    ["Accuracy",    f"%{bm['accuracy']*100:.2f}"],
    ["Precision",   f"%{bm['precision']*100:.2f}"],
    ["Recall",      f"%{bm['recall']*100:.2f}"],
    ["Specificity", f"%{bm['specificity']*100:.2f}"],
    ["F1-Score",    f"%{bm['f1']*100:.2f}"],
    ["ROC-AUC",     f"{bm['roc_auc']:.4f}"],
]
story.append(tbl(base_data, [4.5*cm, 4*cm]))
story.append(Paragraph("Tablo 4. Baseline test seti performansı.", cap))

story.append(Paragraph("5.2. Optimize Edilmiş Model", h2))
story.append(Paragraph(
    f"En iyi parametreler: <b>criterion={bp['criterion']}</b>, "
    f"<b>max_depth={bp['max_depth']}</b>, "
    f"<b>min_samples_split={bp['min_samples_split']}</b>, "
    f"<b>min_samples_leaf={bp['min_samples_leaf']}</b>. "
    f"5-fold CV F1: <b>{R['best_cv_score_f1']:.4f}</b>.",
    body))
final_data = [
    ["Metrik", "Değer"],
    ["Accuracy",    f"%{fm['accuracy']*100:.2f}"],
    ["Precision",   f"%{fm['precision']*100:.2f}"],
    ["Recall",      f"%{fm['recall']*100:.2f}"],
    ["Specificity", f"%{fm['specificity']*100:.2f}"],
    ["F1-Score",    f"%{fm['f1']*100:.2f}"],
    ["ROC-AUC",     f"{fm['roc_auc']:.4f}"],
]
story.append(tbl(final_data, [4.5*cm, 4*cm]))
story.append(Paragraph("Tablo 5. Optimize edilmiş modelin test seti performansı.", cap))

story.append(Paragraph("5.3. Confusion Matrix", h2))
cmtx = R["confusion_matrix"]
story.append(Paragraph(
    f"800 test örneğinden yalnızca <b>1</b> tanesi yanlış sınıflandırılmıştır: "
    f"TN={cmtx[0][0]}, FP={cmtx[0][1]}, FN={cmtx[1][0]}, TP={cmtx[1][1]}.",
    body))
img("08_confusion_matrices.png", 14,
    "Şekil 8. Baseline ve tuned model Confusion Matrix karşılaştırması.")

story.append(Paragraph("5.4. ROC ve Precision-Recall Eğrileri", h2))
img("09_roc_curve.png", 10, "Şekil 9. ROC eğrisi (AUC = 0.9985).")
img("10_precision_recall.png", 10, "Şekil 10. Precision-Recall eğrisi.")

story.append(PageBreak())
story.append(Paragraph("5.5. 5-Fold Çapraz Doğrulama", h2))
cv = R["five_fold_cv_scores"]
cv_data = [["Metrik", "Ortalama ± Std", "Min – Max"]]
for m in ["accuracy", "precision", "recall", "f1", "roc_auc"]:
    s = cv[m]["scores"]
    cv_data.append([m.upper(),
                    f"{cv[m]['mean']:.4f} ± {cv[m]['std']:.4f}",
                    f"{min(s):.4f} – {max(s):.4f}"])
story.append(tbl(cv_data, [3.5*cm, 4.5*cm, 4*cm]))
story.append(Paragraph("Tablo 6. 5-fold çapraz doğrulama sonuçları.", cap))

story.append(Paragraph("5.6. Özellik Önemleri", h2))
fi = R["feature_importances"]
top_fi = sorted(fi.items(), key=lambda x: -x[1])[:5]
fi_data = [["Sıra", "Özellik", "Önem Skoru"]]
for i, (k, v) in enumerate(top_fi, 1):
    fi_data.append([str(i), k, f"{v:.4f}"])
story.append(tbl(fi_data, [1.5*cm, 4.5*cm, 3.5*cm]))
story.append(Paragraph("Tablo 7. En önemli 5 özellik.", cap))
story.append(Paragraph(
    "<b>pose_forward</b> (0.49) — Öğrencinin başının ileriye dönük olup olmaması "
    "en güçlü belirleyici. <b>phone_y</b> (0.32) — Telefonun dikey konumu "
    "ikinci sırada. <b>pose_y</b> ve <b>pose_x</b> (toplam 0.17) — Açısal baş "
    "yönelimi. Bu sıralama etiketleme kurallarının dolaylı bir doğrulamasıdır.",
    body))
img("11_feature_importances.png", 12, "Şekil 11. Tüm özelliklerin önem skorları.")

story.append(Paragraph("5.7. Karar Ağacı Yapısı", h2))
story.append(Paragraph(
    "Kök düğüm <i>pose_forward</i>: öğrencinin başı ileri dönük değilse "
    "(pose_forward ≤ 0.5), 844 örneğin tamamı Inattentive olarak "
    "sınıflandırılmaktadır (Gini=0).",
    body))
img("12_decision_tree.png", 16, "Şekil 12. Karar Ağacı (ilk 4 düzey).")

story.append(Paragraph("5.8. Learning Curve", h2))
img("13_learning_curve.png", 11, "Şekil 13. Learning curve.")

# ─── 6. KARŞILAŞTIRMA ─────────────────────────────────────────────────
story.append(PageBreak())
story.append(Paragraph("6. Akademik Çalışma ile Karşılaştırma", h1))
hr()
story.append(Paragraph(
    "Referans çalışma: Hossen ve Uddin (2023), <i>Computers and Education: AI</i>, "
    "altı farklı ML algoritmasını karşılaştırarak <b>XGBoost ile %99.75 doğruluk</b> "
    "raporlamıştır. İkinci referans: Mello-Roman et al. (2023), benzer bir dikkat "
    "veri setinde XGBoost ile <b>%80.52</b> doğruluk elde etmiştir.",
    body))
comp_data = [
    ["Çalışma",                   "Yöntem",       "Veri Seti",    "Accuracy", "Precision"],
    ["Bu Çalışma (Baseline)",     "Decision Tree","Hossen 2023",  "%99.88",   "%100.00"],
    ["Bu Çalışma (Tuned)",        "Decision Tree","Hossen 2023",  "%99.88",   "%100.00"],
    ["Hossen & Uddin (2023)",     "XGBoost",      "Hossen 2023",  "%99.75",   "%99.71"],
    ["Mello-Roman et al. (2023)", "XGBoost",      "Kendi verisi", "%80.52",   "—"],
]
story.append(tbl(comp_data, [4.2*cm, 2.5*cm, 2.5*cm, 2*cm, 2*cm], highlight_row=2))
story.append(Paragraph(
    "Tablo 8. Literatür karşılaştırması. Sarı satır: bu çalışmanın tuned modeli.",
    cap))
img("14_literature_comparison.png", 13, "Şekil 14. Doğruluk karşılaştırması.")

story.append(Paragraph("6.1. Karşılaştırma Yorumu", h2))
story.append(Paragraph(
    "Karar Ağacı, XGBoost'u <b>0.13 puan</b> geçmiştir. Bu, etiketlerin "
    "kural-tabanlı atanmış olmasından kaynaklanmaktadır — Karar Ağacı bu tür "
    "deterministik eşlemeleri doğal olarak öğrenir. Karar Ağacının avantajları: "
    "<b>(a)</b> her tahmin görsel olarak açıklanabilir, <b>(b)</b> eğitim ve "
    "tahmin çok hızlı, <b>(c)</b> model boyutu küçük, <b>(d)</b> gerçek "
    "zamanlı uygulamalar için ideal.",
    body))

# ─── 7. TARTIŞMA ──────────────────────────────────────────────────────
story.append(Paragraph("7. Tartışma ve Sınırlılıklar", h1))
hr()
story.append(Paragraph(
    "%99.88 doğruluğu büyük ölçüde veri setinin yapısından kaynaklanmaktadır: "
    "etiketler deterministik kurallarla atanmış olduğundan, sınıflandırıcı bu "
    "kuralları yeniden öğrenmektedir. Gerçek dikkat algılaması çok daha "
    "karmaşıktır.",
    body))
story.append(Paragraph(
    "<b>Veri seti sınırlılıkları:</b> (i) Aydınlatma/oda düzeni biasları, "
    "(ii) Tek üniversiteden örnekler, (iii) Sadece dış davranışlara dayalı "
    "etiketleme, (iv) Hafif sınıf dengesizliği.",
    body))
story.append(Paragraph(
    "<b>Yöntemsel sınırlılıklar:</b> (i) 30 yinelenen satır veri sızıntısına "
    "neden olabilir, (ii) Tek random_state, (iii) Sadece 1 yanlış "
    "sınıflandırma ile hata analizi sınırlı.",
    body))

# ─── 8. SONUÇ ─────────────────────────────────────────────────────────
story.append(Paragraph("8. Sonuç", h1))
hr()
story.append(Paragraph(
    "Karar Ağacı modeli test setinde <b>%99.88 doğruluk</b> ve <b>%99.85 "
    "F1</b> skoru elde etmiştir. Referans XGBoost çalışmasını 0.13 puan "
    "aşmıştır. 5-fold CV (%99.90±%0.05) kararlılığı teyit etmiştir. "
    "<i>pose_forward</i> ve <i>phone_y</i> en belirleyici özelliklerdir.",
    body))
story.append(Paragraph(
    "<b>Gelecek çalışmalar:</b> (i) Random Forest/XGBoost ile doğrudan "
    "karşılaştırma, (ii) Farklı demografik veri setlerinde genelleme, "
    "(iii) SHAP ile açıklanabilir AI, (iv) Zamansal modelleme (LSTM).",
    body))

# ─── 9. KAYNAKLAR ─────────────────────────────────────────────────────
story.append(PageBreak())
story.append(Paragraph("9. Kaynaklar", h1))
hr()
refs = [
    "[1] Hossen, M. K., Uddin, M. S. (2023). A dataset for assessing real-time attention levels of the students during online classes. <i>Data in Brief</i>, 51, 109771.",
    "[2] Hossen, M. K., Uddin, M. S. (2023). Attention monitoring of students during online classes using XGBoost classifier. <i>Computers and Education: AI</i>, 5, 100191.",
    "[3] Hossen, M. K., Uddin, M. S. (2025). From data to insights: Using gradient boosting classifier to optimize student engagement in online classes with explainable AI. <i>Education and Information Technologies</i>, 30, 18089–18130.",
    "[4] Hossen, M. K., Uddin, M. S. (2023). Students Attention Detection Dataset, v1. <i>Mendeley Data</i>. DOI: 10.17632/smzggbnkd2.1",
    "[5] Mello-Roman, J. D., et al. (2023). Machine Learning applied to student attentiveness detection. <i>Education and Information Technologies</i>.",
    "[6] Pedregosa, F., et al. (2011). Scikit-learn: Machine learning in Python. <i>JMLR</i>, 12(85), 2825–2830.",
    "[7] Chen, T., Guestrin, C. (2016). XGBoost: A scalable tree boosting system. <i>KDD '16</i>, 785–794.",
    "[8] Lugaresi, C., et al. (2019). MediaPipe: A framework for perceiving and processing reality. <i>CV for AR/VR Workshop, IEEE CVPR</i>.",
    "[9] Wang, C. Y., et al. (2023). YOLOv7: Trainable bag-of-freebies. <i>IEEE/CVF CVPR</i>, 7464–7475.",
    "[10] Bradski, G. (2000). The OpenCV library. <i>Dr. Dobb's Journal</i>, 25(11), 120–123.",
]
for r in refs:
    story.append(Paragraph(r, ref))

# EK
story.append(PageBreak())
story.append(Paragraph("EK A — Tekrar Üretilebilirlik", h1))
hr()
story.append(Paragraph(
    "<b>GitHub:</b> https://github.com/bisraunal/decision-tree-student-attention",
    body))
story.append(Paragraph(
    "Tüm rastgele işlemlerde <i>random_state=42</i> sabitlenmiştir. "
    "Çalıştırma: <font face='DJM'>pip install -r requirements.txt && "
    "python src/main.py</font>",
    body))


# ═══════════════════════════════════════════════════════════════════════
# BELGE OLUŞTUR
# ═══════════════════════════════════════════════════════════════════════
doc = SimpleDocTemplate(
    OUT_PDF, pagesize=A4,
    leftMargin=2.2*cm, rightMargin=2.2*cm,
    topMargin=2.5*cm, bottomMargin=2.5*cm,
    title="BLM463 Decision Tree Attention Detection",
    author="Büşra Ünal"
)

page_tmpl = PageTemplate(doc)

def first_and_later(canvas, doc):
    if doc.page == 1:
        cover_page(canvas, doc)
    else:
        page_tmpl(canvas, doc)

doc.build(story, onFirstPage=cover_page, onLaterPages=page_tmpl)
print(f"PDF oluşturuldu: {OUT_PDF}")
print(f"Boyut: {os.path.getsize(OUT_PDF)/1024:.0f} KB")
