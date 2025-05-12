HTML-Translate-Script
HTML Translator

🔧 Requirements
Python 3.8+
Yandex Cloud API Key
Libraries: requests, beautifulsoup4, tqdm, concurrent.futures

🚀 Setup
Install dependencies: pip install requests beautifulsoup4 tqdm

Create input_html folder for source files
Create output_html folder for translations
Set YANDEX_API_KEY in script

📂 Usage
Place HTML files in input_html folder
Run script: python translator.py
Translated files appear in output_html folder
Logs saved to translation_log.txt

⚙️ Features
Multi-threaded translation chunks
Excludes scripts/styles/technical attributes
Auto-retry failed API calls (3 attempts)
Progress bar per file
UTF-8 encoding support

⚠️ Important Notes
API key required - get from Yandex Cloud
Excluded tags: script, style, meta, code, forms
Excluded attributes: id, class, src, data-*, style
Configure CHUNK_SIZE/MAX_WORKERS as needed

📄 File Structure
input_html/ → Original HTML files
output_html/ → Translated versions
translation_log.txt → Errors/warnings

🛠️ Troubleshooting
Check API key permissions
Verify network connection
Inspect translation_log.txt for errors
Reduce MAX_WORKERS if rate-limited
