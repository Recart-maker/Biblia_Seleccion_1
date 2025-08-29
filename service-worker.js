const CACHE_NAME = 'biblia-cache-v1';
const urlsToCache = [
  '/',
  '/libros',
  '/favoritos',
  '/static/css/style.css',
  '/static/js/script.js',
  '/static/manifest.json',
  '/static/images/icono-192.png',
  '/static/images/icono-512.png',
  '/static/images/biblia.png'
];
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        if (response) {
          return response;
        }
        return fetch(event.request);
      })
  );
});