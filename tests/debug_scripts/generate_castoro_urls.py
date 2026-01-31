"""
Genera tutte le URL delle sottocategorie Castoro da castoro_categories.txt
"""
import re

def normalize_slug(text):
    """Converte testo in slug URL"""
    # Rimuovi numeri iniziali (es: "1. ")
    text = re.sub(r'^\d+\.\s*', '', text)
    
    # Minuscolo
    text = text.lower()
    
    # Sostituisci spazi e virgole con -
    text = text.replace(',', '-')
    text = text.replace(' ', '-')
    
    # Rimuovi trattini multipli
    text = re.sub(r'-+', '-', text)
    
    # Rimuovi trattini all'inizio e fine
    text = text.strip('-')
    
    return text

# Leggi file
with open('src/castoro_categories.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

current_category = None
urls = []

for line in lines:
    line = line.strip()
    
    # Skip linee vuote
    if not line:
        continue
    
    # Categoria principale (numerata)
    if re.match(r'^\d+\.', line):
        current_category = normalize_slug(line)
        print(f"\n📁 Categoria: {current_category}")
    
    # Sottocategoria (maiuscolo, non numerata, non indentata con -)
    elif line.isupper() and not line.startswith('-') and current_category:
        subcategory = normalize_slug(line)
        url = f"/category/{current_category}/{subcategory}"
        urls.append(url)
        print(f"  ├─ {subcategory}")

print(f"\n\n📊 TOTALE: {len(urls)} sottocategorie trovate")

# Salva in file Python
with open('src/castoro_all_urls.py', 'w', encoding='utf-8') as f:
    f.write('"""Tutte le URL delle sottocategorie Castoro generate automaticamente"""\n\n')
    f.write('CASTORO_SUBCATEGORY_URLS = [\n')
    for url in urls:
        f.write(f'    "{url}",\n')
    f.write(']\n')

print(f"\n💾 Salvate in: src/castoro_all_urls.py")
