"""自动扫描仓库目录结构，生成 GitHub Pages 首页和目录导航页
  - 默认纸张色护眼主题，支持暗色切换
  - 侧边栏导航，支持收缩折叠
  - 面包屑返回导航（返回上一级）
  - MD 文件链接包含完整路径，确保可正常打开
"""

import json
from pathlib import Path
from html import escape

ROOT = Path(__file__).parent
CONFIG_PATH = ROOT / "config.json"
OUTPUT_PATH = ROOT / "index.html"

TAG_HINTS = {
    ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
    ".c": "C", ".cpp": "C++", ".h": "C/C++", ".java": "Java",
    ".go": "Go", ".rs": "Rust", ".html": "HTML", ".css": "CSS",
    ".vue": "Vue", ".jsx": "React", ".tsx": "React",
    ".ino": "Arduino", ".cmake": "CMake", ".md": "Markdown",
    "Makefile": "Makefile", "CMakeLists.txt": "CMake",
    "requirements.txt": "Python", "package.json": "Node.js",
}

DESC_HINTS = {
    "robot": "机器人", "electron": "机器人", "cubic": "桌面助手",
    "cyber": "控制器", "controller": "控制器", "hub": "中心平台",
    "ink": "墨水屏", "card": "卡片", "lab": "实验室",
}

# ══════════════════════════════════════════════════════════
#  全局 CSS — 纸张色为默认主题
# ══════════════════════════════════════════════════════════
SHARED_CSS = """
:root {
  --bg: #f8f4ee; --surface: #fffdf7; --card: #ffffff;
  --border: #e2d9ca; --text: #3d3929; --heading: #2a2518;
  --accent: #b8860b; --accent-hover: #9a7209; --muted: #8a8275;
  --shadow: rgba(0,0,0,0.06);
  --sidebar-bg: #f0ebe0; --sidebar-w: 260px;
  --code-bg: #f0ebe0; --code-inline: #8b4513;
}
[data-theme="dark"] {
  --bg: #1a1a2e; --surface: #16213e; --card: #1f2b47;
  --border: #334155; --text: #c9d1d9; --heading: #f0f6fc;
  --accent: #e8a838; --accent-hover: #f0bc5e; --muted: #8892a4;
  --shadow: rgba(0,0,0,0.3);
  --sidebar-bg: #12122a; --sidebar-w: 260px;
  --code-bg: #1c2128; --code-inline: #ff7b72;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans SC", Helvetica, Arial, sans-serif;
  background: var(--bg); color: var(--text);
  line-height: 1.7; min-height: 100vh; transition: background 0.3s, color 0.3s;
}
a { color: var(--accent); text-decoration: none; transition: color 0.2s; }
a:hover { color: var(--accent-hover); }

/* ── 侧边栏 ── */
.sidebar {
  position: fixed; top: 0; left: 0; bottom: 0;
  width: var(--sidebar-w); background: var(--sidebar-bg);
  border-right: 1px solid var(--border);
  overflow: hidden; z-index: 100;
  transition: transform 0.3s ease;
  display: flex; flex-direction: column;
}
.sidebar-header {
  padding: 14px 16px; border-bottom: 1px solid var(--border);
  display: flex; align-items: center; justify-content: space-between;
  flex-shrink: 0;
}
.sidebar-header h2 { font-size: 14px; color: var(--heading); font-weight: 600; }
.sidebar-close {
  display: none; background: none; border: none;
  color: var(--muted); font-size: 18px; cursor: pointer; padding: 2px 6px;
}
.sidebar-toggle {
  position: fixed; top: 12px; left: 12px; z-index: 200;
  background: var(--surface); border: 1px solid var(--border);
  color: var(--text); width: 36px; height: 36px; border-radius: 8px;
  cursor: pointer; display: none; align-items: center; justify-content: center;
  font-size: 18px; box-shadow: 0 2px 8px var(--shadow); transition: all 0.2s;
}
.sidebar-toggle:hover { border-color: var(--accent); color: var(--accent); }
.sidebar-overlay {
  display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.35); z-index: 99;
}
.sidebar-overlay.active { display: block; }

/* ── 导航树 ── */
.nav-tree { padding: 8px 0; flex: 1; min-height: 0; overflow-y: auto; }
.nav-tree ul { list-style: none; padding: 0; margin: 0; }
.nav-item {
  display: block; padding: 5px 14px 5px 18px;
  color: var(--text); font-size: 13px;
  border-left: 2px solid transparent;
  transition: all 0.15s; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.nav-item:hover { background: rgba(184,134,11,0.08); color: var(--accent); }
.nav-item.active { color: var(--accent); background: rgba(184,134,11,0.12); border-left-color: var(--accent); font-weight: 600; }
.nav-folder {
  display: flex; align-items: center;
  padding: 6px 14px 6px 14px; cursor: pointer;
  font-size: 13px; font-weight: 600; color: var(--heading);
  gap: 4px; user-select: none; transition: background 0.15s;
}
.nav-folder:hover { background: rgba(184,134,11,0.08); }
.nav-folder .arrow {
  font-size: 9px; width: 14px; text-align: center; flex-shrink: 0;
  transition: transform 0.2s;
}
.nav-folder.collapsed .arrow { transform: rotate(-90deg); }
.nav-children { padding-left: 12px; }
.nav-children.collapsed { display: none; }

/* ── 主区域 ── */
.main-wrap { margin-left: var(--sidebar-w); min-height: 100vh; transition: margin-left 0.3s ease; }

/* ── 面包屑 ── */
.breadcrumb {
  display: flex; align-items: center; gap: 6px;
  margin-bottom: 24px; font-size: 13px; color: var(--muted); flex-wrap: wrap;
}
.breadcrumb a { color: var(--muted); }
.breadcrumb a:hover { color: var(--accent); }
.breadcrumb .sep { color: var(--border); font-size: 11px; }
.breadcrumb .current { color: var(--heading); font-weight: 600; }

/* ── 页面通用 ── */
.page-container { max-width: 800px; margin: 0 auto; padding: 36px 28px; }
.page-title {
  font-size: 24px; color: var(--heading); margin-bottom: 24px;
  font-weight: 700; letter-spacing: -0.5px;
}
.section-title {
  font-size: 13px; color: var(--muted); margin: 32px 0 12px;
  text-transform: uppercase; letter-spacing: 1px; font-weight: 500;
}

/* ── 卡片网格 ── */
.projects { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 12px; }
.project-card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 12px; padding: 18px; text-decoration: none;
  color: inherit; display: block; transition: all 0.25s;
}
.project-card:hover {
  border-color: var(--accent); transform: translateY(-2px);
  box-shadow: 0 6px 20px var(--shadow);
}
.project-card h3 { font-size: 15px; color: var(--heading); margin-bottom: 4px; font-weight: 600; }
.project-card p { font-size: 12px; color: var(--muted); }
.card-tags { margin-top: 10px; }
.tag {
  display: inline-block; font-size: 10px; color: var(--accent);
  background: color-mix(in srgb, var(--accent) 12%, transparent);
  border-radius: 10px; padding: 2px 8px; margin-right: 4px; font-weight: 500;
}

/* ── 文件列表 ── */
.file-list { display: flex; flex-direction: column; gap: 3px; }
.file-link {
  color: var(--text); padding: 10px 14px; border-radius: 8px;
  transition: all 0.2s; font-size: 14px;
  display: flex; align-items: center; gap: 12px;
}
.file-link:hover { background: var(--surface); color: var(--accent); box-shadow: 0 2px 8px var(--shadow); }
.file-label {
  font-size: 10px; color: var(--accent);
  background: color-mix(in srgb, var(--accent) 12%, transparent);
  padding: 2px 8px; border-radius: 6px; font-weight: 600; min-width: 36px; text-align: center;
}
.file-name { font-weight: 500; }
.empty { color: var(--muted); font-size: 14px; padding: 20px 0; }

/* ── 主题切换 ── */
.theme-toggle {
  position: fixed; top: 12px; right: 12px; z-index: 200;
  background: var(--surface); border: 1px solid var(--border);
  color: var(--text); width: 36px; height: 36px; border-radius: 50%;
  font-size: 16px; cursor: pointer;
  box-shadow: 0 2px 8px var(--shadow); transition: all 0.2s;
  display: flex; align-items: center; justify-content: center;
}
.theme-toggle:hover { border-color: var(--accent); color: var(--accent); }

/* ── 首页专用 ── */
.home-container { max-width: 800px; margin: 0 auto; padding: 72px 24px 40px; }
.home-header { text-align: center; margin-bottom: 48px; }
.avatar {
  width: 100px; height: 100px; border-radius: 50%;
  border: 3px solid var(--accent); margin-bottom: 16px;
  display: inline-block; object-fit: cover; box-shadow: 0 4px 16px var(--shadow);
}
.avatar-placeholder {
  width: 100px; height: 100px; border-radius: 50%;
  background: linear-gradient(135deg, var(--accent), #a371f7);
  margin: 0 auto 16px; display: flex; align-items: center; justify-content: center;
  font-size: 36px; color: #fff; font-weight: 700; box-shadow: 0 4px 16px var(--shadow);
}
.home-header h1 { font-size: 28px; color: var(--heading); margin-bottom: 6px; letter-spacing: -0.5px; }
.home-header p { color: var(--muted); font-size: 16px; }
.social-links { margin-top: 16px; display: flex; justify-content: center; gap: 12px; }
.social-links a {
  color: var(--muted); padding: 8px; border-radius: 50%;
  border: 1px solid var(--border); transition: all 0.2s;
  display: inline-flex; align-items: center; justify-content: center;
}
.social-links a:hover {
  color: var(--accent); border-color: var(--accent);
  transform: translateY(-2px); box-shadow: 0 4px 12px var(--shadow);
}
.home-section { margin-bottom: 40px; }
.home-section h2 {
  font-size: 16px; color: var(--muted); margin-bottom: 16px;
  text-transform: uppercase; letter-spacing: 1px; font-weight: 500;
}
.home-projects { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px; }
.skills { display: flex; flex-wrap: wrap; gap: 8px; }
.skill-tag {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 20px; padding: 6px 16px; font-size: 13px;
  color: var(--text); transition: all 0.2s; font-weight: 500;
}
.skill-tag:hover { border-color: var(--accent); color: var(--accent); }
.footer {
  text-align: center; margin-top: 48px; padding-top: 20px;
  border-top: 1px solid var(--border); color: var(--muted); font-size: 12px;
}

/* ── MD 内容样式 (md.html 使用) ── */
.md-content h1,.md-content h2,.md-content h3,.md-content h4 {
  color: var(--heading); margin: 1.6em 0 0.6em; font-weight: 600;
}
.md-content h1 { font-size: 26px; padding-bottom: 0.3em; border-bottom: 1px solid var(--border); }
.md-content h2 { font-size: 20px; padding-bottom: 0.25em; border-bottom: 1px solid var(--border); }
.md-content h3 { font-size: 17px; }
.md-content p { margin: 1em 0; }
.md-content code {
  background: var(--code-bg); color: var(--code-inline);
  border-radius: 4px; padding: 2px 6px; font-size: 0.88em;
  font-family: "SFMono-Regular", Consolas, monospace;
}
.md-content pre {
  background: var(--code-bg); border: 1px solid var(--border);
  border-radius: 8px; padding: 16px; overflow-x: auto; margin: 1.2em 0;
}
.md-content pre code { background: none; color: var(--text); padding: 0; font-size: 0.85em; line-height: 1.6; }
.md-content blockquote { border-left: 4px solid var(--accent); margin: 1em 0; padding: 0.6em 16px; color: var(--muted); }
.md-content ul, .md-content ol { padding-left: 2em; margin: 0.8em 0; }
.md-content li { margin: 0.3em 0; }
.md-content table { border-collapse: collapse; margin: 1.2em 0; width: 100%; }
.md-content th, .md-content td { border: 1px solid var(--border); padding: 10px 14px; text-align: left; }
.md-content th { background: var(--surface); color: var(--heading); font-weight: 600; }
.md-content img { max-width: 100%; border-radius: 8px; margin: 1em 0; }
.md-content hr { border: none; border-top: 1px solid var(--border); margin: 2em 0; }
.md-content strong { color: var(--heading); font-weight: 600; }

/* ── 侧边栏搜索 ── */
.nav-search-wrap {
  padding: 8px 12px; flex-shrink: 0;
  border-bottom: 1px solid var(--border);
}
.nav-search {
  width: 100%; padding: 6px 10px; font-size: 12px;
  background: var(--surface); color: var(--text);
  border: 1px solid var(--border); border-radius: 6px;
  outline: none; transition: border-color 0.2s;
}
.nav-search::placeholder { color: var(--muted); }
.nav-search:focus { border-color: var(--accent); }

/* ── 内容搜索栏 ── */
.content-search-bar {
  display: flex; align-items: center; gap: 6px;
  margin-bottom: 16px; padding: 8px 12px;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 8px;
  position: sticky; top: 0; z-index: 10;
}
.content-search-bar input {
  flex: 1; padding: 5px 8px; font-size: 13px;
  background: var(--bg); color: var(--text);
  border: 1px solid var(--border); border-radius: 4px; outline: none;
}
.content-search-bar input:focus { border-color: var(--accent); }
.content-search-bar .search-count {
  font-size: 12px; color: var(--muted); white-space: nowrap; min-width: 60px; text-align: center;
}
.search-bar-btn {
  background: none; border: 1px solid var(--border); color: var(--text);
  width: 28px; height: 28px; border-radius: 4px; cursor: pointer;
  display: flex; align-items: center; justify-content: center; font-size: 14px;
  transition: all 0.15s;
}
.search-bar-btn:hover { border-color: var(--accent); color: var(--accent); }

/* ── 下载按钮（右上角固定） ── */
.dl-bar {
  position: fixed; top: 12px; right: 56px; z-index: 200;
  display: none; align-items: center; gap: 6px;
}
.dl-bar.visible { display: flex; }
.dl-btn {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 6px 12px; font-size: 12px;
  background: var(--surface); color: var(--text);
  border: 1px solid var(--border); border-radius: 8px;
  cursor: pointer; transition: all 0.15s; white-space: nowrap;
  box-shadow: 0 2px 8px var(--shadow);
}
.dl-btn:hover { border-color: var(--accent); color: var(--accent); }
.dl-btn svg { width: 14px; height: 14px; }

/* ── 搜索高亮 ── */
mark.search-hl {
  background: rgba(184,134,11,0.3); color: var(--text);
  padding: 1px 2px; border-radius: 2px;
}

/* ── 阅读进度条 ── */
.reading-progress {
  position: fixed; top: 0; left: 0; height: 3px;
  background: var(--accent); z-index: 999; width: 0%;
  transition: width 0.15s linear;
}

/* ── 侧边栏分区 ── */
.sidebar-section {
  border-top: 1px solid var(--border); padding: 8px 0; flex-shrink: 0;
}
.sidebar-section-title {
  font-size: 11px; color: var(--muted); padding: 4px 14px;
  text-transform: uppercase; letter-spacing: 1px; font-weight: 500;
  cursor: pointer; user-select: none; display: flex; align-items: center; justify-content: space-between;
}
.sidebar-section-title:hover { color: var(--text); }
.sidebar-section-title .section-arrow { font-size: 9px; transition: transform 0.2s; }
.sidebar-section.collapsed .section-arrow { transform: rotate(-90deg); }
.sidebar-section.collapsed .recent-list,
.sidebar-section.collapsed .fav-list,
.sidebar-section.collapsed .toc-list { display: none; }
.toc-list a {
  display: block; padding: 3px 14px 3px 24px; font-size: 12px;
  color: var(--muted); text-decoration: none; border-left: 2px solid transparent;
  transition: all 0.15s; line-height: 1.6;
}
.toc-list a:hover { color: var(--accent); }
.toc-list a.active { color: var(--accent); border-left-color: var(--accent); font-weight: 600; }
.toc-list a.toc-h3 { padding-left: 36px; font-size: 11px; }
.toc-list a.toc-h4 { padding-left: 48px; font-size: 11px; }
.empty-hint { font-size: 12px; color: var(--muted); padding: 4px 14px; font-style: italic; }
.recent-list a, .fav-list a {
  display: block; padding: 4px 14px; font-size: 12px; color: var(--muted);
  text-decoration: none; transition: all 0.15s; white-space: nowrap;
  overflow: hidden; text-overflow: ellipsis;
}
.recent-list a:hover, .fav-list a:hover { color: var(--accent); background: rgba(184,134,11,0.06); }
.fav-btn {
  background: none; border: none; cursor: pointer; font-size: 15px;
  color: var(--muted); padding: 0 4px; transition: color 0.15s;
}
.fav-btn:hover, .fav-btn.active { color: #e8a838; }

/* ── 元信息栏 ── */
.meta-bar {
  font-size: 12px; color: var(--muted); margin-bottom: 16px;
}

/* ── 快捷键面板 ── */
.shortcut-overlay {
  display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.4); z-index: 300;
  justify-content: center; align-items: center;
}
.shortcut-overlay.active { display: flex; }
.shortcut-panel {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 12px; padding: 24px 28px; max-width: 380px; width: 90%;
  box-shadow: 0 8px 32px var(--shadow);
}
.shortcut-panel h3 { font-size: 16px; color: var(--heading); margin-bottom: 16px; }
.shortcut-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 5px 0; font-size: 13px; color: var(--text);
}
.shortcut-key {
  background: var(--bg); border: 1px solid var(--border);
  border-radius: 4px; padding: 2px 8px; font-size: 11px; font-family: monospace;
  color: var(--muted);
}

/* ── 电子桌宠 ── */
.pet-wrap{position:fixed;bottom:24px;left:276px;z-index:150;cursor:pointer;user-select:none;-webkit-user-select:none;touch-action:none;}
.pet-wrap.dragging{cursor:grabbing;}
.pet-wrap::after{content:'';position:absolute;top:0;left:0;width:32px;height:32px;}
.pet-sprite{position:relative;width:4px;height:4px;image-rendering:pixelated;image-rendering:crisp-edges;}
.pet-sprite.float{animation:petFloat 2.5s ease-in-out infinite;}
.pet-bubble{
  position:absolute;bottom:calc(100% + 10px);left:50%;transform:translateX(-50%) scale(0.8);
  background:var(--surface);color:var(--text);border:1px solid var(--border);
  border-radius:10px;padding:5px 12px;font-size:12px;white-space:nowrap;
  box-shadow:0 3px 12px var(--shadow);opacity:0;transition:all 0.25s;pointer-events:none;
  min-width:20px;text-align:center;z-index:2;
}
.pet-bubble.show{opacity:1;transform:translateX(-50%) scale(1);}
.pet-bubble::after{content:'';position:absolute;top:100%;left:50%;transform:translateX(-50%);border:5px solid transparent;border-top-color:var(--surface);}
.pet-bubble::before{content:'';position:absolute;top:calc(100% + 1px);left:50%;transform:translateX(-50%);border:5px solid transparent;border-top-color:var(--border);}
.pet-btns{position:absolute;top:-4px;right:-30px;display:flex;flex-direction:column;gap:5px;opacity:0;transition:opacity 0.2s;pointer-events:none;}
.pet-wrap:hover .pet-btns{opacity:1;pointer-events:auto;}
.pet-btn{
  width:24px;height:24px;border-radius:50%;border:1px solid var(--border);
  background:var(--surface);cursor:pointer;display:flex;align-items:center;
  justify-content:center;font-size:12px;box-shadow:0 2px 6px var(--shadow);
  transition:all 0.15s;color:var(--text);line-height:1;
}
.pet-btn:hover{border-color:var(--accent);color:var(--accent);transform:scale(1.15);}
.pet-menu{
  position:absolute;bottom:calc(100% + 44px);left:50%;transform:translateX(-50%);
  background:var(--surface);border:1px solid var(--border);
  border-radius:10px;padding:6px 0;min-width:110px;
  box-shadow:0 6px 20px var(--shadow);z-index:152;display:none;font-size:12px;
}
.pet-menu.show{display:block;animation:petMenuIn 0.15s ease;}
.pet-menu-label{padding:4px 14px 2px;font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:0.5px;font-weight:500;}
.pet-menu-item{padding:6px 14px;cursor:pointer;color:var(--text);transition:background 0.1s;display:flex;align-items:center;gap:8px;}
.pet-menu-item:hover{background:rgba(184,134,11,0.08);}
.pet-menu-item.active{color:var(--accent);font-weight:600;}
.pmi-dot{width:10px;height:10px;border-radius:2px;flex-shrink:0;border:1px solid var(--border);}
.pet-acc{position:absolute;display:none;pointer-events:none;}
.pet-acc.show{display:block;}
.pet-acc-hat{top:-10px;left:50%;transform:translateX(-50%);width:16px;height:9px;background:#E74C3C;border-radius:4px 4px 1px 1px;box-shadow:0 -1px 0 #C0392B inset;}
.pet-acc-bow{top:4px;right:-8px;width:12px;height:12px;}
.pet-acc-bow::before,.pet-acc-bow::after{content:'';position:absolute;width:7px;height:7px;background:#FF69B4;border-radius:50% 50% 50% 0;top:2px;}
.pet-acc-bow::before{left:0;transform:rotate(-45deg);}
.pet-acc-bow::after{right:0;transform:rotate(45deg) scaleX(-1);}
.pet-mood-bar{position:absolute;top:-3px;left:0;right:0;height:2px;border-radius:1px;background:var(--border);overflow:hidden;opacity:0;transition:opacity 0.3s;}
.pet-wrap:hover .pet-mood-bar{opacity:1;}
.pet-mood-fill{height:100%;border-radius:1px;transition:width 0.5s,background 0.5s;}
@keyframes petFloat{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}
@keyframes petJump{0%{transform:translateY(0)}30%{transform:translateY(-20px) scale(1.1,0.9)}60%{transform:translateY(0) scale(0.9,1.1)}80%{transform:scale(1.05)}100%{transform:translateY(0) scale(1)}}
@keyframes petEat{0%,100%{transform:scale(1)}20%{transform:scale(1.15,0.85)}50%{transform:scale(0.9,1.1)}75%{transform:scale(1.08,0.92)}}
@keyframes petBreathe{0%,100%{transform:scaleY(1) scaleX(1)}50%{transform:scaleY(1.06) scaleX(0.96)}}
@keyframes petMenuIn{from{opacity:0;transform:translateX(-50%) translateY(6px)}to{opacity:1;transform:translateX(-50%) translateY(0)}}
@media (max-width:768px){.pet-wrap{left:60px!important;bottom:16px;}.pet-btns{right:-26px;}}

/* ── 打印优化 ── */
@media print {
  .sidebar, .sidebar-toggle, .sidebar-overlay, .theme-toggle,
  .dl-bar, .content-search-bar, .reading-progress, .meta-bar,
  .shortcut-overlay, .breadcrumb, .global-search-overlay,
  .back-to-top, .pet-wrap { display: none !important; }
  .main-wrap { margin-left: 0 !important; }
  .page-container { max-width: 100% !important; padding: 0 !important; }
  body { background: #fff !important; color: #000 !important; }
  .md-content { max-width: 100%; }
  .md-content pre { border: 1px solid #ddd; page-break-inside: avoid; }
  a { color: #000 !important; text-decoration: underline; }
  mark.search-hl { background: #ff0 !important; }
}

/* ── 全局搜索面板 ── */
.global-search-overlay {
  display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.4); z-index: 300;
  justify-content: center; padding-top: 12vh;
}
.global-search-overlay.active { display: flex; }
.global-search-panel {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 12px; width: 480px; max-width: 90%;
  box-shadow: 0 12px 40px var(--shadow);
  max-height: 70vh; display: flex; flex-direction: column; overflow: hidden;
}
.global-search-input-wrap {
  display: flex; align-items: center; padding: 12px 16px;
  border-bottom: 1px solid var(--border); gap: 8px;
}
.global-search-input {
  flex: 1; padding: 8px 0; font-size: 15px;
  background: none; border: none; outline: none; color: var(--text);
}
.global-search-input::placeholder { color: var(--muted); }
.global-search-close {
  background: none; border: none; font-size: 18px;
  color: var(--muted); cursor: pointer; padding: 4px;
}
.global-search-results {
  flex: 1; overflow-y: auto; padding: 8px 0;
}
.global-search-item {
  display: flex; align-items: center; padding: 10px 16px;
  cursor: pointer; transition: background 0.1s; gap: 12px;
}
.global-search-item:hover { background: rgba(184,134,11,0.08); }
.global-search-item.focused { background: rgba(184,134,11,0.12); }
.global-search-item .gsearch-icon {
  flex-shrink: 0; width: 20px; text-align: center; color: var(--muted); font-size: 13px;
}
.global-search-item .gsearch-text { flex: 1; min-width: 0; }
.global-search-item .gsearch-title {
  font-size: 13px; color: var(--text); font-weight: 500;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.global-search-item .gsearch-path {
  font-size: 11px; color: var(--muted); margin-top: 2px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.global-search-item .gsearch-match {
  font-size: 11px; color: var(--muted); margin-top: 2px;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.global-search-empty {
  padding: 24px; text-align: center; color: var(--muted); font-size: 13px;
}

/* ── 返回顶部 ── */
.back-to-top {
  position: fixed; bottom: 24px; right: 24px; z-index: 200;
  width: 40px; height: 40px; border-radius: 50%;
  background: var(--surface); border: 1px solid var(--border);
  color: var(--text); font-size: 18px; cursor: pointer;
  display: none; align-items: center; justify-content: center;
  box-shadow: 0 2px 8px var(--shadow); transition: all 0.2s;
}
.back-to-top.visible { display: flex; }
.back-to-top:hover { border-color: var(--accent); color: var(--accent); transform: translateY(-2px); }

/* ── 桌面端侧边栏收起 ── */
.sidebar.collapsed { transform: translateX(-100%); }
.main-wrap.sb-collapsed { margin-left: 0; }
@media (min-width: 769px) {
  .sidebar-toggle { display: flex; }
}

/* ── 响应式 ── */
@media (max-width: 768px) {
  .sidebar { transform: translateX(-100%); }
  .sidebar.open { transform: translateX(0); }
  .sidebar-toggle { display: flex; }
  .sidebar-close { display: block; }
  .main-wrap { margin-left: 0; }
  .page-container { padding: 24px 16px; }
  .home-container { padding: 56px 16px 30px; }
  .projects, .home-projects { grid-template-columns: 1fr; }
}
"""

# ══════════════════════════════════════════════════════════
#  全局 JS — 主题切换 + 侧边栏 + 文件夹折叠
# ══════════════════════════════════════════════════════════
SHARED_JS = r"""
function _esc(s){var d=document.createElement('div');d.textContent=s;return d.innerHTML;}
function _addRecent(file,title){
  try{var r=JSON.parse(localStorage.getItem('recentNotes')||'[]');
  r=r.filter(function(x){return x.file!==file;});
  r.unshift({file:file,title:title,t:Date.now()});
  if(r.length>15)r=r.slice(0,15);
  localStorage.setItem('recentNotes',JSON.stringify(r));}catch(e){}
}
function _renderRecent(){
  var el=document.getElementById('recent-list');
  if(!el)return;
  try{var r=JSON.parse(localStorage.getItem('recentNotes')||'[]');
  if(!r.length){el.innerHTML='<span class="empty-hint">暂无记录</span>';return;}
  var h='';r.forEach(function(x){h+='<a href="md.html?file='+encodeURIComponent(x.file)+'">'+_esc(x.title)+'</a>';});
  el.innerHTML=h;}catch(e){el.innerHTML='<span class="empty-hint">暂无记录</span>';}
}
function _toggleFav(file,title){
  try{var f=JSON.parse(localStorage.getItem('favNotes')||'[]');
  var i=f.findIndex(function(x){return x.file===file;});
  if(i>=0)f.splice(i,1);else f.push({file:file,title:title});
  localStorage.setItem('favNotes',JSON.stringify(f));_renderFavs();_updateFavBtn(file);}catch(e){}
}
function _renderFavs(){
  var el=document.getElementById('fav-list');
  if(!el)return;
  try{var f=JSON.parse(localStorage.getItem('favNotes')||'[]');
  if(!f.length){el.innerHTML='<span class="empty-hint">暂无收藏</span>';return;}
  var h='';f.forEach(function(x){h+='<a href="md.html?file='+encodeURIComponent(x.file)+'">'+_esc(x.title)+'</a>';});
  el.innerHTML=h;}catch(e){el.innerHTML='<span class="empty-hint">暂无收藏</span>';}
}
function _updateFavBtn(file){
  var btn=document.getElementById('fav-btn');if(!btn)return;
  try{var f=JSON.parse(localStorage.getItem('favNotes')||'[]');
  var is=f.some(function(x){return x.file===file;});
  btn.textContent=is?'\u2605':'\u2606';btn.classList.toggle('active',is);}catch(e){}
}
(function(){
  var t=localStorage.getItem('theme');
  if(t)document.documentElement.setAttribute('data-theme',t);
})();
document.addEventListener('DOMContentLoaded',function(){
  /* 主题切换 */
  var btn=document.getElementById('theme-toggle');
  if(btn){
    function ui(){btn.textContent=document.documentElement.getAttribute('data-theme')==='dark'?'\u2600':'\u263E';}
    ui();
    btn.addEventListener('click',function(){
      var d=document.documentElement.getAttribute('data-theme')==='dark';
      document.documentElement.setAttribute('data-theme',d?'':'dark');
      localStorage.setItem('theme',d?'':'dark');ui();
    });
  }
  /* 侧边栏开关 */
  var sb=document.getElementById('sidebar'),ov=document.getElementById('sidebar-overlay'),mw=document.querySelector('.main-wrap');
  var isMobile=function(){return window.innerWidth<=768;};
  function openSb(){if(sb){sb.classList.add('open');sb.classList.remove('collapsed');}if(mw)mw.classList.remove('sb-collapsed');if(ov)ov.classList.add('active');if(isMobile())document.body.style.overflow='hidden';}
  function closeSb(){if(sb){sb.classList.remove('open');}if(ov){ov.classList.remove('active');}document.body.style.overflow='';}
  function toggleSb(){
    if(isMobile()){if(sb&&sb.classList.contains('open'))closeSb();else openSb();return;}
    if(sb)sb.classList.toggle('collapsed');
    if(mw)mw.classList.toggle('sb-collapsed');
    try{localStorage.setItem('sidebarCollapsed',sb.classList.contains('collapsed')?'1':'0');}catch(e){}
  }
  /* 恢复桌面端侧边栏状态 */
  if(!isMobile()){try{if(localStorage.getItem('sidebarCollapsed')==='1'){if(sb)sb.classList.add('collapsed');if(mw)mw.classList.add('sb-collapsed');}}catch(e){}}
  var tg=document.getElementById('sidebar-toggle');
  if(tg)tg.addEventListener('click',toggleSb);
  var cl=document.getElementById('sidebar-close');
  if(cl)cl.addEventListener('click',closeSb);
  if(ov)ov.addEventListener('click',closeSb);
  /* 文件夹折叠 */
  document.querySelectorAll('.nav-folder').forEach(function(f){
    f.addEventListener('click',function(){this.classList.toggle('collapsed');var c=this.nextElementSibling;if(c&&c.classList.contains('nav-children'))c.classList.toggle('collapsed');});
  });
  /* 高亮当前页 */
  var cp=window.location.pathname.replace(/\/index\.html$/,'').replace(/\/$/,'')||'/';
  document.querySelectorAll('.nav-item').forEach(function(a){
    try{var u=new URL(a.getAttribute('href'),location.href).pathname.replace(/\/index\.html$/,'').replace(/\/$/,'')||'/';
    if(cp===u||location.pathname===a.getAttribute('href'))a.classList.add('active');}catch(e){}
  });
  /* 恢复折叠状态 */
  try{
    var cf=JSON.parse(localStorage.getItem('collapsedFolders')||'[]');
    cf.forEach(function(n){document.querySelectorAll('.nav-folder').forEach(function(f){if(f.dataset.name===n){f.classList.add('collapsed');var c=f.nextElementSibling;if(c)c.classList.add('collapsed');}});});
    document.querySelectorAll('.nav-folder').forEach(function(f){
      f.addEventListener('click',function(){setTimeout(function(){var a=[];document.querySelectorAll('.nav-folder.collapsed').forEach(function(x){if(x.dataset.name)a.push(x.dataset.name);});localStorage.setItem('collapsedFolders',JSON.stringify(a));},60);});
    });
  }catch(e){}
  /* 侧边栏分区折叠 */
  document.querySelectorAll('.sidebar-section-title').forEach(function(t){
    t.addEventListener('click',function(){
      this.parentElement.classList.toggle('collapsed');
      try{var a=[];document.querySelectorAll('.sidebar-section.collapsed').forEach(function(s){if(s.id)a.push(s.id);});localStorage.setItem('collapsedSections',JSON.stringify(a));}catch(e){}
    });
  });
  try{
    var cs=JSON.parse(localStorage.getItem('collapsedSections')||'[]');
    cs.forEach(function(id){var el=document.getElementById(id);if(el)el.classList.add('collapsed');});
  }catch(e){}
  /* 私有文件夹密码保护 */
  (function(){
    if(!window._PRIVATE_PWD||!window._PRIVATE_DIRS||!window._PRIVATE_DIRS.length)return;
    var pwd=window._PRIVATE_PWD,pdirs=window._PRIVATE_DIRS;
    function isUnlocked(){try{return !!sessionStorage.getItem('_private_unlocked_'+pwd);}catch(e){return false;}}
    function unlock(){try{sessionStorage.setItem('_private_unlocked_'+pwd,'1');}catch(e){}}
    function askPwd(cb){
      var overlay=document.createElement('div');
      overlay.style.cssText='position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.4);z-index:400;display:flex;justify-content:center;align-items:center;';
      var box=document.createElement('div');
      box.style.cssText='background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:24px 28px;max-width:340px;width:90%;box-shadow:0 8px 32px var(--shadow);text-align:center;';
      box.innerHTML='<div style="font-size:32px;margin-bottom:12px">&#128274;</div><div style="font-size:15px;font-weight:600;color:var(--heading);margin-bottom:6px">需要密码</div><div style="font-size:13px;color:var(--muted);margin-bottom:16px">此文件夹已加密，请输入密码</div><div style="display:flex;gap:8px;justify-content:center"><input type="password" style="padding:8px 12px;font-size:14px;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:8px;outline:none;width:160px" autofocus><button style="padding:8px 16px;font-size:14px;background:var(--accent);color:#fff;border:none;border-radius:8px;cursor:pointer;font-weight:600">确认</button></div><div style="font-size:12px;color:#e74c3c;margin-top:8px;min-height:18px"></div>';
      overlay.appendChild(box);document.body.appendChild(overlay);
      var inp=box.querySelector('input'),btn=box.querySelector('button'),err=box.querySelectorAll('div')[4];
      inp.focus();
      function tryPw(){if(inp.value===pwd){unlock();document.body.removeChild(overlay);if(cb)cb();}else{err.textContent='密码错误';inp.value='';inp.focus();}}
      btn.addEventListener('click',tryPw);
      inp.addEventListener('keydown',function(e){if(e.key==='Enter')tryPw();});
      overlay.addEventListener('click',function(e){if(e.target===overlay){document.body.removeChild(overlay);}});
    }
    function initPrivateState(){
      var unlocked=isUnlocked();
      document.querySelectorAll('.nav-children-private').forEach(function(el){el.style.display=unlocked?'':'none';});
      document.querySelectorAll('.nav-folder[data-private="1"]').forEach(function(f){
        f.classList.toggle('collapsed',!unlocked);
      });
    }
    initPrivateState();
    document.querySelectorAll('.nav-folder[data-private="1"]').forEach(function(f){
      f.addEventListener('click',function(e){
        if(!isUnlocked()){
          e.stopPropagation();
          askPwd(function(){initPrivateState();
            setTimeout(function(){f.classList.remove('collapsed');var c=f.nextElementSibling;if(c)c.style.display='';},50);
          });
        }
      });
    });
    document.querySelectorAll('.nav-item[data-private="1"]').forEach(function(a){
      a.addEventListener('click',function(e){
        if(!isUnlocked()){e.preventDefault();e.stopPropagation();askPwd(function(){location.href=a.href;});}
      });
    });
  })();
  /* 导览搜索过滤 */
  var searchInput=document.getElementById('nav-search');
  if(searchInput){
    searchInput.addEventListener('input',function(){
      var q=this.value.trim().toLowerCase();
      var items=document.querySelectorAll('.nav-tree .nav-item');
      for(var i=0;i<items.length;i++){
        items[i].style.display=(!q||items[i].textContent.toLowerCase().indexOf(q)!==-1)?'':'none';
      }
      if(q){
        var maxIter=20;
        while(maxIter-->0){
          var changed=false;
          var ch=document.querySelectorAll('.nav-tree .nav-children');
          for(var i=0;i<ch.length;i++){
            var vis=ch[i].querySelectorAll('.nav-item');
            var hasVis=false;
            for(var j=0;j<vis.length;j++){if(vis[j].style.display!=='none'){hasVis=true;break;}}
            if(!hasVis){
              if(ch[i].style.display!=='none'){ch[i].style.display='none';changed=true;}
              var p=ch[i].previousElementSibling;
              if(p&&p.classList.contains('nav-folder')&&p.style.display!=='none'){p.style.display='none';changed=true;}
            }else{
              if(ch[i].style.display==='none'){ch[i].style.display='';changed=true;}
              var p=ch[i].previousElementSibling;
              if(p&&p.classList.contains('nav-folder')&&p.style.display==='none'){p.style.display='';changed=true;}
            }
          }
          if(!changed)break;
        }
      }else{
        var allFolders=document.querySelectorAll('.nav-tree .nav-children, .nav-tree .nav-folder');
        for(var i=0;i<allFolders.length;i++) allFolders[i].style.display='';
      }
    });
  }
  /* md.html 高亮当前文件 */
  try{
    var fp=new URLSearchParams(location.search).get('file');
    if(fp){
      document.querySelectorAll('.nav-item').forEach(function(a){
        try{var u=new URL(a.href);if(u.searchParams.get('file')===fp)a.classList.add('active');}catch(e){}
      });
    }
  }catch(e){}
  /* 渲染最近浏览 & 收藏 */
  _renderRecent();
  _renderFavs();
  /* 键盘快捷键 */
  document.addEventListener('keydown',function(e){
    var tag=document.activeElement.tagName;
    if((e.ctrlKey||e.metaKey)&&!e.shiftKey&&e.key==='k'){
      e.preventDefault();
      var s=document.getElementById('nav-search');
      if(s){s.focus();s.select();}
    }
    if((e.ctrlKey||e.metaKey)&&e.shiftKey&&e.key==='K'){
      e.preventDefault();
      if(window._openGlobalSearch)window._openGlobalSearch();
    }
    if(e.key==='t'&&!e.ctrlKey&&!e.metaKey&&!e.altKey&&tag!=='INPUT'&&tag!=='TEXTAREA'){
      if(btn)btn.click();
    }
    if(e.key==='?'&&!e.ctrlKey&&!e.metaKey&&!e.altKey&&tag!=='INPUT'&&tag!=='TEXTAREA'){
      e.preventDefault();
      var o=document.getElementById('shortcut-overlay');
      if(o)o.classList.toggle('active');
    }
    if(e.key==='Escape'){
      var o=document.getElementById('shortcut-overlay');
      if(o)o.classList.remove('active');
    }
  });
  var so=document.getElementById('shortcut-overlay');
  if(so)so.addEventListener('click',function(e){if(e.target===this)this.classList.remove('active');});
  /* 返回顶部 */
  var btt=document.getElementById('back-to-top');
  if(btt){
    window.addEventListener('scroll',function(){btt.classList.toggle('visible',window.scrollY>400);},{passive:true});
    btt.addEventListener('click',function(){window.scrollTo({top:0,behavior:'smooth'});});
  }
  /* 全局搜索 */
  var gsOverlay=document.getElementById('global-search-overlay');
  var gsInput=document.getElementById('global-search-input');
  var gsResults=document.getElementById('global-search-results');
  if(gsOverlay&&gsInput&&gsResults){
    var gsIdx=-1,gsItems=[];
    function gsOpen(){gsOverlay.classList.add('active');gsInput.value='';gsResults.innerHTML='';gsIdx=-1;gsItems=[];setTimeout(function(){gsInput.focus();},50);}
    function gsClose(){gsOverlay.classList.remove('active');}
    gsInput.addEventListener('input',function(){
      var q=this.value.trim().toLowerCase();
      if(!q){gsResults.innerHTML='<div class="global-search-empty">输入关键词搜索所有笔记</div>';gsItems=[];gsIdx=-1;return;}
      var navItems=document.querySelectorAll('.nav-tree .nav-item');
      var results=[];
      navItems.forEach(function(a){
        var href=a.getAttribute('href');
        if(!href||!href.indexOf('file='))return;
        var fMatch=a.textContent.toLowerCase().indexOf(q)!==-1;
        results.push({title:a.textContent,href:href,score:fMatch?1:2,file:decodeURIComponent(href.split('file=')[1])});
      });
      results.sort(function(a,b){return a.score-b.score||a.title.localeCompare(b.title);});
      results=results.slice(0,20);
      if(!results.length){gsResults.innerHTML='<div class="global-search-empty">未找到匹配笔记</div>';gsItems=[];gsIdx=-1;return;}
      /* 去重 */
      var seen={};results=results.filter(function(r){if(seen[r.file])return false;seen[r.file]=true;return true;});
      gsItems=[];
      var h='';
      results.forEach(function(r,i){
        h+='<div class="global-search-item" data-idx="'+i+'" data-href="'+r.href+'">'
          +'<span class="gsearch-icon">&#128196;</span>'
          +'<div class="gsearch-text"><div class="gsearch-title">'+_esc(r.title)+'</div>'
          +'<div class="gsearch-path">'+_esc(r.file)+'</div></div></div>';
        gsItems.push(r);
      });
      gsResults.innerHTML=h;gsIdx=-1;
      gsResults.querySelectorAll('.global-search-item').forEach(function(el){
        el.addEventListener('click',function(){window.location.href=this.dataset.href;});
        el.addEventListener('mouseenter',function(){gsFocus(+this.dataset.idx);});
      });
      gsFocus(0);
    });
    gsInput.addEventListener('keydown',function(e){
      if(e.key==='Escape')gsClose();
      if(e.key==='Enter'&&gsIdx>=0&&gsItems[gsIdx])window.location.href=gsItems[gsIdx].href;
      if(e.key==='ArrowDown'){e.preventDefault();gsFocus(gsIdx+1);}
      if(e.key==='ArrowUp'){e.preventDefault();gsFocus(gsIdx-1);}
    });
    gsOverlay.addEventListener('click',function(e){if(e.target===gsOverlay)gsClose();});
    function gsFocus(idx){
      if(!gsItems.length)return;
      idx=((idx%gsItems.length)+gsItems.length)%gsItems.length;
      gsIdx=idx;
      gsResults.querySelectorAll('.global-search-item').forEach(function(el,i){
        el.classList.toggle('focused',i===idx);
        if(i===idx)el.scrollIntoView({block:'nearest'});
      });
    }
    window._openGlobalSearch=gsOpen;
  }
});
"""+ """
// ═══ 电子桌宠 ═══
document.addEventListener('DOMContentLoaded',function(){
  var PX=4,G=8,SZ=PX*G;
  var st={skin:'cat',mood:80,hunger:70,acc:null,x:null};
  try{var s=JSON.parse(localStorage.getItem('petState'));if(s){for(var k in s)if(s[k]!=null)st[k]=s[k];}}catch(e){}
  var P={
    cat:{b:'#FFB347',p:'#FF9999',e:'#2d2d2d',n:'#FF6B6B',w:'#eee'},
    dog:{b:'#C49A6C',p:'#8B6914',e:'#2d2d2d',n:'#FF6B6B',w:'#eee'},
    rabbit:{b:'#F0EDE5',p:'#FFB6C1',e:'#2d2d2d',n:'#FF6B6B',w:'#ddd'}
  };
  var FR={
    cat:{
      idle:[[0,'p',0,0,0,0,'p',0],[0,'b',0,0,0,0,'b',0],[0,'b','b','b','b','b','b',0],[0,'b','e',0,0,'e','b',0],[0,'b','b','b','b','b','b',0],[0,0,'b','n','b',0,0,0],[0,'b','b','b','b','b','b',0],[0,0,'b',0,0,'b',0,0]],
      walk:[[0,'p',0,0,0,0,'p',0],[0,'b',0,0,0,0,'b',0],[0,'b','b','b','b','b','b',0],[0,'b','e',0,0,'e','b',0],[0,'b','b','b','b','b','b',0],[0,0,'b','n','b',0,0,0],[0,'b','b','b','b','b','b',0],['b',0,'b',0,0,'b',0,'b']],
      sleep:[[0,'p',0,0,0,0,'p',0],[0,'b',0,0,0,0,'b',0],[0,'b','b','b','b','b','b',0],[0,'b','w',0,0,'w','b',0],[0,'b','b','b','b','b','b',0],[0,0,'b','n','b',0,0,0],[0,'b','b','b','b','b','b',0],[0,0,'b',0,0,'b',0,0]],
      eat:[[0,'p',0,0,0,0,'p',0],[0,'b',0,0,0,0,'b',0],[0,'b','b','b','b','b','b',0],[0,'b','e',0,0,'e','b',0],[0,'b','n','n','n','b','b',0],[0,'b','b','b','b','b','b',0],[0,'b','b','b','b','b','b',0],[0,0,'b',0,0,'b',0,0]]
    },
    dog:{
      idle:[['p',0,0,0,0,0,0,'p'],['p','b',0,0,0,0,'b','p'],[0,'b','b','b','b','b','b',0],[0,'b','e',0,0,'e','b',0],[0,'b','b','b','b','b','b',0],[0,0,'b','n','b',0,0,0],[0,'b','b','b','b','b','b',0],[0,0,'b',0,0,'b',0,0]],
      walk:[['p',0,0,0,0,0,0,'p'],['p','b',0,0,0,0,'b','p'],[0,'b','b','b','b','b','b',0],[0,'b','e',0,0,'e','b',0],[0,'b','b','b','b','b','b',0],[0,0,'b','n','b',0,0,0],[0,'b','b','b','b','b','b',0],['b',0,'b',0,0,'b',0,'b']],
      sleep:[['p',0,0,0,0,0,0,'p'],['p','b',0,0,0,0,'b','p'],[0,'b','b','b','b','b','b',0],[0,'b','w',0,0,'w','b',0],[0,'b','b','b','b','b','b',0],[0,0,'b','n','b',0,0,0],[0,'b','b','b','b','b','b',0],[0,0,'b',0,0,'b',0,0]],
      eat:[['p',0,0,0,0,0,0,'p'],['p','b',0,0,0,0,'b','p'],[0,'b','b','b','b','b','b',0],[0,'b','e',0,0,'e','b',0],[0,'b','n','n','n','b','b',0],[0,'b','b','b','b','b','b',0],[0,'b','b','b','b','b','b',0],[0,0,'b',0,0,'b',0,0]]
    },
    rabbit:{
      idle:[[0,0,'p',0,0,'p',0,0],[0,0,'b',0,0,'b',0,0],[0,'b','b','b','b','b','b',0],[0,'b','e',0,0,'e','b',0],[0,'b','b','b','b','b','b',0],[0,0,'b','n','b',0,0,0],[0,'b','b','b','b','b','b',0],[0,0,'b',0,0,'b',0,0]],
      walk:[[0,0,'p',0,0,'p',0,0],[0,0,'b',0,0,'b',0,0],[0,'b','b','b','b','b','b',0],[0,'b','e',0,0,'e','b',0],[0,'b','b','b','b','b','b',0],[0,0,'b','n','b',0,0,0],[0,'b','b','b','b','b','b',0],['b',0,'b',0,0,'b',0,'b']],
      sleep:[[0,0,'p',0,0,'p',0,0],[0,0,'b',0,0,'b',0,0],[0,'b','b','b','b','b','b',0],[0,'b','w',0,0,'w','b',0],[0,'b','b','b','b','b','b',0],[0,0,'b','n','b',0,0,0],[0,'b','b','b','b','b','b',0],[0,0,'b',0,0,'b',0,0]],
      eat:[[0,0,'p',0,0,'p',0,0],[0,0,'b',0,0,'b',0,0],[0,'b','b','b','b','b','b',0],[0,'b','e',0,0,'e','b',0],[0,'b','n','n','n','b','b',0],[0,'b','b','b','b','b','b',0],[0,'b','b','b','b','b','b',0],[0,0,'b',0,0,'b',0,0]]
    }
  };
  function mkSh(fr,pal){var s=[];for(var r=0;r<fr.length;r++)for(var c=0;c<fr[r].length;c++)if(fr[r][c]&&pal[fr[r][c]])s.push((c*PX)+'px '+(r*PX)+'px 0 '+pal[fr[r][c]]);return s.join(',');}
  function save(){try{localStorage.setItem('petState',JSON.stringify(st));}catch(e){}}
  var wrap=document.createElement('div');wrap.className='pet-wrap';
  if(st.x!=null)wrap.style.left=st.x+'px';
  var bubble=document.createElement('div');bubble.className='pet-bubble';
  var moodBar=document.createElement('div');moodBar.className='pet-mood-bar';
  var moodFill=document.createElement('div');moodFill.className='pet-mood-fill';moodBar.appendChild(moodFill);
  var accHat=document.createElement('div');accHat.className='pet-acc pet-acc-hat';
  var accBow=document.createElement('div');accBow.className='pet-acc pet-acc-bow';
  var sprite=document.createElement('div');sprite.className='pet-sprite float';
  var btns=document.createElement('div');btns.className='pet-btns';
  var feedBtn=document.createElement('div');feedBtn.className='pet-btn';feedBtn.textContent='🍖';feedBtn.title='喂食';
  var menuBtn=document.createElement('div');menuBtn.className='pet-btn';menuBtn.textContent='✨';menuBtn.title='换装';
  btns.appendChild(feedBtn);btns.appendChild(menuBtn);
  var menu=document.createElement('div');menu.className='pet-menu';
  wrap.appendChild(bubble);wrap.appendChild(moodBar);wrap.appendChild(accHat);wrap.appendChild(accBow);
  wrap.appendChild(sprite);wrap.appendChild(btns);wrap.appendChild(menu);
  document.body.appendChild(wrap);
  var curSt='idle',walkDir=1,frameTick=0;
  function render(){
    var sk=FR[st.skin];if(!sk)return;
    var fr=sk[curSt]||sk.idle;
    sprite.style.boxShadow=mkSh(fr,P[st.skin]);
    sprite.style.transform=walkDir===-1?'scaleX(-1)':'';
    if(curSt==='sleep'){sprite.classList.remove('float');sprite.style.animation='petBreathe 2.5s ease-in-out infinite';}
    else if(curSt==='idle'){sprite.style.animation='';void sprite.offsetWidth;sprite.classList.add('float');}
    else{sprite.classList.remove('float');sprite.style.animation='';}
    accHat.classList.toggle('show',st.acc==='hat');accBow.classList.toggle('show',st.acc==='bow');
    var avg=(st.mood+st.hunger)/2;
    moodFill.style.width=Math.max(0,Math.min(100,avg))+'%';
    moodFill.style.background=avg>60?'#4CAF50':avg>30?'#FF9800':'#f44336';
  }
  render();
  var bTimer=null;
  function showBub(txt,dur){bubble.textContent=txt;bubble.classList.add('show');clearTimeout(bTimer);bTimer=setTimeout(function(){bubble.classList.remove('show');},dur||2500);}
  var clickT=['喵~','你好呀！','摸摸我~','今天真好','嘻嘻','别挠我~','(=·ω·=)','溜了溜~','主人来啦！'];
  var hungT=['肚子饿了...','想吃小鱼干','好饿呀','有吃的吗','咕噜咕噜~'];
  var sadT=['主人不理我...','好无聊啊','陪我玩嘛','哼！','一个人好冷清'];
  var slpT=['好困...','Zzz...','呼噜呼噜~','让我再睡会儿'];
  function rnd(a){return a[Math.floor(Math.random()*a.length)];}
  var clickLock=false;
  wrap.addEventListener('click',function(e){
    if(e.target.closest('.pet-btn')||e.target.closest('.pet-menu'))return;
    if(clickLock||wasDrag)return;
    st.mood=Math.min(100,st.mood+5);save();
    if(curSt==='sleep'){curSt='idle';showBub('啊！醒啦~',1500);render();setTimeout(startAI,1500);return;}
    var txt=st.hunger<30?rnd(hungT):st.mood<30?rnd(sadT):rnd(clickT);
    showBub(txt);clickLock=true;
    sprite.classList.remove('float');sprite.style.animation='petJump 0.35s ease';
    setTimeout(function(){sprite.style.animation='';if(curSt==='idle')sprite.classList.add('float');clickLock=false;},350);
    render();
  });
  feedBtn.addEventListener('click',function(e){
    e.stopPropagation();
    if(st.hunger>=100){showBub('已经吃饱啦~');return;}
    st.hunger=Math.min(100,st.hunger+30);st.mood=Math.min(100,st.mood+3);save();
    showBub('好吃！',1500);
    var prev=curSt;curSt='eat';render();
    sprite.style.animation='petEat 0.4s ease';
    setTimeout(function(){curSt=prev;sprite.style.animation='';render();},400);
  });
  function buildMenu(){
    var h='<div class="pet-menu-label">角色</div>';
    var sn={cat:'小猫',dog:'小狗',rabbit:'小兔'};
    var sc={cat:'#FFB347',dog:'#C49A6C',rabbit:'#F0EDE5'};
    for(var k in sn)h+='<div class="pet-menu-item'+(st.skin===k?' active':'')+'" data-skin="'+k+'"><span class="pmi-dot" style="background:'+sc[k]+'"></span>'+sn[k]+'</div>';
    h+='<div class="pet-menu-label" style="margin-top:6px">装饰</div>';
    var an={hat:'帽子',bow:'蝴蝶结'};var ad={hat:'#E74C3C',bow:'#FF69B4'};
    h+='<div class="pet-menu-item"'+(st.acc===null?' active':'')+'" data-acc="none"><span class="pmi-dot" style="background:var(--muted);opacity:0.3"></span>无</div>';
    for(var a in an)h+='<div class="pet-menu-item'+(st.acc===a?' active':'')+'" data-acc="'+a+'"><span class="pmi-dot" style="background:'+ad[a]+'"></span>'+an[a]+'</div>';
    menu.innerHTML=h;
    menu.querySelectorAll('[data-skin]').forEach(function(el){el.addEventListener('click',function(e){e.stopPropagation();st.skin=this.dataset.skin;save();buildMenu();render();});});
    menu.querySelectorAll('[data-acc]').forEach(function(el){el.addEventListener('click',function(e){e.stopPropagation();st.acc=this.dataset.acc==='none'?null:this.dataset.acc;save();buildMenu();render();});});
  }
  menuBtn.addEventListener('click',function(e){e.stopPropagation();menu.classList.toggle('show');if(menu.classList.contains('show'))buildMenu();});
  document.addEventListener('click',function(e){if(!e.target.closest('.pet-menu')&&!e.target.closest('.pet-btn'))menu.classList.remove('show');});
  var dragging=false,wasDrag=false,dragOX=0,dragOY=0;
  function dragStart(e){
    if(e.target.closest('.pet-btn')||e.target.closest('.pet-menu'))return;
    if(aiWalking)return;dragging=true;wasDrag=false;
    var rect=wrap.getBoundingClientRect();
    var cx=e.touches?e.touches[0].clientX:e.clientX;var cy=e.touches?e.touches[0].clientY:e.clientY;
    dragOX=cx-rect.left;dragOY=cy-rect.top;wrap.classList.add('dragging');
    sprite.classList.remove('float');sprite.style.animation='';e.preventDefault();
  }
  function dragMove(e){
    if(!dragging)return;wasDrag=true;
    var cx=e.touches?e.touches[0].clientX:e.clientX;var cy=e.touches?e.touches[0].clientY:e.clientY;
    var x=cx-dragOX,y=window.innerHeight-cy-dragOY-SZ;
    var minL=window.innerWidth>768?280:10;
    x=Math.max(minL,Math.min(window.innerWidth-SZ-40,x));
    y=Math.max(10,Math.min(window.innerHeight-SZ-40,y));
    wrap.style.left=x+'px';wrap.style.bottom=y+'px';st.x=x;e.preventDefault();
  }
  function dragEnd(){if(!dragging)return;dragging=false;wrap.classList.remove('dragging');save();if(curSt==='idle')sprite.classList.add('float');}
  wrap.addEventListener('mousedown',dragStart);wrap.addEventListener('touchstart',dragStart,{passive:false});
  document.addEventListener('mousemove',dragMove);document.addEventListener('touchmove',dragMove,{passive:false});
  document.addEventListener('mouseup',dragEnd);document.addEventListener('touchend',dragEnd);
  var aiTimer=null,aiWalking=false,aiWalkAF=null;
  function startAI(){
    clearInterval(aiTimer);if(aiWalkAF)cancelAnimationFrame(aiWalkAF);aiWalking=false;
    aiTimer=setInterval(function(){
      st.hunger=Math.max(0,st.hunger-2);st.mood=Math.max(0,st.mood-1);
      if(st.hunger<20&&Math.random()<0.3)showBub(rnd(hungT));
      else if(st.mood<20&&Math.random()<0.2)showBub(rnd(sadT));
      save();render();
    },60000);
    schedAI();
  }
  function schedAI(){
    if(curSt==='sleep'){setTimeout(function(){curSt='idle';render();schedAI();},8000+Math.random()*12000);return;}
    setTimeout(function(){
      if(aiWalking)return schedAI();
      var r=Math.random();
      if(r<0.55){
        aiWalking=true;curSt='walk';walkDir=Math.random()<0.5?1:-1;render();
        var sx=parseInt(wrap.style.left)||276;
        var tx=walkDir===1?sx+60+Math.random()*140:sx-60-Math.random()*140;
        tx=Math.max(280,Math.min(window.innerWidth-SZ-50,tx));
        var dur=2000+Math.random()*2000,t0=Date.now();
        function step(){
          if(!aiWalking){curSt='idle';render();schedAI();return;}
          var t=Math.min(1,(Date.now()-t0)/dur);
          var ease=t<0.5?2*t*t:-1+(4-2*t)*t;
          var x=sx+(tx-sx)*ease;wrap.style.left=x+'px';st.x=x;
          frameTick=(frameTick+1)%2;
          var sk=FR[st.skin];sprite.style.boxShadow=mkSh(frameTick?sk.walk:sk.idle,P[st.skin]);
          if(t>=1){aiWalking=false;curSt='idle';render();save();schedAI();}
          else aiWalkAF=requestAnimationFrame(step);
        }
        aiWalkAF=requestAnimationFrame(step);
      }else if(r<0.75){curSt='idle';render();schedAI();}
      else if(r<0.9){curSt='sleep';showBub(rnd(slpT),3000);render();schedAI();}
      else{showBub(st.hunger<30?rnd(hungT):st.mood<30?rnd(sadT):rnd(clickT));schedAI();}
    },3000+Math.random()*5000);
  }
  startAI();
  window.addEventListener('beforeunload',save);
});
"""

THEME_TOGGLE_BTN = '<button id="theme-toggle" class="theme-toggle">\u263E</button>'
SIDEBAR_TOGGLE_BTN = '<button id="sidebar-toggle" class="sidebar-toggle">\u2630</button>'
SIDEBAR_OVERLAY = '<div id="sidebar-overlay" class="sidebar-overlay"></div>'


# ══════════════════════════════════════════════════════════
#  导航树构建
# ══════════════════════════════════════════════════════════
def _get_exclude(config):
    exclude = set(config.get("exclude_dirs", [".github", ".git"]))
    exclude.update({".obsidian", "附件"})
    return exclude


def build_nav_tree(config):
    """扫描笔记和私人目录，构建完整的侧边栏导航树"""
    exclude = _get_exclude(config)
    nav_dirs = ["笔记", "私人"]
    private_dirs = set(config.get("private_dirs", []))

    def _scan(dir_path, is_private=False):
        items = []
        for entry in sorted(dir_path.iterdir()):
            if entry.name.startswith(".") or entry.name in exclude:
                continue
            if entry.is_dir():
                children = _scan(entry, is_private)
                rel = str(entry.relative_to(ROOT)).replace("\\", "/")
                items.append({"name": entry.name, "rel": rel, "children": children, "type": "dir", "private": is_private})
            elif entry.is_file() and entry.suffix.lower() == ".md":
                rel = str(entry.relative_to(ROOT)).replace("\\", "/")
                items.append({"name": entry.stem, "rel": rel, "type": "md", "private": is_private})
        return items

    tree = []
    for dir_name in nav_dirs:
        dir_path = ROOT / dir_name
        if dir_path.is_dir():
            is_private = dir_name in private_dirs
            children = _scan(dir_path, is_private)
            tree.append({"name": dir_name, "rel": dir_name, "children": children, "type": "dir", "private": is_private})
    return tree


def render_nav_html(tree, root_prefix, depth=0):
    """将导航树渲染为 HTML（所有链接以 root_prefix 为前缀）"""
    html = '<ul>\n'
    for item in tree:
        if item["type"] == "dir":
            priv_attr = ' data-private="1"' if item.get("private") else ''
            priv_cls = ' nav-children-private' if item.get("private") else ''
            html += f'<li>\n'
            html += f'  <div class="nav-folder" data-name="{escape(item["name"])}"{priv_attr}>\n'
            html += f'    <span class="arrow">\u25BE</span>\n'
            html += f'    <span>{escape(item["name"])}</span>\n'
            html += f'  </div>\n'
            if item["children"]:
                html += f'  <div class="nav-children{priv_cls}">\n'
                html += render_nav_html(item["children"], root_prefix, depth + 1)
                html += f'  </div>\n'
            html += f'</li>\n'
        elif item["type"] == "md":
            href = f'{root_prefix}md.html?file={escape(item["rel"])}'
            priv_attr = ' data-private="1"' if item.get("private") else ''
            html += f'<li><a class="nav-item" href="{href}"{priv_attr}>{escape(item["name"])}</a></li>\n'
    html += '</ul>\n'
    return html


def build_sidebar_html(nav_tree, root_prefix, config=None):
    """构建完整的侧边栏 HTML"""
    nav_inner = render_nav_html(nav_tree, root_prefix)
    home_href = f"{root_prefix}index.html"
    password = config.get("private_password", "") if config else ""
    private_dirs = config.get("private_dirs", []) if config else []
    private_dirs_js = json.dumps(private_dirs, ensure_ascii=False)
    return f"""
  <div class="sidebar" id="sidebar">
    <div class="sidebar-header">
      <h2>页面导览</h2>
      <button class="sidebar-close" id="sidebar-close">\u2715</button>
    </div>
    <div class="nav-search-wrap">
      <input class="nav-search" id="nav-search" type="text" placeholder="搜索文件名...">
    </div>
    <div class="nav-tree">
      <ul>
        <li><a class="nav-item" href="{home_href}">主页</a></li>
      </ul>
      {nav_inner}
    </div>
    <div class="sidebar-section collapsed" id="recent-section">
      <div class="sidebar-section-title">最近浏览 <span class="section-arrow">\u25BE</span></div>
      <div class="recent-list" id="recent-list"></div>
    </div>
    <div class="sidebar-section collapsed" id="fav-section">
      <div class="sidebar-section-title">收藏笔记 <span class="section-arrow">\u25BE</span></div>
      <div class="fav-list" id="fav-list"></div>
    </div>
  </div>
  <script>window._PRIVATE_PWD="{escape(password)}";window._PRIVATE_DIRS={private_dirs_js};</script>
"""


def build_breadcrumb(directory, root_prefix):
    """构建面包屑导航 HTML，返回上一级"""
    parts = list(directory.relative_to(ROOT).parts)
    crumb_html = f'<a href="{root_prefix}index.html">主页</a>'
    path_so_far = root_prefix
    for i, part in enumerate(parts):
        path_so_far += escape(part) + "/"
        if i < len(parts) - 1:
            crumb_html += f' <span class="sep">/</span> <a href="{path_so_far}">{escape(part)}</a>'
        else:
            crumb_html += f' <span class="sep">/</span> <span class="current">{escape(part)}</span>'
    return crumb_html


# ══════════════════════════════════════════════════════════
#  辅助函数
# ══════════════════════════════════════════════════════════
def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def scan_projects(config):
    exclude = set(config.get("exclude_dirs", [".github", ".git"]))
    exclude.update({".obsidian", "附件"})
    projects = []
    for entry in sorted(ROOT.iterdir()):
        if not entry.is_dir() or entry.name.startswith(".") or entry.name in exclude:
            continue
        tags = detect_tags(entry)
        desc = detect_description(entry.name)
        projects.append({"name": entry.name, "path": entry.name, "description": desc, "tags": tags})
    return projects


def detect_tags(directory):
    tags = set()
    for f in _iter_files(directory, max_depth=2):
        ext = f.suffix.lower()
        if ext in TAG_HINTS:
            tags.add(TAG_HINTS[ext])
        if f.name in TAG_HINTS:
            tags.add(TAG_HINTS[f.name])
    return sorted(tags)[:4]


def detect_description(dir_name):
    name_lower = dir_name.lower()
    for keyword, hint in DESC_HINTS.items():
        if keyword in name_lower:
            return hint + "相关项目"
    return "项目合集"


def _iter_files(directory, max_depth=2):
    if max_depth <= 0:
        return
    for entry in directory.iterdir():
        if entry.is_file():
            yield entry
        elif entry.is_dir() and not entry.name.startswith("."):
            yield from _iter_files(entry, max_depth - 1)


# ══════════════════════════════════════════════════════════
#  生成首页 index.html
# ══════════════════════════════════════════════════════════
def generate_html(config, projects, nav_tree):
    skills_html = "\n        ".join(
        f'<span class="skill-tag">{escape(s)}</span>' for s in config.get("skills", [])
    )
    cards_html = ""
    for p in projects:
        tags_html = " ".join(f'<span class="tag">{escape(t)}</span>' for t in p["tags"])
        cards_html += f"""
        <a class="project-card" href="{escape(p['path'])}/">
          <h3>{escape(p['name'])}</h3>
          <p>{escape(p['description'])}</p>
          <div class="card-tags">{tags_html}</div>
        </a>"""

    social_html = ""
    social = config.get("social", {})
    if social.get("github"):
        social_html += f'\n        <a href="{escape(social["github"])}"><svg width="20" height="20" viewBox="0 0 16 16" fill="currentColor"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg></a>'
    if social.get("email"):
        social_html += f'\n        <a href="mailto:{escape(social["email"])}"><svg width="20" height="20" viewBox="0 0 16 16" fill="currentColor"><path d="M1.75 2A1.75 1.75 0 000 3.75v8.5C0 13.216.784 14 1.75 14h12.5A1.75 1.75 0 0016 12.25v-8.5A1.75 1.75 0 0014.25 2H1.75zM1.5 3.75a.25.25 0 01.25-.25h12.5a.25.25 0 01.25.25v.042l-6.5 4.397L1.5 3.792v-.042zm0 .833L8 9.002l6.5-4.419v8.667a.25.25 0 01-.25.25H1.75a.25.25 0 01-.25-.25V4.583z"/></svg></a>'

    avatar_html = '<div class="avatar-placeholder">?</div>'
    if config.get("avatar_url"):
        avatar_html = f'<img class="avatar" src="{escape(config["avatar_url"])}" alt="avatar" onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'flex\'"><div class="avatar-placeholder" style="display:none">?</div>'

    sidebar_html = build_sidebar_html(nav_tree, "", config)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escape(config['name'])}</title>
  <style>{SHARED_CSS}</style>
</head>
<body>
  {THEME_TOGGLE_BTN}
  {SIDEBAR_TOGGLE_BTN}
  {SIDEBAR_OVERLAY}
  {sidebar_html}
  <div class="global-search-overlay" id="global-search-overlay">
    <div class="global-search-panel">
      <div class="global-search-input-wrap">
        <input class="global-search-input" id="global-search-input" placeholder="搜索所有笔记..." autocomplete="off">
        <button class="global-search-close" id="global-search-close">&times;</button>
      </div>
      <div class="global-search-results" id="global-search-results"><div class="global-search-empty">输入关键词搜索所有笔记</div></div>
    </div>
  </div>
  <button class="back-to-top" id="back-to-top" title="返回顶部">&#8593;</button>
  <div class="main-wrap">
    <div class="home-container">
      <header class="home-header">
        {avatar_html}
        <h1>{escape(config['name'])}</h1>
        <p>{escape(config['bio'])}</p>
        <div class="social-links">{social_html}
        </div>
      </header>
      <section class="home-section">
        <h2>Projects</h2>
        <div class="home-projects">{cards_html}
        </div>
      </section>
      <section class="home-section">
        <h2>Skills</h2>
        <div class="skills">{skills_html}
        </div>
      </section>
      <footer class="footer">
        <p>Powered by GitHub Pages</p>
      </footer>
    </div>
  </div>
  <script>{SHARED_JS}</script>
</body>
</html>"""
    return html


# ══════════════════════════════════════════════════════════
#  生成子目录 index.html
# ══════════════════════════════════════════════════════════
def _is_private_dir(dir_name, config):
    """检查目录是否需要密码保护"""
    return dir_name in config.get("private_dirs", [])


def generate_private_dir_index(directory, config, nav_tree):
    """为私人目录生成带密码保护的 index.html"""
    depth = len(directory.relative_to(ROOT).parts)
    root_prefix = "../" * depth
    dir_name = directory.name
    password = config.get("private_password", "")
    sidebar_html = build_sidebar_html(nav_tree, root_prefix, config)
    breadcrumb_html = build_breadcrumb(directory, root_prefix)

    password_gate_css = """
    .pw-gate {
      display: flex; flex-direction: column; align-items: center;
      justify-content: center; min-height: 50vh; text-align: center;
    }
    .pw-gate h2 { font-size: 20px; color: var(--heading); margin-bottom: 8px; }
    .pw-gate p { color: var(--muted); font-size: 14px; margin-bottom: 24px; }
    .pw-form { display: flex; gap: 8px; align-items: center; }
    .pw-input {
      padding: 10px 16px; font-size: 14px;
      background: var(--surface); color: var(--text);
      border: 1px solid var(--border); border-radius: 8px;
      outline: none; width: 200px; transition: border-color 0.2s;
    }
    .pw-input:focus { border-color: var(--accent); }
    .pw-btn {
      padding: 10px 20px; font-size: 14px;
      background: var(--accent); color: #fff; border: none;
      border-radius: 8px; cursor: pointer; font-weight: 600;
      transition: opacity 0.2s;
    }
    .pw-btn:hover { opacity: 0.85; }
    .pw-error { color: #e74c3c; font-size: 13px; margin-top: 12px; min-height: 20px; }
    .pw-lock-icon { font-size: 48px; margin-bottom: 16px; }
    """

    # 扫描目录内容
    exclude = _get_exclude(config)
    subdirs = []
    files = []
    for entry in sorted(directory.iterdir()):
        if entry.name.startswith(".") or entry.name in exclude:
            continue
        if entry.is_dir():
            subdirs.append(entry)
        elif entry.is_file():
            if entry.suffix.lower() in (".md", ".html", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".pdf"):
                files.append(entry)

    subdir_html = ""
    for d in subdirs:
        file_count = sum(1 for _ in d.iterdir() if not _.name.startswith(".") and _.name not in exclude)
        tags = detect_tags(d)
        tag_str = " ".join(f'<span class="tag">{escape(t)}</span>' for t in tags)
        subdir_html += f"""
        <a class="project-card" href="{escape(d.name)}/">
          <h3>{escape(d.name)}</h3>
          <p>{file_count} 个文件</p>
          <div class="card-tags">{tag_str}</div>
        </a>"""

    file_html = ""
    for f in files:
        ext = f.suffix.lower()
        if ext == ".md":
            md_rel = str(f.relative_to(ROOT)).replace("\\", "/")
            href = f"{root_prefix}md.html?file={escape(md_rel)}"
            label = "MD"
        elif ext == ".html":
            href = f.name
            label = "HTML"
        else:
            href = f.name
            label = ext[1:].upper()
        file_html += f"""
        <a class="file-link" href="{href}">
          <span class="file-label">{label}</span>
          <span class="file-name">{escape(f.stem)}</span>
        </a>"""

    content_html = f"""
        <h1 class="page-title">{escape(dir_name)}</h1>
        {"<h2 class='section-title'>目录</h2><div class='projects'>" + subdir_html + "</div>" if subdir_html else ""}
        {"<h2 class='section-title'>文件</h2><div class='file-list'>" + file_html + "</div>" if file_html else "<p class='empty'>此目录为空</p>"}
    """

    password_gate_js = f"""
    (function(){{
      var CORRECT_PWD = "{escape(password)}";
      var sessionKey = "pw_ok_{escape(dir_name)}";
      if(sessionStorage.getItem(sessionKey)){{
        document.getElementById('pw-gate').style.display='none';
        document.getElementById('pw-content').style.display='block';
        return;
      }}
      var input = document.getElementById('pw-input');
      var btn = document.getElementById('pw-btn');
      var errEl = document.getElementById('pw-error');
      function tryUnlock(){{
        if(input.value === CORRECT_PWD){{
          sessionStorage.setItem(sessionKey, '1');
          document.getElementById('pw-gate').style.display='none';
          document.getElementById('pw-content').style.display='block';
        }} else {{
          errEl.textContent = '密码错误';
          input.value = '';
          input.focus();
        }}
      }}
      btn.addEventListener('click', tryUnlock);
      input.addEventListener('keydown', function(e){{ if(e.key === 'Enter') tryUnlock(); }});
      input.focus();
    }})();
    """

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escape(dir_name)}</title>
  <style>{SHARED_CSS}{password_gate_css}</style>
</head>
<body>
  {THEME_TOGGLE_BTN}
  {SIDEBAR_TOGGLE_BTN}
  {SIDEBAR_OVERLAY}
  {sidebar_html}
  <div class="main-wrap">
    <div class="page-container">
      <div class="breadcrumb">{breadcrumb_html}</div>
      <div id="pw-gate" class="pw-gate">
        <div class="pw-lock-icon">&#128274;</div>
        <h2>此文件夹需要密码</h2>
        <p>请输入密码以查看内容</p>
        <div class="pw-form">
          <input class="pw-input" id="pw-input" type="password" placeholder="输入密码...">
          <button class="pw-btn" id="pw-btn">确认</button>
        </div>
        <div class="pw-error" id="pw-error"></div>
      </div>
      <div id="pw-content" style="display:none">
        {content_html}
      </div>
    </div>
  </div>
  <script>{SHARED_JS}
{password_gate_js}</script>
</body>
</html>"""

    index_path = directory / "index.html"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Generated password-protected index for {directory.name}")


def generate_dir_index(directory, config, nav_tree):
    # 私人目录走单独的密码保护逻辑
    if _is_private_dir(directory.name, config):
        generate_private_dir_index(directory, config, nav_tree)
        # 仍然递归处理子目录
        depth = len(directory.relative_to(ROOT).parts)
        exclude = _get_exclude(config)
        for entry in sorted(directory.iterdir()):
            if entry.name.startswith(".") or entry.name in exclude:
                continue
            if entry.is_dir():
                generate_dir_index(entry, config, nav_tree)
        return

    depth = len(directory.relative_to(ROOT).parts)
    root_prefix = "../" * depth
    parent_prefix = "../"

    exclude = _get_exclude(config)

    subdirs = []
    files = []
    for entry in sorted(directory.iterdir()):
        if entry.name.startswith(".") or entry.name in exclude:
            continue
        if entry.is_dir():
            subdirs.append(entry)
            generate_dir_index(entry, config, nav_tree)
        elif entry.is_file():
            if entry.suffix.lower() in (".md", ".html"):
                files.append(entry)
            elif entry.suffix.lower() in (".png", ".jpg", ".jpeg", ".gif", ".svg", ".pdf"):
                files.append(entry)

    dir_name = directory.name
    sidebar_html = build_sidebar_html(nav_tree, root_prefix, config)
    breadcrumb_html = build_breadcrumb(directory, root_prefix)

    subdir_html = ""
    for d in subdirs:
        file_count = sum(1 for _ in d.iterdir() if not _.name.startswith(".") and _.name not in exclude)
        tags = detect_tags(d)
        tag_str = " ".join(f'<span class="tag">{escape(t)}</span>' for t in tags)
        subdir_html += f"""
        <a class="project-card" href="{escape(d.name)}/">
          <h3>{escape(d.name)}</h3>
          <p>{file_count} 个文件</p>
          <div class="card-tags">{tag_str}</div>
        </a>"""

    file_html = ""
    for f in files:
        ext = f.suffix.lower()
        if ext == ".md":
            # 关键修复：使用完整的相对路径（从笔记根目录开始）
            md_rel = str(f.relative_to(ROOT)).replace("\\", "/")
            href = f"{root_prefix}md.html?file={escape(md_rel)}"
            label = "MD"
        elif ext == ".html":
            href = f.name
            label = "HTML"
        else:
            href = f.name
            label = ext[1:].upper()
        file_html += f"""
        <a class="file-link" href="{href}">
          <span class="file-label">{label}</span>
          <span class="file-name">{escape(f.stem)}</span>
        </a>"""

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escape(dir_name)}</title>
  <style>{SHARED_CSS}</style>
</head>
<body>
  {THEME_TOGGLE_BTN}
  {SIDEBAR_TOGGLE_BTN}
  {SIDEBAR_OVERLAY}
  {sidebar_html}
  <div class="main-wrap">
    <div class="page-container">
      <div class="breadcrumb">{breadcrumb_html}</div>
      <h1 class="page-title">{escape(dir_name)}</h1>
      {"<h2 class='section-title'>目录</h2><div class='projects'>" + subdir_html + "</div>" if subdir_html else ""}
      {"<h2 class='section-title'>文件</h2><div class='file-list'>" + file_html + "</div>" if file_html else "<p class='empty'>此目录为空</p>"}
    </div>
  </div>
  <script>{SHARED_JS}</script>
</body>
</html>"""

    index_path = directory / "index.html"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)


def generate_all_dir_indexes(config, nav_tree):
    exclude = _get_exclude(config)
    count = 0
    for entry in sorted(ROOT.iterdir()):
        if not entry.is_dir() or entry.name.startswith(".") or entry.name in exclude:
            continue
        generate_dir_index(entry, config, nav_tree)
        count += 1
    if count:
        print(f"Generated index pages for {count} top-level directories")


# ══════════════════════════════════════════════════════════
#  MD 查看器 JS — 加载并渲染 Markdown 文件
# ══════════════════════════════════════════════════════════
MD_VIEWER_JS = r"""
var _mdFile = new URLSearchParams(location.search).get('file');
// ═══ 加载 MD 文件 ═══
(function(){
    var file = _mdFile;
    var contentEl = document.getElementById('content');
    var breadcrumbEl = document.getElementById('breadcrumb');

    if (!file) {
      contentEl.className = 'error';
      contentEl.innerHTML = '未指定文件';
      return;
    }

    // 私有文件密码检查
    var _privateDirs = window._PRIVATE_DIRS || [];
    var _privatePwd = window._PRIVATE_PWD || '';
    var _firstDir = file.split('/')[0] || '';
    var _isPrivate = _privateDirs.indexOf(_firstDir) !== -1;
    function _isUnlocked(){try{return !!sessionStorage.getItem('_private_unlocked_'+_privatePwd);}catch(e){return false;}}
    function _askPwdMd(cb){
      var overlay=document.createElement('div');
      overlay.style.cssText='position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.4);z-index:400;display:flex;justify-content:center;align-items:center;';
      var box=document.createElement('div');
      box.style.cssText='background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:24px 28px;max-width:340px;width:90%;box-shadow:0 8px 32px var(--shadow);text-align:center;';
      box.innerHTML='<div style="font-size:32px;margin-bottom:12px">&#128274;</div><div style="font-size:15px;font-weight:600;color:var(--heading);margin-bottom:6px">需要密码</div><div style="font-size:13px;color:var(--muted);margin-bottom:16px">此文件已加密，请输入密码</div><div style="display:flex;gap:8px;justify-content:center"><input type="password" style="padding:8px 12px;font-size:14px;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:8px;outline:none;width:160px" autofocus><button style="padding:8px 16px;font-size:14px;background:var(--accent);color:#fff;border:none;border-radius:8px;cursor:pointer;font-weight:600">确认</button></div><div style="font-size:12px;color:#e74c3c;margin-top:8px;min-height:18px"></div>';
      overlay.appendChild(box);document.body.appendChild(overlay);
      var inp=box.querySelector('input'),btn=box.querySelector('button'),err=box.querySelectorAll('div')[4];
      inp.focus();
      function tryPw(){if(inp.value===_privatePwd){try{sessionStorage.setItem('_private_unlocked_'+_privatePwd,'1');}catch(e){}document.body.removeChild(overlay);cb();}else{err.textContent='密码错误';inp.value='';inp.focus();}}
      btn.addEventListener('click',tryPw);
      inp.addEventListener('keydown',function(e){if(e.key==='Enter')tryPw();});
      overlay.addEventListener('click',function(e){if(e.target===overlay)document.body.removeChild(overlay);});
    }

    var title = file.replace(/^.*\//, '').replace(/\.md$/, '');

    // 面包屑
    var parts = file.split('/');
    var crumb = '<a href="index.html">主页</a>';
    var pathAcc = '';
    for (var i = 0; i < parts.length; i++) {
      var seg = decodeURIComponent(parts[i]);
      if (i === parts.length - 1) {
        crumb += ' <span class="sep">/</span> <span class="current">' + seg.replace(/\.md$/, '') + '</span>';
      } else {
        pathAcc += encodeURIComponent(parts[i]) + '/';
        crumb += ' <span class="sep">/</span> <a href="' + pathAcc + '">' + seg + '</a>';
      }
    }
    breadcrumbEl.innerHTML = crumb;

    var fileDir = file.includes('/') ? file.substring(0, file.lastIndexOf('/')) + '/' : '';

    // 私有文件需要密码才能加载
    if (_isPrivate && !_isUnlocked()) {
      contentEl.className = 'md-content';
      contentEl.innerHTML = '<div style="text-align:center;padding:60px 20px;color:var(--muted)"><div style="font-size:48px;margin-bottom:16px">&#128274;</div><div style="font-size:16px;font-weight:600;color:var(--heading);margin-bottom:8px">此文件需要密码</div><div style="font-size:13px">请输入密码以查看内容</div></div>';
      _askPwdMd(function(){ location.reload(); });
      return;
    }

    fetch(file)
      .then(function(r) {
        if (!r.ok) throw new Error('文件未找到: ' + file);
        return r.text();
      })
      .then(function(md) {
        // 转换 Obsidian ![[image.png]] 为标准 Markdown 图片语法
        md = md.replace(/!\[\[([^\]|]+?)(\|([^\]]+))?\]\]/g, function(m, p1, p2, p3) {
          var alt = (p3 || p1).replace(/\.\w+$/, '');
          return '![' + alt + '](' + encodeURIComponent('附件/' + p1) + ')';
        });

        // 字数 & 阅读时间
        var metaEl = document.getElementById('meta-bar');
        if(metaEl){
          var chars = md.replace(/\s/g, '').length;
          var words = md.split(/\s+/).filter(function(w){return w;}).length;
          var mins = Math.max(1, Math.ceil(words / 300));
          metaEl.textContent = chars + ' 字 · 约 ' + mins + ' 分钟';
        }

        contentEl.className = 'md-content';
        contentEl.innerHTML = marked.parse(md, { breaks: true, gfm: true });
        document.title = title;

        // 图片路径 fallback: 附件/ 找不到时尝试 附件/图片/
        contentEl.querySelectorAll('img').forEach(function(img){
          img.addEventListener('error', function(){
            if(!img.dataset.retried){
              img.dataset.retried = '1';
              img.src = img.src.replace(encodeURIComponent('附件/'), encodeURIComponent('附件/图片/'));
            }
          });
        });

        // 显示 UI
        var dlBar = document.getElementById('dl-bar');
        if(dlBar) dlBar.classList.add('visible');
        if(window._showContentSearchBar) window._showContentSearchBar();

        // 生成目录
        _genToC();

        // KaTeX 渲染
        if(window.renderMathInElement){
          try{renderMathInElement(contentEl,{delimiters:[
            {left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false}
          ]});}catch(e){}
        }

        // 记录最近浏览
        _addRecent(file, title);
        _renderRecent();

        // 收藏按钮状态
        _updateFavBtn(file);

        // 恢复阅读位置
        try{
          var pos=JSON.parse(localStorage.getItem('scrollPositions')||'{}');
          if(pos[file])setTimeout(function(){window.scrollTo(0,pos[file]);},150);
        }catch(e){}
      })
      .catch(function(e) {
        contentEl.className = 'error';
        contentEl.innerHTML = '加载失败: ' + e.message + '<br><br><a href="' + fileDir + '" style="color:var(--accent)">返回上一级</a>';
      });
  })();

// ═══ 文章目录 ═══
function _genToC(){
  var content=document.getElementById('content');
  var tocEl=document.getElementById('toc-list');
  var sec=document.getElementById('toc-section');
  if(!content||!tocEl)return;
  var headings=content.querySelectorAll('h1,h2,h3');
  if(!headings.length){if(sec)sec.style.display='none';return;}
  if(sec)sec.style.display='';
  var html='';
  for(var i=0;i<headings.length;i++){
    var h=headings[i];
    var id='hd-'+i;
    h.id=id;
    var cls=h.tagName==='H3'?' toc-h3':h.tagName==='H4'?' toc-h4':'';
    html+='<a class="toc-link'+cls+'" href="#'+id+'">'+h.textContent+'</a>';
  }
  tocEl.innerHTML=html;
  var links=tocEl.querySelectorAll('.toc-link');
  window.addEventListener('scroll',function(){
    var sp=window.scrollY+120;var cur='';
    for(var i=0;i<headings.length;i++){if(headings[i].offsetTop<=sp)cur=headings[i].id;}
    links.forEach(function(a){a.classList.toggle('active',a.getAttribute('href')==='#'+cur);});
  },{passive:true});
}

// ═══ 阅读进度条 ═══
(function(){
  var bar=document.getElementById('reading-progress');
  if(!bar)return;
  function update(){
    var h=document.documentElement.scrollHeight-window.innerHeight;
    bar.style.width=(h>0?window.scrollY/h*100:0)+'%';
  }
  window.addEventListener('scroll',update,{passive:true});
  update();
})();

// ═══ 阅读进度记忆 ═══
window.addEventListener('beforeunload',function(){
  if(!_mdFile)return;
  try{var p=JSON.parse(localStorage.getItem('scrollPositions')||'{}');
  p[_mdFile]=window.scrollY;localStorage.setItem('scrollPositions',JSON.stringify(p));}catch(e){}
});

// ═══ 内容搜索 ═══
(function(){
  var input = document.getElementById('content-search-input');
  var countEl = document.getElementById('content-search-count');
  if(!input) return;
  var bar = input.closest('.content-search-bar');
  if(bar) bar.style.display = 'none';
  window._showContentSearchBar = function(){ if(bar) bar.style.display = 'flex'; };
  var highlights = [];
  var currentIdx = -1;
  function clearHL(){
    highlights.forEach(function(n){var p=n.parentNode;if(p){p.replaceChild(document.createTextNode(n.textContent),n);p.normalize();}});
    highlights=[];currentIdx=-1;
  }
  function doSearch(){
    clearHL();
    var q=input.value.trim();
    if(!q){countEl.textContent='';return;}
    var content=document.getElementById('content');
    if(!content||content.classList.contains('loading'))return;
    highlights=[];
    var walker=document.createTreeWalker(content,NodeFilter.SHOW_TEXT,null,false);
    var nodes=[];while(walker.nextNode())nodes.push(walker.currentNode);
    var regex=new RegExp('('+q.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+')','gi');
    for(var i=0;i<nodes.length;i++){
      var node=nodes[i];
      if(node.parentElement&&node.parentElement.closest&&node.parentElement.closest('pre,code,script,style,mark'))continue;
      var text=node.nodeValue;regex.lastIndex=0;
      if(!regex.test(text))continue;regex.lastIndex=0;
      var frag=document.createDocumentFragment();var last=0;var m;
      while((m=regex.exec(text))!==null){
        if(m.index>last)frag.appendChild(document.createTextNode(text.substring(last,m.index)));
        var mk=document.createElement('mark');mk.className='search-hl';mk.textContent=m[1];
        frag.appendChild(mk);highlights.push(mk);last=regex.lastIndex;
      }
      if(last<text.length)frag.appendChild(document.createTextNode(text.substring(last)));
      node.parentNode.replaceChild(frag,node);
    }
    countEl.textContent=highlights.length?highlights.length+' 个结果':'无结果';
    currentIdx=-1;if(highlights.length)jumpTo(1);
  }
  function jumpTo(dir){
    if(!highlights.length)return;
    for(var i=0;i<highlights.length;i++)highlights[i].style.background='rgba(184,134,11,0.3)';
    currentIdx=(currentIdx+dir+highlights.length)%highlights.length;
    highlights[currentIdx].style.background='rgba(184,134,11,0.6)';
    highlights[currentIdx].scrollIntoView({behavior:'smooth',block:'center'});
    countEl.textContent=(currentIdx+1)+'/'+highlights.length;
  }
  input.addEventListener('input',doSearch);
  input.addEventListener('keydown',function(e){
    if(e.key==='Enter'){e.preventDefault();jumpTo(e.shiftKey?-1:1);}
    if(e.key==='ArrowLeft'||e.key==='ArrowUp'){e.preventDefault();jumpTo(-1);}
    if(e.key==='ArrowRight'||e.key==='ArrowDown'){e.preventDefault();jumpTo(1);}
    if(e.key==='Escape'){input.value='';doSearch();input.blur();}
  });
  document.getElementById('search-prev').addEventListener('click',function(){jumpTo(-1);});
  document.getElementById('search-next').addEventListener('click',function(){jumpTo(1);});
  document.addEventListener('keydown',function(e){
    if((e.ctrlKey||e.metaKey)&&e.key==='f'){
      e.preventDefault();if(bar)bar.style.display='flex';input.focus();input.select();
    }
  });
})();

// ═══ 下载 & 收藏 ═══
(function(){
  var file=_mdFile;if(!file)return;
  var title=file.replace(/^.*\//,'').replace(/\.md$/,'');
  document.getElementById('dl-md').addEventListener('click',function(){
    fetch(file).then(function(r){return r.text();}).then(function(text){
      var a=document.createElement('a');
      a.href=URL.createObjectURL(new Blob([text],{type:'text/markdown;charset=utf-8'}));
      a.download=title+'.md';a.click();URL.revokeObjectURL(a.href);
    });
  });
  document.getElementById('dl-pdf').addEventListener('click',function(){window.print();});
  document.getElementById('fav-btn').addEventListener('click',function(){_toggleFav(file,title);});
})();
"""


def generate_md_html(config, nav_tree):
    """生成带侧边栏导航的 md.html"""
    sidebar_html = build_sidebar_html(nav_tree, "", config)
    # 在侧边栏中插入文章目录区（在 nav-tree 和最近浏览之间）
    toc_section = """
    <div class="sidebar-section" id="toc-section" style="display:none">
      <div class="sidebar-section-title">文章目录 <span class="section-arrow">\u25BE</span></div>
      <div class="toc-list" id="toc-list"></div>
    </div>
"""
    sidebar_html = sidebar_html.replace(
        '<div class="sidebar-section" id="recent-section">',
        toc_section + '<div class="sidebar-section" id="recent-section">'
    )

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Markdown Viewer</title>
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
  <style>{SHARED_CSS}</style>
</head>
<body>
  <div class="reading-progress" id="reading-progress"></div>
  {THEME_TOGGLE_BTN}
  {SIDEBAR_TOGGLE_BTN}
  {SIDEBAR_OVERLAY}
  <div class="dl-bar" id="dl-bar">
    <button class="dl-btn" id="fav-btn" title="收藏">&#9734;</button>
    <button class="dl-btn" id="dl-md">MD</button>
    <button class="dl-btn" id="dl-pdf">PDF</button>
  </div>
  {sidebar_html}
  <div class="shortcut-overlay" id="shortcut-overlay">
    <div class="shortcut-panel">
      <h3>键盘快捷键</h3>
      <div class="shortcut-row"><span>搜索文件</span><span class="shortcut-key">Ctrl+K</span></div>
      <div class="shortcut-row"><span>全局搜索</span><span class="shortcut-key">Ctrl+Shift+K</span></div>
      <div class="shortcut-row"><span>搜索内容</span><span class="shortcut-key">Ctrl+F</span></div>
      <div class="shortcut-row"><span>切换主题</span><span class="shortcut-key">T</span></div>
      <div class="shortcut-row"><span>显示/关闭帮助</span><span class="shortcut-key">?</span></div>
    </div>
  </div>
  <div class="global-search-overlay" id="global-search-overlay">
    <div class="global-search-panel">
      <div class="global-search-input-wrap">
        <input class="global-search-input" id="global-search-input" placeholder="搜索所有笔记..." autocomplete="off">
        <button class="global-search-close" id="global-search-close">&times;</button>
      </div>
      <div class="global-search-results" id="global-search-results"><div class="global-search-empty">输入关键词搜索所有笔记</div></div>
    </div>
  </div>
  <button class="back-to-top" id="back-to-top" title="返回顶部">&#8593;</button>
  <div class="main-wrap">
    <div class="page-container">
      <div class="breadcrumb" id="breadcrumb"></div>
      <div class="meta-bar" id="meta-bar"></div>
      <div class="content-search-bar" id="content-search-bar">
        <input id="content-search-input" type="text" placeholder="搜索内容...">
        <span class="search-count" id="content-search-count"></span>
        <button class="search-bar-btn" id="search-prev" title="上一个">&uarr;</button>
        <button class="search-bar-btn" id="search-next" title="下一个">&darr;</button>
      </div>
      <div id="content" class="loading">加载中...</div>
    </div>
  </div>
  <script>{SHARED_JS}
{MD_VIEWER_JS}</script>
</body>
</html>"""

    md_path = ROOT / "md.html"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Generated {md_path}")


# ══════════════════════════════════════════════════════════
#  主函数
# ══════════════════════════════════════════════════════════
def main():
    config = load_config()
    nav_tree = build_nav_tree(config)
    projects = scan_projects(config)

    html = generate_html(config, projects, nav_tree)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Generated {OUTPUT_PATH} with {len(projects)} projects")

    generate_all_dir_indexes(config, nav_tree)
    generate_md_html(config, nav_tree)


if __name__ == "__main__":
    main()
