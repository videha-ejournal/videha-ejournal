/* VIDEHA PPT PLAYER — presentation library configuration */
window.VIDEHA_PPT_CONFIG = {
  cacheVersion: "2026-08-22-2",

  defaultPresentation: {
    title: "Water-Burial Among the Crocodiles — English Teaching Course",
    url: "./presentations/default.pptx",
    fallbackUrl: "https://raw.githubusercontent.com/videha-ejournal/videha-ejournal/main/presentations/default.pptx",
    autoLoad: true
  },

  categories: [
    {
      title: "विदेह PPT · Videha Presentations",
      subtitle: "GitHub-hosted presentations",
      open: true,
      items: [
        {
          title: "Water-Burial Among the Crocodiles — English Teaching Course",
          url: "./presentations/default.pptx",
          fallbackUrl: "https://raw.githubusercontent.com/videha-ejournal/videha-ejournal/main/presentations/default.pptx",
          badge: "DEFAULT"
        },
        {
          title: "Videha Teaching — Water Burial",
          url: "./Videha_Teaching_Water_Burial.pptx",
          fallbackUrl: "https://raw.githubusercontent.com/videha-ejournal/videha-ejournal/main/Videha_Teaching_Water_Burial.pptx"
        }
      ]
    },
    {
      title: "बड़ फाइल · Large PPTX",
      subtitle: "Archive.org / download-first presentations",
      open: false,
      items: [
        {
          title: "Gohi Jalsamadhi Teaching — Archive.org",
          downloadUrl: "https://archive.org/download/videha-petar-2/Gohi_Jalsamadhi_Teaching_merge.pptx",
          downloadOnly: true,
          tryDirect: true
        }
      ]
    }
  ]
};
