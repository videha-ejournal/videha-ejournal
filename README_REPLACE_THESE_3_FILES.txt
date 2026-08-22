FIXED VERSION — replace these three files in the root of:
videha-ejournal/videha-ejournal

1. index.html
2. presentations.js
3. sw.js

DO NOT delete:
presentations/default.pptx

The repository already contains that PPTX.

This version:
- uses @aiden0z/pptx-renderer 1.2.4 browser ESM
- uses the documented PptxViewer API
- first tries ./presentations/default.pptx
- automatically falls back to raw.githubusercontent.com
- uses cacheVersion 2026-08-22-2
- preserves India/Nepal inline SVG flags
- preserves Videha खोलू triangle sections
- includes the existing Videha_Teaching_Water_Burial.pptx
- includes Archive.org download-first entry
