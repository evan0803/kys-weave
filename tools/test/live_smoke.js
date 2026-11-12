// 實測版冒煙測試：以假的 claude.sample 跑「範例檔 → 整理重點 → 六部門會診 → 彙整首屏」，
// 第二次會診讓彙整故意失敗，確認能退回逐條版面。印出各項檢查結果。
const { chromium } = require("playwright");
const path = require("path");
(async () => {
  const file = path.resolve(__dirname, "../../out/live/kys-live.html");
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1100, height: 1400 } });
  const errors = [];
  page.on("pageerror", e => errors.push(e.message));
  page.on("console", m => m.type() === "error" && errors.push(m.text()));
  await page.addInitScript(() => {
    const prompts = []; window.__prompts = prompts; let consolidations = 0;
    const S = (what, owner, impact, fact, when = "決標前", rules) => ({ what, to: "丙廠", when, owner, impact, fact, ...(rules ? { rules } : {}) });
    const fn = async () => ({ text: "" });
    fn.json = async (p) => {
      prompts.push(p);
      await new Promise(r => setTimeout(r, 30));
      if (p.includes("只做「合併與排序」")) {
        consolidations++;
        if (consolidations > 1) throw { code: "upstream_error" };
        const ids = [...p.matchAll(/^(\w+-\d)｜/gm)].map(m => m[1]);
        const groups = [{ ids: ["aud-0", "jaud-0"], label: "丙廠個人帳戶收款", impact: "L1" }];
        ids.filter(i => !["aud-0", "jaud-0"].includes(i)).forEach(i => groups.push({ ids: [i], label: "單項 " + i, impact: "L2" }));
        return { groups };
      }
      if (p.includes("案件整理助理")) {
        return { title: "機房冰水主機擴充", item: "550RT × 2", budget: "NT$18,300,000", budget_ntd: 18300000, stage: "6 報價分析", evaluation: "CAPEX 20%／OPEX 80%",
          vendors: [{ name: "甲", role: "總代理", price: "NT$2,070 萬", price_ntd: 20700000, items: [{ k: "預算", v: "超出 13%", level: "caution" }, { k: "付款", v: "驗收後 100%", level: "normal" }] },
                    { name: "乙", role: "原廠分公司", price: "NT$1,978 萬", price_ntd: 19780000, items: [{ k: "幣別", v: "日圓", level: "caution" }] },
                    { name: "丙", role: "貿易商", price: "NT$1,650 萬", price_ntd: 16502500, items: [{ k: "往來", v: "首次・個人帳戶", level: "risk" }] }],
          tags: [{ tag: "首次交易", evidence: "5 廠商資料 第7列" }, { tag: "預付款", evidence: "6 交易與付款條件 第7列" }, { tag: "外幣計價", evidence: "2 報價明細 第11列" },
                 { tag: "進口", evidence: "" }, { tag: "不存在的標籤", evidence: "第1列" }], flags: ["丙收款帳戶為個人帳戶"] };
      }
      const who = (p.match(/你代表遠東集團「(.+?)」/) || [])[1];
      if (who === "稽核處") return { light: "紅", conclusion: "建議先確認丙廠資格", suggestions: [S("請丙廠改用公司帳戶收款", "採購現在行動", "L1", "丙廠個人帳戶收款", "決標前", ["S-01"]), S("請丙廠提供原廠授權書", "採購現在行動", "L2", "丙廠無原廠授權", "決標前", ["S-02"]), S("第三條應被截掉", "採購現在行動", "L1", "x")], evidence: "5 廠商資料 第7列", rules: ["S-01", "S-02"] };
      if (who === "聯稽") return { light: "紅", conclusion: "帳戶戶名不一致", suggestions: [S("依 U-15 確認丙廠收款帳戶戶名", "採購現在行動", "L1", "丙廠個人帳戶收款")], evidence: "5 廠商資料 第7列", rules: ["U-15"] };
      if (who === "財務處") return { light: "黃", conclusion: "乙日圓付款", suggestions: [S("乙下單時一併預購遠期日圓", "採購現在行動", "L2", "乙日圓計價", "議價中"), S("應被截掉一", "採購現在行動", "L2", "x"), S("應被截掉二", "採購現在行動", "L2", "x")], evidence: "2 報價明細", rules: ["F-02"] };
      if (who === "採購處") return { light: "黃", conclusion: "程序備忘", suggestions: [S("議價紀錄附上比價表", "採購現在行動", "L3", "比價紀錄")], evidence: "", rules: ["P-01"] };
      if (who === "國際事務處") return { light: "黃", conclusion: "乙 CIF 基隆", suggestions: [S("確認乙的稅則號列", "轉請其他部門處理", "L2", "乙 CIF 基隆")], evidence: "", rules: ["T-01"] };
      return { light: "綠", conclusion: "無意見", suggestions: [S("綠燈不應有建議", "採購現在行動", "L1", "x")], evidence: "", rules: [] };
    };
    window.claude = { use: async (n) => n === "sample" ? fn : n === "downloads" ? { save: async () => {} } : null };
  });
  await page.goto("file://" + file);
  const R = {};
  await page.click("#bSample");
  await page.click("#bExtract");
  await page.waitForSelector("#tagdet");
  R.tagsClosed = !(await page.$eval("#tagdet", e => e.open));
  R.tagSummary = (await page.textContent("#tagsum")).trim();
  R.tags = await page.evaluate(() => [...state.tags]);
  R.budgetRowDropped = await page.evaluate(() => !state.extracted.vendors[0].items.some(i => i.k === "預算"));
  R.budgetLine = await page.textContent("#summary .bline");
  await page.click("#bConsult");
  await page.waitForSelector("#report .layer1", { timeout: 20000 });
  R.need = await page.$$eval("#report .item.big .ihd b", els => els.map(e => e.textContent));
  R.needRules = await page.$$eval("#report .item.big .imeta", els => els.map(e => (e.textContent.match(/規則：([^｜]*)/) || [])[1]));
  R.fyiCount = await page.$$eval("details.fold .item:not(.big)", els => els.length);
  R.acctSugs = await page.evaluate(() => state.results.acct.suggestions.length);
  R.finSugs = await page.evaluate(() => state.results.fin.suggestions.length);
  R.audSugs = await page.evaluate(() => state.results.aud.suggestions.length);
  R.deptBoxClosed = !(await page.$eval("#deptBox", e => e.open));
  R.head = await page.textContent("#report .layer1 .big");
  R.firstBudget = await page.textContent("#report .layer1 .bline");
  R.timer = await page.textContent("#report .timer");
  R.preBudgetInPrompt = await page.evaluate(() => window.__prompts.filter(p => p.includes("你代表遠東集團")).every(p => p.includes("不要評論預算超支")));
  R.audSawOthers = await page.evaluate(() => window.__prompts.find(p => p.includes("你代表遠東集團「稽核處」")).includes("其他部門已回覆"));
  const visible = await page.evaluate(() => document.body.innerText);
  R.bannedVisible = ["禁止", "退回", "不得"].filter(w => visible.includes(w));
  const firstKey = await page.$eval("#report .item.big select", s => s.dataset.k);
  await page.selectOption(`select[data-k="${firstKey}"]`, "不適用");
  R.hintNoReason = await page.textContent("#decHint");
  R.csvHasCols = await page.evaluate(() => { const c = reportCsv(); return ["歸屬", "採購處處理狀態", "需你處理", "不適用"].every(w => c.includes(w)); });
  await page.screenshot({ path: path.resolve(__dirname, "../../out/live/live_done.png"), fullPage: true });
  // 第二次：彙整失敗 → 退回逐條版面
  await page.click("#bConsult");
  await page.waitForFunction(() => !state.running && state.history.length === 2, null, { timeout: 20000 });
  R.fallbackNote = await page.evaluate(() => state.consolidateNote);
  R.fallbackDeptOpen = await page.$eval("#deptBox", e => e.open);
  R.fallbackNeed = await page.$$eval("#report .item.big", els => els.length);
  R.historyRows = await page.$$eval("table.hist tbody tr", els => els.length);
  await page.click("#bReset"); await page.click("#bSample2");
  R.sample2 = await page.textContent(".file .nm");
  R.errors = errors;
  console.log(JSON.stringify(R, null, 1));
  await browser.close();
})();
