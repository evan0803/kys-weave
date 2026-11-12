"""產生簡報用離線版：把 three.js 與 OrbitControls 內嵌進 index.html，並移除 Google Fonts 連結。
輸出 out/offline/遠東經緯島_離線版.html，放進 USB 直接用瀏覽器開，不需要網路。
先執行 npm install（取得 node_modules/three）。"""
import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
html = (ROOT / "index.html").read_text(encoding="utf-8")
three = ROOT / "node_modules/three"
libs = {
    "three@0.147.0/build/three.min.js": three / "build/three.min.js",
    "three@0.147.0/examples/js/controls/OrbitControls.js": three / "examples/js/controls/OrbitControls.js",
}
for key, path in libs.items():
    tag = re.search(r'<script src="https://cdn\.jsdelivr\.net/npm/' + re.escape(key) + r'"></script>', html)
    if not tag:
        sys.exit(f"找不到 {key} 的 script 標籤")
    code = path.read_text(encoding="utf-8").replace("</script", "<\\/script")
    html = html[:tag.start()] + "<script>\n" + code + "\n</script>" + html[tag.end():]
html, n = re.subn(r'<link[^>]+fonts\.googleapis\.com[^>]*>\s*', "", html)
left = re.findall(r'(?:src|href)="(https?://[^"]+)"', html)
out = ROOT / "out/offline/遠東經緯島_離線版.html"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(html, encoding="utf-8")
print(out, f"{len(html.encode()):,} bytes；移除字型連結 {n} 個；剩餘外部資源 {left}")
