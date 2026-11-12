"""把知識層六部門規則匯出成 out/rules.json，供實測版網頁使用。
out/ 已 gitignore：規則含部門原文，只在本機與私人成品中使用。
欄位與疊加邏輯在 kb_layer.py（2026-11-13 新增類別、用途、觸發條件、影響類型等欄位）。"""
import sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import kb_layer  # noqa: E402

OUT = Path(__file__).resolve().parents[2] / "out"; OUT.mkdir(exist_ok=True)
FIELDS = kb_layer.FIELDS  # id … src ＋ category, use, trigger, impact_type, impact, consequence, action, status, confirmed_by, version_note, stages

# 觸發標籤分類（2026-11-12 實測版調整，待小組討論）：
# attribute＝案件屬性，可由欄位直接判讀；risk＝風險特徵，必須有證據
RISK_TAGS = {"首次交易", "預付款", "非最低價決標", "匯款帳戶變更", "單一報價／指定廠商", "付款條件變更",
             "追加變更", "緊急採購", "空運急件", "可能屬管制品"}

out = {"version": "v0.4", "depts": kb_layer.build(), "tagTypes": {}}
all_tags = sorted({t for d in out["depts"] for r in d["rules"] for t in r["tags"] if not t.startswith("（")})
unknown = RISK_TAGS - set(all_tags)
if unknown:
    sys.exit(f"RISK_TAGS 有不存在的標籤：{unknown}")
out["tagTypes"] = {t: ("risk" if t in RISK_TAGS else "attribute") for t in all_tags}
print("標籤", len(all_tags), "個：risk", sorted(RISK_TAGS), "；其餘為 attribute")

c = kb_layer.counts(out["depts"])
print("統計", c)
# 尚未合併任何部門回覆時，數字應與 v0.4 確認稿一致
if not (kb_layer.DATA / "kb_review_state.json").exists():
    expect = {"總數": 126, "一般檢查": 104, "進一步建議": 22, "事前會診": 106, "履約後查核": 20, "停用": 0}
    if c != expect:
        sys.exit(f"統計與 v0.4 不符：{c} ≠ {expect}")

p = OUT / "rules.json"
p.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(p, c["總數"], [(d["name"], len(d["rules"])) for d in out["depts"]])
