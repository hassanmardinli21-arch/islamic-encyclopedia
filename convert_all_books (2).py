import json
import re
from pathlib import Path

def txt_to_json_advanced(txt_path, json_path, book_name):
    """
    تحويل ملف TXT الخاص بكتب التراجم والرجال إلى JSON - نسخة متقدمة
    """
    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # أنماط مخصصة لكتب التراجم والرجال للبحث عن (رقم الترجمة + اسم الراوي + نص الترجمة)
        patterns = [
            # النمط 1: رقم وشرطة ثم اسم الراوي أو النص (مثال: 1 - أحمد بن حنبل: ...)
            r'(\d+)\s*[-\.\)\:]\s*([^\n]+(?:\n[^\d][^\n]*)*)',
            # النمط 2: أقواس مربعة [1]
            r'\[(\d+)\]\s*([^\n]+(?:\n[^\d][^\n]*)*)',
            # النمط 3: كلمة رقم متبوعة برقم
            r'رقم\s*(\d+)[:\-]?\s*([^\n]+(?:\n[^\d][^\n]*)*)',
        ]
        
        records = []
        found = False
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.MULTILINE | re.DOTALL)
            if matches and len(matches) > 5:
                print(f"✅ تم العثور على {len(matches)} ترجمة باستخدام الأنماط المتقدمة")
                for num, content in matches:
                    content = content.strip()
                    content = re.sub(r'^\d+\s*[-\.\)\:]\s*', '', content)
                    
                    # محاولة استخراج اسم الراوي المفترض (أول بضع كلمات أو ما قبل النقطتين أو الشرطة)
                    name_match = re.match(r'^([\w\s,أإآةؤئءىًٌٍُِْ~]+?)(?:[\-\:\,\.\n]|$)', content)
                    rawi_name = name_match.group(1).strip() if name_match else f"ترجمة رقم {num}"
                    # إذا كان الاسم طويلاً جداً، نأخذ أول 5 كلمات فقط كاسم تقريبي للراوي
                    words = rawi_name.split()
                    if len(words) > 6:
                        rawi_name = " ".join(words[:6])

                    if content and len(content) > 5:
                        records.append({
                            "id": int(num),
                            "idInBook": int(num),
                            "rawiName": rawi_name,
                            "arabic": content,
                            "bookName": book_name
                        })
                found = True
                break
        
        if not found:
            print("⚠️ جاري تجربة طريقة التقسيم السلسلي للسطور...")
            lines = text.split('\n')
            current_num = None
            current_text = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                match = re.match(r'^(\d+)\s*', line)
                if match:
                    if current_num is not None and current_text:
                        full_text = "\n".join(current_text).strip()
                        records.append({
                            "id": current_num,
                            "idInBook": current_num,
                            "rawiName": f"ترجمة رقم {current_num}",
                            "arabic": full_text,
                            "bookName": book_name
                        })
                    
                    current_num = int(match.group(1))
                    remaining = line[match.end():].strip()
                    current_text = [remaining] if remaining else []
                else:
                    if current_num is not None:
                        current_text.append(line)
            
            if current_num is not None and current_text:
                records.append({
                    "id": current_num,
                    "idInBook": current_num,
                    "rawiName": f"ترجمة رقم {current_num}",
                    "arabic": "\n".join(current_text).strip(),
                    "bookName": book_name
                })
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        
        print(f"✅ تم تحويل وحفظ {len(records)} ترجمة بنجاح إلى: {json_path}")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في تحويل {txt_path}: {e}")
        return False


# ===== تشغيل التحويل لجميع الكتب =====

albani_base = Path(r"C:\Users\me\3D Objects\Desktop\albani")

# قائمة الكتب المطلوب تحويلها
books_to_convert = [
    {
        "name": "المجروحين من المحدثين",
        "path": albani_base / "الرواة" / "المجروحين_من_المحدثين.txt",
        "output": albani_base / "الرواة" / "المجروحين_من_المحدثين.json"
    },
    {
        "name": "تهذيب التهذيب",
        "path": albani_base / "الرواة" / "تهذيب_التهذيب.txt",
        "output": albani_base / "الرواة" / "تهذيب_التهذيب.json"
    },
    {
        "name": "تهذيب الكمال في أسماء الرجال",
        "path": albani_base / "الرواة" / "تهذيب_الكمال_في_أسماء_الرجال.txt",
        "output": albani_base / "الرواة" / "تهذيب_الكمال_في_أسماء_الرجال.json"
    }
]

print("="*60)
print("📚 بدء تحويل كتب التراجم والرجال إلى صيغة JSON المهيكلة")
print("="*60)

for book in books_to_convert:
    print(f"\n📖 معالجة كتاب: {book['name']}")
    if book['path'].exists():
        txt_to_json_advanced(
            str(book['path']),
            str(book['output']),
            book['name']
        )
    else:
        print(f"❌ الملف غير موجود في المسار المحدد: {book['path']}")

print("\n" + "="*60)
print("✅ تم الانتهاء من كافة عمليات التحويل بنجاح!")
print("="*60)