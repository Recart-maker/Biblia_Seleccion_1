const CACHE_NAME = 'biblia-cache-v1';
const urlsToCache = [
  '/',
  '/index.html',
  '/favoritos.html',
  '/libros.html',
  '/resultados_busqueda.html',
  '/ver_capitulo.html',
  '/ver_libro.html',
  '/static/css/style.css',
  '/static/js/script.js',
  '/static/manifest.json',
  // Agrega aquí las rutas a los íconos
  '/static/images/icono-192.png',
  '/static/images/icono-512.png',
  // Agrega aquí otras rutas importantes como tus archivos JSON si quieres que se guarden en caché
  '/biblia.json',
  '/resumen_libros.json'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Cacheando archivos estáticos');
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