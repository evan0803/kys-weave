// 離線版冒煙測試：斷網開啟，三個案例各跑一次一鍵會診，印出燈號統計與結論
const { chromium } = require("playwright");
const path = require("path");
(async () => {
  const file = path.resolve(__dirname, "../../out/offline/遠東經緯島_離線版.html");
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 1500, height: 900 } });
  await ctx.setOffline(true);
  const page = await ctx.newPage();
  const errors = [];
  page.on("pageerror", e => errors.push(e.message));
  page.on("console", m => m.type() === "error" && errors.push(m.text()));
  await page.goto("file://" + file);
  await page.waitForSelector("#scene canvas");
  await page.click("#bAuto");
  const out = {};
  for (const k of ["A", "B", "C"]) {
    await page.click(`.cases button[data-k="${k}"]`);
    await page.click("#aRun");
    await page.waitForSelector("#mRes .verdict", { timeout: 20000 });
    out[k] = { tally: await page.$$eval("#mRes .tally .lt", els => els.map(e => e.textContent).join(" ")), verdict: await page.textContent("#mRes .verdict") };
    if (k === "B") await page.screenshot({ path: path.resolve(__dirname, "../../out/offline/offline_B.png") });
  }
  const legend = await page.$$eval("#auto .legend span", els => els.map(e => e.textContent).filter(Boolean).join("｜"));
  console.log(JSON.stringify({ out, legend, errors }, null, 1));
  await browser.close();
})();
