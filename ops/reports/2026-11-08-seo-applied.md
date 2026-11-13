# SEO Changes — Applied 2026-11-08

The owner approved sections 1 and 4 of `2026-11-08-seo-changes.md`, then sections 2 and 3, then section 5
(applied 2026-11-08 to 2026-11-13). All five were applied through the Shopify Admin API. Every batch returned 0 errors, and a
read-back confirmed the new values.

| Section | Applied | Result |
|---|---|---|
| 1. SEO titles and meta descriptions | 37 / 37 products | Live |
| 4. Image alt text | 255 / 255 images | Live. No filename-style alt text remains |
| 2. Product title cleanup | 6 products, plus the alt text on their 42 images | Live |
| 3. URL handle fixes | 12 products | Live. Each old URL 301-redirects to the new one |
| 5. Description fixes | 13 products | Live. See "Section 5: what changed" below |

**Rollback:** `2026-11-08-seo-backup-before-apply.json` holds each product's previous SEO
title, description and image alt text, captured just before the change.
`2026-11-08-seo-backup-before-sections-2-3.json` holds the previous titles, handles and alt
text for the 17 products changed by sections 2 and 3. To undo a handle change, set the old
handle back and delete the matching redirect under Online Store → Navigation → URL redirects.
`2026-11-08-seo-backup-before-section-5.json` holds the full previous description HTML of the
13 products changed by section 5.

## Notes from applying
- Section 4 alt text first used the titles as they were. Section 2 then renamed six
  products ("Intersecting Perspective No3" became "Intersecting Perspectives no3", "Space
  Form no4" became "Space & Form no4", and four casing fixes), and their 42 images' alt text
  was updated in the same batch.
- One image (`MediaImage/43937235796255`, filename `vivid_mosaic_no5…`) is attached to
  both **Vivid Mosaic no2** and **Vivid Mosaic no4**. The filename shows it is the no4
  artwork, so it is labeled as no4. It should be removed from Vivid Mosaic no2, which shows
  the wrong piece. The owner approved it, and it has been removed from Vivid Mosaic no2.
- 75 images are tagged `[duplicate]` in their old filenames. They are relabelled, not
  deleted. Deleting them is a separate decision.

## Sections 2 and 3: what changed

| Product | Old handle → new handle | Title change |
|---|---|---|
| Fractal Dark no1 | `fractal-color-dark-double` → `fractal-dark-no1` | — |
| Fractal Dark no2 | `fractal-color-dark` → `fractal-dark-no2` | — |
| Fractal Noir no1 | `fractal-noir-double` → `fractal-noir-no1` | — |
| Fractal Noir no2 | `fractal-noir` → `fractal-noir-no2` | — |
| Fractal Red no1 | `fractal-double-red` → `fractal-red-no1` | — |
| Fractal Red no2 | `fractal-color-red` → `fractal-red-no2` | — |
| Intersecting Perspectives no1 | `untiled-n011` → `intersecting-perspectives-no1` | from "No1" |
| Intersecting Perspectives no2 | unchanged | from "No2" |
| Intersecting Perspectives no3 | unchanged | from "Intersecting Perspective No3" |
| Intersecting Perspectives no4 | unchanged | from "No4" |
| Intersecting Perspectives no5 | unchanged | from "No5" |
| Parallelogram Illusion no2 | `verdant-layers` → `parallelogram-illusion-no2` | — |
| Parallelogram Illusion no3 | `prismatic-warmth` → `parallelogram-illusion-no3` | — |
| Parallelogram Illusion no4 | `structured-noir-no1` → `parallelogram-illusion-no4` | — |
| Royal Shade | `textured-royal-no1` → `royal-shade` | — |
| Space & Form no4 | unchanged | from "Space Form no4" |
| Vivid Mosaic no4 | `vivid-mosaic-no5` → `vivid-mosaic-no4` | — |

**Follow-up:** links that use the old handles still work through the redirects. Pinterest
pins, Meta ads, blog posts and Pictorem file names should move to the new handles when they
are next edited.

## Section 5: what changed

Only the opening paragraph of each description changed. The specs table and the artist
footer were kept, including the "limited edition" wording, which stays until editions are
decided (see the open decision in `2026-11-08-seo-changes.md`).

| Product | Change |
|---|---|
| Intersecting Perspectives no1 | New opening paragraph, written from the artwork (olive green, magenta, cobalt). The old text described a black-and-white piece |
| Intersecting Perspectives no4 | New opening paragraph (it carried no3's text) |
| Intersecting Perspectives no5 | New opening paragraph (it carried no1's text) |
| Intersecting Perspectives no2, no3 | "Geometric Intersect collection" → "Intersecting Perspectives series"; "No2"/"No3" → "no2"/"no3" |
| Space & Form no1, no2, no4 | "Resonating Structure collection" → "Space & Form series"; names use lowercase "no" |
| Parallelogram Illusion no1, no3, no4 | "Geometric Intersect collection" → "Parallelogram series" |
| Red Kimono | "Geometric Intersect collection" → "Kimono series" |
| Royal Shade | Broken opener "Royal Shade no1 from presents" → "Royal Shade, from the Emergence series, presents" |

Notes:
- The draft said Space & Form no2 copied Intersecting Perspectives no1. Looking at the
  artwork showed it was the other way round: the shared monochrome text fits Space & Form no2
  (a black-and-white piece), so Space & Form no2 kept it and Intersecting Perspectives no1 got
  new copy.
- Intersecting Perspectives no2 and no3 were not listed in the draft but had the same wrong
  collection name, so they were fixed in the same pass.
- Side effect: on these 13 products, the specs table's size line now shows "24×36". The other
  24 products still show the literal text `24\u00d736`, a leftover encoding bug in the old
  import.
