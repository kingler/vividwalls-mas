# SEO Rewrites — Draft for Approval (2026-11-08)

Drafted with the `optimize-listing` playbook from live Shopify data pulled 2026-11-08
(37 active products, 255 images).

> **Status (2026-11-08):** sections 1 and 4 were approved and are **live**. See
> `2026-11-08-seo-applied.md`. Sections 2, 3 and 5 are still drafts awaiting approval.
Machine-readable version: `ops/reports/2026-11-08-seo-changes.json`.

## Summary
| Change | Products | Why |
|---|---|---|
| New SEO title (≤60 chars, name + keyword + brand) | 37 | 8 named the wrong artwork; 36 hard-coded one size ("24x36") |
| New meta description (135–158 chars) | 37 | 34 were 450–1,000 chars (Google shows ~155); 3 were empty |
| Product title cleanup | 6 | Consistent "no" numbering, one typo |
| URL handle fix + 301 redirect | 12 | Handle names a different or old artwork |
| Image alt text | 37 (255 images) | Every alt text is a filename, e.g. `[duplicate] [type:product] … — file_2183x2048.png` |
| Description fixes | 6 | Copy-pasted from another product, or names a collection that doesn't exist |

Title pattern: `<Name> — <color/style> <keyword> | VividWalls`. Each targets one of the
keyword themes in `optimize-listing` (geometric canvas art, black and white abstract art,
red/blue/green abstract wall art, large abstract wall art).

## 1. SEO titles and meta descriptions

### Crimson Shade
- **SEO title** — was: `Crimson Shade 24x36 Gallery Wrapped Canvas`
  - new (53): `Crimson Shade — Red Geometric Canvas Art | VividWalls`
- **Meta description** (was 944 chars) — new (145): Crimson Shade: bold crimson geometry with deep blue and purple accents. Large abstract canvas wall art, ready to hang. Shop sizes 24x36 to 53x72.

### Dark Kimono
- **SEO title** — was: `Dark Kimono 24x36 Gallery Wrapped Canvas`
  - new (52): `Dark Kimono — Geometric Canvas Wall Art | VividWalls`
- **Meta description** (was 958 chars) — new (147): Dark Kimono pairs Japanese kimono forms with dark geometric abstraction. Gallery-wrapped canvas wall art, ready to hang. Shop sizes 24x36 to 53x72.

### Deep Echoes
- **SEO title** — was: `Deep Echoes 53x72 Gallery Wrapped Canvas`
  - new (51): `Deep Echoes — Blue Abstract Canvas Art | VividWalls`
- **Meta description** (was 448 chars) — new (141): Deep Echoes layers deep blue facets like a cut gemstone. Large abstract canvas wall art for modern living rooms, ready to hang. Shop 3 sizes.

### Earthy Weave
- **SEO title** — was: `Earthy Weave 24x36 Gallery Wrapped Canvas`
  - new (54): `Earthy Weave — Earth-Tone Abstract Canvas | VividWalls`
- **Meta description** (was 626 chars) — new (143): Earthy Weave blends browns, forest greens and deep blues into woven geometry. Earth-tone abstract canvas wall art, ready to hang. Shop 3 sizes.

### Fractal Dark no1
- **SEO title** — was: `Fractal Color Dark Double 24x36 Gallery Wrapped Canvas`
  - new (55): `Fractal Dark no1 — Fractal Canvas Wall Art | VividWalls`
- **Meta description** (was 577 chars) — new (144): Fractal Dark no1: symmetric fractal art in blue, orange and red that spirals into depth. Statement canvas wall art, ready to hang. Shop 3 sizes.

### Fractal Dark no2
- **SEO title** — was: `Fractal Color Dark 24x36 Gallery Wrapped Canvas`
  - new (55): `Fractal Dark no2 — Fractal Canvas Wall Art | VividWalls`
- **Meta description** (was 533 chars) — new (140): Fractal Dark no2 sets electric blue, green and orange fractals on a dark ground. Bold abstract canvas wall art, ready to hang. Shop 3 sizes.

### Fractal Noir no1
- **SEO title** — was: `Fractal Noir Double 24x36 Gallery Wrapped Canvas`
  - new (56): `Fractal Noir no1 — Black & White Canvas Art | VividWalls`
- **Meta description** (was 935 chars) — new (145): Fractal Noir no1: crisp black and white fractal geometry. Modern monochrome canvas wall art for living rooms and offices. Ready to hang, 3 sizes.

### Fractal Noir no2
- **SEO title** — was: `Fractal Noir 24x36 Gallery Wrapped Canvas`
  - new (56): `Fractal Noir no2 — Black & White Canvas Art | VividWalls`
- **Meta description** (was 928 chars) — new (146): Fractal Noir no2: angular black and white abstraction with gallery-level contrast. Monochrome canvas wall art, ready to hang. Shop 24x36 to 53x72.

### Fractal Red no1
- **SEO title** — was: `Abstract Art, Wall Art, Ready-To-Hang, Collection Fractal Fractal Double Red 72x53, Black Frame Artwork`
  - new (59): `Fractal Red no1 — Red Abstract Canvas Wall Art | VividWalls`
- **Meta description** (was 930 chars) — new (143): Fractal Red no1 radiates deep red, orange and royal blue from a central burst. Large red abstract canvas wall art, ready to hang. Shop 3 sizes.

### Fractal Red no2
- **SEO title** — was: `Fractal Color Red 24x36 Gallery Wrapped Canvas`
  - new (59): `Fractal Red no2 — Red Abstract Canvas Wall Art | VividWalls`
- **Meta description** (was 936 chars) — new (144): Fractal Red no2: crimson fractal geometry with fiery depth. Statement red abstract canvas wall art for modern interiors. Ready to hang, 3 sizes.

### Intersecting Perspectives no3
- **SEO title** — was: `Intersecting Perspectives No3 24x36 Gallery Wrapped Canvas`
  - new (52): `Intersecting Perspectives no3 — Geometric Canvas Art`
- **Meta description** (was 785 chars) — new (143): Intersecting Perspectives no3: crossing lines and shifting planes in a modern geometric abstract. Canvas wall art, ready to hang. Shop 3 sizes.

### Intersecting Perspectives no1
- **SEO title** — was: `Intersecting Perspectives No1 24x36 Gallery Wrapped Canvas`
  - new (55): `Intersecting Perspectives no1 — Minimal Canvas Wall Art`
- **Meta description** (was 1001 chars) — new (146): Intersecting Perspectives no1: bold monochrome shapes and negative space. Minimalist abstract canvas wall art, ready to hang. Shop 24x36 to 53x72.

### Intersecting Perspectives no2
- **SEO title** — was: `Intersecting Perspectives No2 24x36 Gallery Wrapped Canvas`
  - new (52): `Intersecting Perspectives no2 — Geometric Canvas Art`
- **Meta description** (was 767 chars) — new (142): Intersecting Perspectives no2: dynamic intersecting forms that play with depth. Modern geometric canvas wall art, ready to hang. Shop 3 sizes.

### Intersecting Perspectives no4
- **SEO title** — was: `Intersecting Perspectives No3 24x36 Gallery Wrapped Canvas`
  - new (52): `Intersecting Perspectives no4 — Geometric Canvas Art`
- **Meta description** (was 785 chars) — new (142): Intersecting Perspectives no4: layered planes and crossing lines in a modern geometric abstract. Canvas wall art, ready to hang. Shop 3 sizes.

### Intersecting Perspectives no5
- **SEO title** — was: `Intersecting Perspectives No1 24x36 Gallery Wrapped Canvas`
  - new (55): `Intersecting Perspectives no5 — Minimal Canvas Wall Art`
- **Meta description** (was 1001 chars) — new (143): Intersecting Perspectives no5: minimal geometric abstraction with strong contrast and open space. Canvas wall art, ready to hang. Shop 3 sizes.

### Monochrome Kimono
- **SEO title** — was: `Monochrome Kimono 24x36 Gallery Wrapped Canvas`
  - new (57): `Monochrome Kimono — Black & White Canvas Art | VividWalls`
- **Meta description** (was 911 chars) — new (144): Monochrome Kimono turns kimono forms into crisp black and white geometry. Modern monochrome canvas wall art, ready to hang. Shop 24x36 to 53x72.

### Noir Echoes
- **SEO title** — was: `Noir Echoes 53x72 Gallery Wrapped Canvas`
  - new (51): `Noir Echoes — Black & White Canvas Art | VividWalls`
- **Meta description** (was 882 chars) — new (142): Noir Echoes: layered monochrome geometry from deep black to soft grey. Large black and white abstract canvas wall art, ready to hang. 3 sizes.

### Noir Mosaic no1
- **SEO title** — was: `Noir Mosaic no1 24x36 Gallery Wrapped Canvas`
  - new (55): `Noir Mosaic no1 — Black & White Canvas Art | VividWalls`
- **Meta description** (was 842 chars) — new (143): Noir Mosaic no1: interlocking monochrome tiles with quiet depth. Black and white geometric canvas wall art, ready to hang. Shop 24x36 to 53x72.

### Noir Mosaic no2
- **SEO title** — was: `Noir Mosaic no2 24x36 Gallery Wrapped Canvas`
  - new (55): `Noir Mosaic no2 — Black & White Canvas Art | VividWalls`
- **Meta description** (was 958 chars) — new (145): Noir Mosaic no2: triangles and rectangles in a crisp monochrome mosaic. Black and white canvas wall art for modern rooms. Ready to hang, 3 sizes.

### Noir Mosaic no3
- **SEO title** — was: `Noir Mosaic no3 24x36 Gallery Wrapped Canvas`
  - new (55): `Noir Mosaic no3 — Black & White Canvas Art | VividWalls`
- **Meta description** (was 836 chars) — new (142): Noir Mosaic no3: overlapping translucent forms in black, white and grey. Modern geometric canvas wall art, ready to hang. Shop 24x36 to 53x72.

### Noir Shade
- **SEO title** — was: `Noir Shade 24x36 Gallery Wrapped Canvas`
  - new (50): `Noir Shade — Dark Abstract Canvas Art | VividWalls`
- **Meta description** (was 891 chars) — new (141): Noir Shade: deep tonal shifts and bold geometric forms. Dark abstract canvas wall art printed on museum-grade canvas, ready to hang. 3 sizes.

### Noir Weave
- **SEO title** — was: `Noir Weave 24x36 Gallery Wrapped Canvas`
  - new (50): `Noir Weave — Grey Abstract Canvas Art | VividWalls`
- **Meta description** (was 824 chars) — new (139): Noir Weave: woven greyscale geometry with rich texture. Modern grey and black abstract canvas wall art, ready to hang. Shop 24x36 to 53x72.

### Olive Weave
- **SEO title** — was: `Olive Weave 24x36 Gallery Wrapped Canvas`
  - new (52): `Olive Weave — Green Abstract Canvas Art | VividWalls`
- **Meta description** (was 892 chars) — new (141): Olive Weave layers translucent olive and green planes into calm geometry. Green abstract canvas wall art, ready to hang. Shop 24x36 to 53x72.

### Parallelogram Illusion no1
- **SEO title** — was: `Parallelogram Illusion no1 24x36 Gallery Wrapped Canvas`
  - new (49): `Parallelogram Illusion no1 — Geometric Canvas Art`
- **Meta description** (was 896 chars) — new (145): Parallelogram Illusion no1: transparent parallelograms that play tricks on depth. Optical geometric canvas wall art, ready to hang. Shop 3 sizes.

### Parallelogram Illusion no2
- **SEO title** — was: `Structured Emerald No3 24x36 Gallery Wrapped Canvas`
  - new (55): `Parallelogram Illusion no2 — Green Geometric Canvas Art`
- **Meta description** (was 858 chars) — new (146): Parallelogram Illusion no2: lime to forest-green planes cut with crisp white. Green geometric canvas wall art, ready to hang. Shop 24x36 to 53x72.

### Parallelogram Illusion no3
- **SEO title** — was: `Prismatic Warmth 24x36 Gallery Wrapped Canvas`
  - new (54): `Parallelogram Illusion no3 — Warm Geometric Canvas Art`
- **Meta description** (was 968 chars) — new (146): Parallelogram Illusion no3: warm overlapping planes with a textile feel. Warm-toned geometric canvas wall art, ready to hang. Shop 24x36 to 53x72.

### Parallelogram Illusion no4
- **SEO title** — was: `Structured Noir no1 24x36 Gallery Wrapped Canvas`
  - new (53): `Parallelogram Illusion no4 — Black & White Canvas Art`
- **Meta description** (was 921 chars) — new (144): Parallelogram Illusion no4: minimalist monochrome planes with Constructivist edge. Black and white canvas wall art, ready to hang. Shop 3 sizes.

### Red Kimono
- **SEO title** — was: `Red Kimono 24x36 Gallery Wrapped Canvas`
  - new (50): `Red Kimono — Red Geometric Canvas Art | VividWalls`
- **Meta description** (was 764 chars) — new (142): Red Kimono: flowing kimono forms rebuilt as bold red geometry. Red abstract canvas wall art for modern interiors, ready to hang. Shop 3 sizes.

### Royal Kimono
- **SEO title** — was: `Royal Kimono 24x36 Gallery Wrapped Canvas`
  - new (53): `Royal Kimono — Blue Geometric Canvas Art | VividWalls`
- **Meta description** (was 646 chars) — new (138): Royal Kimono: royal blue parallelograms with vivid pink accents. Blue geometric canvas wall art, ready to hang. Shop sizes 24x36 to 53x72.

### Royal Shade
- **SEO title** — was: `Textured Royal no1 24x36 Gallery Wrapped Canvas`
  - new (51): `Royal Shade — Blue Abstract Canvas Art | VividWalls`
- **Meta description** (was 928 chars) — new (146): Royal Shade: regal blue fractal geometry with a textured look. Blue abstract canvas wall art for living rooms and offices. Ready to hang, 3 sizes.

### Space & Form no1
- **SEO title** — was: `Space & Form no1 24x36 Gallery Wrapped Canvas`
  - new (56): `Space & Form no1 — Textured Canvas Wall Art | VividWalls`
- **Meta description** (was 0 chars) — new (139): Space & Form no1: earthy textured forms with raw, natural energy. Large abstract canvas wall art, ready to hang. Shop sizes 24x36 to 53x72.

### Space & Form no2
- **SEO title** — was: `Space & Form no2 24x36 Gallery Wrapped Canvas`
  - new (55): `Space & Form no2 — Minimal Canvas Wall Art | VividWalls`
- **Meta description** (was 0 chars) — new (141): Space & Form no2: bold minimal shapes balanced against open space. Modern abstract canvas wall art, ready to hang. Shop sizes 24x36 to 53x72.

### Space & Form no4
- **SEO title** — was: `Space & Form no4 53x72 Gallery Wrapped Canvas`
  - new (52): `Space & Form no4 — Geometric Canvas Art | VividWalls`
- **Meta description** (was 0 chars) — new (139): Space & Form no4: geometric shapes that define and divide space. Large architectural abstract canvas wall art, ready to hang. Shop 3 sizes.

### Vista Echoes
- **SEO title** — was: `Vista Echoes 24x36 Gallery Wrapped Canvas`
  - new (52): `Vista Echoes — Blue Abstract Canvas Art | VividWalls`
- **Meta description** (was 462 chars) — new (139): Vista Echoes: deep blues and purples that open like a twilight panorama. Blue abstract canvas wall art, ready to hang. Shop 24x36 to 53x72.

### Vivid Mosaic no1
- **SEO title** — was: `Vivid Mosaic no1 24x36 Gallery Wrapped Canvas`
  - new (56): `Vivid Mosaic no1 — Colorful Canvas Wall Art | VividWalls`
- **Meta description** (was 877 chars) — new (143): Vivid Mosaic no1: translucent polygons in a vivid color mosaic. Colorful geometric canvas wall art that lifts any room. Ready to hang, 3 sizes.

### Vivid Mosaic no2
- **SEO title** — was: `Vivid Mosaic no2 24x36 Gallery Wrapped Canvas`
  - new (56): `Vivid Mosaic no2 — Colorful Canvas Wall Art | VividWalls`
- **Meta description** (was 977 chars) — new (139): Vivid Mosaic no2: luminous overlapping color forms in a bold mosaic. Colorful abstract canvas wall art, ready to hang. Shop 24x36 to 53x72.

### Vivid Mosaic no4
- **SEO title** — was: `Vivid Mosaic no5 24x36 Gallery Wrapped Canvas`
  - new (56): `Vivid Mosaic no4 — Colorful Canvas Wall Art | VividWalls`
- **Meta description** (was 916 chars) — new (142): Vivid Mosaic no4: a vivid, harmonious mosaic of geometric color. Statement abstract canvas wall art, ready to hang. Shop sizes 24x36 to 53x72.

## 2. Product title cleanup
| Current | Proposed |
|---|---|
| Intersecting Perspective No3 | Intersecting Perspectives no3 |
| Intersecting Perspectives No1 | Intersecting Perspectives no1 |
| Intersecting Perspectives No2 | Intersecting Perspectives no2 |
| Intersecting Perspectives No4 | Intersecting Perspectives no4 |
| Intersecting Perspectives No5 | Intersecting Perspectives no5 |
| Space Form no4 | Space & Form no4 |

## 3. URL handle fixes
Shopify creates a 301 redirect from the old URL when the handle is changed with *Create a URL redirect* ticked, so existing links and search rankings carry over.

| Product | Current handle | Proposed handle |
|---|---|---|
| Fractal Dark no1 | `fractal-color-dark-double` | `fractal-dark-no1` |
| Fractal Dark no2 | `fractal-color-dark` | `fractal-dark-no2` |
| Fractal Noir no1 | `fractal-noir-double` | `fractal-noir-no1` |
| Fractal Noir no2 | `fractal-noir` | `fractal-noir-no2` |
| Fractal Red no1 | `fractal-double-red` | `fractal-red-no1` |
| Fractal Red no2 | `fractal-color-red` | `fractal-red-no2` |
| Intersecting Perspectives no1 | `untiled-n011` | `intersecting-perspectives-no1` |
| Parallelogram Illusion no2 | `verdant-layers` | `parallelogram-illusion-no2` |
| Parallelogram Illusion no3 | `prismatic-warmth` | `parallelogram-illusion-no3` |
| Parallelogram Illusion no4 | `structured-noir-no1` | `parallelogram-illusion-no4` |
| Royal Shade | `textured-royal-no1` | `royal-shade` |
| Vivid Mosaic no4 | `vivid-mosaic-no5` | `vivid-mosaic-no4` |

## 4. Image alt text (all 255 images)
Replace every alt text using this pattern, based on what the image shows:

| Image type | Alt text pattern | Example |
|---|---|---|
| Flat artwork | `<Name> abstract canvas wall art by VividWalls` | Crimson Shade abstract canvas wall art by VividWalls |
| Room scene | `<Name> canvas wall art in a <room>` | Crimson Shade canvas wall art in a modern living room |
| Detail / edge | `<Name> gallery-wrapped canvas edge detail` | Crimson Shade gallery-wrapped canvas edge detail |
| Size guide | `<Name> shown at <size> above a sofa` | Crimson Shade shown at 36x48 above a sofa |

The current filenames already say which image is a room scene (`[scene:living-room]`)
and which is a flat shot (`[type:product]`), so the type can be read from them. Some
filenames are marked `[duplicate]`. Those images are worth deleting rather than relabelling.

## 5. Description fixes (copy, not SEO fields)
| Product | Problem | Fix |
|---|---|---|
| Intersecting Perspectives no4 | Description is No3's text (starts "Intersecting Perspectives No3…") | Write a new description for No4 |
| Intersecting Perspectives no5 | Description is No1's text | Write a new description for No5 |
| Space & Form no2 | Same text as Intersecting Perspectives No1 | Write a new description |
| Intersecting Perspectives no1, Space & Form no1/no2/no4 | Name a "Resonating Structure" collection that doesn't exist | Change to the real series |
| Parallelogram Illusion no1/no3/no4, Red Kimono | Say "Geometric Intersect collection" (wrong series) | Change to Parallelogram / Kimono series |
| Royal Shade | Broken sentence: "Royal Shade no1 from presents…" | Rewrite the opening line |

New descriptions follow `list-artwork`: 120–180 words, opening with the room or feeling,
then colors and composition, then specs. Claude drafts these once sections 1–4 are approved.

## Open decision
Descriptions repeatedly say "limited edition", but inventory is tracked at 273–450 per piece.
Until editions are decided (see `business/catalog-and-pricing.md`), the new meta descriptions
avoid the phrase.
