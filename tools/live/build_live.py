"""產生實測版頁面：把 out/rules.json 與範例 Excel 內嵌進 live.template.html，輸出到 out/live/。
輸出含部門規則原文，只發布成 claude.ai 私人成品，不 commit。"""
import sys, json, base64
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[2]
tpl = (ROOT / "tools/live/live.template.html").read_text(encoding="utf-8")
rules = json.loads((ROOT / "out/rules.json").read_text(encoding="utf-8"))
CASES = {
    "chiller": ("模擬測試_冰水主機三家報價分析_v1.xlsx", "使用單位希望年底前完成下單；加權係數（CAPEX 20%／OPEX 80%）尚未簽核。"),
    "simple": ("模擬測試_國內備品軸承三家報價_v1.xlsx", "例行保養備品，規格與前次相同。"),
}
samples = {k: {"name": n, "memo": m, "b64": base64.b64encode((ROOT / "out/test-cases" / n).read_bytes()).decode()} for k, (n, m) in CASES.items()}
html = tpl.replace("/*RULES_JSON*/null", json.dumps(rules, ensure_ascii=False, separators=(",", ":")))
html = html.replace("/*SAMPLES_JSON*/{}", json.dumps(samples, ensure_ascii=False))
imgs = {p.stem: "data:image/webp;base64," + base64.b64encode(p.read_bytes()).decode() for p in (ROOT / "assets/islands").glob("*.webp")}
html = html.replace("/*IMG_JSON*/{}", json.dumps(imgs))
out = ROOT / "out/live/kys-live.html"; out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(html, encoding="utf-8")
print(out, f"{len(html.encode()):,} bytes")
