# Biostat Decision Tool

برنامج بايثون شامل لتحليل بيانات إحصائية حيوية (Biostatistics) مخصص للتحقق من الجودة (QC) في الشركات الدوائية. يدعم:
- الإحصاء الوصفي المتقدم (mode, skewness, kurtosis, variance)
- اختبارات القيم الشاذة: IQR, Z-score, 3±SD, Grubbs, Dixon
- اختبارات الفرضية: t-test, Welch, paired t-test, ANOVA, Kruskal-Wallis, Wilcoxon
- اختبارات ما بعد التحليل: Tukey HSD, Dunn
- مؤشرات القدرة الفعلية: Cp, CpK, PPK
- تقارير شاملة: Excel, PDF مع جداول وأشكال بيانية

## التثبيت

```bash
pip install -r requirements.txt
```

## الاستخدام

### واجهة سطر الأوامر (CLI)

#### مثال بسيط:
```bash
python biostat_decision.py --data data/example.csv --value Value --group Group
```

#### مثال متقدم مع جميع الخيارات:
```bash
python biostat_decision.py --data data/example.csv --value Value --group Group \
  --outlier-method grubbs --alpha 0.05 --paired \
  --usl 13 --lsl 9 \
  --p-correction bonferroni \
  --export-excel report.xlsx --export-pdf report.pdf --export-graphs-dir graphs/
```

### خيارات سطر الأوامر:

| الخيار | الوصف | القيمة الافتراضية |
|--------|-------|------------------|
| `--data` | مسار ملف CSV | مطلوب |
| `--value` | عمود القيم الرقمية | مطلوب |
| `--group` | عمود المجموعات | مطلوب |
| `--alpha` | مستوى الدلالة الإحصائية | 0.05 |
| `--outlier-method` | طريقة إزالة القيم الشاذة (none, iqr, zscore, three-sigma, grubbs, dixon) | none |
| `--zscore-threshold` | عتبة Z-score | 3.0 |
| `--usl` | الحد الأعلى للمواصفات (Upper Spec Limit) | none |
| `--lsl` | الحد الأدنى للمواصفات (Lower Spec Limit) | none |
| `--paired` | استخدام اختبار paired t-test | false |
| `--p-correction` | تصحيح المقارنات المتعددة (none, bonferroni, holm, fdr_bh) | none |
| `--export-excel` | مسار تصدير تقرير Excel | none |
| `--export-pdf` | مسار تصدير تقرير PDF | none |
| `--export-graphs-dir` | مسار حفظ الأشكال البيانية | none |

### واجهة Streamlit التفاعلية

```bash
streamlit run app.py
```

توفر الواجهة:
- رفع ملفات CSV
- اختيار الأعمدة والمعاملات
- عرض فوري للنتائج
- تحميل التقارير (Excel/PDF)

### تشغيل Streamlit من واجهة الإدخال المحلية

يمكنك الآن فتح `data_entry_gui.py` لإدخال البيانات مباشرة في نموذج Tkinter ثم الضغط على زر `Run in Streamlit` لفتح واجهة Streamlit الجميلة تلقائياً مع البيانات المدخلة.

## الاختبارات المدعومة

### الإحصاء الوصفي
- العدد (N), الوسط الحسابي (Mean), الوسيط (Median), المنوال (Mode)
- الانحراف المعياري (Std), التباين (Variance), معامل الاختلاف (CV%)
- المدى (Range), الربيعات (Q1, Q3, IQR)
- الالتواء (Skewness), التفرطح (Kurtosis)

### اختبارات القيم الشاذة
- **IQR** (Interquartile Range): الطريقة التقليدية
- **Z-score**: باستخدام 3±SD افتراضيًا
- **3±SD**: قاعدة الانحراف المعياري الثلاثي
- **Grubbs**: اختبار غروبز الإحصائي
- **Dixon**: اختبار ديكسون للقيم الشاذة

### اختبارات الفرضية
- **لعينتين:**
  - t-test (Independent samples)
  - Welch's t-test (Unequal variances)
  - Paired t-test (Dependent samples)
  - Mann-Whitney U test
  - Wilcoxon signed-rank test
  
- **لمتعدد العينات:**
  - ANOVA (متساوي التباين والتوزيع)
  - Kruskal-Wallis (غير معاملي)
  - Tukey HSD (post-hoc)
  - Dunn test (post-hoc غير معاملي)

### مؤشرات القدرة
- **Cp**: قدرة العملية (بدون مركزية)
- **CpK**: قدرة العملية المركزية
- **PPK**: قدرة الأداء (Performance)

## أمثلة الاستخدام

### مثال 1: تحليل بسيط مع Tukey HSD
```bash
python biostat_decision.py --data data/example.csv --value Value --group Group
```

### مثال 2: مع كشف Grubbs والقدرة
```bash
python biostat_decision.py --data data/example.csv --value Value --group Group \
  --outlier-method grubbs --usl 13 --lsl 9 \
  --export-excel report.xlsx
```

### مثال 3: Paired t-test
```bash
python biostat_decision.py --data data/paired.csv --value Value --group Group \
  --paired --alpha 0.05 --export-pdf report.pdf
```

### مثال 4: مع تصحيح Bonferroni
```bash
python biostat_decision.py --data data/example.csv --value Value --group Group \
  --p-correction bonferroni --outlier-method three-sigma \
  --export-graphs-dir ./graphs/ --export-excel report.xlsx
```

## النتائج المُخرجة

### تقرير Excel يتضمن:
1. **Descriptive Statistics**: الإحصاء الوصفي لكل مجموعة
2. **Assumption Tests**: اختبارات Shapiro-Wilk و Levene
3. **Main Test**: نتائج الاختبار الرئيسي
4. **Post-Hoc Results**: المقارنات الزوجية (إن وجدت)
5. **Outlier Summary**: ملخص القيم الشاذة المكتشفة
6. **Process Capability**: Cp, CpK, PPK (إذا تم تحديد المواصفات)
7. **Raw Data**: البيانات الأصلية

### تقرير PDF يتضمن:
- جميع الجداول من تقرير Excel
- الأشكال البيانية (Box plots, Histograms, إلخ)
- التفسيرات الإحصائية

## الملاحظات المهمة

- **حجم العينة**: الحد الأدنى الموصى به 3-5 مشاهدات لكل مجموعة
- **الاختبارات الافتراضية**: البرنامج يختار الاختبار المناسب حسب توزيع البيانات تلقائيًا
- **تصحيح المقارنات المتعددة**: ضروري عند إجراء مقارنات متعددة (Bonferroni, Holm, FDR-BH)
- **Paired t-test**: يتطلب عدد مشاهدات متساوٍ في كل مجموعة
- **المواصفات**: USL و LSL يجب أن تكون USL > LSL
