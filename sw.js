const CACHE_NAME = "videha-presentation-hub-v8";
const APP_SHELL = ["./","./index.html","./ppt-player.html","./presentations.js","./water-burial-css-documentary/Videha_CSS_Documentary.html"];
const RENDERER =
  "https://cdn.jsdelivr.net/npm/@aiden0z/pptx-renderer@1.2.4/dist/aiden0z-pptx-renderer.browser.es.js";

self.addEventListener("install", event => {
  self.skipWaiting();
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE_NAME);
    for (const item of APP_SHELL) {
      try { await cache.add(item); } catch (_) {}
    }
    try { await cache.add(RENDERER); } catch (_) {}
  })());
});

self.addEventListener("activate", event => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter(k =>
      (k.startsWith("videha-ppt-player-v") || k.startsWith("videha-presentation-hub-v")) && k !== CACHE_NAME
    ).map(k => caches.delete(k)));
    await self.clients.claim();
  })());
});

self.addEventListener("fetch", event => {
  const req = event.request;
  const url = new URL(req.url);

  if (req.mode === "navigate") {
    event.respondWith((async () => {
      try {
        const fresh = await fetch(req, {cache:"no-store"});
        const cache = await caches.open(CACHE_NAME);
        cache.put(req, fresh.clone()).catch(()=>{});
        return fresh;
      } catch (_) {
        return (await caches.match(req)) || (await caches.match("./index.html")) || Response.error();
      }
    })());
    return;
  }

  if (/\.pptx(?:$|\?)/i.test(url.pathname + url.search)) {
    // Do not block PPTX with the service worker. Let page code handle fallback/cache.
    return;
  }

  event.respondWith((async () => {
    const cached = await caches.match(req);
    if (cached) return cached;
    const fresh = await fetch(req);
    if (fresh && (fresh.ok || fresh.type === "opaque")) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(req, fresh.clone()).catch(()=>{});
    }
    return fresh;
  })());
});
