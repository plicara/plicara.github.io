## DEC-002: One visual system, cut paper

- **Date:** 2026-11-02
- **Status:** decided
- **Context:** The site kept two visual styles: a warm serif scheme for the lab and a separate technical scheme and typeset for benchmarks and tools. The owner found the split incoherent and the offset-print look mechanical, and wanted a handcrafted, digital-native feel. After three rounds of mockups the owner chose the "cut paper" direction, with lowercase display and label roles.
- **Decision:** Replace the four schemes and two typesets with one scheme in two lights (daylight and lamplight) and one typeset (Hedvig Letters Serif, Figtree, JetBrains Mono), defined upstream in `plicara-brand` and vendored here. Colour arrives as torn paper blocks and the hand-drawn mark and planes. The home page leads with the question and the mark, routes readers to research, essays and benchmarks, shows models as coming soon, and speaks in the first person singular, because plicara is run by one person.
- **Consequences:** No page sets `data-scheme`; the retired names still resolve upstream so stale markup degrades to the matching light. Fired orange holds ink rather than cream to keep text at AA. Research articles keep their authored voice; only site copy moved to "I".
