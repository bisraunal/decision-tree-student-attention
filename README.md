   #Karar Ağacı ile Çevrimiçi Derslerde Öğrenci Dikkat Tespiti

> **Öğrenci:** Büşra Ünal — 22360859084  
> **Ders:** BLM0463 Veri Madenciliğine Giriş — Dönem Projesi  
> **Yöntem:** Decision Tree (Karar Ağacı)  
> **Veri Seti:** [Students Attention Detection Dataset](https://data.mendeley.com/datasets/smzggbnkd2/1) (Hossen & Uddin, 2023)

## Proje Özeti

Bu projede, çevrimiçi derslere katılan öğrencilerin webcam görüntülerinden çıkarılan davranışsal özellikler (yüz tespiti, el takibi, baş duruşu, telefon tespiti) kullanılarak **dikkatli/dikkatsiz** sınıflandırması yapılmıştır. Karar Ağacı yöntemi uygulanmış ve **%99.88 test doğruluğu** elde edilmiştir.

## Sonuçlar

| Metrik       | Değer   |
|-------------|---------|
| Accuracy    | %99.88  |
| Precision   | %100.00 |
| Recall      | %99.70  |
| F1-Score    | %99.85  |
| Specificity | %100.00 |
| ROC-AUC     | 0.9985  |
| 5-fold CV   | %99.90 ± %0.05 |

### Literatür Karşılaştırması

| Çalışma | Yöntem | Accuracy |
|---------|--------|----------|
| **Bu çalışma** | **Decision Tree** | **%99.88** |
| Hossen & Uddin (2023) | XGBoost | %99.75 |
| Mello-Roman et al. (2023) | XGBoost | %80.52 |

## Proje Yapısı

```
BLM463-Attention-Detection/
├── attention_detection_dataset_v1.csv   # Veri seti
├── src/
│   ├── main.py                          # Ana analiz scripti (EDA + Model + Görselleştirme)
│   └── generate_report.py              # PDF rapor üretici
├── figures/                             # Üretilen tüm grafikler (14 adet)
│   ├── 01_class_distribution.png
│   ├── 02_pose_distribution.png
│   ├── 03_pose_vs_label.png
│   ├── 04_correlation_heatmap.png
│   ├── 05_face_coords_scatter.png
│   ├── 06_confidence_boxplot.png
│   ├── 07_feature_distributions.png
│   ├── 08_confusion_matrices.png
│   ├── 09_roc_curve.png
│   ├── 10_precision_recall.png
│   ├── 11_feature_importances.png
│   ├── 12_decision_tree.png
│   ├── 13_learning_curve.png
│   └── 14_literature_comparison.png
├── results/                             # Sonuç dosyaları
│   ├── results.json
│   ├── classification_report.txt
│   ├── tree_structure.txt
│   └── summary_stats.csv
├── BLM463_Proje_BusraUnal_22360859084.pdf  # Detaylı proje raporu (19 sayfa)
├── requirements.txt
└── README.md
```

## Kurulum ve Çalıştırma

```bash
# 1. Depoyu klonla
git clone https://github.com/bisraunal/BLM463-Attention-Detection.git
cd BLM463-Attention-Detection

# 2. Bağımlılıkları yükle
pip install -r requirements.txt

# 3. Ana analizi çalıştır (EDA + model eğitimi + görselleştirmeler)
python src/main.py

# 4. PDF raporu üret (opsiyonel)
python src/generate_report.py
```

## Bağımlılıklar

- Python 3.9+
- pandas, numpy
- scikit-learn
- matplotlib, seaborn
- reportlab (PDF üretimi için)

## Yöntem

1. **Veri Ön İşleme:** One-hot encoding (pose sütunu), MaxAbsScaler, face_con normalizasyonu
2. **Eğitim/Test Ayrımı:** %80/%20 stratified split (random_state=42)
3. **Hiperparametre Optimizasyonu:** GridSearchCV ile 384 kombinasyon, 5-fold CV, F1 skoru hedefli
4. **En İyi Parametreler:** criterion=gini, max_depth=None, min_samples_split=20, min_samples_leaf=1
5. **Değerlendirme:** Accuracy, Precision, Recall, Specificity, F1, ROC-AUC, Confusion Matrix

## Referanslar

- Hossen, M. K., & Uddin, M. S. (2023). A dataset for assessing real-time attention levels of the students during online classes. *Data in Brief*, 51, 109771.
- Hossen, M. K., & Uddin, M. S. (2023). Attention monitoring of students during online classes using XGBoost classifier. *Computers and Education: AI*, 5, 100191.

## Lisans

Bu proje akademik ödev amaçlıdır. Veri seti [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) lisansı altındadır.
