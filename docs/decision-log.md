# Decision log

## DEC-001: Match the public story to the evidence

- **Date:** 2026-09-13
- **Status:** superseded by DEC-002
- **Context:** Adrian requested a consistent personal and lab presence, clearer contribution statements, and tighter language around research limitations while preserving the visual design.
- **Decision:** Link the lab to Adrian's personal site and professional experience, remove Models from navigation while retaining its URL, and describe Adventure Bench as command interpretation. Clarify the regex article's observational comparisons and the distinction between an unresolved difference and equivalence. Preserve recorded results and identify the linked v1.0 whitepaper as an archived release.
- **Consequences:** The website makes the scope of claims and ownership easier to inspect. Article HTML, feed entries, and its downloadable article must be regenerated together when the interpretation changes; the archived whitepaper remains unchanged. Research and navigation checks run on pull requests.

## DEC-002: Keep the lab independent of the personal profile

- **Date:** 2026-09-14
- **Status:** decided
- **Context:** Adrian clarified that Plicara should stand as an independent research lab, not as an entry point to his personal site or professional experience.
- **Decision:** Remove the homepage paragraph that linked to Adrian's CV and personal website, and remove the corresponding documentation framing.
- **Consequences:** The site presents its research, tools, and benchmarks on their own terms. The removed professional-profile paragraph does not appear in primary lab content.
