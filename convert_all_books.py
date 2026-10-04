import json
import re
from pathlib import Path

def txt_to_json_advanced(txt_path, json_path, book_name):
    """
    تحويل ملف TXT إلى JSON - نسخة متقدمة
    """
    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # محاولة أنماط مختلفة للبحث عن الأحاديث/التراجم
        patterns = [
            # النمط 1: "1 - نص"
            r'(\d+)\s*[-\.\)\:]\s*([^\n]+(?:\n[^\d][^\n]*)*)',
            # النمط 2: "[1] نص"
            r'\[(\d+)\]\s*([^\n]+(?:\n[^\d][^\n]*)*)',
            # النمط 3: "رقم 1: نص"
            r'رقم\s*(\d+)[:\-]?\s*([^\n]+(?:\n[^\d][^\n]*)*)',
            # النمط 4: "1- نص" (بدون مسافة)
            r'^(\d+)\s*-\s*([^\n]+)',
        ]
        
        hadiths = []
        found = False
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.MULTILINE | re.DOTALL)
            if matches and len(matches) > 5:  # تأكد من وجود نتائج كافية
                print(f"✅ تم العثور على {len(matches)} عنصر باستخدام النمط")
                for num, content in matches:
                    content = content.strip()
                    # تنظيف النص من الأرقام المكررة
                    content = re.sub(r'^\d+\s*[-\.\)\:]\s*', '', content)
                    if content and len(content) > 5:
                        hadiths.append({
                            "id": int(num),
                            "idInBook": int(num),
                            "arabic": content,
                            "english": {"narrator": ""}
                        })
                found = True
                break
        
        # إذا لم يتم العثور على عناصر، جرب طريقة تقسيم حسب السطور
        if not found:
            print("⚠️ جاري تجربة طريقة التقسيم حسب الأرقام...")
            lines = text.split('\n')
            current_num = None
            current_text = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # البحث عن أي رقم في بداية السطر
                match = re.match(r'^(\d+)\s*', line)
                if match:
                    if current_num is not None and current_text:
                        hadiths.append({
                            "id": current_num,
                            "idInBook": current_num,
                            "arabic": "\n".join(current_text).strip(),
                            "english": {"narrator": ""}
                        })
                    
                    current_num = int(match.group(1))
                    remaining = line[match.end():].strip()
                    current_text = [remaining] if remaining else []
                else:
                    if current_num is not None:
                        current_text.append(line)
            
            if current_num is not None and current_text:
                hadiths.append({
                    "id": current_num,
                    "idInBook": current_num,
                    "arabic": "\n".join(current_text).strip(),
                    "english": {"narrator": ""}
                })
        
        # حفظ JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(hadiths, f, ensure_ascii=False, indent=2)
        
        print(f"✅ تم تحويل {len(hadiths)} عنصر من {txt_path}")
        print(f"   إلى: {json_path}")
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
print("📚 بدء تحويل الكتب إلى JSON")
print("="*60)

for book in books_to_convert:
    print(f"\n📖 معالجة: {book['name']}")
    if book['path'].exists():
        txt_to_json_advanced(
            str(book['path']),
            str(book['output']),
            book['name']
        )
    else:
        print(f"❌ الملف غير موجود: {book['path']}")

print("\n" + "="*60)
print("✅ تم الانتهاء من تحويل جميع الكتب!")
print("="*60)