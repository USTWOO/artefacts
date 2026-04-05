const CACHE_NAME = "receipt-scanner-v1";
const ASSETS = [
    "./",
    "./index.html",
    "./style.css",
    "./app.js",
    "./manifest.json"
];

self.addEventListener("install", event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS))
    );
});

self.addEventListener("fetch", event => {
    // Only cache GET requests and skip API calls
    if (event.request.method !== "GET" || event.request.url.includes(":8000")) {
        return;
    }

    event.respondWith(
        caches.match(event.request).then(response => {
            return response || fetch(event.request).catch(err => {
                console.log("Fetch failed; returning offline fallback if any.", err);
            });
        })
    );
});
