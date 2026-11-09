"""產生實測版頁面：把 out/rules.json 與範例 Excel 內嵌進 live.template.html，輸出到 out/live/。
輸出含部門規則原文，只發布成 claude.ai 私人成品，不 commit。"""
import sys, json, base64
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[2]
tpl = (ROOT / "tools/live/live.template.html").read_text(encoding="utf-8")
rules = json.loads((ROOT / "out/rules.json").read_text(encoding="utf-8"))
xlsx = ROOT / "out/test-cases/模擬測試_冰水主機三家報價分析_v1.xlsx"
html = tpl.replace("/*RULES_JSON*/null", json.dumps(rules, ensure_ascii=False, separators=(",", ":")))
html = html.replace("/*SAMPLE_B64*/", base64.b64encode(xlsx.read_bytes()).decode())
out = ROOT / "out/live/kys-live.html"; out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(html, encoding="utf-8")
print(out, f"{len(html.encode()):,} bytes")
