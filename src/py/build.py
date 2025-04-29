import os
import re
import yaml
import markdown
from datetime import datetime
import shutil

POSTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'posts')
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DIST_DIR = os.path.join(ROOT_DIR, 'dist')
DIST_POSTS_DIR = os.path.join(DIST_DIR, 'posts')
TEMPLATE_POST = os.path.join(ROOT_DIR, 'post.html')
TEMPLATE_POSTS = os.path.join(ROOT_DIR, 'posts.html')
INDEX_HTML = os.path.join(ROOT_DIR, 'index.html')
ABOUT_HTML = os.path.join(ROOT_DIR, 'about.html')
PUBLIC_DIR = os.path.join(ROOT_DIR, 'public')

def extract_yaml_and_body(md_text):
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', md_text, re.DOTALL)
    if match:
        yaml_part = match.group(1)
        body = match.group(2)
        meta = yaml.safe_load(yaml_part)
        return meta, body
    else:
        return {}, md_text

def render_template(template, mapping):
    def repl(m):
        key = m.group(1).strip()
        return str(mapping.get(key, ''))
    return re.sub(r'\{\{\{(.*?)\}\}\}', repl, template)

def md_body_to_html(md_body):
    # 支持嵌套无序/有序列表
    html_content = markdown.markdown(
        md_body,
        extensions=['fenced_code', 'extra']
    )
    # 替换 <blockquote><p>内容</p></blockquote> 为 <p> | 内容</p>
    html_content = re.sub(
        r'<blockquote>\s*<p>(.*?)</p>\s*</blockquote>',
        r'<p> | \1</p>',
        html_content,
        flags=re.DOTALL
    )
    return html_content

def format_date(date_str):
    # 只取日期部分（如2025-03-03 15:56:57+08:00 -> 2025-03-03）
    m = re.match(r'^(\d{4}-\d{2}-\d{2})', str(date_str))
    return m.group(1) if m else str(date_str)

def parse_datetime(date_str):
    # 尝试解析完整时间戳，否则只用日期
    try:
        return datetime.strptime(date_str[:19], "%Y-%m-%d %H:%M:%S")
    except Exception:
        try:
            return datetime.strptime(date_str[:10], "%Y-%m-%d")
        except Exception:
            return datetime.min

def render_posts_tables(posts_data, posts_tpl):
    # 渲染每篇文章为独立表格，每个表格后加<br>
    tables = []
    for mapping in posts_data:
        table = f'''
        <table border="1" cellpadding="0" cellspacing="0" style="width:100%;max-width:800px;table-layout:auto;word-break:break-all;margin:0 auto;">
            <tr>
                <td rowspan="2" style="width:30%;"><img style="width:100%;height:auto;display:block;" align="left" src="{mapping["img"]}" alt="{mapping["title"]}"></td>
                <td style="word-break:break-all;"><a href="/posts/{mapping["slug"]}">{mapping["title"]} - {mapping["date"]}</a></td>
            </tr>
            <tr>
                <td>{mapping["summry"]}</td>
            </tr>
        </table>
        <br>
        '''
        tables.append(table)
    # 替换原有表格内容（只保留第一个表格标签，插入所有表格）
    posts_tpl = re.sub(
        r'(<div class="main" id="posts">)(.*?)(</div>)',
        lambda m: m.group(1) + ''.join(tables) + m.group(3),
        posts_tpl,
        flags=re.DOTALL
    )
    return posts_tpl

def main():
    os.makedirs(DIST_POSTS_DIR, exist_ok=True)
    # 拷贝 index.html 到 dist 目录
    shutil.copy2(INDEX_HTML, os.path.join(DIST_DIR, 'index.html'))
    # 拷贝 about.html 到 dist 目录
    shutil.copy2(ABOUT_HTML, os.path.join(DIST_DIR, 'about.html'))

    # 新增：拷贝 public 文件夹下所有内容到 dist
    if os.path.exists(PUBLIC_DIR):
        for root, dirs, files in os.walk(PUBLIC_DIR):
            rel_dir = os.path.relpath(root, PUBLIC_DIR)
            target_dir = os.path.join(DIST_DIR, rel_dir) if rel_dir != '.' else DIST_DIR
            os.makedirs(target_dir, exist_ok=True)
            for file in files:
                src_file = os.path.join(root, file)
                dst_file = os.path.join(target_dir, file)
                shutil.copy2(src_file, dst_file)

    with open(TEMPLATE_POST, 'r', encoding='utf-8') as f:
        post_tpl = f.read()
    with open(TEMPLATE_POSTS, 'r', encoding='utf-8') as f:
        posts_tpl = f.read()

    posts_data = []
    for filename in os.listdir(POSTS_DIR):
        if filename.endswith('.md'):
            md_path = os.path.join(POSTS_DIR, filename)
            with open(md_path, 'r', encoding='utf-8') as f:
                md_text = f.read()
            meta, body = extract_yaml_and_body(md_text)
            html_body = md_body_to_html(body)
            slug = os.path.splitext(filename)[0] + '.html'
            date_val = meta.get('published', '')
            mapping = {
                'title': meta.get('title', ''),
                'date': format_date(date_val),
                'img': meta.get('cover', {}).get('image', '') if isinstance(meta.get('cover'), dict) else '',
                'img-alt': meta.get('title', ''),
                'summry': meta.get('summary', ''),
                'Text': html_body,
                'slug': slug,
                'datetime': parse_datetime(str(date_val)),
            }
            # 渲染单篇文章页面
            html_out = render_template(post_tpl, mapping)
            html_path = os.path.join(DIST_POSTS_DIR, slug)
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_out)
            posts_data.append(mapping)

    # 按时间从新到旧排序
    posts_data.sort(key=lambda x: x['datetime'], reverse=True)

    # 渲染聚合页（多篇，每篇一个表格）
    if posts_data:
        posts_html = render_posts_tables(posts_data, posts_tpl)
        posts_html_path = os.path.join(DIST_DIR, 'posts.html')
        with open(posts_html_path, 'w', encoding='utf-8') as f:
            f.write(posts_html)

    # 新增：构建结束后自动运行 inject_global.py
    inject_script = os.path.join(os.path.dirname(__file__), 'inject_global.py')
    os.system(f'python "{inject_script}"')

    # 新增：构建结束后自动运行 general_other.py
    general_other_script = os.path.join(os.path.dirname(__file__), 'general_other.py')
    os.system(f'python "{general_other_script}"')

if __name__ == '__main__':
    main()
