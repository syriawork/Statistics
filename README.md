# Biostat Decision Tool

وصف سريع: برنامج بايثون لتحليل بيانات إحصائية حيوية (QC) لاتخاذ قرار قبول/رفض بناءً على اختبارات إحصائية معروفة.

الاعتماديات:

```bash
pip install -r requirements.txt
```

تشغيل المثال:

```bash
python biostat_decision.py --data data/example.csv --value Value --group Group --remove-outliers
```

تشغيل مع تصحيح المقارنات المتعددة وتصدير تقارير Excel/PDF:

```bash
python biostat_decision.py --data data/example.csv --value Value --group Group --remove-outliers --p-correction bonferroni --export-excel report.xlsx --export-pdf report.pdf
```

تشغيل واجهة Streamlit التفاعلية:

```bash
streamlit run app.py
```

تفسيرات:
- يزيل القيم الشاذة بالـ IQR لكل مجموعة عند استخدام `--remove-outliers`.
- إذا كان عدد المجموعات 2 فإن البرنامج يختار بين `t-test`/`Welch` أو `Mann-Whitney` حسب افتراضات التوزيع والاختلاف في التباين.
- إذا كان أكثر من مجموعتين يستخدم `ANOVA` أو `Kruskal-Wallis` مع اختبارات زوجية ثانوية بطريقة Mann-Whitney.
- القرار: `Accept` عندما لا يوجد فرق معنوي (p >= alpha)، و`Reject` عند وجود فرق معنوي (p < alpha).
