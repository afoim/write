import os
import re

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DIST_DIR = os.path.join(ROOT_DIR, 'dist')
INJECT_DIR = os.path.join(ROOT_DIR, 'src', 'inject')

def read_inject_file(name):
    path = os.path.join(INJECT_DIR, name)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

def inject_content(html, head, body, footer):
    # 注入head：在<head>后
    html = re.sub(r'(<head[^>]*>)', r'\1\n' + head, html, count=1, flags=re.IGNORECASE)
    # 注入body：在<body>后
    html = re.sub(r'(<body[^>]*>)', r'\1\n' + body, html, count=1, flags=re.IGNORECASE)
    # 注入footer：在</body>前
    html = re.sub(r'(</body>)', footer + r'\n\1', html, count=1, flags=re.IGNORECASE)
    return html

def main():
    head = read_inject_file('head.html')
    body = read_inject_file('body.html')
    footer = read_inject_file('footer.html')

    for root, _, files in os.walk(DIST_DIR):
        for file in files:
            if file.endswith('.html'):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    html = f.read()
                html = inject_content(html, head, body, footer)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(html)

if __name__ == '__main__':
    main()
