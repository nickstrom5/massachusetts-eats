# Bay State Eats: name, icon and palette (final: Nick's decisions, 2026-11-07)

Final (Nick, 2026-11-07, "Yes, as proposed" on the 17-state review): the name and App Store subtitle as in
`playbook/app-store/listing.json`, icon concept B, the clam chowder bowl, and the palette as built (below).

## Name
- **Bay State Eats** (App Store name "Bay State Eats: Massachusetts", 28 characters; Home Screen "Bay State Eats", 14). "The Bay State"
  is Massachusetts's best-known nickname. A web search (2026-11-06) found no app, show, magazine or blog called "Bay State Eats"; the
  prompt found baystateeats.com unregistered in September 2026.
- Alternatives from the prompt: **Mass Eats** (short on the Home Screen, but "Mass" is ambiguous) and **Massachusetts Eats** (18 characters,
  will truncate under the icon); both .coms are registered. **Wicked Good Eats** is out (.com taken, many "wicked good" marks).
- Avoided: the state tourism office's taglines, Boston team names and marks, the state flag, seal and arms (a commission is redesigning
  them).
- Bundle id `com.massachusettseats.ios`; site nickstrom5.github.io/massachusetts-eats/ until a `massachusetts.eatsranked.com` record exists.

## Icon (state-prompts/ICON-STYLE.md)
- **B, Nick's choice (2026-11-07): a bowl of clam chowder with two oyster crackers**, a cranberry band on the bowl, on Atlantic navy. Passes
  check.swift; reads as soup at 60 px.
- A: a cold lobster roll in a split-top bun, side view. Passes, but at 60 px the three red chunks read like cherries on a pastry.
- C: a Boston cream pie wedge with its chocolate top. Passes after re-centring; the dark chocolate top all but vanishes on navy.
Drawn by `scripts/icon-concepts.swift` (PNGs in `playbook/brand/`); `scripts/make-brand.swift` makes the app icon, site icons and
docs/og.png from B.

## Palette (the prompt's second option: cranberry with Atlantic navy and cream; no team colors or marks)
Atlantic navy #13294B (14.4:1 on white) for titles and tint; cranberry #9E1B32 (white on it 7.9:1) for the hand-checked guide cards and
honors chips; Cape sand #E2B25A only as a fill under navy text (7.4:1); chowder cream #F7F2E6 pages. Header band: two Atlantic swells over
a cranberry baseline, with the Cape's flexed arm rising at the right in navy.
