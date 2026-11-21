# What makes a small local business website work

A one-page site for a bakery, garage, salon or plumber has one job: turn a visitor into a call, a visit or a quote request. These findings come from Google, W3C, Nielsen Norman Group and BrightLocal pages read on 2026-11-21, and each one maps to a field or feature in this generator.

## Get found

1. **Keep name, address and phone the same everywhere, and match the Google Business Profile.**
   Google says businesses "with complete and accurate info are more likely to show up in local search results", and its profile rules ask for the real-world name, a precise address or service area, and a local phone number the business controls.
   Sources: [Google Business Profile, local ranking](https://support.google.com/business/answer/7091), [Business Profile guidelines](https://support.google.com/business/answer/3038177).
   In this generator: `name`, `address`, `phone` fill the page, footer and JSON-LD from one place, so they cannot drift apart.

2. **Know the three things Google uses to rank local results: relevance, distance and prominence.**
   Google says prominence depends partly on how many sites link to the business and how many reviews it has, and that there is no way to pay for a better local ranking.
   Source: [Google Business Profile, local ranking](https://support.google.com/business/answer/7091).
   In this generator: the title, H1 and `services` cover relevance; `address`, `map` and `service_area` cover distance; `testimonials` and links to the real review profile support prominence.

3. **Put the service type and the town in the page title, said once, with the business name.**
   Google asks for titles that are descriptive, concise and unique, with the brand at the start or end behind a delimiter such as a pipe, and warns that repeated keywords look spammy.
   Source: [Google Search Central, title links](https://developers.google.com/search/docs/appearance/title-link).
   In this generator: built in, the title is `<Business> | <type> in <town>, <region>`.

4. **Write a meta description that states practical facts like hours and location.**
   Google's own shop example reads "Open Monday-Friday 8-5pm, located in the Fashion District", and it says keyword lists do not help.
   Source: [Google Search Central, snippets and meta descriptions](https://developers.google.com/search/docs/appearance/snippet).
   In this generator: `description` (falls back to a line built from the tagline); write hours and town into it.

5. **Add LocalBusiness structured data with address, phone, geo and opening hours.**
   Google lists `name` and `address` as required, and `geo` (at least 5 decimal places), `openingHoursSpecification`, `telephone` with country and area code, `url` and `priceRange` (under 100 characters) as recommended.
   Source: [Google Search Central, LocalBusiness structured data](https://developers.google.com/search/docs/appearance/structured-data/local-business).
   In this generator: LocalBusiness JSON-LD is built in from `name`, `address`, `phone`, `hours`, `price_range` and `url` (there is no `geo` field yet, a possible addition).

6. **For businesses that travel to customers, name the towns they serve.**
   Schema.org defines `areaServed` as "the geographic area where a service or offered item is provided" and lists it on Organization (LocalBusiness is a subtype); Google's LocalBusiness page does not list it, so treat it as a clarity signal, not a ranking switch. Google's profile rules say service-area businesses should hide their address and set a service area instead.
   Sources: [schema.org areaServed](https://schema.org/areaServed), [Business Profile guidelines](https://support.google.com/business/answer/3038177).
   In this generator: `service_area` shows on the page and becomes JSON-LD `areaServed`.

7. **Set a canonical URL; a sitemap and robots.txt are cheap extras.**
   Google calls `rel="canonical"` "a strong signal" and sitemap inclusion "a weak signal", says a site of about 500 pages or fewer that is well linked might not need a sitemap, and says robots.txt "is not a mechanism for keeping a web page out of Google."
   Sources: [canonical URLs](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls), [sitemaps overview](https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview), [robots.txt intro](https://developers.google.com/search/docs/crawling-indexing/robots/intro).
   In this generator: `url` produces the canonical tag, `sitemap.xml` and `robots.txt`.

## Get the call

8. **Show the phone number plainly and make it tappable, near the top.**
   NN/g's contact guidelines (2019) say "Clearly display contact phone numbers on your site. Don't hide or remove phone numbers", and found most users prefer talking to a person by phone.
   Source: [NN/g, Contact Us page guidelines](https://www.nngroup.com/articles/contact-us-pages/).
   In this generator: phone and click-to-call buttons are built in above the fold, plus a sticky mobile Call and Directions bar.

9. **List hours and time zone, and say whether the business is open right now.**
   NN/g says to state hours of operation and time zones, and Google asks profiles for regular customer-facing hours, including special hours.
   Sources: [NN/g, Contact Us page guidelines](https://www.nngroup.com/articles/contact-us-pages/), [Business Profile guidelines](https://support.google.com/business/answer/3038177).
   In this generator: `hours` and `timezone` drive the hours table and the open now badge.

10. **Offer a second, short way to reach out, never as the only option.**
    NN/g says a contact form should add to phone numbers, not replace them, and should keep to 3 to 5 fields.
    Source: [NN/g, Contact Us page guidelines](https://www.nngroup.com/articles/contact-us-pages/).
    In this generator: `quote_cta` adds a Request a free quote button (mailto or SMS, no backend), always next to the Call button.

11. **Make directions one tap away.**
    Distance is one of Google's three local ranking factors, and NN/g says to always include the full address with state and ZIP.
    Sources: [Google Business Profile, local ranking](https://support.google.com/business/answer/7091), [NN/g, Contact Us page guidelines](https://www.nngroup.com/articles/contact-us-pages/).
    In this generator: `map` embeds the map; the Directions button in the sticky bar is built in.

## Earn trust

12. **Show real reviews near the top and link to where they live.**
    BrightLocal's Local Consumer Review Survey 2026 (1,002 US adults) found 97% read reviews for local businesses, 92% factor in star ratings, 74% look for reviews from the past three months, and after a positive review 54% visit the business website and 20% contact the business.
    Source: [BrightLocal, Local Consumer Review Survey 2026](https://www.brightlocal.com/research/local-consumer-review-survey/).
    In this generator: `testimonials`, only real quotes with permission, never invented; keep them recent.

13. **Do not fake or pad social proof, and avoid showing tiny counts.**
    NN/g warns that low numbers can make a business look unpopular and says each social proof feature should be tested, not assumed to help.
    Source: [NN/g, Social proof in the user experience](https://www.nngroup.com/articles/social-proof-ux/).
    In this generator: `testimonials` is skipped when empty; there are no review counts or star widgets made up on the page.

14. **Be upfront: say who runs it, what it costs, and how to reach them.**
    NN/g's four credibility factors are design quality, upfront disclosure, comprehensive and current content, and connection to the rest of the web, and hiding basics like rates or contact details drives people away.
    Source: [NN/g, Trustworthiness in web design](https://www.nngroup.com/articles/trustworthy-design/).
    In this generator: `trust` badges (licensed and insured, years in business, local owner), `services` in plain language, and an optional price range.

15. **Use real photos of the shop, the work and the people.**
    Google asks for photos that are in focus, well lit and not heavily filtered or AI altered, recommends at least three exterior photos, and suggests 720 by 720 px.
    Source: [Google Business Profile, photos](https://support.google.com/business/answer/6123536).
    In this generator: `photos`; the first one also feeds `og:image`.

16. **Answer the questions people call about, in plain words.**
    NN/g lists comprehensive, current content as a trust factor; Google limited FAQ rich results in August 2023 to "well-known, authoritative government and health websites", so FAQ markup will not usually earn a rich result for a small business.
    Sources: [NN/g, Trustworthiness in web design](https://www.nngroup.com/articles/trustworthy-design/), [Google Search Central blog, FAQ and HowTo changes](https://developers.google.com/search/blog/2023/08/howto-faq-changes).
    In this generator: `faq` renders on the page and as FAQPage JSON-LD, for clarity, not for a guaranteed rich result.

## Be fast and usable

17. **Load fast on phones: LCP within 2.5 s, INP within 200 ms, CLS at 0.1 or less.**
    web.dev sets these as the "good" thresholds, measured at the 75th percentile of page loads on mobile and desktop.
    Source: [web.dev, Web Vitals](https://web.dev/articles/vitals).
    In this generator: built in, one static HTML file with inline CSS and no framework.

18. **Never lazy-load the hero image, and give it high fetch priority.**
    web.dev says "Never lazy-load your LCP image" and suggests `fetchpriority="high"` on it, with right-sized AVIF or WebP files.
    Source: [web.dev, Optimize LCP](https://web.dev/articles/optimize-lcp).
    In this generator: the first entry in `photos` is the hero and loads eagerly; the rest lazy-load.

19. **Keep text contrast at 4.5:1 or better.**
    WCAG 1.4.3 (Level AA) requires 4.5:1 for normal text and 3:1 for large text (18 pt, or 14 pt bold), and 4.499:1 fails.
    Source: [W3C, Understanding SC 1.4.3 Contrast (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html).
    In this generator: `color` is auto-adjusted until text on it reaches 4.5:1.

20. **Make buttons big enough to tap: 44 by 44.**
    WCAG 2.5.8 (Level AA) sets a 24 by 24 CSS pixel minimum and 2.5.5 uses 44 by 44 CSS pixels; Apple asks for hit regions of at least 44 by 44 points.
    Sources: [W3C, Understanding SC 2.5.8 Target Size (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html), [Apple HIG, Buttons](https://developer.apple.com/design/human-interface-guidelines/buttons).
    In this generator: built in, every button and tel link has a 44 px minimum.

## Share well

21. **Give the page Open Graph tags so links look right in texts and social posts.**
    The Open Graph protocol requires `og:title`, `og:type`, `og:image` and `og:url`, and describes `og:description` as one to two sentences.
    Source: [Open Graph protocol](https://ogp.me/).
    In this generator: built in; `og:image` comes from `og_image` when set, otherwise from the first entry in `photos` (a local photo needs `url` so the link can be absolute).

22. **Ship a square favicon.**
    Google says a favicon must be square (1:1) and recommends one larger than 48 by 48 px, linked with `<link rel="icon">`.
    Source: [Google Search Central, favicon in search results](https://developers.google.com/search/docs/appearance/favicon-in-search).
    In this generator: built in, an SVG favicon drawn from the brand initial.

## Not used

- A widely repeated "53% of mobile visits leave after 3 seconds" figure: the Think with Google page now redirects and the number could not be checked, so it is left out.
- Moz local SEO pages could not be fetched. Whitespark's ranking factor surveys poll SEO practitioners, not Google, so they are context, not proof.

## Sources

- [Google Business Profile, how local ranking works](https://support.google.com/business/answer/7091)
- [Google Business Profile, guidelines for representing your business](https://support.google.com/business/answer/3038177)
- [Google Business Profile, photos](https://support.google.com/business/answer/6123536)
- [Google Search Central, title links](https://developers.google.com/search/docs/appearance/title-link)
- [Google Search Central, snippets and meta descriptions](https://developers.google.com/search/docs/appearance/snippet)
- [Google Search Central, LocalBusiness structured data](https://developers.google.com/search/docs/appearance/structured-data/local-business)
- [Google Search Central, canonical URLs](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)
- [Google Search Central, sitemaps overview](https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview)
- [Google Search Central, robots.txt intro](https://developers.google.com/search/docs/crawling-indexing/robots/intro)
- [Google Search Central, favicon in search results](https://developers.google.com/search/docs/appearance/favicon-in-search)
- [Google Search Central blog, FAQ and HowTo changes (2023)](https://developers.google.com/search/blog/2023/08/howto-faq-changes)
- [schema.org areaServed](https://schema.org/areaServed)
- [web.dev, Web Vitals](https://web.dev/articles/vitals)
- [web.dev, Optimize LCP](https://web.dev/articles/optimize-lcp)
- [W3C, Understanding SC 1.4.3 Contrast (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)
- [W3C, Understanding SC 2.5.8 Target Size (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html)
- [Apple HIG, Buttons](https://developer.apple.com/design/human-interface-guidelines/buttons)
- [NN/g, Contact Us page guidelines (2019)](https://www.nngroup.com/articles/contact-us-pages/)
- [NN/g, Trustworthiness in web design (2016)](https://www.nngroup.com/articles/trustworthy-design/)
- [NN/g, Social proof in the user experience (2014)](https://www.nngroup.com/articles/social-proof-ux/)
- [BrightLocal, Local Consumer Review Survey 2026](https://www.brightlocal.com/research/local-consumer-review-survey/)
- [Open Graph protocol](https://ogp.me/)
- [Whitespark, Local Search Ranking Factors](https://whitespark.ca/local-search-ranking-factors/)
