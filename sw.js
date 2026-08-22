const CACHE_NAME = "videha-ppt-player-v1";
const APP_SHELL = [
  "./",
  "./index.html",
  "./presentations.js"
];

// Single bundled module used by the player.
// The service worker attempts to cache it for later offline reuse.
const REMOTE_MODULE =
  "https://esm.sh/pptx-preview@1.0.7?bundle&target=es2022";

self.addEventListener("install", event => {
  self.skipWaiting();
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE_NAME);
    try { await cache.addAll(APP_SHELL); } catch (_) {}
    try { await cache.add(REMOTE_MODULE); } catch (_) {}
  })());
});

self.addEventListener("activate", event => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)));
    await self.clients.claim();
  })());
});

self.addEventListener("fetch", event => {
  const req = event.request;

  // Navigation: network first, cached shell fallback.
  if (req.mode === "navigate") {
    event.respondWith((async () => {
      try {
        const fresh = await fetch(req);
        const cache = await caches.open(CACHE_NAME);
        cache.put("./index.html", fresh.clone()).catch(() => {});
        return fresh;
      } catch (_) {
        return (await caches.match("./index.html")) || Response.error();
      }
    })());
    return;
  }

  // PPTX: network first so a replaced default can update, then cached copy.
  if (/\.pptx(?:$|\?)/i.test(req.url)) {
    event.respondWith((async () => {
      try {
        const fresh = await fetch(req);
        if (fresh.ok) {
          const cache = await caches.open(CACHE_NAME);
          cache.put(req, fresh.clone()).catch(() => {});
        }
        return fresh;
      } catch (_) {
        return (await caches.match(req)) || Response.error();
      }
    })());
    return;
  }

  // Static/module assets: cache first, network and cache on miss.
  event.respondWith((async () => {
    const cached = await caches.match(req);
    if (cached) return cached;
    const fresh = await fetch(req);
    if (fresh && (fresh.ok || fresh.type === "opaque")) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(req, fresh.clone()).catch(() => {});
    }
    return fresh;
  })());
});
