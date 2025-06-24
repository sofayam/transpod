async function clearAppCache() {
  if ('caches' in window) {
    const keys = await caches.keys();
    await Promise.all(keys.map(key => caches.delete(key)));
    if (navigator.serviceWorker.controller) {
      await navigator.serviceWorker.getRegistration().then(reg => reg.unregister());
    }
    location.reload(true);
  }
}