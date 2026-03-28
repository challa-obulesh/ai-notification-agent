// Service Worker — AI Notification Agent PWA
const CACHE_NAME = 'notifai-v1';
const STATIC_ASSETS = [
  '/',
  '/static/manifest.json',
];

// Install: cache core assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

// Activate: clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Fetch: network-first for API, cache-first for static
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Always go network for API calls
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(event.request).catch(() =>
        new Response(JSON.stringify({ status: 'error', message: 'Offline — API unavailable.' }), {
          headers: { 'Content-Type': 'application/json' },
        })
      )
    );
    return;
  }

  // Cache-first for everything else
  event.respondWith(
    caches.match(event.request).then((cached) => cached || fetch(event.request))
  );
});
