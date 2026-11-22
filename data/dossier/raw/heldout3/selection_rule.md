# Test set 3 expansion: how the seven new companies were chosen

Written and committed before any research agent ran (DECISIONS, 19 November). Criteria:
- A manufacturer whose revenue is mainly business-to-business; group revenue roughly EUR 0.3 to 15 billion.
- Not in `excluded_companies.txt` (every case file and proposal), so not one of the 63 training or 6 validation companies.
- Not in the product category of any development, test or test set 3 company (judged against the 99 development scopes,
  the two earlier test sets and the first five test set 3 companies; the reason is given for each one struck out).
- The 12 together cover 12 different sectors and at least 5 countries (the first five are all German).
- At least 15 public pages reachable without login, established by the research; a company that falls short is replaced
  by the next passing company in the order below.
- Questions are set at the freeze date, so no source can postdate the case date; the research does not use pages about
  the companies' future decisions.

Pool (vetted before the draw):

| Company | Country | Sector | Revenue | Verdict | Reason |
|---|---|---|---|---|---|
| Interroll Holding AG | CH | conveyor rollers and modules | ~EUR 0.55bn | pass |  |
| Komax Holding AG | CH | wire-processing machines | ~CHF 0.75bn | pass | machines for harness makers, not cables (Lapp) |
| Dätwyler Holding AG | CH | elastomer sealing components | ~CHF 1.1bn | strike | SKF (development) also makes industrial seals |
| Rieter Holding AG | CH | textile spinning machinery | ~CHF 0.86bn | pass | machines, not fibres (Lenzing) |
| Brembo N.V. | IT | brake systems | ~EUR 3.8bn | pass |  |
| Gerresheimer AG | DE | pharma glass and plastic packaging | ~EUR 2bn | strike | packaging (Sealed Air, MULTIVAC) and glass (Corning, proposed) |
| Dürr AG | DE | painting and finishing systems | ~EUR 4.7bn | strike | coating systems (Nordson, development) |
| Ahlstrom Oyj | FI | fibre materials and filters | ~EUR 3bn | strike | fibres (Lenzing) and filtration (Calgon Carbon) |
| Donaldson Company | US | filtration | ~USD 3.6bn | strike | filtration (Calgon Carbon, development) |
| Rittal GmbH & Co. KG | DE | electrical enclosures | ~EUR 2.5bn | strike | electrical products (Hubbell, Phoenix Contact) |
| Ponsse Oyj | FI | forest machines | ~EUR 0.8bn | strike | agricultural and forestry machinery (Deere, validation) |
| Tomra Systems ASA | NO | sorting and reverse-vending machines | ~EUR 1.3bn | pass |  |
| Nabtesco Corporation | JP | precision gear reducers and automatic doors | ~EUR 2bn | pass | gears, not drives or robots (Yaskawa) |
| Hoerbiger Holding AG | CH | compressor components | ~EUR 1.2bn | strike | compressors (Atlas Copco, development) |
| Kardex Holding AG | CH | automated storage and retrieval systems | ~CHF 0.7bn | pass |  |
| Biesse S.p.A. | IT | woodworking and stone machinery | ~EUR 0.7bn | pass |  |
| Sika AG | CH | construction chemicals | ~CHF 11bn | pass | chemicals, not insulation panels (Kingspan) |
| Vestas Wind Systems A/S | DK | wind turbines | ~EUR 17bn | strike | above the revenue range |

Draw: the passing companies shuffled with `random.Random(23)`, then taken in that order while sectors differ:

1. Kardex Holding AG (CH, automated storage and retrieval systems) - selected
2. Nabtesco Corporation (JP, precision gear reducers and automatic doors) - selected
3. Biesse S.p.A. (IT, woodworking and stone machinery) - selected
4. Brembo N.V. (IT, brake systems) - selected
5. Rieter Holding AG (CH, textile spinning machinery) - selected
6. Sika AG (CH, construction chemicals) - selected
7. Interroll Holding AG (CH, conveyor rollers and modules) - replaced (country rule below)
8. Komax Holding AG (CH, wire-processing machines) - reserve
9. Tomra Systems ASA (NO, sorting and reverse-vending machines) - selected (country rule below)

Country rule (applied before any agent ran, 23:16): the draw above gives Germany, Switzerland, Italy and Japan, four
countries against the five required. The last company taken from the most common country (Interroll, Switzerland)
is replaced by the next reserve from a country not yet covered (Tomra, Norway). Selected: Kardex, Nabtesco, Biesse,
Brembo, Rieter, Sika, Tomra; reserves in order: Komax, Interroll.
