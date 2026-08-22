/* VIDEHA PPT PLAYER — presentation library configuration
   Add future presentations here. No HTML editing is required.

   For a GitHub-hosted PPTX:
     { title: "My PPT", url: "./presentations/my-file.pptx" }

   For a large Archive.org PPTX that readers should download first:
     {
       title: "Large presentation",
       downloadUrl: "https://archive.org/download/ITEM/file.pptx",
       downloadOnly: true
     }

   Change cacheVersion when replacing a file but keeping the same URL/filename.
*/
window.VIDEHA_PPT_CONFIG = {
  cacheVersion: "2026-08-22-1",

  // Put your always-available GitHub PPTX at this path.
  defaultPresentation: {
    title: "Default Videha Presentation",
    url: "./presentations/default.pptx",
    autoLoad: true
  },

  categories: [
    {
      title: "विदेह PPT · Videha Presentations",
      subtitle: "GitHub-hosted presentations",
      open: true,
      items: [
        {
          title: "Default Videha Presentation",
          url: "./presentations/default.pptx",
          badge: "DEFAULT"
        }
      ]
    },
    {
      title: "बड़ फाइल · Large PPTX",
      subtitle: "Archive.org / download-first presentations",
      open: false,
      items: [
        // Example:
        // {
        //   title: "Large Teaching Course",
        //   downloadUrl: "https://archive.org/download/ITEM_NAME/file.pptx",
        //   downloadOnly: true
        // }
      ]
    }
  ]
};
