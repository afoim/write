import os
import datetime
from urllib.parse import quote
from bs4 import BeautifulSoup

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DIST_DIR = os.path.join(ROOT_DIR, 'dist')
SITE_URL = "https://072103.xyz"  # 请替换为你的站点地址

def find_all_html_files():
    html_files = []
    for root, _, files in os.walk(DIST_DIR):
        for file in files:
            if file.endswith('.html'):
                rel_path = os.path.relpath(os.path.join(root, file), DIST_DIR)
                html_files.append(rel_path.replace("\\", "/"))
    return html_files

def generate_sitemap(html_files):
    urls = [
        f'  <url><loc>{SITE_URL}/{quote(f)}</loc></url>'
        for f in html_files
    ]
    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls) +
        '\n</urlset>'
    )
    with open(os.path.join(DIST_DIR, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write(sitemap)

def extract_post_content(post_path):
    """提取文章标题和内容"""
    with open(post_path, 'r', encoding='utf-8') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    # 标题
    title = soup.title.string if soup.title else os.path.splitext(os.path.basename(post_path))[0]
    # 日期
    date_tag = soup.find('p')
    pub_date = date_tag.text.strip() if date_tag else ''
    # 正文内容
    content_div = soup.find(id='text-post')
    content_html = str(content_div) if content_div else ''
    return title, pub_date, content_html

def generate_rss(html_files):
    # 使用timezone-aware的UTC时间
    now = datetime.datetime.now(datetime.UTC).strftime('%a, %d %b %Y %H:%M:%S +0000')
    items = []
    for f in html_files:
        if f.startswith('posts/') and f.endswith('.html'):
            post_path = os.path.join(DIST_DIR, f)
            title, pub_date, content_html = extract_post_content(post_path)
            link = f"{SITE_URL}/{f}"
            # 尝试格式化 pubDate
            try:
                pub_date_fmt = datetime.datetime.strptime(pub_date[:10], "%Y-%m-%d").strftime('%a, %d %b %Y 00:00:00 +0000')
            except Exception:
                pub_date_fmt = now
            items.append(
                f"<item>"
                f"<title>{title}</title>"
                f"<link>{link}</link>"
                f"<guid>{link}</guid>"
                f"<pubDate>{pub_date_fmt}</pubDate>"
                f"<description><![CDATA[{content_html}]]></description>"
                f"</item>"
            )
    rss = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0">\n'
        '<channel>\n'
        f'<title>AcoFork Blog</title>\n<link>{SITE_URL}/</link>\n<description>RSS Feed</description>\n'
        + "\n".join(items) +
        '\n</channel>\n</rss>'
    )
    with open(os.path.join(DIST_DIR, 'rss.xml'), 'w', encoding='utf-8') as f:
        f.write(rss)

def main():
    html_files = find_all_html_files()
    generate_sitemap(html_files)
    generate_rss(html_files)

if __name__ == '__main__':
    main()
