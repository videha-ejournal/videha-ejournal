VIDEHA PPT PLAYER
=================

Files
-----
index.html          Main browser player
presentations.js    EDIT THIS when adding/changing PPTX presentations
sw.js               Browser cache/offline shell support
presentations/      Put GitHub-hosted PPTX files here

DEFAULT PRESENTATION
--------------------
1. Put one PPTX at:
      presentations/default.pptx

2. Upload this whole folder to GitHub Pages.

3. The player automatically attempts to open:
      ./presentations/default.pptx

4. If you replace the PPTX but keep the same filename, change:
      cacheVersion: "..."
   in presentations.js so browsers do not keep an older cached copy.

ADDING FUTURE PPTs — NO HTML EDITING
------------------------------------
Open presentations.js.

Add an item to a category:

{
  title: "My new presentation",
  url: "./presentations/my-new-presentation.pptx"
}

Add as many items/categories as required. Every category is automatically
shown with the same Videha "खोलू" triangle logic.

LARGE PPTX / ARCHIVE.ORG
------------------------
For a very large file:

{
  title: "Large teaching course",
  downloadUrl: "https://archive.org/download/ITEM/file.pptx",
  downloadOnly: true
}

The player shows a Download button. The reader downloads the PPTX and then
uses "Open local PPT/PPTX". A "Try direct" button is also shown; it works only
when the remote host permits the browser request.

LOCAL PPTX
----------
The local file input reads the file inside the visitor's browser. The player
does not upload that local PPTX to Videha, GitHub, or another server.

Legacy .ppt is not supported by the rendering engine because it is the older
binary PowerPoint format. Convert .ppt to .pptx first.

KEYBOARD
--------
Right Arrow / Page Down = next slide
Left Arrow / Page Up    = previous slide
Home                    = first slide
End                     = last slide
Space                   = play/pause
F                       = fullscreen
Esc                     = leave fullscreen

CURRENT BROWSER RENDERER
------------------------
The player uses pptx-preview 1.0.7 in the browser:
https://www.npmjs.com/package/pptx-preview

It is fetched as a bundled ES module from esm.sh and the service worker
attempts to cache the application/module for later reuse.

NOTES ON POWERPOINT FIDELITY
----------------------------
PPTX rendering in a web browser is not Microsoft PowerPoint itself.
Most ordinary text, images, shapes, tables, charts and formatting can be
rendered, but complex PowerPoint animations, uncommon embedded objects,
special fonts, macros, and some media may differ.

GITHUB
------
Use PPTX for GitHub-hosted files. For files too large for normal GitHub
repository storage, keep them on Archive.org and use the download-first
workflow above.

VIDEHA
------
© Gajendra Thakur, Editor
Videha First Maithili Fortnightly eJournal
ISSN 2229-547X
www.videha.co.in
