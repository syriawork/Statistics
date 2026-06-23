import pandas as pd
import sys
sys.path.insert(0, r'e:\programs and applications\Statistics')

from stats_analysis.analysis import analyze_groups

# البيانات من الصورة التي أرسلها المستخدم
data = {
    'group': ['A', 'A', 'A', 'A', 'B', 'B', 'B', 'B', 'C', 'C', 'C', 'C', 'D', 'D', 'D'],
    'value': [99.5, 100.3, 101.5, 100.3, 103.0, 98.95, 104.0, 103.95, 96.0, 965.0, 97.0, 110.0, 111.0, 109.0, 109.5]
}

df = pd.DataFrame(data)

print("=" * 80)
print("البيانات المدخلة:")
print("=" * 80)
print(df)
print(f"\nعدد الصفوف: {len(df)}")
print(f"الأعمدة: {df.columns.tolist()}")
print(f"المجموعات الفريدة: {df['group'].unique().tolist()}")
print(f"عدد المجموعات: {df['group'].nunique()}")

print("\n" + "=" * 80)
print("اختبار analyze_groups:")
print("=" * 80)

try:
    result = analyze_groups(df, 'value', 'group', alpha=0.05)
    
    print("\n✓ النتحليل اكتمل بنجاح!")
    print(f"\nالمجموعات المحللة:")
    for group, stats in result.get('descriptive', {}).items():
        print(f"  {group}: n={stats.get('n')}, mean={stats.get('mean'):.4f}, std={stats.get('std'):.4f}")
    
    print(f"\nعدد المجموعات في النتائج: {len(result.get('descriptive', {}))}")
    print(f"الاختبار الرئيسي: {result.get('main_test', {}).get('test')}")
    print(f"عدد المقارنات الثنائية: {len(result.get('posthoc', []))}")
    
except Exception as e:
    print(f"\n✗ خطأ: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("ملاحظة مهمة: قيمة 965.0 في المجموعة C غير عادية جداً!")
print("هذا قد يكون خطأ إدخال (هل كانت تقصد 96.5 أم 965.0 فعلاً؟)")
print("=" * 80)
