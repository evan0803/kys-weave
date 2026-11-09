// 實測版冒煙測試：以假的 claude.sample 跑完「範例檔 → 抽重點 → 六部門會診 → 會診單」
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
    const prompts = [];
    window.__prompts = prompts;
    const fn = async () => ({ text: "" });
    fn.json = async (p) => {
      prompts.push(p);
      await new Promise(r => setTimeout(r, 50));
      if (p.includes("案件整理助理")) {
        const hasData = p.includes("丙機電貿易") && p.includes("PR-SIM-2026-0158");
        return { title: hasData ? "機房冰水主機擴充" : "讀檔失敗", item: "550RT × 2", budget: "NT$18,300,000", stage: "6 報價分析",
          evaluation: "CAPEX 20%／OPEX 80%", vendors: [{ name: "丙機電貿易", price: "NT$16,502,500", currency: "新台幣", incoterm: "國內交貨", payment: "40% 預付", first_time: "是", origin: "中國大陸", note: "個人帳戶" }],
          tags: ["首次交易", "預付款", "外幣計價", "不存在的標籤"], flags: ["丙收款帳戶為個人帳戶"] };
      }
      const red = p.includes("「稽核處」");
      return { light: red ? "紅" : "綠", conclusion: red ? "丙廠資格不足" : "可行", suggestions: ["測試建議"], rules: ["X-01"] };
    };
    window.claude = { use: async (n) => n === "sample" ? fn : n === "downloads" ? { save: async () => {} } : null };
  });
  await page.goto("file://" + file);
  await page.click("#bSample");
  await page.click("#bExtract");
  await page.waitForSelector("#tagbox .tag.on");
  const onTags = await page.$$eval("#tagbox .tag.on", els => els.map(e => e.textContent));
  await page.click("#bConsult");
  await page.waitForFunction(() => document.querySelectorAll(".dots i.綠, .dots i.紅").length === 6, null, { timeout: 15000 });
  const verdict = await page.textContent(".verdict");
  const audSawOthers = await page.evaluate(() => window.__prompts.find(p => p.includes("「稽核處」")).includes("其他部門已回覆"));
  const sampleRead = await page.evaluate(() => window.__prompts[0].includes("丙機電貿易"));
  const csvOk = await page.isEnabled("#bCsv");
  await page.screenshot({ path: path.resolve(__dirname, "../../out/live/live_done.png"), fullPage: true });
  console.log(JSON.stringify({ onTags, verdict, audSawOthers, sampleRead, csvOk, errors }, null, 1));
  await browser.close();
})();
