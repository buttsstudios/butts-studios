# BUTTS STUDIOS — APPAREL & WEBSITE DEVELOPER HANDOFF
**Status:** Concept and direction handoff, not production-approved designs.  
**Primary tagline:** **Made of Story.**  
**Critical instruction:** Later AI renderings introduced errors and DO NOT override explicit client feedback.

## 1. Project objective
Create a premium Butts Studios apparel and accessories collection and a visually rich e-commerce website. Butts Studios is a multidisciplinary creative/production studio making books, comics, channels, cartoons, art and related original work, founded in 2018. Apparel is an extension of the studio's artistic identity, NOT an outdoor equipment brand or generic merch store. The intended mood is refined, artful, cultured, distinctive, wearable, and premium. Mountain and nature photography may provide atmosphere but must not define the customer as a hiker or wilderness gear buyer.

## 2. FINAL PRODUCT SCOPE — explicit priority
| Product | Decision | Instructions |
|---|---|---|
| Rust/orange hoodie | **KEEP** | User explicitly corrected an omission: KEEP the rust-orange hoodie, with contour-line back graphic. |
| Black hoodie | **KEEP** | Back contour illustration, restrained studio logo/typography. |
| Olive/black technical windbreaker | **KEEP** | Olive/black blocking, refined utility detailing; not overly rugged. |
| Dark plaid flannel | **KEEP** | **NO LOGO ON FRONT.** Dark understated plaid. Small inside neck label is acceptable. |
| Black knit beanie | **KEEP — IMPORTANT** | User explicitly objected to its disappearance from later concepts. Include it in product grid, category navigation and website imagery. |
| Multipurpose premium bag | **REWORK, NOT APPROVED** | One refined personal/work/travel bag concept; premium and versatile, useful for studio, commuting and travel. Avoid outdoorsy duffel styling, tactical straps, camping hardware. Prior tote and backpack are NOT approved. Do not assume the last render's bag is final. |
| Baseball/ball cap | **REMOVE** | User explicitly requested removal. |
| Tote bag | **REMOVE** | User explicitly rejected the tote; do not include even though it appeared in later images. |
| Previous flap backpack | **REJECT** | Did not fit the audience or design direction. No reuse as final product. |
| Orange printed button-up shirt | **REMOVE** | This is different from the approved orange hoodie. |

**Hierarchy:** User's written corrections > earlier liked concepts > generated images. In particular: the beanie must be restored, and the tote must not survive into the final build.

## 3. BRAND IDENTITY
- Name: Butts Studios.
- Tagline: **Made of Story.** (singular Story, with period).
- Preserve the **original bold sans-serif / clean letter-spaced tagline direction** from the initial 'Made of Story' lookbook and related early renderings. The user explicitly rejected the later switch to a delicate serif headline. Do not use “A studio for the long game,” “A studio for what's next,” or other invented studio taglines as hero copy.
- Brand mark: square containing an X-like geometric construction, paired with stacked “Butts Studios.” Match the provided source website screenshots, not arbitrary redraws. Obtain vector originals from owner before production; renderings are not authoritative artwork.
- Palette: black, charcoal, cream, muted olive, rust-orange, subtle warm accent. Keep high contrast, textured fabrics, cinematic lighting. Orange belongs as a hoodie color and small accents, not as a printed button-up shirt.
- Graphic language: topographic/contour artwork, tactile fabric close-ups, discreet labels, intentional typography. Do not imply the topo art is a geographic map of a specific real place.

## 4. AUDIENCE & POSITIONING
The customer is creative, culturally engaged and design-conscious, interested in art and storytelling even if not a professional artist. Products should feel suitable for a creative professional, gallery visitor, traveler, designer, reader or studio collaborator. Prior concepts were too outdoorsy. The brand can use atmospheric landscapes but should also feel at home in a city, studio, gallery, café, or airport. Avoid generic hiking/camping retail conventions.

## 5. WEBSITE DIRECTION
Build a complete responsive website with multiple page/section experiences, NOT just a single collage. The user specifically requested MORE renderings of site areas. Suggested architecture:
1. Homepage: original Butts Studios logo; hero with **MADE OF STORY.** in the original clean typography; cinematic editorial photograph; understated collection link.
2. Collection page: all approved products, including the **beanie** and **orange hoodie**. No cap, no tote, no rejected backpack. Show accurate front/back views and variants.
3. Product detail pages: large front/back images, fabric and trim details, sizing, variant selection, add to bag, care and shipping details. Do not invent confirmed specifications or prices.
4. Editorial/story page: creative-studio identity, art/storytelling, visual inspiration and process. Show some studio/gallery/urban contexts alongside landscape imagery.
5. Craft/materials page: close-ups of knit, flannel, technical fabric, embroidery, zippers and bag materials; claims about waterproofing/material composition require verification.
6. Accessories page: black beanie and **one new premium multipurpose bag direction** only; bag not yet approved.
7. Cart and checkout states: standard usable e-commerce behavior; actual platform, payment and inventory systems TBD.
8. Mobile designs: homepage, collection, product detail, menu and cart.

**Presentation:** Avoid a cookie-cutter outdoor retailer and avoid excessive tiny tiles. Use strong art direction, editorial whitespace, a few large immersive panels, and practical shopping interfaces. Homepage should communicate the studio identity first, then lead naturally into the collection.

## 6. IMAGE-BY-IMAGE COMMENTARY AND APPROVAL STATUS
All images are *concept references*, not source assets ready for production. Generated typography and logos may contain inconsistencies.

### 01_initial_lookbook.png — EARLY REFERENCE, PARTIALLY APPROVED
Strong visual mood, garment silhouettes, contour graphic, black/olive palette, beanie and windbreaker. **Reject** “A studio for the long game” headline and the rust/orange button-up shirt. Keep rust hoodie direction.

### 02_made_of_story_first_pass.png — COPY REFERENCE, PARTIALLY APPROVED
Introduces **Made of Story.** Use its tagline concept, orange hoodie and established product family. **Reject** alternate “A studio for what's next” hero copy and baseball cap.

### 03_refined_beanie_flannel.png — IMPORTANT PRODUCT REFERENCE
Good beanie, logo treatment, unbranded-front dark flannel, technical jacket and hoodie. Earlier outdoorsy duffel is **not approved**. Keep original Made of Story typography direction.

### 04_site_concept_with_rejected_cap.png — LAYOUT REFERENCE ONLY
Demonstrates editorial homepage, product strip, atmospheric panels and close-up modules. **Reject** baseball cap, outdoorsy bag and “Built for what's next” copy. Keep orange hoodie and black beanie in future grids.

### 05_site_concept_with_rejected_tote_backpack.png — LAYOUT REFERENCE ONLY
Useful modular site composition and product imagery. **Reject BOTH tote and backpack**, and reject the unrequested serif change to “Made of Story.” The beanie is a keeper.

### 06_latest_site_concept_NOT_APPROVED.png — LATEST BUT NOT APPROVED
Provides examples of expanded site sections, material closeups and editorial modules. **Explicitly WRONG** to remove the beanie while retaining a tote-like bag; the user called this out. Do not copy its product assortment or typography. It is included solely to show potential site areas and mistakes to avoid.

### Original website screenshots
These show Butts Studios' original geometric logo, stacked wordmark, bold typography, black/cream visual system and broader creative-studio positioning. Use them for brand continuity. One screenshot shows a portfolio/case study, which is background context, not apparel artwork.

## 7. DEVELOPER IMPLEMENTATION NOTES
- Deliver a working responsive storefront with navigation, collection filters if needed, product pages, cart and accessible controls.
- Store product data centrally and avoid hardcoding rejected SKUs into templates.
- Create a real image asset library: product cutouts/front/back, lifestyle, detail crops, editorial hero, mobile crops. AI collages are moodboards, not separately exportable product photography or proof of materials.
- Acquire authentic logo SVG, approved font files/licenses, actual manufacturing details, sizing, pricing, inventory and fulfillment before launch.
- Any proposed premium bag should be separately reviewed before inclusion as a purchasable item.
- Use consistent logo scale, color values and tagline typography across all pages.
- Do not add unapproved slogans, product categories, specifications, prices, performance claims or materials as facts.

## 8. ACCEPTANCE CHECKLIST
- [ ] Homepage uses **Made of Story.**, no “A studio for...” copy.
- [ ] Original clean tagline typography, NOT the later serif treatment.
- [ ] Orange/rust hoodie present.
- [ ] Black hoodie present.
- [ ] Olive/black windbreaker present.
- [ ] Dark flannel has **no front logo**.
- [ ] Black knit **beanie present** on collection/accessories pages.
- [ ] **NO baseball cap**.
- [ ] **NO tote bag**.
- [ ] **NO old backpack**.
- [ ] **NO orange printed button-up shirt**.
- [ ] Premium multipurpose bag treated as unresolved design needing approval.
- [ ] Multiple real website page/section designs and mobile views.
- [ ] Studio/art audience prioritized over outdoors/hiking positioning.
- [ ] Logo sourced faithfully from original references.

## 9. OUTSTANDING DECISIONS
Final bag silhouette/materials; garment manufacturing and specifications; retail prices; e-commerce platform; photography and model direction; final approved artwork files; legal/returns/shipping details. None should be fabricated from AI renderings.
