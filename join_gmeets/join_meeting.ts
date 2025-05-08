/**
 * npm add playwright playwright-extra playwright-extra-plugin-stealth dotenv
 * npm add -D typescript ts-node @types/node
 * npx ts-node src/meet‑stealth.ts
 */

import "dotenv/config";
import { chromium } from "patchright";
import type { Browser, BrowserContext, Page, Locator } from "patchright";

const meetingUrl = process.env.GMEETS_URL ?? "";
const headlessTestUrl = "https://arh.antoinevastel.com/bots/areyouheadless";
const fingerprintTestUrl = "https://fingerprint-scan.com/";

(async () => {
  /* ---------- Launch browser ---------- */
  console.log("Starting Playwright…");
  const browser: Browser = await chromium.launch({
    headless: false, // set true if you must
    args: [
      "--no-sandbox",
      "--disable-gpu",
      "--disable-extensions",
      "--disable-dev-shm-usage",
    ],
  });

  /* ---------- Context & page ---------- */
  const context: BrowserContext = await browser.newContext({
    permissions: ["geolocation", "microphone", "camera"],
    viewport: { width: 1440, height: 900 },
    userAgent:
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
  });
  await context.grantPermissions(["geolocation", "microphone", "camera"], {
    origin: "https://meet.google.com",
  });

  const page: Page = await context.newPage();
  console.log("Stealth patches applied.\n");

  /* ---------- Headless‑detection test ---------- */
  try {
    console.log(`Navigating to ${headlessTestUrl}`);
    await page.goto(headlessTestUrl, { waitUntil: "domcontentloaded" });
    await page.waitForLoadState("networkidle", { timeout: 10_000 });

    const resultText =
      (await page.textContent("p.success", { timeout: 5_000 }))?.trim() ?? "";

    console.log(`Headless Test Result: "${resultText}"`);

    if (!resultText.toLowerCase().includes("you're not chrome headless")) {
      console.log("SUCCESS: Headless browser not detected.");
    } else {
      console.warn("WARNING: Headless browser detected!");
    }
  } catch (err) {
    console.error(`Headless test error: ${(err as Error).message}`);
  }

  /* ---------- Fingerprint‑scan test ---------- */
  try {
    console.log(`\nNavigating to ${fingerprintTestUrl}`);
    await page.goto(fingerprintTestUrl, { waitUntil: "domcontentloaded" });
    await page.waitForLoadState("networkidle", { timeout: 15_000 });

    const fingerprintId = (
      await page.textContent(
        "//div[contains(text(), 'Fingerprint ID')]/following-sibling::div/span",
        { timeout: 10_000 }
      )
    )?.trim();
    console.log(`Fingerprint ID: ${fingerprintId}`);

    const scoreText = (
      await page.textContent("//div[contains(@class,'score-value')]", {
        timeout: 10_000,
      })
    )?.trim();
    console.log(`Raw Score Text: ${scoreText}`);

    const score = scoreText
      ? parseInt(scoreText.split("/")[0].trim(), 10)
      : NaN;
    if (!Number.isNaN(score)) {
      console.log(`Bot Risk Score: ${score}`);
      if (score > 50) {
        console.warn(`WARNING: Score ${score} > 50 → likely bot.`);
      } else {
        console.log("SUCCESS: Score under threshold.");
      }
    }
  } catch (err) {
    console.error(`Fingerprint test error: ${(err as Error).message}`);
  }

  /* ---------- Google Meet Join Logic ---------- */
  if (meetingUrl) {
    try {
      console.log(`\nOpening Google Meet: ${meetingUrl}`);
      await page.goto(meetingUrl, { waitUntil: "domcontentloaded" }); // Added waitUntil

      console.log("Waiting for Google Meet page to load...");
      // Wait for a known element that appears after loading
      const joinButtonAreaLocator: Locator = page.locator(
        "xpath=//*[contains(text(),'Ask to join') or contains(text(),'Join now')]"
      );
      // Wait longer for the join button area, as page load can be slow
      await joinButtonAreaLocator.waitFor({ state: "visible", timeout: 20000 });
      console.log("Meet page appears loaded.");

      // Optionally: Enter a name if prompted (for guests)
      try {
        const nameInputLocator: Locator = page.locator(
          "xpath=//input[@type='text' and @aria-label='Your name']"
        );
        console.log("Checking for name input field...");
        // Check if visible before filling, as it might not always be present
        // Use a shorter timeout here as it's expected to appear quickly if needed
        if (await nameInputLocator.isVisible({ timeout: 5000 })) {
          await nameInputLocator.fill("Toni's executive assistant", {
            timeout: 5000,
          });
          console.log("Name entered.");
        } else {
          console.log("Name input field not found or not visible.");
        }
      } catch (error) {
        // Catching potential timeout errors if isVisible takes too long or other errors
        console.log(
          "Error checking/filling name input field (maybe not required):",
          error
        );
      }

      // Click "Ask to join" or "Join now"
      try {
        // Use Math.random() for a delay between 1 and 3 seconds
        const randomWaitMs = Math.random() * 2000 + 1000;
        console.log(
          `Waiting ${(randomWaitMs / 1000).toFixed(
            2
          )}s before clicking 'Ask to join'...`
        );
        await page.waitForTimeout(randomWaitMs);

        const joinButtonLocator: Locator = page.locator(
          "xpath=//span[contains(text(),'Ask to join') or contains(text(),'Join now')]/ancestor::button"
        );
        await joinButtonLocator.waitFor({ state: "visible", timeout: 15000 });

        await joinButtonLocator.click({ timeout: 5000 });
        console.log("Clicked 'Ask to join' or 'Join now'.");
      } catch (error) {
        console.error(
          "'Ask to join' / 'Join now' button interaction failed:",
          error
        );
      }

      // Ensure the mic is unmuted
      try {
        await page.waitForTimeout(2000); // Wait briefly for UI to settle after joining
        const micButtonLocator: Locator = page.locator(
          // More specific selector targeting the mic button
          "xpath=//button[@aria-label[contains(., 'microphone')]]"
        );
        await micButtonLocator.waitFor({ state: "visible", timeout: 10000 });

        const ariaLabel = await micButtonLocator.getAttribute("aria-label", {
          timeout: 5000,
        });

        // Check if the label indicates the mic is off (text might vary by language)
        if (
          ariaLabel &&
          (ariaLabel.includes("Turn on microphone") ||
            ariaLabel.includes("Activar micrófono"))
        ) {
          console.log("Microphone seems to be off. Attempting to turn it on.");
          await micButtonLocator.click({ timeout: 5000 });
          console.log("Clicked microphone button.");
        } else {
          console.log(
            `Microphone state: '${ariaLabel}' (already on or state unknown).`
          );
        }
      } catch (error) {
        console.error("Microphone toggle interaction failed:", error);
      }
    } catch (error) {
      console.error("Error during Google Meet join process:", error);
      // Consider adding more specific error handling or closing the browser here
    }
  } else {
    console.log("\nSkipping Google Meet join logic: GMEETS_URL not set.");
  }
  /* ---------- End Google Meet Join Logic ---------- */

  console.log("\nWaiting 60 s before closing…");
  await page.waitForTimeout(60_000);

  await browser.close();
  console.log("Script finished.");
})();
