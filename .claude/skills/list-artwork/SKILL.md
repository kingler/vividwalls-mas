---
name: list-artwork
description: Add a new artwork to the VividWalls Shopify catalog as a draft, with the standard size and format variants, pricing ladder, SEO, collection, and room-mockup images. Use when the owner has a new piece or series to sell.
---

# List a New Artwork

Inputs from the owner: artwork name, series, the high-res image (or a Shopify or Drive link),
orientation, and optionally an inspiration or story line.

## Steps
1. Check `business/catalog-and-pricing.md` for the current price ladder and naming rules.
2. Write the copy in the brand voice (`business/company.md`):
   - Title: `<Name>` (series naming: "Fractal Red no3", "Noir Mosaic no4"; lowercase "no")
   - Description: 120–180 words. Lead with the room or feeling, then colors and composition,
     then specs (materials, gallery-wrap depth, ready to hang, printed to order).
   - SEO title ≤60 chars: `<Name> — Abstract Canvas Wall Art | VividWalls`
   - Meta description 140–155 chars with a call to action.
   - Handle: kebab-case of the title.
3. Create room mockups with Higgsfield (living room above a sofa, office, bedroom) plus a scale
   shot. Get the owner's approval on the images.
4. Create the product as a **DRAFT** (`create-product`) with product type `Artwork`, vendor
   `VividWalls`, series tag, variants Size × Format at ladder prices, inventory **not tracked**.
5. Add it to the series collection (`add-to-collection`).
6. Remind the owner to upload the master file to Pictorem under the same handle.
7. Publish (set ACTIVE) only after the owner reviews the draft.
