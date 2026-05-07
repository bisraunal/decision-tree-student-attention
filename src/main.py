"""
BLM0463 Veri Madenciliğine Giriş — Dönem Projesi
================================================
Sınıflandırma Yöntemi : Decision Tree
Veri Seti             : Students Attention Detection Dataset (Hossen & Uddin, 2023)
Platform              : Python 3 + scikit-learn

Bu script:
  1. Veri setini yükler ve keşifsel veri analizi (EDA) yapar
  2. Önişleme: pose için one-hot encoding, MaxAbsScaler ile ölçekleme
  3. %80-20 train/test split (makaledeki ayrımla aynı)
  4. Decision Tree modelini varsayılan ve tuned parametrelerle eğitir
  5. Çapraz doğrulama (5-fold) ile model güvenilirliğini test eder
  6. Tüm değerlendirme metriklerini hesaplar:
        Accuracy, Precision, Recall, F1, Specificity, ROC-AUC
  7. Görselleştirmeleri üretir:
        Sınıf dağılımı, korelasyon, confusion matrix, ROC, PR, ağaç,
        özellik önemleri, learning curve
  8. Tüm sonuçları figures/ ve results/ dizinlerine kaydeder
"""

import os
import json
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import (
    train_test_split, GridSearchCV, cross_val_score, StratifiedKFold, learning_curve
)
from sklearn.tree import DecisionTreeClassifier, plot_tree, export_text
from sklearn.preprocessing import MaxAbsScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
    roc_curve, precision_recall_curve, average_precision_score
)

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid", context="notebook")
np.random.seed(42)

# ----------------------------------------------------------------------------
# 0. Yollar
# ----------------------------------------------------------------------------
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(ROOT, "attention_detection_dataset_v1.csv")
FIG_DIR = os.path.join(ROOT, "figures")
RES_DIR = os.path.join(ROOT, "results")
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(RES_DIR, exist_ok=True)


def savefig(name):
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, name), dpi=150, bbox_inches="tight")
    plt.close()


# ----------------------------------------------------------------------------
# 1. Veri yükleme ve hızlı bakış
# ----------------------------------------------------------------------------
print("=" * 70)
print("1. VERİ YÜKLEME")
print("=" * 70)
df = pd.read_csv(DATA_PATH)
print(f"Veri seti boyutu  : {df.shape}")
print(f"Sütunlar          : {df.columns.tolist()}")
print(f"Eksik değer sayısı: {df.isnull().sum().sum()}")
print(f"Yinelenen satır   : {df.duplicated().sum()}")
print("\nİlk 5 satır:")
print(df.head())
print("\nHedef sınıf dağılımı:")
class_counts = df["label"].value_counts().sort_index()
print(class_counts)
print(f"  Attentive   (0): {class_counts[0]:>4} ({class_counts[0]/len(df)*100:.2f}%)")
print(f"  Inattentive (1): {class_counts[1]:>4} ({class_counts[1]/len(df)*100:.2f}%)")

# Özet istatistikleri kaydet
df.describe().to_csv(os.path.join(RES_DIR, "summary_stats.csv"))

# ----------------------------------------------------------------------------
# 2. Keşifsel Veri Analizi (EDA) görselleri
# ----------------------------------------------------------------------------
print("\n" + "=" * 70)
print("2. KEŞİFSEL VERİ ANALİZİ")
print("=" * 70)

# 2.1 Sınıf dağılımı pasta grafiği (makaledeki Fig. 1'in yeniden üretimi)
fig, ax = plt.subplots(figsize=(7, 7))
labels = ["Attentive (0)", "Inattentive (1)"]
colors = ["#4C9FE0", "#7FCB8F"]
ax.pie(
    class_counts.values, labels=labels, colors=colors, autopct="%1.1f%%",
    startangle=90, explode=(0.02, 0.02), shadow=True,
    textprops={"fontsize": 12, "fontweight": "bold"}
)
ax.set_title("Sınıf Dağılımı", fontsize=14, fontweight="bold")
savefig("01_class_distribution.png")
print("  -> 01_class_distribution.png")

# 2.2 Pose dağılımı
fig, ax = plt.subplots(figsize=(8, 5))
pose_counts = df["pose"].value_counts()
ax.bar(pose_counts.index, pose_counts.values,
       color=["#4C9FE0", "#7FCB8F", "#F5A742", "#E07A7A"])
for i, v in enumerate(pose_counts.values):
    ax.text(i, v + 30, str(v), ha="center", fontweight="bold")
ax.set_xlabel("Baş Yönelimi (pose)")
ax.set_ylabel("Frekans")
ax.set_title("Baş Yönelimi Dağılımı", fontweight="bold")
savefig("02_pose_distribution.png")
print("  -> 02_pose_distribution.png")

# 2.3 Etikete göre pose dağılımı (yığılmış)
fig, ax = plt.subplots(figsize=(9, 5))
pose_label = pd.crosstab(df["pose"], df["label"])
pose_label.columns = ["Attentive", "Inattentive"]
pose_label.plot(kind="bar", stacked=True, ax=ax, color=["#4C9FE0", "#E07A7A"])
ax.set_title("Pose'a Göre Dikkat Sınıfı Dağılımı", fontweight="bold")
ax.set_xlabel("Pose")
ax.set_ylabel("Örnek sayısı")
ax.tick_params(axis="x", rotation=0)
ax.legend(title="Sınıf")
savefig("03_pose_vs_label.png")
print("  -> 03_pose_vs_label.png")

# 2.4 Korelasyon ısı haritası (sayısal)
fig, ax = plt.subplots(figsize=(12, 10))
num_df = df.drop(columns=["pose"])
corr = num_df.corr()
sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", center=0,
            square=True, linewidths=0.4, cbar_kws={"shrink": 0.7}, ax=ax)
ax.set_title("Sayısal Özellikler Arası Korelasyon", fontweight="bold")
savefig("04_correlation_heatmap.png")
print("  -> 04_correlation_heatmap.png")

# 2.5 Yüz koordinatlarının etikete göre saçılım grafiği (makale Fig. 3)
fig, ax = plt.subplots(figsize=(9, 7))
for lbl, color, name in [(0, "#4C9FE0", "Attentive"), (1, "#E07A7A", "Inattentive")]:
    sub = df[df["label"] == lbl]
    ax.scatter(sub["face_x"], sub["face_y"], c=color, alpha=0.4, s=14, label=name)
ax.set_xlabel("Face X-coordinate")
ax.set_ylabel("Face Y-coordinate")
ax.set_title("Yüz Koordinatları ve Dikkat Sınıfı İlişkisi", fontweight="bold")
ax.legend()
savefig("05_face_coords_scatter.png")
print("  -> 05_face_coords_scatter.png")

# 2.6 Güven skoru kutu grafiği (makale Fig. 2)
fig, ax = plt.subplots(figsize=(7, 6))
phone_present = df[df["phone"] == 1]["phone_con"].values
data_box = [df["face_con"].values / 100.0, phone_present]
ax.boxplot(data_box, labels=["Face Detection", "Phone Detection"])
ax.set_ylabel("Confidence Score")
ax.set_title("Yüz ve Telefon Tespiti Güven Skoru Dağılımı", fontweight="bold")
savefig("06_confidence_boxplot.png")
print("  -> 06_confidence_boxplot.png")

# 2.7 Sayısal özelliklerin etikete göre dağılımı
key_features = ["face_con", "no_of_face", "no_of_hand", "phone", "pose_x", "pose_y"]
fig, axes = plt.subplots(2, 3, figsize=(15, 9))
for ax, feat in zip(axes.ravel(), key_features):
    for lbl, color in [(0, "#4C9FE0"), (1, "#E07A7A")]:
        ax.hist(df[df["label"] == lbl][feat], bins=30, alpha=0.6, label=f"label={lbl}", color=color)
    ax.set_title(feat, fontweight="bold")
    ax.legend()
plt.suptitle("Anahtar Özelliklerin Sınıfa Göre Dağılımı", fontsize=14, fontweight="bold")
savefig("07_feature_distributions.png")
print("  -> 07_feature_distributions.png")

# ----------------------------------------------------------------------------
# 3. Önişleme
# ----------------------------------------------------------------------------
print("\n" + "=" * 70)
print("3. ÖNİŞLEME")
print("=" * 70)

# 3.1 pose: one-hot encoding (makaledeki gibi)
df_proc = pd.get_dummies(df, columns=["pose"], prefix="pose", dtype=int)
print(f"One-hot encoding sonrası boyut: {df_proc.shape}")

# 3.2 face_con [0, 100] -> [0, 1] aralığına normalize
df_proc["face_con"] = df_proc["face_con"] / 100.0

# 3.3 Özellikler ve etiket
y = df_proc["label"].values
X = df_proc.drop(columns=["label"])
feature_names = X.columns.tolist()
print(f"Özellik sayısı: {len(feature_names)}")

# 3.4 %80-20 stratified train/test split (makaledeki oranla aynı)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)
print(f"Eğitim boyutu : {X_train.shape}")
print(f"Test boyutu   : {X_test.shape}")

# 3.5 MaxAbsScaler (makaledeki gibi)
scaler = MaxAbsScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

# ----------------------------------------------------------------------------
# 4. Baseline Decision Tree (varsayılan parametreler)
# ----------------------------------------------------------------------------
print("\n" + "=" * 70)
print("4. BASELINE DECISION TREE (varsayılan parametreler)")
print("=" * 70)

baseline = DecisionTreeClassifier(random_state=42)
baseline.fit(X_train_s, y_train)
y_pred_base = baseline.predict(X_test_s)
y_proba_base = baseline.predict_proba(X_test_s)[:, 1]

base_metrics = {
    "accuracy":  accuracy_score(y_test, y_pred_base),
    "precision": precision_score(y_test, y_pred_base),
    "recall":    recall_score(y_test, y_pred_base),
    "f1":        f1_score(y_test, y_pred_base),
    "roc_auc":   roc_auc_score(y_test, y_proba_base),
}
cm_base = confusion_matrix(y_test, y_pred_base)
tn, fp, fn, tp = cm_base.ravel()
base_metrics["specificity"] = tn / (tn + fp)
print("Baseline metrikleri:")
for k, v in base_metrics.items():
    print(f"  {k:<12}: {v:.4f}")

# ----------------------------------------------------------------------------
# 5. Hiperparametre tuning (GridSearchCV)
# ----------------------------------------------------------------------------
print("\n" + "=" * 70)
print("5. HİPERPARAMETRE TUNING (GridSearchCV, 5-fold)")
print("=" * 70)

param_grid = {
    "criterion":         ["gini", "entropy"],
    "max_depth":         [None, 5, 10, 15, 20, 30],
    "min_samples_split": [2, 5, 10, 20],
    "min_samples_leaf":  [1, 2, 5, 10],
    "class_weight":      [None, "balanced"],
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
grid = GridSearchCV(
    estimator=DecisionTreeClassifier(random_state=42),
    param_grid=param_grid,
    scoring="f1",
    cv=cv,
    n_jobs=-1,
    verbose=1,
)
grid.fit(X_train_s, y_train)
print(f"\nEn iyi parametreler  : {grid.best_params_}")
print(f"En iyi CV F1 skoru   : {grid.best_score_:.4f}")
best_dt = grid.best_estimator_

# ----------------------------------------------------------------------------
# 6. Final değerlendirme (test set)
# ----------------------------------------------------------------------------
print("\n" + "=" * 70)
print("6. FİNAL DEĞERLENDİRME (tuned model, test set)")
print("=" * 70)

y_pred = best_dt.predict(X_test_s)
y_proba = best_dt.predict_proba(X_test_s)[:, 1]
cm = confusion_matrix(y_test, y_pred)
tn, fp, fn, tp = cm.ravel()

final_metrics = {
    "accuracy":    accuracy_score(y_test, y_pred),
    "precision":   precision_score(y_test, y_pred),
    "recall":      recall_score(y_test, y_pred),
    "specificity": tn / (tn + fp),
    "f1":          f1_score(y_test, y_pred),
    "roc_auc":     roc_auc_score(y_test, y_proba),
}
print("Test seti metrikleri (tuned):")
for k, v in final_metrics.items():
    print(f"  {k:<12}: {v:.4f}")

print("\nClassification Report:")
print(classification_report(y_test, y_pred,
                            target_names=["Attentive", "Inattentive"], digits=4))
print("Confusion Matrix:")
print(cm)
print(f"  TN={tn}  FP={fp}")
print(f"  FN={fn}  TP={tp}")

# ----------------------------------------------------------------------------
# 7. 5-fold CV stabilite kontrolü
# ----------------------------------------------------------------------------
print("\n" + "=" * 70)
print("7. 5-FOLD CROSS-VALIDATION (tüm veri üzerinde)")
print("=" * 70)
X_all_s = scaler.fit_transform(X)
cv_scores = {}
for metric in ["accuracy", "precision", "recall", "f1", "roc_auc"]:
    scores = cross_val_score(
        DecisionTreeClassifier(**grid.best_params_, random_state=42),
        X_all_s, y, cv=cv, scoring=metric, n_jobs=-1
    )
    cv_scores[metric] = {
        "mean": float(scores.mean()),
        "std":  float(scores.std()),
        "scores": scores.tolist(),
    }
    print(f"  {metric:<10}: {scores.mean():.4f} ± {scores.std():.4f}")

# ----------------------------------------------------------------------------
# 8. Görseller (final model)
# ----------------------------------------------------------------------------
print("\n" + "=" * 70)
print("8. GÖRSELLEŞTİRMELER")
print("=" * 70)

# 8.1 Confusion matrix
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
for ax, cm_, title in [
    (axes[0], cm_base, "Baseline (varsayılan)"),
    (axes[1], cm,      "Tuned (GridSearchCV)")
]:
    sns.heatmap(cm_, annot=True, fmt="d", cmap="Blues",
                xticklabels=["Attentive", "Inattentive"],
                yticklabels=["Attentive", "Inattentive"],
                cbar=False, ax=ax, annot_kws={"size": 14, "weight": "bold"})
    ax.set_xlabel("Tahmin")
    ax.set_ylabel("Gerçek")
    ax.set_title(title, fontweight="bold")
plt.suptitle("Confusion Matrix Karşılaştırması", fontsize=14, fontweight="bold")
savefig("08_confusion_matrices.png")
print("  -> 08_confusion_matrices.png")

# 8.2 ROC eğrisi
fig, ax = plt.subplots(figsize=(7, 6))
fpr_b, tpr_b, _ = roc_curve(y_test, y_proba_base)
fpr_t, tpr_t, _ = roc_curve(y_test, y_proba)
ax.plot(fpr_b, tpr_b, lw=2, label=f"Baseline (AUC = {base_metrics['roc_auc']:.4f})")
ax.plot(fpr_t, tpr_t, lw=2, label=f"Tuned (AUC = {final_metrics['roc_auc']:.4f})")
ax.plot([0, 1], [0, 1], "k--", alpha=0.5, label="Rastgele")
ax.set_xlabel("False Positive Rate")
ax.set_ylabel("True Positive Rate")
ax.set_title("ROC Eğrisi", fontweight="bold")
ax.legend(loc="lower right")
savefig("09_roc_curve.png")
print("  -> 09_roc_curve.png")

# 8.3 Precision-Recall eğrisi
fig, ax = plt.subplots(figsize=(7, 6))
pr_b, rc_b, _ = precision_recall_curve(y_test, y_proba_base)
pr_t, rc_t, _ = precision_recall_curve(y_test, y_proba)
ap_b = average_precision_score(y_test, y_proba_base)
ap_t = average_precision_score(y_test, y_proba)
ax.plot(rc_b, pr_b, lw=2, label=f"Baseline (AP = {ap_b:.4f})")
ax.plot(rc_t, pr_t, lw=2, label=f"Tuned (AP = {ap_t:.4f})")
ax.set_xlabel("Recall")
ax.set_ylabel("Precision")
ax.set_title("Precision-Recall Eğrisi", fontweight="bold")
ax.legend(loc="lower left")
savefig("10_precision_recall.png")
print("  -> 10_precision_recall.png")

# 8.4 Özellik önemleri
importances = pd.Series(best_dt.feature_importances_, index=feature_names) \
                .sort_values(ascending=True)
fig, ax = plt.subplots(figsize=(9, 8))
ax.barh(importances.index, importances.values, color="#4C9FE0")
ax.set_xlabel("Önem skoru")
ax.set_title("Decision Tree — Özellik Önemleri", fontweight="bold")
savefig("11_feature_importances.png")
print("  -> 11_feature_importances.png")

# 8.5 Karar ağacı (max_depth=4 ile sınırlı, görsel için)
fig, ax = plt.subplots(figsize=(20, 10))
viz_tree = DecisionTreeClassifier(
    **{**grid.best_params_, "max_depth": 4}, random_state=42
)
viz_tree.fit(X_train_s, y_train)
plot_tree(
    viz_tree, feature_names=feature_names,
    class_names=["Attentive", "Inattentive"],
    filled=True, rounded=True, fontsize=9, ax=ax
)
ax.set_title("Karar Ağacı Yapısı (max_depth=4 — okunabilirlik için)", fontweight="bold")
savefig("12_decision_tree.png")
print("  -> 12_decision_tree.png")

# 8.6 Learning curve
print("  Learning curve hesaplanıyor...")
train_sizes, train_scores, val_scores = learning_curve(
    DecisionTreeClassifier(**grid.best_params_, random_state=42),
    X_train_s, y_train,
    train_sizes=np.linspace(0.1, 1.0, 8),
    cv=cv, scoring="f1", n_jobs=-1, random_state=42
)
fig, ax = plt.subplots(figsize=(8, 6))
ax.plot(train_sizes, train_scores.mean(axis=1), "o-", label="Eğitim F1")
ax.fill_between(train_sizes,
                train_scores.mean(axis=1) - train_scores.std(axis=1),
                train_scores.mean(axis=1) + train_scores.std(axis=1), alpha=0.2)
ax.plot(train_sizes, val_scores.mean(axis=1), "s-", label="CV F1")
ax.fill_between(train_sizes,
                val_scores.mean(axis=1) - val_scores.std(axis=1),
                val_scores.mean(axis=1) + val_scores.std(axis=1), alpha=0.2)
ax.set_xlabel("Eğitim örneği sayısı")
ax.set_ylabel("F1 skoru")
ax.set_title("Learning Curve", fontweight="bold")
ax.legend(loc="lower right")
savefig("13_learning_curve.png")
print("  -> 13_learning_curve.png")

# 8.7 Karşılaştırma çubuğu (literature comparison)
fig, ax = plt.subplots(figsize=(10, 6))
methods = ["Bizim DT\n(Baseline)", "Bizim DT\n(Tuned)",
           "Hossen & Uddin\nXGBoost (2023)", "Mello-Roman\nXGBoost (2023)"]
acc_vals = [base_metrics["accuracy"]*100, final_metrics["accuracy"]*100, 99.75, 80.52]
colors_bar = ["#7FCB8F", "#4C9FE0", "#F5A742", "#9B7FB8"]
bars = ax.bar(methods, acc_vals, color=colors_bar)
for bar, val in zip(bars, acc_vals):
    ax.text(bar.get_x() + bar.get_width() / 2, val + 0.5, f"{val:.2f}%",
            ha="center", fontweight="bold")
ax.set_ylabel("Accuracy (%)")
ax.set_title("Literatür ile Karşılaştırma", fontweight="bold")
ax.set_ylim(0, 105)
ax.axhline(y=100, color="gray", linestyle=":", alpha=0.5)
savefig("14_literature_comparison.png")
print("  -> 14_literature_comparison.png")

# ----------------------------------------------------------------------------
# 9. Tüm sonuçları kaydet
# ----------------------------------------------------------------------------
print("\n" + "=" * 70)
print("9. SONUÇLARI KAYDETME")
print("=" * 70)

results = {
    "dataset": {
        "name": "Students Attention Detection Dataset (Hossen & Uddin, 2023)",
        "n_samples": int(len(df)),
        "n_features": int(len(feature_names)),
        "class_distribution": {str(k): int(v) for k, v in class_counts.items()},
    },
    "preprocessing": {
        "pose_encoding": "one-hot",
        "scaling": "MaxAbsScaler",
        "face_con_normalized_to_01": True,
        "train_test_split": "80/20 stratified, random_state=42",
    },
    "baseline_metrics": {k: float(v) for k, v in base_metrics.items()},
    "best_hyperparameters": {k: str(v) for k, v in grid.best_params_.items()},
    "best_cv_score_f1": float(grid.best_score_),
    "final_test_metrics": {k: float(v) for k, v in final_metrics.items()},
    "five_fold_cv_scores": cv_scores,
    "confusion_matrix": cm.tolist(),
    "feature_importances": importances.to_dict(),
}
with open(os.path.join(RES_DIR, "results.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"  -> results/results.json")

# Tree yapısını yazdır
with open(os.path.join(RES_DIR, "tree_structure.txt"), "w", encoding="utf-8") as f:
    f.write("Karar Ağacı Yapısı (tuned model)\n")
    f.write("=" * 70 + "\n\n")
    f.write(export_text(best_dt, feature_names=feature_names, max_depth=6))
print(f"  -> results/tree_structure.txt")

# Classification report
with open(os.path.join(RES_DIR, "classification_report.txt"), "w", encoding="utf-8") as f:
    f.write("Classification Report (Tuned Decision Tree)\n")
    f.write("=" * 70 + "\n\n")
    f.write(classification_report(y_test, y_pred,
                                  target_names=["Attentive", "Inattentive"], digits=4))
    f.write(f"\nConfusion Matrix:\n{cm}\n")
    f.write(f"  TN={tn}  FP={fp}\n  FN={fn}  TP={tp}\n")
print(f"  -> results/classification_report.txt")

print("\n" + "=" * 70)
print("TAMAMLANDI! Çıktılar: figures/ ve results/ klasörlerinde")
print("=" * 70)
