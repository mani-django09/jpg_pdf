import os
import re
import time

try:
    from googletrans import Translator
    translator = Translator()
except ImportError:
    print("Error: googletrans not installed")
    print("Run: pip install googletrans==3.1.0a0")
    exit(1)

LANGUAGES = {
    'pt': 'Portuguese',
    'es': 'Spanish', 
    'de': 'German',
    'id': 'Indonesian',
    'fr': 'French',
    'tr': 'Turkish',
}

def translate_po_file(lang_code, lang_name):
    po_file_path = f'locale/{lang_code}/LC_MESSAGES/django.po'
    
    if not os.path.exists(po_file_path):
        print(f"File not found: {po_file_path}")
        return
    
    print(f"\nTranslating to {lang_name} ({lang_code})...")
    
    with open(po_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all untranslated msgid/msgstr pairs
    pattern = r'msgid "((?:[^"\\]|\\.)*)"\nmsgstr ""'
    
    def replace_translation(match):
        msgid = match.group(1)
        
        if not msgid or not msgid.strip():
            return match.group(0)
        
        try:
            # Unescape the msgid
            msgid_unescaped = msgid.replace('\\"', '"').replace('\\n', '\n')
            
            print(f"  Translating: {msgid_unescaped[:60]}...")
            translated = translator.translate(msgid_unescaped, dest=lang_code)
            
            # Escape the translation
            translation_escaped = translated.text.replace('"', '\\"').replace('\n', '\\n')
            
            time.sleep(0.5)  # Avoid rate limiting
            
            return f'msgid "{msgid}"\nmsgstr "{translation_escaped}"'
            
        except Exception as e:
            print(f"  Error: {str(e)}")
            return match.group(0)
    
    # Replace all untranslated strings
    content_translated = re.sub(pattern, replace_translation, content)
    
    # Write back
    with open(po_file_path, 'w', encoding='utf-8') as f:
        f.write(content_translated)
    
    print(f"Completed {lang_name}")

def main():
    print("=" * 60)
    print("AUTOMATIC TRANSLATION TOOL")
    print("=" * 60)
    
    for lang_code, lang_name in LANGUAGES.items():
        try:
            translate_po_file(lang_code, lang_name)
        except Exception as e:
            print(f"Failed {lang_name}: {str(e)}")
    
    print("\n" + "=" * 60)
    print("TRANSLATION COMPLETE!")
    print("=" * 60)
    print("\nNext: Run 'django-admin compilemessages'")

if __name__ == '__main__':
    main()
