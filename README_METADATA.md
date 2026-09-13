# Curated PDF metadata

`data/curated-pdf-metadata.json` is the authoritative hand-curated overlay for bibliographic roles that cannot be inferred safely from filenames alone.

The catalogue generator keeps these roles distinct: `author`, `originalAuthor`, `editor`, `originalEditor`, `translator`, `subjectPersons`, `documentType`, `contributorNote`, `originalLanguage`, and `originalLanguageCode`. File identity, SHA-256, size, and repository URLs continue to be generated from the actual PDF objects.

Do not infer or auto-fill these fields from filenames when the role is uncertain. Add or correct them only from editor-supplied or otherwise verified information.
