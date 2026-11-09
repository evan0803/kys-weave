# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from kys_content3 import *
from openpyxl import Workbook
from pathlib import Path
OUT = Path(__file__).resolve().parents[2] / "out"; OUT.mkdir(exist_ok=True)
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.comments import Comment

FONT = "微軟正黑體"
NAVY = "16324F"
F_H = Font(name=FONT, bold=True, color="FFFFFF", size=11)
F_B = Font(name=FONT, size=10.5)
F_BB = Font(name=FONT, size=10.5, bold=True)
F_T = Font(name=FONT, size=16, bold=True, color=NAVY)
F_S = Font(name=FONT, size=10.5, color="5D6B78")
FILL_H = PatternFill("solid", fgColor=NAVY)
FILL_IN = PatternFill("solid", fgColor="FFF2B3")
FILL_DEMO = PatternFill("solid", fgColor="F3F5F7")
FILL_SEC = PatternFill("solid", fgColor="E3ECF4")
THIN = Side(style="thin", color="C9D3DC")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical="top")
CENTER = Alignment(horizontal="center", vertical="top", wrap_text=True)
CONFIRM = ["保留", "修改", "刪除"]
NEW_ROWS = 8

def header(ws, row, cols, widths, confirm_from=None):
    for i, (c, w) in enumerate(zip(cols, widths), 1):
        cell = ws.cell(row=row, column=i, value=c)
        cell.font = F_H; cell.fill = FILL_H; cell.alignment = CENTER; cell.border = BOX
        ws.column_dimensions[cell.column_letter].width = w
        if confirm_from and i >= confirm_from:
            cell.fill = PatternFill("solid", fgColor="B07B12")
    ws.row_dimensions[row].height = 34

def body(ws, r, values, input_cols=(), center_cols=()):
    for i, v in enumerate(values, 1):
        c = ws.cell(row=r, column=i, value=v)
        c.font = F_B; c.border = BOX
        c.alignment = CENTER if i in center_cols else WRAP
        if i in input_cols:
            c.fill = FILL_IN

def title(ws, text, sub):
    ws["A1"] = text; ws["A1"].font = F_T
    ws["A2"] = sub; ws["A2"].font = F_S
    ws.row_dimensions[1].height = 28

def dv_list(ws, items, ref):
    dv = DataValidation(type="list", formula1='"' + ",".join(items) + '"', allow_blank=True)
    dv.error = "請從下拉選單選擇"; dv.errorTitle = "選項不符"
    ws.add_data_validation(dv); dv.add(ref)

def build(key):
    d = DEPTS[key]; wb = Workbook()

    # 1. 填寫說明
    ws = wb.active; ws.title = "填寫說明"
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 4; ws.column_dimensions["B"].width = 22; ws.column_dimensions["C"].width = 80
    ws["B1"] = f"KYS 知識層確認稿｜{d['name']}"; ws["B1"].font = F_T
    ws["B2"] = f"遠東經緯島・{d['landmark']}　草稿日期：2026-11-07　版本：v0.3（採購處代擬，待 {d['name']} 確認）"; ws["B2"].font = F_S
    rows = [
        ("這份檔案是什麼", f"採購處依採購作業流程與常見案件，先擬好「{d['name']}在會診時可以提供什麼、要檢查什麼」的草稿。請貴部門確認、修正、補充，不必從零開始寫。"),
        ("要做的事", "1. 在黃色欄位選「保留／修改／刪除」。\n2. 選「修改」時，在旁邊的黃色欄位寫下修正內容。\n3. 草稿沒寫到的，請填在每張表最下方的「新增」列。\n4. 數字標示「示範值」者，請改成貴部門實際採用的門檻；若屬機密，維持示範值即可。"),
        ("填寫範例", "規則 F-06 預付款保證：確認欄選「修改」，修正欄寫「門檻改為 30%，保證函期限需涵蓋到貨後 30 天」。"),
        ("工作表說明", "• 案例參考：兩件設備組實際案件（去識別化），示範各部門如何參與會診\n• 服務項目：其他部門送件後，貴部門可以回覆的專業意見\n• 檢核規則：什麼情況一定要找貴部門、要問什麼問題（格式與聯稽一致）\n• 採購情境對應：採購實際常遇到的案件，希望貴部門提供的資訊\n• 燈號判定：貴部門何時給綠、黃、紅燈\n• 共用標籤：平台用來自動派案的條件清單（各部門共用）" + ("\n• 費率表欄位：物流費率表的欄位格式與示範資料" if d["rate"] else "")),
        ("燈號定義", "綠燈＝允許（可附建議）；黃燈＝無其他意見；紅燈＝嚴重紅旗，處理後再送會診。"),
        ("一般／進階", "一般＝經辦查表即可處理；進階＝需轉貴部門窗口會診，請在「進階窗口」欄填寫窗口（原型階段可寫職稱即可）。"),
        *([("版本說明", d["note"])] if d.get("note") else []),
        ("資安原則", "目前平台是模擬環境，只放結論層的規則與虛構個案。請勿填入真實廠商名稱、金額、查核報告原文或個人資料。"),
        ("交回時間（建議）", "2026-11-12（四）前交回採購處 Evan，供 11/19 更新原型 v0.3。"),
    ]
    r = 4
    for k, v in rows:
        ws.cell(row=r, column=2, value=k).font = F_BB
        c = ws.cell(row=r, column=3, value=v); c.font = F_B; c.alignment = WRAP
        ws.cell(row=r, column=2).alignment = WRAP
        ws.row_dimensions[r].height = max(22, 18 * (v.count("\n") + 1 + len(v) // 60))
        r += 1
    ws.cell(row=r+1, column=2, value="圖例").font = F_BB
    ws.cell(row=r+1, column=3, value="黃色儲存格＝請貴部門填寫或確認").fill = FILL_IN
    ws.cell(row=r+2, column=3, value="灰色儲存格＝示範資料，可直接改寫").fill = FILL_DEMO
    for rr in (r+1, r+2): ws.cell(row=rr, column=3).font = F_B

    # 1b. 案例參考
    ws = wb.create_sheet("案例參考")
    title(ws, "真實案例參考｜各部門如何參與會診", "依設備組實際案件改編，廠商名稱已去識別化、金額取整數。黃底列為貴部門的會診重點，請確認是否合理。")
    ws.column_dimensions["A"].width = 16; ws.column_dimensions["B"].width = 60; ws.column_dimensions["C"].width = 22; ws.column_dimensions["D"].width = 10; ws.column_dimensions["E"].width = 34
    r = 4
    order = ["proc", "fin", "acct", "intl", "aud", "jaud"]
    for case in REAL_CASES:
        c = ws.cell(row=r, column=1, value=f"{case['code']}｜{case['title']}"); c.font = Font(name=FONT, size=13, bold=True, color=NAVY)
        ws.cell(row=r+1, column=1, value=case["src"]).font = F_S; r += 2
        for k, v in case["facts"]:
            body(ws, r, [k, v]); ws.cell(row=r, column=1).font = F_BB; ws.cell(row=r, column=1).fill = FILL_SEC; ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=5); r += 1
        r += 1
        header(ws, r, ["部門", "會診重點", "對應規則", "預期燈號", "修正或補充"], [16, 60, 22, 10, 34]); r += 1
        for dk in order:
            focus, rule, light = case["consult"][dk]
            body(ws, r, [DEPTS[dk]["name"], focus, rule, light, None], input_cols=(5,) if dk == key else (), center_cols=(4,))
            if dk == key:
                for i in range(1, 5): ws.cell(row=r, column=i).fill = FILL_IN
                ws.cell(row=r, column=1).font = F_BB
            r += 1
        r += 2

    # 2. 服務項目
    ws = wb.create_sheet("服務項目")
    title(ws, f"{d['name']}｜我能提供的服務", "其他部門（目前以採購處為入口）送件後，貴部門可以回覆的專業意見。回覆時效為建議值。")
    cols = ["編號", "服務名稱", "服務內容", "送件方需提供的資料", "回覆內容", "回覆時效（建議）", "確認", "修正或補充"]
    header(ws, 4, cols, [8, 18, 34, 34, 26, 14, 10, 32], confirm_from=7)
    r = 5
    for i, s in enumerate(d["services"], 1):
        body(ws, r, [f"{d['code']}S-{i:02d}", *s, None, None], input_cols=(7, 8), center_cols=(1, 6, 7)); r += 1
    first_new = r
    for j in range(NEW_ROWS):
        body(ws, r, ["新增"] + [None]*7, input_cols=range(2, 9), center_cols=(1,)); r += 1
    dv_list(ws, CONFIRM, f"G5:G{first_new-1}")
    ws.freeze_panes = "C5"

    # 3. 檢核規則
    ws = wb.create_sheet("檢核規則")
    title(ws, f"{d['name']}｜檢核規則（格式與聯稽一致，另加觸發標籤）", "觸發標籤請從「共用標籤」表選用，可多選，以頓號分隔；平台依標籤自動派案。")
    cols = ["編號", "原則（簡短名稱）", "要問的問題／提醒事項", "適用情境", "一般／進階", "進階窗口", "檢核時點（採購八步）", "觸發標籤", "來源", "確認", "修正或補充"]
    header(ws, 4, cols, [9, 18, 46, 22, 10, 18, 14, 22, 16, 10, 34], confirm_from=10)
    r = 5
    for ru in d["rules"]:
        body(ws, r, [*ru, None, None], input_cols=(10, 11), center_cols=(1, 5, 7, 10))
        if "代擬" in ru[8] or "補充" in ru[8]: ws.cell(row=r, column=9).fill = FILL_DEMO
        r += 1
    first_new = r
    for j in range(NEW_ROWS):
        body(ws, r, ["新增"] + [None]*7 + ["部門新增", None, None], input_cols=list(range(2, 9)) + [10, 11], center_cols=(1, 5, 7)); r += 1
    dv_list(ws, CONFIRM, f"J5:J{first_new-1}")
    dv_list(ws, ["一般", "進階"], f"E5:E{r-1}")
    dv_list(ws, STEPS, f"G5:G{r-1}")
    ws.freeze_panes = "C5"

    # 4. 採購情境對應
    ws = wb.create_sheet("採購情境對應")
    title(ws, f"採購常見情境｜希望{d['name']}提供的資訊", "以下是採購實際常遇到的案件類型（內容已去識別化）。請確認希望貴部門提供的資訊是否合理，也歡迎補充貴部門常見的情境。")
    cols = ["代號", "情境", "採購八步節點", "採購常遇到的狀況", f"希望{d['name']}提供的資訊", "貴部門是否會參與", "修正或補充"]
    header(ws, 4, cols, [7, 26, 16, 38, 44, 12, 34], confirm_from=6)
    r = 5
    for code, name, step, sit, ask in SCENARIOS:
        body(ws, r, [code, name, step, sit, ask[key], None, None], input_cols=(6, 7), center_cols=(1, 3, 6)); r += 1
    first_new = r
    for j in range(4):
        body(ws, r, ["新增"] + [None]*6, input_cols=range(2, 8), center_cols=(1,)); r += 1
    dv_list(ws, ["會參與", "偶爾參與", "不涉及"], f"F5:F{r-1}")
    ws.freeze_panes = "C5"

    # 5. 燈號判定
    ws = wb.create_sheet("燈號判定")
    title(ws, f"{d['name']}｜燈號判定標準", "一鍵會診時，貴部門依下列標準回覆燈號。請確認紅燈的判定條件。")
    cols = ["燈號", "判定標準（草稿）", "範例", "確認", "修正或補充"]
    header(ws, 4, cols, [18, 56, 40, 10, 36], confirm_from=4)
    light_fill = {"綠": "D8EFDF", "黃": "FBEBC4", "紅": "F6D5DA"}
    r = 5
    for lt in d["lights"]:
        body(ws, r, [*lt, None, None], input_cols=(4, 5), center_cols=(4,))
        ws.cell(row=r, column=1).fill = PatternFill("solid", fgColor=light_fill[lt[0][0]]); r += 1
    dv_list(ws, CONFIRM, f"D5:D{r-1}")

    # 6. 共用標籤
    ws = wb.create_sheet("共用標籤")
    title(ws, "共用觸發標籤（六個部門共用）", "採購送件時勾選這些標籤，平台再依各部門規則上的標籤派案。新增建議請填在最下方。")
    cols = ["類別", "標籤", "說明", "狀態", f"{d['name']}意見"]
    header(ws, 4, cols, [14, 20, 48, 14, 36], confirm_from=5)
    r = 5
    for t in TAGS_BASE:
        body(ws, r, [*t, "第一版", None], input_cols=(5,), center_cols=(1, 4)); r += 1
    for t in TAGS_NEW:
        body(ws, r, [*t, "新增建議", None], input_cols=(5,), center_cols=(1, 4))
        ws.cell(row=r, column=4).fill = FILL_SEC; r += 1
    for j in range(4):
        body(ws, r, [None, None, None, "新增", None], input_cols=(1, 2, 3, 5), center_cols=(1, 4)); r += 1
    ws.freeze_panes = "A5"

    # 7. 費率表欄位
    if d["rate"]:
        ws = wb.create_sheet("費率表欄位")
        title(ws, "國際事務處物流費率表｜欄位格式與示範資料", "灰色為示範資料（非實際費率）。請確認欄位是否符合貴部門現行費率表；實際費率屬內部資料，原型階段維持示範值即可。")
        header(ws, 4, RATE_COLS, [16, 12, 8, 10, 9, 24, 11, 12, 9, 14, 12, 10, 10, 26])
        r = 5
        for row in RATE_ROWS:
            body(ws, r, row, center_cols=(3, 5, 9, 12))
            for i in range(1, len(row)+1): ws.cell(row=r, column=i).fill = FILL_DEMO
            for i in (7, 8, 10, 11): ws.cell(row=r, column=i).number_format = '#,##0'
            ws.cell(row=r, column=9).number_format = '0%'
            r += 1
        r += 1
        ws.cell(row=r, column=1, value="欄位確認").font = F_BB
        ws.cell(row=r, column=2, value="現行費率表是否還有其他欄位（例如燃油附加費、旺季附加費、目的港費用）？請寫在右側：").font = F_B
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=7)
        c = ws.cell(row=r, column=8); c.fill = FILL_IN; c.border = BOX
        ws.merge_cells(start_row=r, start_column=8, end_row=r, end_column=14)
        ws.freeze_panes = "B5"

    import math
    for w in [x for x in wb.worksheets[1:]]:
        for row in w.iter_rows(min_row=5):
            n=1
            for c in row:
                if c.value is None or c.coordinate in w.merged_cells or c.font.sz and c.font.sz>=13 or (c.font.color is not None and str(c.font.color.rgb).endswith('5D6B78')): continue
                if any(c.coordinate in m for m in w.merged_cells.ranges): wd_override=110
                else: wd_override=None
                wd=wd_override or w.column_dimensions[c.column_letter].width or 10
                t=str(c.value); units=sum(2 if ord(ch)>255 else 1 for ch in t)
                n=max(n,math.ceil(units/max(wd-1,4)))
            w.row_dimensions[row[0].row].height=max(20,16*n+6)
    for w in wb.worksheets:
        w.sheet_properties.pageSetUpPr.fitToPage = True
        w.page_setup.orientation = "landscape"; w.page_setup.fitToWidth = 1; w.page_setup.fitToHeight = 0

    out = f"{OUT}/KYS知識層確認稿_{d['name']}_v0.3_20261107.xlsx"
    wb.save(out); print(out)

for k in ("proc", "fin", "acct", "intl", "aud", "jaud"):
    build(k)

# ---------- 總表 ----------
def master():
    import math
    wb = Workbook(); order = ["proc", "fin", "acct", "intl", "aud", "jaud"]
    ws = wb.active; ws.title = "全部規則"
    title(ws, "KYS 知識層總表｜六部門檢核規則（v0.3）", "採購處彙整用；各部門確認後回填。觸發標籤供遠東經緯島自動派案。")
    cols = ["部門", "地標", "編號", "原則（簡短名稱）", "要問的問題／提醒事項", "適用情境", "一般／進階", "進階窗口", "檢核時點（採購八步）", "觸發標籤", "來源", "部門確認狀態"]
    header(ws, 4, cols, [10, 12, 9, 18, 50, 22, 9, 18, 14, 24, 16, 12]); r = 5
    for k in order:
        d = DEPTS[k]
        for ru in d["rules"]:
            body(ws, r, [d["name"], d["landmark"], *ru, "待確認"], center_cols=(1, 3, 7, 9, 12)); r += 1
    ws.auto_filter.ref = f"A4:L{r-1}"; ws.freeze_panes = "D5"
    ws2 = wb.create_sheet("全部服務")
    title(ws2, "六部門服務項目", "")
    header(ws2, 4, ["部門", "編號", "服務名稱", "服務內容", "送件方需提供的資料", "回覆內容", "回覆時效（建議）"], [10, 8, 18, 36, 36, 28, 14]); r = 5
    for k in order:
        d = DEPTS[k]
        for i, s in enumerate(d["services"], 1):
            body(ws2, r, [d["name"], f"{d['code']}S-{i:02d}", *s], center_cols=(1, 2, 7)); r += 1
    ws3 = wb.create_sheet("採購情境")
    title(ws3, "採購常見情境 × 六部門需求", "C10、C11 為設備組真實案件改編（去識別化）。")
    header(ws3, 4, ["代號", "情境", "採購八步節點", "狀況"] + [DEPTS[k]["name"] for k in order], [7, 26, 16, 36] + [28]*6); r = 5
    for code, name, step, sit, ask in SCENARIOS:
        body(ws3, r, [code, name, step, sit] + [ask.get(k, "") for k in order], center_cols=(1, 3)); r += 1
    ws3.freeze_panes = "C5"
    ws4 = wb.create_sheet("共用標籤")
    title(ws4, "共用觸發標籤", "")
    header(ws4, 4, ["類別", "標籤", "說明", "狀態", "使用部門數"], [14, 20, 48, 12, 12]); r = 5
    allrules = [ru for k in order for ru in DEPTS[k]["rules"]]
    for t in TAGS_BASE + TAGS_NEW:
        n = sum(1 for k in order if any(t[1] in ru[7] for ru in DEPTS[k]["rules"]))
        body(ws4, r, [*t, "第一版" if t in TAGS_BASE else "新增建議", n], center_cols=(1, 4, 5)); r += 1
    for w in wb.worksheets:
        for row in w.iter_rows(min_row=5):
            n = 1
            for c in row:
                if c.value is None: continue
                wd = w.column_dimensions[c.column_letter].width or 10
                u = sum(2 if ord(ch) > 255 else 1 for ch in str(c.value)); n = max(n, math.ceil(u / max(wd - 1, 4)))
            w.row_dimensions[row[0].row].height = max(20, 16 * n + 6)
    out = f"{OUT}/KYS知識層總表_六部門_v0.3_20261107.xlsx"; wb.save(out); print(out)
master()
