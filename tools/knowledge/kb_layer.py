"""知識層：在部門原文（kys_content3.DEPTS，不改）之上，疊加 2026-11-13 新增的欄位。

疊加順序：部門原文 → 預設值（由 level／step 推得）→ 暫擬內容（review_drafts.py ＋ data/review_drafts_jaud.json）
→ 確認稿回收結果（data/kb_review_state.json，由 merge_review.py 產生；不存在時略過）。

狀態檔格式（供 merge_review.py 寫入）：
  {"rules": {"F-02": {"confirmed_by": "王小明", "status": "停用", ...}},   # 只寫要覆蓋的欄位
   "added": [{"dept": "fin", "id": "F-12", "principle": ..., ...}]}       # 部門新增條目
"""
import sys, json
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from kys_content3 import DEPTS  # noqa: E402  部門原文與代擬條目
import review_drafts as RD  # noqa: E402

ROOT = HERE.parents[1]
DATA = ROOT / "data"
ORDER = ["proc", "fin", "acct", "intl", "aud", "jaud"]
BASE = ["id", "principle", "question", "situation", "level", "window", "step", "tags", "src"]
# 2026-11-13 新增（實測版調整，待小組討論確認）；stages 為 11/12 預留欄位，保留
NEW = ["category", "use", "trigger", "impact_type", "impact", "consequence", "action",
       "status", "confirmed_by", "version_note", "stages"]
FIELDS = BASE + NEW
ORIGINAL = ("principle", "question", "situation")  # 部門原文，任何疊加都不得覆蓋
CAT = {"一般": "一般檢查", "進階": "進一步建議"}


def load_drafts():
    """回傳 {編號: {trigger, impact_type, impact, consequence, what, to, when}}，含聯稽私有檔。"""
    p = DATA / "review_drafts_jaud.json"
    if not p.exists():
        sys.exit(f"缺少 {p.relative_to(ROOT)}（聯稽暫擬，只放本機）。少了它進一步建議會從 22 條變 14 條。")
    adv = {k: dict(zip(RD.ADV_KEYS, v)) for k, v in RD.ADV.items()}
    adv.update(json.loads(p.read_text(encoding="utf-8")))
    return adv


def load_state():
    p = DATA / "kb_review_state.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"rules": {}, "added": []}


def _tags(v):
    if isinstance(v, list):
        return v
    return [t.strip() for t in str(v or "").replace("、", "，").split("，") if t.strip()]


def _defaults(row):
    row["tags"] = _tags(row.get("tags"))
    row.setdefault("category", CAT.get(row.get("level"), "一般檢查"))
    if row["id"] in RD.USE_BOTH:
        use = "事前會診＋履約後"
    else:
        use = "履約後查核" if row.get("step") == "下單後" else "事前會診"
    row.setdefault("use", use)
    row.setdefault("status", "有效")
    for f in NEW:
        row.setdefault(f, None)
    return row


def build():
    """回傳 [{key, code, name, rules:[{FIELDS...}]}]，依 ORDER 排列。"""
    adv, state = load_drafts(), load_state()
    ids = {r[0] for k in ORDER for r in DEPTS[k]["rules"]}
    missing = set(adv) - ids
    if missing:
        sys.exit(f"暫擬內容的編號不存在：{sorted(missing)}")
    out = []
    for k in ORDER:
        d = DEPTS[k]; rules = []
        for r in d["rules"]:
            row = dict(zip(BASE, r))
            a = adv.get(row["id"])
            if a:
                row.update(category="進一步建議", trigger=a["trigger"], impact_type=a["impact_type"],
                           impact=a["impact"], consequence=a["consequence"],
                           action={"what": a["what"], "to": a["to"], "when": a["when"]},
                           version_note=RD.DRAFT_NOTE + ("；類別由一般改列進一步建議，待部門判斷" if row["id"] in RD.UPGRADE else ""))
            _defaults(row)
            row.update({f: v for f, v in state["rules"].get(row["id"], {}).items() if f not in ORIGINAL and f != "id"})
            rules.append({f: row.get(f) for f in FIELDS})
        for n in state.get("added", []):
            if n.get("dept") == k:
                rules.append({f: v for f, v in _defaults(dict(n)).items() if f in FIELDS})
        out.append({"key": k, "code": d.get("code"), "name": d["name"], "rules": rules})
    return out


def counts(depts):
    rs = [r for d in depts for r in d["rules"]]
    c = lambda f, v: sum(1 for r in rs if r[f] == v)
    return {"總數": len(rs), "一般檢查": c("category", "一般檢查"), "進一步建議": c("category", "進一步建議"),
            "事前會診": sum(1 for r in rs if r["use"].startswith("事前會診")), "履約後查核": c("use", "履約後查核"),
            "停用": c("status", "停用")}
