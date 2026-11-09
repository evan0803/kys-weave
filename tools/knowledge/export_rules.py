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

out = {"version": "v0.3", "depts": []}
for k in ORDER:
    d = DEPTS[k]
    rules = []
    for r in d["rules"]:
        row = dict(zip(FIELDS, r))
        row["tags"] = [t.strip() for t in str(row.get("tags") or "").replace("、", "，").split("，") if t.strip()]
        rules.append({f: row.get(f) for f in FIELDS})
    out["depts"].append({"key": k, "code": d.get("code"), "name": d["name"], "rules": rules})

p = OUT / "rules.json"
p.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(p, sum(len(d["rules"]) for d in out["depts"]), [(d["name"], len(d["rules"])) for d in out["depts"]])
print(out["depts"][1]["rules"][0])
