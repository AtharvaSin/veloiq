#!/usr/bin/env node
/**
 * Export ARCHITECTURE_REPORT.html to PDF via Puppeteer.
 * Uses system Chrome via puppeteer-core from asr-visual-studio plugin.
 *
 * Usage: node export-pdf.cjs
 */
const path = require('path');
const fs = require('fs');

const PLUGIN = 'C:/Users/ASR/OneDrive/Desktop/AI Agents/AI Operating System/ai-os-project/ai-os-project/cowork-configuration/asr-visual-studio/asr-visual-studio';
const puppeteer = require(path.join(PLUGIN, 'node_modules', 'puppeteer-core'));

function findChrome() {
  const candidates = [
    process.env.CHROME_PATH,
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
    `${process.env.LOCALAPPDATA}\\Google\\Chrome\\Application\\chrome.exe`,
  ].filter(Boolean);
  for (const p of candidates) {
    if (fs.existsSync(p)) return p;
  }
  throw new Error('Chrome not found');
}

(async () => {
  const chrome = findChrome();
  console.log('Using Chrome at:', chrome);

  const browser = await puppeteer.launch({
    executablePath: chrome,
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  const page = await browser.newPage();
  const url = 'http://localhost:8765/ARCHITECTURE_REPORT.html';
  console.log('Loading:', url);
  await page.goto(url, { waitUntil: 'networkidle0', timeout: 30000 });

  const outPath = path.join(__dirname, 'ARCHITECTURE_REPORT.pdf');
  await page.pdf({
    path: outPath,
    format: 'A4',
    printBackground: true,  // CRITICAL: keeps dark theme
    margin: { top: '14mm', right: '14mm', bottom: '14mm', left: '14mm' },
    preferCSSPageSize: false,
  });

  const stats = fs.statSync(outPath);
  console.log(`PDF written: ${outPath} (${(stats.size / 1024 / 1024).toFixed(2)} MB)`);

  await browser.close();
})().catch((e) => {
  console.error('Error:', e.message);
  process.exit(1);
});
