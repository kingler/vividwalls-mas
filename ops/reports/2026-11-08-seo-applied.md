# SEO Changes — Applied 2026-11-08

The owner approved sections 1 and 4 of `2026-11-08-seo-changes.md`. Both were applied through
the Shopify Admin API in 4 batches. Every batch returned 0 errors, and a read-back confirmed
the new values.

| Section | Applied | Result |
|---|---|---|
| 1. SEO titles and meta descriptions | 37 / 37 products | Live |
| 4. Image alt text | 255 / 255 images | Live. No filename-style alt text remains |
| 2. Product title cleanup | Not approved yet | Not applied |
| 3. URL handle fixes | Not approved yet | Not applied |

**Rollback:** `2026-11-08-seo-backup-before-apply.json` holds each product's previous SEO
title, description and image alt text, captured just before the change.

## Notes from applying
- Alt text uses each product's **current** title, because section 2 is not approved. Two
  products still use their old names in alt text: "Intersecting Perspective No3"
  (singular) and "Space Form no4". These update when section 2 is applied.
- One image (`MediaImage/43937235796255`, filename `vivid_mosaic_no5…`) is attached to
  both **Vivid Mosaic no2** and **Vivid Mosaic no4**. The filename shows it is the no4
  artwork, so it is labeled as no4. It should be removed from Vivid Mosaic no2, which shows
  the wrong piece. This needs the owner's approval.
- 75 images are tagged `[duplicate]` in their old filenames. They are relabelled, not
  deleted. Deleting them is a separate decision.
