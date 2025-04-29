import os
import re
import markdown

POSTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'posts')

def strip_yaml_front_matter(md_text):
    # 匹配开头的yaml元数据
    return re.sub(r'^---[\s\S]*?---\s*', '', md_text, count=1)
def md_file_to_html(md_path, html_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    md_content = strip_yaml_front_matter(md_content)
    html_content = markdown.markdown(
        md_content,
        extensions=['fenced_code']
    )
    # 替换 <blockquote><p>内容</p></blockquote> 为 <p> | 内容</p>
    html_content = re.sub(
        r'<blockquote>\s*<p>(.*?)</p>\s*</blockquote>',
        r'<p> | \1</p>',
        html_content,
        flags=re.DOTALL
    )
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

def main():
    for filename in os.listdir(POSTS_DIR):
        if filename.endswith('.md'):
            md_path = os.path.join(POSTS_DIR, filename)
            html_path = os.path.splitext(md_path)[0] + '.html'
            md_file_to_html(md_path, html_path)
            print(f'Converted {filename} -> {os.path.basename(html_path)}')

if __name__ == '__main__':
    main()
