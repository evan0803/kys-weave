"""把知識層六部門規則匯出成 out/rules.json，供實測版網頁使用。
out/ 已 gitignore：規則含部門原文，只在本機與私人成品中使用。"""
import sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).resolve().parent))
from kys_content3 import *  # noqa: F401,F403  載入 DEPTS（已含部門原文與代擬條目）

OUT = Path(__file__).resolve().parents[2] / "out"; OUT.mkdir(exist_ok=True)
ORDER = ["proc", "fin", "acct", "intl", "aud", "jaud"]
FIELDS = ["id", "principle", "question", "situation", "level", "window", "step", "tags", "src"]

# 觸發標籤分類（2026-11-12 實測版調整，待小組討論）：
# attribute＝案件屬性，可由欄位直接判讀；risk＝風險特徵，必須有證據
RISK_TAGS = {"首次交易", "預付款", "非最低價決標", "匯款帳戶變更", "單一報價／指定廠商", "付款條件變更",
             "追加變更", "緊急採購", "空運急件", "可能屬管制品"}
# 規則庫預留欄位（期末由部門確認稿補齊；目前全部空白）
RESERVED = {"stages": None, "impact": None, "action": None}  # 適用階段／影響層級 L1-L3／標準建議動作

out = {"version": "v0.3", "depts": [], "tagTypes": {}}
for k in ORDER:
    d = DEPTS[k]
    rules = []
    for r in d["rules"]:
        row = dict(zip(FIELDS, r))
        row["tags"] = [t.strip() for t in str(row.get("tags") or "").replace("、", "，").split("，") if t.strip()]
        rules.append({**{f: row.get(f) for f in FIELDS}, **RESERVED})
    out["depts"].append({"key": k, "code": d.get("code"), "name": d["name"], "rules": rules})
all_tags = sorted({t for d in out["depts"] for r in d["rules"] for t in r["tags"] if not t.startswith("（")})
unknown = RISK_TAGS - set(all_tags)
if unknown:
    sys.exit(f"RISK_TAGS 有不存在的標籤：{unknown}")
out["tagTypes"] = {t: ("risk" if t in RISK_TAGS else "attribute") for t in all_tags}
print("標籤", len(all_tags), "個：risk", sorted(RISK_TAGS), "；其餘為 attribute")

p = OUT / "rules.json"
p.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(p, sum(len(d["rules"]) for d in out["depts"]), [(d["name"], len(d["rules"])) for d in out["depts"]])
print(out["depts"][1]["rules"][0])
