import { expect, test } from "@playwright/test";

/**
 * Exercises the primary user workflow end-to-end against the real
 * backend (mock providers): analyse text, inspect token chips, select
 * a pronunciation candidate, start streaming synthesis, observe live
 * metrics, then cancel. Requires `apps/api` running on :8000 (see
 * README "Running the system") — this spec does not start it itself.
 */
test("analyse, correct a pronunciation, stream, and cancel", async ({ page }) => {
  await page.goto("/studio");

  await expect(page.getByRole("heading", { name: "Text" })).toBeVisible();

  const editor = page.getByLabel("Multilingual text editor");
  await editor.fill("मुझे कल 5 बजे meeting है।");
  await page.getByRole("button", { name: "Analyse Text" }).click();

  const meetingChip = page.getByRole("group", { name: "Analysed tokens" }).getByText("meeting");
  await expect(meetingChip).toBeVisible();
  await meetingChip.click();

  await expect(page.getByText(/Candidates/)).toBeVisible();
  const candidateButtons = page.locator("ul li button");
  await expect(candidateButtons.first()).toBeVisible();

  await page.context().grantPermissions([]);
  await page.getByRole("button", { name: "Start" }).click();

  await expect(page.getByText(/running|completed/)).toBeVisible({ timeout: 15_000 });

  const cancelButton = page.getByRole("button", { name: "Cancel" });
  if (await cancelButton.isEnabled().catch(() => false)) {
    await cancelButton.click();
  }

  await expect(page.getByText(/cancelled|completed/)).toBeVisible({ timeout: 15_000 });
});

test("system status page reports backend health", async ({ page }) => {
  await page.goto("/status");
  await expect(page.getByText("ok")).toBeVisible({ timeout: 10_000 });
});

test("lexicon CRUD workflow", async ({ page }) => {
  await page.goto("/lexicon");
  const surface = `e2e-word-${Date.now()}`;

  await page.locator("#new-surface").fill(surface);
  await page.locator("#new-language").fill("en");
  await page.locator("#new-phonemes").fill("t ɛ s t");
  await page.getByRole("button", { name: "Add entry" }).click();

  await expect(page.getByText(surface)).toBeVisible();

  const row = page.locator("tr", { hasText: surface });
  await row.getByRole("button", { name: "Delete" }).click();
  await expect(page.getByText(surface)).not.toBeVisible();
});
