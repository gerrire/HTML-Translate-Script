import os
import time
import requests
import concurrent.futures
from bs4 import BeautifulSoup
from tqdm import tqdm

# 🔧API Settings
YANDEX_API_KEY = ""
YANDEX_URL = "https://translate.api.cloud.yandex.net/translate/v2/translate"

# settingы
CHUNK_SIZE = 50  
MAX_RETRIES = 3
MAX_WORKERS = 8  
DELAY = 0.1  

# Tags and attributes that do NOT need to be translated
EXCLUDED_TAGS = {
    "script", "style", "meta", "noscript", "code", "pre", "kbd", "samp", "var",
    "input", "textarea", "select", "option", "button", "label", "form"
}

EXCLUDED_ATTRIBUTES = {
    "id", "class", "src", "data-*", "style", "on*", "aria-*",
    "role", "tabindex", "type", "name", "value", "placeholder", "alt",
    "rel", "target", "method", "action", "enctype"
}

def should_translate(tag):
    """Проверяет, нужно ли переводить данный тег"""
    if tag.parent.name in EXCLUDED_TAGS:
        return False
    if tag.parent.name == "a":
        if tag.parent.get("href") and tag == tag.parent.get("href"):
            return False
    else:
        if any(attr in EXCLUDED_ATTRIBUTES for attr in tag.parent.attrs):
            return False
        
    if not tag.strip():
        return False
        
    if tag.strip().startswith('<') or tag.strip().endswith('>'):
        return False
        
    if all(c.isdigit() or c in '.,:;!?@#$%^&*()[]{}-_=+\\|/<>' for c in tag.strip()):
        return False
        
    return True

def translate_chunk(texts, source_lang="en", target_lang="ru"):
    """Переводит чанк текстов"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {YANDEX_API_KEY}",
    }

    body = {
        "texts": texts,
        "sourceLanguageCode": source_lang,
        "targetLanguageCode": target_lang,
    }

    for _ in range(MAX_RETRIES):
        try:
            response = requests.post(YANDEX_URL, json=body, headers=headers, timeout=10)
            response.raise_for_status()
            return [trans["text"] for trans in response.json()["translations"]]
        except Exception as e:
            print(f"[!] Ошибка перевода — {e}")
            time.sleep(1)
    return texts

def translate_html_file(input_path, output_path, log_file):
    with open(input_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    all_strings = [tag for tag in soup.find_all(string=True) if should_translate(tag)]
    
    if not all_strings:
        log_file.write(f"[!] Нет текста для перевода в файле: {input_path}\n")
        return

    chunks = [all_strings[i:i + CHUNK_SIZE] for i in range(0, len(all_strings), CHUNK_SIZE)]
    
    results = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_chunk = {
            executor.submit(translate_chunk, [str(tag) for tag in chunk]): chunk 
            for chunk in chunks
        }
        
        for future in tqdm(concurrent.futures.as_completed(future_to_chunk), 
                         total=len(chunks),
                         desc=f"Перевод {os.path.basename(input_path)}"):
            chunk = future_to_chunk[future]
            try:
                translated_texts = future.result()
                for original, translated in zip(chunk, translated_texts):
                    results[original] = translated
            except Exception as e:
                log_file.write(f"[!] Ошибка обработки чанка: {e}\n")

е
    for tag in soup.find_all(string=True):
        if should_translate(tag):
            if tag in results:
                tag.replace_with(results[tag])
            else:
                log_file.write(f"[!] Не найден перевод для: {tag}\n")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(str(soup))

    log_file.write(f"[+] Переведено: {input_path} → {output_path}\n")

def main():
    input_folder = "input_html"
    output_folder = "output_html"
    log_path = "translation_log.txt"

    os.makedirs(output_folder, exist_ok=True)

    with open(log_path, "w", encoding="utf-8") as log_file:
        for filename in os.listdir(input_folder):
            if filename.endswith(".html"):
                input_path = os.path.join(input_folder, filename)
                output_path = os.path.join(output_folder, filename)
                translate_html_file(input_path, output_path, log_file)

if __name__ == "__main__":
    main()
