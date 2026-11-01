# Groundwork Landscaping — Website Improvement Plan

Prepared October 2, 2026
Website reviewed: https://groundworkllc.netlify.app/

## Goal

Make the website easier to use on phones, make every important message readable, and turn more visitors into qualified quote requests—without replacing the current earthy design.

## Review scope

This plan is based on a visual review of the live homepage at desktop and 390px mobile widths, a mobile review of the contact page, and inspection of the local homepage, contact page, shared stylesheet, and shared JavaScript. It is not a complete accessibility, SEO, performance, or security audit. No quote request was submitted and no website code was changed during the review.

## What to preserve

- Warm earth-tone palette and distinctive serif headings.
- Real project photographs and location-specific case studies.
- Clear focus on hardscaping, fencing, and lawn care.
- Longmont and Boulder County service-area messaging.
- Simple static-site architecture and existing form provider.

## Phase 1 — Fix usability blockers

Priority: urgent. Complete before adding new features.

### 1. Repair the mobile header

Observed: at a 390px viewport, the document measured 445px wide. The quote button was clipped and the menu button extended beyond the screen.

Actions:
- Fit the brand, quote action, and menu control into narrow viewports.
- Use a compact brand layout or reduce competing header elements on small screens.
- Fix the underlying sizing problem rather than hiding horizontal overflow.
- Check every page that uses the shared navigation.

Acceptance criteria:
- No horizontal scrolling at 320px, 375px, 390px, 768px, or desktop widths.
- Menu button and quote action remain fully visible and usable.
- Menu opens, closes, responds to Escape, and exposes correct expanded state.
- Desktop navigation remains intact.

### 2. Restore brand visibility

Observed: the live homepage brand text “Groundwork” had the same computed brown color as its header background.

Actions:
- Give header brand links an explicit high-contrast color.
- Resolve competing link-color rules in the CSS cascade.
- Check default, hover, focus, and visited states.

Acceptance criteria:
- The complete business name is readable on every page.
- Header text meets applicable WCAG AA contrast requirements.

### 3. Fix the contact-page introduction

Observed: dark text appeared over a dark gradient, making the heading and supporting text hard to read.

Actions:
- Choose one consistent treatment: light text on a dark panel, or dark text on a light panel.
- Align the introduction with the shared earth-tone theme.
- Check the response-time note, breadcrumb, and call button as well as the headline.

Acceptance criteria:
- All intro copy is legible on mobile and desktop.
- Normal text meets 4.5:1 contrast and large text meets 3:1.

### 4. Repair the mobile contact bar

Observed: the Call label was difficult to see, and the Netlify badge overlapped the quote control.

Actions:
- Correct text and control contrast, including the dismiss button.
- Investigate the hosting badge configuration and avoid overlap with fixed controls.
- Preserve safe-area spacing and ensure the bar does not obscure page content.
- Test the quote sheet at small heights and with an on-screen keyboard.

Acceptance criteria:
- Call, quote, and dismiss controls remain readable and unobstructed.
- Touch targets are approximately 44px or larger.
- Quote-sheet fields and submit action remain reachable with scrolling.
- Closing the sheet restores focus to the initiating control.

## Phase 2 — Simplify quote requests

Priority: high. Start after Phase 1 is verified.

### 5. Reduce initial form effort

Actions:
- Ask for name, service, one usable contact method, and brief project details.
- Make timeline, budget, and photo link optional secondary fields.
- Add a city or ZIP field if needed to qualify service-area coverage.
- Keep the stated response time only if the business can consistently meet it.
- Reduce nested mobile padding so fields have useful width.

Acceptance criteria:
- A visitor can send a basic inquiry without providing both phone and email.
- At least one valid contact method is required.
- Labels remain visible; validation identifies the field needing correction.
- Failed submissions preserve entered information and provide a clear retry/call option.
- Successful submissions show an unambiguous confirmation.

### 6. Verify the full conversion flow

Actions:
- Test homepage, service-page, and case-study quote entry points.
- Check service preselection and the quick-quote sheet.
- Verify telephone links and thank-you navigation.
- Use mocked form responses for routine testing; obtain permission before sending a real test lead.

Acceptance criteria:
- Every quote entry point works on mobile and desktop.
- Success, error, and timeout states are tested.
- No duplicate submissions or console errors occur during tested flows.

## Phase 3 — Strengthen business credibility

Priority: medium. Requires real business assets and confirmed claims.

### 7. Add authentic people and review proof

Actions:
- Add a genuine owner or crew photograph and a short introduction.
- Link testimonials to genuine review sources where available and permitted.
- Confirm the experience and property-count claims before retaining them.
- Add insurance, licensing, or warranty information only if accurate and applicable.

Acceptance criteria:
- Every published claim is supportable.
- Photos and testimonials have appropriate permission.
- Visitors can understand who will perform the work.

### 8. Improve project storytelling

Actions:
- Prioritize finished-project photographs with clear focal points.
- Add concise problem, work performed, and outcome descriptions to case studies.
- Add matched before/after comparisons only where suitable photographs exist.
- Include location, materials, and approximate scope when accurate and appropriate.
- Consider making xeriscaping easier to discover if it is a service the business wants to grow.

Acceptance criteria:
- Featured projects demonstrate specific capabilities rather than only decoration.
- Images have honest descriptions and useful captions.
- Each case study offers a relevant next step for requesting similar work.

## Phase 4 — Technical cleanup and measurement

Priority: medium. Keep changes incremental.

### 9. Consolidate shared presentation and behavior

Actions:
- Reduce conflicting page-level and shared color/navigation rules.
- Remove redundant interaction handlers after confirming current behavior.
- Make primary content, hero imagery, and business statistics meaningful without JavaScript.
- Preserve reduced-motion support and keyboard access.
- Compare source pages with generated output so deployment does not undo fixes.

Acceptance criteria:
- Shared header and contact controls behave consistently across templates.
- Core content remains usable when JavaScript is unavailable.
- No regressions in navigation, galleries, or form handling.

### 10. Audit discoverability and performance

Actions:
- Check local-business structured data, canonical URLs, sitemap, and social-preview images.
- Check image dimensions and responsive image selection.
- Evaluate whether rotating hero images justify their loading and motion cost.
- Run accessibility and performance checks on representative pages.
- If analytics are wanted, choose a privacy-conscious approach and measure quote starts, completed requests, and call clicks without recording personal form data.

Acceptance criteria:
- Internal links and image references pass the project's checker.
- Structured data accurately describes the business.
- Representative mobile pages are checked for layout shifts, loading delays, and accessibility issues.
- Any tracking has an explicit purpose and appropriate privacy disclosures.

## Recommended implementation order

1. Mobile header sizing and brand contrast.
2. Contact-page contrast and mobile contact-bar overlap.
3. Cross-page mobile and keyboard verification.
4. Shorter quote form and submission-state testing.
5. Authentic people, reviews, and improved project stories.
6. Shared-code cleanup and broader technical audit.
7. Optional conversion measurement and further improvements based on evidence.

## Release checklist

- [ ] Homepage, contact, work, about, one service page, one case study, and one blog page checked.
- [ ] No horizontal overflow at 320px, 375px, 390px, and 768px.
- [ ] Desktop layout checked at approximately 1440px.
- [ ] Brand, navigation, contact copy, and fixed controls are readable.
- [ ] Keyboard navigation, Escape behavior, and focus restoration checked.
- [ ] Reduced-motion settings respected.
- [ ] Quote success, failure, timeout, and service preselection tested.
- [ ] Internal links and images checked using the existing project tooling.
- [ ] Generated site output compared with source changes.
- [ ] Real business claims and customer permissions confirmed.
- [ ] Changes reviewed locally before deployment; no deployment without approval.

## First milestone

A mobile visitor can read the complete business name, open the menu, understand the contact page, and request a quote without clipped controls, horizontal scrolling, or overlapping badges.

This is the highest-value first release. A full redesign is not necessary to reach it.
