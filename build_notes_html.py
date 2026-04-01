import os
import re
import markdown
from pathlib import Path

BASE_DIR = Path(__file__).parent
NOTES_DIR = BASE_DIR / "笔记"
OUTPUT_DIR = BASE_DIR / "html展示"

# 分类配置：子文件夹 -> 分类名和图标
CATEGORIES = {
    "Linux学习": {"label": "Linux 学习", "icon": "🐧"},
    "AI学习": {"label": "AI 学习", "icon": "🤖"},
    "工作笔记": {"label": "工作笔记", "icon": "📝"},
    "电机摸索/概念": {"label": "电机摸索 · 概念", "icon": "⚡", "parent": "电机摸索"},
    "电机摸索/md文件": {"label": "电机摸索 · 实践", "icon": "🔧", "parent": "电机摸索"},
}

def slugify(text):
    """生成安全的 HTML 锚点 id"""
    text = re.sub(r'[\\/:*?"<>|\s]+', '-', text)
    return text.strip('-')

def convert_md_to_html(md_path):
    """读取 md 文件并转为 HTML 片段"""
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    html = markdown.markdown(
        content,
        extensions=['tables', 'fenced_code', 'codehilite', 'toc', 'nl2br']
    )
    return html

def build_sidebar(categories_files):
    """构建侧边栏导航 HTML"""
    html = '<nav class="sidebar-nav">\n'
    html += '<div class="nav-header">📋 笔记目录</div>\n'

    # 按大类分组
    grouped = {}
    for rel_path, info in categories_files:
        cat = info["category"]
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append((rel_path, info))

    for cat, files in grouped.items():
        cat_info = CATEGORIES.get(cat, {"label": cat, "icon": "📄"})
        html += f'<div class="nav-category">\n'
        html += f'  <div class="nav-category-title">{cat_info["icon"]} {cat_info["label"]}</div>\n'
        html += f'  <ul>\n'
        for rel_path, info in files:
            anchor = info["anchor"]
            name = info["name"]
            html += f'    <li><a href="#{anchor}" data-target="{anchor}">{name}</a></li>\n'
        html += f'  </ul>\n'
        html += f'</div>\n'

    html += '</nav>\n'
    return html

def build_content(categories_files):
    """构建主内容区 HTML"""
    html = '<main class="content">\n'

    grouped = {}
    for rel_path, info in categories_files:
        cat = info["category"]
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append((rel_path, info))

    for cat, files in grouped.items():
        cat_info = CATEGORIES.get(cat, {"label": cat, "icon": "📄"})
        html += f'<div class="content-category">\n'
        html += f'<h1 class="category-heading">{cat_info["icon"]} {cat_info["label"]}</h1>\n'

        for rel_path, info in files:
            anchor = info["anchor"]
            name = info["name"]
            body = info["body"]
            html += f'<article class="note-article" id="{anchor}">\n'
            html += f'  <h2 class="note-title">{name}</h2>\n'
            html += f'  <a href="#top" class="back-to-top">↑ 返回顶部</a>\n'
            html += f'  <div class="note-body">{body}</div>\n'
            html += f'</article>\n'

        html += f'</div>\n'

    html += '</main>\n'
    return html

def generate_css():
    return """
    :root {
      --bg: #0d1117; --card: #161b22; --border: #30363d;
      --text: #c9d1d9; --heading: #f0f6fc; --accent: #58a6ff;
      --accent-hover: #79c0ff; --muted: #8b949e;
      --sidebar-bg: #010409; --sidebar-w: 280px;
      --code-bg: #1c2128;
    }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html { scroll-behavior: smooth; scroll-padding-top: 20px; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
      background: var(--bg); color: var(--text);
      line-height: 1.7; min-height: 100vh;
    }

    /* 顶部栏 */
    .top-bar {
      position: fixed; top: 0; left: 0; right: 0; z-index: 100;
      background: var(--sidebar-bg); border-bottom: 1px solid var(--border);
      padding: 0 24px; height: 56px;
      display: flex; align-items: center; gap: 16px;
    }
    .top-bar .home-link {
      color: var(--accent); text-decoration: none; font-weight: 600; font-size: 16px;
      white-space: nowrap;
    }
    .top-bar .home-link:hover { color: var(--accent-hover); }
    .top-bar .page-title {
      color: var(--heading); font-size: 18px; font-weight: 600;
      border-left: 1px solid var(--border); padding-left: 16px; margin-left: 8px;
    }
    .menu-toggle {
      display: none; background: none; border: 1px solid var(--border);
      color: var(--text); font-size: 20px; cursor: pointer;
      width: 36px; height: 36px; border-radius: 6px;
      align-items: center; justify-content: center;
    }
    .menu-toggle:hover { border-color: var(--accent); color: var(--accent); }

    /* 侧边栏 */
    .sidebar {
      position: fixed; top: 56px; left: 0; bottom: 0; width: var(--sidebar-w);
      background: var(--sidebar-bg); border-right: 1px solid var(--border);
      overflow-y: auto; padding: 16px 0; z-index: 90;
    }
    .sidebar-nav .nav-header {
      padding: 8px 20px; font-size: 15px; font-weight: 600;
      color: var(--heading); margin-bottom: 8px;
    }
    .nav-category { margin-bottom: 8px; }
    .nav-category-title {
      padding: 6px 20px; font-size: 13px; font-weight: 600;
      color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px;
    }
    .nav-category ul { list-style: none; }
    .nav-category li a {
      display: block; padding: 6px 20px 6px 32px;
      color: var(--text); text-decoration: none; font-size: 13px;
      transition: background 0.15s, color 0.15s; border-left: 2px solid transparent;
    }
    .nav-category li a:hover,
    .nav-category li a.active {
      background: rgba(88,166,255,0.08); color: var(--accent);
      border-left-color: var(--accent);
    }

    /* 主内容 */
    .content {
      margin-left: var(--sidebar-w); margin-top: 56px;
      padding: 40px 48px 80px; max-width: 900px;
    }
    .category-heading {
      font-size: 24px; color: var(--heading); margin-bottom: 24px;
      padding-bottom: 12px; border-bottom: 2px solid var(--border);
    }
    .content-category { margin-bottom: 56px; }

    .note-article {
      background: var(--card); border: 1px solid var(--border);
      border-radius: 10px; padding: 32px; margin-bottom: 32px;
    }
    .note-title {
      font-size: 20px; color: var(--heading); margin-bottom: 8px;
      padding-bottom: 12px; border-bottom: 1px solid var(--border);
    }
    .back-to-top {
      display: inline-block; font-size: 12px; color: var(--muted);
      text-decoration: none; margin-bottom: 16px; padding: 2px 10px;
      border: 1px solid var(--border); border-radius: 12px;
      transition: all 0.2s;
    }
    .back-to-top:hover { color: var(--accent); border-color: var(--accent); }

    /* Markdown 内容样式 */
    .note-body h1 { font-size: 22px; color: var(--heading); margin: 28px 0 12px; }
    .note-body h2 { font-size: 19px; color: var(--heading); margin: 24px 0 10px; }
    .note-body h3 { font-size: 16px; color: var(--heading); margin: 20px 0 8px; }
    .note-body h4 { font-size: 15px; color: var(--heading); margin: 16px 0 6px; }
    .note-body p { margin-bottom: 12px; }
    .note-body ul, .note-body ol { margin: 8px 0 12px 24px; }
    .note-body li { margin-bottom: 4px; }
    .note-body code {
      background: var(--code-bg); padding: 2px 6px; border-radius: 4px;
      font-size: 0.9em; font-family: "Fira Code", Consolas, monospace;
    }
    .note-body pre {
      background: var(--code-bg); padding: 16px; border-radius: 8px;
      overflow-x: auto; margin: 12px 0; border: 1px solid var(--border);
    }
    .note-body pre code { background: none; padding: 0; }
    .note-body blockquote {
      border-left: 3px solid var(--accent); padding: 8px 16px;
      margin: 12px 0; color: var(--muted); background: rgba(88,166,255,0.05);
      border-radius: 0 6px 6px 0;
    }
    .note-body table {
      width: 100%; border-collapse: collapse; margin: 12px 0;
    }
    .note-body th, .note-body td {
      border: 1px solid var(--border); padding: 8px 12px; text-align: left;
    }
    .note-body th { background: var(--code-bg); color: var(--heading); font-weight: 600; }
    .note-body a { color: var(--accent); text-decoration: none; }
    .note-body a:hover { text-decoration: underline; }
    .note-body hr { border: none; border-top: 1px solid var(--border); margin: 20px 0; }
    .note-body img { max-width: 100%; border-radius: 8px; margin: 8px 0; }

    /* 响应式 */
    @media (max-width: 768px) {
      .menu-toggle { display: flex; }
      .sidebar {
        transform: translateX(-100%); transition: transform 0.3s ease;
        width: 260px;
      }
      .sidebar.open { transform: translateX(0); }
      .content { margin-left: 0; padding: 24px 16px 60px; }
      .note-article { padding: 20px; }
    }
    """

def scan_notes():
    """扫描笔记目录，收集所有 md 文件并分类"""
    categories_files = []
    seen_anchors = set()

    for root, dirs, files in os.walk(NOTES_DIR):
        dirs.sort()
        for fname in sorted(files):
            if not fname.endswith('.md'):
                continue
            full_path = Path(root) / fname
            rel_path = full_path.relative_to(NOTES_DIR)
            rel_str = str(rel_path).replace('\\', '/')

            # 匹配分类
            category = None
            for cat_key in CATEGORIES:
                if rel_str.startswith(cat_key):
                    category = cat_key
                    break
            if category is None:
                # 取第一层目录作为分类
                parts = rel_str.split('/')
                category = parts[0] if len(parts) > 1 else "其他"

            name = fname.replace('.md', '')
            anchor = slugify(rel_str)

            # 避免锚点重复
            base_anchor = anchor
            counter = 1
            while anchor in seen_anchors:
                anchor = f"{base_anchor}-{counter}"
                counter += 1
            seen_anchors.add(anchor)

            print(f"  处理: {rel_str}")
            body = convert_md_to_html(full_path)

            categories_files.append((rel_str, {
                "category": category,
                "name": name,
                "anchor": anchor,
                "body": body,
            }))

    return categories_files

def main():
    print("扫描笔记目录...")
    categories_files = scan_notes()
    print(f"共找到 {len(categories_files)} 篇笔记\n")

    # 构建页面
    sidebar_html = build_sidebar(categories_files)
    content_html = build_content(categories_files)

    full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>学习笔记</title>
  <style>{generate_css()}</style>
</head>
<body id="top">
  <!-- 顶部栏 -->
  <div class="top-bar">
    <button class="menu-toggle" onclick="document.querySelector('.sidebar').classList.toggle('open')">☰</button>
    <a href="../index.html" class="home-link">← 返回主页</a>
    <span class="page-title">📚 学习笔记</span>
  </div>

  <!-- 侧边栏 -->
  <div class="sidebar">
    {sidebar_html}
  </div>

  <!-- 主内容 -->
  {content_html}

  <!-- 高亮当前目录 -->
  <script>
    // 侧边栏点击高亮
    document.querySelectorAll('.nav-category a').forEach(function(link) {{
      link.addEventListener('click', function(e) {{
        document.querySelectorAll('.nav-category a.active').forEach(function(a) {{
          a.classList.remove('active');
        }});
        this.classList.add('active');
        // 移动端点击后关闭侧边栏
        if (window.innerWidth <= 768) {{
          document.querySelector('.sidebar').classList.remove('open');
        }}
      }});
    }});

    // 滚动时自动高亮
    var articles = document.querySelectorAll('.note-article');
    var navLinks = document.querySelectorAll('.nav-category a');
    window.addEventListener('scroll', function() {{
      var current = '';
      articles.forEach(function(article) {{
        var rect = article.getBoundingClientRect();
        if (rect.top <= 100) {{
          current = article.getAttribute('id');
        }}
      }});
      navLinks.forEach(function(link) {{
        link.classList.remove('active');
        if (link.getAttribute('data-target') === current) {{
          link.classList.add('active');
        }}
      }});
    }});
  </script>
</body>
</html>"""

    # 创建输出目录
    OUTPUT_DIR.mkdir(exist_ok=True)
    output_path = OUTPUT_DIR / "notes.html"

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_html)

    print(f"[OK] Generated: {output_path}")
    print(f"     Total: {len(categories_files)} notes")

if __name__ == '__main__':
    main()
