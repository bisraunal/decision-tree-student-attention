"""
PDF Proje Raporu Üretici
========================
BLM0463 Veri Madenciliğine Giriş - Dönem Projesi
Decision Tree ile Öğrenci Dikkat Tespiti

Bu script results/ ve figures/ klasörlerindeki tüm çıktıları birleştirip
profesyonel akademik bir PDF raporu üretir.
"""

import os
import json
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image,
    Table, TableStyle, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Türkçe karakterler için DejaVu Sans fontunu kaydet
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
pdfmetrics.registerFont(TTFont("DejaVu",         f"{FONT_DIR}/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-Bold",    f"{FONT_DIR}/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-Italic",  f"{FONT_DIR}/DejaVuSans-Oblique.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-BoldIt",  f"{FONT_DIR}/DejaVuSans-BoldOblique.ttf"))
pdfmetrics.registerFont(TTFont("DejaVuMono",     f"{FONT_DIR}/DejaVuSansMono.ttf"))
# Aile kaydı (b/i/bi varyantları için)
from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily(
    "DejaVu",
    normal="DejaVu", bold="DejaVu-Bold",
    italic="DejaVu-Italic", boldItalic="DejaVu-BoldIt",
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG_DIR = os.path.join(ROOT, "figures")
RES_DIR = os.path.join(ROOT, "results")
OUT_PDF = os.path.join(ROOT, "BLM463_Proje_Rapor.pdf")

# Sonuçları yükle
with open(os.path.join(RES_DIR, "results.json"), "r", encoding="utf-8") as f:
    R = json.load(f)

# ----- Stil tanımları --------------------------------------------------------
styles = getSampleStyleSheet()

title_st = ParagraphStyle(
    "TitleX", parent=styles["Title"], fontSize=18, leading=22,
    alignment=TA_CENTER, spaceAfter=14, textColor=colors.HexColor("#1F3A68"),
    fontName="DejaVu-Bold"
)
subtitle_st = ParagraphStyle(
    "SubTitle", parent=styles["Normal"], fontSize=12, alignment=TA_CENTER,
    spaceAfter=10, textColor=colors.HexColor("#444444"),
    fontName="DejaVu"
)
h1_st = ParagraphStyle(
    "H1", parent=styles["Heading1"], fontSize=15, leading=18,
    spaceBefore=14, spaceAfter=10, textColor=colors.HexColor("#1F3A68"),
    fontName="DejaVu-Bold"
)
h2_st = ParagraphStyle(
    "H2", parent=styles["Heading2"], fontSize=12.5, leading=15,
    spaceBefore=10, spaceAfter=6, textColor=colors.HexColor("#2A5599"),
    fontName="DejaVu-Bold"
)
body_st = ParagraphStyle(
    "Body", parent=styles["Normal"], fontSize=10.5, leading=15,
    alignment=TA_JUSTIFY, spaceAfter=8,
    fontName="DejaVu"
)
caption_st = ParagraphStyle(
    "Caption", parent=styles["Normal"], fontSize=9.5, leading=12,
    alignment=TA_CENTER, spaceAfter=12, textColor=colors.HexColor("#555555"),
    fontName="DejaVu-Italic"
)
code_st = ParagraphStyle(
    "Code", parent=styles["Code"], fontSize=9, leading=11,
    backColor=colors.HexColor("#F4F4F4"), leftIndent=8, rightIndent=8,
    spaceBefore=4, spaceAfter=8, borderPadding=4,
    fontName="DejaVuMono"
)
ref_st = ParagraphStyle(
    "Ref", parent=styles["Normal"], fontSize=9.5, leading=12,
    leftIndent=18, firstLineIndent=-18, spaceAfter=4, alignment=TA_LEFT,
    fontName="DejaVu"
)

story = []


def add_image(path, width_cm=15, caption=None):
    """Görsel ekle (varsa) ve altına başlık koy. En-boy oranını korur."""
    from reportlab.lib.utils import ImageReader
    full = os.path.join(FIG_DIR, path)
    if os.path.exists(full):
        # Gerçek en-boy oranını koru
        ir = ImageReader(full)
        iw, ih = ir.getSize()
        ratio = ih / float(iw)
        target_w = width_cm * cm
        target_h = target_w * ratio
        img = Image(full, width=target_w, height=target_h)
        img.hAlign = "CENTER"
        story.append(img)
        if caption:
            story.append(Paragraph(caption, caption_st))
        else:
            story.append(Spacer(1, 8))


def metrics_table(data, col_widths=None):
    """Standart metrik tablosu stili."""
    t = Table(data, colWidths=col_widths or [5*cm, 3*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0), colors.HexColor("#1F3A68")),
        ("TEXTCOLOR",    (0, 0), (-1, 0), colors.white),
        ("FONTNAME",     (0, 0), (-1, 0), "DejaVu-Bold"),
        ("FONTNAME",     (0, 1), (-1, -1), "DejaVu"),
        ("FONTSIZE",     (0, 0), (-1, -1), 10),
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("GRID",         (0, 0), (-1, -1), 0.4, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#F4F7FB")]),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
    ]))
    return t


# =========================================================================
# KAPAK
# =========================================================================
story.append(Spacer(1, 2 * cm))
story.append(Paragraph("BLM0463 — Veri Madenciliğine Giriş", subtitle_st))
story.append(Paragraph("Dönem Projesi Raporu", subtitle_st))
story.append(Spacer(1, 1 * cm))
story.append(Paragraph(
    "Karar Ağacı (Decision Tree) Yöntemi ile<br/>"
    "Çevrimiçi Derslerde Öğrenci Dikkat Düzeyi Tespiti",
    title_st
))
story.append(Spacer(1, 0.6 * cm))
story.append(Paragraph(
    "Hossen &amp; Uddin (2023) Öğrenci Dikkat Tespiti Veri Seti Üzerinde<br/>"
    "Sınıflandırma Analizi ve Literatür ile Karşılaştırma",
    subtitle_st
))
story.append(Spacer(1, 2.5 * cm))

cover_tbl = Table([
    ["Ders",          "BLM0463 — Veri Madenciliğine Giriş"],
    ["Yöntem",        "Decision Tree (Karar Ağacı)"],
    ["Veri Seti",     "Students Attention Detection Dataset (Data in Brief, 2023)"],
    ["Platform",      "Python 3 + scikit-learn"],
    ["Örnek Sayısı",  "4.000 örnek, 16 özellik, 2 sınıf"],
    ["Test Doğruluğu", "%99.88 (Accuracy)"],
], colWidths=[3.5 * cm, 12 * cm])
cover_tbl.setStyle(TableStyle([
    ("BACKGROUND",  (0, 0), (0, -1), colors.HexColor("#1F3A68")),
    ("TEXTCOLOR",   (0, 0), (0, -1), colors.white),
    ("FONTNAME",    (0, 0), (0, -1), "DejaVu-Bold"),
    ("FONTNAME",    (1, 0), (1, -1), "DejaVu"),
    ("FONTSIZE",    (0, 0), (-1, -1), 10.5),
    ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
    ("GRID",        (0, 0), (-1, -1), 0.5, colors.grey),
    ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ("RIGHTPADDING",(0, 0), (-1, -1), 10),
    ("TOPPADDING",  (0, 0), (-1, -1), 8),
    ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
]))
story.append(cover_tbl)

story.append(Spacer(1, 3 * cm))
story.append(Paragraph(
    "<b>Öğrenci:</b> [Ad Soyad] &nbsp;&nbsp;&nbsp;&nbsp; <b>Numara:</b> [Öğrenci No]",
    subtitle_st
))
story.append(Paragraph(
    "<b>GitHub:</b> https://github.com/[kullaniciadi]/BLM463-Attention-Detection",
    subtitle_st
))
story.append(Paragraph("Mayıs 2026", subtitle_st))
story.append(PageBreak())


# =========================================================================
# 1. ÖZET
# =========================================================================
story.append(Paragraph("1. Özet", h1_st))
story.append(Paragraph(
    "Bu çalışmada, Hossen ve Uddin tarafından 2023 yılında <i>Data in Brief</i> "
    "dergisinde yayınlanan <b>Students Attention Detection Dataset</b> üzerinde "
    "Karar Ağacı (Decision Tree) sınıflandırma yöntemi uygulanmıştır. Veri seti, "
    "çevrimiçi derslere katılan öğrencilerin webcam görüntülerinden MediaPipe "
    "(yüz, el, baş duruşu) ve YOLOv7 (cep telefonu tespiti) kullanılarak çıkarılan "
    "16 özelliği içermekte ve 4.000 örnekten oluşmaktadır. Model, ikili sınıflandırma "
    "(Attentive / Inattentive) görevini gerçekleştirmek üzere eğitilmiş; %80 eğitim "
    "ve %20 test ayrımı, MaxAbsScaler ölçekleme ve <b>GridSearchCV</b> ile 5-fold "
    "çapraz doğrulamalı hiperparametre optimizasyonu uygulanmıştır.",
    body_st
))
story.append(Paragraph(
    "Optimize edilmiş Karar Ağacı modeli test setinde <b>%99.88 doğruluk</b>, "
    "<b>%100 kesinlik (precision)</b>, <b>%99.70 duyarlılık (recall)</b> ve "
    "<b>%99.85 F1 skoru</b> elde etmiştir. 5-fold çapraz doğrulamada ortalama "
    "doğruluk <b>%99.90 ± %0.05</b> ile son derece kararlı bir performans "
    "sergilenmiştir. Aynı veri seti üzerinde Hossen ve Uddin (2023) tarafından "
    "yapılan ve XGBoost ile <b>%99.75</b> doğruluğa ulaşılan referans çalışmayla "
    "karşılaştırıldığında, bu çalışma daha basit ve daha yorumlanabilir bir model "
    "olan Karar Ağacı ile <b>0.13 puan</b> daha yüksek bir doğruluk elde etmiştir.",
    body_st
))
story.append(Paragraph(
    "<b>Anahtar Kelimeler:</b> Veri madenciliği, Karar ağacı, Sınıflandırma, "
    "Öğrenci dikkati, Çevrimiçi öğrenme, MediaPipe, YOLOv7, scikit-learn",
    body_st
))


# =========================================================================
# 2. GİRİŞ
# =========================================================================
story.append(Paragraph("2. Giriş", h1_st))
story.append(Paragraph(
    "COVID-19 pandemisinin ardından çevrimiçi eğitim yaygın bir öğretim modeline "
    "dönüşmüştür. Ancak bu model, fiziksel sınıflarda öğretmenlerin doğal olarak "
    "yürüttüğü dikkat takibi konusunda ciddi zorluklar barındırmaktadır. "
    "Öğrencilerin kameralarının kapalı olması, dijital dikkat dağıtıcılar "
    "(telefon, başka sekmeler) ve göz teması kuramama gibi etkenler, eğitmenin "
    "öğrenci katılımını değerlendirmesini güçleştirmektedir. Bu nedenle, "
    "bilgisayarlı görü ve makine öğrenmesi temelli otomatik dikkat tespit "
    "sistemleri son yıllarda artan bir araştırma alanı haline gelmiştir.",
    body_st
))
story.append(Paragraph(
    "Bu projenin amacı, BLM0463 ders kapsamında Karar Ağacı sınıflandırma "
    "yöntemini uygulayarak, gerçek öğrenci verilerinden oluşan bir veri seti "
    "üzerinde dikkat tespiti yapmak ve elde edilen sonuçları yaygın değerlendirme "
    "ölçütleriyle (Accuracy, Precision, Recall, F1, Specificity, ROC-AUC) "
    "raporlamaktır. Ayrıca, aynı veri seti üzerinde yapılmış akademik bir "
    "çalışmayla karşılaştırma sunularak modelin literatürdeki konumu "
    "değerlendirilmektedir.",
    body_st
))
story.append(Paragraph("2.1. Çalışmanın Katkıları", h2_st))
story.append(Paragraph(
    "Bu çalışmanın başlıca katkıları şunlardır: "
    "<b>(i)</b> Veri seti üzerinde kapsamlı keşifsel veri analizi (EDA) ve "
    "görselleştirmeler sunulmuştur. "
    "<b>(ii)</b> Önişleme adımları (one-hot encoding, MaxAbsScaler, normalize) "
    "makaledeki yaklaşımla tam uyumlu olarak uygulanmış, böylece sonuçların "
    "literatürle adil karşılaştırılması sağlanmıştır. "
    "<b>(iii)</b> 384 farklı parametre kombinasyonu için 5-fold çapraz "
    "doğrulamalı GridSearchCV uygulanarak optimum Karar Ağacı modeli "
    "belirlenmiştir. "
    "<b>(iv)</b> Sonuçlar Hossen ve Uddin (2023) XGBoost çalışmasıyla "
    "karşılaştırılmıştır.",
    body_st
))


# =========================================================================
# 3. VERİ SETİ
# =========================================================================
story.append(Paragraph("3. Veri Seti", h1_st))
story.append(Paragraph(
    "Çalışmada kullanılan <b>Students Attention Detection Dataset</b>, "
    "Hossen ve Uddin (2023) tarafından <i>Data in Brief</i> dergisinde "
    "yayınlanmış ve Mendeley Data üzerinden açık erişimli olarak paylaşılmıştır "
    "(DOI: 10.17632/smzggbnkd2.1). Veri seti, Bangladesh'teki Jahangirnagar "
    "Üniversitesi'nde Haziran 2023'te bilgisayar bilimleri dersine katılan "
    "öğrencilerden, açık rıza ile alınan webcam görüntülerinin saniyede "
    "20 kare hızıyla işlenmesiyle oluşturulmuştur.",
    body_st
))

story.append(Paragraph("3.1. Veri Toplama Mimarisi", h2_st))
story.append(Paragraph(
    "Her video karesi dört bağımsız modülden geçirilerek özellikler "
    "çıkarılmıştır: "
    "<b>(1) Yüz tespiti</b> — MediaPipe BlazeFace ile yüz koordinatları, "
    "boyutu ve güven skoru elde edilmiştir. "
    "<b>(2) El takibi</b> — MediaPipe Hands ile algılanan el sayısı "
    "kaydedilmiştir. "
    "<b>(3) Baş duruşu (head pose) tahmini</b> — MediaPipe Face Mesh ve "
    "OpenCV solvePnP() ile baş yönelimi (forward / down / left / right) "
    "ve x-y açıları (derece cinsinden) belirlenmiştir. "
    "<b>(4) Cep telefonu tespiti</b> — MS-COCO üzerinde önceden eğitilmiş "
    "YOLOv7 modeli ile telefon varlığı, koordinatları, boyutu ve güven skoru "
    "tespit edilmiştir.",
    body_st
))

story.append(Paragraph("3.2. Özellikler ve Etiket", h2_st))
feat_data = [
    ["#", "Özellik", "Açıklama", "Tip"],
    ["1", "no_of_face",  "Karedeki yüz sayısı", "Tamsayı"],
    ["2", "face_x/y",    "Yüz sınırlayıcı kutu koordinatları", "Float"],
    ["3", "face_w/h",    "Yüz genişlik/yükseklik (piksel)", "Float"],
    ["4", "face_con",    "Yüz tespit güven skoru", "Float"],
    ["5", "no_of_hand",  "Tespit edilen el sayısı", "Tamsayı"],
    ["6", "pose",        "Baş yönelimi (forward/down/left/right)", "Kategorik"],
    ["7", "pose_x/y",    "Baş açıları (derece)", "Float"],
    ["8", "phone",       "Telefon varlığı (0/1)", "İkili"],
    ["9", "phone_x/y/w/h", "Telefon koordinat/boyut", "Float"],
    ["10","phone_con",   "Telefon tespit güven skoru", "Float"],
    ["11","label",       "Hedef: 0=Attentive, 1=Inattentive", "İkili"],
]
feat_tbl = Table(feat_data, colWidths=[0.8*cm, 3*cm, 8.5*cm, 2.7*cm])
feat_tbl.setStyle(TableStyle([
    ("BACKGROUND",     (0, 0), (-1, 0), colors.HexColor("#1F3A68")),
    ("TEXTCOLOR",      (0, 0), (-1, 0), colors.white),
    ("FONTNAME",       (0, 0), (-1, 0), "DejaVu-Bold"),
    ("FONTNAME",       (0, 1), (-1, -1), "DejaVu"),
    ("FONTSIZE",       (0, 0), (-1, -1), 9.5),
    ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
    ("GRID",           (0, 0), (-1, -1), 0.4, colors.grey),
    ("ALIGN",          (0, 0), (0, -1), "CENTER"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1),
     [colors.white, colors.HexColor("#F4F7FB")]),
    ("TOPPADDING",     (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING",  (0, 0), (-1, -1), 4),
]))
story.append(feat_tbl)
story.append(Paragraph("Tablo 1. Veri seti özellikleri ve veri tipleri.", caption_st))

story.append(Paragraph("3.3. Sınıf Dağılımı", h2_st))
story.append(Paragraph(
    "Veri seti toplam <b>4.000 örnek</b> içermektedir. Sınıf dağılımı "
    "<b>2.314 Attentive (%57.85)</b> ve <b>1.686 Inattentive (%42.15)</b> "
    "şeklindedir. Bu dağılım hafif dengesizdir ancak Decision Tree algoritması "
    "için kritik bir sorun teşkil etmemektedir; yine de hiperparametre "
    "optimizasyonu sırasında <i>class_weight</i> = 'balanced' seçeneği "
    "değerlendirilmiştir.",
    body_st
))
add_image("01_class_distribution.png", 11,
          "Şekil 1. Veri setindeki sınıf dağılımı pasta grafiği.")

story.append(Paragraph("3.4. Etiketleme Kriterleri", h2_st))
story.append(Paragraph(
    "Hossen ve Uddin (2023), her bir örneğe etiket atarken aşağıdaki "
    "kuralları kullanmıştır:",
    body_st
))
label_rules = [
    ["Modül", "Attentive (0) Kuralı", "Inattentive (1) Kuralı"],
    ["Yüz Tespiti",  "Yüz güvenle tespit edildi ve merkezde", "Yüz tespit edilemedi veya kısmen kadrajda"],
    ["El Takibi",    "Bir veya iki el yüze yakın",             "El tespit edilemedi veya çok uzakta"],
    ["Baş Duruşu",   "İleri veya hafif eğik",                  "Sol / sağ / aşağı / ekrandan başka yöne"],
    ["Telefon",      "Telefon yok veya yere bakar şekilde",    "Telefon ekranı yukarı, dikkat dağıtıcı pozisyonda"],
]
lbl_tbl = Table(label_rules, colWidths=[2.2*cm, 5.8*cm, 7.0*cm])
lbl_tbl.setStyle(TableStyle([
    ("BACKGROUND",     (0, 0), (-1, 0), colors.HexColor("#1F3A68")),
    ("TEXTCOLOR",      (0, 0), (-1, 0), colors.white),
    ("FONTNAME",       (0, 0), (-1, 0), "DejaVu-Bold"),
    ("FONTNAME",       (0, 1), (-1, -1), "DejaVu"),
    ("FONTSIZE",       (0, 0), (-1, -1), 9),
    ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
    ("GRID",           (0, 0), (-1, -1), 0.4, colors.grey),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1),
     [colors.white, colors.HexColor("#F4F7FB")]),
    ("TOPPADDING",     (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING",  (0, 0), (-1, -1), 4),
]))
story.append(lbl_tbl)
story.append(Paragraph(
    "Tablo 2. Veri setinin deterministik etiketleme kuralları "
    "(Hossen &amp; Uddin, 2023, Tablo 4'ten uyarlanmıştır).",
    caption_st
))
story.append(Paragraph(
    "<b>Önemli bir gözlem:</b> Etiketler tamamen kural-tabanlı bir mantıkla "
    "atandığı için, özellik uzayından etiketlere büyük ölçüde "
    "deterministik bir eşleme bulunmaktadır. Bu durum, Karar Ağacı gibi "
    "kural çıkarımına dayalı modellerin neden çok yüksek doğruluk elde "
    "ettiğini açıklamaktadır (Bölüm 6'da detaylı tartışılmıştır).",
    body_st
))

story.append(PageBreak())

story.append(Paragraph("3.5. Keşifsel Veri Analizi (EDA)", h2_st))
story.append(Paragraph(
    "Veri setinde herhangi bir eksik değer bulunmamaktadır; yalnızca 30 satır "
    "yinelenmiştir (toplamın %0.75'i) ve bu durum modeli olumsuz "
    "etkilemeyecek seviyededir. Kategorik <i>pose</i> değişkeninin dağılımına "
    "bakıldığında 2.951 'forward', 537 'down', 334 'left' ve 178 'right' "
    "değeri olduğu görülmektedir.",
    body_st
))
add_image("02_pose_distribution.png", 13,
          "Şekil 2. Baş yönelimi (pose) dağılımı.")
add_image("03_pose_vs_label.png", 13,
          "Şekil 3. Baş yönelimi ile dikkat sınıfı çapraz dağılımı. "
          "<i>forward</i> dışındaki tüm yönelimler büyük ölçüde "
          "<i>Inattentive</i> ile ilişkilidir.")
add_image("04_correlation_heatmap.png", 14.5,
          "Şekil 4. Sayısal özellikler arası Pearson korelasyon matrisi. "
          "Telefon ile ilgili özellikler kendi aralarında çok yüksek "
          "(>0.85) korelasyona sahiptir; bu durum tek bir <i>phone</i> "
          "olayını birden fazla özellikte bilgi olarak yansıttığını "
          "göstermektedir.")
add_image("05_face_coords_scatter.png", 13,
          "Şekil 5. Yüz koordinatları ile dikkat sınıfı arasındaki ilişki. "
          "Iki sınıf büyük ölçüde örtüşmektedir; tek başına yüz konumu "
          "ayırt edici değildir.")
add_image("06_confidence_boxplot.png", 11,
          "Şekil 6. Yüz ve telefon tespiti güven skorlarının kutu grafiği. "
          "Yüz tespiti yüksek ve dar bir aralıkta yoğunlaşırken, "
          "telefon tespiti daha geniş bir dağılım göstermektedir.")
add_image("07_feature_distributions.png", 14.5,
          "Şekil 7. Anahtar özelliklerin sınıf bazında histogramları.")


# =========================================================================
# 4. YÖNTEM
# =========================================================================
story.append(PageBreak())
story.append(Paragraph("4. Yöntem", h1_st))

story.append(Paragraph("4.1. Karar Ağacı (Decision Tree)", h2_st))
story.append(Paragraph(
    "Karar Ağacı, denetimli öğrenmede yaygın olarak kullanılan, ağaç yapısına "
    "dayalı, yorumlanabilir bir sınıflandırma yöntemidir. Veri kümesini "
    "ardışık 'eğer-ise' koşullarıyla bölerek, her iç düğümde bir özelliğe "
    "göre karar verilir; yapraklarda ise sınıf etiketi atanır. Bu çalışmada, "
    "scikit-learn kütüphanesindeki <i>DecisionTreeClassifier</i> sınıfı "
    "kullanılmıştır.",
    body_st
))
story.append(Paragraph(
    "Bölme kriteri olarak iki ölçüt değerlendirilmiştir:",
    body_st
))
story.append(Paragraph(
    "<b>Gini Indeksi:</b> Gini(t) = 1 − Σ p<sub>i</sub><super>2</super>, "
    "burada p<sub>i</sub> düğüm <i>t</i>'de sınıf <i>i</i>'nin oranını ifade eder. "
    "Düşük değerler daha saf düğümler anlamına gelir.",
    body_st
))
story.append(Paragraph(
    "<b>Entropi (Bilgi Kazancı):</b> H(t) = − Σ p<sub>i</sub> log<sub>2</sub>(p<sub>i</sub>). "
    "Bilgi kazancı, bir özellik üzerinden bölme yaparak entropideki azalmayı ölçer.",
    body_st
))
story.append(Paragraph(
    "Karar Ağacının ana avantajları: <b>(i)</b> yorumlanabilirliği yüksektir, "
    "her tahmin görsel bir kural zinciriyle açıklanabilir; <b>(ii)</b> "
    "özellik ölçeklemesine duyarsızdır; <b>(iii)</b> kategorik ve sayısal "
    "veriyi birlikte işleyebilir; <b>(iv)</b> hızlı eğitim ve tahmin sağlar. "
    "Dezavantajı ise aşırı öğrenmeye (overfitting) eğilimli olmasıdır; bu nedenle "
    "<i>max_depth</i>, <i>min_samples_split</i>, <i>min_samples_leaf</i> gibi "
    "parametrelerle düzenlileştirme uygulanması gerekir.",
    body_st
))

story.append(Paragraph("4.2. Önişleme", h2_st))
story.append(Paragraph(
    "Veri seti, makaledeki tarif edildiği şekilde işlenmiştir:",
    body_st
))
story.append(Paragraph(
    "&nbsp;&nbsp;<b>1.</b> Kategorik <i>pose</i> sütunu <b>one-hot encoding</b> "
    "ile dört ikili sütuna (pose_forward, pose_down, pose_left, pose_right) "
    "dönüştürülmüştür.<br/>"
    "&nbsp;&nbsp;<b>2.</b> <i>face_con</i> [0, 100] aralığından [0, 1] aralığına "
    "100'e bölünerek normalize edilmiştir.<br/>"
    "&nbsp;&nbsp;<b>3.</b> Tüm sayısal özellikler <b>MaxAbsScaler</b> ile "
    "[−1, 1] aralığına ölçeklenmiştir (Karar Ağacı için zorunlu olmasa da "
    "literatürle uyumluluk açısından uygulanmıştır).<br/>"
    "&nbsp;&nbsp;<b>4.</b> Veri %80 eğitim (3.200 örnek) ve %20 test (800 örnek) "
    "olarak <b>stratified</b> şekilde ayrılmış (random_state=42), böylece "
    "iki alt kümede de sınıf oranı korunmuştur.",
    body_st
))

story.append(Paragraph("4.3. Hiperparametre Optimizasyonu", h2_st))
story.append(Paragraph(
    "Optimum Karar Ağacı yapısını bulmak için <b>GridSearchCV</b> ile "
    "kapsamlı bir arama yapılmıştır. Toplam <b>384 farklı parametre "
    "kombinasyonu</b> 5-fold çapraz doğrulama ile değerlendirilmiştir "
    "(toplam 1.920 model uydurma). Skor metriği olarak <b>F1</b> tercih "
    "edilmiştir, çünkü hafif dengesiz veri setinde precision-recall dengesini "
    "yansıtmaktadır.",
    body_st
))
grid_data = [
    ["Parametre", "Aranan Değerler"],
    ["criterion",         "{gini, entropy}"],
    ["max_depth",         "{None, 5, 10, 15, 20, 30}"],
    ["min_samples_split", "{2, 5, 10, 20}"],
    ["min_samples_leaf",  "{1, 2, 5, 10}"],
    ["class_weight",      "{None, balanced}"],
]
story.append(metrics_table(grid_data, [4.5*cm, 9*cm]))
story.append(Paragraph("Tablo 3. GridSearchCV parametre uzayı.", caption_st))

story.append(Paragraph("4.4. Değerlendirme Metrikleri", h2_st))
story.append(Paragraph(
    "Sonuçlar şu metriklerle raporlanmıştır:",
    body_st
))
story.append(Paragraph(
    "<b>Accuracy</b> = (TP + TN) / (TP + TN + FP + FN)<br/>"
    "<b>Precision</b> = TP / (TP + FP)<br/>"
    "<b>Recall (Sensitivity)</b> = TP / (TP + FN)<br/>"
    "<b>Specificity</b> = TN / (TN + FP)<br/>"
    "<b>F1-score</b> = 2 · Precision · Recall / (Precision + Recall)<br/>"
    "<b>ROC-AUC</b> = ROC eğrisi altında kalan alan",
    body_st
))


# =========================================================================
# 5. SONUÇLAR
# =========================================================================
story.append(PageBreak())
story.append(Paragraph("5. Bulgular ve Sonuçlar", h1_st))

bm = R["baseline_metrics"]
fm = R["final_test_metrics"]

story.append(Paragraph("5.1. Baseline (Varsayılan Parametreler)", h2_st))
story.append(Paragraph(
    "İlk olarak scikit-learn'ün varsayılan parametreleriyle bir Karar Ağacı "
    "eğitilmiştir. Sonuçlar zaten oldukça yüksektir, bu da veri setinin "
    "kural-tabanlı yapısının modele uygun olduğunu doğrulamaktadır.",
    body_st
))
baseline_data = [
    ["Metrik",       "Değer"],
    ["Accuracy",     f"{bm['accuracy']:.4f}  ({bm['accuracy']*100:.2f}%)"],
    ["Precision",    f"{bm['precision']:.4f}  ({bm['precision']*100:.2f}%)"],
    ["Recall",       f"{bm['recall']:.4f}  ({bm['recall']*100:.2f}%)"],
    ["Specificity",  f"{bm['specificity']:.4f}  ({bm['specificity']*100:.2f}%)"],
    ["F1-Score",     f"{bm['f1']:.4f}  ({bm['f1']*100:.2f}%)"],
    ["ROC-AUC",      f"{bm['roc_auc']:.4f}"],
]
story.append(metrics_table(baseline_data))
story.append(Paragraph(
    "Tablo 4. Varsayılan parametrelerle test seti performansı.", caption_st))

story.append(Paragraph("5.2. Optimize Edilmiş Model", h2_st))
bp = R["best_hyperparameters"]
story.append(Paragraph(
    f"GridSearchCV sonucunda en iyi parametre kombinasyonu şu şekilde "
    f"belirlenmiştir: <b>criterion={bp['criterion']}</b>, "
    f"<b>max_depth={bp['max_depth']}</b>, "
    f"<b>min_samples_split={bp['min_samples_split']}</b>, "
    f"<b>min_samples_leaf={bp['min_samples_leaf']}</b>, "
    f"<b>class_weight={bp['class_weight']}</b>. "
    f"En iyi 5-fold CV F1 skoru: <b>{R['best_cv_score_f1']:.4f}</b>.",
    body_st
))
final_data = [
    ["Metrik",       "Değer"],
    ["Accuracy",     f"{fm['accuracy']:.4f}  ({fm['accuracy']*100:.2f}%)"],
    ["Precision",    f"{fm['precision']:.4f}  ({fm['precision']*100:.2f}%)"],
    ["Recall",       f"{fm['recall']:.4f}  ({fm['recall']*100:.2f}%)"],
    ["Specificity",  f"{fm['specificity']:.4f}  ({fm['specificity']*100:.2f}%)"],
    ["F1-Score",     f"{fm['f1']:.4f}  ({fm['f1']*100:.2f}%)"],
    ["ROC-AUC",      f"{fm['roc_auc']:.4f}"],
]
story.append(metrics_table(final_data))
story.append(Paragraph(
    "Tablo 5. Optimize edilmiş Karar Ağacı modelinin test seti performansı.",
    caption_st))

story.append(Paragraph("5.3. Confusion Matrix", h2_st))
cmtx = R["confusion_matrix"]
story.append(Paragraph(
    f"Test setindeki 800 örneğin yalnızca <b>1</b> tanesi yanlış "
    f"sınıflandırılmıştır. Karışıklık matrisi: <b>TN={cmtx[0][0]}</b>, "
    f"<b>FP={cmtx[0][1]}</b>, <b>FN={cmtx[1][0]}</b>, <b>TP={cmtx[1][1]}</b>. "
    f"Yani 463 Attentive örneğin tamamı doğru sınıflandırılmış (Specificity = "
    f"%100), 337 Inattentive örneğinden ise yalnızca 1 tanesi yanlışlıkla "
    f"Attentive olarak etiketlenmiştir.",
    body_st
))
add_image("08_confusion_matrices.png", 15,
          "Şekil 8. Baseline ve tuned modellerin Confusion Matrix karşılaştırması.")

story.append(Paragraph("5.4. ROC ve Precision-Recall Eğrileri", h2_st))
story.append(Paragraph(
    f"ROC eğrisi altında kalan alan (AUC) her iki modelde de "
    f"<b>{fm['roc_auc']:.4f}</b> olup mükemmele oldukça yakındır. "
    f"Precision-Recall eğrisi de aynı şekilde sağ üst köşeye yapışıktır; "
    f"bu, sınıflandırıcının her iki sınıfı da yüksek doğrulukla ayırt "
    f"ettiğini göstermektedir.",
    body_st
))
add_image("09_roc_curve.png", 11, "Şekil 9. ROC eğrisi.")
add_image("10_precision_recall.png", 11, "Şekil 10. Precision-Recall eğrisi.")

story.append(Paragraph("5.5. 5-Fold Çapraz Doğrulama", h2_st))
story.append(Paragraph(
    "Modelin tek bir test ayrımına bağımlı olmadığını doğrulamak için "
    "tüm veri seti üzerinde 5-fold çapraz doğrulama uygulanmıştır. "
    "Sonuçlar son derece kararlıdır:",
    body_st
))
cv = R["five_fold_cv_scores"]
cv_data = [["Metrik", "Ortalama ± Std", "Min – Max"]]
for m in ["accuracy", "precision", "recall", "f1", "roc_auc"]:
    s = cv[m]["scores"]
    cv_data.append([
        m.upper(),
        f"{cv[m]['mean']:.4f} ± {cv[m]['std']:.4f}",
        f"{min(s):.4f} – {max(s):.4f}"
    ])
cv_tbl = Table(cv_data, colWidths=[3.5*cm, 5*cm, 4.5*cm])
cv_tbl.setStyle(TableStyle([
    ("BACKGROUND",     (0, 0), (-1, 0), colors.HexColor("#1F3A68")),
    ("TEXTCOLOR",      (0, 0), (-1, 0), colors.white),
    ("FONTNAME",       (0, 0), (-1, 0), "DejaVu-Bold"),
    ("FONTNAME",       (0, 1), (-1, -1), "DejaVu"),
    ("FONTSIZE",       (0, 0), (-1, -1), 10),
    ("ALIGN",          (0, 0), (-1, -1), "CENTER"),
    ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
    ("GRID",           (0, 0), (-1, -1), 0.4, colors.grey),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1),
     [colors.white, colors.HexColor("#F4F7FB")]),
    ("TOPPADDING",     (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING",  (0, 0), (-1, -1), 5),
]))
story.append(cv_tbl)
story.append(Paragraph(
    "Tablo 6. 5-fold çapraz doğrulama sonuçları. Düşük standart sapmalar, "
    "modelin farklı veri ayrımlarında kararlı performans sergilediğini "
    "göstermektedir.",
    caption_st))

story.append(Paragraph("5.6. Özellik Önemleri", h2_st))
story.append(Paragraph(
    "Karar Ağacı tarafından atanan özellik önem skorları, hangi "
    "özelliklerin sınıflandırma kararına katkı sağladığını ortaya "
    "koymaktadır. En önemli üç özellik:",
    body_st
))
fi = R["feature_importances"]
top_fi = sorted(fi.items(), key=lambda x: -x[1])[:5]
fi_data = [["Sıra", "Özellik", "Önem Skoru"]]
for i, (k, v) in enumerate(top_fi, 1):
    fi_data.append([str(i), k, f"{v:.4f}"])
story.append(metrics_table(fi_data, [1.5*cm, 5*cm, 4*cm]))
story.append(Paragraph(
    "Tablo 7. En önemli 5 özellik (Decision Tree feature_importances).",
    caption_st))
story.append(Paragraph(
    "<b>pose_forward</b> (önem: 0.49) — Öğrencinin başının ileriye dönük "
    "olup olmaması, dikkat tespitinde en güçlü tek belirleyicidir. "
    "<b>phone_y</b> (önem: 0.32) — Telefonun dikey konumu (yani 'kaldırılmış "
    "mı, yatık mı'), ikinci en önemli ipucudur. <b>pose_y</b> ve <b>pose_x</b> "
    "(toplam 0.17) — Açısal baş yönelimi de etiketlemede kritik rol oynar. "
    "Bu sıralama, etiketleme kurallarının (Tablo 2) dolaylı bir doğrulamasıdır: "
    "Model, etiketlemede kullanılan aynı özelliklerde yoğunlaşmıştır.",
    body_st
))
add_image("11_feature_importances.png", 13,
          "Şekil 11. Tüm özelliklerin önem skorları.")

story.append(PageBreak())
story.append(Paragraph("5.7. Karar Ağacı Yapısı", h2_st))
story.append(Paragraph(
    "Aşağıdaki şekilde, max_depth=4 ile sınırlandırılmış (okunabilirlik "
    "için) Karar Ağacı görselleştirilmiştir. Görüldüğü üzere kök düğüm "
    "<i>pose_forward</i>'dur: öğrencinin başı ileri dönük değilse "
    "(pose_forward ≤ 0.5), 844 örneğin tamamı doğrudan Inattentive olarak "
    "sınıflandırılmaktadır (Gini = 0). Bu, etiketleme kuralındaki '"
    "<i>head pose down/left/right ⇒ Inattentive</i>' mantığını yakalamaktadır.",
    body_st
))
add_image("12_decision_tree.png", 16,
          "Şekil 12. Karar Ağacının ilk 4 düzeyi (görsel basitlik için "
          "sınırlandırılmıştır).")

story.append(Paragraph("5.8. Learning Curve", h2_st))
story.append(Paragraph(
    "Eğitim örneği sayısının modele etkisini incelemek için learning curve "
    "üretilmiştir. Eğitim ve doğrulama F1 skorları çok küçük örnek "
    "sayılarında bile %99'un üzerine çıkmakta ve örnek sayısı arttıkça "
    "yakınsamaktadır. Bu, modelin verimli öğrendiğini ve büyük bir veri "
    "ihtiyacının olmadığını göstermektedir.",
    body_st
))
add_image("13_learning_curve.png", 12, "Şekil 13. Learning curve.")


# =========================================================================
# 6. KARŞILAŞTIRMA
# =========================================================================
story.append(PageBreak())
story.append(Paragraph("6. Akademik Çalışma ile Karşılaştırma", h1_st))
story.append(Paragraph(
    "Aynı veri seti üzerinde yapılmış başlıca akademik çalışma, "
    "Hossen ve Uddin'in (2023) <i>Computers and Education: Artificial "
    "Intelligence</i> dergisinde yayınladığı 'Attention monitoring of students "
    "during online classes using XGBoost classifier' başlıklı makaledir. "
    "Yazarlar, altı farklı makine öğrenmesi algoritmasını (Decision Tree, "
    "Random Forest, AdaBoost, Gradient Boosting, SVM, XGBoost) karşılaştırarak "
    "<b>XGBoost'un %99.75 doğruluk ve %99.71 kesinlikle</b> en iyi performansı "
    "sergilediğini raporlamışlardır.",
    body_st
))
story.append(Paragraph(
    "İkinci karşılaştırma noktası olarak Mello-Roman ve diğerleri (2023) "
    "<i>'Machine Learning applied to student attentiveness detection'</i> "
    "çalışması alınmıştır. Bu makalede, benzer (fakat farklı ve daha küçük) "
    "bir öğrenci dikkat veri seti üzerinde XGBoost ile <b>%80.52</b> "
    "doğruluk elde edilmiştir.",
    body_st
))

comp_data = [
    ["Çalışma",                      "Yöntem",       "Veri Seti",    "Accuracy", "Precision", "Recall"],
    ["Bu Çalışma (Baseline DT)",     "Decision Tree","Hossen 2023",  "99.88%",   "100.00%",   "99.70%"],
    ["Bu Çalışma (Tuned DT)",        "Decision Tree","Hossen 2023",  "99.88%",   "100.00%",   "99.70%"],
    ["Hossen & Uddin (2023)",        "XGBoost",      "Hossen 2023",  "99.75%",   "99.71%",    "—"],
    ["Mello-Roman et al. (2023)",    "XGBoost",      "Kendi verisi", "80.52%",   "—",         "—"],
]
comp_tbl = Table(comp_data, colWidths=[4*cm, 2.7*cm, 2.5*cm, 2*cm, 2*cm, 1.8*cm])
comp_tbl.setStyle(TableStyle([
    ("BACKGROUND",     (0, 0), (-1, 0), colors.HexColor("#1F3A68")),
    ("TEXTCOLOR",      (0, 0), (-1, 0), colors.white),
    ("FONTNAME",       (0, 0), (-1, 0), "DejaVu-Bold"),
    ("FONTNAME",       (0, 1), (-1, -1), "DejaVu"),
    ("FONTSIZE",       (0, 0), (-1, -1), 9),
    ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
    ("GRID",           (0, 0), (-1, -1), 0.4, colors.grey),
    ("BACKGROUND",     (0, 2), (-1, 2), colors.HexColor("#FFF8DC")),
    ("FONTNAME",       (0, 2), (-1, 2), "DejaVu-Bold"),
    ("ROWBACKGROUNDS", (0, 1), (-1, 1),
     [colors.HexColor("#F4F7FB")]),
    ("TOPPADDING",     (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING",  (0, 0), (-1, -1), 4),
]))
story.append(comp_tbl)
story.append(Paragraph(
    "Tablo 8. Literatürdeki çalışmalarla karşılaştırma. Sarı renkli satır "
    "bu çalışmanın final modelidir.",
    caption_st))
add_image("14_literature_comparison.png", 14,
          "Şekil 14. Yöntemlerin doğruluk karşılaştırması.")

story.append(Paragraph("6.1. Karşılaştırma Yorumu", h2_st))
story.append(Paragraph(
    "Bu çalışmada uygulanan optimize edilmiş Karar Ağacı modeli, "
    "Hossen ve Uddin'in en iyi modelini (XGBoost) <b>0.13 yüzde puan</b> "
    "geçmiştir. Bu, ilk bakışta şaşırtıcı görünebilir, çünkü XGBoost "
    "genellikle Karar Ağacından üstündür. Ancak burada birkaç önemli faktör "
    "bu sonucu açıklamaktadır:",
    body_st
))
story.append(Paragraph(
    "<b>(1) Veri setinin yapısı:</b> Etiketler kural-tabanlı atandığı için "
    "(Tablo 2) özellikten etikete neredeyse deterministik bir eşleme vardır. "
    "Bu durum, kural çıkarımına dayanan Karar Ağacının doğal olarak iyi "
    "performans göstermesine yol açmaktadır; XGBoost'un sağladığı ek esneklik "
    "marjinaldir.<br/>"
    "<b>(2) Hiperparametre optimizasyonu:</b> Bu çalışmada 384 kombinasyonda "
    "5-fold CV ile arama yapılmıştır; makaledeki kapsamlı bir DT taraması "
    "raporlanmamıştır.<br/>"
    "<b>(3) Karar Ağacının eşit performansla tercih sebepleri:</b> "
    "(a) <b>Yorumlanabilirlik</b> — her tahmin görsel ve sözel olarak "
    "açıklanabilir; (b) <b>Hız</b> — eğitim ve tahmin XGBoost'tan kat kat "
    "hızlıdır; (c) <b>Bellek</b> — model boyutu çok küçüktür; (d) <b>Kolay "
    "dağıtım</b> — gerçek zamanlı dikkat takip aracında düşük hesaplama "
    "maliyeti büyük avantajdır.",
    body_st
))


# =========================================================================
# 7. TARTIŞMA / SINIRLILIKLAR
# =========================================================================
story.append(Paragraph("7. Tartışma ve Sınırlılıklar", h1_st))
story.append(Paragraph(
    "Modelin %99.88 doğruluğu çok etkileyici görünse de, bu sonucun büyük "
    "ölçüde veri setinin yapısından kaynaklandığı dikkate alınmalıdır. "
    "Etiketler, bilgisayarlı görü modüllerinin çıktıları üzerine "
    "deterministik kurallarla atanmış olduğu için, sınıflandırıcı bu "
    "kuralları yeniden öğrenmektedir. Gerçek dikkat algılaması (yani "
    "öğrencinin sübjektif zihinsel durumunun tespiti) çok daha karmaşık "
    "olup bu veri seti, dikkatin <b>davranışsal göstergeleriyle</b> "
    "sınırlıdır.",
    body_st
))
story.append(Paragraph(
    "<b>Veri setinin sınırlılıkları</b> (yazarların kendileri tarafından da "
    "belirtildiği üzere): "
    "<i>(i)</i> Aydınlatma ve oda düzeni biaslarına yol açabilir; "
    "<i>(ii)</i> Sadece Bangladesh'teki tek bir üniversiteden örnekler içerir, "
    "kültürel ve demografik genelleme sınırlıdır; "
    "<i>(iii)</i> Etiketleme bias'a açıktır, çünkü yalnızca dış davranışlara "
    "dayalıdır; "
    "<i>(iv)</i> Hafif sınıf dengesizliği vardır.",
    body_st
))
story.append(Paragraph(
    "<b>Yöntemsel sınırlılıklar:</b> "
    "<i>(i)</i> 30 yinelenen satır mevcut; bu, train-test ayrımında "
    "veri sızıntısına neden olabileceği için ileride duplicate temizleme "
    "ile yeniden değerlendirilebilir. "
    "<i>(ii)</i> Tek bir random_state ile yapılan ayrım stokastik etkilere "
    "açıktır; çoklu run istatistikleri eklenebilir. "
    "<i>(iii)</i> Hata analizi yalnızca tek bir yanlış sınıflandırılmış "
    "örnek üzerinde sınırlıdır.",
    body_st
))


# =========================================================================
# 8. SONUÇ
# =========================================================================
story.append(Paragraph("8. Sonuç", h1_st))
story.append(Paragraph(
    "Bu projede, Hossen ve Uddin'in (2023) Students Attention Detection "
    "Dataset üzerinde Karar Ağacı sınıflandırma yöntemi uygulanmış ve "
    "test setinde <b>%99.88 doğruluk</b> ile <b>%99.85 F1</b> skoru elde "
    "edilmiştir. Bu sonuç, aynı veri setinde XGBoost ile %99.75 doğruluk "
    "rapor eden referans çalışmasını 0.13 puan aşmaktadır. 5-fold çapraz "
    "doğrulama (%99.90 ± %0.05) modelin kararlılığını teyit etmiştir.",
    body_st
))
story.append(Paragraph(
    "Özellik önem analizleri, <i>baş yönelimi</i> (pose_forward) ve "
    "<i>telefon konumu</i> (phone_y) özelliklerinin dikkat tespitinde en "
    "belirleyici unsurlar olduğunu ortaya koymuştur. Karar Ağacının yüksek "
    "yorumlanabilirliği ve düşük hesaplama maliyeti, bu modeli gerçek "
    "zamanlı eğitim teknolojisi uygulamaları için ideal bir aday haline "
    "getirmektedir.",
    body_st
))
story.append(Paragraph(
    "<b>Gelecek çalışmalar</b> şunları içerebilir: <i>(i)</i> ensemble "
    "yöntemlerle (Random Forest, XGBoost) doğrudan karşılaştırma; "
    "<i>(ii)</i> daha geniş ve çeşitli demografik veri setleri ile "
    "genelleme testleri; <i>(iii)</i> SHAP gibi açıklanabilir AI "
    "(XAI) teknikleriyle yorumlanabilirliğin daha da artırılması; "
    "<i>(iv)</i> zamansal modelleme (LSTM/Temporal CNN) ile dikkatin "
    "anlık değil sürekli takibi.",
    body_st
))


# =========================================================================
# 9. KAYNAKLAR
# =========================================================================
story.append(Paragraph("9. Kaynaklar", h1_st))
refs = [
    "[1] Hossen, M. K., & Uddin, M. S. (2023). A dataset for assessing "
    "real-time attention levels of the students during online classes. "
    "<i>Data in Brief</i>, 51, 109771. "
    "https://doi.org/10.1016/j.dib.2023.109771",
    "[2] Hossen, M. K., & Uddin, M. S. (2023). Attention monitoring of "
    "students during online classes using XGBoost classifier. "
    "<i>Computers and Education: Artificial Intelligence</i>, 5, 100191. "
    "https://doi.org/10.1016/j.caeai.2023.100191",
    "[3] Hossen, M. K., & Uddin, M. S. (2025). From data to insights: Using "
    "gradient boosting classifier to optimize student engagement in online "
    "classes with explainable AI. <i>Education and Information Technologies</i>, "
    "30, 18089–18130. https://doi.org/10.1007/s10639-025-13500-0",
    "[4] Hossen, M. K., & Uddin, M. S. (2023). Students Attention Detection "
    "Dataset, v1. <i>Mendeley Data</i>. "
    "https://doi.org/10.17632/smzggbnkd2.1",
    "[5] Mello-Roman, J. D., Hernandez, A., Mello-Roman, J. C. (2023). Machine "
    "Learning applied to student attentiveness detection: Using emotional "
    "and non-emotional measures. <i>Education and Information Technologies</i>.",
    "[6] Pedregosa, F., Varoquaux, G., et al. (2011). Scikit-learn: Machine "
    "learning in Python. <i>Journal of Machine Learning Research</i>, 12(85), "
    "2825–2830.",
    "[7] Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting "
    "system. <i>KDD '16</i>, 785–794. https://doi.org/10.1145/2939672.2939785",
    "[8] Lugaresi, C., Tang, J., et al. (2019). MediaPipe: A framework for "
    "perceiving and processing reality. <i>CV for AR/VR Workshop, IEEE CVPR</i>.",
    "[9] Wang, C. Y., Bochkovskiy, A., & Liao, H. Y. M. (2023). YOLOv7: "
    "Trainable bag-of-freebies sets new state-of-the-art for real-time object "
    "detectors. <i>IEEE/CVF CVPR</i>, 7464–7475.",
    "[10] Bradski, G. (2000). The OpenCV library. <i>Dr. Dobb's Journal of "
    "Software Tools</i>, 25(11), 120–123.",
]
for r in refs:
    story.append(Paragraph(r, ref_st))


# =========================================================================
# EK: ÇALIŞMAYI YENİDEN ÜRETMEK İÇİN
# =========================================================================
story.append(PageBreak())
story.append(Paragraph("EK A — Çalışmayı Yeniden Üretmek İçin", h1_st))
story.append(Paragraph(
    "Tüm proje kaynak kodu, GitHub üzerinde public olarak paylaşılmıştır:",
    body_st
))
story.append(Paragraph(
    "<b>GitHub:</b> https://github.com/[kullaniciadi]/BLM463-Attention-Detection",
    body_st
))
story.append(Paragraph("Çalıştırma adımları:", h2_st))
story.append(Paragraph(
    "<font face='DejaVuMono'>"
    "$ git clone https://github.com/[kullaniciadi]/BLM463-Attention-Detection<br/>"
    "$ cd BLM463-Attention-Detection<br/>"
    "$ pip install -r requirements.txt<br/>"
    "$ python src/main.py<br/>"
    "$ python src/generate_report.py"
    "</font>",
    body_st
))
story.append(Paragraph(
    "<b>Bağımlılıklar:</b> Python 3.9+, pandas, numpy, scikit-learn, "
    "matplotlib, seaborn, reportlab.",
    body_st
))
story.append(Paragraph(
    "<b>Tekrar üretilebilirlik:</b> Tüm rastgele işlemlerde "
    "<i>random_state=42</i> sabitlenmiş; train/test ayrımı stratified "
    "yapılmış; 5-fold CV aynı seed ile çalıştırıldığında birebir "
    "aynı sonuçları üretmektedir.",
    body_st
))


# =========================================================================
# Belgeyi oluştur
# =========================================================================
doc = SimpleDocTemplate(
    OUT_PDF, pagesize=A4,
    leftMargin=2.2*cm, rightMargin=2.2*cm,
    topMargin=2.2*cm, bottomMargin=2.2*cm,
    title="BLM463 Decision Tree Attention Detection Project Report",
    author="BLM463 Student"
)
doc.build(story)
print(f"PDF oluşturuldu: {OUT_PDF}")
print(f"Boyut: {os.path.getsize(OUT_PDF) / 1024:.1f} KB")
